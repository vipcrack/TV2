package com.ffzy.tv.data

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object FFZYRepository {
    private const val BASE_URL = "https://cj.ffzyapi.com/"

    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    val apiService: FFZYApiService by lazy {
        retrofit.create(FFZYApiService::class.java)
    }
}
