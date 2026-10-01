package com.sahitol.collector

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.view.WindowInsetsControllerCompat
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.sahitol.collector.ui.collector.CollectorNavHost
import com.sahitol.collector.ui.theme.SahiTolTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Android 15 draws edge-to-edge by default. Our Compose top bars reserve
        // the status-bar inset, while this keeps the icons readable on their
        // light surface.
        WindowInsetsControllerCompat(window, window.decorView).apply {
            isAppearanceLightStatusBars = true
            isAppearanceLightNavigationBars = true
        }

        val app = application as SahiTolApp

        setContent {
            SahiTolTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    CollectorNavHost(
                        sessionManager = app.sessionManager,
                        lotRepository = app.lotRepository,
                        classifier = app.classifier
                    )
                }
            }
        }
    }
}

