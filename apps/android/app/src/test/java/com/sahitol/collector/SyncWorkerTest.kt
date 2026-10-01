package com.sahitol.collector

import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.data.sync.*
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.util.UUID

class SyncWorkerTest {

    @Test
    fun testSyncBatchRequestSerialization() {
        val op = SyncOperationPayload(
            operationId = "op_123",
            entityType = "LOT",
            entityId = "lot_456",
            command = "CREATE_LOT",
            expectedVersion = 0,
            payloadJson = "{\"material_code\":\"MAT-CAB-01\",\"estimated_weight_g\":2500}",
            dependsOn = listOf("op_prereq"),
            mediaIds = listOf("/data/photo.jpg")
        )

        val batch = SyncBatchRequest(
            deviceId = "dev_pixel7a",
            operations = listOf(op)
        )

        val jsonStr = batch.toJson()
        val json = JSONObject(jsonStr)

        assertEquals("dev_pixel7a", json.getString("device_id"))
        val ops = json.getJSONArray("operations")
        assertEquals(1, ops.length())

        val firstOp = ops.getJSONObject(0)
        assertEquals("op_123", firstOp.getString("operation_id"))
        assertEquals("LOT", firstOp.getString("entity_type"))
        assertEquals("CREATE_LOT", firstOp.getString("command"))
        assertEquals(2500, firstOp.getJSONObject("payload").getInt("estimated_weight_g"))
        assertEquals("op_prereq", firstOp.getJSONArray("depends_on").getString(0))
    }

    @Test
    fun testSyncBatchResponseDeserializationAllOutcomes() {
        val serverJson = """
        {
            "device_id": "dev_pixel7a",
            "applied_count": 2,
            "results": [
                {
                    "operation_id": "op_1",
                    "outcome": "APPLIED",
                    "entity_id": "lot_1",
                    "server_version": 1,
                    "result": {"status": "LISTED"}
                },
                {
                    "operation_id": "op_2",
                    "outcome": "RETRY",
                    "entity_id": "lot_2",
                    "error": {"code": "TRANSIENT_LOCK"},
                    "retry_after_seconds": 15
                },
                {
                    "operation_id": "op_3",
                    "outcome": "AUTH_REQUIRED",
                    "entity_id": "lot_3",
                    "error": {"code": "TOKEN_EXPIRED"}
                },
                {
                    "operation_id": "op_4",
                    "outcome": "CONFLICT",
                    "entity_id": "lot_4",
                    "error": {"code": "CONCURRENT_TERMS_UPDATE"}
                },
                {
                    "operation_id": "op_5",
                    "outcome": "REJECTED",
                    "entity_id": "lot_5",
                    "error": {"code": "INVALID_WEIGHT_NEGATIVE"}
                }
            ]
        }
        """.trimIndent()

        val response = SyncBatchResponse.fromJson(serverJson)
        assertEquals("dev_pixel7a", response.deviceId)
        assertEquals(2, response.appliedCount)
        assertEquals(5, response.results.size)

        val res1 = response.results[0]
        assertEquals("op_1", res1.operationId)
        assertEquals("APPLIED", res1.outcome)
        assertEquals(1L, res1.serverVersion)

        val res2 = response.results[1]
        assertEquals("op_2", res2.operationId)
        assertEquals("RETRY", res2.outcome)
        assertEquals(15, res2.retryAfterSeconds)

        val res3 = response.results[2]
        assertEquals("AUTH_REQUIRED", res3.outcome)

        val res4 = response.results[3]
        assertEquals("CONFLICT", res4.outcome)

        val res5 = response.results[4]
        assertEquals("REJECTED", res5.outcome)
    }

    @Test
    fun testSyncBatchResponseDeserializesHostedApiEnvelope() {
        val response = SyncBatchResponse.fromJson(
            """{"data":{"results":[{"operation_id":"op-1","outcome":"APPLIED","entity_id":"lot-1","server_version":2,"result":{"status":"DRAFT"}}]},"meta":{"request_id":"req-1"}}"""
        )

        assertEquals(1, response.results.size)
        assertEquals("APPLIED", response.results.single().outcome)
        assertEquals(2L, response.results.single().serverVersion)
    }

    @Test
    fun testDeltaChangesResponseDeserialization() {
        val deltaJson = """
        {
            "data": {
                "changes": [
                    {
                        "entity_type": "LOT",
                        "entity_id": "lot_999",
                        "version": 3,
                        "operation": "UPSERT",
                        "data": {
                            "material_code": "MAT-PCB-01",
                            "status": "CONFIRMED",
                            "estimated_weight_g": 5000
                        }
                    },
                    {
                        "entity_type": "LOT",
                        "entity_id": "lot_void",
                        "version": 4,
                        "operation": "DELETE",
                        "data": {}
                    }
                ]
            },
            "meta": {
                "next_cursor": "cursor_opaque_12345",
                "has_more": false
            }
        }
        """.trimIndent()

        val delta = DeltaChangesResponse.fromJson(deltaJson)
        assertEquals("cursor_opaque_12345", delta.nextCursor)
        assertFalse(delta.hasMore)
        assertEquals(2, delta.changes.size)

        val c1 = delta.changes[0]
        assertEquals("LOT", c1.entityType)
        assertEquals("lot_999", c1.entityId)
        assertEquals("UPSERT", c1.operation)
        assertEquals(3L, c1.version)
        assertTrue(c1.dataJson.contains("MAT-PCB-01"))

        val c2 = delta.changes[1]
        assertEquals("lot_void", c2.entityId)
        assertEquals("DELETE", c2.operation)
    }

    @Test
    fun testExponentialBackoffCalculation() {
        // Attempt 0: ~2000ms + jitter
        val backoff0 = SyncEngine.calculateBackoffMs(0, null)
        assertTrue("Attempt 0 backoff should be >= 2000ms", backoff0 >= 2000L)
        assertTrue("Attempt 0 backoff should be < 4000ms", backoff0 < 4000L)

        // Attempt 2: base * 4 = 8000ms + jitter
        val backoff2 = SyncEngine.calculateBackoffMs(2, null)
        assertTrue("Attempt 2 backoff should be >= 8000ms", backoff2 >= 8000L)
        assertTrue("Attempt 2 backoff should be < 11000ms", backoff2 < 11000L)

        // Explicit retry_after_seconds override: 30s -> 30000ms + jitter
        val backoffExplicit = SyncEngine.calculateBackoffMs(0, 30)
        assertTrue("Explicit 30s backoff should be >= 30000ms", backoffExplicit >= 30000L)
        assertTrue("Explicit 30s backoff should be < 32000ms", backoffExplicit < 32000L)
    }
}
