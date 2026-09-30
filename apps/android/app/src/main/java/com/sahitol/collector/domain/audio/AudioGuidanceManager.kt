package com.sahitol.collector.domain.audio

import android.content.Context
import android.media.MediaPlayer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.IOException

/**
 * AudioGuidanceManager handles local offline playback of pre-generated Hindi and Marathi clips.
 * Conforms to R-LANG-02, R-OPS-03, and AT-050:
 * - 100% on-device playback from local assets (zero cloud API call / airplane mode safe).
 * - Sequential queue playback with repeat and mute controls.
 * - Switching language stops previous queue immediately (no overlapping narration).
 * - Complete fallback behavior for missing/corrupt clips without crashing or halting the app.
 */
class AudioGuidanceManager(private val context: Context) {

    private var mediaPlayer: MediaPlayer? = null
    private var activeQueue = mutableListOf<String>()
    private var currentIndex = 0
    private var lastPlayedQueue = listOf<String>()

    private val _isMuted = MutableStateFlow(false)
    val isMuted: StateFlow<Boolean> = _isMuted.asStateFlow()

    private val _playbackState = MutableStateFlow<AudioPlaybackEvent>(AudioPlaybackEvent.Idle)
    val playbackState: StateFlow<AudioPlaybackEvent> = _playbackState.asStateFlow()

    private val missingClipsAudit = mutableListOf<String>()

    fun toggleMute(): Boolean {
        val newMute = !_isMuted.value
        _isMuted.value = newMute
        if (newMute) {
            stop()
        }
        return newMute
    }

    fun setMute(muted: Boolean) {
        _isMuted.value = muted
        if (muted) {
            stop()
        }
    }

    /**
     * Stops the playing queue immediately. Used during screen transitions or language switching.
     */
    fun stop() {
        try {
            mediaPlayer?.stop()
            mediaPlayer?.reset()
            mediaPlayer?.release()
        } catch (e: Exception) {
            // Ignored on cleanup
        } finally {
            mediaPlayer = null
            activeQueue.clear()
            currentIndex = 0
            _playbackState.value = AudioPlaybackEvent.Stopped
        }
    }

    /**
     * Plays a sequence of clip IDs sequentially.
     */
    fun playQueue(clipIds: List<String>) {
        if (_isMuted.value || clipIds.isEmpty()) return

        stop()
        activeQueue = clipIds.toMutableList()
        lastPlayedQueue = clipIds.toList()
        currentIndex = 0

        playNextClip()
    }

    /**
     * Repeats the last played audio queue (Tap-to-hear replay).
     */
    fun repeatLastQueue() {
        if (lastPlayedQueue.isNotEmpty()) {
            playQueue(lastPlayedQueue)
        }
    }

    private fun playNextClip() {
        if (currentIndex >= activeQueue.size) {
            _playbackState.value = AudioPlaybackEvent.Completed
            return
        }

        val clipId = activeQueue[currentIndex]
        val fileName = if (clipId.endsWith(".mp3")) clipId else "$clipId.mp3"
        val assetPath = "audio/$fileName"

        try {
            val afd = try {
                context.assets.openFd(assetPath)
            } catch (e: IOException) {
                // Missing clip fallback: log missing clip, notify state, and advance queue
                synchronized(missingClipsAudit) {
                    missingClipsAudit.add(clipId)
                }
                _playbackState.value = AudioPlaybackEvent.MissingClip(clipId)
                currentIndex++
                playNextClip()
                return
            }

            mediaPlayer = MediaPlayer().apply {
                setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
                afd.close()
                prepare()
                setOnCompletionListener {
                    it.reset()
                    it.release()
                    mediaPlayer = null
                    currentIndex++
                    playNextClip()
                }
                setOnErrorListener { mp, what, extra ->
                    mp.reset()
                    mp.release()
                    mediaPlayer = null
                    _playbackState.value = AudioPlaybackEvent.Error("MediaPlayer error: what=$what, extra=$extra")
                    currentIndex++
                    playNextClip()
                    true
                }
                start()
            }

            _playbackState.value = AudioPlaybackEvent.Playing(clipId, currentIndex, activeQueue.size)

        } catch (e: Exception) {
            _playbackState.value = AudioPlaybackEvent.Error("Failed to play clip $clipId: ${e.message}")
            currentIndex++
            playNextClip()
        }
    }

    fun getRecordedMissingClips(): List<String> {
        return synchronized(missingClipsAudit) {
            missingClipsAudit.toList()
        }
    }

    fun release() {
        stop()
    }
}
