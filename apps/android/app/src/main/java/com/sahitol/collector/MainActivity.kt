package com.sahitol.collector

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.view.WindowInsetsControllerCompat
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.padding
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import com.sahitol.collector.ui.collector.CollectorNavHost
import com.sahitol.collector.ui.components.SahiTolFullLogo
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
                var showSplash by remember { mutableStateOf(true) }
                LaunchedEffect(Unit) {
                    delay(1200)
                    showSplash = false
                }

                if (showSplash) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(Color(0xFFFDF8F0)),
                        contentAlignment = Alignment.Center
                    ) {
                        SahiTolFullLogo(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(40.dp)
                        )
                    }
                } else {
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
}

