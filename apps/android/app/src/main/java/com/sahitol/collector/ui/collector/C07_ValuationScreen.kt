package com.sahitol.collector.ui.collector

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.repository.FacilityRepository
import com.sahitol.collector.data.repository.PriceRepository
import com.sahitol.collector.data.repository.RecyclerOfferItem
import com.sahitol.collector.data.repository.ValuationRange
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.ui.theme.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C07_ValuationScreen(
    lotId: String,
    priceRepository: PriceRepository,
    facilityRepository: FacilityRepository,
    sessionManager: SessionManager,
    onNavigateBack: () -> Unit,
    onNavigateDirectory: (String) -> Unit,
    onNavigateHandover: (String) -> Unit,
    onNavigateHome: () -> Unit,
    onNavigateSync: () -> Unit,
    onNavigateSettings: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val session by sessionManager.session.collectAsState()
    val accountId = session.accountId

    val valuation = remember(lotId) {
        priceRepository.calculateValuation("MAT-CAB-01", 2500, "GOOD")
    }

    var offers by remember { mutableStateOf<List<RecyclerOfferItem>>(emptyList()) }
    var offerMessage by remember { mutableStateOf<String?>(null) }

    var isRateBasisExpanded by remember { mutableStateOf(false) }
    var acceptedOfferName by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(lotId, accountId) {
        when (val result = facilityRepository.fetchLiveOffers(lotId, accountId)) {
            is com.sahitol.collector.data.repository.TradeResult.Success -> offers = result.value
            is com.sahitol.collector.data.repository.TradeResult.Failure -> offerMessage = result.message
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
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = onNavigateBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                        }
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            modifier = Modifier.weight(1f),
                            text = "Valuation & Offers",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }

                    // Offline Badge
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = SuccessGreen.copy(alpha = 0.12f),
                        border = androidx.compose.foundation.BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.3f))
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(CircleShape)
                                    .background(SuccessGreen)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "Offline Ready",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = SuccessGreen
                            )
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
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Spacer(modifier = Modifier.height(4.dp))
                // Lot Header Card
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
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                modifier = Modifier.weight(1f),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Default.Build,
                                    contentDescription = null,
                                    tint = TerracottaPrimary,
                                    modifier = Modifier.size(24.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = "Copper Cable Lot",
                                        fontSize = 16.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = OnSurface,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                    Text(
                                        text = "केबल (तांबा) · 2.5 kg · Good Condition",
                                        fontSize = 12.sp,
                                        color = OnSurfaceVariant,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
                            }

                            SuggestionChip(
                                onClick = {},
                                label = { Text("Verified", fontSize = 11.sp, maxLines = 1) },
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
                            Row(
                                modifier = Modifier.weight(1f),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Default.LocationOn,
                                    contentDescription = null,
                                    tint = OnSurfaceVariant,
                                    modifier = Modifier.size(14.dp)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = valuation.yardLocation,
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                            }
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    Icons.Default.Info,
                                    contentDescription = null,
                                    tint = OnSurfaceVariant,
                                    modifier = Modifier.size(14.dp)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = "Just now",
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }
                    }
                }
            }

            // Estimated Value Range Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = TerracottaPrimary.copy(alpha = 0.08f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, TerracottaPrimary.copy(alpha = 0.3f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Estimated Value Range / अनुमानित मूल्य",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = TerracottaPrimary
                        )

                        Text(
                            text = "₹ ${valuation.lowInr} – ₹ ${valuation.highInr}",
                            fontSize = 32.sp,
                            fontWeight = FontWeight.Bold,
                            color = TerracottaPrimary
                        )

                        Text(
                            text = "Based on ${valuation.weightKg} kg × ₹ ${valuation.ratePerKgLowInr}–₹ ${valuation.ratePerKgHighInr}/kg indicative scrap market rate.",
                            fontSize = 13.sp,
                            color = OnSurfaceVariant
                        )

                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = Color.White.copy(alpha = 0.8f),
                            border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.3f))
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Default.CheckCircle,
                                    contentDescription = null,
                                    tint = SuccessGreen,
                                    modifier = Modifier.size(14.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = "${valuation.syncAgeText} • ${valuation.confidenceTier} Confidence",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = OnSurfaceVariant
                                )
                            }
                        }
                    }
                }
            }

            // Rate Basis & Evidence Expandable Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.3f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { isRateBasisExpanded = !isRateBasisExpanded },
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Rate Basis & Evidence / मूल्य आधार",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = OnSurface
                            )
                            Icon(
                                if (isRateBasisExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                                contentDescription = null,
                                tint = OnSurfaceVariant
                            )
                        }

                        AnimatedVisibility(visible = isRateBasisExpanded) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(top = 10.dp),
                                verticalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                HorizontalDivider(color = OutlineVariantColor.copy(alpha = 0.2f))
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text("Market Grade A Copper Blend", fontSize = 12.sp, color = OnSurfaceVariant)
                                    Text("₹ ${valuation.baseRateInr} / kg max", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = OnSurface)
                                }
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(valuation.deductionReason, fontSize = 12.sp, color = ErrorRed)
                                    Text("- ₹ ${valuation.deductionInr} / kg", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = ErrorRed)
                                }
                                Text(
                                    text = "Note: Offline cached pricing active. Rates will auto-reconcile upon full network sync.",
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant,
                                    modifier = Modifier.padding(top = 4.dp)
                                )
                            }
                        }
                    }
                }
            }

            // Recycler Offers Section Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Recycler Offers / खरीदार बोलियां",
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "${offers.count { it.status == "OPEN" }} live offers available",
                            fontSize = 12.sp,
                            color = OnSurfaceVariant
                        )
                    }

                    TextButton(onClick = { onNavigateDirectory(lotId) }) {
                        Text("View Directory", color = TerracottaPrimary, maxLines = 1)
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(Icons.Default.ArrowForward, contentDescription = null, modifier = Modifier.size(16.dp))
                    }
                }
            }

            if (offerMessage != null) {
                item {
                    Text(offerMessage!!, fontSize = 12.sp, color = OnSurfaceVariant)
                }
            }

            // Offers List
            items(offers) { offer ->
                RecyclerOfferCard(
                    offer = offer,
                    onAccept = {
                        coroutineScope.launch {
                            when (val result = facilityRepository.acceptLiveOffer(offer, accountId)) {
                                is com.sahitol.collector.data.repository.TradeResult.Success -> {
                                    acceptedOfferName = offer.facilityName
                                    onNavigateHandover(lotId)
                                }
                                is com.sahitol.collector.data.repository.TradeResult.Failure -> offerMessage = result.message
                            }
                        }
                    }
                )
            }

            // Offer Accepted Banner
            if (acceptedOfferName != null) {
                item {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = SuccessGreen.copy(alpha = 0.15f),
                        border = androidx.compose.foundation.BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.4f)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(14.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.CheckCircle,
                                contentDescription = null,
                                tint = SuccessGreen,
                                modifier = Modifier.size(24.dp)
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "Offer Accepted!",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = SuccessGreen
                                )
                                Text(
                                    text = "Weigh-slip generated for $acceptedOfferName.",
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                            IconButton(onClick = { acceptedOfferName = null }) {
                                Icon(Icons.Default.Close, contentDescription = "Dismiss", tint = OnSurfaceVariant)
                            }
                        }
                    }
                }
            }

            // Route Compatibility Card
            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.3f))
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Send,
                            contentDescription = null,
                            tint = TerracottaPrimary,
                            modifier = Modifier.size(28.dp)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(
                                text = "Route Compatibility / रूट सूचना",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface
                            )
                            Text(
                                text = "Standard scrap collection route approved for North zone. Pickup vehicle #UP-14-CZ-8891 assigned for transit.",
                                fontSize = 12.sp,
                                color = OnSurfaceVariant
                            )
                        }
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(20.dp))
            }
        }
    }
}

@Composable
fun RecyclerOfferCard(
    offer: RecyclerOfferItem,
    onAccept: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
        border = androidx.compose.foundation.BorderStroke(
            width = if (offer.isBestMatch) 2.dp else 1.dp,
            color = if (offer.isBestMatch) TerracottaPrimary else OutlineVariantColor.copy(alpha = 0.4f)
        )
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
                verticalAlignment = Alignment.Top
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape)
                            .background(TerracottaPrimary.copy(alpha = 0.12f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = offer.facilityName.take(2).uppercase(),
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = TerracottaPrimary
                        )
                    }
                    Spacer(modifier = Modifier.width(10.dp))
                    Column {
                        Text(
                            text = offer.facilityName,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = offer.routeDescription,
                            fontSize = 12.sp,
                            color = OnSurfaceVariant
                        )
                    }
                }

                if (offer.isBestMatch) {
                    SuggestionChip(
                        onClick = {},
                        label = { Text("Best Match", fontSize = 11.sp) },
                        colors = SuggestionChipDefaults.suggestionChipColors(
                            containerColor = TerracottaPrimary,
                            labelColor = Color.White
                        )
                    )
                }
            }

            HorizontalDivider(color = OutlineVariantColor.copy(alpha = 0.2f))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Offered Rate",
                        fontSize = 11.sp,
                        color = OnSurfaceVariant
                    )
                    Text(
                        text = "₹ ${offer.rateInrPerKg.toInt()} / kg",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = if (offer.offerType == "FIXED_TOTAL") "Fixed Total" else "Total Payout",
                        fontSize = 11.sp,
                        color = OnSurfaceVariant
                    )
                    Text(
                        text = "₹ ${"%.2f".format(offer.totalPayoutInr)}",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = TerracottaPrimary
                    )
                }
            }

            if (!offer.isOfflinePending) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = onAccept,
                        modifier = Modifier
                            .weight(1f)
                            .height(44.dp),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                    ) {
                        Text("Accept Offer / स्वीकार करें", fontSize = 13.sp)
                    }
                    OutlinedButton(
                        onClick = { /* Counter */ },
                        modifier = Modifier.height(44.dp),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Text("Counter", fontSize = 13.sp)
                    }
                }
            } else {
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = MustardSecondary.copy(alpha = 0.12f),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Warning,
                            contentDescription = null,
                            tint = MustardSecondary,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Waiting to sync when cellular connection restores.",
                            fontSize = 11.sp,
                            color = OnSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}
