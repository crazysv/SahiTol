package com.sahitol.collector.domain.canonical

import org.json.JSONArray
import org.json.JSONObject
import java.security.MessageDigest

/**
 * SAHITOL-JCS-1 Canonical JSON serialization and SHA-256 integrity hashing.
 * Guarantees exact cross-platform byte parity with Python and Web implementations.
 * Conforms to docs/planning/handover_fixture.json.
 */
object CanonicalJson {

    fun serialize(value: Any?): String {
        return when (value) {
            null -> "null"
            is JSONObject -> {
                val map = mutableMapOf<String, Any?>()
                val keys = value.keys()
                while (keys.hasNext()) {
                    val k = keys.next()
                    map[k] = if (value.isNull(k)) null else value.get(k)
                }
                serializeMap(map)
            }
            is JSONArray -> {
                val list = mutableListOf<Any?>()
                for (i in 0 until value.length()) {
                    list.add(if (value.isNull(i)) null else value.get(i))
                }
                serializeList(list)
            }
            is Map<*, *> -> {
                val stringMap = mutableMapOf<String, Any?>()
                for ((k, v) in value) {
                    stringMap[k.toString()] = v
                }
                serializeMap(stringMap)
            }
            is List<*> -> serializeList(value)
            is Array<*> -> serializeList(value.toList())
            is String -> escapeString(value)
            is Boolean -> if (value) "true" else "false"
            is Number -> value.toString()
            else -> escapeString(value.toString())
        }
    }

    private fun serializeMap(map: Map<String, Any?>): String {
        val sortedKeys = map.keys.sorted()
        val sb = StringBuilder("{")
        for ((idx, key) in sortedKeys.withIndex()) {
            if (idx > 0) sb.append(",")
            sb.append(escapeString(key)).append(":")
            sb.append(serialize(map[key]))
        }
        sb.append("}")
        return sb.toString()
    }

    private fun serializeList(list: List<Any?>): String {
        val sb = StringBuilder("[")
        for ((idx, item) in list.withIndex()) {
            if (idx > 0) sb.append(",")
            sb.append(serialize(item))
        }
        sb.append("]")
        return sb.toString()
    }

    private fun escapeString(s: String): String {
        val sb = StringBuilder("\"")
        for (c in s) {
            when (c) {
                '\"' -> sb.append("\\\"")
                '\\' -> sb.append("\\\\")
                '\b' -> sb.append("\\b")
                '\u000C' -> sb.append("\\f")
                '\n' -> sb.append("\\n")
                '\r' -> sb.append("\\r")
                '\t' -> sb.append("\\t")
                else -> {
                    if (c.code in 0x00..0x1F) {
                        sb.append(String.format("\\u%04x", c.code))
                    } else {
                        sb.append(c)
                    }
                }
            }
        }
        sb.append("\"")
        return sb.toString()
    }

    fun sha256Hex(canonicalString: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val bytes = digest.digest(canonicalString.toByteArray(Charsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it) }
    }

    fun hashPayload(payload: Any?): String {
        return sha256Hex(serialize(payload))
    }
}
