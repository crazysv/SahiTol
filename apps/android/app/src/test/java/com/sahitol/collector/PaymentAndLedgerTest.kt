package com.sahitol.collector

import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.data.repository.PaymentRepository
import com.sahitol.collector.domain.payment.PaymentMethod
import com.sahitol.collector.domain.payment.PaymentState
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class PaymentAndLedgerTest {

    private lateinit var fakeOutboxDao: FakeOutboxDao
    private lateinit var fakeDomainEventDao: FakeDomainEventDao
    private lateinit var paymentRepository: PaymentRepository

    private class FakeOutboxDao : OutboxDao {
        val inserted = mutableListOf<OutboxOperationEntity>()

        override suspend fun enqueue(operation: OutboxOperationEntity) {
            inserted.add(operation)
        }

        override suspend fun getPendingOperations(accountId: String, batchSize: Int): List<OutboxOperationEntity> =
            inserted.filter { it.accountId == accountId && it.state in listOf("QUEUED", "RETRY_WAIT") }.take(batchSize)

        override suspend fun getOperationsForAccount(accountId: String): List<OutboxOperationEntity> =
            inserted.filter { it.accountId == accountId }

        override suspend fun getUnsyncedCount(accountId: String): Int =
            inserted.count { it.accountId == accountId && it.state != "ACKNOWLEDGED" }

        override suspend fun getOperationById(operationId: String): OutboxOperationEntity? =
            inserted.find { it.operationId == operationId }

        override suspend fun update(operation: OutboxOperationEntity) {}
        override suspend fun updateState(operationId: String, newState: String, lastErrorCode: String?) {}
        override suspend fun markAcknowledged(operationId: String) {}
        override suspend fun pruneAcknowledged(accountId: String) {}
    }

    private class FakeDomainEventDao : DomainEventDao {
        val events = mutableListOf<DomainEventEntity>()

        override suspend fun insertEvent(event: DomainEventEntity) {
            events.add(event)
        }

        override suspend fun getEventsForAccount(accountId: String): List<DomainEventEntity> =
            events.filter { it.accountId == accountId }

        override suspend fun getEventsForEntity(entityType: String, entityId: String): List<DomainEventEntity> =
            events.filter { it.entityType == entityType && it.entityId == entityId }

        override suspend fun getLatestEventForEntity(entityId: String): DomainEventEntity? =
            events.findLast { it.entityId == entityId }
    }

    @Before
    fun setUp() {
        fakeOutboxDao = FakeOutboxDao()
        fakeDomainEventDao = FakeDomainEventDao()
        paymentRepository = PaymentRepository(
            database = null,
            outboxDao = fakeOutboxDao,
            domainEventDao = fakeDomainEventDao
        )
    }

    @Test
    fun test_cashPaymentAssertionAndAcknowledgement_R_PAY_01_AT_035() = runBlocking {
        // R-PAY-01 / AT-035: Record cash without bank account/gateway; optional UPI reference;
        // counterparty acknowledgement; both sides see actor, time, and acknowledgement
        val tx = paymentRepository.getTransaction("tx_cable_01")
        assertNotNull(tx)
        assertEquals("Mixed Cable & Copper", tx!!.materialNameEn)
        assertEquals(450.0, tx.grossAgreedInr, 0.01)

        val initialRemainingDues = tx.remainingDuesPaise

        // 1. Collector asserts new cash payment of ₹150 (15,000 paise)
        val payment = paymentRepository.assertPaymentAtomic(
            transactionId = tx.transactionId,
            amountPaise = 15000L,
            method = PaymentMethod.CASH,
            reference = "Handover cash note #55",
            assertedByRole = "COLLECTOR",
            assertedByName = "Collector Santosh",
            isDemo = true
        )

        assertNotNull(payment.id)
        assertEquals(PaymentState.ASSERTED, payment.state)
        assertEquals(15000L, payment.amountPaise)
        assertEquals("COLLECTOR", payment.assertedByRole)
        assertEquals("Collector Santosh", payment.assertedByName)
        assertEquals("SAVED_LOCAL_ONLY", payment.syncState)

        // Verify outbox queued ASSERT_PAYMENT and domain event emitted
        assertEquals(1, fakeOutboxDao.inserted.size)
        assertEquals("ASSERT_PAYMENT", fakeOutboxDao.inserted[0].command)
        assertEquals(1, fakeDomainEventDao.events.size)
        assertEquals("PAYMENT_ASSERTED", fakeDomainEventDao.events[0].eventType)

        // Remaining dues should now reflect asserted payment (450 - 300 - 150 = 0)
        val updatedTx = paymentRepository.getTransaction("tx_cable_01")!!
        assertEquals(0L, updatedTx.remainingDuesPaise)
        assertEquals(15000L, updatedTx.assertedPendingPaise)

        // 2. Recycler counterparty acknowledges payment
        val ackPayment = paymentRepository.acknowledgePaymentAtomic(
            transactionId = tx.transactionId,
            paymentId = payment.id,
            ackByUserId = "usr_recycler_suresh",
            ackByName = "Suresh Kumar (Recycler)"
        )

        assertEquals(PaymentState.ACKNOWLEDGED, ackPayment.state)
        assertEquals("usr_recycler_suresh", ackPayment.counterpartyAckBy)
        assertNotNull(ackPayment.ackAt)

        // Verify outbox queued ACKNOWLEDGE_PAYMENT
        assertEquals(2, fakeOutboxDao.inserted.size)
        assertEquals("ACKNOWLEDGE_PAYMENT", fakeOutboxDao.inserted[1].command)

        // Transaction now has 0 remaining dues and 450 acknowledged paid
        val finalTx = paymentRepository.getTransaction("tx_cable_01")!!
        assertEquals(45000L, finalTx.acknowledgedPaidPaise)
        assertEquals(0L, finalTx.assertedPendingPaise)
        assertEquals(0L, finalTx.remainingDuesPaise)
        assertTrue(finalTx.isSettled)
    }

    @Test
    fun test_upiPaymentAssertionWithReference_R_PAY_01() = runBlocking {
        // Optional UPI reference recording
        val tx = paymentRepository.getTransaction("tx_paper_02")!!
        val payment = paymentRepository.assertPaymentAtomic(
            transactionId = tx.transactionId,
            amountPaise = 28000L, // ₹280
            method = PaymentMethod.UPI,
            reference = "UPI-UTR-992384729102",
            assertedByRole = "COLLECTOR",
            assertedByName = "Collector Santosh"
        )

        assertEquals(PaymentMethod.UPI, payment.method)
        assertEquals("UPI-UTR-992384729102", payment.privateReference)
        assertEquals(PaymentState.ASSERTED, payment.state)
    }

    @Test
    fun test_partialPaymentsAndReversalsAndStrictClosure_R_PAY_02_AT_036() = runBlocking {
        // R-PAY-02 / AT-036: Two partial receipts sum once without double counting,
        // reversal links original record without deletion, transaction cannot close with pending dues
        val tx = paymentRepository.getTransaction("tx_iron_03")!!
        assertEquals(1800.0, tx.grossAgreedInr, 0.01) // ₹1,800 total
        assertEquals(1000.0, tx.assertedPendingInr, 0.01) // ₹1,000 pending
        assertEquals(800.0, tx.remainingDuesInr, 0.01) // ₹800 dues

        // Attempting to close transaction with pending dues MUST fail
        try {
            paymentRepository.closeTransactionAtomic(tx.transactionId)
            fail("Expected IllegalStateException when closing transaction with pending dues")
        } catch (e: IllegalStateException) {
            assertTrue(e.message!!.contains("Cannot close transaction with pending dues"))
        }

        // Reversal of mistaken payment: append-only reversal linking original record
        val pendingPayment = tx.payments.first { it.id == "pay_03" }
        val reversal = paymentRepository.reversePaymentAtomic(
            transactionId = tx.transactionId,
            paymentId = pendingPayment.id,
            reason = "Correction: Scale tare weight adjustment applied"
        )

        assertEquals(PaymentState.REVERSED, reversal.state)
        assertEquals(pendingPayment.id, reversal.reversalOf)
        assertEquals(-100000L, reversal.amountPaise)
        assertEquals("Correction: Scale tare weight adjustment applied", reversal.reason)

        // Original record is marked REVERSED, not deleted
        val originalAfter = tx.payments.first { it.id == "pay_03" }
        assertEquals(PaymentState.REVERSED, originalAfter.state)
        assertEquals(2, tx.payments.size) // Both original and reversal exist in history

        // Outbox contains REVERSE_PAYMENT
        assertTrue(fakeOutboxDao.inserted.any { it.command == "REVERSE_PAYMENT" })
    }

    @Test
    fun test_collectorEarningsAndMonthlyReconciliation_R_PAY_03_AT_037() = runBlocking {
        // R-PAY-03 / AT-037: Reconcile gross agreed, acknowledged paid, asserted pending,
        // and remaining dues against transactions; offline view shows freshness; demo partition isolation
        val summary = paymentRepository.getLedgerSummary("2026-09", "ALL")
        assertEquals("September 2026", summary.monthLabelEn)
        assertEquals("सितंबर २०२६", summary.monthLabelHi)
        assertTrue(summary.isDemoIsolated)
        assertEquals(4, summary.transactions.size)

        // Sum of all 4 transactions:
        // tx1: ₹450 gross, ₹300 acknowledged paid, ₹0 asserted pending, ₹150 remaining dues
        // tx2: ₹280 gross, ₹0 acknowledged paid, ₹0 asserted pending, ₹280 remaining dues (offline saved)
        // tx3: ₹1,800 gross, ₹0 acknowledged paid, ₹1,000 asserted pending, ₹800 remaining dues
        // tx4: ₹320 gross, ₹0 acknowledged paid, ₹0 asserted pending, ₹320 remaining dues (disputed)
        // Total Gross: 450 + 280 + 1800 + 320 = ₹2,850 (285,000 paise)
        val expectedTotalAgreedPaise = 45000L + 28000L + 180000L + 32000L
        assertEquals(expectedTotalAgreedPaise, summary.totalAgreedPaise)
        assertEquals(2850.0, summary.totalAgreedInr, 0.01)

        assertEquals(30000L, summary.acknowledgedPaidPaise)
        assertEquals(300.0, summary.acknowledgedPaidInr, 0.01)

        assertEquals(100000L, summary.assertedPendingPaise)
        assertEquals(1000.0, summary.assertedPendingInr, 0.01)

        val expectedRemainingDues = 15000L + 28000L + 80000L + 32000L // 155,000 paise = ₹1,550
        assertEquals(expectedRemainingDues, summary.remainingDuesPaise)
        assertEquals(1550.0, summary.remainingDuesInr, 0.01)

        // Saved on device count: tx2 is offline saved, tx3 has offline saved payment
        assertEquals(2, summary.savedOnDevicePendingSlips)

        // Disputed count: tx4 is disputed
        assertEquals(1, summary.disputedCount)

        // Filter: DUES_REMAINING
        val duesOnlySummary = paymentRepository.getLedgerSummary("2026-09", "DUES_REMAINING")
        assertEquals(4, duesOnlySummary.transactions.size) // All 4 currently have remaining dues

        // Filter: DISPUTED
        val disputedSummary = paymentRepository.getLedgerSummary("2026-09", "DISPUTED")
        assertEquals(1, disputedSummary.transactions.size)
        assertEquals("tx_plastic_04", disputedSummary.transactions[0].transactionId)
    }

    @Test
    fun test_weightDiscrepancyAndDisputePreservation_R_HAND_05_AT_033() = runBlocking {
        // R-HAND-05 / AT-033: Weight/grade/price disagreement retains original facts,
        // records reason, does not overwrite physical history
        val tx = paymentRepository.getTransaction("tx_plastic_04")!!
        assertEquals("DISPUTED", tx.lifecycle)
        assertEquals("Yard manager reviewing weight scale discrepancy", tx.disputeReason)
        assertEquals(8.2, tx.weightKg, 0.01)
        assertEquals(320.0, tx.grossAgreedInr, 0.01)

        // Assert payment on another transaction and dispute it
        val payment = paymentRepository.assertPaymentAtomic(
            transactionId = "tx_cable_01",
            amountPaise = 5000L,
            method = PaymentMethod.CASH,
            assertedByRole = "COLLECTOR"
        )
        val disputedPayment = paymentRepository.disputePaymentAtomic(
            transactionId = "tx_cable_01",
            paymentId = payment.id,
            reason = "Collector asserts ₹150 was paid, yard records only ₹50"
        )

        assertEquals(PaymentState.DISPUTED, disputedPayment.state)
        assertEquals("Collector asserts ₹150 was paid, yard records only ₹50", disputedPayment.reason)
        assertTrue(fakeOutboxDao.inserted.any { it.command == "DISPUTE_PAYMENT" })
    }
}
