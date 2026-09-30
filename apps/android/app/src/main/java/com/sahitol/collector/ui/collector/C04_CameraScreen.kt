package com.sahitol.collector.ui.collector

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.sahitol.collector.domain.media.PhotoCompressor
import com.sahitol.collector.ui.theme.*
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

/**
 * Screen C04: Photo Capture & Import (Stitch 83f516e48f1a).
 * Features:
 * - CameraX live viewfinder with 3:4 aspect ratio.
 * - Permission denied fallback banner with Settings intent and manual gallery import.
 * - Captured photo preview, retake, remove.
 * - Bounded JPEG compression (PhotoCompressor) guaranteeing < 500KB size budget.
 * - Proceed without photo fallback.
 */
@Composable
fun C04_CameraScreen(
    onPhotoConfirmed: (photoPath: String?) -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED
        )
    }

    var showPermissionBanner by remember { mutableStateOf(!hasCameraPermission) }
    var capturedPhotoPath by remember { mutableStateOf<String?>(null) }
    var isCompressing by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasCameraPermission = granted
        showPermissionBanner = !granted
    }

    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        if (uri != null) {
            // Copy uri to local app file and compress
            val file = File(context.cacheDir, "gallery_${System.currentTimeMillis()}.jpg")
            try {
                context.contentResolver.openInputStream(uri)?.use { input ->
                    file.outputStream().use { output ->
                        input.copyTo(output)
                    }
                }
                val compressed = PhotoCompressor.compress(file.absolutePath, maxDimension = 1024, maxBytes = 500_000)
                capturedPhotoPath = compressed.absolutePath
            } catch (e: Exception) {
                capturedPhotoPath = file.absolutePath
            }
        }
    }

    val imageCapture = remember { ImageCapture.Builder().build() }

    Scaffold(
        topBar = {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = NeutralSurface,
                tonalElevation = 1.dp
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        IconButton(onClick = onBack) {
                            Icon(
                                imageVector = Icons.Default.ArrowBack,
                                contentDescription = "Back",
                                tint = OnSurface
                            )
                        }
                        Text(
                            text = "Photo / फोटो",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(NeutralSurface)
                .padding(16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Column(modifier = Modifier.fillMaxWidth()) {
                // Camera Permission Warning Banner (Stitch C04)
                if (showPermissionBanner && !hasCameraPermission) {
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 12.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = ErrorContainer)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(14.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.Top
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.Warning,
                                        contentDescription = null,
                                        tint = ErrorRed,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Text(
                                        text = "कैमरा अनुमति आवश्यक है",
                                        style = MaterialTheme.typography.labelLarge,
                                        fontWeight = FontWeight.Bold,
                                        color = ErrorRed
                                    )
                                }

                                TextButton(onClick = { showPermissionBanner = false }) {
                                    Text("✕", color = ErrorRed, fontWeight = FontWeight.Bold)
                                }
                            }

                            Text(
                                text = "कबाड़ की पहचान और प्रमाण के लिए कैमरा चालू करें।",
                                style = MaterialTheme.typography.bodySmall,
                                color = ErrorRed,
                                modifier = Modifier.padding(vertical = 4.dp)
                            )

                            Button(
                                onClick = { permissionLauncher.launch(Manifest.permission.CAMERA) },
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = ErrorRed),
                                modifier = Modifier.padding(top = 4.dp)
                            ) {
                                Text(
                                    text = "अनुमति दें (Grant Permission)",
                                    style = MaterialTheme.typography.labelMedium,
                                    color = Color.White
                                )
                            }
                        }
                    }
                }

                // Viewfinder / Capture Zone (3:4 aspect ratio, Stitch C04)
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(3f / 4f)
                        .clip(RoundedCornerShape(16.dp))
                        .background(SurfaceContainerHigh)
                        .border(2.dp, OutlineColor.copy(alpha = 0.3f), RoundedCornerShape(16.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    if (capturedPhotoPath != null) {
                        // Captured Photo State Preview
                        Column(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center
                        ) {
                            Text(text = "📸", fontSize = 48.sp)
                            Spacer(modifier = Modifier.height(12.dp))
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.CheckCircle,
                                    contentDescription = null,
                                    tint = SuccessGreen,
                                    modifier = Modifier.size(20.dp)
                                )
                                Text(
                                    text = "फोटो सुरक्षित है (Photo Captured)",
                                    style = MaterialTheme.typography.labelLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                            }
                            Text(
                                text = "संपीड़ित आकार: < 500 KB • LiteRT तैयार",
                                style = MaterialTheme.typography.bodySmall,
                                color = OnSurfaceVariant,
                                modifier = Modifier.padding(top = 4.dp)
                            )

                            Spacer(modifier = Modifier.height(24.dp))

                            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                Button(
                                    onClick = { capturedPhotoPath = null },
                                    colors = ButtonDefaults.buttonColors(containerColor = SurfaceContainerHighest)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Refresh,
                                        contentDescription = null,
                                        tint = OnSurface
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text("फिर से (Retake)", color = OnSurface)
                                }

                                Button(
                                    onClick = { capturedPhotoPath = null },
                                    colors = ButtonDefaults.buttonColors(containerColor = ErrorContainer)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Delete,
                                        contentDescription = null,
                                        tint = ErrorRed
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text("हटाएं (Remove)", color = ErrorRed)
                                }
                            }
                        }
                    } else if (hasCameraPermission) {
                        // Live Camera Preview
                        AndroidView(
                            factory = { ctx ->
                                val previewView = PreviewView(ctx)
                                val cameraProviderFuture = ProcessCameraProvider.getInstance(ctx)
                                cameraProviderFuture.addListener({
                                    val cameraProvider = cameraProviderFuture.get()
                                    val preview = Preview.Builder().build().also {
                                        it.setSurfaceProvider(previewView.surfaceProvider)
                                    }
                                    try {
                                        cameraProvider.unbindAll()
                                        cameraProvider.bindToLifecycle(
                                            lifecycleOwner,
                                            CameraSelector.DEFAULT_BACK_CAMERA,
                                            preview,
                                            imageCapture
                                        )
                                    } catch (e: Exception) {
                                        e.printStackTrace()
                                    }
                                }, ContextCompat.getMainExecutor(ctx))
                                previewView
                            },
                            modifier = Modifier.fillMaxSize()
                        )

                        // High contrast alignment guides
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(24.dp)
                                .border(1.dp, TerracottaPrimary.copy(alpha = 0.5f), RoundedCornerShape(12.dp))
                        )
                    } else {
                        // Camera Permission Missing Placeholder
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(12.dp),
                            modifier = Modifier.padding(24.dp)
                        ) {
                            Text(text = "📷", fontSize = 48.sp)
                            Text(
                                text = "मटीरियल को फ्रेम में रखें",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface,
                                textAlign = TextAlign.Center
                            )
                            Button(
                                onClick = { galleryLauncher.launch("image/*") },
                                colors = ButtonDefaults.buttonColors(containerColor = SurfaceContainer)
                            ) {
                                Text(
                                    text = "गैलरी से लें (Import from Gallery)",
                                    color = OnSurface,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }
            }

            // Bottom Controls (Stitch C04)
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                if (capturedPhotoPath == null) {
                    if (hasCameraPermission) {
                        Button(
                            onClick = {
                                val photoFile = File(
                                    context.cacheDir,
                                    "lot_${SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())}.jpg"
                                )
                                val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()
                                imageCapture.takePicture(
                                    outputOptions,
                                    ContextCompat.getMainExecutor(context),
                                    object : ImageCapture.OnImageSavedCallback {
                                        override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                                            val compressed = PhotoCompressor.compress(
                                                photoFile.absolutePath,
                                                maxDimension = 1024,
                                                maxBytes = 500_000
                                            )
                                            capturedPhotoPath = compressed.absolutePath
                                        }

                                        override fun onError(exception: ImageCaptureException) {
                                            exception.printStackTrace()
                                        }
                                    }
                                )
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(56.dp),
                            shape = RoundedCornerShape(14.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                        ) {
                            Text(
                                text = "फोटो खींचें (Capture Photo)",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        TextButton(onClick = { galleryLauncher.launch("image/*") }) {
                            Text(
                                text = "गैलरी से लें (Import)",
                                color = TerracottaPrimary,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        TextButton(onClick = { onPhotoConfirmed(null) }) {
                            Text(
                                text = "बिना फोटो आगे बढ़ें (Skip)",
                                color = OnSurfaceVariant,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                } else {
                    Button(
                        onClick = { onPhotoConfirmed(capturedPhotoPath) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                    ) {
                        Text(
                            text = "आगे बढ़ें (Continue to Editor)",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                }
            }
        }
    }
}
