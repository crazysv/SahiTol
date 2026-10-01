package com.sahitol.collector

import android.app.Application
import androidx.room.Room
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import com.sahitol.collector.data.local.SahiTolDatabase
import com.sahitol.collector.data.repository.LotRepository
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.domain.classifier.LiteRtClassifier

/**
 * SahiTol Collector Android Application.
 * Configured with offline Room database, SessionManager, LotRepository, and LiteRT on-device classifier.
 */
class SahiTolApp : Application() {

    lateinit var database: SahiTolDatabase
        private set

    lateinit var lotRepository: LotRepository
        private set

    lateinit var priceRepository: com.sahitol.collector.data.repository.PriceRepository
        private set

    lateinit var facilityRepository: com.sahitol.collector.data.repository.FacilityRepository
        private set

    lateinit var handoverRepository: com.sahitol.collector.data.repository.HandoverRepository
        private set

    lateinit var paymentRepository: com.sahitol.collector.data.repository.PaymentRepository
        private set

    lateinit var sessionManager: SessionManager
        private set

    lateinit var classifier: LiteRtClassifier
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this
        database = Room.databaseBuilder(
            applicationContext,
            SahiTolDatabase::class.java,
            "sahitol.db"
        ).addMigrations(MIGRATION_3_4).build()

        lotRepository = LotRepository(database)
        priceRepository = com.sahitol.collector.data.repository.PriceRepository(database, applicationContext)
        facilityRepository = com.sahitol.collector.data.repository.FacilityRepository(database)
        handoverRepository = com.sahitol.collector.data.repository.HandoverRepository(database)
        paymentRepository = com.sahitol.collector.data.repository.PaymentRepository(database)
        sessionManager = SessionManager(applicationContext)
        classifier = LiteRtClassifier(applicationContext)
    }


    override fun onTerminate() {
        super.onTerminate()
        if (::classifier.isInitialized) {
            classifier.close()
        }
    }

    companion object {
        private val MIGRATION_3_4 = object : Migration(3, 4) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("""CREATE TABLE IF NOT EXISTS payment_entries (
                    paymentId TEXT NOT NULL PRIMARY KEY, accountId TEXT NOT NULL,
                    transactionId TEXT NOT NULL, amountPaise INTEGER NOT NULL,
                    method TEXT NOT NULL, privateReference TEXT, assertedByRole TEXT NOT NULL,
                    assertedByName TEXT NOT NULL, assertedAt TEXT NOT NULL, state TEXT NOT NULL,
                    counterpartyAckBy TEXT, ackAt TEXT, reversalOf TEXT, reason TEXT,
                    isDemo INTEGER NOT NULL, syncState TEXT NOT NULL, createdAt INTEGER NOT NULL,
                    updatedAt INTEGER NOT NULL)""")
                db.execSQL("CREATE INDEX IF NOT EXISTS index_payment_entries_accountId ON payment_entries (accountId)")
                db.execSQL("CREATE INDEX IF NOT EXISTS index_payment_entries_transactionId ON payment_entries (transactionId)")
            }
        }
        lateinit var instance: SahiTolApp
            private set
    }
}
