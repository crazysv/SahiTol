package com.sahitol.collector.ui.collector

import android.content.Intent
import android.widget.Toast
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.repository.HandoverProposal
import com.sahitol.collector.data.repository.HandoverRepository
import com.sahitol.collector.data.repository.FacilityRepository
import com.sahitol.collector.data.repository.TradeResult
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.domain.pdf.ReceiptPdfGenerator
import com.sahitol.collector.domain.qr.QrGenerator
import com.sahitol.collector.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Screen C11: Digital Handover Record & QR Confirmation (Stitch b41f09f64e78).
 * Features:
 * - Offline generated QR Code for second-device yard scanning (R-HAND-02, R-HAND-04).
 * - Statutory Non-EPR disclosure banner (R-HAND-06 invariant).
 * - Cryptographic SHA-256 seal (SAHITOL-JCS-1) and unguessable verification link.
 * - Share Record intent and Android native PdfDocument generation.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C11_DigitalHandoverRecordScreen(
    handoverId: String,
    facilityRepository: FacilityRepository,
    handoverRepository: HandoverRepository,
    sessionManager: SessionManager,
    onNavigateBack: () -> Unit,
    onNavigateHome: () -> Unit,
    onNavigatePrices: () -> Unit,
    onNavigateHandover: () -> Unit,
    onNavigatePassport: (String) -> Unit,
    onNavigateSettings: () -> Unit
) {
    val context = LocalContext.current
    val session by sessionManager.session.collectAsState()
    val alias = session.alias

    var proposal by remember(handoverId) { mutableStateOf(handoverRepository.getHandoverProposal(handoverId)) }
    var refreshMessage by remember(handoverId) { mutableStateOf<String?>(null) }
    var pdfGeneratedFile by remember { mutableStateOf<String?>(null) }
    var revision by remember(handoverId) { mutableStateOf<com.sahitol.collector.data.repository.LiveTermsRevision?>(null) }
    var serverVersion by remember(handoverId) { mutableIntStateOf(0) }
    var actionInProgress by remember(handoverId) { mutableStateOf(false) }
    var showDisputeDialog by remember(handoverId) { mutableStateOf(false) }
    var disputeReason by remember(handoverId) { mutableStateOf("") }
    val coroutineScope = rememberCoroutineScope()

    // Recycler confirmation happens on a different device. Keep this record
    // current while it remains visible instead of requiring the collector to
    // leave and reopen the screen after the QR confirmation completes.
    LaunchedEffect(handoverId, session.accountId) {
        val accountId = session.accountId ?: return@LaunchedEffect
        while (true) {
            when (val result = facilityRepository.fetchLiveHandoverStatus(handoverId, accountId)) {
                is TradeResult.Success -> {
                    revision = result.value.latestTermsRevision
                    serverVersion = result.value.version
                    proposal = handoverRepository.updateServerStatus(handoverId, result.value.status)
                        ?: proposal.copy(status = result.value.status)
                    proposal = revision?.let {
                        proposal.copy(
                            materialId = it.materialId,
                            measuredWeightG = it.measuredWeightG,
                            totalPayoutInr = it.finalTotalPaise / 100.0,
                            rateInrPerKg = if (it.measuredWeightG > 0) it.finalTotalPaise / 100.0 * 1000 / it.measuredWeightG else 0.0
                        )
                    } ?: proposal
                    refreshMessage = when (result.value.status) {
                        "CONFIRMED" -> "Recycler receipt confirmed by server."
                        "PENDING_COLLECTOR_ACK" -> "Review the recycler's changed measurement before confirming or disputing it."
                        "DISPUTED" -> "Dispute recorded. The original handover evidence remains unchanged."
                        else -> null
                    }
                    if (result.value.status in setOf("CONFIRMED", "DISPUTED")) break
                }
                is TradeResult.Failure -> refreshMessage = result.message
            }
            delay(3_000)
        }
    }

    val qrBitmap = remember(proposal.verificationUrl) {
        try {
            QrGenerator.generateQrBitmap(proposal.verificationUrl, 512)
        } catch (_: Exception) {
            null
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Digital Handover Record",
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "डिजिटल हस्तनांतरण रसीद",
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
                        Row(
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .background(SuccessGreen, CircleShape)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "Offline Ready",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = SuccessGreen
                    )
                }
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
                    selected = true,
                    onClick = { /* Current */ },
                    icon = { Icon(Icons.Default.CheckCircle, contentDescription = "QR Record") },
                    label = { Text("QR Record", fontSize = 10.sp) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = TerracottaPrimary,
                        selectedTextColor = TerracottaPrimary,
                        indicatorColor = TerracottaPrimary.copy(alpha = 0.15f)
                    )
                )
                NavigationBarItem(
                    selected = false,
                    onClick = { onNavigatePassport(proposal.lotId) },
                    icon = { Icon(Icons.Default.Info, contentDescription = "Passport") },
                    label = { Text("Passport", fontSize = 10.sp) }
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
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Material & Value Banner
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                elevation = CardDefaults.cardElevation(2.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = proposal.materialName,
                                fontSize = 17.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = "Yard: ${proposal.facilityName}",
                                fontSize = 11.sp,
                                color = OnSurfaceVariant
                            )
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                text = "₹%.2f".format(proposal.totalPayoutInr),
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary
                            )
                            Text(
                                text = "%.2f kg".format((proposal.measuredWeightG ?: proposal.estimatedWeightG) / 1000.0),
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = OnSurfaceVariant
                            )
                        }
                    }

                    // Hash seal strip
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(SurfaceContainerLow, RoundedCornerShape(8.dp))
                            .padding(horizontal = 10.dp, vertical = 6.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SuccessGreen, modifier = Modifier.size(14.dp))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "Hash: 0x${proposal.canonicalHash.take(8)}...${proposal.canonicalHash.takeLast(4)}",
                                fontFamily = FontFamily.Monospace,
                                fontSize = 10.sp,
                                color = OnSurfaceVariant
                            )
                        }
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = PrimaryContainer.copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = "SHA-256 Secure",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                }
            }

            // Prominent QR Code Container
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                elevation = CardDefaults.cardElevation(2.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Top tag
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = TerracottaPrimary
                    ) {
                        Text(
                            text = "SCAN AT YARD",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnPrimary,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                        )
                    }

                    // QR Display
                    Box(
                        modifier = Modifier
                            .size(200.dp)
                            .background(SurfaceContainerLow, RoundedCornerShape(16.dp))
                            .padding(12.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        if (qrBitmap != null) {
                            Image(
                                bitmap = qrBitmap.asImageBitmap(),
                                contentDescription = "Digital Handover QR Code",
                                modifier = Modifier.fillMaxSize()
                            )
                        } else {
                            Icon(
                                Icons.Default.CheckCircle,
                                contentDescription = null,
                                tint = TerracottaPrimary,
                                modifier = Modifier.size(64.dp)
                            )
                        }
                    }

                    Text(
                        text = "Ref: ${proposal.referenceCode}",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )

                    Text(
                        text = when (proposal.status) {
                            "CONFIRMED" -> "Recycler receipt confirmed / रसीद की पुष्टि हुई"
                            "PENDING_COLLECTOR_ACK" -> "Recycler revised the terms — your acknowledgement is required"
                            "DISPUTED" -> "Handover disputed — joint review required"
                            else -> "Awaiting recycler confirmation / रिसाइकलर की पुष्टि बाकी है"
                        },
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = when (proposal.status) {
                            "CONFIRMED" -> SuccessGreen
                            "DISPUTED" -> ErrorRed
                            else -> OnSurfaceVariant
                        },
                        textAlign = TextAlign.Center
                    )

                    Text(
                        text = refreshMessage ?: "Show this QR code to the yard manager or recycling facility partner for instant handover confirmation.",
                        fontSize = 11.sp,
                        color = OnSurfaceVariant,
                        textAlign = TextAlign.Center
                    )

                    // Mandatory Non-EPR Invariant Notice
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = SurfaceContainerLow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier.padding(10.dp),
                            verticalAlignment = Alignment.Top
                        ) {
                            Icon(
                                Icons.Default.Info,
                                contentDescription = null,
                                tint = MustardSecondary,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling.",
                                fontSize = 10.sp,
                                color = OnSurfaceVariant,
                                lineHeight = 14.sp
                            )
                        }
                    }
                }
            }

            if (proposal.status == "PENDING_COLLECTOR_ACK" && revision != null) {
                Card(
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = ErrorRed.copy(alpha = 0.08f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, ErrorRed.copy(alpha = 0.35f))
                ) {
                    Column(
                        modifier = Modifier.fillMaxWidth().padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text("Recycler changed the receipt terms", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = OnSurface)
                        Text(
                            "${"%.2f".format(revision!!.measuredWeightG / 1000.0)} kg · ₹${"%.2f".format(revision!!.finalTotalPaise / 100.0)}",
                            fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = ErrorRed
                        )
                        Text(revision!!.reason, fontSize = 12.sp, color = OnSurfaceVariant)
                        Text("Review the changed terms before confirming. You can dispute without rewriting the original record.", fontSize = 11.sp, color = OnSurfaceVariant)
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            Button(
                                enabled = !actionInProgress,
                                onClick = {
                                    actionInProgress = true
                                    coroutineScope.launch {
                                        when (val result = facilityRepository.acknowledgeLiveHandoverTerms(handoverId, revision!!.termsHash, serverVersion, session.accountId ?: "")) {
                                            is TradeResult.Success -> {
                                                proposal = handoverRepository.updateServerStatus(handoverId, result.value) ?: proposal.copy(status = result.value)
                                                revision = null
                                                refreshMessage = "Revised terms acknowledged; recycler receipt confirmed by server."
                                            }
                                            is TradeResult.Failure -> refreshMessage = result.message
                                        }
                                        actionInProgress = false
                                    }
                                },
                                modifier = Modifier.weight(1f), shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = SuccessGreen)
                            ) { Text(if (actionInProgress) "Saving…" else "Accept revised terms", fontSize = 11.sp) }
                            OutlinedButton(
                                enabled = !actionInProgress,
                                onClick = { showDisputeDialog = true },
                                modifier = Modifier.weight(1f), shape = RoundedCornerShape(8.dp)
                            ) { Text("Dispute", fontSize = 11.sp, color = ErrorRed) }
                        }
                    }
                }
            }

            // Action Buttons: Share & PDF
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Button(
                    onClick = {
                        val shareIntent = Intent(Intent.ACTION_SEND).apply {
                            type = "text/plain"
                            putExtra(
                                Intent.EXTRA_TEXT,
                                "SahiTol Handover Record ${proposal.referenceCode}\n" +
                                        "Material: ${proposal.materialName}\n" +
                                        "Weight: %.2f kg\n".format((proposal.measuredWeightG ?: proposal.estimatedWeightG) / 1000.0) +
                                        "Agreed Value: ₹%.2f\n".format(proposal.totalPayoutInr) +
                                        "Verification: ${proposal.verificationUrl}\n" +
                                        "SHA-256: ${proposal.canonicalHash}"
                            )
                        }
                        context.startActivity(Intent.createChooser(shareIntent, "Share Handover Record"))
                    },
                    modifier = Modifier
                        .weight(1f)
                        .height(48.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                ) {
                    Icon(Icons.Default.Share, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("Share Record", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }

                OutlinedButton(
                    onClick = {
                        try {
                            val pdfFile = ReceiptPdfGenerator.generateReceiptPdf(
                                context = context,
                                data = ReceiptPdfGenerator.ReceiptData(
                                    handoverId = proposal.handoverId,
                                    referenceCode = proposal.referenceCode,
                                    occurredAt = proposal.occurredAt,
                                    collectorAlias = alias,
                                    facilityName = proposal.facilityName,
                                    materialName = proposal.materialName,
                                    weightG = proposal.measuredWeightG ?: proposal.estimatedWeightG,
                                    rateInrPerKg = proposal.rateInrPerKg,
                                    totalPayoutInr = proposal.totalPayoutInr,
                                    canonicalHash = proposal.canonicalHash,
                                    verificationUrl = proposal.verificationUrl,
                                    statusText = proposal.status
                                )
                            )
                            pdfGeneratedFile = pdfFile.name
                            Toast.makeText(context, "Saved PDF: ${pdfFile.name}", Toast.LENGTH_LONG).show()
                        } catch (e: Exception) {
                            Toast.makeText(context, "PDF generation failed: ${e.message}", Toast.LENGTH_SHORT).show()
                        }
                    },
                    modifier = Modifier
                        .weight(1f)
                        .height(48.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("Save PDF", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }
            }

            if (pdfGeneratedFile != null) {
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = SuccessGreen.copy(alpha = 0.12f),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(10.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SuccessGreen, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "PDF exported: $pdfGeneratedFile",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium,
                            color = OnSurface
                        )
                    }
                }
            }

            // Offline Sync Footer Strip
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = SurfaceContainerLow,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(SuccessGreen, CircleShape)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Auto-sync active when online", fontSize = 12.sp, color = OnSurfaceVariant)
                    }
                    Text("Ready for batch #12", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = TerracottaPrimary)
                }
            }
        }
    }

    if (showDisputeDialog) {
        AlertDialog(
            onDismissRequest = { showDisputeDialog = false },
            title = { Text("Dispute revised terms") },
            text = {
                OutlinedTextField(
                    value = disputeReason,
                    onValueChange = { disputeReason = it },
                    label = { Text("Reason for joint re-weigh") },
                    modifier = Modifier.fillMaxWidth()
                )
            },
            confirmButton = {
                Button(
                    enabled = !actionInProgress,
                    onClick = {
                        showDisputeDialog = false
                        actionInProgress = true
                        coroutineScope.launch {
                            when (val result = facilityRepository.disputeLiveHandover(
                                handoverId,
                                disputeReason.ifBlank { "Collector requests a joint re-weigh before settlement." },
                                serverVersion,
                                session.accountId ?: ""
                            )) {
                                is TradeResult.Success -> {
                                    proposal = handoverRepository.updateServerStatus(handoverId, result.value) ?: proposal.copy(status = result.value)
                                    revision = null
                                    refreshMessage = "Dispute recorded. The original handover evidence remains unchanged."
                                }
                                is TradeResult.Failure -> refreshMessage = result.message
                            }
                            actionInProgress = false
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = ErrorRed)
                ) { Text("Raise dispute") }
            },
            dismissButton = { TextButton(onClick = { showDisputeDialog = false }) { Text("Cancel") } }
        )
    }
}
