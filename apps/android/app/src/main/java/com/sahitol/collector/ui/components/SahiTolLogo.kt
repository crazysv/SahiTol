package com.sahitol.collector.ui.components

import androidx.compose.foundation.Image
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import com.sahitol.collector.R

/** The three approved brand treatments, kept separate so each context stays intentional. */
@Composable
fun SahiTolMark(modifier: Modifier = Modifier) {
    Image(
        painter = painterResource(R.drawable.sahitol_logo_mark),
        contentDescription = "SahiTol",
        contentScale = ContentScale.Fit,
        modifier = modifier
    )
}

@Composable
fun SahiTolFullLogo(modifier: Modifier = Modifier) {
    Image(
        painter = painterResource(R.drawable.sahitol_logo_full),
        contentDescription = "SahiTol logo",
        contentScale = ContentScale.Fit,
        modifier = modifier
    )
}

@Composable
fun SahiTolWordmark(modifier: Modifier = Modifier) {
    Image(
        painter = painterResource(R.drawable.sahitol_logo_wordmark),
        contentDescription = "SahiTol wordmark",
        contentScale = ContentScale.Fit,
        modifier = modifier
    )
}
