package com.sahitol.collector.data.repository

import com.sahitol.collector.data.local.SahiTolDatabase
import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.domain.canonical.CanonicalJson
import com.sahitol.collector.domain.payment.CollectorLedgerSummary
import com.sahitol.collector.domain.payment.PaymentEntry
import com.sahitol.collector.domain.payment.PaymentMethod
import com.sahitol.collector.domain.payment.PaymentState
import com.sahitol.collector.domain.payment.TransactionSummary
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.json.JSONObject
import java.time.Instant
import java.util.UUID

class PaymentRepository(
    private val database: SahiTolDatabase? = null,
    private val outboxDao: OutboxDao? = database?.outboxDao(),
    private val domainEventDao: DomainEventDao? = database?.domainEventDao()
) {
    private val _transactions = MutableStateFlow<List<TransactionSummary>>(createDefaultSeedTransactions())
    val transactions: StateFlow<List<TransactionSummary>> = _transactions.asStateFlow()

    private fun createDefaultSeedTransactions(): List<TransactionSummary> {
        val tx1 = TransactionSummary(
            transactionId = "tx_cable_01",
            lotId = "lot_cable_01",
            referenceCode = "ST-24A7",
            materialNameEn = "Mixed Cable & Copper",
            materialNameHi = "तांबा तार",
            materialCategory = "CABLE",
            facilityName = "Delhi Central Yard #4",
            dateFormatted = "29 Sep, 2026",
            weightKg = 2.5,
            ratePerKgInr = 180.0,
            grossAgreedPaise = 45000L, // ₹450
            lifecycle = "CONFIRMED",
            isDemo = true,
            isOfflineSavedOnly = false,
            payments = mutableListOf(
                PaymentEntry(
                    id = "pay_01",
                    transactionId = "tx_cable_01",
                    amountPaise = 20000L, // ₹200
                    method = PaymentMethod.CASH,
                    assertedByRole = "COLLECTOR",
                    assertedByName = "Collector Santosh",
                    assertedAt = "2026-09-29T14:42:00Z",
                    state = PaymentState.ACKNOWLEDGED,
                    counterpartyAckBy = "usr_suresh_01",
                    ackAt = "2026-09-29T14:45:00Z",
                    isDemo = true,
                    syncState = "SYNCED"
                ),
                PaymentEntry(
                    id = "pay_02",
                    transactionId = "tx_cable_01",
                    amountPaise = 10000L, // ₹100
                    method = PaymentMethod.CASH,
                    assertedByRole = "COLLECTOR",
                    assertedByName = "Collector Santosh",
                    assertedAt = "2026-09-29T15:10:00Z",
                    state = PaymentState.ACKNOWLEDGED,
                    counterpartyAckBy = "usr_suresh_01",
                    ackAt = "2026-09-29T15:12:00Z",
                    isDemo = true,
                    syncState = "SYNCED"
                )
            )
        )

        val tx2 = TransactionSummary(
            transactionId = "tx_paper_02",
            lotId = "lot_paper_02",
            referenceCode = "ST-28B2",
            materialNameEn = "Old Newspaper (रद्दी)",
            materialNameHi = "रद्दी अख़बार",
            materialCategory = "PAPER",
            facilityName = "Mayapuri Scrap Mandi #1",
            dateFormatted = "28 Sep, 2026",
            weightKg = 14.0,
            ratePerKgInr = 20.0,
            grossAgreedPaise = 28000L, // ₹280
            lifecycle = "CONFIRMED",
            isDemo = true,
            isOfflineSavedOnly = true,
            payments = mutableListOf()
        )

        val tx3 = TransactionSummary(
            transactionId = "tx_iron_03",
            lotId = "lot_iron_03",
            referenceCode = "ST-27C3",
            materialNameEn = "Iron Scraps (लोहा)",
            materialNameHi = "लोहा स्क्रैप",
            materialCategory = "IRON",
            facilityName = "City Kabadi Yard",
            dateFormatted = "27 Sep, 2026",
            weightKg = 45.0,
            ratePerKgInr = 40.0,
            grossAgreedPaise = 180000L, // ₹1,800
            lifecycle = "CONFIRMED",
            isDemo = true,
            isOfflineSavedOnly = false,
            payments = mutableListOf(
                PaymentEntry(
                    id = "pay_03",
                    transactionId = "tx_iron_03",
                    amountPaise = 100000L, // ₹1,000
                    method = PaymentMethod.CASH,
                    assertedByRole = "COLLECTOR",
                    assertedByName = "Collector Santosh",
                    assertedAt = "2026-09-27T11:30:00Z",
                    state = PaymentState.ASSERTED, // Pending Recycler Acknowledgement
                    isDemo = true,
                    syncState = "SAVED_LOCAL_ONLY"
                )
            )
        )

        val tx4 = TransactionSummary(
            transactionId = "tx_plastic_04",
            lotId = "lot_plastic_04",
            referenceCode = "ST-25D4",
            materialNameEn = "Plastic Bottles (PET)",
            materialNameHi = "प्लास्टिक बोतलें",
            materialCategory = "PET",
            facilityName = "Okhla Clean Recyclers",
            dateFormatted = "25 Sep, 2026",
            weightKg = 8.2,
            ratePerKgInr = 39.02,
            grossAgreedPaise = 32000L, // ₹320
            lifecycle = "DISPUTED",
            isDemo = true,
            isOfflineSavedOnly = false,
            disputeReason = "Yard manager reviewing weight scale discrepancy",
            payments = mutableListOf()
        )

        return listOf(tx1, tx2, tx3, tx4)
    }

    fun getLedgerSummary(monthKey: String = "2026-09", filter: String = "ALL"): CollectorLedgerSummary {
        val currentList = _transactions.value
        val filtered = when (filter) {
            "DUES_REMAINING" -> currentList.filter { it.remainingDuesPaise > 0L }
            "WAITING_SYNC" -> currentList.filter { it.isOfflineSavedOnly || it.payments.any { p -> p.syncState == "SAVED_LOCAL_ONLY" } }
            "DISPUTED" -> currentList.filter { it.disputedPaise > 0L || it.lifecycle == "DISPUTED" || it.disputeReason != null }
            else -> currentList
        }

        return CollectorLedgerSummary(
            monthKey = monthKey,
            monthLabelEn = if (monthKey == "2026-09") "September 2026" else "August 2026",
            monthLabelHi = if (monthKey == "2026-09") "सितंबर २०२६" else "अगस्त २०२६",
            isDemoIsolated = true,
            transactions = filtered
        )
    }

    fun getTransaction(transactionId: String): TransactionSummary? {
        return _transactions.value.find { it.transactionId == transactionId }
    }

    /**
     * Atomically assert a payment (Cash or UPI) without bank gateway execution (R-PAY-01).
     * Enqueues ASSERT_PAYMENT to Room Outbox and records PAYMENT_ASSERTED domain event.
     */
    suspend fun assertPaymentAtomic(
        transactionId: String,
        amountPaise: Long,
        method: PaymentMethod = PaymentMethod.CASH,
        reference: String? = null,
        assertedByRole: String = "COLLECTOR",
        assertedByName: String = "Collector Santosh",
        isDemo: Boolean = true
    ): PaymentEntry {
        require(amountPaise > 0) { "Payment amount must be strictly greater than 0 paise" }
        val tx = _transactions.value.find { it.transactionId == transactionId }
            ?: throw IllegalArgumentException("Transaction $transactionId not found")

        val paymentEntry = PaymentEntry(
            id = UUID.randomUUID().toString(),
            transactionId = transactionId,
            amountPaise = amountPaise,
            method = method,
            privateReference = reference,
            assertedByRole = assertedByRole,
            assertedByName = assertedByName,
            assertedAt = Instant.now().toString(),
            state = PaymentState.ASSERTED,
            isDemo = isDemo,
            syncState = "SAVED_LOCAL_ONLY"
        )

        // Atomic Outbox & Domain Event Enqueuing
        val payloadMap = mapOf(
            "payment_id" to paymentEntry.id,
            "transaction_id" to transactionId,
            "amount_paise" to amountPaise,
            "method" to method.name,
            "private_reference" to reference,
            "asserted_by_role" to assertedByRole,
            "asserted_by_name" to assertedByName,
            "asserted_at" to paymentEntry.assertedAt,
            "is_demo" to isDemo
        )
        val payloadJson = JSONObject(payloadMap).toString()
        val payloadHash = CanonicalJson.sha256Hex(payloadJson)

        val outboxOp = OutboxOperationEntity(
            operationId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            deviceId = "android_device",
            entityType = "TRANSACTION",
            entityId = transactionId,
            command = "ASSERT_PAYMENT",
            expectedVersion = 0,
            payloadJson = payloadJson,
            payloadSha256 = payloadHash,
            state = "QUEUED",
            createdAt = System.currentTimeMillis()
        )
        outboxDao?.enqueue(outboxOp)

        val domainEvent = DomainEventEntity(
            eventId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            entityType = "TRANSACTION",
            entityId = transactionId,
            eventType = "PAYMENT_ASSERTED",
            payloadJson = payloadJson,
            prevHash = "0".repeat(64),
            currentHash = payloadHash,
            createdAt = System.currentTimeMillis()
        )
        domainEventDao?.insertEvent(domainEvent)

        // Update in-memory state
        tx.payments.add(paymentEntry)
        _transactions.value = _transactions.value.map { if (it.transactionId == transactionId) tx else it }

        return paymentEntry
    }

    /**
     * Counterparty acknowledgement of payment assertion (R-PAY-01).
     */
    suspend fun acknowledgePaymentAtomic(
        transactionId: String,
        paymentId: String,
        ackByUserId: String = "usr_suresh_01",
        ackByName: String = "Suresh Kumar (Recycler)"
    ): PaymentEntry {
        val tx = _transactions.value.find { it.transactionId == transactionId }
            ?: throw IllegalArgumentException("Transaction $transactionId not found")
        val payment = tx.payments.find { it.id == paymentId }
            ?: throw IllegalArgumentException("Payment $paymentId not found")

        payment.state = PaymentState.ACKNOWLEDGED
        payment.counterpartyAckBy = ackByUserId
        payment.ackAt = Instant.now().toString()

        val payloadMap = mapOf(
            "transaction_id" to transactionId,
            "payment_id" to paymentId,
            "ack_by_user_id" to ackByUserId,
            "ack_by_name" to ackByName,
            "ack_at" to payment.ackAt
        )
        val payloadJson = JSONObject(payloadMap).toString()
        val payloadHash = CanonicalJson.sha256Hex(payloadJson)

        val outboxOp = OutboxOperationEntity(
            operationId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            deviceId = "android_device",
            entityType = "TRANSACTION",
            entityId = transactionId,
            command = "ACKNOWLEDGE_PAYMENT",
            expectedVersion = 0,
            payloadJson = payloadJson,
            payloadSha256 = payloadHash,
            state = "QUEUED",
            createdAt = System.currentTimeMillis()
        )
        outboxDao?.enqueue(outboxOp)

        val domainEvent = DomainEventEntity(
            eventId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            entityType = "TRANSACTION",
            entityId = transactionId,
            eventType = "PAYMENT_ACKNOWLEDGED",
            payloadJson = payloadJson,
            prevHash = "0".repeat(64),
            currentHash = payloadHash,
            createdAt = System.currentTimeMillis()
        )
        domainEventDao?.insertEvent(domainEvent)

        _transactions.value = _transactions.value.map { if (it.transactionId == transactionId) tx else it }
        return payment
    }

    /**
     * Record dispute on a payment assertion without fact overwriting (R-PAY-01).
     */
    suspend fun disputePaymentAtomic(
        transactionId: String,
        paymentId: String,
        reason: String
    ): PaymentEntry {
        require(reason.isNotBlank()) { "Dispute reason must not be blank" }
        val tx = _transactions.value.find { it.transactionId == transactionId }
            ?: throw IllegalArgumentException("Transaction $transactionId not found")
        val payment = tx.payments.find { it.id == paymentId }
            ?: throw IllegalArgumentException("Payment $paymentId not found")

        payment.state = PaymentState.DISPUTED
        payment.reason = reason

        val payloadMap = mapOf(
            "transaction_id" to transactionId,
            "payment_id" to paymentId,
            "reason" to reason,
            "disputed_at" to Instant.now().toString()
        )
        val payloadJson = JSONObject(payloadMap).toString()
        val payloadHash = CanonicalJson.sha256Hex(payloadJson)

        val outboxOp = OutboxOperationEntity(
            operationId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            deviceId = "android_device",
            entityType = "TRANSACTION",
            entityId = transactionId,
            command = "DISPUTE_PAYMENT",
            expectedVersion = 0,
            payloadJson = payloadJson,
            payloadSha256 = payloadHash,
            state = "QUEUED",
            createdAt = System.currentTimeMillis()
        )
        outboxDao?.enqueue(outboxOp)

        val domainEvent = DomainEventEntity(
            eventId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            entityType = "TRANSACTION",
            entityId = transactionId,
            eventType = "PAYMENT_DISPUTED",
            payloadJson = payloadJson,
            prevHash = "0".repeat(64),
            currentHash = payloadHash,
            createdAt = System.currentTimeMillis()
        )
        domainEventDao?.insertEvent(domainEvent)

        _transactions.value = _transactions.value.map { if (it.transactionId == transactionId) tx else it }
        return payment
    }

    /**
     * Append-only payment reversal linking original without deletion (R-PAY-02).
     */
    suspend fun reversePaymentAtomic(
        transactionId: String,
        paymentId: String,
        reason: String
    ): PaymentEntry {
        require(reason.isNotBlank()) { "Reversal reason must not be blank" }
        val tx = _transactions.value.find { it.transactionId == transactionId }
            ?: throw IllegalArgumentException("Transaction $transactionId not found")
        val original = tx.payments.find { it.id == paymentId }
            ?: throw IllegalArgumentException("Payment $paymentId not found")

        original.state = PaymentState.REVERSED
        original.reason = reason

        val reversalEntry = PaymentEntry(
            id = UUID.randomUUID().toString(),
            transactionId = transactionId,
            amountPaise = -original.amountPaise,
            method = original.method,
            privateReference = original.privateReference,
            assertedByRole = "SYSTEM_REVERSAL",
            assertedByName = "System Tare Correction",
            assertedAt = Instant.now().toString(),
            state = PaymentState.REVERSED,
            reversalOf = paymentId,
            reason = reason,
            isDemo = original.isDemo,
            syncState = "SAVED_LOCAL_ONLY"
        )

        val payloadMap = mapOf(
            "reversal_id" to reversalEntry.id,
            "original_payment_id" to paymentId,
            "transaction_id" to transactionId,
            "amount_paise" to reversalEntry.amountPaise,
            "reason" to reason
        )
        val payloadJson = JSONObject(payloadMap).toString()
        val payloadHash = CanonicalJson.sha256Hex(payloadJson)

        val outboxOp = OutboxOperationEntity(
            operationId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            deviceId = "android_device",
            entityType = "TRANSACTION",
            entityId = transactionId,
            command = "REVERSE_PAYMENT",
            expectedVersion = 0,
            payloadJson = payloadJson,
            payloadSha256 = payloadHash,
            state = "QUEUED",
            createdAt = System.currentTimeMillis()
        )
        outboxDao?.enqueue(outboxOp)

        val domainEvent = DomainEventEntity(
            eventId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            entityType = "TRANSACTION",
            entityId = transactionId,
            eventType = "PAYMENT_REVERSED",
            payloadJson = payloadJson,
            prevHash = "0".repeat(64),
            currentHash = payloadHash,
            createdAt = System.currentTimeMillis()
        )
        domainEventDao?.insertEvent(domainEvent)

        tx.payments.add(reversalEntry)
        _transactions.value = _transactions.value.map { if (it.transactionId == transactionId) tx else it }
        return reversalEntry
    }

    /**
     * Strict closure invariant (R-PAY-02 / AT-036):
     * Transaction can only close if remaining dues == 0 and zero active disputes.
     */
    suspend fun closeTransactionAtomic(transactionId: String): TransactionSummary {
        val tx = _transactions.value.find { it.transactionId == transactionId }
            ?: throw IllegalArgumentException("Transaction $transactionId not found")

        check(tx.remainingDuesPaise == 0L) {
            "Cannot close transaction with pending dues: ₹${tx.remainingDuesInr} remaining"
        }
        check(tx.disputedPaise == 0L && tx.disputeReason == null) {
            "Cannot close transaction with unresolved disputes"
        }

        tx.lifecycle = "CLOSED"

        val payloadMap = mapOf(
            "transaction_id" to transactionId,
            "closed_at" to Instant.now().toString()
        )
        val payloadJson = JSONObject(payloadMap).toString()
        val payloadHash = CanonicalJson.sha256Hex(payloadJson)

        val outboxOp = OutboxOperationEntity(
            operationId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            deviceId = "android_device",
            entityType = "TRANSACTION",
            entityId = transactionId,
            command = "CLOSE_TRANSACTION",
            expectedVersion = 0,
            payloadJson = payloadJson,
            payloadSha256 = payloadHash,
            state = "QUEUED",
            createdAt = System.currentTimeMillis()
        )
        outboxDao?.enqueue(outboxOp)

        val domainEvent = DomainEventEntity(
            eventId = UUID.randomUUID().toString(),
            accountId = "col_demo_santosh",
            entityType = "TRANSACTION",
            entityId = transactionId,
            eventType = "TRANSACTION_CLOSED",
            payloadJson = payloadJson,
            prevHash = "0".repeat(64),
            currentHash = payloadHash,
            createdAt = System.currentTimeMillis()
        )
        domainEventDao?.insertEvent(domainEvent)

        _transactions.value = _transactions.value.map { if (it.transactionId == transactionId) tx else it }
        return tx
    }
}
