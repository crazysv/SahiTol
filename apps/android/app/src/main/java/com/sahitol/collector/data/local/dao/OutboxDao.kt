package com.sahitol.collector.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.sahitol.collector.data.local.entity.OutboxOperationEntity

@Dao
interface OutboxDao {
    @Query("SELECT * FROM outbox_operations WHERE accountId = :accountId AND state IN ('QUEUED', 'RETRY_WAIT') ORDER BY createdAt ASC LIMIT :batchSize")
    suspend fun getPendingOperations(accountId: String, batchSize: Int = 50): List<OutboxOperationEntity>

    @Query("SELECT * FROM outbox_operations WHERE accountId = :accountId ORDER BY createdAt ASC")
    suspend fun getOperationsForAccount(accountId: String): List<OutboxOperationEntity>

    @Query("SELECT COUNT(*) FROM outbox_operations WHERE accountId = :accountId AND state != 'ACKNOWLEDGED'")
    suspend fun getUnsyncedCount(accountId: String): Int

    @Query("SELECT * FROM outbox_operations WHERE operationId = :operationId LIMIT 1")
    suspend fun getOperationById(operationId: String): OutboxOperationEntity?

    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun enqueue(operation: OutboxOperationEntity)

    @Update
    suspend fun update(operation: OutboxOperationEntity)

    @Query("UPDATE outbox_operations SET state = :newState, lastErrorCode = :lastErrorCode WHERE operationId = :operationId")
    suspend fun updateState(operationId: String, newState: String, lastErrorCode: String? = null)

    @Query("UPDATE outbox_operations SET state = 'ACKNOWLEDGED' WHERE operationId = :operationId")
    suspend fun markAcknowledged(operationId: String)

    @Query("DELETE FROM outbox_operations WHERE accountId = :accountId AND state = 'ACKNOWLEDGED'")
    suspend fun pruneAcknowledged(accountId: String)
}
