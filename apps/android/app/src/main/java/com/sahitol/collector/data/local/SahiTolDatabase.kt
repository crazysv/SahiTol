package com.sahitol.collector.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.LotDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity

@Database(
    entities = [
        LotEntity::class,
        OutboxOperationEntity::class,
        DomainEventEntity::class
    ],
    version = 3,
    exportSchema = false
)
abstract class SahiTolDatabase : RoomDatabase() {
    abstract fun lotDao(): LotDao
    abstract fun outboxDao(): OutboxDao
    abstract fun domainEventDao(): DomainEventDao
}
