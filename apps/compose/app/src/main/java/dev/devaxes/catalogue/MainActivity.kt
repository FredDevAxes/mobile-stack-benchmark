package dev.devaxes.catalogue

import android.graphics.BitmapFactory
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicText
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.semantics.*
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.*
import org.json.JSONArray

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val array = JSONArray(assets.open("products.json").bufferedReader().use { it.readText() })
        val products =
            (0 until array.length()).map { index ->
                val p = array.getJSONObject(index)
                Product(
                    p.getString("id"),
                    p.getString("name"),
                    p.getString("category"),
                    p.getInt("priceCents"),
                    p.getString("description"),
                    p.getString("imageKey"),
                )
            }
        val preferences = getSharedPreferences("catalogue", MODE_PRIVATE)
        setContent {
            var favorites by remember { mutableStateOf(preferences.getStringSet("favorites", emptySet())!!.toSet()) }
            var draft by remember { mutableStateOf("") }
            var query by remember { mutableStateOf("") }
            var only by remember { mutableStateOf(false) }
            var selected by remember { mutableStateOf<Product?>(null) }
            var source by remember { mutableStateOf(Rect.Zero) }
            var target by remember { mutableFloatStateOf(0f) }
            var busy by remember { mutableStateOf(false) }
            var queued by remember { mutableStateOf(false) }
            var closing by remember { mutableStateOf(false) }
            var error by remember { mutableStateOf("") }
            var origin by remember { mutableStateOf(Offset.Zero) }
            val positions = remember { mutableMapOf<String, Rect>() }
            val listState = rememberLazyListState()
            val density = LocalDensity.current
            val reduced = Settings.Global.getFloat(contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f
            val (progress, time) =
                navProgress(target, reduced) { value ->
                    busy = false
                    if (value == 0f && closing) {
                        selected = null
                        closing = false
                    }
                    if (value == 1f && queued) {
                        queued = false
                        busy = true
                        closing = true
                        target = 0f
                    }
                }
            val close: () -> Unit = {
                if (busy) {
                    if (!closing) queued = true
                } else {
                    busy = true
                    closing = true
                    target = 0f
                }
            }
            BackHandler(selected != null) { close() }
            val toggle: (String) -> Unit = { id ->
                if (!busy) {
                    favorites = if (id in favorites) favorites - id else favorites + id
                    if (!preferences.edit().putStringSet("favorites", favorites).commit()) error = "Could not save favorites"
                }
            }
            val data = filtered(products, query, only, favorites)
            Box(Modifier.fillMaxSize().background(Color.White).windowInsetsPadding(WindowInsets.safeDrawing)) {
                BoxWithConstraints(Modifier.fillMaxSize().onGloballyPositioned { origin = it.boundsInRoot().topLeft }) {
                    val width = maxWidth
                    Column(Modifier.fillMaxSize().semantics { if (selected != null) hideFromAccessibility() }) {
                        Box(Modifier.fillMaxWidth().height(52.dp).padding(horizontal = 16.dp), contentAlignment = Alignment.CenterStart) {
                            Label("Trail catalogue", 20, true)
                        }
                        Row(Modifier.height(44.dp).padding(horizontal = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                            BasicTextField(
                                draft,
                                { draft = it },
                                Modifier
                                    .weight(
                                        1f,
                                    ).fillMaxHeight()
                                    .border(1.dp, Color.Gray, RoundedCornerShape(8.dp))
                                    .padding(10.dp)
                                    .semantics {
                                        contentDescription =
                                            "Search products"
                                    },
                                textStyle = TextStyle(fontSize = 16.sp),
                                singleLine = true,
                            )
                            Action("Search") { if (selected == null) query = draft }
                        }
                        Row(
                            Modifier.height(40.dp).fillMaxWidth().padding(horizontal = 16.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            BasicText(
                                "${if (only) "☑" else "☐"} Favorites only",
                                Modifier
                                    .semantics {
                                        role = Role.Checkbox
                                        stateDescription =
                                            if (only) "Checked" else "Unchecked"
                                    }.clickable { if (selected == null) only = !only },
                            )
                            Action("Clear filters") {
                                if (selected == null) {
                                    draft = ""
                                    query = ""
                                    only = false
                                }
                            }
                        }
                        if (error.isNotEmpty()) Label(error, 14)
                        if (data.isEmpty()) {
                            Box(
                                Modifier.fillMaxSize(),
                                contentAlignment = Alignment.Center,
                            ) { Label("No products found", 16) }
                        }
                        LazyColumn(state = listState) {
                            items(data, key = { it.id }) { item ->
                                Column(Modifier.padding(start = 16.dp, end = 16.dp, bottom = 16.dp)) {
                                    Box(
                                        Modifier
                                            .fillMaxWidth()
                                            .height(180.dp)
                                            .onGloballyPositioned {
                                                positions[item.id] =
                                                    it.boundsInRoot().translate(-origin)
                                            }.semantics {
                                                contentDescription = "Open ${item.id}"
                                                role =
                                                    Role.Button
                                            }.clickable {
                                                if (!busy &&
                                                    selected == null
                                                ) {
                                                    source = positions[item.id] ?: Rect.Zero
                                                    selected = item
                                                    busy = true
                                                    target =
                                                        1f
                                                }
                                            },
                                    ) { Photo(item, 16f, Modifier.fillMaxSize().alpha(if (selected?.id == item.id) 0f else 1f)) }
                                    Row(Modifier.height(72.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                                        Column(Modifier.weight(1f)) {
                                            Label(item.name, 18)
                                            Label("${item.category} · ${item.price}", 14)
                                        }
                                        Action(if (item.id in favorites) "★" else "☆", "Favorite ${item.id}") { toggle(item.id) }
                                    }
                                }
                            }
                        }
                    }
                    selected?.let { item ->
                        val exists = data.any { it.id == item.id }
                        val start =
                            with(density) {
                                Rect(
                                    source.left / density.density,
                                    source.top / density.density,
                                    source.right / density.density,
                                    source.bottom / density.density,
                                )
                            }

                        fun mix(
                            a: Float,
                            b: Float,
                        ) = a + (b - a) * progress
                        Box(Modifier.fillMaxSize().background(Color.White.copy(alpha = progress)).clickable(enabled = busy) {})
                        val x = if (exists) mix(start.left, 0f) else 0f
                        val y = if (exists) mix(start.top, 52f) else 52f
                        val w = if (exists) mix(start.width, width.value) else width.value
                        val h = if (exists) mix(start.height, 280f) else 280f
                        Photo(
                            item,
                            if (exists) 16f * (1 - progress) else 0f,
                            Modifier.offset(x.dp, y.dp).size(w.dp, h.dp).alpha(if (exists) 1f else progress),
                        )
                        Column(Modifier.fillMaxWidth().alpha(((time - 0.35f) / 0.65f).coerceIn(0f, 1f))) {
                            Box(Modifier.height(52.dp)) { Action("‹ Back", "Back", close) }
                            Spacer(Modifier.height(280.dp))
                            Column(Modifier.padding(16.dp)) {
                                Label(item.name, 24)
                                Label("${item.category} · ${item.price}", 14)
                                Spacer(Modifier.height(16.dp))
                                Label(item.description, 16)
                                Spacer(Modifier.height(16.dp))
                                Action(
                                    if (item.id in
                                        favorites
                                    ) {
                                        "Remove favorite"
                                    } else {
                                        "Add favorite"
                                    },
                                    "Favorite ${item.id}",
                                ) { toggle(item.id) }
                            }
                        }
                    }
                }
            }
        }
    }

    @Composable private fun Photo(
        p: Product,
        radius: Float,
        modifier: Modifier,
    ) {
        val bitmap = remember(p.imageKey) { assets.open("images/${p.imageKey}.png").use { BitmapFactory.decodeStream(it).asImageBitmap() } }
        Image(bitmap, null, modifier.clip(RoundedCornerShape(radius.dp)), contentScale = ContentScale.Crop)
    }
}

@Composable private fun Label(
    text: String,
    size: Int,
    bold: Boolean = false,
) {
    BasicText(
        text,
        style = TextStyle(fontSize = size.sp, color = Color(0xff17271f), fontWeight = if (bold) FontWeight.SemiBold else FontWeight.Normal),
    )
}

@Composable private fun Action(
    text: String,
    name: String = text,
    action: () -> Unit,
) {
    BasicText(
        text,
        Modifier
            .semantics {
                contentDescription = name
                role = Role.Button
            }.clickable(onClick = action)
            .padding(12.dp),
        style = TextStyle(fontSize = 16.sp, color = Color(0xff235a45)),
    )
}
