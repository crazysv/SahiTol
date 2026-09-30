package com.sahitol.collector.ui.collector

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.repository.PaymentRepository
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.domain.payment.CollectorLedgerSummary
import com.sahitol.collector.domain.payment.TransactionSummary
import com.sahitol.collector.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C12_LedgerScreen(
    paymentRepository: PaymentRepository,
    sessionManager: SessionManager,
    onNavigateBack: () -> Unit,
    onNavigateHome: () -> Unit,
    onNavigatePrices: () -> Unit,
    onNavigateHandover: () -> Unit,
    onNavigateTransaction: (String) -> Unit,
    onNavigateSync: () -> Unit,
    onNavigateSettings: () -> Unit
) {
    val session by sessionManager.session.collectAsState()
    val alias = session.alias

    var selectedFilter by remember { mutableStateOf("ALL") }
    var selectedMonth by remember { mutableStateOf("2026-09") }

    val transactions by paymentRepository.transactions.collectAsState()
    val summary = remember(transactions, selectedMonth, selectedFilter) {
        paymentRepository.getLedgerSummary(selectedMonth, selectedFilter)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = TerracottaPrimary
                        ) {
                            Text(
                                text = "सहीTol",
                                color = OnPrimary,
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                        Column {
                            Text(
                                text = "SahiTol",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = "Collector Ledger · $alias",
                                fontSize = 10.sp,
                                color = OnSurfaceVariant
                            )
                        }
                    }
                },
                actions = {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = SurfaceContainerHigh,
                        modifier = Modifier.padding(end = 8.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(6.dp)
                                    .background(Color(0xFF735C00), CircleShape)
                            )
                            Text(
                                text = "Offline Ready",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Medium,
                                color = Color(0xFF735C00)
                            )
                        }
                    }

                    Box(
                        modifier = Modifier
                            .padding(end = 12.dp)
                            .size(32.dp)
                            .background(TerracottaPrimary, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = alias.take(1),
                            color = OnPrimary,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = SurfaceBright
                )
            )
        },
        bottomBar = {
            NavigationBar(
                containerColor = SurfaceBright,
                tonalElevation = 8.dp
            ) {
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateHome,
                    icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
                    label = { Text("Home", fontSize = 11.sp) }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateHandover,
                    icon = { Icon(Icons.Default.List, contentDescription = "Timeline") },
                    label = { Text("Timeline", fontSize = 11.sp) }
                )
                NavigationBarItem(
                    selected = true,
                    onClick = { /* already here */ },
                    icon = { Icon(Icons.Default.ShoppingCart, contentDescription = "Earnings") },
                    label = { Text("Earnings", fontSize = 11.sp, fontWeight = FontWeight.Bold) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = OnPrimary,
                        selectedTextColor = TerracottaPrimary,
                        indicatorColor = TerracottaPrimary
                    )
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateSync,
                    icon = { Icon(Icons.Default.Refresh, contentDescription = "Sync") },
                    label = { Text("Sync", fontSize = 11.sp) }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateSettings,
                    icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                    label = { Text("Settings", fontSize = 11.sp) }
                )
            }
        },
        containerColor = SurfaceBright
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Header & Subtitle
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "मेरी कमाई / My Earnings",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                    Text(
                        text = "Daily scrap collection ledger & verified dues",
                        fontSize = 12.sp,
                        color = OnSurfaceVariant
                    )
                }

                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = Color(0xFFFED65B)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = null,
                            tint = Color(0xFF745C00),
                            modifier = Modifier.size(13.dp)
                        )
                        Text(
                            text = "Live Ledger",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF745C00)
                        )
                    }
                }
            }

            // Demo mode isolation notice
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Icon(
                        imageVector = Icons.Default.Info,
                        contentDescription = null,
                        tint = TerracottaPrimary,
                        modifier = Modifier.size(18.dp)
                    )
                    Column {
                        Text(
                            text = "Demo mode isolation active / डेमो खाता",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "Transactions shown are stored locally on this device. Sync with yard manager to clear dues.",
                            fontSize = 11.sp,
                            color = OnSurfaceVariant
                        )
                    }
                }
            }

            // Prominent Earnings Summary Card (Terracotta)
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = PrimaryContainer),
                elevation = CardDefaults.cardElevation(2.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.Top
                    ) {
                        Column {
                            Text(
                                text = "TOTAL AGREED / कुल तय राशि",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnPrimary.copy(alpha = 0.85f),
                                letterSpacing = 0.5.sp
                            )
                            Text(
                                text = "₹${summary.totalAgreedInr.toInt()}",
                                fontSize = 28.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnPrimary
                            )
                        }

                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                text = "REMAINING DUES",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnPrimary.copy(alpha = 0.85f)
                            )
                            Text(
                                text = "₹${summary.remainingDuesInr.toInt()}",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFFFFE088)
                            )
                        }
                    }

                    HorizontalDivider(color = OnPrimary.copy(alpha = 0.2f), thickness = 1.dp)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(
                                text = "Acknowledged Paid",
                                fontSize = 11.sp,
                                color = OnPrimary.copy(alpha = 0.8f)
                            )
                            Text(
                                text = "₹${summary.acknowledgedPaidInr.toInt()}",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnPrimary
                            )
                        }

                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                text = "Saved on Device",
                                fontSize = 11.sp,
                                color = OnPrimary.copy(alpha = 0.8f)
                            )
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(6.dp)
                                        .background(Color(0xFFFFE088), CircleShape)
                                )
                                Text(
                                    text = "${summary.savedOnDevicePendingSlips} Slips Pending",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnPrimary
                                )
                            }
                        }
                    }
                }
            }

            // Month Selector
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainer)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(
                        onClick = { selectedMonth = "2026-08" },
                        modifier = Modifier.size(36.dp)
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Previous Month",
                            tint = OnSurface
                        )
                    }

                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = summary.monthLabelEn,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = summary.monthLabelHi,
                            fontSize = 11.sp,
                            color = OnSurfaceVariant
                        )
                    }

                    IconButton(
                        onClick = { selectedMonth = "2026-09" },
                        modifier = Modifier.size(36.dp)
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                            contentDescription = "Next Month",
                            tint = OnSurface
                        )
                    }
                }
            }

            // Filter Chips
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChipItem(
                    label = "All Entries (${summary.transactions.size})",
                    selected = selectedFilter == "ALL",
                    onClick = { selectedFilter = "ALL" }
                )
                FilterChipItem(
                    label = "Dues Remaining (${summary.transactions.count { it.remainingDuesPaise > 0L }})",
                    selected = selectedFilter == "DUES_REMAINING",
                    onClick = { selectedFilter = "DUES_REMAINING" }
                )
                FilterChipItem(
                    label = "Waiting Sync (${summary.transactions.count { it.isOfflineSavedOnly || it.payments.any { p -> p.syncState == "SAVED_LOCAL_ONLY" } }})",
                    selected = selectedFilter == "WAITING_SYNC",
                    onClick = { selectedFilter = "WAITING_SYNC" }
                )
                FilterChipItem(
                    label = "Disputed (${summary.disputedCount})",
                    selected = selectedFilter == "DISPUTED",
                    onClick = { selectedFilter = "DISPUTED" }
                )
            }

            // Transaction Cards Stream
            Column(
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                summary.transactions.forEach { tx ->
                    TransactionLedgerCard(
                        transaction = tx,
                        onClick = { onNavigateTransaction(tx.transactionId) }
                    )
                }

                if (summary.transactions.isEmpty()) {
                    Card(
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Info,
                                contentDescription = null,
                                tint = OnSurfaceVariant,
                                modifier = Modifier.size(32.dp)
                            )
                            Text(
                                text = "No entries in this view",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Medium,
                                color = OnSurfaceVariant
                            )
                        }
                    }
                }
            }

            // Action Footer
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = onNavigateSync,
                    colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .weight(1f)
                        .height(48.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Refresh,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Sync All Dues & Slips",
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp
                    )
                }

                OutlinedButton(
                    onClick = { selectedFilter = "ALL" },
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.size(48.dp),
                    contentPadding = PaddingValues(0.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.List,
                        contentDescription = "Filter",
                        tint = OnSurface
                    )
                }
            }

            // Cash-first statutory disclaimer
            Text(
                text = "Cash-first: App records settlement assertions, not bank transfers. Zero collector fee.",
                fontSize = 11.sp,
                color = OnSurfaceVariant,
                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
            )
        }
    }
}

@Composable
private fun FilterChipItem(
    label: String,
    selected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(20.dp),
        color = if (selected) TerracottaPrimary else SurfaceContainer,
        modifier = Modifier.clickable { onClick() }
    ) {
        Text(
            text = label,
            fontSize = 12.sp,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
            color = if (selected) OnPrimary else OnSurface,
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp)
        )
    }
}

@Composable
private fun TransactionLedgerCard(
    transaction: TransactionSummary,
    onClick: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (transaction.lifecycle == "DISPUTED") ErrorContainer.copy(alpha = 0.25f)
            else SurfaceContainerLow
        ),
        elevation = CardDefaults.cardElevation(1.dp),
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = when (transaction.materialCategory) {
                            "CABLE" -> Color(0xFFFED65B)
                            "PAPER" -> Color(0xFFEAE0DE)
                            "IRON" -> Color(0xFFFFDBCF)
                            else -> ErrorContainer
                        },
                        modifier = Modifier.size(38.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Text(
                                text = when (transaction.materialCategory) {
                                    "CABLE" -> "🔌"
                                    "PAPER" -> "📄"
                                    "IRON" -> "⚙"
                                    else -> "📦"
                                },
                                fontSize = 18.sp
                            )
                        }
                    }

                    Column {
                        Text(
                            text = transaction.materialNameEn,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "${transaction.dateFormatted} · ${transaction.weightKg} kg",
                            fontSize = 11.sp,
                            color = OnSurfaceVariant
                        )
                    }
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "₹${transaction.grossAgreedInr.toInt()}",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                    Text(
                        text = when {
                            transaction.lifecycle == "DISPUTED" -> "Disputed Weight"
                            transaction.isOfflineSavedOnly -> "Waiting to sync"
                            transaction.remainingDuesPaise > 0L && transaction.acknowledgedPaidPaise > 0L -> "Partially Paid"
                            transaction.acknowledgedPaidPaise == transaction.grossAgreedPaise -> "Acknowledged"
                            else -> "Pending Settlement"
                        },
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        color = when {
                            transaction.lifecycle == "DISPUTED" -> ErrorRed
                            transaction.isOfflineSavedOnly -> Color(0xFF615A59)
                            transaction.remainingDuesPaise > 0L && transaction.acknowledgedPaidPaise > 0L -> TerracottaPrimary
                            else -> Color(0xFF735C00)
                        }
                    )
                }
            }

            // Status Breakdown Strip
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = SurfaceBright,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = when {
                            transaction.lifecycle == "DISPUTED" -> "Discrepancy"
                            transaction.isOfflineSavedOnly -> "Sync status"
                            transaction.remainingDuesPaise > 0L -> "Payment Status"
                            else -> "Settlement"
                        },
                        fontSize = 11.sp,
                        color = OnSurfaceVariant
                    )

                    Text(
                        text = when {
                            transaction.lifecycle == "DISPUTED" -> "Yard manager reviewing scale discrepancy"
                            transaction.isOfflineSavedOnly -> "Local device storage only"
                            else -> "₹${transaction.acknowledgedPaidInr.toInt()} paid · ₹${transaction.remainingDuesInr.toInt()} due"
                        },
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = if (transaction.lifecycle == "DISPUTED") ErrorRed else OnSurface
                    )
                }
            }
        }
    }
}
