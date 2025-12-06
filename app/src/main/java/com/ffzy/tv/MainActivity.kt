package com.ffzy.tv

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.tv.material3.ExperimentalTvMaterial3Api
import com.ffzy.tv.ui.DetailScreen
import com.ffzy.tv.ui.HomeScreen
import com.ffzy.tv.ui.MovieListViewModel
import com.ffzy.tv.ui.SearchDialog
import com.ffzy.tv.data.VodItem

@OptIn(ExperimentalTvMaterial3Api::class)
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            FFZYTVApp()
        }
    }
}

@OptIn(ExperimentalTvMaterial3Api::class)
@Composable
fun FFZYTVApp() {
    val navController = rememberNavController()
    var showSearch by remember { mutableStateOf(false) }

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            val viewModel: MovieListViewModel = viewModel()
            val movies by viewModel.movies.collectAsState()
            val categories by viewModel.categories.collectAsState()
            val loading by viewModel.loading.collectAsState()

            HomeScreen(
                categories = categories,
                movies = movies,
                loading = loading,
                onCategorySelect = { category ->
                    viewModel.loadMovies(typeId = category.id)
                },
                onSearch = { _ ->
                    showSearch = true
                },
                onMovieClick = { movie ->
                    CurrentMovieHolder.current = movie
                    navController.navigate("detail/${movie.id}")
                }
            )

            if (showSearch) {
                SearchDialog(
                    onDismiss = { showSearch = false },
                    onSearch = { keyword ->
                        if (keyword.isNotBlank()) {
                            viewModel.loadMovies(keyword = keyword)
                        }
                    }
                )
            }
        }
        composable("detail/{id}") {
            val movie = CurrentMovieHolder.current
            if (movie != null) {
                DetailScreen(movie = movie, onBack = { navController.popBackStack() })
            }
        }
    }
}

object CurrentMovieHolder {
    var current: VodItem? = null
}
