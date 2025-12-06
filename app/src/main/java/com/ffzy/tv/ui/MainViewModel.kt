package com.ffzy.tv.ui

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ffzy.tv.data.ApiResponse
import com.ffzy.tv.data.RetrofitClient
import com.ffzy.tv.data.VodItem
import kotlinx.coroutines.launch

class MainViewModel : ViewModel() {
    var movies by mutableStateOf<List<VodItem>>(emptyList())
        private set
    var isLoading by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set

    fun loadMovies(type: String? = null, keyword: String? = null, page: Int = 1) {
        viewModelScope.launch {
            isLoading = true
            error = null
            try {
                val response = RetrofitClient.apiService.getVodList(
                    type = type,
                    keyword = keyword,
                    page = page
                )
                if (response.isSuccessful) {
                    movies = response.body()?.list ?: emptyList()
                } else {
                    error = "加载失败: ${'$'}{response.code()}"
                }
            } catch (e: Exception) {
                error = e.message ?: "未知错误"
            } finally {
                isLoading = false
            }
        }
    }
}
