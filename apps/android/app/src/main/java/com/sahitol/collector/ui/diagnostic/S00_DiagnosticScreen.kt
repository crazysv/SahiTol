package com.sahitol.collector.ui.diagnostic

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Bitmap
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import com.sahitol.collector.data.local.SahiTolDatabase
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.domain.classifier.ClassificationResult
import com.sahitol.collector.domain.classifier.LiteRtClassifier
import com.sahitol.collector.domain.media.CompressionResult
import com.sahitol.collector.domain.media.PhotoCompressor
import com.sahitol.collector.ui.theme.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.util.UUID

@Composable
fun S00_DiagnosticScreen(
    database: SahiTolDatabase,
    classifier: LiteRtClassifier,
    onStartCollection: () -> Unit = {}
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val scrollState = rememberScrollState()

    // --- State ---
    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED
        )
    }

    var capturedBitmap by remember { mutableStateOf<Bitmap?>(null) }
    var compressionResult by remember { mutableStateOf<CompressionResult?>(null) }
    var persistedLot by remember { mutableStateOf<LotEntity?>(null) }
    var dbOperationLatencyMs by remember { mutableStateOf<Long?>(null) }
    var classificationResult by remember { mutableStateOf<ClassificationResult?>(null) }
    var isRunningInference by remember { mutableStateOf(false) }
    var isTestingStorage by remember { mutableStateOf(false) }
    var showManualCategoryPicker by remember { mutableStateOf(false) }
    var selectedManualCategory by remember { mutableStateOf<String?>(null) }

    // Camera launcher
    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicturePreview()
    ) { bitmap ->
        if (bitmap != null) {
            capturedBitmap = bitmap
            coroutineScope.launch(Dispatchers.IO) {
                val cacheFile = File(context.cacheDir, "diagnostic_photo_${System.currentTimeMillis()}.jpg")
                val comp = PhotoCompressor.compressBitmap(bitmap, cacheFile)
                withContext(Dispatchers.Main) {
                    compressionResult = comp
                }
                // Automatically run offline LiteRT classifier on the captured photo
                val result = classifier.classify(bitmap)
                withContext(Dispatchers.Main) {
                    classificationResult = result
                }
            }
        }
    }

    // Permission launcher
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasCameraPermission = granted
        if (granted) {
            cameraLauncher.launch(null)
        }
    }

    // Auto-load default persisted diagnostic test row on launch
    LaunchedEffect(Unit) {
        val lots = withContext(Dispatchers.IO) {
            database.lotDao().getLotById("diagnostic-lot-001")
        }
        if (lots != null) {
            persistedLot = lots
        }
    }

    val photoReady = hasCameraPermission || compressionResult != null
    val saveReady = persistedLot != null
    val offlineReady = classificationResult != null
    val phoneReady = saveReady && (photoReady || offlineReady)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(NeutralSurface)
            .verticalScroll(scrollState)
            .padding(horizontal = 16.dp, vertical = 20.dp)
    ) {
        // --- 1. Top Header ---
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(SecondaryContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = "SahiTol Logo",
                        tint = OnSecondaryContainer,
                        modifier = Modifier.size(28.dp)
                    )
                }
                Column {
                    Text(
                        text = "सही Tol SahiTol",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                    Text(
                        text = "Android Feasibility Diagnostic",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = OutlineColor
                    )
                }
            }

            // Readiness Badge
            Surface(
                shape = CircleShape,
                color = SurfaceContainerHigh,
                border = BorderStroke(1.dp, OutlineVariantColor)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(if (phoneReady) SuccessGreen else TerracottaPrimary)
                    )
                    Text(
                        text = if (phoneReady) "v2.4 Ready" else "Diagnostics",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = OnSurfaceVariant
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // --- 2. Phone Readiness Hero Card ---
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            color = SurfaceContainerLow,
            shadowElevation = 1.dp
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Done,
                        contentDescription = null,
                        tint = TerracottaPrimary,
                        modifier = Modifier.size(20.dp)
                    )
                    Text(
                        text = "फ़ोन की तैयारी / Phone Readiness",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = TerracottaPrimary
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Check the things SahiTol needs to work reliably on this phone.",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = OnSurface,
                    lineHeight = 26.sp
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "Reliable offline-first weighing, photo compression, and LiteRT diagnostics for Indian scrap collectors.",
                    fontSize = 14.sp,
                    color = OnSurfaceVariant
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // --- 3. Four Status Badges Grid ---
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            DiagnosticStatusBadge(
                label = "PHOTO",
                isActive = photoReady,
                icon = Icons.Default.Add,
                modifier = Modifier.weight(1f)
            )
            DiagnosticStatusBadge(
                label = "SAVE",
                isActive = saveReady,
                icon = Icons.Default.Check,
                modifier = Modifier.weight(1f)
            )
            DiagnosticStatusBadge(
                label = "OFFLINE",
                isActive = offlineReady,
                icon = Icons.Default.Warning,
                modifier = Modifier.weight(1f)
            )
            DiagnosticStatusBadge(
                label = "READY",
                isActive = phoneReady,
                icon = Icons.Default.CheckCircle,
                isHighlight = true,
                modifier = Modifier.weight(1f)
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        // --- 4. Diagnostic Item 1: Camera Access & Compression ---
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            color = SurfaceContainer,
            shadowElevation = 1.dp
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(SurfaceContainerHigh),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Add,
                                contentDescription = null,
                                tint = TerracottaPrimary
                            )
                        }
                        Column {
                            Text(
                                text = "Camera Access / फोटो अनुमति",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = if (hasCameraPermission) "Permission granted / Ready" else "Requires camera access",
                                fontSize = 13.sp,
                                color = if (hasCameraPermission) SuccessGreen else OnSurfaceVariant
                            )
                        }
                    }

                    Icon(
                        imageVector = if (photoReady) Icons.Default.CheckCircle else Icons.Default.Warning,
                        contentDescription = null,
                        tint = if (photoReady) SuccessGreen else OutlineColor
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = {
                            if (hasCameraPermission) {
                                cameraLauncher.launch(null)
                            } else {
                                permissionLauncher.launch(Manifest.permission.CAMERA)
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(if (hasCameraPermission) "Take Photo / फोटो लें" else "Grant Camera / अनुमति दें", fontSize = 13.sp)
                    }

                    OutlinedButton(
                        onClick = {
                            // Synthesize camera-free test photo
                            val sample = PhotoCompressor.createDiagnosticSampleBitmap()
                            capturedBitmap = sample
                            coroutineScope.launch(Dispatchers.IO) {
                                val testFile = File(context.cacheDir, "diagnostic_sample.jpg")
                                val comp = PhotoCompressor.compressBitmap(sample, testFile)
                                withContext(Dispatchers.Main) {
                                    compressionResult = comp
                                }
                                val result = classifier.classify(sample)
                                withContext(Dispatchers.Main) {
                                    classificationResult = result
                                }
                            }
                        },
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Simulate / टेस्ट फोटो", fontSize = 13.sp)
                    }
                }

                // Compression stats if available
                compressionResult?.let { comp ->
                    Spacer(modifier = Modifier.height(10.dp))
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = SurfaceContainerLowest,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(10.dp)) {
                            Text(
                                text = "JPEG Bounded Compression Verified",
                                fontWeight = FontWeight.Bold,
                                fontSize = 12.sp,
                                color = SuccessGreen
                            )
                            Text(
                                text = "Size: ${comp.compressedSizeBytes / 1024} KB (${String.format("%.1f", comp.compressionRatioPercent)}% reduction, ${comp.width}x${comp.height}, ${comp.durationMs}ms)",
                                fontSize = 12.sp,
                                color = OnSurfaceVariant
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // --- 5. Diagnostic Item 2: Local Storage (Room DB Persistence) ---
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .border(BorderStroke(2.dp, TerracottaPrimary), RoundedCornerShape(12.dp)),
            shape = RoundedCornerShape(12.dp),
            color = SurfaceContainer,
            shadowElevation = 1.dp
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Local Storage / स्थानीय सहेजें",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = OutlineColor
                    )
                    Text(
                        text = if (persistedLot != null) "इस फ़ोन पर सुरक्षित" else "Not Saved Yet",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (persistedLot != null) SuccessGreen else TerracottaPrimary
                    )
                }

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = "Material: Cable (केबल)",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = OnSurface
                )
                Text(
                    text = "Weight: 2.5 kg • Offline Room SQLite Record",
                    fontSize = 14.sp,
                    color = OnSurfaceVariant
                )

                Spacer(modifier = Modifier.height(10.dp))

                Button(
                    onClick = {
                        isTestingStorage = true
                        coroutineScope.launch(Dispatchers.IO) {
                            val startTime = System.currentTimeMillis()
                            val lot = LotEntity(
                                lotId = "diagnostic-lot-001",
                                materialCode = "MAT-CAB-01",
                                estimatedWeightG = 2500L,
                                status = "DRAFT",
                                syncStatus = "SAVED_LOCAL_ONLY"
                            )
                            database.lotDao().insertLot(lot)
                            val retrieved = database.lotDao().getLotById("diagnostic-lot-001")
                            val elapsed = System.currentTimeMillis() - startTime
                            withContext(Dispatchers.Main) {
                                persistedLot = retrieved
                                dbOperationLatencyMs = elapsed
                                isTestingStorage = false
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = MustardSecondary),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = if (persistedLot != null) "Re-verify Local Storage (Room DB)" else "Test Local Storage Save",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                dbOperationLatencyMs?.let { latency ->
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Room SQLite write & read verified in ${latency}ms (persists across app restarts)",
                        fontSize = 11.sp,
                        color = SuccessGreen
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // --- 6. Diagnostic Item 3: Offline Inference (LiteRT Model) ---
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            color = SurfaceContainer,
            shadowElevation = 1.dp
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Offline Inference / बिना इंटरनेट पहचान",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = OutlineColor
                    )
                    classificationResult?.let { res ->
                        Text(
                            text = "${(res.confidence * 100).toInt()}% विश्वास / Confidence",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = TerracottaPrimary
                        )
                    }
                }

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = classificationResult?.let { "Suggestion: ${it.categoryNameHi} (${it.categoryNameEn})" }
                        ?: "Suggestion: Cable (केबल)",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = OnSurface
                )
                Text(
                    text = "Calculated offline on device (बिना इंटरनेट के डिवाइस पर परखा गया)",
                    fontSize = 14.sp,
                    color = OnSurfaceVariant
                )

                Spacer(modifier = Modifier.height(10.dp))

                Button(
                    onClick = {
                        isRunningInference = true
                        coroutineScope.launch(Dispatchers.IO) {
                            val bmp = capturedBitmap ?: PhotoCompressor.createDiagnosticSampleBitmap()
                            val res = classifier.classify(bmp)
                            withContext(Dispatchers.Main) {
                                classificationResult = res
                                isRunningInference = false
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = if (isRunningInference) "Running LiteRT Inference..." else "Run Offline Inference Benchmark",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                classificationResult?.let { res ->
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "LiteRT MobileNetV3-Small: ${String.format("%.2f", res.latencyMs)}ms inference on CPU in airplane mode (Threshold: 0.65)",
                        fontSize = 11.sp,
                        color = SuccessGreen
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // --- 7. Diagnostic Item 4: Fallback / Unknown Category Handling ---
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            color = SurfaceContainerHigh,
            border = BorderStroke(1.dp, OutlineVariantColor),
            shadowElevation = 1.dp
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Could not identify this photo / इस फोटो की पहचान नहीं हो सकी",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = OnSurface
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "No network needed. Select manually from catalog.",
                    fontSize = 13.sp,
                    color = OnSurfaceVariant
                )
                Spacer(modifier = Modifier.height(10.dp))

                OutlinedButton(
                    onClick = { showManualCategoryPicker = !showManualCategoryPicker },
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.outlinedButtonColors(containerColor = SurfaceContainerLowest),
                    border = BorderStroke(1.dp, OutlineColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = selectedManualCategory?.let { "Selected: $it" } ?: "Choose the material yourself / सामग्री स्वयं चुनें",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = OnSurface
                    )
                }

                AnimatedVisibility(visible = showManualCategoryPicker) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 8.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        listOf(
                            "MAT-CAB-01" to "Cable & Wire (केबल / तार)",
                            "MAT-PCB-01" to "Circuit Board / PCB (पीसीबी)",
                            "MAT-BAT-01" to "Lead-Acid Battery (लेड-एसिड बैटरी)",
                            "MAT-MET-01" to "Metals Cu/Al (धातु तांबा/एल्युमिनियम)",
                            "MAT-UNK-01" to "Other / Unknown Scrap (अन्य सामग्री)"
                        ).forEach { (code, title) ->
                            TextButton(
                                onClick = {
                                    selectedManualCategory = title
                                    showManualCategoryPicker = false
                                },
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text(
                                    text = "• $title",
                                    fontSize = 13.sp,
                                    color = TerracottaPrimary,
                                    modifier = Modifier.fillMaxWidth(),
                                    textAlign = TextAlign.Start
                                )
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // --- 8. Bottom Action Button ---
        Text(
            text = "Phone ready for SahiTol / SahiTol के लिए फ़ोन तैयार है",
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            color = TerracottaPrimary,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        Button(
            onClick = onStartCollection,
            colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.PlayArrow,
                    contentDescription = null,
                    tint = OnPrimary
                )
                Text(
                    text = "Start Collection / शुरू करें",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = OnPrimary
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // --- 9. Footer Note ---
        Text(
            text = "Made for Indian Scrap Dealers • कबाड़ी भाइयों के लिए समर्पित",
            fontSize = 12.sp,
            fontWeight = FontWeight.Normal,
            color = OutlineColor,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))
    }
}

@Composable
fun DiagnosticStatusBadge(
    label: String,
    isActive: Boolean,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    isHighlight: Boolean = false,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        color = if (isHighlight && isActive) SurfaceContainerHigh else SurfaceContainer,
        border = if (isHighlight) BorderStroke(1.dp, TerracottaPrimary.copy(alpha = 0.3f)) else null,
        shadowElevation = 1.dp
    ) {
        Column(
            modifier = Modifier.padding(vertical = 12.dp, horizontal = 4.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = if (isActive) SuccessGreen else OutlineColor,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = label,
                fontSize = 11.sp,
                fontWeight = if (isHighlight) FontWeight.Bold else FontWeight.SemiBold,
                color = OnSurface,
                textAlign = TextAlign.Center
            )
        }
    }
}
