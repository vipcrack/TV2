package com.ffzy.tv.data

import com.google.gson.annotations.SerializedName

data class TypeItem(
    @SerializedName("type_id") val id: String,
    @SerializedName("type_name") val name: String
)

data class TypesResponse(
    val code: Int,
    val msg: String,
    val types: List<TypeItem>
)
