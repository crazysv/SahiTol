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

    var proposal by remember { mutableStateOf(handoverRepository.getHandoverProposal(lotId)) }
    var termsState by remember { mutableStateOf("PENDING_REVIEW") } // PENDING_REVIEW, ACCEPTED, DISPUTED
    var showReviewDetails by remember { mutableStateOf(false) }
    var disputeReason by remember { mutableStateOf("") }
    var showDisputeDialog by remember { mutableStateOf(false) }
    var isSaving by remember { mutableStateOf(false) }
    var savedSuccessToast by remember { mutableStateOf(false) }

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
                                text = "Terms Changed / शर्तों में बदलाव",
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
                                text = if (termsState == "ACCEPTED") "Accepted" else if (termsState == "DISPUTED") "Disputed" else "Discrepancy Found",
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
                            Text("Original Estimate", fontSize = 11.sp, color = OnSurfaceVariant)
                            Text("₹450.00", fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = OnSurface)
                            Text("2.5 kg @ ₹180/kg", fontSize = 10.sp, color = OnSurfaceVariant)
                        }
                        Box(
                            modifier = Modifier
                                .width(1.dp)
                                .height(40.dp)
                                .background(OutlineVariantColor.copy(alpha = 0.5f))
                        )
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("New Measured Term", fontSize = 11.sp, color = OnSurfaceVariant)
                            Text(
                                "₹414.00",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (termsState == "DISPUTED") ErrorRed else TerracottaPrimary
                            )
                            Text("2.3 kg @ ₹180/kg (-200g tare)", fontSize = 10.sp, color = OnSurfaceVariant)
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
                                    text = "Certified Scale #OKH-04 calibrated Oct 12. Moisture & rubber sleeve deduction: -200 grams. Net metallic copper core: 2.30 kg.",
                                    fontSize = 10.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }
                    }

                    // Three Decision Buttons
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

                        Button(
                            onClick = {
                                termsState = "ACCEPTED"
                                coroutineScope.launch {
                                    proposal = handoverRepository.recordDiscrepancyResponseAtomic(
                                        handoverId = proposal.handoverId,
                                        action = "ACCEPT_TERMS",
                                        collectorId = accountId
                                    )
                                }
                            },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (termsState == "ACCEPTED") SuccessGreen else TerracottaPrimary
                            )
                        ) {
                            Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(14.dp))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(if (termsState == "ACCEPTED") "Accepted" else "Accept", fontSize = 11.sp)
                        }

                        OutlinedButton(
                            onClick = { showDisputeDialog = true },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.outlinedButtonColors(
                                contentColor = if (termsState == "DISPUTED") ErrorRed else OnSurfaceVariant
                            )
                        ) {
                            Icon(Icons.Default.Close, contentDescription = null, modifier = Modifier.size(14.dp))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Dispute", fontSize = 11.sp)
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
                            Text("Verified Scale Snap: 2.30 kg", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = OnSurface)
                            Text("Tare calibrated: -0.20 kg insulation tare", fontSize = 10.sp, color = OnSurfaceVariant)
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
                            Text("Okhla Hub, Bay 4 (GPS Accurate)", fontSize = 11.sp, color = OnSurfaceVariant)
                        }
                        Text("Today, 02:45 PM", fontSize = 11.sp, color = OnSurfaceVariant)
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CheckCircle, contentDescription = null, tint = PrimaryContainer, modifier = Modifier.size(14.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "HASH: ${proposal.canonicalHash.take(16)}...",
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
                    isSaving = true
                    coroutineScope.launch {
                        proposal = handoverRepository.createProposalAtomic(
                            lotId = lotId,
                            collectorId = accountId,
                            facilityId = proposal.facilityId,
                            facilityName = proposal.facilityName,
                            materialId = proposal.materialId,
                            materialName = proposal.materialName,
                            condition = proposal.condition,
                            estimatedWeightG = proposal.estimatedWeightG,
                            measuredWeightG = proposal.measuredWeightG ?: 2300L,
                            rateInrPerKg = proposal.rateInrPerKg,
                            totalPayoutInr = if (termsState == "ACCEPTED") 414.0 else 450.0,
                            isDemo = true
                        )
                        isSaving = false
                        savedSuccessToast = true
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
                enabled = !isSaving
            ) {
                Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = if (isSaving) "Saving..." else "Save & Generate Handover Record / हस्तनांतरण सहेजें",
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
                                Text("Handover Saved Locally!", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = OnSurface)
                                Text("Receipt ${proposal.referenceCode} queued for network sync.", fontSize = 11.sp, color = OnSurfaceVariant)
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
