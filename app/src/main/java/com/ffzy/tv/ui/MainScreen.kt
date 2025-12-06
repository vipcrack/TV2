package com.ffzy.tv.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.ffzy.tv.util.HistoryManager

@Composable
fun MainScreen(
    onMovieClick: (vod: com.ffzy.tv.data.VodItem) -> Unit,
    onSearchRequested: () -> Unit
) {
    val viewModel: MainViewModel = viewModel()
    val context = LocalContext.current
    val historyManager = remember { HistoryManager(context) }
    var movies by remember { mutableStateOf<List<com.ffzy.tv.data.VodItem>>(emptyList()) }

    LaunchedEffect(Unit) {
        viewModel.loadMovies()
        historyManager.history.collect { list ->
            movies = list
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        if (movies.isNotEmpty()) {
            MovieGrid(movies = movies) { vod ->
                historyManager.addToHistory(vod)
                onMovieClick(vod)
            }
        } else {
            Column(
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text("无历史记录")
                Button(onClick = { onSearchRequested() }) {
                    Text("开始语音搜索")
                }
            }
        }
    }
}
