package com.sahitol.collector.ui.collector

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.domain.classifier.ClassificationResult
import com.sahitol.collector.domain.classifier.LiteRtClassifier
import com.sahitol.collector.domain.model.MaterialCategory
import com.sahitol.collector.ui.theme.*
import java.util.Locale

/**
 * Screen C05: Material, Weight & Condition Lot Editor (Stitch afa6f950fa3a).
 * Features:
 * - Live On-Device LiteRT Advisory Classifier inference off the main thread.
 * - Real confidence score display and advisory threshold evaluation (0.52).
 * - SahiTol AI Suggestion banner with Confirm / Change / Abstain controls.
 * - Separate persistence of AI suggestion vs human-confirmed material label (R-ML-04).
 * - 3x3 Grid of Material Tiles (CRT, LCD, PCB, Cable, Battery, Motor, Plastics, Mixed, UNKNOWN).
 * - Weight entry in Kilograms with decimal precision and quick adjustment buttons (-1kg, -100g, +100g, +1kg).
 * - 4 Condition choices: Clean, Damaged, Sorted, Mixed.
 * - Coarse location assurance strip.
 * - Primary "Save Lot & Print Tag" atomic Room persistence action.
 */
import com.sahitol.collector.domain.locale.MaterialAliases
import com.sahitol.collector.domain.safety.SafetyContentManager
import com.sahitol.collector.domain.locale.NumeralPreference
import com.sahitol.collector.domain.locale.SahiTolStrings

@Composable
fun C05_LotEditorScreen(
    initialPhotoPath: String?,
    classifier: LiteRtClassifier? = null,
    initialAiSuggestion: String? = null,
    initialAiConfidence: Float? = null,
    currentLanguage: String = "hi",
    currentNumeralPref: NumeralPreference = NumeralPreference.LATIN,
    onSaveLot: (
        materialCode: String,
        weightGrams: Long,
        condition: String,
        photoPath: String?,
        isDraft: Boolean,
        aiSuggestedCode: String?,
        aiConfidence: Float?,
        aiModelVersion: String?
    ) -> Unit,
    onNavigateSafety: (String) -> Unit = {},
    onBack: () -> Unit
) {
    var classificationResult by remember { mutableStateOf<ClassificationResult?>(null) }
    var isAnalyzing by remember { mutableStateOf(false) }

    var selectedMaterial by remember { mutableStateOf(MaterialCategory.PCB) }
    var weightInput by remember { mutableStateOf("14.25") }
    var selectedCondition by remember { mutableStateOf("Sorted") }
    var isAiConfirmed by remember { mutableStateOf(false) }
    var weightError by remember { mutableStateOf<String?>(null) }

    // Run on-device LiteRT inference off the main thread when a photo path is present
    LaunchedEffect(initialPhotoPath) {
        if (!initialPhotoPath.isNullOrBlank() && classifier != null) {
            isAnalyzing = true
            val result = classifier.classifyFileAsync(initialPhotoPath)
            classificationResult = result
            isAnalyzing = false
            // A prediction never changes the collector's material choice by
            // itself. The collector must tap Confirm for a reviewed mapping.
        }
    }

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
                            text = "Material Editor / सामग्री विवरण",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(NeutralSurface)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Spacer(modifier = Modifier.height(4.dp))
                // Top Photo Context Banner (Stitch C05)
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(130.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(14.dp),
                        contentAlignment = Alignment.BottomStart
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(TerracottaPrimary)
                                        .padding(horizontal = 8.dp, vertical = 4.dp)
                                ) {
                                    Text(
                                        text = "Lot #SCRP-${(1000..9999).random()}",
                                        style = MaterialTheme.typography.labelSmall,
                                        fontWeight = FontWeight.Bold,
                                        color = Color.White
                                    )
                                }

                                if (initialPhotoPath != null) {
                                    Text(
                                        text = "📷 Photo attached",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = OnSurfaceVariant,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                } else {
                                    Text(
                                        text = "Manual Entry (No Photo)",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = OnSurfaceVariant
                                    )
                                }
                            }

                            Text(
                                text = "10:42 AM",
                                style = MaterialTheme.typography.labelSmall,
                                color = OnSurfaceVariant
                            )
                        }
                    }
                }
            }

            // Advisory AI Suggestion Banner (Stitch C05)
            item {
                if (isAnalyzing) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = TerracottaPrimary,
                                strokeWidth = 2.dp
                            )
                            Column {
                                Text(
                                    text = "चित्र का विश्लेषण हो रहा है...",
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "On-device LiteRT MobileNetV3 (Offline)",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = OnSurfaceVariant
                                )
                            }
                        }
                    }
                } else if (classificationResult != null) {
                    val result = classificationResult!!
                    if (result.meetsThreshold && !result.isFallback) {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(14.dp),
                            colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(14.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(40.dp)
                                            .clip(CircleShape)
                                            .background(SecondaryContainer),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(text = "🧠", fontSize = 20.sp)
                                    }
                                    Column {
                                        Text(
                                            text = "SahiTol AI Suggestion (Advisory)",
                                            style = MaterialTheme.typography.labelMedium,
                                            fontWeight = FontWeight.Bold,
                                            color = OnSurface
                                        )
                                        Text(
                                            text = "${result.categoryNameHi} • ${String.format(Locale.US, "%.1f", result.confidence * 100)}% विश्वास",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = TerracottaPrimary,
                                            fontWeight = FontWeight.Bold
                                        )
                                        Text(
                                        text = "लेटेंसी: ${result.latencyMs.toInt()} ms • ऑफलाइन LiteRT • स्वयं पुष्टि करें",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = OnSurfaceVariant
                                        )
                                    }
                                }

                                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    Button(
                                        onClick = {
                                            selectedMaterial = MaterialCategory.fromModelCode(result.categoryCode)
                                            isAiConfirmed = true
                                        },
                                        shape = RoundedCornerShape(8.dp),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (isAiConfirmed) SuccessGreen else TerracottaPrimary
                                        ),
                                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                                    ) {
                                        Text(
                                            text = if (isAiConfirmed) "पुष्टि की गई (Confirmed)" else "पुष्टि करें (Confirm)",
                                            style = MaterialTheme.typography.labelSmall,
                                            fontWeight = FontWeight.Bold,
                                            color = Color.White
                                        )
                                    }

                                    OutlinedButton(
                                        onClick = { isAiConfirmed = false },
                                        shape = RoundedCornerShape(8.dp),
                                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                                    ) {
                                        Text(
                                            text = "बदलें (Change)",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = OnSurface
                                        )
                                    }
                                }
                            }
                        }
                    } else {
                        // Abstain State (Low confidence / OOD scrap)
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(14.dp),
                            colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(14.dp),
                                horizontalArrangement = Arrangement.spacedBy(10.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(40.dp)
                                        .clip(CircleShape)
                                        .background(ErrorContainer),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(text = "⚠️", fontSize = 20.sp)
                                }
                                Column {
                                    Text(
                                        text = if (result.meetsThreshold) "मॉडल का लेबल सुरक्षित रूप से मैप नहीं किया जा सकता" else "मॉडल निश्चित नहीं है (कम विश्वास / अस्पष्ट)",
                                        style = MaterialTheme.typography.labelMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = OnSurface
                                    )
                                    Text(
                                        text = if (result.meetsThreshold) "मॉडल लेबल: ${result.categoryNameHi} • ${String.format(Locale.US, "%.1f", result.confidence * 100)}% — स्वतः चयन नहीं" else "विश्वास स्तर: ${String.format(Locale.US, "%.1f", result.confidence * 100)}% (सीमा 52% से कम)",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = ErrorRed,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                    Text(
                                        text = "कृपया नीचे 3×3 ग्रिड से सही सामग्री स्वयं चुनें।",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = OnSurfaceVariant
                                    )
                                }
                            }
                        }
                    }
                } else if (initialAiSuggestion != null) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(40.dp)
                                        .clip(CircleShape)
                                        .background(SecondaryContainer),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(text = "🧠", fontSize = 20.sp)
                                }
                                Column {
                                    Text(
                                        text = "SahiTol AI Suggestion (Advisory)",
                                        style = MaterialTheme.typography.labelMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = OnSurface
                                    )
                                    Text(
                                        text = "$initialAiSuggestion • ${(initialAiConfidence ?: 0.85f) * 100}% confidence",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = TerracottaPrimary,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                            }

                            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                Button(
                                    onClick = {
                                        selectedMaterial = MaterialCategory.fromModelCode(initialAiSuggestion)
                                        isAiConfirmed = true
                                    },
                                    shape = RoundedCornerShape(8.dp),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = if (isAiConfirmed) SuccessGreen else TerracottaPrimary
                                    ),
                                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                                ) {
                                    Text(
                                        text = if (isAiConfirmed) "Confirmed" else "Confirm",
                                        style = MaterialTheme.typography.labelSmall,
                                        fontWeight = FontWeight.Bold,
                                        color = Color.White
                                    )
                                }

                                OutlinedButton(
                                    onClick = { isAiConfirmed = false },
                                    shape = RoundedCornerShape(8.dp),
                                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                                ) {
                                    Text(
                                        text = "Change",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = OnSurface
                                    )
                                }
                            }
                        }
                    }
                } else {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(text = "ℹ️", fontSize = 20.sp)
                            Text(
                                text = "मैनुअल चयन सक्रिय • नीचे दी गई श्रेणियों में से सही प्रकार चुनें।",
                                style = MaterialTheme.typography.bodySmall,
                                color = OnSurfaceVariant
                            )
                        }
                    }
                }
            }

            // SECTION 1: WHAT IS IT? / सामग्री क्या है? (Stitch C05)
            item {
                Column {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "1. What is it? / सामग्री क्या है?",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "Tap to select",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceVariant
                        )
                    }

                    // 3x3 Grid of Material Tiles
                    val categories = MaterialCategory.entries
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        for (row in categories.chunked(3)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                for (cat in row) {
                                    val isSelected = selectedMaterial == cat
                                    Card(
                                        modifier = Modifier
                                            .weight(1f)
                                            .height(84.dp)
                                            .clickable { selectedMaterial = cat },
                                        shape = RoundedCornerShape(12.dp),
                                        colors = CardDefaults.cardColors(
                                            containerColor = if (isSelected) TerracottaPrimary else SurfaceContainer
                                        ),
                                        border = if (isSelected) androidx.compose.foundation.BorderStroke(2.dp, TerracottaPrimary) else null
                                    ) {
                                        Column(
                                            modifier = Modifier
                                                .fillMaxSize()
                                                .padding(6.dp),
                                            horizontalAlignment = Alignment.CenterHorizontally,
                                            verticalArrangement = Arrangement.Center
                                        ) {
                                            Text(
                                                text = when (cat.code) {
                                                    "CRT" -> "📺"
                                                    "LCD" -> "🖥"
                                                    "PCB" -> "💻"
                                                    "CABLE" -> "🔌"
                                                    "BATTERY" -> "🔋"
                                                    "MOTOR" -> "⚙"
                                                    "PLASTICS" -> "🧴"
                                                    "MIXED" -> "📦"
                                                    else -> "❓"
                                                },
                                                fontSize = 22.sp
                                            )
                                            Text(
                                                text = cat.code,
                                                style = MaterialTheme.typography.labelMedium,
                                                fontWeight = FontWeight.Bold,
                                                color = if (isSelected) Color.White else OnSurface
                                            )
                                            Text(
                                                text = cat.displayNameHi.take(6),
                                                style = MaterialTheme.typography.labelSmall,
                                                fontSize = 9.sp,
                                                color = if (isSelected) Color.White.copy(alpha = 0.8f) else OnSurfaceVariant
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Colloquial Material Aliases (R-LANG-01, T010, T036)
                    val aliases = MaterialAliases.getAliasesForCategory(selectedMaterial, currentLanguage)
                    if (aliases.isNotEmpty()) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 8.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .background(SurfaceContainerLow)
                                .padding(horizontal = 10.dp, vertical = 6.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Text(
                                text = "🏷 " + when (currentLanguage) {
                                    "hi" -> "स्थानीय नाम:"
                                    "mr" -> "स्थानिक नावे:"
                                    else -> "Yard Aliases:"
                                },
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = aliases.take(4).joinToString(" • "),
                                style = MaterialTheme.typography.bodySmall,
                                color = TerracottaPrimary,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }

                    // Contextual Safety Card Alert (R-SAFE-01, AT-048, T035, T039)
                    val safetyCard = SafetyContentManager.getCardForCategory(selectedMaterial)
                    if (safetyCard != null) {
                        val safetyLoc = safetyCard.localized(currentLanguage)
                        Surface(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 8.dp)
                                .clip(RoundedCornerShape(10.dp))
                                .clickable { onNavigateSafety(selectedMaterial.code) },
                            color = ErrorRed.copy(alpha = 0.08f),
                            border = androidx.compose.foundation.BorderStroke(1.dp, ErrorRed.copy(alpha = 0.3f))
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(10.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    modifier = Modifier.weight(1f),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    Text(text = "⚠️", fontSize = 18.sp)
                                    Column {
                                        Text(
                                            text = safetyLoc.title,
                                            style = MaterialTheme.typography.labelSmall,
                                            fontWeight = FontWeight.Bold,
                                            color = ErrorRed
                                        )
                                        Text(
                                            text = safetyLoc.subtitle,
                                            style = MaterialTheme.typography.bodySmall,
                                            fontSize = 11.sp,
                                            color = OnSurfaceVariant,
                                            maxLines = 1
                                        )
                                    }
                                }
                                Text(
                                    text = when (currentLanguage) {
                                        "hi" -> "गाइड देखें →"
                                        "mr" -> "मार्गदर्शक पाहा →"
                                        else -> "View Guide →"
                                    },
                                    style = MaterialTheme.typography.labelSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = TerracottaPrimary
                                )
                            }
                        }
                    }
                }
            }

            // SECTION 2: WEIGHT / वजन (Stitch C05)
            item {
                Column {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "2. Weight / वजन",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(text = "⚡", fontSize = 14.sp)
                            Text(
                                text = "Live scale sync",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary
                            )
                        }
                    }

                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainer)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                OutlinedTextField(
                                    value = weightInput,
                                    onValueChange = {
                                        weightInput = it
                                        weightError = null
                                    },
                                    textStyle = MaterialTheme.typography.headlineLarge.copy(
                                        fontWeight = FontWeight.Bold,
                                        color = OnSurface
                                    ),
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                    singleLine = true,
                                    modifier = Modifier.weight(1f),
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedBorderColor = Color.Transparent,
                                        unfocusedBorderColor = Color.Transparent
                                    )
                                )

                                Text(
                                    text = "KG",
                                    style = MaterialTheme.typography.headlineMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = TerracottaPrimary
                                )
                            }

                            if (weightError != null) {
                                Text(
                                    text = weightError ?: "",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = ErrorRed,
                                    modifier = Modifier.padding(top = 4.dp)
                                )
                            }

                            Divider(
                                modifier = Modifier.padding(vertical = 12.dp),
                                color = OutlineColor.copy(alpha = 0.2f)
                            )

                            // Quick adjustment buttons (-1kg, -100g, +100g, +1kg)
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    AdjustmentButton("-1kg") {
                                        val cur = weightInput.toDoubleOrNull() ?: 0.0
                                        weightInput = String.format(Locale.US, "%.2f", maxOf(0.0, cur - 1.0))
                                    }
                                    AdjustmentButton("-100g") {
                                        val cur = weightInput.toDoubleOrNull() ?: 0.0
                                        weightInput = String.format(Locale.US, "%.2f", maxOf(0.0, cur - 0.1))
                                    }
                                }

                                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    AdjustmentButton("+100g") {
                                        val cur = weightInput.toDoubleOrNull() ?: 0.0
                                        weightInput = String.format(Locale.US, "%.2f", cur + 0.1)
                                    }
                                    AdjustmentButton("+1kg") {
                                        val cur = weightInput.toDoubleOrNull() ?: 0.0
                                        weightInput = String.format(Locale.US, "%.2f", cur + 1.0)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // SECTION 3: CONDITION / स्थिति (Stitch C05)
            item {
                Column {
                    Text(
                        text = "3. Condition / स्थिति",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )

                    val conditions = listOf(
                        "Clean" to "साफ-सुथरा",
                        "Damaged" to "टूटा-फूटा",
                        "Sorted" to "छाँटा हुआ",
                        "Mixed" to "मिक्स"
                    )

                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        for (row in conditions.chunked(2)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                for ((code, labelHi) in row) {
                                    val isSelected = selectedCondition == code
                                    Card(
                                        modifier = Modifier
                                            .weight(1f)
                                            .height(64.dp)
                                            .clickable { selectedCondition = code },
                                        shape = RoundedCornerShape(12.dp),
                                        colors = CardDefaults.cardColors(
                                            containerColor = if (isSelected) TerracottaPrimary else SurfaceContainer
                                        ),
                                        border = if (isSelected) androidx.compose.foundation.BorderStroke(2.dp, TerracottaPrimary) else null
                                    ) {
                                        Row(
                                            modifier = Modifier
                                                .fillMaxSize()
                                                .padding(horizontal = 12.dp),
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                                        ) {
                                            Box(
                                                modifier = Modifier
                                                    .size(32.dp)
                                                    .clip(CircleShape)
                                                    .background(if (isSelected) Color.White.copy(alpha = 0.2f) else SurfaceContainerHigh),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Text(
                                                    text = when (code) {
                                                        "Clean" -> "✨"
                                                        "Damaged" -> "💥"
                                                        "Sorted" -> "✓"
                                                        else -> "🔀"
                                                    },
                                                    fontSize = 14.sp
                                                )
                                            }

                                            Column {
                                                Text(
                                                    text = code,
                                                    style = MaterialTheme.typography.labelMedium,
                                                    fontWeight = FontWeight.Bold,
                                                    color = if (isSelected) Color.White else OnSurface
                                                )
                                                Text(
                                                    text = labelHi,
                                                    style = MaterialTheme.typography.labelSmall,
                                                    color = if (isSelected) Color.White.copy(alpha = 0.8f) else OnSurfaceVariant
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Coarse Location Strip (Stitch C05)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Text(text = "📍", fontSize = 16.sp)
                                Text(
                                    text = "Sector 4, Yard Gate B",
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                            }
                            Text(
                                text = "Change",
                                style = MaterialTheme.typography.labelSmall,
                                color = TerracottaPrimary,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Text(
                            text = "GPS उपलब्ध नहीं - मोटा स्थान चुनें (Coarse Location Active)",
                            style = MaterialTheme.typography.bodySmall,
                            fontSize = 11.sp,
                            color = OnSurfaceVariant
                        )
                    }
                }
            }

            // ACTION BUTTONS (Stitch C05)
            item {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Button(
                        onClick = {
                            val parsedKg = weightInput.toDoubleOrNull()
                            if (parsedKg == null || parsedKg <= 0) {
                                weightError = "कृपया वैध वजन दर्ज करें (वजन 0 से अधिक होना चाहिए)"
                            } else {
                                val grams = (parsedKg * 1000).toLong()
                                val finalAiSuggestedCode = classificationResult?.let {
                                    if (it.meetsThreshold) it.categoryCode else "ABSTAIN"
                                } ?: initialAiSuggestion
                                val finalAiConfidence = classificationResult?.confidence ?: initialAiConfidence
                                val finalAiModelVersion = classificationResult?.modelVersion ?: "v2.0-mendeley-openimages"

                                onSaveLot(
                                    selectedMaterial.code,
                                    grams,
                                    selectedCondition,
                                    initialPhotoPath,
                                    false,
                                    finalAiSuggestedCode,
                                    finalAiConfidence,
                                    finalAiModelVersion
                                )
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.CheckCircle,
                            contentDescription = null,
                            tint = Color.White
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Save Lot & Print Tag / लॉट सेव करें",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }

                    OutlinedButton(
                        onClick = {
                            val parsedKg = weightInput.toDoubleOrNull() ?: 1.0
                            val grams = (parsedKg * 1000).toLong()
                            val finalAiSuggestedCode = classificationResult?.let {
                                if (it.meetsThreshold) it.categoryCode else "ABSTAIN"
                            } ?: initialAiSuggestion
                            val finalAiConfidence = classificationResult?.confidence ?: initialAiConfidence
                            val finalAiModelVersion = classificationResult?.modelVersion ?: "v2.0-mendeley-openimages"

                            onSaveLot(
                                selectedMaterial.code,
                                grams,
                                selectedCondition,
                                initialPhotoPath,
                                true,
                                finalAiSuggestedCode,
                                finalAiConfidence,
                                finalAiModelVersion
                            )
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(50.dp),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            text = "Save Draft / ड्राफ्ट रखें",
                            style = MaterialTheme.typography.labelLarge,
                            fontWeight = FontWeight.SemiBold,
                            color = OnSurface
                        )
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
private fun AdjustmentButton(text: String, onClick: () -> Unit) {
    Button(
        onClick = onClick,
        shape = RoundedCornerShape(8.dp),
        colors = ButtonDefaults.buttonColors(containerColor = NeutralSurface),
        elevation = ButtonDefaults.buttonElevation(defaultElevation = 1.dp),
        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color = OnSurface
        )
    }
}
