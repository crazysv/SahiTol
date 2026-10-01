package com.sahitol.collector.ui.collector

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

/**
 * Screen C03: Collector Dashboard & Work Table (Stitch 89622e073daa).
 * Features:
 * - Dominant hero CTA: "सामग्री बेचें / SELL MATERIAL & WEIGH".
 * - Quick status strips for prices, lots, earnings, recyclers, and safety.
 * - Paper-slips ledger: Recent lots rendered directly from Room database.
 * - Bottom navigation bar linking Home (C03), Sync Centre (C14), and Settings (C15).
 */
@Composable
fun C03_HomeScreen(
    collectorAlias: String,
    isDemo: Boolean,
    unsyncedCount: Int,
    lots: List<LotEntity>,
    onAddLot: () -> Unit,
    onNavigateSync: () -> Unit,
    onNavigateSettings: () -> Unit,
    onNavigatePrices: () -> Unit = {},
    onNavigateDirectory: () -> Unit = {},
    onNavigateLedger: () -> Unit = {},
    onNavigateSafety: () -> Unit = {},
    onLotClick: (String) -> Unit = {}
) {
    val totalWeightKg = remember(lots) {
        lots.sumOf { it.estimatedWeightG } / 1000.0
    }

    Scaffold(
        topBar = {
            // App Top Bar (Stitch C03)
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
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(TerracottaPrimary)
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(
                                text = "सहीTol",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        }
                        Column {
                            Text(
                                text = "SahiTol",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = if (isDemo) "DEMO MODE" else "Collector App",
                                style = MaterialTheme.typography.labelSmall,
                                fontSize = 10.sp,
                                color = if (isDemo) TerracottaPrimary else OnSurfaceVariant
                            )
                        }
                    }

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // Offline Ready Badge
                        Row(
                            modifier = Modifier
                                .clip(RoundedCornerShape(16.dp))
                                .background(SurfaceContainerHigh)
                                .clickable { onNavigateSync() }
                                .padding(horizontal = 10.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(CircleShape)
                                    .background(if (unsyncedCount > 0) SecondaryContainer else SuccessGreen)
                            )
                            Text(
                                text = if (unsyncedCount > 0) "$unsyncedCount to Sync" else "Synced",
                                style = MaterialTheme.typography.labelSmall,
                                color = OnSurfaceVariant,
                                fontWeight = FontWeight.SemiBold
                            )
                        }

                        // Avatar
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                                .background(TerracottaPrimary)
                                .clickable { onNavigateSettings() },
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = collectorAlias.take(1),
                                color = Color.White,
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp
                            )
                        }
                    }
                }
            }
        },
        bottomBar = {
            // Bottom Navigation Bar (Stitch C03)
            NavigationBar(
                containerColor = SurfaceContainerLow,
                tonalElevation = 4.dp
            ) {
                NavigationBarItem(
                    selected = true,
                    onClick = { /* Already on Home */ },
                    icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
                    label = { Text("Home / मुख्य") },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = TerracottaPrimary,
                        selectedTextColor = TerracottaPrimary,
                        indicatorColor = PrimaryContainer.copy(alpha = 0.2f)
                    )
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigatePrices,
                    icon = { Icon(Icons.Default.ArrowForward, contentDescription = "Prices") },
                    label = { Text("Prices / भाव") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateSync,
                    icon = {
                        BadgedBox(badge = {
                            if (unsyncedCount > 0) {
                                Badge(containerColor = TerracottaPrimary) {
                                    Text(unsyncedCount.toString())
                                }
                            }
                        }) {
                            Icon(Icons.Default.Refresh, contentDescription = "Sync")
                        }
                    },
                    label = { Text("Sync / सिंक") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateSettings,
                    icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                    label = { Text("Settings / सेटिंग्स") }
                )
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
                // Work Table Header (Stitch C03)
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "${collectorAlias} का बही-खाता",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceVariant,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            text = "आज का बही-खाता",
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                    }

                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(SecondaryContainer)
                            .padding(horizontal = 10.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.CheckCircle,
                            contentDescription = null,
                            tint = OnSecondaryContainer,
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = "Duty Active",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = OnSecondaryContainer
                        )
                    }
                }
            }

            // Hero CTA Button: SELL MATERIAL / सामग्री बेचें (Stitch C03)
            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onAddLot() },
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = TerracottaPrimary),
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(44.dp)
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(Color.White.copy(alpha = 0.2f)),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(text = "⚖", fontSize = 24.sp)
                            }
                            Column {
                                Text(
                                    text = "सामग्री बेचें",
                                    style = MaterialTheme.typography.titleLarge,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Text(
                                    text = "SELL MATERIAL & WEIGH",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = PrimaryContainer.copy(alpha = 0.9f),
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                        }

                        Icon(
                            imageVector = Icons.Default.ArrowForward,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier
                                .size(36.dp)
                                .clip(RoundedCornerShape(10.dp))
                                .background(Color.White.copy(alpha = 0.15f))
                                .padding(6.dp)
                        )
                    }
                }
            }

            // Quick Status Strips (Horizontal Scrollable Marquee, Stitch C03)
            item {
                Column {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "त्वरित स्थिति / Quick Status",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Bold,
                            color = OnSurfaceVariant
                        )
                        Text(
                            text = "लाइव बाज़ार",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = TerracottaPrimary
                        )
                    }

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        QuickStatusCard(
                            label = "आज के भाव",
                            value = "₹24.50",
                            unit = "/kg",
                            subtitle = "KABADI RATES",
                            accentColor = MustardSecondary,
                            onClick = onNavigatePrices
                        )
                        QuickStatusCard(
                            label = "मेरे लॉट",
                            value = "${lots.size} Lots",
                            unit = "",
                            subtitle = String.format(Locale.getDefault(), "%.1f kg total", totalWeightKg),
                            accentColor = TerracottaPrimary
                        )
                        QuickStatusCard(
                            label = "कमाई",
                            value = "₹12,450",
                            unit = "",
                            subtitle = "This Week",
                            accentColor = SuccessGreen,
                            onClick = onNavigateLedger
                        )
                        QuickStatusCard(
                            label = "रिसाइकिलर",
                            value = "4 Active",
                            unit = "",
                            subtitle = "Nearest 2.4km",
                            accentColor = TerracottaPrimary,
                            onClick = onNavigateDirectory
                        )
                        QuickStatusCard(
                            label = "सुरक्षा",
                            value = "Verified",
                            unit = "",
                            subtitle = "Safety Guides",
                            accentColor = MustardSecondary,
                            onClick = onNavigateSafety
                        )
                    }
                }
            }

            // Recent Lots Section Header (Stitch C03)
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "हाल की सामग्री / Recent Lots (${lots.size})",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                    Text(
                        text = if (unsyncedCount > 0) "$unsyncedCount Unsynced" else "All Synced",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (unsyncedCount > 0) TerracottaPrimary else SuccessGreen,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            // Paper Slips / Recent Lots Table (Stitch C03)
            if (lots.isEmpty()) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(text = "📦", fontSize = 32.sp)
                            Text(
                                text = "अभी कोई लॉट नहीं है।",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = "सामग्री का तौल दर्ज करने के लिए ऊपर 'सामग्री बेचें' पर टैप करें।",
                                style = MaterialTheme.typography.bodySmall,
                                color = OnSurfaceVariant
                            )
                        }
                    }
                }
            } else {
                items(lots) { lot ->
                    Box(modifier = Modifier.clickable { onLotClick(lot.lotId) }) {
                        LotSlipCard(lot = lot)
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
private fun QuickStatusCard(
    label: String,
    value: String,
    unit: String,
    subtitle: String,
    accentColor: Color,
    onClick: () -> Unit = {}
) {
    Card(
        modifier = Modifier
            .width(135.dp)
            .height(95.dp)
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(10.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = OnSurfaceVariant
            )
            Row(verticalAlignment = Alignment.Bottom) {
                Text(
                    text = value,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = OnSurface
                )
                if (unit.isNotEmpty()) {
                    Text(
                        text = unit,
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceVariant,
                        modifier = Modifier.padding(bottom = 2.dp, start = 2.dp)
                    )
                }
            }
            Text(
                text = subtitle,
                style = MaterialTheme.typography.labelSmall,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                color = accentColor
            )
        }
    }
}

@Composable
private fun LotSlipCard(lot: LotEntity) {
    val sdf = remember { SimpleDateFormat("dd MMM, hh:mm a", Locale.getDefault()) }
    val formattedDate = remember(lot.createdAt) { sdf.format(Date(lot.createdAt)) }
    val weightKg = lot.estimatedWeightG / 1000.0

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
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
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(SurfaceContainerHigh),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = when (lot.materialCode) {
                            "PCB" -> "💻"
                            "CRT" -> "📺"
                            "LCD" -> "🖥"
                            "CABLE" -> "🔌"
                            "BATTERY" -> "🔋"
                            "MOTOR" -> "⚙"
                            else -> "📦"
                        },
                        fontSize = 20.sp
                    )
                }

                Column {
                    Text(
                        text = lot.materialCode,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                    Text(
                        text = formattedDate,
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceVariant
                    )
                }
            }

            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = String.format(Locale.getDefault(), "%.2f kg", weightKg),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TerracottaPrimary
                )
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(6.dp))
                        .background(
                            if (lot.syncStatus == "SYNCED") SuccessGreen.copy(alpha = 0.15f)
                            else PrimaryContainer.copy(alpha = 0.2f)
                        )
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                ) {
                    Text(
                        text = if (lot.syncStatus == "SYNCED") "Synced" else "Saved on phone",
                        style = MaterialTheme.typography.labelSmall,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (lot.syncStatus == "SYNCED") SuccessGreen else TerracottaPrimary
                    )
                }
            }
        }
    }
}
