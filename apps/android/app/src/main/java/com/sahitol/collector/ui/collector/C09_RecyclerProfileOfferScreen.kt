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
import com.sahitol.collector.data.repository.RecyclerFacilityItem
import com.sahitol.collector.data.local.entity.LotEntity
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
    lot: LotEntity?,
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
    val lotContext = remember(lot) { lotDisplayContext(lot) }

    var facility by remember(facilityId) { mutableStateOf(facilityRepository.getFacilityDetails(facilityId) ?: RecyclerFacilityItem(
        facilityId, "Selected live facility", "Selected live facility", "Live directory", 0.0, 0, emptyList(), false,
        "Check with facility", 0.0, "Unknown", "Unknown", latitude = null, longitude = null
    )) }

    var requestState by remember { mutableStateOf(LotRequestState.READY) }
    var selectedLanguage by remember { mutableStateOf("हिंदी") }
    var liveOffer by remember { mutableStateOf<com.sahitol.collector.data.repository.RecyclerOfferItem?>(null) }
    var tradeMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(facilityId) {
        when (val result = facilityRepository.fetchLiveFacilities()) {
            is com.sahitol.collector.data.repository.TradeResult.Success -> result.value.firstOrNull { it.facilityId == facilityId }?.let { facility = it }
            is com.sahitol.collector.data.repository.TradeResult.Failure -> tradeMessage = result.message
        }
    }

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
                        modifier = Modifier.weight(1f),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
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
                                    modifier = Modifier.padding(horizontal = 5.dp, vertical = 7.dp)
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
                                text = if (lotContext.canonicalMaterialId in facility.materialsAccepted) "Listed route" else "Check route",
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
                            Column(modifier = Modifier.weight(1f, fill = false)) {
                                Text("YOUR LOT", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = OnSurfaceVariant)
                                Text(lotContext.materialLabel, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = OnSurface)
                                Text(lotContext.weightLabel, fontSize = 12.sp, color = OnSurfaceVariant)
                            }
                            Column(
                                modifier = Modifier.weight(1f, fill = false),
                                horizontalAlignment = Alignment.End
                            ) {
                                Text("ACCEPTED HERE", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SuccessGreen)
                                Text(if (lotContext.canonicalMaterialId in facility.materialsAccepted) "Listed material route" else "Route needs review", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = OnSurface)
                                Text("Final terms come from the recycler", fontSize = 12.sp, color = SuccessGreen)
                            }
                        }
                    }
                }
            }

            // There is no offer until the recycler creates a server-issued offer for this lot.
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
                            text = "Commercial offer status",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = TerracottaPrimary.copy(alpha = 0.12f)
                            ) {
                                Text(
                                    text = "No offer yet",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = TerracottaPrimary,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
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
                                    text = "The directory rate is indicative only. A recycler must create server-issued terms before you can accept an offer.",
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }
                    }
                }
            }

            // Live request and offer lifecycle. The collector never simulates or creates recycler offers.
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

                        if (tradeMessage != null) {
                            Text(tradeMessage!!, fontSize = 12.sp, color = OnSurfaceVariant)
                        }

                        when (requestState) {
                            LotRequestState.READY -> {
                                Text(
                                    text = "Send this saved lot to ${facility.nameEn}. The recycler must create an offer before you can accept terms.",
                                    fontSize = 13.sp,
                                    color = OnSurfaceVariant
                                )
                                Button(
                                    onClick = {
                                        coroutineScope.launch {
                                            when (val result = facilityRepository.requestRecycler(lotId, facility.facilityId, accountId)) {
                                                is com.sahitol.collector.data.repository.TradeResult.Success -> requestState = LotRequestState.WAITING_FOR_RESPONSE
                                                is com.sahitol.collector.data.repository.TradeResult.Failure -> tradeMessage = result.message
                                            }
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
                                    Text("Request recycler offer", fontSize = 15.sp)
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
                                        onClick = {
                                            coroutineScope.launch {
                                                when (val result = facilityRepository.fetchLiveOffers(lotId, accountId)) {
                                                    is com.sahitol.collector.data.repository.TradeResult.Success -> {
                                                        liveOffer = result.value.firstOrNull { it.facilityId == facility.facilityId && it.status == "OPEN" }
                                                        requestState = if (liveOffer == null) LotRequestState.WAITING_FOR_RESPONSE else LotRequestState.OFFER_RECEIVED
                                                        if (liveOffer == null) tradeMessage = "No live offer yet. Ask the recycler to create one, then refresh."
                                                    }
                                                    is com.sahitol.collector.data.repository.TradeResult.Failure -> tradeMessage = result.message
                                                }
                                            }
                                        },
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        Text("Refresh live offers")
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
                                        Text("₹${liveOffer?.totalPayoutInr ?: 0.0} offered", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = SuccessGreen)
                                        Text("This is a live recycler offer. Accepting will verify its server-issued terms.", fontSize = 12.sp, color = OnSurface)
                                    }
                                }

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    OutlinedButton(
                                        onClick = {
                                            requestState = LotRequestState.OFFER_REJECTED
                                        },
                                        modifier = Modifier.weight(1f).heightIn(min = 60.dp),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Icon(Icons.Default.Close, contentDescription = null, modifier = Modifier.size(16.dp))
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Text("Reject", maxLines = 1)
                                    }

                                    Button(
                                        onClick = {
                                            coroutineScope.launch {
                                                val offer = liveOffer
                                                if (offer == null) tradeMessage = "Refresh the live offer before accepting."
                                                else when (val result = facilityRepository.acceptLiveOffer(offer, accountId)) {
                                                    is com.sahitol.collector.data.repository.TradeResult.Success -> requestState = LotRequestState.OFFER_ACCEPTED
                                                    is com.sahitol.collector.data.repository.TradeResult.Failure -> tradeMessage = result.message
                                                }
                                            }
                                        },
                                        modifier = Modifier.weight(1f).heightIn(min = 60.dp),
                                        shape = RoundedCornerShape(10.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = SuccessGreen)
                                    ) {
                                        Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(16.dp))
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Text("Accept\nOffer", maxLines = 2, lineHeight = 16.sp)
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
                                            modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp),
                                            shape = RoundedCornerShape(8.dp),
                                            colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                                        ) {
                                            Icon(Icons.Default.ArrowForward, contentDescription = null, modifier = Modifier.size(16.dp))
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Text("Proceed to Handover / हस्तनांतरण करें", maxLines = 2)
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
