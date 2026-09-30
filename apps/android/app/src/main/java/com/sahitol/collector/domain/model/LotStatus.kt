package com.sahitol.collector.domain.model

enum class LotStatus {
    DRAFT,
    STAGED,
    PENDING_CONFIRMATION,
    CONFIRMED,
    DISPUTED,
    CLOSED
}

enum class SyncStatus {
    PENDING_SYNC,
    SYNCING,
    SYNCED,
    FAILED
}
