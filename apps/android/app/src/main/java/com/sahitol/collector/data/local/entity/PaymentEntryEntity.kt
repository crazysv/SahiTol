package com.sahitol.collector.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

/** Durable local projection of a payment assertion; server acknowledgement is separate. */
@Entity(
    tableName = "payment_entries",
    indices = [Index(value = ["accountId"]), Index(value = ["transactionId"])]
)
data class PaymentEntryEntity(
    @PrimaryKey val paymentId: String,
    val accountId: String,
    val transactionId: String,
    val amountPaise: Long,
    val method: String,
    val privateReference: String?,
    val assertedByRole: String,
    val assertedByName: String,
    val assertedAt: String,
    val state: String,
    val counterpartyAckBy: String?,
    val ackAt: String?,
    val reversalOf: String?,
    val reason: String?,
    val isDemo: Boolean,
    val syncState: String,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
