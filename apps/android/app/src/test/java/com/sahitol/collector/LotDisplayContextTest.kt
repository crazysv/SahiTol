package com.sahitol.collector

import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.ui.collector.lotDisplayContext
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class LotDisplayContextTest {
    @Test
    fun syncedPcbLot_isShownAsTheActualPersistedLot() {
        val context = lotDisplayContext(
            LotEntity(
                lotId = "lot-pcb",
                materialCode = "PCB",
                estimatedWeightG = 14250,
                syncStatus = "SYNCED"
            )
        )

        assertEquals("MAT-PCB-01", context.canonicalMaterialId)
        assertEquals("Printed circuit boards", context.materialLabel)
        assertEquals("14.25 kg", context.weightLabel)
        assertTrue(context.detailLabel.contains("Synced"))
        assertTrue(context.isConcreteLot)
    }

    @Test
    fun absentSavedLot_isNotPresentedAsAnActionableSampleLot() {
        val context = lotDisplayContext(null)

        assertEquals("Price preview", context.materialLabel)
        assertFalse(context.isConcreteLot)
        assertTrue(context.detailLabel.contains("Select a saved lot"))
    }
}
