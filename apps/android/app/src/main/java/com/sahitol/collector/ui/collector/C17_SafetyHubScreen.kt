package com.sahitol.collector.ui.collector

import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.domain.audio.AudioGrammar
import com.sahitol.collector.domain.audio.AudioGuidanceManager
import com.sahitol.collector.domain.audio.AudioPlaybackEvent
import com.sahitol.collector.domain.safety.*
import com.sahitol.collector.ui.theme.*

/**
 * Screen C17: Contextual Safety Hub & Hazard Guides (R-SAFE-01, T035, T039).
 * Stitch Screen ID: 1579fe53bac5 (Project 245073995801566548).
 * Provides trilingual hazard alerts, strict prohibitions, safer collection protocols,
 * and pre-generated offline Hindi/Marathi voice briefings.
 */
@Composable
fun C17_SafetyHubScreen(
    initialCardId: String? = null,
    initialMaterialId: String? = null,
    onNavigateBack: () -> Unit = {}
) {
    val context = LocalContext.current
    val audioManager = remember { AudioGuidanceManager(context) }

    // Resolve initial card
    val allCards = remember { SafetyContentManager.getAllCards() }
    val initialCard = remember(initialCardId, initialMaterialId) {
        when {
            initialCardId != null -> SafetyContentManager.getCard(initialCardId)
            initialMaterialId != null -> SafetyContentManager.getCardForMaterial(initialMaterialId)
            else -> SafetyContentManager.getCard("SC-CRT-01")
        } ?: allCards.first()
    }

    var activeCard by remember { mutableStateOf(initialCard) }
    var currentLang by remember { mutableStateOf("hi") } // Default Hindi for vernacular field collectors
    var feedbackReported by remember { mutableStateOf(false) }

    // Audio playback state
    val playbackEvent by audioManager.playbackState.collectAsState()
    val isPlaying = playbackEvent is AudioPlaybackEvent.Playing

    // Clean up audio on screen disposal or language/card change
    DisposableEffect(activeCard, currentLang) {
        onDispose {
            audioManager.stop()
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            audioManager.release()
        }
    }

    val localizedContent = activeCard.localized(currentLang)

    Scaffold(
        topBar = {
            // Header matching Stitch C17
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = NeutralSurface,
                shadowElevation = 2.dp
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
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        IconButton(onClick = {
                            audioManager.stop()
                            onNavigateBack()
                        }) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Back",
                                tint = OnSurface
                            )
                        }
                        Text(
                            text = when (currentLang) {
                                "hi" -> "सुरक्षा लाइब्रेरी"
                                "mr" -> "सुरक्षा ग्रंथालय"
                                else -> "SAFETY LIBRARY"
                            },
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                    }

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                                .background(SurfaceContainerHigh),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(text = "🛡", fontSize = 18.sp)
                        }
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(CircleShape)
                                .background(TerracottaPrimary),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Person,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(18.dp)
                            )
                        }
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
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 1. Top Language Selector & Offline Ready Indicator (Stitch C17)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Language buttons
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(SurfaceContainer)
                        .padding(4.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    LangButton(
                        text = "English",
                        isSelected = currentLang == "en",
                        onClick = {
                            audioManager.stop()
                            currentLang = "en"
                        }
                    )
                    LangButton(
                        text = "हिन्दी",
                        isSelected = currentLang == "hi",
                        onClick = {
                            audioManager.stop()
                            currentLang = "hi"
                        }
                    )
                    LangButton(
                        text = "मराठी",
                        isSelected = currentLang == "mr",
                        onClick = {
                            audioManager.stop()
                            currentLang = "mr"
                        }
                    )
                }

                // Offline Ready Badge
                Row(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(MustardSecondary.copy(alpha = 0.15f))
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(text = "📡", fontSize = 12.sp)
                    Text(
                        text = when (currentLang) {
                            "hi" -> "ऑफ़लाइन उपलब्ध"
                            "mr" -> "ऑफलाइन उपलब्ध"
                            else -> "Offline Ready"
                        },
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = MustardSecondary
                    )
                }
            }

            // 2. Material Detail Header Card (Stitch C17)
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainer),
                elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.Top
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                val badgeBg = when (activeCard.hazardLevel) {
                                    HazardLevel.CRITICAL -> Color(0xFFFFDAD6)
                                    HazardLevel.HIGH -> PrimaryContainer
                                    HazardLevel.MODERATE -> SecondaryContainer
                                }
                                val badgeText = when (activeCard.hazardLevel) {
                                    HazardLevel.CRITICAL -> Color(0xFF93000A)
                                    HazardLevel.HIGH -> Color.White
                                    HazardLevel.MODERATE -> OnSecondaryContainer
                                }
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(4.dp))
                                        .background(badgeBg)
                                        .padding(horizontal = 6.dp, vertical = 2.dp)
                                ) {
                                    Text(
                                        text = when (activeCard.hazardLevel) {
                                            HazardLevel.CRITICAL -> when (currentLang) {
                                                "hi" -> "अत्यंत गंभीर खतरा"
                                                "mr" -> "अत्यंत गंभीर धोका"
                                                else -> "CRITICAL HAZARD"
                                            }
                                            HazardLevel.HIGH -> when (currentLang) {
                                                "hi" -> "गंभीर खतरा"
                                                "mr" -> "गंभीर धोका"
                                                else -> "HIGH HAZARD"
                                            }
                                            HazardLevel.MODERATE -> when (currentLang) {
                                                "hi" -> "मध्यम खतरा"
                                                "mr" -> "मध्यम धोका"
                                                else -> "MODERATE HAZARD"
                                            }
                                        },
                                        style = MaterialTheme.typography.labelSmall,
                                        fontWeight = FontWeight.Bold,
                                        color = badgeText,
                                        fontSize = 11.sp
                                    )
                                }
                                Text(
                                    text = "#${activeCard.id}",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = OnSurfaceVariant
                                )
                            }
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = localizedContent.title,
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = localizedContent.subtitle,
                                style = MaterialTheme.typography.bodySmall,
                                color = OnSurfaceVariant
                            )
                        }

                        Box(
                            modifier = Modifier
                                .size(50.dp)
                                .clip(RoundedCornerShape(12.dp))
                                .background(TerracottaPrimary.copy(alpha = 0.15f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = when (activeCard.id) {
                                    "SC-CAB-01" -> "🔌"
                                    "SC-PCB-01" -> "💻"
                                    "SC-CRT-01" -> "📺"
                                    "SC-BAT-01" -> "🔋"
                                    "SC-BAT-02" -> "⚡"
                                    "SC-BAT-03" -> "🪫"
                                    "SC-DAM-01" -> "⚠️"
                                    "SC-PLA-01" -> "♻️"
                                    else -> "📦"
                                },
                                fontSize = 26.sp
                            )
                        }
                    }

                    // Audio Player Affordance Box (Stitch C17)
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        color = NeutralSurface,
                        border = BorderStroke(1.5.dp, OutlineVariantColor.copy(alpha = 0.5f))
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                IconButton(
                                    onClick = {
                                        if (isPlaying) {
                                            audioManager.stop()
                                        } else {
                                            val clips = AudioGrammar.speakSafety(activeCard.id, currentLang)
                                            audioManager.playQueue(clips)
                                        }
                                    },
                                    modifier = Modifier
                                        .size(48.dp)
                                        .clip(CircleShape)
                                        .background(TerracottaPrimary)
                                ) {
                                    Text(
                                        text = if (isPlaying) "⏹" else "🔊",
                                        fontSize = 20.sp,
                                        color = Color.White
                                    )
                                }

                                Column {
                                    Text(
                                        text = when (currentLang) {
                                            "hi" -> "ऑडियो गाइड सुनें"
                                            "mr" -> "ऑडिओ मार्गदर्शक ऐका"
                                            else -> "Listen to Audio Guide"
                                        },
                                        style = MaterialTheme.typography.labelMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = OnSurface
                                    )
                                    Text(
                                        text = if (isPlaying) {
                                            when (currentLang) {
                                                "hi" -> "ऑडियो चल रहा है..."
                                                "mr" -> "ऑडिओ वाजत आहे..."
                                                else -> "Playing safety briefing..."
                                            }
                                        } else {
                                            when (currentLang) {
                                                "hi" -> "सुरक्षा नियम सुनने के लिए टैप करें"
                                                "mr" -> "सुरक्षा नियम ऐकण्यासाठी टॅप करा"
                                                else -> "Tap to play safety briefing"
                                            }
                                        },
                                        style = MaterialTheme.typography.bodySmall,
                                        color = if (isPlaying) TerracottaPrimary else OnSurfaceVariant,
                                        fontSize = 12.sp
                                    )
                                }
                            }

                            // Soundwave pulses
                            Row(
                                horizontalArrangement = Arrangement.spacedBy(3.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                SoundwaveBar(isPlaying = isPlaying, delayMillis = 0, baseHeight = 16)
                                SoundwaveBar(isPlaying = isPlaying, delayMillis = 100, baseHeight = 24)
                                SoundwaveBar(isPlaying = isPlaying, delayMillis = 200, baseHeight = 18)
                            }
                        }
                    }
                }
            }

            // 3. Critical Hazards Section ("Watch-For Warnings" / Stitch C17)
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = null,
                            tint = ErrorRed,
                            modifier = Modifier.size(20.dp)
                        )
                        Text(
                            text = when (currentLang) {
                                "hi" -> "मुख्य खतरे (चेतावनी)"
                                "mr" -> "प्रमुख धोके (सावधान)"
                                else -> "Watch-For Warnings"
                            },
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                    }
                }

                // Hazard Description Card
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = ErrorRed.copy(alpha = 0.08f)),
                    border = BorderStroke(1.5.dp, ErrorRed.copy(alpha = 0.25f))
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.Top
                    ) {
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .background(ErrorRed),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(text = "⚡", fontSize = 18.sp, color = Color.White)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = when (currentLang) {
                                    "hi" -> "घातक प्रभाव व नुकसान"
                                    "mr" -> "धोकादायक परिणाम व इजा"
                                    else -> "Hazardous Impact & Health Risk"
                                },
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.Bold,
                                color = ErrorRed
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = localizedContent.hazardWarning,
                                style = MaterialTheme.typography.bodySmall,
                                color = OnSurface,
                                lineHeight = 18.sp
                            )
                        }
                    }
                }
            }

            // 4. Strictly Avoid Section ("Strictly Avoid" / Stitch C17)
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Text(text = "⛔", fontSize = 18.sp)
                    Text(
                        text = when (currentLang) {
                            "hi" -> "ये कभी न करें (सख्त मना)"
                            "mr" -> "कधीही करू नका (सक्त मनाई)"
                            else -> "Strictly Avoid"
                        },
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                }

                // 3 Prohibitions Grid
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    activeCard.prohibitions.forEach { prohib ->
                        val label = when (currentLang) {
                            "hi" -> prohib.hiLabel
                            "mr" -> prohib.mrLabel
                            else -> prohib.enLabel
                        }
                        Card(
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(12.dp),
                            colors = CardDefaults.cardColors(containerColor = SurfaceContainer),
                            border = BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.3f))
                        ) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(10.dp),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(36.dp)
                                        .clip(CircleShape)
                                        .background(ErrorRed.copy(alpha = 0.12f)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(text = "🚫", fontSize = 18.sp)
                                }
                                Text(
                                    text = label,
                                    style = MaterialTheme.typography.labelSmall,
                                    fontWeight = FontWeight.SemiBold,
                                    textAlign = TextAlign.Center,
                                    fontSize = 11.sp,
                                    color = OnSurface,
                                    maxLines = 2
                                )
                            }
                        }
                    }
                }
            }

            // 5. Safer Collector Steps Section (Stitch C17)
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = null,
                        tint = TerracottaPrimary,
                        modifier = Modifier.size(20.dp)
                    )
                    Text(
                        text = when (currentLang) {
                            "hi" -> "कलेक्टर के लिए सुरक्षित नियम"
                            "mr" -> "कलेक्टरसाठी सुरक्षित नियमावली"
                            else -> "Safer Collector Steps"
                        },
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                }

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainer),
                    border = BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.3f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        activeCard.steps.forEach { step ->
                            val stepTitle = when (currentLang) {
                                "hi" -> step.hiTitle
                                "mr" -> step.mrTitle
                                else -> step.enTitle
                            }
                            val stepDesc = when (currentLang) {
                                "hi" -> step.hiDesc
                                "mr" -> step.mrDesc
                                else -> step.enDesc
                            }
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp),
                                verticalAlignment = Alignment.Top
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(28.dp)
                                        .clip(CircleShape)
                                        .background(TerracottaPrimary),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = "${step.stepNumber}",
                                        style = MaterialTheme.typography.labelSmall,
                                        fontWeight = FontWeight.Bold,
                                        color = Color.White
                                    )
                                }
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = stepTitle,
                                        style = MaterialTheme.typography.labelMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = OnSurface
                                    )
                                    Spacer(modifier = Modifier.height(2.dp))
                                    Text(
                                        text = stepDesc,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = OnSurfaceVariant,
                                        lineHeight = 18.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // 6. Other Material Libraries Selector Bar (Stitch C17)
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = when (currentLang) {
                        "hi" -> "अन्य सामग्री सुरक्षा गाइड"
                        "mr" -> "इतर साहित्य सुरक्षा मार्गदर्शक"
                        else -> "OTHER MATERIAL LIBRARIES"
                    },
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                    color = OnSurfaceVariant
                )

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    allCards.forEach { card ->
                        val isSelected = card.id == activeCard.id
                        val shortName = when (card.id) {
                            "SC-CRT-01" -> when (currentLang) { "hi" -> "CRT टीवी" "mr" -> "CRT टीव्ही" else -> "CRT Tube" }
                            "SC-PCB-01" -> when (currentLang) { "hi" -> "मदरबोर्ड / PCB" "mr" -> "PCB बोर्ड" else -> "PCB Boards" }
                            "SC-BAT-02" -> when (currentLang) { "hi" -> "लिथियम बैटरी" "mr" -> "लिथियम बॅटरी" else -> "Li-Ion Battery" }
                            "SC-BAT-01" -> when (currentLang) { "hi" -> "लेड-एसिड बैटरी" "mr" -> "मोठी बॅटरी" else -> "Lead Battery" }
                            "SC-CAB-01" -> when (currentLang) { "hi" -> "तांबा तार / केबल" "mr" -> "तांब्याची वायर" else -> "Copper Wire" }
                            "SC-MIX-01" -> when (currentLang) { "hi" -> "मिश्रित कबाड़" "mr" -> "मिश्रित भंगार" else -> "Mixed Scrap" }
                            "SC-PLA-01" -> when (currentLang) { "hi" -> "इलेक्ट्रॉनिक प्लास्टिक" "mr" -> "प्लास्टिक कव्हर" else -> "Plastics" }
                            "SC-DAM-01" -> when (currentLang) { "hi" -> "लीक / गरम कबाड़" "mr" -> "धोकादायक गळती" else -> "Damaged Scrap" }
                            else -> card.id
                        }
                        Button(
                            onClick = {
                                audioManager.stop()
                                activeCard = card
                            },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (isSelected) TerracottaPrimary else SurfaceContainer,
                                contentColor = if (isSelected) Color.White else OnSurface
                            ),
                            shape = RoundedCornerShape(12.dp),
                            border = if (!isSelected) BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.4f)) else null,
                            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 8.dp)
                        ) {
                            Text(
                                text = shortName,
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.SemiBold
                            )
                        }
                    }
                }
            }

            // 7. Source Attribution & Feedback Footer (Stitch C17)
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                color = SurfaceContainerHigh
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "SahiTol Safety Standards Board",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "Verified under Central E-Waste (Management) Rules 2022. No instructional dismantling advice is provided.",
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurfaceVariant,
                            fontSize = 11.sp,
                            lineHeight = 14.sp
                        )
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    OutlinedButton(
                        onClick = { feedbackReported = true },
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                    ) {
                        Text(
                            text = if (feedbackReported) "Recorded" else "Report Issue",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = if (feedbackReported) SuccessGreen else TerracottaPrimary
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun LangButton(
    text: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(if (isSelected) TerracottaPrimary else Color.Transparent)
            .clickable { onClick() }
            .padding(horizontal = 10.dp, vertical = 6.dp)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
            color = if (isSelected) Color.White else OnSurfaceVariant
        )
    }
}

@Composable
private fun SoundwaveBar(
    isPlaying: Boolean,
    delayMillis: Int,
    baseHeight: Int
) {
    val infiniteTransition = rememberInfiniteTransition(label = "soundwave")
    val heightScale by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 400 + delayMillis, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "height"
    )

    val actualHeight = if (isPlaying) (baseHeight * heightScale).dp else 8.dp

    Box(
        modifier = Modifier
            .width(3.dp)
            .height(actualHeight)
            .clip(RoundedCornerShape(2.dp))
            .background(if (isPlaying) TerracottaPrimary else OnSurfaceVariant.copy(alpha = 0.4f))
    )
}
