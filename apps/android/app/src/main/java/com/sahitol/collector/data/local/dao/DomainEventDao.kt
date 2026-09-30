package com.sahitol.collector.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.sahitol.collector.data.local.entity.DomainEventEntity

@Dao
interface DomainEventDao {
    @Query("SELECT * FROM domain_events WHERE accountId = :accountId ORDER BY createdAt ASC")
    suspend fun getEventsForAccount(accountId: String): List<DomainEventEntity>

    @Query("SELECT * FROM domain_events WHERE entityType = :entityType AND entityId = :entityId ORDER BY createdAt ASC")
    suspend fun getEventsForEntity(entityType: String, entityId: String): List<DomainEventEntity>

    @Query("SELECT * FROM domain_events WHERE entityId = :entityId ORDER BY createdAt DESC LIMIT 1")
    suspend fun getLatestEventForEntity(entityId: String): DomainEventEntity?

    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insertEvent(event: DomainEventEntity)
}
