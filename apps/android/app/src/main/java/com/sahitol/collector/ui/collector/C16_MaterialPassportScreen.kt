package com.sahitol.collector.ui.collector

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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.repository.HandoverRepository
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.ui.theme.*

/**
 * Screen C16: Material Passport & Journey Spine (Stitch a1e7f356962f).
 * Features:
 * - 5-stage lifecycle spine: Collection -> Offer -> Handover (Discrepancy) -> Receipt -> Settlement.
 * - Cryptographic SHA-256 event chaining audit trail.
 * - Verified scale snaps and signed QR log reference.
 * - Settlement trigger CTA leading to payment ledger.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C16_MaterialPassportScreen(
    lotId: String,
    handoverRepository: HandoverRepository,
    sessionManager: SessionManager,
    onNavigateBack: () -> Unit,
    onNavigateHome: () -> Unit,
    onNavigatePrices: () -> Unit,
    onNavigateHandover: () -> Unit,
    onNavigateRecord: (String) -> Unit,
    onNavigateSettings: () -> Unit,
    onNavigateSettlement: () -> Unit
) {
    val session by sessionManager.session.collectAsState()
    val alias = session.alias

    val events = remember(lotId) { handoverRepository.getJourneyTimeline(lotId) }
    val proposal = remember(lotId) { handoverRepository.getHandoverProposal(lotId) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Material Passport",
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "सामग्री पासपोर्ट · 5 Events",
                            fontSize = 11.sp,
                            color = OnSurfaceVariant
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = OnSurface)
                    }
                },
                actions = {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = SuccessGreen.copy(alpha = 0.15f),
                        modifier = Modifier.padding(end = 12.dp)
                    ) {
                        Text(
                            text = "Synced 12m ago",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = SuccessGreen,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = NeutralSurface)
            )
        },
        bottomBar = {
            NavigationBar(
                containerColor = NeutralSurface,
                tonalElevation = 8.dp
            ) {
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateHome,
                    icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
                    label = { Text("Home", fontSize = 10.sp) }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigatePrices,
                    icon = { Icon(Icons.Default.ArrowForward, contentDescription = "Prices") },
                    label = { Text("Prices", fontSize = 10.sp) }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateHandover,
                    icon = { Icon(Icons.Default.Place, contentDescription = "Handover") },
                    label = { Text("Handover", fontSize = 10.sp) }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = { onNavigateRecord(proposal.handoverId) },
                    icon = { Icon(Icons.Default.CheckCircle, contentDescription = "QR Record") },
                    label = { Text("QR Record", fontSize = 10.sp) }
                )
                NavigationBarItem(
                    selected = true,
                    onClick = { /* Current */ },
                    icon = { Icon(Icons.Default.Info, contentDescription = "Passport") },
                    label = { Text("Passport", fontSize = 10.sp) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = TerracottaPrimary,
                        selectedTextColor = TerracottaPrimary,
                        indicatorColor = TerracottaPrimary.copy(alpha = 0.15f)
                    )
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateSettings,
                    icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                    label = { Text("Settings", fontSize = 10.sp) }
                )
            }
        },
        containerColor = NeutralSurface
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Material Header Card
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                elevation = CardDefaults.cardElevation(2.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "Cable · तांबा केबल",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = "Lot ID: ${lotId.take(14)}",
                                fontSize = 11.sp,
                                color = OnSurfaceVariant
                            )
                        }
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = PrimaryContainer.copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = "2.3 kg Net",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary,
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                            )
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Condition: Good Quality", fontSize = 11.sp, color = OnSurfaceVariant)
                        Text("Collector: $alias", fontSize = 11.sp, fontWeight = FontWeight.Medium, color = OnSurfaceVariant)
                    }
                }
            }

            // Journey Spine Section Title
            Text(
                text = "Journey Spine / यात्रा इतिहास",
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                color = OnSurface
            )

            // 5 Timeline Events
            events.forEachIndexed { index, event ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.Top
                ) {
                    // Stepper Column: Number Badge & Vertical Spine line
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.width(36.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(24.dp)
                                .background(
                                    if (event.isCompleted) (if (event.isWarningOrDispute) ErrorRed else TerracottaPrimary)
                                    else SurfaceContainerHigh,
                                    CircleShape
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = (index + 1).toString(),
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (event.isCompleted) OnPrimary else OnSurfaceVariant
                            )
                        }

                        if (index < events.size - 1) {
                            Box(
                                modifier = Modifier
                                    .width(2.dp)
                                    .height(90.dp)
                                    .background(OutlineVariantColor.copy(alpha = 0.5f))
                            )
                        }
                    }

                    Spacer(modifier = Modifier.width(10.dp))

                    // Event Card
                    Card(
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = if (event.isWarningOrDispute) ErrorContainer.copy(alpha = 0.15f) else SurfaceContainerLowest
                        ),
                        border = if (event.isWarningOrDispute) androidx.compose.foundation.BorderStroke(1.dp, ErrorRed.copy(alpha = 0.4f)) else null,
                        elevation = CardDefaults.cardElevation(1.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 12.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "${event.titleEn} / ${event.titleHi}",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (event.isWarningOrDispute) ErrorRed else TerracottaPrimary
                                )
                                Text(
                                    text = event.timestamp,
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant
                                )
                            }

                            Text(
                                text = event.description,
                                fontSize = 11.sp,
                                color = OnSurface,
                                lineHeight = 15.sp
                            )

                            if (event.metadataSnippet != null) {
                                Surface(
                                    shape = RoundedCornerShape(6.dp),
                                    color = SurfaceContainerLow,
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Row(
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(
                                            Icons.Default.Place,
                                            contentDescription = null,
                                            tint = TerracottaPrimary,
                                            modifier = Modifier.size(12.dp)
                                        )
                                        Spacer(modifier = Modifier.width(4.dp))
                                        Text(
                                            text = event.metadataSnippet,
                                            fontSize = 10.sp,
                                            color = OnSurfaceVariant
                                        )
                                    }
                                }
                            }

                            // Trigger Settlement CTA on final step
                            if (index == 4) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Button(
                                    onClick = onNavigateSettlement,
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(8.dp),
                                    colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                                ) {
                                    Icon(Icons.Default.ArrowForward, contentDescription = null, modifier = Modifier.size(14.dp))
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text("Trigger Instant Settlement", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }
            }

            // Bottom Ledger Protocol Note
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = SurfaceContainerHigh,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "Immutable audit trail secured via SahiTol Ledger Protocol v2.4 (SHA-256 hash chaining).",
                    fontSize = 11.sp,
                    color = OnSurfaceVariant,
                    modifier = Modifier.padding(12.dp),
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
            }
        }
    }
}
