package com.ffzy.tv

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.ffzy.tv.ui.MainScreen
import com.ffzy.tv.ui.PlayerScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyApp()
        }
    }

    fun performSearch(query: String) {
        // TODO: 实现搜索跳转
    }
}

@Composable
fun MyApp() {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            MainScreen(
                onMovieClick = { vod ->
                    navController.navigate("play/${'$'}{vod.id}")
                },
                onSearchRequested = {
                    val intent = Intent(it, VoiceSearchActivity::class.java)
                    it.startActivity(intent)
                }
            )
        }
        composable("play/{vodId}") { backStackEntry ->
            val vodId = backStackEntry.arguments?.getString("vodId") ?: ""
            PlayerScreen(videoUri = "https://example.com/video.mp4")
        }
    }
}
