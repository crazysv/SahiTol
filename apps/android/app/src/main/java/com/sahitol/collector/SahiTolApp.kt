package com.sahitol.collector

import android.app.Application
import androidx.room.Room
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
        ).fallbackToDestructiveMigration().build()

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
        lateinit var instance: SahiTolApp
            private set
    }
}
