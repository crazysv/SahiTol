package com.sahitol.collector.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.sahitol.collector.data.local.entity.LotEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface LotDao {
    @Query("SELECT * FROM lots WHERE accountId = :accountId ORDER BY createdAt DESC")
    fun getLotsForAccountFlow(accountId: String): Flow<List<LotEntity>>

    @Query("SELECT * FROM lots WHERE accountId = :accountId ORDER BY createdAt DESC")
    suspend fun getLotsForAccount(accountId: String): List<LotEntity>

    @Query("SELECT * FROM lots WHERE lotId = :lotId LIMIT 1")
    suspend fun getLotById(lotId: String): LotEntity?

    @Query("SELECT * FROM lots WHERE accountId = :accountId AND syncStatus = 'SAVED_LOCAL_ONLY' ORDER BY createdAt ASC")
    suspend fun getUnsyncedLotsForAccount(accountId: String): List<LotEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertLot(lot: LotEntity)

    @Update
    suspend fun updateLot(lot: LotEntity)

    @Query("UPDATE lots SET syncStatus = :newSyncStatus, serverVersion = :serverVersion, updatedAt = :updatedAt WHERE lotId = :lotId")
    suspend fun updateSyncStatus(lotId: String, newSyncStatus: String, serverVersion: Long, updatedAt: Long = System.currentTimeMillis())

    @Query("DELETE FROM lots WHERE lotId = :lotId")
    suspend fun deleteLotById(lotId: String)
}
