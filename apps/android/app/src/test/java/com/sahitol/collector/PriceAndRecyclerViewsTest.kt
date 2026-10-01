package com.sahitol.collector

import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.data.repository.FacilityRepository
import com.sahitol.collector.data.repository.NewPriceObservation
import com.sahitol.collector.data.repository.PriceRepository
import com.sahitol.collector.data.repository.offerTotalInr
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class PriceAndRecyclerViewsTest {

    private class FakeOutboxDao : OutboxDao {
        val enqueuedOps = mutableListOf<OutboxOperationEntity>()

        override suspend fun requeueLegacyCollectorProfileFailures(accountId: String): Int = 0

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
    private lateinit var priceRepository: PriceRepository
    private lateinit var facilityRepository: FacilityRepository

    @Before
    fun setUp() {
        fakeOutboxDao = FakeOutboxDao()
        fakeDomainEventDao = FakeDomainEventDao()

        priceRepository = PriceRepository(outboxDao = fakeOutboxDao, domainEventDao = fakeDomainEventDao)
        facilityRepository = FacilityRepository(outboxDao = fakeOutboxDao, domainEventDao = fakeDomainEventDao)
    }

    @Test
    fun getBenchmarks_allAndFilteredCategories() {
        val all = priceRepository.getBenchmarks()
        assertTrue(all.isNotEmpty())
        assertTrue(all.any { it.category == "CABLE" })
        assertTrue(all.any { it.category == "PCB" })

        val cableOnly = priceRepository.getBenchmarks("CABLE")
        assertTrue(cableOnly.all { it.category == "CABLE" })
        assertTrue(cableOnly.any { it.materialNameEn.contains("Copper") })
    }

    @Test
    fun calculateValuation_integerPaiseAndDeductionMath() {
        // 2500 grams (2.5 kg) of Copper Wire at ~₹745/kg
        val valuation = priceRepository.calculateValuation(
            materialId = "MAT-CAB-01",
            weightG = 2500,
            condition = "GOOD"
        )

        assertEquals(2.5, valuation.weightKg, 0.001)
        assertTrue(valuation.lowInr > 0)
        assertTrue(valuation.highInr >= valuation.lowInr)
        assertTrue(valuation.medianPaise > 0)
        assertEquals(valuation.lowPaise / 100, valuation.lowInr)
        assertEquals(valuation.highPaise / 100, valuation.highInr)
        assertEquals("HIGH", valuation.confidenceTier)
    }

    @Test
    fun rateOfferTotal_usesServerWeightBasisWithoutInventingFixedTotal() {
        assertEquals(4275.0, offerTotalInr("RATE_PER_KG", 30000, 0, 14250), 0.001)
        assertEquals(1250.0, offerTotalInr("FIXED_TOTAL", 0, 125000, 0), 0.001)
    }

    @Test
    fun recordObservationAtomic_insertsOutboxAndDomainEvent() = runBlocking {
        val obs = NewPriceObservation(
            materialId = "MAT-CAB-01",
            observedRatePaise = 74500,
            unit = "kg",
            location = "Delhi Central Mandi",
            sourceDescription = "Local Kabadiwala Shop",
            accountId = "col_test_santosh"
        )

        val outboxOp = priceRepository.recordObservationAtomic(obs)

        assertEquals("col_test_santosh", outboxOp.accountId)
        assertEquals("PRICE_OBSERVATION", outboxOp.entityType)
        assertEquals("CREATE_PRICE_OBSERVATION", outboxOp.command)
        assertEquals("QUEUED", outboxOp.state)
        assertEquals(64, outboxOp.payloadSha256.length) // valid 64-hex SHA-256

        assertEquals(1, fakeOutboxDao.enqueuedOps.size)
        assertEquals(outboxOp.operationId, fakeOutboxDao.enqueuedOps[0].operationId)

        assertEquals(1, fakeDomainEventDao.events.size)
        assertEquals(outboxOp.payloadSha256, fakeDomainEventDao.events[0].currentHash)
        assertEquals("PRICE_OBSERVATION_RECORDED", fakeDomainEventDao.events[0].eventType)
    }

    @Test
    fun facilityRepository_cachedDirectoryIsReferenceOnly() {
        val facilities = facilityRepository.getFacilities()
        assertTrue(facilities.size >= 2)
        assertTrue(facilities.any { it.nameEn.contains("Verma") })

        val areaFiltered = facilityRepository.getFacilities("Dadar")
        assertTrue(areaFiltered.any { it.address.contains("Dadar") })

        // Cached entries are browse-only. The repository exposes no method that
        // turns their non-UUID reference IDs into a queued trade operation.
        assertFalse(facilities.first().facilityId.matches(Regex("^[0-9a-fA-F]{8}-")))
        assertTrue(fakeOutboxDao.enqueuedOps.isEmpty())
    }
}
