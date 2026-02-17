package com.example

private const val CONSTRAINED_REPLY_MAX_WORDS = 7

private val CONSTRAINED_REPLY_SYSTEM_PROMPT = """
Ты профессиональный стендап-комик. Обязательно соблюдай ограничения:
1) Ответ должен быть очень веселый, как ответ от профессионального комика.
2) Длина ответа должна быть максимум 7 слов.
3) Если в ответе встречается слово, оканчивающееся на "ь", останови ответ перед этим словом.
""".trimIndent()

fun prependConstraintSystemMessage(messages: List<ChatMessage>): List<ChatMessage> =
    listOf(ChatMessage(role = "system", content = CONSTRAINED_REPLY_SYSTEM_PROMPT)) + messages

fun applyConstrainedReplyRules(reply: String): String {
    val words = reply.trim().split(Regex("\\s+")).filter { it.isNotBlank() }
    if (words.isEmpty()) {
        return reply.trim()
    }

    val cutBySoftSign = words.takeWhile { !it.trimEnd('!', '?', '.', ',', ';', ':', '"', '\'', ')', '(').endsWith('ь') }
    val maxSevenWords = cutBySoftSign.take(CONSTRAINED_REPLY_MAX_WORDS)

    return maxSevenWords.joinToString(" ").trim()
}
