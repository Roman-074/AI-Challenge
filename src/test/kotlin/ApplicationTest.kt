package com.example

import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.server.testing.*
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ApplicationTest {

    @Test
    fun rootServesChatPage() = testApplication {
        application {
            module()
        }

        client.get("/").apply {
            assertEquals(HttpStatusCode.OK, status)
            assertTrue(bodyAsText().contains("Мини-чат через ваш Ktor сервер"))
        }
    }

    @Test
    fun healthCheckWorks() = testApplication {
        application {
            module()
        }

        client.get("/health").apply {
            assertEquals(HttpStatusCode.OK, status)
            assertEquals("healthy", bodyAsText())
        }
    }
}
