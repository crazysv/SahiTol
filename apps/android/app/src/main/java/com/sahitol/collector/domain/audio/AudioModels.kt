package com.sahitol.collector.domain.audio

/**
 * Audio models conforming to docs/14_TRANSLATION_AUDIO_AUDIT.md and R-LANG-02.
 */

data class AudioClipEntry(
    val clipId: String,
    val locale: String,
    val scriptKey: String,
    val exactText: String,
    val voice: String,
    val toolVersion: String,
    val licenceAttribution: String,
    val generationDate: String,
    val fileName: String,
    val codec: String,
    val durationMs: Int,
    val sizeBytes: Long,
    val sha256: String,
    val reviewStatus: String
)

data class AudioManifest(
    val formatVersion: String,
    val description: String,
    val totalClips: Int,
    val locales: List<String>,
    val licence: String,
    val runtimeCloudCall: Boolean,
    val clips: List<AudioClipEntry>
)

sealed class AudioPlaybackEvent {
    object Idle : AudioPlaybackEvent()
    data class Playing(val clipId: String, val index: Int, val total: Int) : AudioPlaybackEvent()
    data class MissingClip(val clipId: String) : AudioPlaybackEvent()
    object Completed : AudioPlaybackEvent()
    object Stopped : AudioPlaybackEvent()
    data class Error(val message: String) : AudioPlaybackEvent()
}
