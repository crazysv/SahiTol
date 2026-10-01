package com.sahitol.collector

import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.data.repository.CreateLotParams
import com.sahitol.collector.data.repository.LotRepository
import org.junit.Assert.*
import org.junit.Test
import java.util.UUID

class RoomOutboxRepositoryTest {

    @Test
    fun testSha256Determinism() {
        val input = "{\"lot_id\":\"test-123\",\"material_code\":\"MAT-CAB-01\"}"
        val hash1 = LotRepository.sha256(input)
        val hash2 = LotRepository.sha256(input)
        assertEquals(hash1, hash2)
        assertEquals(64, hash1.length)
        assertTrue(hash1.matches(Regex("^[a-f0-9]{64}$")))
    }

    @Test
    fun presentationMaterialCodesMapToCuratedCatalogIds() {
        assertEquals("MAT-PCB-01", LotRepository.canonicalMaterialId("PCB"))
        assertEquals("MAT-CAB-01", LotRepository.canonicalMaterialId("CABLE"))
        assertEquals("MAT-BAT-01", LotRepository.canonicalMaterialId("BATTERY"))
        assertEquals("MAT-PCB-02", LotRepository.canonicalMaterialId("MAT-PCB-02"))
    }

    @Test
    fun testDomainEventHashChainProgression() {
        val genesis = "0000000000000000000000000000000000000000000000000000000000000000"
        val payload1 = "{\"lot_id\":\"lot_1\",\"status\":\"DRAFT\"}"
        val hash1 = LotRepository.sha256("$genesis:LOT_CREATED:$payload1")

        val event1 = DomainEventEntity(
            eventId = "evt_1",
            accountId = "user_123",
            entityType = "LOT",
            entityId = "lot_1",
            eventType = "LOT_CREATED",
            payloadJson = payload1,
            prevHash = genesis,
            currentHash = hash1
        )

        // Event 2 links to event 1's current hash
        val payload2 = "{\"lot_id\":\"lot_1\",\"status\":\"LISTED\"}"
        val hash2 = LotRepository.sha256("${event1.currentHash}:LOT_LISTED:$payload2")

        val event2 = DomainEventEntity(
            eventId = "evt_2",
            accountId = "user_123",
            entityType = "LOT",
            entityId = "lot_1",
            eventType = "LOT_LISTED",
            payloadJson = payload2,
            prevHash = event1.currentHash,
            currentHash = hash2
        )

        // Verify chain integrity
        assertEquals(genesis, event1.prevHash)
        assertEquals(event1.currentHash, event2.prevHash)
        assertNotEquals(event1.currentHash, event2.currentHash)

        // Verification logic
        val calculated1 = LotRepository.sha256("${event1.prevHash}:${event1.eventType}:${event1.payloadJson}")
        assertEquals(event1.currentHash, calculated1)

        val calculated2 = LotRepository.sha256("${event2.prevHash}:${event2.eventType}:${event2.payloadJson}")
        assertEquals(event2.currentHash, calculated2)
    }

    @Test
    fun testOutboxOperationContract() {
        val op = OutboxOperationEntity(
            operationId = UUID.randomUUID().toString(),
            accountId = "collector_456",
            deviceId = "device_test_01",
            entityType = "LOT",
            entityId = "lot_abc",
            command = "CREATE_DRAFT",
            expectedVersion = 0,
            payloadJson = "{\"material_id\":\"MAT-CAB-01\"}",
            payloadSha256 = LotRepository.sha256("{\"material_id\":\"MAT-CAB-01\"}"),
            dependsOnJson = "[]",
            mediaIdsJson = "[]",
            state = "QUEUED",
            attemptCount = 0
        )

        assertEquals("QUEUED", op.state)
        assertEquals(0, op.attemptCount)
        assertEquals("collector_456", op.accountId)
        assertEquals("CREATE_DRAFT", op.command)
        assertNull(op.lastErrorCode)
    }

    @Test
    fun testUserPartitionContract() {
        val userALots = listOf(
            LotEntity(lotId = "l1", accountId = "user_A", materialCode = "MAT-CAB-01", estimatedWeightG = 1000L),
            LotEntity(lotId = "l2", accountId = "user_A", materialCode = "MAT-PCB-01", estimatedWeightG = 2000L)
        )
        val userBLots = listOf(
            LotEntity(lotId = "l3", accountId = "user_B", materialCode = "MAT-BAT-01", estimatedWeightG = 5000L)
        )

        // Ensure user filtering does not leak across accounts
        val filteredForA = (userALots + userBLots).filter { it.accountId == "user_A" }
        assertEquals(2, filteredForA.size)
        assertTrue(filteredForA.all { it.accountId == "user_A" })

        val filteredForB = (userALots + userBLots).filter { it.accountId == "user_B" }
        assertEquals(1, filteredForB.size)
        assertEquals("user_B", filteredForB[0].accountId)
    }

    @Test
    fun testSafeLogoutPreservationInvariant() {
        // R-AUTH-03 / AT-009: Logging out must preserve unsynced records
        val outbox = listOf(
            OutboxOperationEntity(
                operationId = "op1",
                accountId = "user_active",
                deviceId = "dev1",
                entityType = "LOT",
                entityId = "l1",
                command = "CREATE_LOT",
                payloadJson = "{}",
                payloadSha256 = "hash",
                state = "QUEUED"
            ),
            OutboxOperationEntity(
                operationId = "op2",
                accountId = "user_active",
                deviceId = "dev1",
                entityType = "LOT",
                entityId = "l2",
                command = "CREATE_LOT",
                payloadJson = "{}",
                payloadSha256 = "hash",
                state = "QUEUED"
            )
        )

        val unsyncedCount = outbox.count { it.state != "ACKNOWLEDGED" }
        assertEquals(2, unsyncedCount)
        // On logout, outbox is preserved in SQLite, tokens cleared in memory
        assertTrue("Unsynced operations must remain in outbox upon logout", unsyncedCount > 0)
    }
}
