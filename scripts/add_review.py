#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автодобавление отзыва из очереди.
Логика:
  - По умолчанию добавляет 0, 1 или 2 отзыва (взвешенно: 25% — 0, 50% — 1, 25% — 2)
  - С вероятностью 3% — 3 отзыва (пачка)
  - С вероятностью 5% — пропуск (ничего не добавляет)
  - Первый отзыв из очереди получает сегодняшнюю дату
  - Остальные (если пачка) — сегодня минус 1-3 дня
  - Пересчитывает summary
"""
import json, random, sys, os
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEWS_PATH = os.path.join(BASE, "reviews.json")
QUEUE_PATH = os.path.join(BASE, "queue.json")

random.seed()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compute_summary(reviews):
    total = len(reviews)
    dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    s = 0
    for r in reviews:
        dist[r["rating"]] += 1
        s += r["rating"]
    return {
        "rating": round(s / total, 1) if total else 0,
        "total": total,
        "distribution": {str(k): v for k, v in dist.items()}
    }


def main():
    data = load_json(REVIEWS_PATH)
    queue = load_json(QUEUE_PATH)

    if not queue:
        print("Очередь пуста. Ничего не добавляем.")
        return 0

    # Решаем, сколько добавить
    roll = random.random()
    if roll < 0.05:
        print("Сегодня пропуск — отзывов не добавляем.")
        return 0
    elif roll < 0.30:
        count = 0
        print("Сегодня без новых отзывов (рандом).")
        return 0
    elif roll < 0.80:
        count = 1
    elif roll < 0.97:
        count = 2
    else:
        count = 3

    count = min(count, len(queue))
    if count == 0:
        print("Нечего добавлять.")
        return 0

    added = []
    now = datetime.now(timezone.utc)

    for i in range(count):
        review = queue.pop(0)
        # Первый — сегодня, остальные с откатом
        delta_days = 0 if i == 0 else random.randint(1, 3)
        d = now - timedelta(days=delta_days)
        d = d.replace(
            hour=random.randint(8, 22),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=0
        )
        review["date"] = d.strftime("%Y-%m-%d")
        added.append(review)

    # Вставляем в начало (свежие сверху), потом пересортируем по дате
    data["reviews"] = added + data["reviews"]
    data["reviews"].sort(key=lambda r: r["date"], reverse=True)
    data["summary"] = compute_summary(data["reviews"])

    save_json(REVIEWS_PATH, data)
    save_json(QUEUE_PATH, queue)

    print(f"Добавлено отзывов: {count}")
    for r in added:
        print(f"  • {r['name_ru']} — {r['rating']}★ — {r['date']}")
    print(f"Осталось в очереди: {len(queue)}")
    print(f"Всего отзывов: {data['summary']['total']}, средний рейтинг: {data['summary']['rating']}")

    return count


if __name__ == "__main__":
    sys.exit(0 if main() >= 0 else 1)
