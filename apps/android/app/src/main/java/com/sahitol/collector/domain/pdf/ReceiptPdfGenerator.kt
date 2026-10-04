package com.sahitol.collector.domain.pdf

import android.content.Context
import android.content.ContentValues
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Typeface
import android.graphics.pdf.PdfDocument
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import com.sahitol.collector.domain.qr.QrGenerator
import java.io.File
import java.io.FileOutputStream

/**
 * Generates offline PDF receipts for Digital Handover Records.
 * Implements R-HAND-06 / AT-034 with statutory Non-EPR disclosure and cryptographic hash seal.
 */
object ReceiptPdfGenerator {

    data class ReceiptExport(
        val displayName: String,
        val locationLabel: String
    )

    data class ReceiptData(
        val handoverId: String,
        val referenceCode: String,
        val occurredAt: String,
        val collectorAlias: String,
        val facilityName: String,
        val materialName: String,
        val weightG: Long,
        val rateInrPerKg: Double,
        val totalPayoutInr: Double,
        val canonicalHash: String,
        val verificationUrl: String,
        val statusText: String = "PENDING_CONFIRMATION"
    )

    fun generateReceiptPdf(context: Context, data: ReceiptData): ReceiptExport {
        val pdfDocument = PdfDocument()
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 1).create() // A4 standard in points
        val page = pdfDocument.startPage(pageInfo)
        val canvas = page.canvas

        val paint = Paint().apply {
            isAntiAlias = true
        }

        // Background
        canvas.drawColor(Color.WHITE)

        // Header Brand Bar
        paint.color = Color.parseColor("#9F3C16") // TerracottaPrimary
        canvas.drawRect(0f, 0f, 595f, 60f, paint)

        // Header Text
        paint.color = Color.WHITE
        paint.textSize = 20f
        paint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("SahiTol (सही तोल)", 36f, 38f, paint)

        paint.textSize = 12f
        paint.typeface = Typeface.DEFAULT
        canvas.drawText("Digital Handover Record · डिजिटल हस्तनांतरण रसीद", 240f, 38f, paint)

        // Statutory Non-EPR Notice Banner (Mandatory Invariant R-HAND-06)
        paint.color = Color.parseColor("#FFF3E0") // Light amber
        canvas.drawRect(36f, 80f, 559f, 130f, paint)

        paint.color = Color.parseColor("#B78103") // Warning border
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = 1f
        canvas.drawRect(36f, 80f, 559f, 130f, paint)

        paint.style = Paint.Style.FILL
        paint.color = Color.parseColor("#6D4C41")
        paint.textSize = 9f
        paint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("STATUTORY NOTICE / वैधानिक सूचना:", 46f, 96f, paint)

        paint.typeface = Typeface.DEFAULT
        paint.textSize = 8.5f
        canvas.drawText("SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate.", 46f, 110f, paint)
        canvas.drawText("Received mass does not prove recycling. Batteries follow isolated hazardous handling.", 46f, 122f, paint)

        // Handover Reference & Status Box
        var y = 160f
        paint.color = Color.parseColor("#1C1B1F")
        paint.textSize = 14f
        paint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Reference: ${data.referenceCode}", 36f, y, paint)

        paint.color = Color.parseColor("#4A6572")
        paint.textSize = 11f
        paint.typeface = Typeface.DEFAULT
        canvas.drawText("Status: ${data.statusText}", 340f, y, paint)

        y += 24f
        paint.color = Color.parseColor("#79747E")
        paint.textSize = 10f
        canvas.drawText("Handover ID: ${data.handoverId}", 36f, y, paint)
        canvas.drawText("Date & Time: ${data.occurredAt}", 340f, y, paint)

        // Divider
        y += 16f
        paint.color = Color.parseColor("#E0E0E0")
        canvas.drawLine(36f, y, 559f, y, paint)

        // Transaction Details
        y += 30f
        paint.color = Color.parseColor("#1C1B1F")
        paint.textSize = 12f
        paint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Commercial & Material Details", 36f, y, paint)

        y += 20f
        val rows = listOf(
            "Collector Alias" to data.collectorAlias,
            "Receiving Facility" to data.facilityName,
            "Material Classification" to data.materialName,
            "Net Measured Weight" to "%.2f kg (%d g)".format(data.weightG / 1000.0, data.weightG),
            "Agreed Rate" to "₹%.2f / kg".format(data.rateInrPerKg),
            "Total Agreed Value" to "₹%.2f".format(data.totalPayoutInr)
        )

        paint.textSize = 10f
        for ((label, value) in rows) {
            paint.typeface = Typeface.DEFAULT
            paint.color = Color.parseColor("#49454F")
            canvas.drawText(label, 36f, y, paint)

            paint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            paint.color = Color.parseColor("#1C1B1F")
            canvas.drawText(value, 240f, y, paint)
            y += 18f
        }

        // Cryptographic Hash Section
        y += 15f
        paint.color = Color.parseColor("#E0E0E0")
        canvas.drawLine(36f, y, 559f, y, paint)

        y += 25f
        paint.color = Color.parseColor("#1C1B1F")
        paint.textSize = 12f
        paint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Cryptographic Integrity Seal (SAHITOL-JCS-1)", 36f, y, paint)

        y += 18f
        paint.color = Color.parseColor("#49454F")
        paint.textSize = 9f
        paint.typeface = Typeface.MONOSPACE
        canvas.drawText("SHA-256: ${data.canonicalHash}", 36f, y, paint)

        y += 16f
        canvas.drawText("Verify: ${data.verificationUrl}", 36f, y, paint)

        // Draw Embedded QR Code
        try {
            val qrBitmap = QrGenerator.generateQrBitmap(data.verificationUrl, 160)
            canvas.drawBitmap(qrBitmap, 380f, y + 10f, null)
        } catch (_: Exception) {}

        // Footer note
        paint.typeface = Typeface.DEFAULT
        paint.color = Color.parseColor("#79747E")
        paint.textSize = 8.5f
        canvas.drawText("Generated locally by SahiTol Android Client. Offline tamper-evident record.", 36f, 800f, paint)

        pdfDocument.finishPage(page)

        val displayName = "Receipt_${data.referenceCode}_${System.currentTimeMillis()}.pdf"
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                // MediaStore makes the receipt visible in Files/Downloads without a
                // broad storage permission. It is intentionally not written to cache.
                val values = ContentValues().apply {
                    put(MediaStore.Downloads.DISPLAY_NAME, displayName)
                    put(MediaStore.Downloads.MIME_TYPE, "application/pdf")
                    put(MediaStore.Downloads.RELATIVE_PATH, "${Environment.DIRECTORY_DOWNLOADS}/SahiTol")
                }
                val uri = context.contentResolver.insert(
                    MediaStore.Downloads.EXTERNAL_CONTENT_URI,
                    values
                ) ?: error("Could not create the Downloads receipt file.")
                try {
                    context.contentResolver.openOutputStream(uri)?.use { out ->
                        pdfDocument.writeTo(out)
                    } ?: error("Could not write the Downloads receipt file.")
                } catch (error: Exception) {
                    context.contentResolver.delete(uri, null, null)
                    throw error
                }
                return ReceiptExport(displayName, "Downloads/SahiTol")
            }

            // Android 8–9 fallback. Newer devices use the public Downloads path above.
            val outputDir = File(context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), "SahiTol").apply { mkdirs() }
            val outputFile = File(outputDir, displayName)
            FileOutputStream(outputFile).use { out -> pdfDocument.writeTo(out) }
            return ReceiptExport(displayName, "SahiTol app files")
        } finally {
            pdfDocument.close()
        }
    }
}
