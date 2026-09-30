package com.sahitol.collector.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(
    tableName = "lots",
    indices = [
        Index(value = ["accountId"]),
        Index(value = ["status"]),
        Index(value = ["syncStatus"]),
        Index(value = ["createdAt"])
    ]
)
data class LotEntity(
    @PrimaryKey
    val lotId: String = UUID.randomUUID().toString(),
    val accountId: String = "collector_default",
    val materialCode: String,
    val estimatedWeightG: Long,
    val measuredWeightG: Long? = null,
    val estimatedLowPaise: Long? = null,
    val estimatedMedianPaise: Long? = null,
    val estimatedHighPaise: Long? = null,
    val localPhotoPath: String? = null,
    val status: String = "DRAFT",
    val syncStatus: String = "SAVED_LOCAL_ONLY",
    val serverVersion: Long = 0,
    val aiSuggestedCode: String? = null,
    val aiConfidence: Float? = null,
    val aiModelVersion: String? = null,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
