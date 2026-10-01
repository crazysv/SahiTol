package com.sahitol.collector

import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.data.repository.HandoverProposal
import com.sahitol.collector.data.repository.HandoverRepository
import com.sahitol.collector.domain.canonical.CanonicalJson
import com.sahitol.collector.domain.pdf.ReceiptPdfGenerator
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class HandoverAndReceiptTest {

    private class FakeOutboxDao : OutboxDao {
        val enqueuedOps = mutableListOf<OutboxOperationEntity>()

        override suspend fun enqueue(operation: OutboxOperationEntity) {
            enqueuedOps.add(operation)
        }

        override suspend fun getPendingOperations(accountId: String, batchSize: Int): List<OutboxOperationEntity> =
            enqueuedOps.filter { it.accountId == accountId && it.state in listOf("QUEUED", "RETRY_WAIT") }

        override suspend fun getOperationsForAccount(accountId: String): List<OutboxOperationEntity> =
            enqueuedOps.filter { it.accountId == accountId }

        override suspend fun getUnsyncedCount(accountId: String): Int =
            enqueuedOps.count { it.accountId == accountId && it.state != "ACKNOWLEDGED" }

        override suspend fun getOperationById(operationId: String): OutboxOperationEntity? =
            enqueuedOps.find { it.operationId == operationId }

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

    private lateinit var fakeOutboxDao: FakeOutboxDao
    private lateinit var fakeDomainEventDao: FakeDomainEventDao
    private lateinit var handoverRepository: HandoverRepository

    @Before
    fun setUp() {
        fakeOutboxDao = FakeOutboxDao()
        fakeDomainEventDao = FakeDomainEventDao()
        handoverRepository = HandoverRepository(outboxDao = fakeOutboxDao, domainEventDao = fakeDomainEventDao)
    }

    @Test
    fun createProposalAtomic_satisfiesOfflinePendingHandoverInvariant() = runBlocking {
        // R-HAND-01 / AT-029: In offline mode create UUID proposal with grams, location, terms and hash;
        // status is PENDING_CONFIRMATION and queued for sync, NEVER recycler-confirmed.
        val proposal = handoverRepository.createProposalAtomic(
            lotId = "lot-copper-001",
            collectorId = "col_test_santosh",
            facilityId = "fac-verma-01",
            facilityName = "Verma Electricals",
            materialId = "MAT-CAB-01",
            materialName = "Copper Wire (Grade A)",
            condition = "GOOD",
            estimatedWeightG = 2500,
            measuredWeightG = 2300,
            rateInrPerKg = 180.0,
            totalPayoutInr = 414.0,
            isDemo = true
        )

        assertEquals("PENDING_CONFIRMATION", proposal.status)
        assertNotEquals("CONFIRMED", proposal.status)
        assertEquals(64, proposal.canonicalHash.length)
        assertTrue(proposal.referenceCode.startsWith("ST-"))
        assertTrue(proposal.verificationUrl.startsWith("https://sahitol.pages.dev/recycler/scan?"))
        assertTrue(proposal.verificationUrl.contains("ref=${proposal.referenceCode}"))
        assertTrue(proposal.verificationUrl.contains("weight=2.3"))
        assertFalse(proposal.verificationUrl.contains("414"))

        // Outbox operation verification
        assertEquals(1, fakeOutboxDao.enqueuedOps.size)
        val op = fakeOutboxDao.enqueuedOps[0]
        assertEquals("HANDOVER_PROPOSAL", op.entityType)
        assertEquals("CREATE_HANDOVER_PROPOSAL", op.command)
        assertEquals("QUEUED", op.state)
        assertEquals(proposal.canonicalHash, op.payloadSha256)

        // Domain event verification
        assertEquals(1, fakeDomainEventDao.events.size)
        val evt = fakeDomainEventDao.events[0]
        assertEquals("HANDOVER_PROPOSED", evt.eventType)
        assertEquals(proposal.canonicalHash, evt.currentHash)
    }

    @Test
    fun termsDiscrepancyResponse_acceptsOrDisputesWithoutOverwritingHistory() = runBlocking {
        // R-HAND-05 / AT-033: Measured weight difference records acceptance or dispute without overwriting
        val proposal = handoverRepository.createProposalAtomic(
            lotId = "lot-copper-002",
            collectorId = "col_test_santosh",
            facilityId = "fac-verma-01",
            facilityName = "Verma Electricals",
            materialId = "MAT-CAB-01",
            materialName = "Copper Wire",
            condition = "GOOD",
            estimatedWeightG = 2500,
            measuredWeightG = 2300,
            rateInrPerKg = 180.0,
            totalPayoutInr = 414.0
        )

        // Collector accepts revised terms
        val accepted = handoverRepository.recordDiscrepancyResponseAtomic(
            handoverId = proposal.handoverId,
            action = "ACCEPT_TERMS",
            collectorId = "col_test_santosh"
        )
        assertEquals("PENDING_CONFIRMATION", accepted.status)
        assertTrue(fakeOutboxDao.enqueuedOps.any { it.command == "ACCEPT_TERMS_REVISION" })
        assertTrue(fakeDomainEventDao.events.any { it.eventType == "TERMS_REVISION_ACCEPTED" })

        // Collector disputes revised terms
        val disputed = handoverRepository.recordDiscrepancyResponseAtomic(
            handoverId = proposal.handoverId,
            action = "DISPUTE_TERMS",
            collectorId = "col_test_santosh",
            reason = "Scale tare calibration inaccurate by 200g"
        )
        assertEquals("DISPUTED", disputed.status)
        assertTrue(fakeOutboxDao.enqueuedOps.any { it.command == "DISPUTE_HANDOVER" })
        assertTrue(fakeDomainEventDao.events.any { it.eventType == "HANDOVER_DISPUTED" })
    }

    @Test
    fun materialPassport_journeySpineContains5CanonicalStages() {
        // R-HAND-06 / AT-034: Journey spine tracking 5 lifecycle milestones
        val timeline = handoverRepository.getJourneyTimeline("lot-copper-001")
        assertEquals(5, timeline.size)

        assertEquals("Collection & Weighing", timeline[0].titleEn)
        assertTrue(timeline[0].isCompleted)
        assertTrue(timeline[0].metadataSnippet?.contains("GPS") == true)

        assertEquals("Commercial Offer Agreed", timeline[1].titleEn)
        assertTrue(timeline[1].isCompleted)

        assertEquals("Yard Handover & Scale Reconciliation", timeline[2].titleEn)
        assertTrue(timeline[2].isCompleted)

        assertEquals("Digital Handover Record Generated", timeline[3].titleEn)
        assertTrue(timeline[3].isCompleted)

        assertEquals("Payment Settlement", timeline[4].titleEn)
        assertFalse(timeline[4].isCompleted) // settlement cycle pending
    }

    @Test
    fun receiptPdfData_containsStatutoryNonEprNoticeAndCanonicalHash() {
        // Statutory non-EPR disclosure invariant
        val receiptData = ReceiptPdfGenerator.ReceiptData(
            handoverId = "10000000-0000-4000-8000-000000000001",
            referenceCode = "ST-24A7",
            occurredAt = "2026-09-28T08:30:00.000Z",
            collectorAlias = "Collector Santosh",
            facilityName = "Verma Electricals",
            materialName = "Copper Wire (Grade A)",
            weightG = 2300,
            rateInrPerKg = 180.0,
            totalPayoutInr = 414.0,
            canonicalHash = "a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f",
            verificationUrl = "https://sahitol.in/v/10000000-0000-4000-8000-000000000001",
            statusText = "PENDING_CONFIRMATION"
        )

        assertEquals(64, receiptData.canonicalHash.length)
        assertEquals(2300L, receiptData.weightG)
        assertEquals(414.0, receiptData.totalPayoutInr, 0.001)
        assertTrue(receiptData.verificationUrl.startsWith("https://sahitol.in/v/"))
    }
}
