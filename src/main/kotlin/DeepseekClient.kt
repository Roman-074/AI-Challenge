package com.example

import io.ktor.http.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

private const val DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
private const val DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"

class DeepseekClient(
    private val apiKey: String,
    private val model: String = DEFAULT_DEEPSEEK_MODEL,
    private val httpClient: HttpClient = HttpClient.newHttpClient()
) {
    suspend fun ask(prompt: String): String {
        require(prompt.isNotBlank()) { "Prompt must not be blank" }
        return chat(listOf(ChatMessage(role = "user", content = prompt.trim())))
    }

    suspend fun chat(messages: List<ChatMessage>): String {
        require(messages.isNotEmpty()) { "Messages must not be empty" }
        require(messages.all { it.content.isNotBlank() }) { "Message content must not be blank" }

        val requestBody = Json.encodeToString(
            ChatCompletionsRequest(
                model = model,
                messages = messages
            )
        )

        val httpRequest = HttpRequest.newBuilder()
            .uri(URI.create(DEEPSEEK_API_URL))
            .header(HttpHeaders.Authorization, "Bearer $apiKey")
            .header(HttpHeaders.ContentType, ContentType.Application.Json.toString())
            .POST(HttpRequest.BodyPublishers.ofString(requestBody))
            .build()

        val response = withContext(Dispatchers.IO) {
            httpClient.send(httpRequest, HttpResponse.BodyHandlers.ofString())
        }

        if (response.statusCode() !in 200..299) {
            throw IllegalStateException("Deepseek API request failed: HTTP ${response.statusCode()} body=${response.body()}")
        }

        return Json.parseToJsonElement(response.body())
            .jsonObject["choices"]
            ?.jsonArray
            ?.firstOrNull()
            ?.jsonObject
            ?.get("message")
            ?.jsonObject
            ?.get("content")
            ?.jsonPrimitive
            ?.content
            ?.trim()
            .orEmpty()
    }
}

@Serializable
data class ChatCompletionsRequest(
    val model: String,
    val messages: List<ChatMessage>
)

@Serializable
data class ChatMessage(
    val role: String,
    val content: String
)
