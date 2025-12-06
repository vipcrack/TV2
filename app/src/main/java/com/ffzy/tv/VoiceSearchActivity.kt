package com.ffzy.tv

import android.os.Bundle
import androidx.leanback.app.SearchSupportFragment
import androidx.leanback.widget.SearchBar
import androidx.leanback.widget.SpeechRecognitionCallback

class VoiceSearchActivity : androidx.fragment.app.FragmentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager.beginTransaction()
            .replace(android.R.id.content, VoiceSearchFragment())
            .commit()
    }
}

class VoiceSearchFragment : SearchSupportFragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setSearchResultProvider(object : SearchSupportFragment.SearchResultProvider {
            override fun getResults(searchQuery: String, progress: SearchBar.SearchBarProgress): MutableList<*> {
                return mutableListOf()
            }
            override fun onQueryTextChange(newQuery: String): Boolean = false
            override fun onQueryTextSubmit(query: String): Boolean {
                (activity as? MainActivity)?.performSearch(query)
                activity?.finish()
                return true
            }
        })

        setSpeechRecognitionCallback(object : SpeechRecognitionCallback {
            override fun recognizeSpeech() {
                startRecognition()
            }
        })
    }
}
