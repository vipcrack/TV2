package com.ffzy.tv.player

import android.content.Context
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer

class ExoPlayerManager(context: Context) {
    val player: ExoPlayer = ExoPlayer.Builder(context).build()

    fun prepare(url: String) {
        val mediaItem = MediaItem.fromUri(url)
        player.setMediaItem(mediaItem)
        player.prepare()
        player.playWhenReady = true
    }

    fun release() {
        player.release()
    }
}
