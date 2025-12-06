package com.ffzy.tv.util

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.ffzy.tv.data.VodItem
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "history")

class HistoryManager(private val context: Context) {
    private val HISTORY_KEY = stringPreferencesKey("history_json")
    private val gson = Gson()
    private val historyType = object : TypeToken<List<VodItem>>() {}.type

    val history: Flow<List<VodItem>> = context.dataStore.data.map { prefs ->
        val json = prefs[HISTORY_KEY] ?: "[]"
        try {
            gson.fromJson(json, historyType) as List<VodItem>
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun addToHistory(item: VodItem) {
        val current = history.firstOrNull() ?: emptyList()
        val updated = listOf(item) + current.filter { it.id != item.id }.take(19)
        context.dataStore.edit { prefs ->
            prefs[HISTORY_KEY] = gson.toJson(updated)
        }
    }
}
