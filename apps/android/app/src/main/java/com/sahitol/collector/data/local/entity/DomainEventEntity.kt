package com.sahitol.collector.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(
    tableName = "domain_events",
    indices = [
        Index(value = ["accountId"]),
        Index(value = ["entityType", "entityId"]),
        Index(value = ["createdAt"])
    ]
)
data class DomainEventEntity(
    @PrimaryKey
    val eventId: String = UUID.randomUUID().toString(),
    val accountId: String,
    val entityType: String,
    val entityId: String,
    val eventType: String,
    val payloadJson: String,
    val prevHash: String,
    val currentHash: String,
    val createdAt: Long = System.currentTimeMillis()
)
