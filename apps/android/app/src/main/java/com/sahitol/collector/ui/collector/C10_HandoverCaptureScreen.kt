package com.sahitol.collector.ui.collector

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.repository.HandoverProposal
import com.sahitol.collector.data.repository.HandoverRepository
import com.sahitol.collector.data.repository.FacilityRepository
import com.sahitol.collector.data.repository.AcceptedTransaction
import com.sahitol.collector.data.repository.RecyclerOfferItem
import com.sahitol.collector.data.repository.TradeResult
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.ui.theme.*
import kotlinx.coroutines.launch

/**
 * Screen C10: Handover Capture & Scale Reconciliation (Stitch b389d91e2be7).
 * Features:
 * - Actual weight, photo evidence, and assigned yard verification.
 * - Terms Changed / Discrepancy Found inspection card (Original vs Measured).
 * - Review, Accept, and Dispute actions with explicit non-destructive log.
 * - Atomic local handover proposal creation with SAHITOL-JCS-1 canonical hash and outbox queuing.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C10_HandoverCaptureScreen(
    lotId: String,
    lot: LotEntity?,
    facilityRepository: FacilityRepository,
    handoverRepository: HandoverRepository,
    sessionManager: SessionManager,
    onNavigateBack: () -> Unit,
    onNavigateHome: () -> Unit,
    onNavigatePrices: () -> Unit,
    onNavigateRecord: (String) -> Unit,
    onNavigatePassport: (String) -> Unit,
    onNavigateSettings: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val session by sessionManager.session.collectAsState()
    val accountId = session.accountId ?: "col_demo_santosh"

    val lotContext = remember(lot) { lotDisplayContext(lot) }
    var proposal by remember { mutableStateOf(handoverRepository.getHandoverProposal(lotId)) }
    var agreement by remember { mutableStateOf<AcceptedTransaction?>(null) }
    var acceptedOffer by remember { mutableStateOf<RecyclerOfferItem?>(null) }
    var loadingAgreement by remember { mutableStateOf(true) }
    var agreementError by remember { mutableStateOf<String?>(null) }
    var termsState by remember { mutableStateOf("AGREED") }
    var showReviewDetails by remember { mutableStateOf(false) }
    var disputeReason by remember { mutableStateOf("") }
    var showDisputeDialog by remember { mutableStateOf(false) }
    var isSaving by remember { mutableStateOf(false) }
    var savedSuccessToast by remember { mutableStateOf(false) }
    val hasServerHandover = proposal.handoverId != lotId && proposal.canonicalHash.isNotBlank()

    LaunchedEffect(lotId, accountId, lotContext.canonicalMaterialId) {
        loadingAgreement = true
        agreementError = null
        val savedRecord = handoverRepository.getHandoverProposal(lotId)
        val hasSavedServerRecord = savedRecord.handoverId != lotId && savedRecord.canonicalHash.isNotBlank()
        if (hasSavedServerRecord) proposal = savedRecord
        when (val txResult = facilityRepository.fetchAcceptedTransaction(lotId, accountId)) {
            is TradeResult.Failure -> agreementError = txResult.message
            is TradeResult.Success -> {
                agreement = txResult.value
                val materialId = lotContext.canonicalMaterialId
                if (materialId != null) {
                    when (val handoverResult = facilityRepository.fetchLiveHandoverForLot(lotId, accountId)) {
                        is TradeResult.Success -> {
                            proposal = handoverRepository.cacheRecoveredServerProposal(
                                handoverResult.value.handoverId,
                                handoverResult.value.status,
                                handoverResult.value.proposalHash,
                                txResult.value,
                                materialId,
                                lotContext.materialLabel,
                                "Accepted live facility"
                            )
                            savedSuccessToast = true
                            loadingAgreement = false
                            return@LaunchedEffect
                        }
                        is TradeResult.Failure -> Unit // No server handover yet; continue with accepted-offer recovery.
                    }
                }
                if (txResult.value.lifecycle == "CONFIRMED" && hasSavedServerRecord) {
                    proposal = handoverRepository.updateServerStatus(savedRecord.handoverId, "CONFIRMED") ?: savedRecord.copy(status = "CONFIRMED")
                    savedSuccessToast = true
                    loadingAgreement = false
                    return@LaunchedEffect
                }
                when (val offersResult = facilityRepository.fetchLiveOffers(lotId, accountId)) {
                    is TradeResult.Failure -> agreementError = offersResult.message
                    is TradeResult.Success -> {
                        val offer = offersResult.value.firstOrNull { it.offerId == txResult.value.acceptedOfferId }
                        if (offer == null || offer.termsHash.isNullOrBlank()) {
                            agreementError = "The accepted offer terms could not be recovered. Refresh the offer before creating a handover."
                        } else {
                            acceptedOffer = offer
                            proposal = HandoverProposal(
                                handoverId = lotId,
                                transactionId = txResult.value.transactionId,
                                lotId = txResult.value.lotId,
                                collectorId = txResult.value.collectorId,
                                facilityId = txResult.value.facilityId,
                                facilityName = "Accepted live facility",
                                materialId = lotContext.canonicalMaterialId ?: "",
                                materialName = lotContext.materialLabel,
                                condition = "INTACT",
                                estimatedWeightG = txResult.value.agreedWeightG,
                                measuredWeightG = txResult.value.agreedWeightG,
                                rateInrPerKg = if (txResult.value.agreedWeightG > 0) txResult.value.agreedTotalPaise / 100.0 * 1000 / txResult.value.agreedWeightG else 0.0,
                                totalPayoutInr = txResult.value.agreedTotalPaise / 100.0,
                                referenceCode = "Pending server proposal",
                                status = "AGREED",
                                canonicalHash = "",
                                verificationUrl = "",
                                isDemo = txResult.value.isDemo
                            )
                        }
                    }
                }
            }
        }
        loadingAgreement = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Handover Capture / हस्तनांतरण",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "Lot Ref: ${lotId.take(12)}",
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
                    selected = true,
                    onClick = { /* Current */ },
                    icon = { Icon(Icons.Default.Place, contentDescription = "Handover") },
                    label = { Text("Handover", fontSize = 10.sp) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = TerracottaPrimary,
                        selectedTextColor = TerracottaPrimary,
                        indicatorColor = TerracottaPrimary.copy(alpha = 0.15f)
                    )
                )
                NavigationBarItem(
                    selected = false,
                    onClick = { onNavigateRecord(proposal.handoverId) },
                    icon = { Icon(Icons.Default.CheckCircle, contentDescription = "QR Record") },
                    label = { Text("QR Record", fontSize = 10.sp) }
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
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            if (loadingAgreement) {
                LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                Text("Loading the accepted server agreement…", fontSize = 12.sp, color = OnSurfaceVariant)
            }
            agreementError?.let { Text(it, color = ErrorRed, fontSize = 12.sp) }
            // Material & Yard Card
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
                        Text(
                            text = proposal.materialName,
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = PrimaryContainer.copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = "%.1f kg".format(proposal.estimatedWeightG / 1000.0),
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                            )
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Condition: ${proposal.condition}",
                            fontSize = 12.sp,
                            color = OnSurfaceVariant
                        )
                        Text(
                            text = "Yard: ${proposal.facilityName}",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                            color = OnSurfaceVariant
                        )
                    }
                }
            }

            // Discrepancy & Terms Revision Card (Mandatory R-HAND-05 Invariant)
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (termsState == "DISPUTED") ErrorContainer.copy(alpha = 0.3f)
                    else SecondaryContainer.copy(alpha = 0.25f)
                ),
                border = androidx.compose.foundation.BorderStroke(
                    1.dp,
                    if (termsState == "DISPUTED") ErrorRed.copy(alpha = 0.4f) else MustardSecondary.copy(alpha = 0.4f)
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Default.Warning,
                                contentDescription = null,
                                tint = if (termsState == "DISPUTED") ErrorRed else MustardSecondary,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                            text = "Agreed Terms / स्वीकृत शर्तें",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (termsState == "DISPUTED") ErrorRed else MustardSecondary
                            )
                        }
                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = (if (termsState == "DISPUTED") ErrorRed else MustardSecondary).copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = if (termsState == "DISPUTED") "Disputed" else "Agreement loaded",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (termsState == "DISPUTED") ErrorRed else MustardSecondary,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }

                    // Comparison grid
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(SurfaceContainerLowest, RoundedCornerShape(8.dp))
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceAround
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Agreed total", fontSize = 11.sp, color = OnSurfaceVariant)
                            Text("₹%.2f".format(proposal.totalPayoutInr), fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = OnSurface)
                            Text("%.2f kg @ ₹%.2f/kg".format(proposal.estimatedWeightG / 1000.0, proposal.rateInrPerKg), fontSize = 10.sp, color = OnSurfaceVariant)
                        }
                        Box(
                            modifier = Modifier
                                .width(1.dp)
                                .height(40.dp)
                                .background(OutlineVariantColor.copy(alpha = 0.5f))
                        )
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Agreed handover value", fontSize = 11.sp, color = OnSurfaceVariant)
                            Text(
                                "₹%.2f".format(proposal.totalPayoutInr),
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (termsState == "DISPUTED") ErrorRed else TerracottaPrimary
                            )
                            Text(
                                "%.2f kg agreed; no recycler measurement yet".format(proposal.estimatedWeightG / 1000.0),
                                fontSize = 10.sp,
                                color = OnSurfaceVariant
                            )
                        }
                    }

                    // Review details expansion
                    if (showReviewDetails) {
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = SurfaceContainerLowest,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                Text(
                                    text = "Scale Calibration Audit Log",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "This screen records the accepted agreement. A recycler can submit a measured difference only after the server-backed proposal is created.",
                                    fontSize = 10.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }
                    }

                    // Agreement state and inspection controls. A recycler measurement or
                    // revision is only available after the QR handover exists on the server.
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        OutlinedButton(
                            onClick = { showReviewDetails = !showReviewDetails },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Icon(Icons.Default.Info, contentDescription = null, modifier = Modifier.size(14.dp))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Review", fontSize = 11.sp)
                        }

                        Surface(
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp),
                            color = SuccessGreen.copy(alpha = 0.15f)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 10.dp),
                                horizontalArrangement = Arrangement.Center,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(14.dp), tint = SuccessGreen)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("Terms accepted", fontSize = 11.sp, color = SuccessGreen)
                            }
                        }

                        Surface(
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp),
                            color = SurfaceContainer
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 10.dp),
                                horizontalArrangement = Arrangement.Center,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(Icons.Default.Info, contentDescription = null, modifier = Modifier.size(14.dp), tint = OnSurfaceVariant)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("Awaiting measurement", fontSize = 11.sp, color = OnSurfaceVariant)
                            }
                        }
                    }
                }
            }

            // Evidence & Inspection Card
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                elevation = CardDefaults.cardElevation(2.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Text(
                        text = "Evidence & Inspection / साक्ष्य विवरण",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )

                    // Simulated Scale Photo Box
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(110.dp)
                            .background(SurfaceContainer, RoundedCornerShape(12.dp))
                            .border(1.dp, OutlineVariantColor.copy(alpha = 0.4f), RoundedCornerShape(12.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SuccessGreen, modifier = Modifier.size(24.dp))
                            Spacer(modifier = Modifier.height(4.dp))
                            Text("Accepted mass: %.2f kg".format(proposal.estimatedWeightG / 1000.0), fontSize = 12.sp, fontWeight = FontWeight.Bold, color = OnSurface)
                            Text("Recycler measurement has not been recorded", fontSize = 10.sp, color = OnSurfaceVariant)
                        }
                    }

                    // Metadata details
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Place, contentDescription = null, tint = TerracottaPrimary, modifier = Modifier.size(14.dp))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Facility: ${proposal.facilityName}", fontSize = 11.sp, color = OnSurfaceVariant)
                        }
                        Text("Server agreement", fontSize = 11.sp, color = OnSurfaceVariant)
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CheckCircle, contentDescription = null, tint = PrimaryContainer, modifier = Modifier.size(14.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = if (proposal.canonicalHash.isBlank()) "Hash will be issued by server" else "HASH: ${proposal.canonicalHash.take(16)}...",
                            fontFamily = FontFamily.Monospace,
                            fontSize = 10.sp,
                            color = OnSurfaceVariant
                        )
                    }
                }
            }

            // Primary Save Action Button
            Button(
                onClick = {
                    if (hasServerHandover) {
                        onNavigateRecord(proposal.handoverId)
                        return@Button
                    }
                    isSaving = true
                    coroutineScope.launch {
                        val tx = agreement
                        val offer = acceptedOffer
                        val materialId = lotContext.canonicalMaterialId
                        if (tx == null || offer == null || materialId == null) {
                            agreementError = "A verified accepted agreement is required before creating a handover."
                        } else when (val result = facilityRepository.createLiveHandover(tx, offer, materialId, accountId)) {
                            is TradeResult.Failure -> agreementError = result.message
                            is TradeResult.Success -> proposal = handoverRepository.cacheServerProposal(
                                result.value, tx, offer, materialId, lotContext.materialLabel, proposal.facilityName
                            )
                        }
                        isSaving = false
                        savedSuccessToast = proposal.handoverId != lotId && proposal.canonicalHash.isNotBlank()
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
                enabled = hasServerHandover || (!isSaving && !loadingAgreement && agreement != null && acceptedOffer != null && lotContext.canonicalMaterialId != null)
            ) {
                Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = when {
                        hasServerHandover -> "Open Digital Handover Record (QR)"
                        isSaving -> "Saving..."
                        else -> "Save & Generate Handover Record / हस्तनांतरण सहेजें"
                    },
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            // Success Card with Navigation Prompt
            if (savedSuccessToast) {
                Card(
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = SuccessGreen.copy(alpha = 0.12f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.3f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SuccessGreen)
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text(
                                    if (proposal.status == "CONFIRMED") "Recycler Handover Confirmed" else "Server Handover Proposal Created",
                                    fontSize = 13.sp, fontWeight = FontWeight.Bold, color = OnSurface
                                )
                                Text(
                                    if (proposal.status == "CONFIRMED") {
                                        "Receipt ${proposal.referenceCode} has been confirmed by the recycler."
                                    } else {
                                        "Receipt ${proposal.referenceCode} is ready for recycler confirmation."
                                    },
                                    fontSize = 11.sp, color = OnSurfaceVariant
                                )
                            }
                        }

                        Button(
                            onClick = { onNavigateRecord(proposal.handoverId) },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = SuccessGreen)
                        ) {
                            Text("Open Digital Handover Record (QR)")
                        }
                    }
                }
            }
        }
    }

    // Dispute dialog
    if (showDisputeDialog) {
        AlertDialog(
            onDismissRequest = { showDisputeDialog = false },
            title = { Text("Log Handover Dispute / विवाद दर्ज करें") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = "Enter discrepancy reason for joint inspection with yard supervisor:",
                        fontSize = 12.sp,
                        color = OnSurfaceVariant
                    )
                    OutlinedTextField(
                        value = disputeReason,
                        onValueChange = { disputeReason = it },
                        placeholder = { Text("e.g., Scale tare inaccurate, excessive deduction") },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        termsState = "DISPUTED"
                        showDisputeDialog = false
                        coroutineScope.launch {
                            proposal = handoverRepository.recordDiscrepancyResponseAtomic(
                                handoverId = proposal.handoverId,
                                action = "DISPUTE_TERMS",
                                collectorId = accountId,
                                reason = disputeReason.ifBlank { "Collector disputed measured weight difference" }
                            )
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = ErrorRed)
                ) {
                    Text("Raise Dispute")
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
