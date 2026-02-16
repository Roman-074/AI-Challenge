package com.example

import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.http.content.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.Serializable

fun Application.configureRouting() {
    routing {
        staticResources("/assets", "static")


        // Главная страница: resources/static/index.html
        staticResources("/", basePackage = "static") {
            default("index.html")
        }

        get("/health") {
            call.respondText("healthy")
        }

        post("/api/chat") {
            val apiKey = System.getenv("DEEPSEEK_API_KEY")
            if (apiKey.isNullOrBlank()) {
                call.respond(
                    HttpStatusCode.InternalServerError,
                    mapOf("error" to "DEEPSEEK_API_KEY is not set")
                )
                return@post
            }

            val request = call.receive<ChatProxyRequest>()
            val deepseekClient = DeepseekClient(apiKey = apiKey)

            val messages = request.messages?.takeIf { it.isNotEmpty() }
                ?.map { ChatMessage(role = it.role, content = it.content) }
                ?: listOf(ChatMessage(role = "user", content = request.prompt.orEmpty()))

            val reply = try {
                deepseekClient.chat(messages)
            } catch (error: IllegalArgumentException) {
                call.respond(HttpStatusCode.BadRequest, mapOf("error" to error.message.orEmpty()))
                return@post
            } catch (error: Exception) {
                call.respond(HttpStatusCode.BadGateway, mapOf("error" to error.message.orEmpty()))
                return@post
            }

            call.respond(ChatProxyResponse(reply = reply))
        }
    }
}

@Serializable
data class ChatProxyRequest(
    val prompt: String? = null,
    val messages: List<ChatTurn>? = null
)

@Serializable
data class ChatTurn(
    val role: String,
    val content: String
)

@Serializable
data class ChatProxyResponse(
    val reply: String
)
