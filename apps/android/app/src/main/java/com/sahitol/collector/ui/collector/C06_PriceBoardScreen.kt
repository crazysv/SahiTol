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
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.repository.NewPriceObservation
import com.sahitol.collector.data.repository.PriceBenchmarkItem
import com.sahitol.collector.data.repository.PriceRepository
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.ui.theme.*
import com.sahitol.collector.ui.components.SahiTolWordmark
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun C06_PriceBoardScreen(
    priceRepository: PriceRepository,
    sessionManager: SessionManager,
    onNavigateHome: () -> Unit,
    onNavigateSync: () -> Unit,
    onNavigateSettings: () -> Unit,
    onNavigateLotValuation: (String) -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    val session by sessionManager.session.collectAsState()
    val isDemo = session.isDemo
    val accountId = session.accountId

    var selectedCategory by remember { mutableStateOf("ALL") }
    val benchmarks = remember(selectedCategory) {
        priceRepository.getBenchmarks(if (selectedCategory == "ALL") null else selectedCategory)
    }

    // Observation Form States
    var obsMaterialId by remember { mutableStateOf("MAT-CAB-01") }
    var obsRateInput by remember { mutableStateOf("") }
    var obsUnit by remember { mutableStateOf("kg") }
    var obsLocation by remember { mutableStateOf("") }
    var obsSource by remember { mutableStateOf("") }
    var showObservationSuccess by remember { mutableStateOf(false) }
    var isSavingObservation by remember { mutableStateOf(false) }

    val categories = listOf(
        "ALL" to "All Materials",
        "CABLE" to "Cable (केबल)",
        "PCB" to "PCB (पीसीबी)",
        "IRON" to "Iron (लोहा)",
        "PET" to "PET (प्लास्टिक)"
    )

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
                        SahiTolWordmark(modifier = Modifier.width(104.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Collector",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = OnSurfaceVariant
                        )
                    }

                    // Connectivity badge
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
                                text = "ऑफ़लाइन तैयार (Offline)",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = SuccessGreen
                            )
                        }
                    }
                }
            }
        },
        bottomBar = {
            NavigationBar(
                containerColor = NeutralSurface,
                tonalElevation = 3.dp
            ) {
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateHome,
                    icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
                    label = { Text("Home") },
                    colors = NavigationBarItemDefaults.colors(
                        indicatorColor = TerracottaPrimary.copy(alpha = 0.15f)
                    )
                )
                NavigationBarItem(
                    selected = true,
                    onClick = { /* Current */ },
                    icon = { Icon(Icons.Default.ArrowForward, contentDescription = "Prices") },
                    label = { Text("Prices") },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = TerracottaPrimary,
                        selectedTextColor = TerracottaPrimary,
                        indicatorColor = TerracottaPrimary.copy(alpha = 0.15f)
                    )
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateSync,
                    icon = { Icon(Icons.Default.Refresh, contentDescription = "Sync") },
                    label = { Text("Sync") },
                    colors = NavigationBarItemDefaults.colors(
                        indicatorColor = TerracottaPrimary.copy(alpha = 0.15f)
                    )
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateSettings,
                    icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                    label = { Text("Settings") },
                    colors = NavigationBarItemDefaults.colors(
                        indicatorColor = TerracottaPrimary.copy(alpha = 0.15f)
                    )
                )
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
                // Title & Subtitle
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Price Board / भाव बोर्ड",
                            fontSize = 22.sp,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )
                        Text(
                            text = "Indicative yard rates and local market trends",
                            fontSize = 13.sp,
                            color = OnSurfaceVariant
                        )
                    }

                    Surface(
                        modifier = Modifier.padding(start = 8.dp),
                        shape = RoundedCornerShape(8.dp),
                        color = TerracottaPrimary.copy(alpha = 0.1f)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.CheckCircle,
                                contentDescription = null,
                                tint = TerracottaPrimary,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "Live Feed",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }
                }
            }

            // Material Category Filter Tabs
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    categories.forEach { (catKey, catLabel) ->
                        val isSelected = selectedCategory == catKey
                        FilterChip(
                            selected = isSelected,
                            onClick = { selectedCategory = catKey },
                            label = { Text(catLabel, fontSize = 13.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = TerracottaPrimary,
                                selectedLabelColor = Color.White
                            )
                        )
                    }
                }
            }

            // Benchmark Cards List
            items(benchmarks) { item ->
                PriceBenchmarkCard(item = item, onClick = { onNavigateLotValuation(item.materialId) })
            }

            // Record Field Observation Form
            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.5f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.Add,
                                contentDescription = null,
                                tint = TerracottaPrimary,
                                modifier = Modifier.size(24.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text(
                                    text = "Record Field Observation",
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = "अपनी बाजार कीमत दर्ज करें",
                                    fontSize = 12.sp,
                                    color = OnSurfaceVariant
                                )
                            }
                        }

                        HorizontalDivider(color = OutlineVariantColor.copy(alpha = 0.3f))

                        // Material Selection
                        Text(
                            text = "Select Material / सामग्री चुनें",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = OnSurface
                        )
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            listOf(
                                "MAT-CAB-01" to "Copper Wire (तांबा)",
                                "MAT-CAB-02" to "Aluminium Cable (एल्युमिनियम)",
                                "MAT-MET-01" to "Iron Scrap (लोहा)",
                                "MAT-PCB-01" to "Motherboard / PCB"
                            ).forEach { (mId, mLabel) ->
                                val isSelected = obsMaterialId == mId
                                SuggestionChip(
                                    onClick = { obsMaterialId = mId },
                                    label = { Text(mLabel, fontSize = 12.sp) },
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

                        // Observed Rate & Unit
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            OutlinedTextField(
                                value = obsRateInput,
                                onValueChange = { obsRateInput = it },
                                label = { Text("Rate (₹) / दर") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                modifier = Modifier.weight(1f),
                                singleLine = true
                            )
                            OutlinedTextField(
                                value = obsUnit,
                                onValueChange = { obsUnit = it },
                                label = { Text("Unit (इकाई)") },
                                modifier = Modifier.weight(0.8f),
                                singleLine = true
                            )
                        }

                        // Location Input
                        OutlinedTextField(
                            value = obsLocation,
                            onValueChange = { obsLocation = it },
                            label = { Text("Location / मंडी या क्षेत्र का नाम") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true
                        )

                        // Source Input
                        OutlinedTextField(
                            value = obsSource,
                            onValueChange = { obsSource = it },
                            label = { Text("Source / किससे जानकारी मिली?") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true
                        )

                        // Offline Queued Note
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.Refresh,
                                contentDescription = null,
                                tint = OnSurfaceVariant,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "Saved on this phone — waiting to sync",
                                fontSize = 12.sp,
                                color = OnSurfaceVariant
                            )
                        }

                        // Submit Button
                        Button(
                            onClick = {
                                val rateNum = obsRateInput.toDoubleOrNull() ?: 0.0
                                val ratePaise = (rateNum * 100).toLong()
                                if (ratePaise > 0) {
                                    isSavingObservation = true
                                    coroutineScope.launch {
                                        priceRepository.recordObservationAtomic(
                                            NewPriceObservation(
                                                materialId = obsMaterialId,
                                                observedRatePaise = ratePaise,
                                                unit = obsUnit,
                                                location = obsLocation.ifBlank { "Local Mandi" },
                                                sourceDescription = obsSource.ifBlank { "Field Survey" },
                                                accountId = accountId
                                            )
                                        )
                                        isSavingObservation = false
                                        showObservationSuccess = true
                                        obsRateInput = ""
                                        obsLocation = ""
                                        obsSource = ""
                                    }
                                }
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(48.dp),
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
                            enabled = !isSavingObservation && obsRateInput.isNotBlank()
                        ) {
                            Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Save Observation to Ledger")
                        }

                        if (showObservationSuccess) {
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = SuccessGreen.copy(alpha = 0.12f),
                                border = androidx.compose.foundation.BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.3f))
                            ) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        Icons.Default.CheckCircle,
                                        contentDescription = null,
                                        tint = SuccessGreen,
                                        modifier = Modifier.size(18.dp)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = "Observation Saved! Queued for sync when online.",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = SuccessGreen
                                    )
                                }
                            }
                        }
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
fun PriceBenchmarkCard(
    item: PriceBenchmarkItem,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
        border = androidx.compose.foundation.BorderStroke(1.dp, OutlineVariantColor.copy(alpha = 0.4f))
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
                        text = item.materialNameEn,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                    Text(
                        text = item.materialNameHi,
                        fontSize = 13.sp,
                        color = OnSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                Column(
                    modifier = Modifier.padding(start = 8.dp),
                    horizontalAlignment = Alignment.End
                ) {
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(
                            text = "₹ ${item.rateInrPerKg.toInt()}",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = TerracottaPrimary
                        )
                        Text(
                            text = " / kg",
                            fontSize = 12.sp,
                            color = OnSurfaceVariant,
                            modifier = Modifier.padding(bottom = 2.dp)
                        )
                    }

                    // Trend Indicator
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        val trendText = when (item.trendDirection) {
                            "UP" -> "+${item.trendPct}% this week"
                            "DOWN" -> "${item.trendPct}% this week"
                            else -> "Stable"
                        }
                        val trendColor = when (item.trendDirection) {
                            "UP" -> SuccessGreen
                            "DOWN" -> ErrorRed
                            else -> OnSurfaceVariant
                        }
                        val trendIcon = when (item.trendDirection) {
                            "UP" -> Icons.Default.ArrowForward
                            "DOWN" -> Icons.Default.ArrowDropDown
                            else -> Icons.Default.ArrowForward
                        }
                        Icon(
                            trendIcon,
                            contentDescription = null,
                            tint = trendColor,
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(3.dp))
                        Text(
                            text = trendText,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = trendColor,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
            }

            HorizontalDivider(color = OutlineVariantColor.copy(alpha = 0.2f))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Place,
                        contentDescription = null,
                        tint = OnSurfaceVariant,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = item.yardLocation,
                        fontSize = 12.sp,
                        color = OnSurfaceVariant
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
                        text = item.lastUpdated,
                        fontSize = 11.sp,
                        color = OnSurfaceVariant
                    )
                }
            }
        }
    }
}
