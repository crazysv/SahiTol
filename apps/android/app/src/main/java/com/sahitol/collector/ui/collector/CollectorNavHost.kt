package com.sahitol.collector.ui.collector

import android.content.Context
import android.provider.Settings
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.data.repository.CreateLotParams
import com.sahitol.collector.data.repository.LotRepository
import com.sahitol.collector.data.session.CollectorSession
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.data.sync.SyncWorker
import com.sahitol.collector.domain.classifier.LiteRtClassifier
import com.sahitol.collector.ui.diagnostic.S00_DiagnosticScreen
import kotlinx.coroutines.launch
import java.net.URLDecoder
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

sealed class Screen(val route: String) {
    object Welcome : Screen("welcome")
    object Auth : Screen("auth")
    object Home : Screen("home")
    object Camera : Screen("camera")
    object LotEditor : Screen("lot_editor?photoPath={photoPath}") {
        fun createRoute(photoPath: String?): String {
            return if (photoPath != null) {
                val encoded = URLEncoder.encode(photoPath, StandardCharsets.UTF_8.toString())
                "lot_editor?photoPath=$encoded"
            } else {
                "lot_editor?photoPath="
            }
        }
    }
    object SyncCentre : Screen("sync_centre")
    object SettingsScreen : Screen("settings")
    object Diagnostic : Screen("diagnostic")
    object PriceBoard : Screen("price_board")
    object LotValuation : Screen("lot_valuation/{lotId}") {
        fun createRoute(lotId: String) = "lot_valuation/$lotId"
    }
    object RecyclerDirectory : Screen("recycler_directory/{lotId}") {
        fun createRoute(lotId: String) = "recycler_directory/$lotId"
    }
    object RecyclerProfile : Screen("recycler_profile/{facilityId}/{lotId}") {
        fun createRoute(facilityId: String, lotId: String) = "recycler_profile/$facilityId/$lotId"
    }
    object HandoverCapture : Screen("handover_capture/{lotId}") {
        fun createRoute(lotId: String) = "handover_capture/$lotId"
    }
    object DigitalHandoverRecord : Screen("digital_handover_record/{handoverId}") {
        fun createRoute(handoverId: String) = "digital_handover_record/$handoverId"
    }
    object MaterialPassport : Screen("material_passport/{lotId}") {
        fun createRoute(lotId: String) = "material_passport/$lotId"
    }
    object Ledger : Screen("ledger")
    object PaymentSettlement : Screen("payment_settlement/{transactionId}") {
        fun createRoute(transactionId: String) = "payment_settlement/$transactionId"
    }
    object SafetyHub : Screen("safety_hub?cardId={cardId}&materialId={materialId}") {
        fun createRoute(cardId: String? = null, materialId: String? = null): String {
            val c = if (cardId != null) "cardId=$cardId" else "cardId="
            val m = if (materialId != null) "materialId=$materialId" else "materialId="
            return "safety_hub?$c&$m"
        }
    }
}

@Composable
fun CollectorNavHost(
    sessionManager: SessionManager,
    lotRepository: LotRepository,
    classifier: LiteRtClassifier,
    priceRepository: com.sahitol.collector.data.repository.PriceRepository = com.sahitol.collector.SahiTolApp.instance.priceRepository,
    facilityRepository: com.sahitol.collector.data.repository.FacilityRepository = com.sahitol.collector.SahiTolApp.instance.facilityRepository,
    handoverRepository: com.sahitol.collector.data.repository.HandoverRepository = com.sahitol.collector.SahiTolApp.instance.handoverRepository,
    paymentRepository: com.sahitol.collector.data.repository.PaymentRepository = com.sahitol.collector.SahiTolApp.instance.paymentRepository,
    navController: NavHostController = rememberNavController()
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val session by sessionManager.session.collectAsState()

    val startDestination = if (session.isLoggedIn) Screen.Home.route else Screen.Welcome.route

    // Real-time Flow of lots for active account
    val lots by lotRepository.getLotsForAccountFlow(session.accountId)
        .collectAsState(initial = emptyList())

    // Real-time pending operations and unsynced count
    var unsyncedCount by remember { mutableIntStateOf(0) }
    var operations by remember { mutableStateOf<List<OutboxOperationEntity>>(emptyList()) }
    var isSyncing by remember { mutableStateOf(false) }

    LaunchedEffect(session.accountId, lots) {
        unsyncedCount = lotRepository.getUnsyncedCount(session.accountId)
        operations = lotRepository.getPendingOutboxOperations(session.accountId, 100)
    }

    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        // C01: Welcome, Language & Demo Selection
        composable(Screen.Welcome.route) {
            C01_WelcomeScreen(
                currentLanguage = session.language,
                onLanguageSelected = { lang ->
                    sessionManager.setLanguage(lang)
                },
                onStartCollection = {
                    navController.navigate(Screen.Auth.route)
                },
                onStartDemo = {
                    sessionManager.loginDemo()
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Welcome.route) { inclusive = true }
                    }
                },
                onOpenDiagnostic = {
                    navController.navigate(Screen.Diagnostic.route)
                }
            )
        }

        // C02: Phone / PIN Authentication & Offline Registration
        composable(Screen.Auth.route) {
            C02_AuthScreen(
                isOffline = false,
                onAuthSuccess = { phone, alias ->
                    sessionManager.login(phone, alias)
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Welcome.route) { inclusive = true }
                    }
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        // C03: Collector Dashboard & Work Table
        composable(Screen.Home.route) {
            C03_HomeScreen(
                collectorAlias = session.alias,
                isDemo = session.isDemo,
                unsyncedCount = unsyncedCount,
                lots = lots,
                onAddLot = {
                    navController.navigate(Screen.Camera.route)
                },
                onNavigateSync = {
                    navController.navigate(Screen.SyncCentre.route)
                },
                onNavigateSettings = {
                    navController.navigate(Screen.SettingsScreen.route)
                },
                onNavigatePrices = {
                    navController.navigate(Screen.PriceBoard.route)
                },
                onNavigateDirectory = {
                    navController.navigate(Screen.RecyclerDirectory.createRoute("all_lots"))
                },
                onNavigateLedger = {
                    navController.navigate(Screen.Ledger.route)
                },
                onNavigateSafety = {
                    navController.navigate(Screen.SafetyHub.createRoute())
                },
                onLotClick = { lotId ->
                    navController.navigate(Screen.LotValuation.createRoute(lotId))
                }
            )
        }

        // C04: Photo Capture & Import
        composable(Screen.Camera.route) {
            C04_CameraScreen(
                onPhotoConfirmed = { photoPath ->
                    navController.navigate(Screen.LotEditor.createRoute(photoPath))
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        // C05: Material, Weight & Condition Lot Editor
        composable(
            route = Screen.LotEditor.route,
            arguments = listOf(
                navArgument("photoPath") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val rawPath = backStackEntry.arguments?.getString("photoPath")
            val photoPath = if (!rawPath.isNullOrBlank()) {
                URLDecoder.decode(rawPath, StandardCharsets.UTF_8.toString())
            } else null

            C05_LotEditorScreen(
                initialPhotoPath = photoPath,
                classifier = classifier,
                currentLanguage = session.language,
                currentNumeralPref = session.numeralPreference,
                onSaveLot = { materialCode, weightGrams, condition, finalPhotoPath, isDraft, aiSuggestedCode, aiConfidence, aiModelVersion ->
                    coroutineScope.launch {
                        val deviceId = try {
                            Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
                        } catch (e: Exception) {
                            "device_android_${session.accountId}"
                        }

                        val created = lotRepository.createLotAtomic(
                            CreateLotParams(
                                accountId = session.accountId,
                                deviceId = deviceId ?: "device_android_default",
                                materialCode = materialCode,
                                estimatedWeightG = weightGrams,
                                estimatedLowPaise = null,
                                estimatedMedianPaise = null,
                                estimatedHighPaise = null,
                                localPhotoPath = finalPhotoPath,
                                aiSuggestedCode = aiSuggestedCode,
                                aiConfidence = aiConfidence,
                                aiModelVersion = aiModelVersion
                            )
                        )

                        // Update counts and navigate to valuation
                        unsyncedCount = lotRepository.getUnsyncedCount(session.accountId)
                        navController.navigate(Screen.LotValuation.createRoute(created.lotId)) {
                            popUpTo(Screen.Home.route) { inclusive = false }
                        }
                    }
                },
                onNavigateSafety = { matCode ->
                    navController.navigate(Screen.SafetyHub.createRoute(materialId = matCode))
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        // C14: Sync Centre & Collector Movement Board
        composable(Screen.SyncCentre.route) {
            C14_SyncCentreScreen(
                unsyncedCount = unsyncedCount,
                operations = operations,
                isSyncing = isSyncing,
                onTriggerSync = {
                    isSyncing = true
                    SyncWorker.enqueueManualSync(context, session.accountId)
                    coroutineScope.launch {
                        kotlinx.coroutines.delay(1000)
                        unsyncedCount = lotRepository.getUnsyncedCount(session.accountId)
                        operations = lotRepository.getPendingOutboxOperations(session.accountId, 100)
                        isSyncing = false
                    }
                },
                onSafeLogout = {
                    sessionManager.logoutPreservingData()
                    navController.navigate(Screen.Welcome.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        // C15: Settings, Audio Guidance & Safe Logout
        composable(Screen.SettingsScreen.route) {
            C15_SettingsScreen(
                collectorAlias = session.alias,
                maskedPhone = session.maskedPhone,
                isDemo = session.isDemo,
                currentLanguage = session.language,
                currentNumeralPref = session.numeralPreference,
                unsyncedCount = unsyncedCount,
                onLanguageSelected = { lang ->
                    sessionManager.setLanguage(lang)
                },
                onNumeralPrefSelected = { pref ->
                    sessionManager.setNumeralPreference(pref)
                },
                onNavigateSync = {
                    navController.navigate(Screen.SyncCentre.route)
                },
                onOpenDiagnostic = {
                    navController.navigate(Screen.Diagnostic.route)
                },
                onLogout = {
                    sessionManager.logoutPreservingData()
                    navController.navigate(Screen.Welcome.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        // C06: Price Board & Market Trends
        composable(Screen.PriceBoard.route) {
            C06_PriceBoardScreen(
                priceRepository = priceRepository,
                sessionManager = sessionManager,
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigateSync = {
                    navController.navigate(Screen.SyncCentre.route)
                },
                onNavigateSettings = {
                    navController.navigate(Screen.SettingsScreen.route)
                },
                onNavigateLotValuation = { materialId ->
                    navController.navigate(Screen.LotValuation.createRoute(materialId))
                }
            )
        }

        // C07: Valuation & Active Recycler Offers
        composable(
            route = Screen.LotValuation.route,
            arguments = listOf(
                navArgument("lotId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val lotId = backStackEntry.arguments?.getString("lotId") ?: "default_lot"
            C07_ValuationScreen(
                lotId = lotId,
                priceRepository = priceRepository,
                facilityRepository = facilityRepository,
                sessionManager = sessionManager,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateDirectory = { targetLotId ->
                    navController.navigate(Screen.RecyclerDirectory.createRoute(targetLotId))
                },
                onNavigateHandover = { targetLotId ->
                    navController.navigate(Screen.HandoverCapture.createRoute(targetLotId))
                },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigateSync = {
                    navController.navigate(Screen.SyncCentre.route)
                },
                onNavigateSettings = {
                    navController.navigate(Screen.SettingsScreen.route)
                }
            )
        }

        // C08: Recycler Directory & Map Radar
        composable(
            route = Screen.RecyclerDirectory.route,
            arguments = listOf(
                navArgument("lotId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val lotId = backStackEntry.arguments?.getString("lotId") ?: "default_lot"
            C08_RecyclerDirectoryScreen(
                lotId = lotId,
                facilityRepository = facilityRepository,
                sessionManager = sessionManager,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateFacilityProfile = { facId, targetLotId ->
                    navController.navigate(Screen.RecyclerProfile.createRoute(facId, targetLotId))
                },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigateSync = {
                    navController.navigate(Screen.SyncCentre.route)
                },
                onNavigateSettings = {
                    navController.navigate(Screen.SettingsScreen.route)
                }
            )
        }

        // C09: Recycler Profile & Commercial Offer Terminal
        composable(
            route = Screen.RecyclerProfile.route,
            arguments = listOf(
                navArgument("facilityId") { type = NavType.StringType },
                navArgument("lotId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val facilityId = backStackEntry.arguments?.getString("facilityId") ?: "fac-verma-01"
            val lotId = backStackEntry.arguments?.getString("lotId") ?: "default_lot"
            C09_RecyclerProfileOfferScreen(
                facilityId = facilityId,
                lotId = lotId,
                facilityRepository = facilityRepository,
                sessionManager = sessionManager,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigateSync = {
                    navController.navigate(Screen.SyncCentre.route)
                },
                onNavigateSettings = {
                    navController.navigate(Screen.SettingsScreen.route)
                },
                onNavigateHandover = { lid ->
                    navController.navigate(Screen.HandoverCapture.createRoute(lid))
                }
            )
        }

        // C10: Handover Capture & Scale Reconciliation
        composable(
            route = Screen.HandoverCapture.route,
            arguments = listOf(navArgument("lotId") { type = NavType.StringType })
        ) { backStackEntry ->
            val lotId = backStackEntry.arguments?.getString("lotId") ?: "default_lot"
            C10_HandoverCaptureScreen(
                lotId = lotId,
                handoverRepository = handoverRepository,
                sessionManager = sessionManager,
                onNavigateBack = { navController.popBackStack() },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigatePrices = { navController.navigate(Screen.PriceBoard.route) },
                onNavigateRecord = { hid -> navController.navigate(Screen.DigitalHandoverRecord.createRoute(hid)) },
                onNavigatePassport = { lid -> navController.navigate(Screen.MaterialPassport.createRoute(lid)) },
                onNavigateSettings = { navController.navigate(Screen.SettingsScreen.route) }
            )
        }

        // C11: Digital Handover Record & QR Confirmation
        composable(
            route = Screen.DigitalHandoverRecord.route,
            arguments = listOf(navArgument("handoverId") { type = NavType.StringType })
        ) { backStackEntry ->
            val handoverId = backStackEntry.arguments?.getString("handoverId") ?: "default_handover"
            C11_DigitalHandoverRecordScreen(
                handoverId = handoverId,
                handoverRepository = handoverRepository,
                sessionManager = sessionManager,
                onNavigateBack = { navController.popBackStack() },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigatePrices = { navController.navigate(Screen.PriceBoard.route) },
                onNavigateHandover = { navController.popBackStack() },
                onNavigatePassport = { lid -> navController.navigate(Screen.MaterialPassport.createRoute(lid)) },
                onNavigateSettings = { navController.navigate(Screen.SettingsScreen.route) }
            )
        }

        // C16: Material Passport & Journey Spine
        composable(
            route = Screen.MaterialPassport.route,
            arguments = listOf(navArgument("lotId") { type = NavType.StringType })
        ) { backStackEntry ->
            val lotId = backStackEntry.arguments?.getString("lotId") ?: "default_lot"
            C16_MaterialPassportScreen(
                lotId = lotId,
                handoverRepository = handoverRepository,
                sessionManager = sessionManager,
                onNavigateBack = { navController.popBackStack() },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigatePrices = { navController.navigate(Screen.PriceBoard.route) },
                onNavigateHandover = { navController.navigate(Screen.HandoverCapture.createRoute(lotId)) },
                onNavigateRecord = { hid -> navController.navigate(Screen.DigitalHandoverRecord.createRoute(hid)) },
                onNavigateSettings = { navController.navigate(Screen.SettingsScreen.route) },
                onNavigateSettlement = {
                    navController.navigate(Screen.PaymentSettlement.createRoute("tx_cable_01"))
                }
            )
        }

        // C12: Collector Ledger / Bahi-Khata Screen
        composable(Screen.Ledger.route) {
            C12_LedgerScreen(
                paymentRepository = paymentRepository,
                sessionManager = sessionManager,
                onNavigateBack = { navController.popBackStack() },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigatePrices = { navController.navigate(Screen.PriceBoard.route) },
                onNavigateHandover = { navController.navigate(Screen.MaterialPassport.createRoute("lot_cable_01")) },
                onNavigateTransaction = { txId ->
                    navController.navigate(Screen.PaymentSettlement.createRoute(txId))
                },
                onNavigateSync = { navController.navigate(Screen.SyncCentre.route) },
                onNavigateSettings = { navController.navigate(Screen.SettingsScreen.route) }
            )
        }

        // C13: Payment Settlement / Assertion Screen
        composable(
            route = Screen.PaymentSettlement.route,
            arguments = listOf(navArgument("transactionId") { type = NavType.StringType })
        ) { backStackEntry ->
            val transactionId = backStackEntry.arguments?.getString("transactionId") ?: "tx_cable_01"
            C13_PaymentSettlementScreen(
                transactionId = transactionId,
                paymentRepository = paymentRepository,
                sessionManager = sessionManager,
                onNavigateBack = { navController.popBackStack() },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                onNavigateLedger = { navController.navigate(Screen.Ledger.route) },
                onNavigateSync = { navController.navigate(Screen.SyncCentre.route) },
                onNavigateSettings = { navController.navigate(Screen.SettingsScreen.route) }
            )
        }

        // C17: Contextual Safety Hub & Guides (Stitch 1579fe53bac5)
        composable(
            route = Screen.SafetyHub.route,
            arguments = listOf(
                navArgument("cardId") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                },
                navArgument("materialId") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val cardId = backStackEntry.arguments?.getString("cardId")?.ifBlank { null }
            val materialId = backStackEntry.arguments?.getString("materialId")?.ifBlank { null }
            C17_SafetyHubScreen(
                initialCardId = cardId,
                initialMaterialId = materialId,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // S00: Feasibility Diagnostic
        composable(Screen.Diagnostic.route) {
            S00_DiagnosticScreen(
                database = lotRepository.let { (context.applicationContext as com.sahitol.collector.SahiTolApp).database },
                classifier = classifier,
                onStartCollection = {
                    navController.popBackStack()
                }
            )
        }
    }
}
