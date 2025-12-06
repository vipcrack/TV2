package com.ffzy.tv.ui

import android.annotation.SuppressLint
import android.content.res.Configuration
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.media3.ui.PlayerView
import androidx.tv.foundation.lazy.list.TvLazyColumn
import androidx.tv.foundation.lazy.list.TvLazyRow
import androidx.tv.material3.Button
import androidx.tv.material3.ExperimentalTvMaterial3Api
import androidx.tv.material3.FocusableCard
import androidx.tv.material3.OutlinedButton
import androidx.tv.material3.TvMaterialTheme
import com.ffzy.tv.data.TypeItem
import com.ffzy.tv.data.VodItem
import com.ffzy.tv.player.ExoPlayerManager

@OptIn(ExperimentalTvMaterial3Api::class)
@Composable
fun HomeScreen(
    categories: List<TypeItem>,
    movies: List<VodItem>,
    loading: Boolean,
    onCategorySelect: (TypeItem) -> Unit,
    onSearch: (String) -> Unit,
    onMovieClick: (VodItem) -> Unit
) {
    val isLandscape = LocalConfiguration.current.orientation == Configuration.ORIENTATION_LANDSCAPE
    val padding = if (isLandscape) 32.dp else 16.dp

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Category Row
            TvLazyRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                items(categories.size) { index ->
                    val cat = categories[index]
                    OutlinedButton(
                        onClick = { onCategorySelect(cat) },
                        modifier = Modifier
                    ) {
                        Text(cat.name, color = Color.White)
                    }
                }
            }

            // Search Button
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 12.dp, bottom = 12.dp),
                horizontalArrangement = Arrangement.End
            ) {
                Button(onClick = { onSearch("") }) {
                    Text("🔍 搜索", color = Color.Black)
                }
            }

            // Movie List
            if (loading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(color = Color.White)
                }
            } else {
                TvLazyColumn(
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    contentPadding = androidx.compose.foundation.layout.PaddingValues(vertical = 16.dp)
                ) {
                    items(movies.size) { index ->
                        val movie = movies[index]
                        FocusableCard(
                            onClick = { onMovieClick(movie) },
                            modifier = Modifier.padding(horizontal = 8.dp)
                        ) {
                            Column(
                                modifier = Modifier.padding(20.dp),
                                verticalArrangement = Arrangement.Center
                            ) {
                                Text(
                                    text = movie.name,
                                    style = TvMaterialTheme.typography.headlineSmall,
                                    color = Color.White
                                )
                                Text(
                                    text = "${movie.area} · ${movie.type}",
                                    style = TvMaterialTheme.typography.bodyMedium,
                                    color = Color.Gray
                                )
                                if (movie.score != "0.0") {
                                    Text(
                                        text = "豆瓣: ${movie.score}",
                                        style = TvMaterialTheme.typography.bodySmall,
                                        color = Color.Yellow
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@SuppressLint("UnsafeOptInUsageError")
@Composable
fun DetailScreen(movie: VodItem, onBack: () -> Unit) {
    val context = LocalContext.current
    val playerManager = remember { ExoPlayerManager(context) }

    LaunchedEffect(movie) {
        val url = movie.getPlayableUrl()
        if (url != null) {
            playerManager.prepare(url)
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            playerManager.release()
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                PlayerView(ctx).apply {
                    useController = true
                    player = playerManager.player
                    setShowBuffering(PlayerView.SHOW_BUFFERING_WHEN_PLAYING)
                }
            },
            modifier = Modifier.fillMaxSize()
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(32.dp),
            verticalArrangement = Arrangement.Top
        ) {
            Text(
                text = movie.name,
                fontSize = 32.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            Text(
                text = "${movie.area} | ${movie.type} | ${movie.updateTime}",
                fontSize = 16.sp,
                color = Color.LightGray
            )
            if (movie.score != "0.0") {
                Text(text = "豆瓣评分: ${movie.score}", color = Color.Yellow)
            }
        }

        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.BottomEnd) {
            Button(onClick = onBack, modifier = Modifier.padding(24.dp)) {
                Text("返回", color = Color.Black)
            }
        }
    }
}

@Composable
fun SearchDialog(
    onDismiss: () -> Unit,
    onSearch: (String) -> Unit
) {
    var query by remember { mutableStateOf("") }
    val focusRequester = remember { FocusRequester() }

    LaunchedEffect(Unit) {
        focusRequester.requestFocus()
    }

    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(48.dp)
        ) {
            Text("搜索影片", fontSize = 24.sp, color = Color.White, modifier = Modifier.padding(bottom = 16.dp))
            TextField(
                value = query,
                onValueChange = { query = it },
                placeholder = { Text("输入影片名称", color = Color.Gray) },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Text,
                    imeAction = ImeAction.Search
                ),
                keyboardActions = KeyboardActions(
                    onSearch = { onSearch(query); onDismiss() }
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .focusRequester(focusRequester),
                colors = androidx.compose.material3.TextFieldDefaults.colors(
                    focusedIndicatorColor = Color.Transparent,
                    unfocusedIndicatorColor = Color.Transparent,
                    disabledIndicatorColor = Color.Transparent
                )
            )
            Row(modifier = Modifier.padding(top = 24.dp)) {
                Button(onClick = { onSearch(query); onDismiss() }) {
                    Text("搜索", color = Color.Black)
                }
                Button(onClick = onDismiss, modifier = Modifier.padding(start = 12.dp)) {
                    Text("取消", color = Color.Black)
                }
            }
        }
    }
}

@Composable
fun AndroidView(
    factory: (android.content.Context) -> android.view.View,
    modifier: androidx.compose.ui.Modifier = Modifier
) {
    androidx.compose.ui.viewinterop.AndroidView(
        factory = factory,
        modifier = modifier
    )
}
