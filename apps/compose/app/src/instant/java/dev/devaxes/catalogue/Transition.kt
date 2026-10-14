package dev.devaxes.catalogue
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect

@Composable
fun navProgress(
    target: Float,
    reduced: Boolean,
    finished: (Float) -> Unit,
): Pair<Float, Float> {
    LaunchedEffect(target) { finished(target) }
    return target to target
}
