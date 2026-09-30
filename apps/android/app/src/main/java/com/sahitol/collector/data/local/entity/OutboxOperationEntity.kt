package com.sahitol.collector.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(
    tableName = "outbox_operations",
    indices = [
        Index(value = ["accountId"]),
        Index(value = ["state"]),
        Index(value = ["entityType", "entityId"]),
        Index(value = ["createdAt"])
    ]
)
data class OutboxOperationEntity(
    @PrimaryKey
    val operationId: String = UUID.randomUUID().toString(),
    val accountId: String,
    val deviceId: String,
    val entityType: String,
    val entityId: String,
    val command: String,
    val expectedVersion: Long = 0,
    val payloadJson: String,
    val payloadSha256: String,
    val dependsOnJson: String = "[]",
    val mediaIdsJson: String = "[]",
    val createdAt: Long = System.currentTimeMillis(),
    val attemptCount: Int = 0,
    val nextAttemptAt: Long = System.currentTimeMillis(),
    val state: String = "QUEUED",
    val lastErrorCode: String? = null
)
