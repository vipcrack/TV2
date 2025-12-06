package com.ffzy.tv.data

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface FFZYApiService {
    @GET("api.php/provide/vod/")
    suspend fun getLatestMovies(
        @Query("ac") ac: String = "list",
        @Query("pg") page: Int = 1,
        @Query("t") typeId: String? = null,
        @Query("wd") keyword: String? = null
    ): Response<ApiResponse>

    @GET("api.php/provide/vodtypes/")
    suspend fun getCategories(): Response<TypesResponse>
}
