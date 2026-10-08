package com.sahitol.collector.ui.collector

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
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
import com.sahitol.collector.domain.payment.PaymentMethod
import com.sahitol.collector.domain.payment.PaymentState
import com.sahitol.collector.ui.theme.*
import com.sahitol.collector.ui.components.SahiTolWordmark
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C13_PaymentSettlementScreen(
    transactionId: String,
    paymentRepository: PaymentRepository,
    sessionManager: SessionManager,
    onNavigateBack: () -> Unit,
    onNavigateHome: () -> Unit,
    onNavigateLedger: () -> Unit,
    onNavigateSync: () -> Unit,
    onNavigateSettings: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val session by sessionManager.session.collectAsState()
    val alias = session.alias

    val transactions by paymentRepository.transactions.collectAsState()
    val tx = remember(transactions, transactionId) {
        paymentRepository.getTransaction(transactionId) ?: transactions.first()
    }

    var showAddCashDialog by remember { mutableStateOf(false) }
    var cashAmountInput by remember { mutableStateOf("") }
    var paymentMethodInput by remember { mutableStateOf(PaymentMethod.CASH) }
    var referenceInput by remember { mutableStateOf("") }

    var showDisputeDialog by remember { mutableStateOf(false) }
    var disputeReasonInput by remember { mutableStateOf("") }

    var statusMessage by remember { mutableStateOf<String?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        SahiTolWordmark(modifier = Modifier.width(104.dp))
                        Column {
                            Text(
                                text = "Payment Settlement",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = "भुगतान निपटान · ${tx.referenceCode}",
                                fontSize = 10.sp,
                                color = OnSurfaceVariant
                            )
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = OnSurface
                        )
                    }
                },
                actions = {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = SurfaceContainerHigh,
                        modifier = Modifier.padding(end = 12.dp)
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
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceBright)
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
                    onClick = onNavigateLedger,
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
            // Status Feedback
            statusMessage?.let { msg ->
                Card(
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFFED65B))
                ) {
                    Text(
                        text = msg,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF745C00),
                        modifier = Modifier.padding(12.dp)
                    )
                }
            }

            // Offline Saved Locally Notice
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = null,
                            tint = Color(0xFF735C00),
                            modifier = Modifier.size(18.dp)
                        )
                        Column {
                            Text(
                                text = "Offline Saved Locally",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = "Syncs automatically when network returns",
                                fontSize = 10.sp,
                                color = OnSurfaceVariant
                            )
                        }
                    }

                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = SurfaceContainer
                    ) {
                        Text(
                            text = "Staged #402",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF735C00),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                        )
                    }
                }
            }

            // Material Identity Ledger Header
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                elevation = CardDefaults.cardElevation(1.dp)
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
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = PrimaryContainer,
                                modifier = Modifier.size(44.dp)
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Text(
                                        text = "🔌",
                                        fontSize = 22.sp
                                    )
                                }
                            }

                            Column {
                                Text(
                                    text = "${tx.materialNameEn} / ${tx.materialNameHi}",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "${tx.facilityName} · ${tx.dateFormatted}",
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }

                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = Color(0xFFFED65B)
                        ) {
                            Text(
                                text = "Ref: ${tx.referenceCode}",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF745C00),
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }

                    // Quick Stats Grid
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = SurfaceContainerLow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceAround
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "Measured Weight",
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant
                                )
                                Text(
                                    text = "${tx.weightKg} kg",
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                            }

                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "Agreed Rate",
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant
                                )
                                Text(
                                    text = "₹${tx.ratePerKgInr.toInt()} / kg",
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                            }
                        }
                    }
                }
            }

            // Agreed Amount & Dues Breakdown Card (Terracotta)
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = TerracottaPrimary),
                elevation = CardDefaults.cardElevation(2.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.Bottom
                    ) {
                        Column {
                            Text(
                                text = "AGREED TOTAL / कुल राशि",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFFFFDBCF),
                                letterSpacing = 0.5.sp
                            )
                            Text(
                                text = "₹${tx.grossAgreedInr.toInt()}",
                                fontSize = 28.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnPrimary
                            )
                            Text(
                                text = "Basis: ${tx.weightKg} kg × ₹${tx.ratePerKgInr.toInt()}/kg",
                                fontSize = 11.sp,
                                color = Color(0xFFFFDBCF).copy(alpha = 0.8f)
                            )
                        }

                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                text = "Remaining Due",
                                fontSize = 11.sp,
                                color = Color(0xFFFFDBCF)
                            )
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = OnPrimary.copy(alpha = 0.15f)
                            ) {
                                Text(
                                    text = "₹${tx.remainingDuesInr.toInt()}",
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFFFFE088),
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                                )
                            }
                        }
                    }

                    // Breakdown Progress Bar
                    val totalPaise = tx.grossAgreedPaise.coerceAtLeast(1L)
                    val paidFraction = (tx.acknowledgedPaidPaise.toFloat() / totalPaise).coerceIn(0f, 1f)

                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "Acknowledged: ₹${tx.acknowledgedPaidInr.toInt()}",
                                fontSize = 11.sp,
                                color = Color(0xFFFFDBCF)
                            )
                            Text(
                                text = "Pending: ₹${tx.remainingDuesInr.toInt()}",
                                fontSize = 11.sp,
                                color = Color(0xFFFFDBCF)
                            )
                        }

                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(10.dp)
                                .background(Color.Black.copy(alpha = 0.25f), RoundedCornerShape(5.dp))
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth(paidFraction)
                                    .fillMaxHeight()
                                    .background(Color(0xFFFFE088), RoundedCornerShape(5.dp))
                            )
                        }
                    }
                }
            }

            // Event-Oriented Payment History Stream
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                elevation = CardDefaults.cardElevation(1.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Payment Stream / भुगतान इतिहास",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "${tx.payments.size} Events Recorded",
                            fontSize = 11.sp,
                            color = OnSurfaceVariant
                        )
                    }

                    if (tx.payments.isEmpty()) {
                        Text(
                            text = "No payments recorded yet. Tap 'Add Cash Log' below.",
                            fontSize = 12.sp,
                            color = OnSurfaceVariant,
                            modifier = Modifier.padding(vertical = 8.dp)
                        )
                    } else {
                        tx.payments.forEachIndexed { index, payment ->
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(10.dp),
                                verticalAlignment = Alignment.Top
                            ) {
                                Surface(
                                    shape = CircleShape,
                                    color = when (payment.state) {
                                        PaymentState.ACKNOWLEDGED -> Color(0xFFFED65B)
                                        PaymentState.DISPUTED, PaymentState.REVERSED -> ErrorContainer
                                        else -> PrimaryContainer
                                    },
                                    modifier = Modifier.size(32.dp)
                                ) {
                                    Box(contentAlignment = Alignment.Center) {
                                        Icon(
                                            imageVector = when (payment.state) {
                                                PaymentState.ACKNOWLEDGED -> Icons.Default.CheckCircle
                                                PaymentState.DISPUTED -> Icons.Default.Warning
                                                PaymentState.REVERSED -> Icons.Default.Refresh
                                                else -> Icons.Default.Check
                                            },
                                            contentDescription = null,
                                            tint = when (payment.state) {
                                                PaymentState.ACKNOWLEDGED -> Color(0xFF745C00)
                                                PaymentState.DISPUTED, PaymentState.REVERSED -> ErrorRed
                                                else -> OnPrimary
                                            },
                                            modifier = Modifier.size(16.dp)
                                        )
                                    }
                                }

                                Surface(
                                    shape = RoundedCornerShape(10.dp),
                                    color = SurfaceContainerLow,
                                    modifier = Modifier.weight(1f)
                                ) {
                                    Column(
                                        modifier = Modifier.padding(10.dp),
                                        verticalArrangement = Arrangement.spacedBy(4.dp)
                                    ) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Text(
                                                text = "₹${payment.amountInr.toInt()} · ${payment.method.name}",
                                                fontSize = 12.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = OnSurface
                                            )
                                            Text(
                                                text = payment.state.name,
                                                fontSize = 10.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = when (payment.state) {
                                                    PaymentState.ACKNOWLEDGED -> Color(0xFF735C00)
                                                    PaymentState.DISPUTED, PaymentState.REVERSED -> ErrorRed
                                                    else -> TerracottaPrimary
                                                }
                                            )
                                        }

                                        Text(
                                            text = "Asserted by ${payment.assertedByName}",
                                            fontSize = 11.sp,
                                            color = OnSurfaceVariant
                                        )

                                        payment.reason?.let { reason ->
                                            Text(
                                                text = "Note: $reason",
                                                fontSize = 11.sp,
                                                color = if (payment.state == PaymentState.DISPUTED) ErrorRed else OnSurfaceVariant
                                            )
                                        }

                                        // A collector can record an assertion offline, but only the
                                        // authenticated recycler may acknowledge it on the server.
                                        if (payment.state == PaymentState.ASSERTED) {
                                            Row(
                                                horizontalArrangement = Arrangement.spacedBy(6.dp),
                                                modifier = Modifier.padding(top = 4.dp)
                                            ) {
                                                Text(
                                                    text = "Waiting for recycler acknowledgement",
                                                    fontSize = 10.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    color = OnSurfaceVariant,
                                                    modifier = Modifier.padding(vertical = 6.dp)
                                                )

                                                OutlinedButton(
                                                    onClick = {
                                                        showDisputeDialog = true
                                                    },
                                                    shape = RoundedCornerShape(6.dp),
                                                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                                                    modifier = Modifier.height(28.dp)
                                                ) {
                                                    Text("Dispute", fontSize = 10.sp, color = ErrorRed)
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Action Footer Toolbar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = { showAddCashDialog = true },
                    colors = ButtonDefaults.buttonColors(containerColor = SurfaceContainerHigh),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .weight(1f)
                        .height(48.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = null,
                        tint = OnSurface,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Add Cash Log",
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp,
                        color = OnSurface
                    )
                }

                Button(
                    onClick = {
                        coroutineScope.launch {
                            try {
                                if (tx.remainingDuesPaise > 0L) {
                                    // Settle remaining dues with cash
                                    paymentRepository.assertPaymentAtomic(
                                        transactionId = tx.transactionId,
                                        amountPaise = tx.remainingDuesPaise,
                                        method = PaymentMethod.CASH,
                                        reference = "Settlement clearance in field",
                                        assertedByRole = "COLLECTOR",
                                        assertedByName = alias,
                                        isDemo = tx.isDemo
                                    )
                                    statusMessage = "Remaining dues logged. Awaiting acknowledgement."
                                } else {
                                    paymentRepository.closeTransactionAtomic(tx.transactionId)
                                    statusMessage = "Transaction verified and closed."
                                }
                            } catch (e: Exception) {
                                statusMessage = e.message
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .weight(1f)
                        .height(48.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = null,
                        tint = OnPrimary,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = if (tx.remainingDuesPaise > 0L) "Settle Dues" else "Verify Balance",
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp,
                        color = OnPrimary
                    )
                }
            }

            // Statutory Non-EPR & Cash-First Invariant Notice
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
            ) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = "Statutory Disclosure & Cash-First Notice",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                    Text(
                        text = "SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling. App records cash settlement assertions, not automated bank transfers. Zero collector fee.",
                        fontSize = 10.sp,
                        color = OnSurfaceVariant,
                        lineHeight = 14.sp
                    )
                }
            }
        }
    }

    // Add Cash Log Dialog
    if (showAddCashDialog) {
        AlertDialog(
            onDismissRequest = { showAddCashDialog = false },
            title = {
                Text(
                    text = "Record Payment Assertion",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(
                        text = "Enter amount settled in field. The app records your assertion for recycler acknowledgement.",
                        fontSize = 12.sp,
                        color = OnSurfaceVariant
                    )

                    OutlinedTextField(
                        value = cashAmountInput,
                        onValueChange = { cashAmountInput = it },
                        label = { Text("Amount (₹)") },
                        placeholder = { Text("e.g. 150") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        FilterChip(
                            selected = paymentMethodInput == PaymentMethod.CASH,
                            onClick = { paymentMethodInput = PaymentMethod.CASH },
                            label = { Text("Cash First") }
                        )
                        FilterChip(
                            selected = paymentMethodInput == PaymentMethod.UPI,
                            onClick = { paymentMethodInput = PaymentMethod.UPI },
                            label = { Text("UPI Ref") }
                        )
                    }

                    if (paymentMethodInput == PaymentMethod.UPI) {
                        OutlinedTextField(
                            value = referenceInput,
                            onValueChange = { referenceInput = it },
                            label = { Text("UPI UTR / Reference") },
                            placeholder = { Text("e.g. 423984102941") },
                            singleLine = true,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        val amountInr = cashAmountInput.toDoubleOrNull() ?: 0.0
                        if (amountInr > 0) {
                            coroutineScope.launch {
                                paymentRepository.assertPaymentAtomic(
                                    transactionId = tx.transactionId,
                                    amountPaise = (amountInr * 100).toLong(),
                                    method = paymentMethodInput,
                                    reference = referenceInput.ifBlank { null },
                                    assertedByRole = "COLLECTOR",
                                    assertedByName = alias,
                                    isDemo = tx.isDemo
                                )
                                showAddCashDialog = false
                                cashAmountInput = ""
                                referenceInput = ""
                                statusMessage = "Payment assertion recorded (queued to sync outbox)"
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                ) {
                    Text("Save Assertion")
                }
            },
            dismissButton = {
                TextButton(onClick = { showAddCashDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }

    // Dispute Dialog
    if (showDisputeDialog) {
        AlertDialog(
            onDismissRequest = { showDisputeDialog = false },
            title = {
                Text(
                    text = "Dispute Payment Record",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    color = ErrorRed
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = "Document reason for payment or weight disagreement. History will not be overwritten.",
                        fontSize = 12.sp,
                        color = OnSurfaceVariant
                    )
                    OutlinedTextField(
                        value = disputeReasonInput,
                        onValueChange = { disputeReasonInput = it },
                        label = { Text("Dispute Reason") },
                        placeholder = { Text("e.g. Cash received was ₹100 not ₹200") },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (disputeReasonInput.isNotBlank()) {
                            coroutineScope.launch {
                                val firstPending = tx.payments.find { it.state == PaymentState.ASSERTED }
                                if (firstPending != null) {
                                    paymentRepository.disputePaymentAtomic(
                                        tx.transactionId,
                                        firstPending.id,
                                        disputeReasonInput
                                    )
                                }
                                showDisputeDialog = false
                                disputeReasonInput = ""
                                statusMessage = "Dispute documented and queued to outbox."
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = ErrorRed)
                ) {
                    Text("Submit Dispute")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDisputeDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}
