package com.sahitol.collector.domain.media

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import kotlin.math.max

data class CompressionResult(
    val originalSizeBytes: Long,
    val compressedSizeBytes: Long,
    val width: Int,
    val height: Int,
    val savedFile: File,
    val compressionRatioPercent: Double,
    val durationMs: Long
)

object PhotoCompressor {

    fun compress(
        filePath: String,
        maxDimension: Int = 1024,
        maxBytes: Int = 500_000
    ): File {
        val inputFile = File(filePath)
        if (!inputFile.exists()) return inputFile
        val bitmap = BitmapFactory.decodeFile(filePath) ?: return inputFile
        val outputFile = File(inputFile.parentFile, "comp_${inputFile.name}")
        compressBitmap(bitmap, outputFile, maxDimension, quality = 80)
        return if (outputFile.exists()) outputFile else inputFile
    }

    fun compressBitmap(
        bitmap: Bitmap,
        outputFile: File,
        maxDimension: Int = 1024,
        quality: Int = 80
    ): CompressionResult {
        val startTime = System.currentTimeMillis()

        // Calculate aspect-ratio preserving dimensions
        val originalWidth = bitmap.width
        val originalHeight = bitmap.height
        val maxOriginal = max(originalWidth, originalHeight)

        val targetBitmap = if (maxOriginal > maxDimension) {
            val scale = maxDimension.toFloat() / maxOriginal
            val targetW = (originalWidth * scale).toInt()
            val targetH = (originalHeight * scale).toInt()
            Bitmap.createScaledBitmap(bitmap, targetW, targetH, true)
        } else {
            bitmap
        }

        val outStream = ByteArrayOutputStream()
        targetBitmap.compress(Bitmap.CompressFormat.JPEG, quality, outStream)
        val compressedBytes = outStream.toByteArray()

        FileOutputStream(outputFile).use { fos ->
            fos.write(compressedBytes)
            fos.flush()
        }

        val duration = System.currentTimeMillis() - startTime
        val uncompressedEstBytes = (originalWidth * originalHeight * 4).toLong()
        val compressedBytesSize = compressedBytes.size.toLong()
        val ratio = (1.0 - (compressedBytesSize.toDouble() / uncompressedEstBytes.toDouble())) * 100.0

        return CompressionResult(
            originalSizeBytes = uncompressedEstBytes,
            compressedSizeBytes = compressedBytesSize,
            width = targetBitmap.width,
            height = targetBitmap.height,
            savedFile = outputFile,
            compressionRatioPercent = ratio,
            durationMs = duration
        )
    }

    fun createDiagnosticSampleBitmap(): Bitmap {
        // Creates a sample 800x600 test bitmap simulating waste cable image for camera-free verification
        val bitmap = Bitmap.createBitmap(800, 600, Bitmap.Config.ARGB_8888)
        val canvas = android.graphics.Canvas(bitmap)
        val paint = android.graphics.Paint()

        // Background
        paint.color = android.graphics.Color.rgb(240, 238, 232)
        canvas.drawRect(0f, 0f, 800f, 600f, paint)

        // Cable loops
        paint.color = android.graphics.Color.rgb(159, 60, 22)
        paint.strokeWidth = 32f
        paint.style = android.graphics.Paint.Style.STROKE
        canvas.drawCircle(400f, 300f, 180f, paint)

        paint.color = android.graphics.Color.rgb(115, 92, 0)
        paint.strokeWidth = 24f
        canvas.drawCircle(400f, 300f, 120f, paint)

        return bitmap
    }
}
