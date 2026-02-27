#!/usr/bin/env python3
import json
import os
import time
import urllib.request

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Одна задача с проверяемым правильным ответом
TASK = (
    "Задача: Дан список чисел [10, 9, 2, 5, 3, 7, 101, 18]. "
    "Найди длину самой длинной строго возрастающей подпоследовательности (LIS). "
    "Ответ дай числом и коротким пояснением."
)
EXPECTED_ANSWER = "4"


def chat_completion(messages, temperature=0):
    if not API_KEY:
        raise RuntimeError("Set OPENAI_API_KEY first")

    url = f"{BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )

    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def judge_accuracy(answer_text: str) -> str:
    # Простая оценка для этой задачи
    return "correct" if EXPECTED_ANSWER in answer_text else "possibly wrong"


def run_all():
    runs = []

    # 1) Прямой ответ
    direct_messages = [
        {"role": "user", "content": TASK}
    ]
    direct = chat_completion(direct_messages)
    runs.append({"method": "direct", "answer": direct, "accuracy": judge_accuracy(direct)})

    # 2) Решай пошагово
    step_messages = [
        {"role": "user", "content": TASK + "\n\nИнструкция: решай пошагово."}
    ]
    step = chat_completion(step_messages)
    runs.append({"method": "step_by_step", "answer": step, "accuracy": judge_accuracy(step)})

    # 3) Сначала составь промпт, потом реши им
    prompt_builder_messages = [
        {
            "role": "user",
            "content": (
                "Сначала создай максимально эффективный промпт для решения задачи ниже. "
                "Верни только текст этого промпта.\n\n" + TASK
            )
        }
    ]
    generated_prompt = chat_completion(prompt_builder_messages)

    prompt_then_solve_messages = [
        {"role": "user", "content": generated_prompt}
    ]
    prompt_then_solve = chat_completion(prompt_then_solve_messages)
    runs.append({
        "method": "prompt_then_solve",
        "generated_prompt": generated_prompt,
        "answer": prompt_then_solve,
        "accuracy": judge_accuracy(prompt_then_solve),
    })

    # 4) Группа экспертов
    experts_messages = [
        {
            "role": "user",
            "content": (
                "Реши задачу в формате группы экспертов.\n"
                "Эксперт 1: Аналитик\n"
                "Эксперт 2: Инженер\n"
                "Эксперт 3: Критик\n"
                "Каждый дает свое решение кратко. Затем общий итог.\n\n"
                + TASK
            ),
        }
    ]
    experts = chat_completion(experts_messages)
    runs.append({"method": "experts", "answer": experts, "accuracy": judge_accuracy(experts)})

    # Итоговое сравнение
    correct_count = sum(1 for r in runs if r["accuracy"] == "correct")
    summary = {
        "task": TASK,
        "expected": EXPECTED_ANSWER,
        "model": MODEL,
        "base_url": BASE_URL,
        "timestamp": int(time.time()),
        "results": runs,
        "comparison": {
            "answers_differ": len({r["answer"] for r in runs}) > 1,
            "correct_count": correct_count,
            "best_method": (
                "step_by_step"
                if any(r["method"] == "step_by_step" and r["accuracy"] == "correct" for r in runs)
                else runs[0]["method"]
            ),
            "note": "Обычно step-by-step или experts дают более прозрачное и надежное обоснование.",
        },
    }

    out_path = "day3_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Done. Results saved to {out_path}")
    print(json.dumps(summary["comparison"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_all()
