#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавляет один отзыв из queue.json в reviews.json.
Запускается вручную или через cron.
"""
import json
import os
import random
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def summary(reviews):
    total = len(reviews)
    if total == 0:
        return {"rating": 0, "total": 0, "distribution": {}}
    s = sum(r["rating"] for r in reviews)
    dist = {5:0,4:0,3:0,2:0,1:0}
    for r in reviews:
        dist[r["rating"]] += 1
    rating = round(s / total + random.uniform(-0.03, 0.03), 2)
    rating = max(1.0, min(5.0, rating))
    return {
        "rating": rating,
        "total": total,
        "distribution": {str(k): v for k, v in dist.items()}
    }


def main():
    rp = os.path.join(BASE, "reviews.json")
    qp = os.path.join(BASE, "queue.json")

    if not os.path.exists(qp):
        print("queue.json не найден. Запусти generate_reviews.py")
        return

    with open(rp, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(qp, "r", encoding="utf-8") as f:
        queue = json.load(f)

    if not queue:
        print("Очередь пуста.")
        return

    # Берём 1 отзыв, но иногда 0 или 2 (для реалистичности)
    n = random.choices([0, 1, 2], weights=[10, 75, 15], k=1)[0]
    if n == 0:
        print("Сегодня без нового отзыва (реалистичная пауза).")
        return

    new = queue[:n]
    queue = queue[n:]

    # Обновляем дату на сегодня
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for r in new:
        r["date"] = today

    # Добавляем в reviews
    data["reviews"] = new + data["reviews"]
    # Ограничиваем 200
    data["reviews"] = data["reviews"][:200]
    data["summary"] = summary(data["reviews"])

    with open(rp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(qp, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    print(f"Добавлено: {len(new)}. Осталось в очереди: {len(queue)}")


if __name__ == "__main__":
    main()
