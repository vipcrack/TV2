package com.ffzy.tv.util

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "favorites")

class FavoriteManager(private val context: Context) {
    fun isFavorite(vodId: String): Flow<Boolean> {
        return context.dataStore.data.map { prefs ->
            prefs[booleanPreferencesKey(vodId)] ?: false
        }
    }

    suspend fun toggleFavorite(vodId: String, isFavorite: Boolean) {
        context.dataStore.edit { prefs ->
            prefs[booleanPreferencesKey(vodId)] = isFavorite
        }
    }
}
