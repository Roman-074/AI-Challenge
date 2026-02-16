# Holisto Backend: Deepseek Proxy Chat

Это Ktor-сервер, который поднимает мини-чат в браузере и проксирует сообщения в Deepseek API.

## Что умеет

- Web UI для чата на `http://localhost:8080`
- Кнопка отправки + Enter для отправки
- История диалога хранится на клиенте и отправляется серверу
- Серверная прослойка до Deepseek API через `POST /api/chat`

## Запуск

1. Установите ключ:

```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

2. Запустите сервер:

```bash
./gradlew run
```

3. Откройте в браузере:

```text
http://localhost:8080
```

## Проверка API вручную

```bash
curl -X POST http://localhost:8080/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Привет! Ответь в 1 предложении"}'
```

Или с историей:

```bash
curl -X POST http://localhost:8080/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Кто ты?"}]}'
```

## Полезные команды

- `./gradlew test` — тесты
- `./gradlew run` — запуск сервера
- `./gradlew build` — сборка
