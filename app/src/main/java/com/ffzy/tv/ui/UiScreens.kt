package com.ffzy.tv.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import androidx.tv.foundation.lazy.list.TvLazyColumn
import androidx.tv.foundation.lazy.list.items
import com.ffzy.tv.data.VodItem

@Composable
fun FocusableCard(
    movie: VodItem,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    var isFocused by remember { mutableStateOf(false) }
    val focusRequester = remember { FocusRequester() }

    Box(
        modifier = modifier
            .focusRequester(focusRequester)
            .focusProperties { left = focusRequester; right = focusRequester }
            .onFocusChanged { isFocused = it.hasFocus }
            .padding(8.dp)
            .width(220.dp)
            .height(320.dp)
            .clickable { onClick() }
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Top
        ) {
            if (!movie.pic.isNullOrBlank()) {
                AsyncImage(
                    model = movie.pic,
                    contentDescription = movie.name,
                    modifier = Modifier
                        .size(200.dp, 280.dp)
                        .padding(bottom = 8.dp),
                    placeholder = Color.LightGray
                )
            }
            Text(
                text = movie.name,
                fontSize = 14.sp,
                fontWeight = if (isFocused) FontWeight.Bold else FontWeight.Normal,
                maxLines = 2,
                lineHeight = 16.sp
            )
        }
    }
}

@Composable
fun MovieGrid(movies: List<VodItem>, onMovieClick: (VodItem) -> Unit) {
    TvLazyColumn(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.Start
    ) {
        items(movies, key = { it.id }) { movie ->
            FocusableCard(movie = movie, onClick = { onMovieClick(movie) })
        }
    }
}
