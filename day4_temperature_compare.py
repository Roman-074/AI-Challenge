#!/usr/bin/env python3
import json
import os
import time
import urllib.request
import re
from collections import Counter

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Один и тот же запрос для всех температур
PROMPT = (
    "Задача: Дан список чисел [10, 9, 2, 5, 3, 7, 101, 18]. "
    "Найди длину самой длинной строго возрастающей подпоследовательности (LIS). "
    "Ответ дай в формате: 1) число, 2) короткое объяснение (2-3 предложения), "
    "3) одна простая аналогия из жизни."
)
EXPECTED_ANSWER = "4"
TEMPERATURES = [0, 0.7, 1.2]


def chat_completion(messages, temperature=0.0):
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

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"].strip()


def tokenize(text: str):
    return re.findall(r"[\wа-яА-ЯёЁ]+", text.lower())


def lexical_diversity(text: str) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    return round(len(set(tokens)) / len(tokens), 4)


def accuracy_label(answer_text: str) -> str:
    return "high" if EXPECTED_ANSWER in answer_text else "low"


def creativity_label(diversity: float, length: int) -> str:
    if diversity >= 0.7 and length >= 220:
        return "high"
    if diversity >= 0.55 and length >= 150:
        return "medium"
    return "low"


def diversity_vs_base(base: str, candidate: str) -> float:
    a = set(tokenize(base))
    b = set(tokenize(candidate))
    if not a and not b:
        return 0.0
    jaccard = len(a & b) / max(1, len(a | b))
    return round(1 - jaccard, 4)


def run_all():
    results = []

    for temp in TEMPERATURES:
        answer = chat_completion([{"role": "user", "content": PROMPT}], temperature=temp)
        diversity = lexical_diversity(answer)
        res = {
            "temperature": temp,
            "answer": answer,
            "metrics": {
                "accuracy": accuracy_label(answer),
                "length_chars": len(answer),
                "lexical_diversity": diversity,
                "creativity": creativity_label(diversity, len(answer)),
            },
        }
        results.append(res)

    base_answer = next(r["answer"] for r in results if r["temperature"] == 0)
    for r in results:
        r["metrics"]["diversity_vs_temp0"] = diversity_vs_base(base_answer, r["answer"])

    recommendation = {
        "temperature_0": "Лучше для точных, воспроизводимых задач: код, расчеты, инструкции, FAQ.",
        "temperature_0_7": "Баланс точности и естественности: деловая переписка, контент, понятные объяснения.",
        "temperature_1_2": "Лучше для креативных задач: брейншторм, варианты слоганов, идеи кампаний.",
    }

    summary = {
        "task": PROMPT,
        "expected": EXPECTED_ANSWER,
        "model": MODEL,
        "base_url": BASE_URL,
        "timestamp": int(time.time()),
        "results": results,
        "recommendation": recommendation,
    }

    out_path = "day4_temperature_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Done. Results saved to {out_path}")
    print(json.dumps(summary["results"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_all()
