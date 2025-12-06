package com.ffzy.tv.data

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface ApiService {
    @GET("/api.php/provide/vod")
    suspend fun getVodList(
        @Query("ac") ac: String = "list",
        @Query("t") type: String? = null,
        @Query("wd") keyword: String? = null,
        @Query("pg") page: Int = 1,
        @Query("f") filters: String? = null
    ): Response<ApiResponse>
}
