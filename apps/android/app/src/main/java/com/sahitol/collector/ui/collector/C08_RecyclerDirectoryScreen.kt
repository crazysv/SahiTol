package com.sahitol.collector.ui.collector

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
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
import com.sahitol.collector.data.repository.TradeResult
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.ui.theme.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C08_RecyclerDirectoryScreen(
    lotId: String,
    lot: LotEntity?,
    facilityRepository: FacilityRepository,
    sessionManager: SessionManager,
    onNavigateBack: () -> Unit,
    onNavigateFacilityProfile: (String, String) -> Unit,
    onNavigateHome: () -> Unit,
    onNavigateSync: () -> Unit,
    onNavigateSettings: () -> Unit
) {
    val lotContext = remember(lot) { lotDisplayContext(lot) }
    var searchQuery by remember { mutableStateOf("") }
    var selectedFilter by remember { mutableStateOf("ALL") }
    var selectedArea by remember { mutableStateOf("ALL") }

    var liveFacilities by remember { mutableStateOf<List<RecyclerFacilityItem>>(emptyList()) }
    var directoryMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()
    LaunchedEffect(Unit) {
        when (val result = facilityRepository.fetchLiveFacilities()) {
            is TradeResult.Success -> liveFacilities = result.value
            is TradeResult.Failure -> directoryMessage = result.message
        }
    }
    val facilities = remember(selectedArea, searchQuery, liveFacilities, lotContext) {
        val list = liveFacilities.ifEmpty { facilityRepository.getFacilities(if (selectedArea == "ALL") null else selectedArea) }
        val eligible = lotContext.canonicalMaterialId?.let { materialId ->
            list.filter { materialId in it.materialsAccepted }
        } ?: list
        if (searchQuery.isBlank()) eligible else eligible.filter {
            it.nameEn.contains(searchQuery, ignoreCase = true) ||
            it.nameLocal.contains(searchQuery, ignoreCase = true) ||
            it.address.contains(searchQuery, ignoreCase = true)
        }
    }
    // Cached directory entries are deliberately browse-only.  A server-issued facility id is
    // required before a lot can be sent to a recycler, so never route a cached card into C09.
    val hasLiveDirectory = liveFacilities.isNotEmpty()

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
                            text = "Recycler Directory",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
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
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            item {
                Spacer(modifier = Modifier.height(4.dp))
                // Lot Context Banner
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.3f))
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
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
                                modifier = Modifier.size(22.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text(
                                    text = "${lotContext.materialLabel} · ${lotContext.weightLabel}",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = lotContext.detailLabel,
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }

                        SuggestionChip(
                            onClick = {},
                            label = { Text(if (lotContext.isConcreteLot) "Route match" else "Select lot", fontSize = 11.sp) },
                            colors = SuggestionChipDefaults.suggestionChipColors(
                                containerColor = SuccessGreen.copy(alpha = 0.12f),
                                labelColor = SuccessGreen
                            )
                        )
                    }
                }
            }

            // Search Bar & Mic
            item {
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    placeholder = { Text("Search recyclers, mandi, yards...") },
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                    trailingIcon = {
                        IconButton(onClick = {}) {
                            Icon(Icons.Default.Search, contentDescription = "Search", tint = TerracottaPrimary)
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    singleLine = true
                )
            }

            // Quick Filter Chips
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    listOf(
                        "ALL" to "All Eligible (${facilities.size})",
                        "NEARBY" to "< 3 km",
                        "OPEN" to "Open Now",
                        "LANG" to "मराठी / हिंदी"
                    ).forEach { (fKey, fLabel) ->
                        val isSelected = selectedFilter == fKey
                        FilterChip(
                            selected = isSelected,
                            onClick = { selectedFilter = fKey },
                            label = { Text(fLabel, fontSize = 12.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = TerracottaPrimary,
                                selectedLabelColor = Color.White
                            )
                        )
                    }
                }
            }

            // Live Yard Radar / GPS Map Banner
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = TerracottaPrimary.copy(alpha = 0.08f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, TerracottaPrimary.copy(alpha = 0.25f))
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            modifier = Modifier.weight(1f),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.Place,
                                contentDescription = null,
                                tint = TerracottaPrimary,
                                modifier = Modifier.size(24.dp)
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(
                                    text = "Live Yard Radar",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "GPS located Dadar / Central Zone",
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }

                        OutlinedButton(
                            onClick = { /* Recenter */ },
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 8.dp)
                        ) {
                            Text("Recenter", fontSize = 11.sp, color = TerracottaPrimary)
                        }
                    }
                }
            }

            // Offline Cache Notice
            item {
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = SurfaceContainerLowest,
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.3f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            modifier = Modifier.weight(1f),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.Refresh,
                                contentDescription = null,
                                tint = OnSurfaceVariant,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = if (hasLiveDirectory) "Live Recycler Directory" else "Offline Reference Directory",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = OnSurface
                                )
                                Text(
                                    text = if (hasLiveDirectory) "Live facilities can receive a recycler request" else "Reference entries cannot receive a recycler request",
                                    fontSize = 11.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }

                        TextButton(
                            modifier = Modifier.widthIn(min = 88.dp),
                            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 6.dp),
                            onClick = {
                            directoryMessage = null
                            coroutineScope.launch {
                                // Reference entries remain browseable offline, but this explicit
                                // action always refreshes only from the live directory.
                                when (val result = facilityRepository.fetchLiveFacilities()) {
                                    is TradeResult.Success -> liveFacilities = result.value
                                    is TradeResult.Failure -> directoryMessage = result.message
                                }
                            }
                        }) {
                            Text("Refresh", fontSize = 12.sp, color = TerracottaPrimary)
                        }
                    }
                }
            }

            if (directoryMessage != null) {
                item { Text(directoryMessage!!, fontSize = 12.sp, color = OnSurfaceVariant) }
            }

            if (!hasLiveDirectory) {
                item {
                    Text(
                        text = "To request an offer, connect to the internet and tap Refresh. Your saved lot will remain safe on this phone.",
                        fontSize = 12.sp,
                        color = OnSurfaceVariant
                    )
                }
            }

            // Recycler Facilities List
            items(facilities) { facility ->
                RecyclerDirectoryCard(
                    facility = facility,
                    materialLabel = lotContext.materialLabel,
                    enabled = lotContext.isConcreteLot && hasLiveDirectory,
                    isLiveFacility = hasLiveDirectory,
                    onClick = { if (lotContext.isConcreteLot && hasLiveDirectory) onNavigateFacilityProfile(facility.facilityId, lotId) }
                )
            }

            // GPS Fallback & Manual Area Selection Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.4f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Default.Place,
                                contentDescription = null,
                                tint = OnSurfaceVariant,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text(
                                    text = "Need to search another locality?",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "GPS access is restricted or offline. Select area manually:",
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }

                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            listOf(
                                "ALL" to "All Areas (सभी)",
                                "Dadar" to "Dadar / Matunga",
                                "Mayapuri" to "Mayapuri Hub",
                                "Okhla" to "Okhla Industrial",
                                "Kurla" to "Kurla / Ghatkopar"
                            ).forEach { (aKey, aLabel) ->
                                val isSelected = selectedArea == aKey
                                SuggestionChip(
                                    onClick = { selectedArea = aKey },
                                    label = { Text(aLabel, fontSize = 12.sp) },
                                    colors = SuggestionChipDefaults.suggestionChipColors(
                                        containerColor = if (isSelected) TerracottaPrimary.copy(alpha = 0.15f) else Color.Transparent
                                    ),
                                    border = SuggestionChipDefaults.suggestionChipBorder(
                                        enabled = true,
                                        borderColor = if (isSelected) TerracottaPrimary else OutlineVariantColor
                                    )
                                )
                            }
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
fun RecyclerDirectoryCard(
    facility: RecyclerFacilityItem,
    materialLabel: String,
    enabled: Boolean,
    isLiveFacility: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = enabled, onClick = onClick),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
        border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.35f))
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
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = facility.nameEn,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                    Text(
                        text = "${facility.nameLocal} • ${facility.address}",
                        fontSize = 12.sp,
                        color = OnSurfaceVariant
                    )
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "${facility.distanceKm} km",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = TerracottaPrimary
                    )
                    Text(
                        text = "~${facility.travelTimeMinutes} min route",
                        fontSize = 11.sp,
                        color = OnSurfaceVariant
                    )
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                SuggestionChip(
                    onClick = {},
                    label = { Text("$materialLabel route", fontSize = 11.sp, maxLines = 1) },
                    colors = SuggestionChipDefaults.suggestionChipColors(
                        containerColor = SuccessGreen.copy(alpha = 0.10f),
                        labelColor = SuccessGreen
                    )
                )
                if (facility.instantUpi) {
                    SuggestionChip(
                        onClick = {},
                        label = { Text("Instant UPI Payout", fontSize = 11.sp) },
                        colors = SuggestionChipDefaults.suggestionChipColors(
                            containerColor = TerracottaPrimary.copy(alpha = 0.10f),
                            labelColor = TerracottaPrimary
                        )
                    )
                }
            }

            HorizontalDivider(color = OutlineVariantColor.copy(alpha = 0.2f))

            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Info,
                        contentDescription = null,
                        tint = OnSurfaceVariant,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = if (isLiveFacility) {
                            "${facility.operatingHours} · ₹${facility.rateInrPerKg.toInt()}/kg rate"
                        } else {
                            "Reference only — refresh to request an offer"
                        },
                        fontSize = 12.sp,
                        color = OnSurfaceVariant
                    )
                }

                Button(
                    onClick = onClick,
                    enabled = enabled,
                    modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary)
                ) {
                    Icon(Icons.Default.ArrowForward, contentDescription = null, modifier = Modifier.size(14.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(if (isLiveFacility) "View facility" else "Reference only — refresh to request", fontSize = 12.sp)
                }
            }
        }
    }
}
