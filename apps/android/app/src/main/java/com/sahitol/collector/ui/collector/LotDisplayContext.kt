package com.sahitol.collector.ui.collector

import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.repository.LotRepository
import java.util.Locale

/**
 * Presentation-only description of a saved lot.  Screens that can also be opened
 * from the price board receive no LotEntity and must not pretend a sample lot is
 * actionable.
 */
internal data class LotDisplayContext(
    val canonicalMaterialId: String?,
    val materialLabel: String,
    val weightLabel: String,
    val detailLabel: String,
    val isConcreteLot: Boolean
)

internal fun lotDisplayContext(lot: LotEntity?): LotDisplayContext {
    if (lot == null) {
        return LotDisplayContext(
            canonicalMaterialId = null,
            materialLabel = "Price preview",
            weightLabel = "No saved lot selected",
            detailLabel = "Select a saved lot before requesting a recycler offer.",
            isConcreteLot = false
        )
    }

    val materialId = LotRepository.canonicalMaterialId(lot.materialCode)
    val materialLabel = when (materialId) {
        "MAT-PCB-01", "MAT-PCB-02" -> "Printed circuit boards"
        "MAT-CAB-01", "MAT-CAB-02" -> "Copper cable"
        "MAT-BAT-01" -> "Batteries"
        "MAT-CRT-01" -> "CRT glass"
        "MAT-LCD-01" -> "LCD panels"
        "MAT-MOT-01" -> "Motors"
        "MAT-PLA-01" -> "E-waste plastics"
        else -> lot.materialCode
    }
    val weightKg = lot.estimatedWeightG / 1000.0
    val weightLabel = "${if (weightKg % 1.0 == 0.0) weightKg.toLong() else "%.2f".format(Locale.US, weightKg)} kg"
    val syncLabel = if (lot.syncStatus == "SYNCED") "Synced" else "Saved locally"
    return LotDisplayContext(
        canonicalMaterialId = materialId,
        materialLabel = materialLabel,
        weightLabel = weightLabel,
        detailLabel = "$materialLabel · $weightLabel · $syncLabel",
        isConcreteLot = true
    )
}
