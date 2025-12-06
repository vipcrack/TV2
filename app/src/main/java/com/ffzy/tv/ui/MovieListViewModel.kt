package com.ffzy.tv.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ffzy.tv.data.FFZYRepository
import com.ffzy.tv.data.TypeItem
import com.ffzy.tv.data.VodItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MovieListViewModel : ViewModel() {
    private val _movies = MutableStateFlow<List<VodItem>>(emptyList())
    val movies: StateFlow<List<VodItem>> = _movies

    private val _categories = MutableStateFlow<List<TypeItem>>(emptyList())
    val categories: StateFlow<List<TypeItem>> = _categories

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading

    init {
        loadCategories()
        loadMovies()
    }

    private fun loadCategories() {
        viewModelScope.launch {
            try {
                val response = FFZYRepository.apiService.getCategories()
                if (response.isSuccessful && response.body()?.code == 1) {
                    val list = listOf(TypeItem("0", "全部")) + (response.body()?.types ?: emptyList())
                    _categories.value = list
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun loadMovies(typeId: String? = null, keyword: String? = null) {
        viewModelScope.launch {
            _loading.value = true
            try {
                val response = FFZYRepository.apiService.getLatestMovies(
                    page = 1,
                    typeId = if (typeId == "0") null else typeId,
                    keyword = keyword
                )
                if (response.isSuccessful && response.body()?.code == 1) {
                    _movies.value = response.body()?.list ?: emptyList()
                }
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                _loading.value = false
            }
        }
    }
}
