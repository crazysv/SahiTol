package com.sahitol.collector.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.sahitol.collector.data.local.entity.PaymentEntryEntity

@Dao
interface PaymentEntryDao {
    @Insert(onConflict = OnConflictStrategy.ABORT)
    suspend fun insert(entry: PaymentEntryEntity)

    @Update
    suspend fun update(entry: PaymentEntryEntity)

    @Query("SELECT * FROM payment_entries WHERE accountId = :accountId ORDER BY createdAt ASC")
    suspend fun getForAccount(accountId: String): List<PaymentEntryEntity>
}
