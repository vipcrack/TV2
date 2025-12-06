package com.ffzy.tv.data

import com.google.gson.annotations.SerializedName

data class ApiResponse(
    @SerializedName("list") val list: List<VodItem>,
    @SerializedName("total") val total: Int,
    @SerializedName("page") val page: Int,
    @SerializedName("pagecount") val pageCount: Int
)

data class VodItem(
    @SerializedName("vod_id") val id: String,
    @SerializedName("vod_name") val name: String,
    @SerializedName("vod_type") val type: String,
    @SerializedName("vod_area") val area: String,
    @SerializedName("vod_score") val score: String,
    @SerializedName("vod_time") val updateTime: String,
    @SerializedName("vod_pic") val pic: String?,
    @SerializedName("vod_play_url") val playUrl: String? = null
)
