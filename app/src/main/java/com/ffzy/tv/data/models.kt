package com.ffzy.tv.data

import com.google.gson.annotations.SerializedName

data class ApiResponse(
    val code: Int,
    val msg: String,
    val page: Int,
    val pagecount: Int,
    val limit: Int,
    val total: Int,
    val list: List<VodItem>
)

data class VodItem(
    @SerializedName("vod_id") val id: String,
    @SerializedName("vod_name") val name: String,
    @SerializedName("vod_type") val type: String,
    @SerializedName("vod_area") val area: String,
    @SerializedName("vod_score") val score: String,
    @SerializedName("vod_time") val updateTime: String,
    @SerializedName("vod_play_url") val playUrl: String? = null
) {
    fun getM3u8Url(): String? {
        return playUrl?.split("\$")?.getOrNull(1)
    }

    fun getPlayableUrl(): String? {
        val m3u8 = getM3u8Url()
        return if (m3u8 != null) {
            "https://svip.ffzyplay.com/?url=$m3u8"
        } else null
    }
}
