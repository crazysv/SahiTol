package com.sahitol.collector.ui.collector

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.repository.FacilityRepository
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.ui.theme.*
import kotlinx.coroutines.launch

enum class LotRequestState {
    READY,
    WAITING_FOR_RESPONSE,
    OFFER_RECEIVED,
    OFFLINE_QUEUED,
    OFFER_ACCEPTED,
    OFFER_REJECTED
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C09_RecyclerProfileOfferScreen(
    facilityId: String,
    lotId: String,
    facilityRepository: FacilityRepository,
    sessionManager: SessionManager,
    onNavigateBack: () -> Unit,
    onNavigateHome: () -> Unit,
    onNavigateSync: () -> Unit,
    onNavigateSettings: () -> Unit,
    onNavigateHandover: (String) -> Unit = {}
) {
    val coroutineScope = rememberCoroutineScope()
    val session by sessionManager.session.collectAsState()
    val accountId = session.accountId

    val facility = remember(facilityId) {
        facilityRepository.getFacilityDetails(facilityId) ?: facilityRepository.getFacilities().first()
    }

    var requestState by remember { mutableStateOf(LotRequestState.READY) }
    var selectedLanguage by remember { mutableStateOf("हिंदी") }

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
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = onNavigateBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                        }
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "Facility & Offer",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                    }

                    // Language toggles
                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        listOf("EN", "हिंदी", "मराठी").forEach { lang ->
                            val isSelected = selectedLanguage == lang
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = if (isSelected) TerracottaPrimary else Color.Transparent,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(6.dp))
                                    .border(1.dp, if (isSelected) TerracottaPrimary else OutlineVariantColor, RoundedCornerShape(6.dp))
                            ) {
                                Text(
                                    text = lang,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = if (isSelected) Color.White else OnSurfaceVariant,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                                )
                            }
                        }
                    }
                }
            }
        },
        containerColor = NeutralSurface
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            item {
                Spacer(modifier = Modifier.height(4.dp))
                // Facility Profile Card
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.4f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.Top
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(
                                        text = facility.nameEn,
                                        fontSize = 18.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = OnSurface
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Icon(
                                        Icons.Default.CheckCircle,
                                        contentDescription = null,
                                        tint = SuccessGreen,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                                Text(
                                    text = "${facility.address} • Authorized Recycler",
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                            }

                            SuggestionChip(
                                onClick = {},
                                label = { Text("${facility.trustScorePct}% Trust", fontSize = 11.sp) },
                                colors = SuggestionChipDefaults.suggestionChipColors(
                                    containerColor = SuccessGreen.copy(alpha = 0.12f),
                                    labelColor = SuccessGreen
                                )
                            )
                        }

                        HorizontalDivider(color = OutlineVariantColor.copy(alpha = 0.2f))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    Icons.Default.Send,
                                    contentDescription = null,
                                    tint = OnSurfaceVariant,
                                    modifier = Modifier.size(16.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = "Route Auth: ${facility.routeCode}",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = OnSurface
                                )
                            }

                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    Icons.Default.Refresh,
                                    contentDescription = null,
                                    tint = SuccessGreen,
                                    modifier = Modifier.size(16.dp)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = "Reviewed Today",
                                    fontSize = 12.sp,
                                    color = SuccessGreen
                                )
                            }
                        }
                    }
                }
            }

            // Material Compatibility Match Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SuccessGreen.copy(alpha = 0.08f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.3f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Material Compatibility Match",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    Icons.Default.CheckCircle,
                                    contentDescription = null,
                                    tint = SuccessGreen,
                                    modifier = Modifier.size(16.dp)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = "100% Match",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = SuccessGreen
                                )
                            }
                        }

                        HorizontalDivider(color = SuccessGreen.copy(alpha = 0.2f))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("YOUR LOT", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = OnSurfaceVariant)
                                Text("Cable (Copper Mixed)", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = OnSurface)
                                Text("2.5 kg net weight", fontSize = 12.sp, color = OnSurfaceVariant)
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text("ACCEPTED HERE", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SuccessGreen)
                                Text("Cable - Standard Grade A", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = OnSurface)
                                Text("Route Authorized", fontSize = 12.sp, color = SuccessGreen)
                            }
                        }
                    }
                }
            }

            // Live Commercial Offer Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.4f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Live Commercial Offer",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = TerracottaPrimary.copy(alpha = 0.12f)
                            ) {
                                Text(
                                    text = "Valid for 45 mins",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = TerracottaPrimary,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                                )
                            }
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text(
                                    text = "Offered Rate per kg",
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                                Text(
                                    text = "₹340.00 / kg",
                                    fontSize = 20.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                            }

                            Column(horizontalAlignment = Alignment.End) {
                                Text(
                                    text = "Estimated Total Payout",
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                                Text(
                                    text = "₹850.00",
                                    fontSize = 26.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = TerracottaPrimary
                                )
                            }
                        }

                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = NeutralSurface,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier.padding(10.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Default.Info,
                                    contentDescription = null,
                                    tint = OnSurfaceVariant,
                                    modifier = Modifier.size(16.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "Weighing basis: Certified digital platform scale at facility gate. Instant UPI transfer upon verification.",
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }
                    }
                }
            }

            // Interactive Request State Lifecycle & Simulator
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.4f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text(
                            text = "Lot Request & Action / लॉट कार्रवाई",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )

                        when (requestState) {
                            LotRequestState.READY -> {
                                Text(
                                    text = "Ready to dispatch 2.5 kg lot? Sending request locks the material batch to ${facility.nameEn} for 30 minutes.",
                                    fontSize = 13.sp,
                                    color = OnSurfaceVariant
                                )
                                Button(
                                    onClick = {
                                        coroutineScope.launch {
                                            facilityRepository.respondToOfferAtomic(
                                                offerId = "req_${facility.facilityId}_$lotId",
                                                action = "REQUEST_RECYCLER",
                                                accountId = accountId
                                            )
                                            requestState = LotRequestState.WAITING_FOR_RESPONSE
                                        }
                                    },
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(50.dp),
                                    shape = RoundedCornerShape(12.dp),
                                    colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                                ) {
                                    Icon(Icons.Default.Send, contentDescription = null, modifier = Modifier.size(18.dp))
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("Request / Send Lot (₹850.00)", fontSize = 15.sp)
                                }
                            }

                            LotRequestState.WAITING_FOR_RESPONSE -> {
                                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        CircularProgressIndicator(
                                            modifier = Modifier.size(20.dp),
                                            color = TerracottaPrimary,
                                            strokeWidth = 2.dp
                                        )
                                        Spacer(modifier = Modifier.width(10.dp))
                                        Text(
                                            text = "Request sent — Waiting for response",
                                            fontSize = 14.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = OnSurface
                                        )
                                    }
                                    Text(
                                        text = "${facility.nameEn} yard manager is reviewing your lot and route credentials.",
                                        fontSize = 12.sp,
                                        color = OnSurfaceVariant
                                    )
                                    OutlinedButton(
                                        onClick = { requestState = LotRequestState.OFFER_RECEIVED },
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        Text("Simulate Recipient Acceptance")
                                    }
                                }
                            }

                            LotRequestState.OFFER_RECEIVED -> {
                                Surface(
                                    shape = RoundedCornerShape(10.dp),
                                    color = SuccessGreen.copy(alpha = 0.12f),
                                    border = androidx.compose.foundation.BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.3f)),
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Column(
                                        modifier = Modifier.padding(12.dp),
                                        verticalArrangement = Arrangement.spacedBy(4.dp)
                                    ) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Text("OFFER RECEIVED", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SuccessGreen)
                                            Text("Just now", fontSize = 11.sp, color = OnSurfaceVariant)
                                        }
                                        Text("₹850.00 Approved", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = SuccessGreen)
                                        Text("Recycler has verified lot parameters and confirmed rate of ₹340/kg.", fontSize = 12.sp, color = OnSurface)
                                    }
                                }

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    OutlinedButton(
                                        onClick = {
                                            coroutineScope.launch {
                                                facilityRepository.respondToOfferAtomic("off_${facility.facilityId}", "REJECT_OFFER", accountId)
                                                requestState = LotRequestState.OFFER_REJECTED
                                            }
                                        },
                                        modifier = Modifier.weight(1f).height(46.dp),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Icon(Icons.Default.Close, contentDescription = null, modifier = Modifier.size(16.dp))
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Text("Reject")
                                    }

                                    Button(
                                        onClick = {
                                            coroutineScope.launch {
                                                facilityRepository.respondToOfferAtomic("off_${facility.facilityId}", "ACCEPT_OFFER", accountId)
                                                requestState = LotRequestState.OFFER_ACCEPTED
                                            }
                                        },
                                        modifier = Modifier.weight(1f).height(46.dp),
                                        shape = RoundedCornerShape(10.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = SuccessGreen)
                                    ) {
                                        Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(16.dp))
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Text("Accept Offer")
                                    }
                                }
                            }

                            LotRequestState.OFFER_ACCEPTED -> {
                                Surface(
                                    shape = RoundedCornerShape(10.dp),
                                    color = SuccessGreen.copy(alpha = 0.15f),
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Column(
                                        modifier = Modifier.padding(14.dp),
                                        verticalArrangement = Arrangement.spacedBy(10.dp)
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SuccessGreen)
                                            Spacer(modifier = Modifier.width(10.dp))
                                            Column {
                                                Text("Commercial Terms Accepted!", fontWeight = FontWeight.Bold, color = SuccessGreen)
                                                Text("Proceed to physical handover with QR token.", fontSize = 12.sp, color = OnSurface)
                                            }
                                        }

                                        Button(
                                            onClick = { onNavigateHandover(lotId) },
                                            modifier = Modifier.fillMaxWidth().height(44.dp),
                                            shape = RoundedCornerShape(8.dp),
                                            colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                                        ) {
                                            Icon(Icons.Default.ArrowForward, contentDescription = null, modifier = Modifier.size(16.dp))
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Text("Proceed to Handover / हस्तनांतरण करें")
                                        }
                                    }
                                }
                            }

                            LotRequestState.OFFER_REJECTED -> {
                                Text("Offer rejected. You can request another authorized facility from the directory.", fontSize = 13.sp, color = OnSurfaceVariant)
                            }

                            LotRequestState.OFFLINE_QUEUED -> {
                                Surface(
                                    shape = RoundedCornerShape(10.dp),
                                    color = MustardSecondary.copy(alpha = 0.12f),
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Row(
                                        modifier = Modifier.padding(12.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(Icons.Default.Warning, contentDescription = null, tint = MustardSecondary)
                                        Spacer(modifier = Modifier.width(10.dp))
                                        Column {
                                            Text("Saved on this phone — waiting to sync", fontWeight = FontWeight.Bold, color = OnSurface)
                                            Text("Stored locally in Room outbox. Dispatches automatically once online.", fontSize = 12.sp, color = OnSurfaceVariant)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // SahiTol Support Helpline Card
            item {
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = SurfaceContainerLowest,
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.3f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Phone,
                            contentDescription = null,
                            tint = TerracottaPrimary,
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            text = "Need assistance with this facility? Call SahiTol Support at 1800-SAHI-TOL (Toll Free).",
                            fontSize = 12.sp,
                            color = OnSurfaceVariant
                        )
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(20.dp))
            }
        }
    }
}
