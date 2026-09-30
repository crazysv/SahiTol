package com.sahitol.collector

import com.sahitol.collector.domain.canonical.CanonicalJson
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.io.File

class CanonicalJsonTest {

    @Test
    fun testHandoverFixtureParityWithFrozenCanonicalHash() {
        // Read docs/planning/handover_fixture.json
        val fixtureFile = File("../../../docs/planning/handover_fixture.json")
        val content = if (fixtureFile.exists()) {
            fixtureFile.readText(Charsets.UTF_8)
        } else {
            // Fallback for execution from different working directories
            File("d:/SahiTol/docs/planning/handover_fixture.json").readText(Charsets.UTF_8)
        }

        val fixtureJson = JSONObject(content)
        val proposalPayload = fixtureJson.getJSONObject("proposal_payload")
        val expectedCanonicalUtf8 = fixtureJson.getString("canonical_utf8")
        val expectedHash = fixtureJson.getString("proposal_hash")

        val actualCanonicalUtf8 = CanonicalJson.serialize(proposalPayload)
        assertEquals(expectedCanonicalUtf8, actualCanonicalUtf8)

        val actualHash = CanonicalJson.sha256Hex(actualCanonicalUtf8)
        assertEquals("a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f", actualHash)
        assertEquals(expectedHash, actualHash)
    }

    @Test
    fun testAlteredByteInvalidatesDigest() {
        val payload = mapOf(
            "lot_id" to "lot_123",
            "weight_g" to 5000,
            "condition" to "GOOD"
        )
        val canonical1 = CanonicalJson.serialize(payload)
        val hash1 = CanonicalJson.sha256Hex(canonical1)

        val payloadAltered = mapOf(
            "lot_id" to "lot_123",
            "weight_g" to 5001, // 1 gram difference
            "condition" to "GOOD"
        )
        val canonical2 = CanonicalJson.serialize(payloadAltered)
        val hash2 = CanonicalJson.sha256Hex(canonical2)

        assertNotEquals(canonical1, canonical2)
        assertNotEquals(hash1, hash2)
    }

    @Test
    fun testDeterministicKeySorting() {
        val mapUnsorted = mapOf(
            "z" to 1,
            "a" to 2,
            "m" to mapOf("y" to 10, "b" to 20)
        )
        val serialized = CanonicalJson.serialize(mapUnsorted)
        assertEquals("{\"a\":2,\"m\":{\"b\":20,\"y\":10},\"z\":1}", serialized)
    }
}
