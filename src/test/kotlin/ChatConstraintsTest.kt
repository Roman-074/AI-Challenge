package com.example

import kotlin.test.Test
import kotlin.test.assertEquals

class ChatConstraintsTest {

    @Test
    fun `cuts reply before word ending with soft sign`() {
        val input = "Шутка огонь, но лошадь танцует ярко"

        val constrained = applyConstrainedReplyRules(input)

        assertEquals("Шутка огонь, но", constrained)
    }

    @Test
    fun `limits reply to seven words`() {
        val input = "раз два три четыре пять шесть семь восемь"

        val constrained = applyConstrainedReplyRules(input)

        assertEquals("раз два три четыре пять шесть семь", constrained)
    }

    @Test
    fun `prepends system message for constrained mode`() {
        val messages = listOf(ChatMessage(role = "user", content = "Привет"))

        val constrained = prependConstraintSystemMessage(messages)

        assertEquals("system", constrained.first().role)
        assertEquals("user", constrained[1].role)
    }
}
