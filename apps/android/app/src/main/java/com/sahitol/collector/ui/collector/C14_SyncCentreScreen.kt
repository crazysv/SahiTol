package com.sahitol.collector.ui.collector

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.ui.theme.*

/**
 * Screen C14: Sync Centre & Collector Movement Board (Stitch screens 565a8be33852 and 3f09445d4d5d).
 * Features:
 * - Network status & offline reassurance banner.
 * - 4 Summary Counters: Saved, Waiting, Sending, Synced.
 * - Movement Board divided into:
 *   - Sending to Cloud (SENDING)
 *   - Waiting to Sync (QUEUED, RETRY_WAIT)
 *   - Action Required (NEEDS_REVIEW, NEEDS_REPAIR, AUTH_REQUIRED)
 *   - Synchronized (ACKNOWLEDGED)
 * - Immediate "Sync Now / अभी सिंक करें" trigger (invokes SyncWorker).
 * - Safe Logout options.
 */
@Composable
fun C14_SyncCentreScreen(
    unsyncedCount: Int,
    operations: List<OutboxOperationEntity>,
    isSyncing: Boolean,
    onTriggerSync: () -> Unit,
    onSafeLogout: () -> Unit,
    onBack: () -> Unit
) {
    val queuedOps = remember(operations) { operations.filter { it.state == "QUEUED" || it.state == "RETRY_WAIT" } }
    val sendingOps = remember(operations) { operations.filter { it.state == "SENDING" } }
    val exceptionOps = remember(operations) { operations.filter { it.state in listOf("NEEDS_REVIEW", "NEEDS_REPAIR", "AUTH_REQUIRED") } }
    val ackOps = remember(operations) { operations.filter { it.state == "ACKNOWLEDGED" } }

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
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        IconButton(onClick = onBack) {
                            Icon(
                                imageVector = Icons.Default.ArrowBack,
                                contentDescription = "Back",
                                tint = OnSurface
                            )
                        }
                        Text(
                            modifier = Modifier.weight(1f),
                            text = "Sync Centre / डेटा सिंक केंद्र",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(NeutralSurface)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Spacer(modifier = Modifier.height(4.dp))
                // Top Header Card (Stitch C14)
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "COLLECTOR MOVEMENT BOARD",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary
                            )
                            Text(
                                text = "डेटा सिंक स्थिति",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                color = OnSurface,
                                maxLines = 2,
                                overflow = TextOverflow.Ellipsis
                            )
                            Text(
                                text = "Offline-first ledger & dispatch manager",
                                style = MaterialTheme.typography.bodySmall,
                                color = OnSurfaceVariant
                            )
                        }

                        Box(
                            modifier = Modifier
                                .size(48.dp)
                                .clip(CircleShape)
                                .background(PrimaryContainer),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                    }
                }
            }

            // Offline Reassurance & Sync Action Banner (Stitch C14)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerHigh)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                            modifier = Modifier.weight(1f)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(CircleShape)
                                    .background(if (unsyncedCount > 0) SecondaryContainer else SuccessGreen.copy(alpha = 0.2f)),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = if (unsyncedCount > 0) "⚡" else "✓",
                                    fontSize = 16.sp
                                )
                            }

                            Column {
                                Text(
                                    text = if (unsyncedCount > 0) "डेटा सुरक्षित है (Records Safe)" else "सभी रिकॉर्ड सिंक हैं (All Synced)",
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = OnSurface
                                )
                                Text(
                                    text = if (unsyncedCount > 0) "$unsyncedCount रिकॉर्ड कतार में हैं" else "क्लाउड से पूर्णतः सत्यापित",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = OnSurfaceVariant
                                )
                            }
                        }

                        Button(
                            onClick = onTriggerSync,
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = TerracottaPrimary),
                            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 8.dp),
                            enabled = !isSyncing
                        ) {
                            Text(
                                text = if (isSyncing) "सिंक हो रहा है..." else "Sync Now",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        }
                    }
                }
            }

            // Summary 4-Counter Grid (Stitch C14)
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    StatusCountCard("Saved", (operations.size).toString(), OnSurface, Modifier.weight(1f))
                    StatusCountCard("Waiting", queuedOps.size.toString(), MustardSecondary, Modifier.weight(1f))
                    StatusCountCard("Sending", sendingOps.size.toString(), TerracottaPrimary, Modifier.weight(1f))
                    StatusCountCard("Synced", ackOps.size.toString(), SuccessGreen, Modifier.weight(1f))
                }
            }

            // Section 1: Waiting to Sync (Stitch C14)
            if (queuedOps.isNotEmpty()) {
                item {
                    Text(
                        text = "Waiting to Sync / सिंक की प्रतीक्षा में (${queuedOps.size})",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = OnSurface
                    )
                }

                items(queuedOps) { op ->
                    OutboxOpCard(op = op, badgeColor = MustardSecondary, badgeText = "Queued Locally")
                }
            }

            // Section 2: Exceptions / Action Required (Stitch C14)
            if (exceptionOps.isNotEmpty()) {
                item {
                    Text(
                        text = "Action Required / ध्यान दें (${exceptionOps.size})",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = ErrorRed
                    )
                }

                items(exceptionOps) { op ->
                    OutboxOpCard(op = op, badgeColor = ErrorRed, badgeText = op.state)
                }
            }

            // Section 3: Synchronized Recently (Stitch C14)
            if (ackOps.isNotEmpty()) {
                item {
                    Text(
                        text = "Synchronized / सिंक हो चुके (${ackOps.size})",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = SuccessGreen
                    )
                }

                items(ackOps.take(5)) { op ->
                    OutboxOpCard(op = op, badgeColor = SuccessGreen, badgeText = "Confirmed Cloud")
                }
            }

            // Safe Logout Action (Stitch C14 / R-AUTH-03)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
                    border = androidx.compose.foundation.BorderStroke(1.dp, OutlineColor.copy(alpha = 0.2f))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "सुरक्षित लॉगआउट (Safe Logout)",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = OnSurface
                        )
                        Text(
                            text = "लॉगआउट करने पर भी आपका ऑफलाइन डेटा और अनसिंक्ड रिकॉर्ड फोन पर सुरक्षित रहेंगे।",
                            style = MaterialTheme.typography.bodySmall,
                            color = OnSurfaceVariant
                        )
                        OutlinedButton(
                            onClick = onSafeLogout,
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = "Safe Logout Options",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.Bold,
                                color = TerracottaPrimary
                            )
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
private fun StatusCountCard(
    title: String,
    count: String,
    accentColor: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.height(72.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLow)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.labelSmall,
                color = OnSurfaceVariant,
                fontSize = 11.sp
            )
            Text(
                text = count,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = accentColor
            )
        }
    }
}

@Composable
private fun OutboxOpCard(
    op: OutboxOperationEntity,
    badgeColor: Color,
    badgeText: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceContainerLowest),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "${op.command} • #${op.entityId.take(8)}",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = OnSurface,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = "EntityType: ${op.entityType} • Attempts: ${op.attemptCount}",
                    style = MaterialTheme.typography.labelSmall,
                    color = OnSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }

            Box(
                modifier = Modifier
                    .padding(start = 8.dp)
                    .widthIn(max = 112.dp)
                    .clip(RoundedCornerShape(6.dp))
                    .background(badgeColor.copy(alpha = 0.15f))
                    .padding(horizontal = 8.dp, vertical = 4.dp)
            ) {
                Text(
                    text = badgeText,
                    style = MaterialTheme.typography.labelSmall,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold,
                    color = badgeColor,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}
