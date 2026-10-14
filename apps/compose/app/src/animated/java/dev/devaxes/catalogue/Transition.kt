package dev.devaxes.catalogue
import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue

@Composable
fun navProgress(
    target: Float,
    reduced: Boolean,
    finished: (Float) -> Unit,
): Pair<Float, Float> {
    val time by animateFloatAsState(
        target,
        tween(if (reduced) 0 else 400, easing = LinearEasing),
        finishedListener = finished,
        label = "navigation",
    )
    return CubicBezierEasing(0.4f, 0f, 0.2f, 1f).transform(time) to time
}
