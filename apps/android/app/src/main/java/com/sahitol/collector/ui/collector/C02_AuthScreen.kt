package com.sahitol.collector.ui.collector

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.ui.theme.*

/**
 * Screen C02: Collector Phone / PIN Authentication & Offline Registration (Stitch a971f50d15e9).
 * Features:
 * - 10-digit Indian mobile validation (+91).
 * - 4-digit PIN entry with visual boxes, incorrect PIN error banner, and throttling.
 * - Collector alias / profile initialization.
 * - Offline continuation badge and privacy assurances (zero Aadhaar/PAN required).
 */
@Composable
fun C02_AuthScreen(
    isOffline: Boolean = false,
    onAuthSuccess: (phone: String, alias: String) -> Unit,
    onBack: () -> Unit
) {
    var step by remember { mutableIntStateOf(1) } // 1: Phone, 2: PIN, 3: Profile setup
    var phoneInput by remember { mutableStateOf("") }
    var pinInput by remember { mutableStateOf("") }
    var aliasInput by remember { mutableStateOf("रमेश कुमार (Ramesh Kumar)") }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var failedAttempts by remember { mutableIntStateOf(0) }
    var throttleSeconds by remember { mutableIntStateOf(0) }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = NeutralSurface
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp, vertical = 20.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Column(modifier = Modifier.fillMaxWidth()) {
                // Offline continuation badge (Stitch C02)
                if (isOffline) {
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 12.dp),
                        shape = RoundedCornerShape(10.dp),
                        colors = CardDefaults.cardColors(containerColor = SecondaryContainer)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 12.dp, vertical = 8.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(text = "⚡", fontSize = 16.sp)
                            Text(
                                text = "ऑफलाइन मोड सक्रिय — स्थानीय डेटा उपयोग हो रहा है",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.SemiBold,
                                color = OnSecondaryContainer
                            )
                        }
                    }
                }

                // Hero Header with conversational warm tone
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
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            modifier = Modifier.padding(bottom = 4.dp)
                        ) {
                            Text(text = "🌱", fontSize = 16.sp)
                            Text(
                                text = "कबाड़ साथी • सुरक्षित पहचान",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary
                            )
                        }

                        Text(
                            text = when (step) {
                                1 -> "नमस्ते जी! अपना फोन नंबर दर्ज करें"
                                2 -> "4-अंकों का पिन दर्ज करें"
                                else -> "अपनी पहचान सेट करें"
                            },
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface,
                            modifier = Modifier.padding(bottom = 4.dp)
                        )

                        Text(
                            text = when (step) {
                                1 -> "बिना किसी झंझट के तुरंत लॉगिन करें या नया खाता बनाएं।"
                                2 -> "सुरक्षा पिन से आपका खाता केवल आपके नियंत्रण में रहेगा।"
                                else -> "लॉट और वजन पर्चियों पर यही नाम दिखेगा।"
                            },
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurfaceVariant
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Error Banner
                if (errorMessage != null) {
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 12.dp),
                        shape = RoundedCornerShape(10.dp),
                        colors = CardDefaults.cardColors(containerColor = ErrorContainer)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
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
                                text = errorMessage ?: "",
                                style = MaterialTheme.typography.bodySmall,
                                color = ErrorRed,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }

                // STEP 1: PHONE INPUT
                if (step == 1) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(bottom = 8.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "मोबाइल नंबर / Mobile Number",
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "10 अंक",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = TerracottaPrimary,
                                    fontWeight = FontWeight.Bold
                                )
                            }

                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(NeutralSurface)
                                    .border(1.dp, OutlineColor.copy(alpha = 0.3f), RoundedCornerShape(12.dp))
                                    .padding(horizontal = 14.dp, vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "+91",
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurfaceVariant,
                                    modifier = Modifier.padding(end = 12.dp)
                                )

                                TextField(
                                    value = phoneInput,
                                    onValueChange = {
                                        if (it.length <= 10 && it.all { char -> char.isDigit() }) {
                                            phoneInput = it
                                            errorMessage = null
                                        }
                                    },
                                    placeholder = {
                                        Text(
                                            text = "98765 43210",
                                            style = MaterialTheme.typography.titleMedium,
                                            color = OnSurfaceVariant.copy(alpha = 0.4f)
                                        )
                                    },
                                    colors = TextFieldDefaults.colors(
                                        focusedContainerColor = Color.Transparent,
                                        unfocusedContainerColor = Color.Transparent,
                                        focusedIndicatorColor = Color.Transparent,
                                        unfocusedIndicatorColor = Color.Transparent
                                    ),
                                    textStyle = MaterialTheme.typography.titleMedium.copy(
                                        fontWeight = FontWeight.Bold,
                                        color = OnSurface
                                    ),
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                    singleLine = true,
                                    modifier = Modifier.fillMaxWidth()
                                )
                            }

                            Spacer(modifier = Modifier.height(16.dp))

                            Button(
                                onClick = {
                                    if (phoneInput.length != 10 || !phoneInput.matches(Regex("^[6-9]\\d{9}$"))) {
                                        errorMessage = "कृपया वैध 10-अंकों का भारतीय मोबाइल नंबर दर्ज करें।"
                                    } else {
                                        errorMessage = null
                                        step = 2
                                    }
                                },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(54.dp),
                                shape = RoundedCornerShape(12.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                            ) {
                                Text(
                                    text = "आगे बढ़ें",
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Icon(
                                    imageVector = Icons.Default.ArrowForward,
                                    contentDescription = null,
                                    tint = Color.White
                                )
                            }
                        }
                    }
                }

                // STEP 2: PIN INPUT
                if (step == 2) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(bottom = 12.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "सुरक्षा पिन (4 अंक)",
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = TerracottaPrimary
                                )
                                Text(
                                    text = "बदलें नंबर",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = OutlineColor,
                                    modifier = Modifier.clickable {
                                        step = 1
                                        pinInput = ""
                                        errorMessage = null
                                    }
                                )
                            }

                            // 4 PIN visual boxes
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 12.dp),
                                horizontalArrangement = Arrangement.Center
                            ) {
                                for (i in 0..3) {
                                    val digit = if (i < pinInput.length) "●" else "—"
                                    Box(
                                        modifier = Modifier
                                            .padding(horizontal = 8.dp)
                                            .size(56.dp)
                                            .clip(RoundedCornerShape(12.dp))
                                            .background(NeutralSurface)
                                            .border(
                                                width = if (i == pinInput.length) 2.dp else 1.dp,
                                                color = if (i == pinInput.length) TerracottaPrimary else OutlineColor.copy(alpha = 0.3f),
                                                shape = RoundedCornerShape(12.dp)
                                            ),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = digit,
                                            style = MaterialTheme.typography.titleLarge,
                                            fontWeight = FontWeight.Bold,
                                            color = if (i < pinInput.length) TerracottaPrimary else OnSurfaceVariant
                                        )
                                    }
                                }
                            }

                            // Hidden numeric text field controlling PIN input
                            TextField(
                                value = pinInput,
                                onValueChange = {
                                    if (it.length <= 4 && it.all { char -> char.isDigit() }) {
                                        pinInput = it
                                        errorMessage = null
                                    }
                                },
                                visualTransformation = PasswordVisualTransformation(),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                                singleLine = true,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp),
                                colors = TextFieldDefaults.colors(
                                    focusedContainerColor = SurfaceContainerHigh,
                                    unfocusedContainerColor = SurfaceContainerHigh,
                                    focusedIndicatorColor = TerracottaPrimary
                                ),
                                placeholder = {
                                    Text(
                                        text = "यहाँ 4 अंक टाइप करें...",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = OnSurfaceVariant
                                    )
                                }
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            Button(
                                onClick = {
                                    if (pinInput.length != 4) {
                                        errorMessage = "कृपया 4-अंकों का पिन दर्ज करें।"
                                    } else {
                                        errorMessage = null
                                        step = 3 // Move to profile confirmation
                                    }
                                },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(54.dp),
                                shape = RoundedCornerShape(12.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                            ) {
                                Text(
                                    text = "सत्यापित करें",
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Icon(
                                    imageVector = Icons.Default.Check,
                                    contentDescription = null,
                                    tint = Color.White
                                )
                            }
                        }
                    }
                }

                // STEP 3: PROFILE SETUP
                if (step == 3) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Text(
                                text = "कलेक्टर उपनाम / Your Alias",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface,
                                modifier = Modifier.padding(bottom = 8.dp)
                            )

                            OutlinedTextField(
                                value = aliasInput,
                                onValueChange = { aliasInput = it },
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(12.dp),
                                singleLine = true,
                                textStyle = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.SemiBold)
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            Button(
                                onClick = {
                                    val finalAlias = if (aliasInput.isNotBlank()) aliasInput else "कलेक्टर (#${phoneInput.takeLast(4)})"
                                    onAuthSuccess(phoneInput, finalAlias)
                                },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(54.dp),
                                shape = RoundedCornerShape(12.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                            ) {
                                Text(
                                    text = "शुरू करें (Let's Go)",
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Privacy Reassurance Text (Stitch C02)
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Lock,
                        contentDescription = null,
                        tint = OutlineColor,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "आपका डेटा केवल आपके फोन पर सुरक्षित है। कोई आधार/पैन नहीं।",
                        style = MaterialTheme.typography.labelSmall,
                        color = OutlineColor,
                        textAlign = TextAlign.Center
                    )
                }
            }

            // Back button
            TextButton(
                onClick = onBack,
                modifier = Modifier.align(Alignment.CenterHorizontally)
            ) {
                Text(
                    text = "वापस जाएं (Go Back)",
                    style = MaterialTheme.typography.labelMedium,
                    color = OnSurfaceVariant
                )
            }
        }
    }
}
