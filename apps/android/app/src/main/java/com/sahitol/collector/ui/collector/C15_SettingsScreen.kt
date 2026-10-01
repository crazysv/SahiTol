package com.sahitol.collector.ui.collector

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.outlined.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.ui.theme.*

import com.sahitol.collector.domain.locale.NumeralPreference
import com.sahitol.collector.domain.locale.SahiTolStrings

/**
 * Screen C15: Settings, Audio Guidance & Safe Logout (Stitch screens 786c12e6beec and 7bd4f59f2447).
 * Features:
 * - Collector Profile Card with masked phone number and demo mode indicator.
 * - Language selection (English, हिन्दी, मराठी).
 * - Numeral preference (English Digits vs Devanagari Numerals).
 * - Voice weight readout & tap-to-hear repeat preferences.
 * - Safe Logout dialog with pending records warning preserving local SQLite database rows.
 * - Hardware feasibility diagnostic link (S00).
 */
@Composable
fun C15_SettingsScreen(
    collectorAlias: String,
    maskedPhone: String,
    isDemo: Boolean,
    currentLanguage: String,
    currentNumeralPref: NumeralPreference = NumeralPreference.LATIN,
    unsyncedCount: Int,
    onLanguageSelected: (String) -> Unit,
    onNumeralPrefSelected: (NumeralPreference) -> Unit = {},
    onNavigateSync: () -> Unit,
    onOpenDiagnostic: () -> Unit,
    onLogout: () -> Unit,
    onBack: () -> Unit
) {
    var voiceReadoutsEnabled by remember { mutableStateOf(true) }
    var tapToHearEnabled by remember { mutableStateOf(true) }
    var showLogoutDialog by remember { mutableStateOf(false) }

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
                        .statusBarsPadding()
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
                            modifier = Modifier.weight(1f),
                            text = "Settings / सेटिंग्स",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
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
                // Top Profile Banner (Stitch C15)
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            modifier = Modifier.weight(1f),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(52.dp)
                                    .clip(CircleShape)
                                    .background(PrimaryContainer),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = "👤",
                                    fontSize = 24.sp
                                )
                            }

                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = if (isDemo) "DEMO PROFILE" else "Collector ID #SC-8921",
                                    style = MaterialTheme.typography.labelSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = TerracottaPrimary
                                )
                                Text(
                                    text = collectorAlias,
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                                Text(
                                    text = "Phone: $maskedPhone",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = OnSurfaceVariant
                                )
                            }
                        }

                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(12.dp))
                                .background(SurfaceContainerHigh)
                                .padding(horizontal = 10.dp, vertical = 4.dp)
                        ) {
                            Text(
                                text = if (isDemo) "Demo Mode" else "Level 3 Agent",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = OnSurfaceVariant,
                                maxLines = 1
                            )
                        }
                    }
                }
            }

            // Quick Pending Data Banner (Connecting to C14, Stitch C15)
            if (unsyncedCount > 0) {
                item {
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onNavigateSync() },
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = SecondaryContainer)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                modifier = Modifier.weight(1f),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Text(text = "⚡", fontSize = 22.sp)
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = "$unsyncedCount Batches Pending Sync",
                                        style = MaterialTheme.typography.labelMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = OnSecondaryContainer
                                    )
                                    Text(
                                        text = "Scrap logged offline on device. Safe & queued.",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = OnSecondaryContainer.copy(alpha = 0.8f)
                                    )
                                }
                            }
                            Text(
                                text = "View >",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.Bold,
                                color = OnSecondaryContainer
                            )
                        }
                    }
                }
            }

            // Language Selector Card (Stitch C15)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text(
                            text = "Language / भाषा / भाषा",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "Select your preferred assistant voice & interface script.",
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurfaceVariant
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            LanguageOptionButton(
                                title = "English",
                                subtitle = "Default",
                                isSelected = currentLanguage == "en",
                                modifier = Modifier.weight(1f),
                                onClick = { onLanguageSelected("en") }
                            )
                            LanguageOptionButton(
                                title = "हिन्दी",
                                subtitle = "प्रमुख",
                                isSelected = currentLanguage == "hi",
                                modifier = Modifier.weight(1f),
                                onClick = { onLanguageSelected("hi") }
                            )
                            LanguageOptionButton(
                                title = "मराठी",
                                subtitle = "स्थानिक",
                                isSelected = currentLanguage == "mr",
                                modifier = Modifier.weight(1f),
                                onClick = { onLanguageSelected("mr") }
                            )
                        }
                    }
                }
            }

            // Numeral Display Preference Card (R-UX-01 / AT-051 / T036)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text(
                            text = SahiTolStrings.get("pref_numeral_title", currentLanguage),
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = when (currentLanguage) {
                                "hi" -> "वजन और दाम अंग्रेजी (1, 2, 3) या देवनागरी (१, २, ३) अंकों में देखें।"
                                "mr" -> "वजन आणि भाव इंग्रजी (1, 2, 3) किंवा देवनागरी (१, २, ३) अंकांमध्ये पहा."
                                else -> "Display weights, rates, and values in Latin or Devanagari numerals."
                            },
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurfaceVariant
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            LanguageOptionButton(
                                title = "1, 2, 3",
                                subtitle = SahiTolStrings.get("pref_numeral_latin", currentLanguage),
                                isSelected = currentNumeralPref == NumeralPreference.LATIN,
                                modifier = Modifier.weight(1f),
                                onClick = { onNumeralPrefSelected(NumeralPreference.LATIN) }
                            )
                            LanguageOptionButton(
                                title = "१, २, ३",
                                subtitle = SahiTolStrings.get("pref_numeral_devanagari", currentLanguage),
                                isSelected = currentNumeralPref == NumeralPreference.DEVANAGARI,
                                modifier = Modifier.weight(1f),
                                onClick = { onNumeralPrefSelected(NumeralPreference.DEVANAGARI) }
                            )
                        }
                    }
                }
            }

            // Audio & Voice Readout Toggles (Stitch C15)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "Voice Weight Readouts",
                                    style = MaterialTheme.typography.labelLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "Read scale measurements aloud in selected language",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = OnSurfaceVariant
                                )
                            }
                            Switch(
                                checked = voiceReadoutsEnabled,
                                onCheckedChange = { voiceReadoutsEnabled = it },
                                colors = SwitchDefaults.colors(checkedThumbColor = TerracottaPrimary)
                            )
                        }

                        Divider(color = OutlineColor.copy(alpha = 0.2f))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "Tap-to-Hear Repeat",
                                    style = MaterialTheme.typography.labelLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "Tap weight card to replay audio narration",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = OnSurfaceVariant
                                )
                            }
                            Switch(
                                checked = tapToHearEnabled,
                                onCheckedChange = { tapToHearEnabled = it },
                                colors = SwitchDefaults.colors(checkedThumbColor = TerracottaPrimary)
                            )
                        }
                    }
                }
            }

            // Hardware & Diagnostics Card (S00 Feasibility Diagnostic)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Hardware Feasibility Diagnostics (S00)",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "Run on-device camera compression, Room persistence verification, and LiteRT ML benchmark in airplane mode.",
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurfaceVariant
                        )
                        OutlinedButton(
                            onClick = onOpenDiagnostic,
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = "Open Feasibility Diagnostic (S00)",
                                color = TerracottaPrimary,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }

            // Safe Logout Action (Stitch C15 / R-AUTH-03)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, ErrorRed.copy(alpha = 0.3f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Account Session",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "Logging out clears session tokens. Local unacknowledged lots are permanently retained in SQLite.",
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurfaceVariant
                        )
                        Button(
                            onClick = { showLogoutDialog = true },
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = ErrorRed),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = "Log Out Safely",
                                color = Color.White,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }

    // Safe Logout Dialog (R-AUTH-03, Stitch C15)
    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            title = {
                Text(
                    text = "सुरक्षित लॉगआउट / Safe Logout",
                    fontWeight = FontWeight.Bold
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    if (unsyncedCount > 0) {
                        Text(
                            text = "चेतावनी: आपके फोन पर $unsyncedCount अनसिंक्ड रिकॉर्ड हैं।",
                            color = ErrorRed,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Text(
                        text = "लॉगआउट करने पर आपका ऑफलाइन डेटा नष्ट नहीं होगा। अगली बार लॉगिन करने पर यह वापस मिल जाएगा।"
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        showLogoutDialog = false
                        onLogout()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = ErrorRed)
                ) {
                    Text("Log Out Anyway", color = Color.White)
                }
            },
            dismissButton = {
                OutlinedButton(onClick = { showLogoutDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
private fun LanguageOptionButton(
    title: String,
    subtitle: String,
    isSelected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Card(
        modifier = modifier
            .height(72.dp)
            .clickable { onClick() },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) TerracottaPrimary else SurfaceContainerLow
        ),
        border = if (isSelected) androidx.compose.foundation.BorderStroke(2.dp, TerracottaPrimary) else null
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = if (isSelected) Color.White else OnSurface
            )
            Text(
                text = subtitle,
                style = MaterialTheme.typography.labelSmall,
                color = if (isSelected) Color.White.copy(alpha = 0.8f) else OnSurfaceVariant
            )
        }
    }
}
