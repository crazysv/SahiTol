package com.sahitol.collector.domain.classifier

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.tensorflow.lite.Interpreter
import java.io.File
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel
import java.security.MessageDigest

data class ClassificationResult(
    val categoryCode: String,
    val categoryNameEn: String,
    val categoryNameHi: String,
    val categoryNameMr: String,
    val confidence: Float,
    val meetsThreshold: Boolean,
    val latencyMs: Double,
    val isFallback: Boolean,
    val rawScores: Map<String, Float>,
    val modelVersion: String = "v1.0",
    val modelChecksum: String = LiteRtClassifier.EXPECTED_SHA256
)

class LiteRtClassifier(
    private val context: Context? = null,
    customInterpreter: Interpreter? = null,
    customLabels: List<String>? = null,
    forceCorrupted: Boolean = false
) {
    private var interpreter: Interpreter? = customInterpreter
    val labels = mutableListOf<String>()
    val advisoryThreshold = 0.65f
    val modelVersion = "v1.0"
    var isCorrupted = forceCorrupted
        private set
    var actualSha256: String? = null
        private set

    companion object {
        const val EXPECTED_SHA256 = "35d0ad7cdd7f8c3d5f20ecda408b87d7f091a8b997f30793554ce416f790eb23"
        const val MODEL_PATH = "model/classifier.tflite"
        const val LABELS_PATH = "model/labels.json"
    }

    init {
        if (customLabels != null) {
            labels.addAll(customLabels)
        } else if (context != null) {
            loadLabels()
        } else {
            // Default 12 classes from model metadata
            labels.addAll(
                listOf(
                    "MAT-BAT-01", "MAT-BAT-02", "MAT-CAB-01", "MAT-CRT-01",
                    "MAT-LCD-01", "MAT-MET-01", "MAT-MIX-01", "MAT-MOT-01",
                    "MAT-PCB-01", "MAT-PCB-02", "MAT-PLA-01", "MAT-UNK-01"
                )
            )
        }

        if (interpreter == null && context != null && !isCorrupted) {
            loadModel()
        }
    }

    private fun loadModel() {
        val ctx = context ?: return
        try {
            val fileDescriptor = ctx.assets.openFd(MODEL_PATH)
            val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
            val fileChannel = inputStream.channel
            val startOffset = fileDescriptor.startOffset
            val declaredLength = fileDescriptor.declaredLength
            val modelBuffer = fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)

            // Verify model checksum for runtime safety and tamper protection
            verifyChecksum(modelBuffer)

            val options = Interpreter.Options().apply {
                setNumThreads(4)
            }
            interpreter = Interpreter(modelBuffer, options)
        } catch (e: Exception) {
            e.printStackTrace()
            isCorrupted = true
            interpreter = null
        }
    }

    private fun verifyChecksum(buffer: java.nio.MappedByteBuffer) {
        try {
            val digest = MessageDigest.getInstance("SHA-256")
            val originalPosition = buffer.position()
            buffer.rewind()
            val tempBytes = ByteArray(8192)
            while (buffer.hasRemaining()) {
                val len = minOf(buffer.remaining(), tempBytes.size)
                buffer.get(tempBytes, 0, len)
                digest.update(tempBytes, 0, len)
            }
            buffer.position(originalPosition)
            val hash = digest.digest().joinToString("") { "%02x".format(it) }
            actualSha256 = hash
            if (hash != EXPECTED_SHA256) {
                // Not matching expected frozen weights
                isCorrupted = true
            }
        } catch (e: Exception) {
            e.printStackTrace()
            isCorrupted = true
        }
    }

    private fun loadLabels() {
        val ctx = context ?: return
        try {
            val jsonString = ctx.assets.open(LABELS_PATH).bufferedReader().use { it.readText() }
            val jsonArray = JSONArray(jsonString)
            for (i in 0 until jsonArray.length()) {
                labels.add(jsonArray.getString(i))
            }
        } catch (e: Exception) {
            e.printStackTrace()
            // Fallback hardcoded 12 classes from model metadata
            labels.addAll(
                listOf(
                    "MAT-BAT-01", "MAT-BAT-02", "MAT-CAB-01", "MAT-CRT-01",
                    "MAT-LCD-01", "MAT-MET-01", "MAT-MIX-01", "MAT-MOT-01",
                    "MAT-PCB-01", "MAT-PCB-02", "MAT-PLA-01", "MAT-UNK-01"
                )
            )
        }
    }

    fun isModelLoaded(): Boolean = interpreter != null && labels.isNotEmpty() && !isCorrupted

    fun verifyChecksum(): Boolean = actualSha256 == EXPECTED_SHA256 && !isCorrupted

    /**
     * Synchronous classification. Safe against OOM and runtime faults.
     */
    fun classify(bitmap: Bitmap): ClassificationResult {
        val startTime = System.nanoTime()
        val interp = interpreter
        if (interp == null || labels.isEmpty() || isCorrupted) {
            val latency = (System.nanoTime() - startTime) / 1_000_000.0
            return getFallbackResult(latency)
        }

        try {
            val resizedBitmap = Bitmap.createScaledBitmap(bitmap, 224, 224, true)
            val inputBuffer = ByteBuffer.allocateDirect(1 * 224 * 224 * 3 * 4).apply {
                order(ByteOrder.nativeOrder())
                rewind()
            }

            val intValues = IntArray(224 * 224)
            resizedBitmap.getPixels(intValues, 0, 224, 0, 0, 224, 224)

            for (pixel in intValues) {
                val r = (pixel shr 16 and 0xFF).toFloat()
                val g = (pixel shr 8 and 0xFF).toFloat()
                val b = (pixel and 0xFF).toFloat()

                // Normalization formula from metadata: (pixel / 127.5) - 1.0
                inputBuffer.putFloat((r / 127.5f) - 1.0f)
                inputBuffer.putFloat((g / 127.5f) - 1.0f)
                inputBuffer.putFloat((b / 127.5f) - 1.0f)
            }

            val outputArray = Array(1) { FloatArray(labels.size) }
            interp.run(inputBuffer, outputArray)

            val latencyMs = (System.nanoTime() - startTime) / 1_000_000.0
            val scores = outputArray[0]

            var maxIdx = -1
            var maxScore = -1.0f
            val rawMap = mutableMapOf<String, Float>()
            for (i in scores.indices) {
                val label = labels.getOrElse(i) { "MAT-UNK-01" }
                val score = scores[i]
                rawMap[label] = score
                if (score > maxScore) {
                    maxScore = score
                    maxIdx = i
                }
            }

            val bestLabel = if (maxIdx >= 0) labels[maxIdx] else "MAT-UNK-01"
            val (en, hi, mr) = getCategoryNames(bestLabel)
            val meetsThreshold = maxScore >= advisoryThreshold

            return ClassificationResult(
                categoryCode = bestLabel,
                categoryNameEn = en,
                categoryNameHi = hi,
                categoryNameMr = mr,
                confidence = maxScore,
                meetsThreshold = meetsThreshold,
                latencyMs = latencyMs,
                isFallback = !meetsThreshold,
                rawScores = rawMap,
                modelVersion = modelVersion,
                modelChecksum = actualSha256 ?: EXPECTED_SHA256
            )
        } catch (oom: OutOfMemoryError) {
            System.gc()
            val latency = (System.nanoTime() - startTime) / 1_000_000.0
            return getFallbackResult(latency)
        } catch (e: Exception) {
            val latency = (System.nanoTime() - startTime) / 1_000_000.0
            return getFallbackResult(latency)
        }
    }

    /**
     * Executes classification asynchronously off the main thread on Dispatchers.Default.
     */
    suspend fun classifyBitmapAsync(bitmap: Bitmap): ClassificationResult = withContext(Dispatchers.Default) {
        classify(bitmap)
    }

    /**
     * Safely decodes an image file with bounded memory consumption (<15MB) and classifies it off the main thread.
     */
    suspend fun classifyFileAsync(filePath: String): ClassificationResult = withContext(Dispatchers.IO) {
        try {
            val file = File(filePath)
            if (!file.exists() || file.length() == 0L) {
                return@withContext getFallbackResult(0.0)
            }

            val boundsOptions = BitmapFactory.Options().apply {
                inJustDecodeBounds = true
            }
            BitmapFactory.decodeFile(filePath, boundsOptions)

            val maxDim = maxOf(boundsOptions.outWidth, boundsOptions.outHeight)
            var sampleSize = 1
            while (maxDim / sampleSize > 1024) {
                sampleSize *= 2
            }

            val decodeOptions = BitmapFactory.Options().apply {
                inSampleSize = sampleSize
                inPreferredConfig = Bitmap.Config.ARGB_8888
            }
            val bitmap = BitmapFactory.decodeFile(filePath, decodeOptions)
                ?: return@withContext getFallbackResult(0.0)

            val result = withContext(Dispatchers.Default) {
                classify(bitmap)
            }
            bitmap.recycle()
            result
        } catch (oom: OutOfMemoryError) {
            System.gc()
            getFallbackResult(0.0)
        } catch (e: Exception) {
            getFallbackResult(0.0)
        }
    }

    fun runBenchmark(iterations: Int = 3): Double {
        val bitmap = Bitmap.createBitmap(224, 224, Bitmap.Config.ARGB_8888)
        var totalLatency = 0.0
        for (i in 0 until iterations) {
            val res = classify(bitmap)
            totalLatency += res.latencyMs
        }
        return totalLatency / iterations
    }

    fun getFallbackResult(latencyMs: Double): ClassificationResult {
        return ClassificationResult(
            categoryCode = "MAT-UNK-01",
            categoryNameEn = "Unknown / Other",
            categoryNameHi = "अज्ञात / अन्य",
            categoryNameMr = "अज्ञात / इतर",
            confidence = 0.0f,
            meetsThreshold = false,
            latencyMs = latencyMs,
            isFallback = true,
            rawScores = emptyMap(),
            modelVersion = modelVersion,
            modelChecksum = actualSha256 ?: EXPECTED_SHA256
        )
    }

    fun getCategoryNames(code: String): Triple<String, String, String> {
        return when (code) {
            "MAT-CAB-01" -> Triple("Cables & Wires", "केबल (Cable)", "केबल (Cable)")
            "MAT-BAT-01" -> Triple("Lead-Acid Battery", "लेड-एसिड बैटरी", "लेड-अ‍ॅसिड बॅटरी")
            "MAT-BAT-02" -> Triple("Lithium-Ion Battery", "लिथियम-आयन बैटरी", "लिथियम-आयन बॅटरी")
            "MAT-CRT-01" -> Triple("CRT Glass / Monitors", "सीआरटी ग्लास / टीवी", "सीआरटी काच / टीव्ही")
            "MAT-LCD-01" -> Triple("Flat Display / Screens", "एलसीडी / डिस्प्ले स्क्रीन", "एलसीडी / डिस्प्ले स्क्रीन")
            "MAT-MET-01" -> Triple("Metals (Cu/Al/Fe)", "धातु (तांबा/एल्युमिनियम)", "धातू (तांबे/अल्युमिनियम)")
            "MAT-MIX-01" -> Triple("Mixed Electronics", "मिश्रित ई-कचरा", "मिश्रित ई-कचरा")
            "MAT-MOT-01" -> Triple("Motors & Compressors", "मोटर और कंप्रेसर", "मोटर आणि कॉम्प्रेसर")
            "MAT-PCB-01" -> Triple("High-Grade PCB", "उच्च श्रेणी पीसीबी", "उच्च दर्जाचे पीसीबी")
            "MAT-PCB-02" -> Triple("Low/Mid-Grade PCB", "सामान्य पीसीबी", "सामान्य पीसीबी")
            "MAT-PLA-01" -> Triple("Rigid FR Plastics", "कठोर प्लास्टिक", "कठीण प्लॅस्टिक")
            else -> Triple("Unknown Scrap", "अज्ञात सामग्री", "अज्ञात वस्तू")
        }
    }

    fun close() {
        interpreter?.close()
        interpreter = null
    }
}

