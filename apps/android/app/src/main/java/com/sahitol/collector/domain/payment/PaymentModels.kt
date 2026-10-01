package com.sahitol.collector.domain.payment

import java.time.Instant
import java.util.UUID

enum class PaymentMethod {
    CASH,
    UPI,
    OTHER
}

enum class PaymentState {
    ASSERTED,
    ACKNOWLEDGED,
    DISPUTED,
    REVERSED
}

data class PaymentEntry(
    val id: String = UUID.randomUUID().toString(),
    val transactionId: String,
    val amountPaise: Long,
    val method: PaymentMethod = PaymentMethod.CASH,
    val privateReference: String? = null,
    val assertedByRole: String = "COLLECTOR",
    val assertedByName: String = "Collector Santosh",
    val assertedAt: String = Instant.now().toString(),
    var state: PaymentState = PaymentState.ASSERTED,
    var counterpartyAckBy: String? = null,
    var ackAt: String? = null,
    val reversalOf: String? = null,
    var reason: String? = null,
    val isDemo: Boolean = true,
    var syncState: String = "SAVED_LOCAL_ONLY"
) {
    val amountInr: Double
        get() = amountPaise / 100.0
}

data class TransactionSummary(
    val transactionId: String = UUID.randomUUID().toString(),
    val lotId: String = UUID.randomUUID().toString(),
    val referenceCode: String = "ST-24A7",
    val materialNameEn: String,
    val materialNameHi: String,
    val materialCategory: String = "CABLE",
    val facilityName: String,
    val dateFormatted: String,
    val weightKg: Double,
    val ratePerKgInr: Double,
    val grossAgreedPaise: Long,
    var lifecycle: String = "CONFIRMED", // "CONFIRMED", "SETTLED", "DISPUTED", "CLOSED"
    val isDemo: Boolean = true,
    val isOfflineSavedOnly: Boolean = false,
    val disputeReason: String? = null,
    val payments: MutableList<PaymentEntry> = mutableListOf()
) {
    val grossAgreedInr: Double
        get() = grossAgreedPaise / 100.0

    val acknowledgedPaidPaise: Long
        get() = payments.filter { it.state == PaymentState.ACKNOWLEDGED }.sumOf { it.amountPaise }

    val acknowledgedPaidInr: Double
        get() = acknowledgedPaidPaise / 100.0

    val assertedPendingPaise: Long
        get() = payments.filter { it.state == PaymentState.ASSERTED }.sumOf { it.amountPaise }

    val assertedPendingInr: Double
        get() = assertedPendingPaise / 100.0

    val disputedPaise: Long
        get() = payments.filter { it.state == PaymentState.DISPUTED }.sumOf { it.amountPaise }

    val remainingDuesPaise: Long
        // An assertion records a claim only. It does not reduce a collector's
        // due until the counterparty acknowledgement is received from server.
        get() = maxOf(0L, grossAgreedPaise - acknowledgedPaidPaise)

    val remainingDuesInr: Double
        get() = remainingDuesPaise / 100.0

    val isSettled: Boolean
        get() = remainingDuesPaise == 0L && disputedPaise == 0L && disputeReason == null
}

data class CollectorLedgerSummary(
    val monthKey: String = "2026-09",
    val monthLabelEn: String = "September 2026",
    val monthLabelHi: String = "सितंबर २०२६",
    val isDemoIsolated: Boolean = true,
    val transactions: List<TransactionSummary>
) {
    val totalAgreedPaise: Long
        get() = transactions.sumOf { it.grossAgreedPaise }

    val totalAgreedInr: Double
        get() = totalAgreedPaise / 100.0

    val acknowledgedPaidPaise: Long
        get() = transactions.sumOf { it.acknowledgedPaidPaise }

    val acknowledgedPaidInr: Double
        get() = acknowledgedPaidPaise / 100.0

    val assertedPendingPaise: Long
        get() = transactions.sumOf { it.assertedPendingPaise }

    val assertedPendingInr: Double
        get() = assertedPendingPaise / 100.0

    val remainingDuesPaise: Long
        get() = transactions.sumOf { it.remainingDuesPaise }

    val remainingDuesInr: Double
        get() = remainingDuesPaise / 100.0

    val savedOnDevicePendingSlips: Int
        get() = transactions.count { it.isOfflineSavedOnly || it.payments.any { p -> p.syncState == "SAVED_LOCAL_ONLY" } }

    val disputedCount: Int
        get() = transactions.count { it.disputedPaise > 0L || it.lifecycle == "DISPUTED" || it.disputeReason != null }
}
