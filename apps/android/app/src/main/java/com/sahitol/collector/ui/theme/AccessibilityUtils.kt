package com.sahitol.collector.ui.theme

import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.sahitol.collector.domain.locale.LocaleFormatter

/**
 * Accessibility standards and TalkBack semantics helpers conforming to R-UX-01 and AT-051:
 * - Minimum 48dp (and 56dp for primary CTA) mobile touch targets.
 * - Meaningful content descriptions on all icons and status indicators (no color-only status).
 * - Screen-reader announcements formatted as: label + value + unit + status.
 */
object AccessibilityUtils {

    val MinimumTouchTarget: Dp = 48.dp
    val PrimaryTouchTarget: Dp = 56.dp

    /**
     * Modifier ensuring interactive element meets Android accessibility touch target guidelines (>= 48dp).
     */
    fun Modifier.accessibleTouchTarget(): Modifier = this.then(
        Modifier.defaultMinSize(minWidth = MinimumTouchTarget, minHeight = MinimumTouchTarget)
    )

    /**
     * Modifier ensuring primary action buttons meet 56dp height standard for field workers with gloves / rough hands.
     */
    fun Modifier.primaryTouchTarget(): Modifier = this.then(
        Modifier.defaultMinSize(minWidth = PrimaryTouchTarget, minHeight = PrimaryTouchTarget)
    )

    /**
     * Semantics description builder for scrap lot cards and ledger items:
     * Label + Value + Unit + Status.
     */
    fun Modifier.scrapLotSemantics(
        label: String,
        value: String,
        unit: String,
        status: String,
        isHeader: Boolean = false
    ): Modifier = this.then(
        Modifier.semantics {
            contentDescription = LocaleFormatter.formatScreenReader(label, value, unit, status)
            if (isHeader) {
                heading()
            }
        }
    )
}
