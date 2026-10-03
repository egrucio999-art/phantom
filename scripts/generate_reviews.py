#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, random
from datetime import datetime, timedelta, timezone
from faker import Faker
from texts_ru import TEXTS_RU
from texts_uk import TEXTS_UK
from texts_en import TEXTS_EN
from texts_replies import REPLIES_POS, REPLIES_NEG

fake_ru = Faker('ru_RU')
fake_uk = Faker('uk_UA')

SEED = random.randint(1, 10**9)
random.seed(SEED)
Faker.seed(SEED)

TOP_RU = ["Александр","Сергей","Дмитрий","Андрей","Алексей","Максим","Евгений","Иван","Михаил","Артём","Николай","Владимир","Елена","Ольга","Наталья","Анна","Татьяна","Ирина","Мария","Светлана","Екатерина","Юлия","Марина","Виктория","Дарья"]
RARE_RU = ["Арсений","Всеволод","Филипп","Тимур","Ярослав","Богдан","Степан","Пётр","Василий","Ульяна","Пелагея"]
TOP_UK = ["Олександр","Сергій","Дмитро","Андрій","Олексій","Максим","Євген","Іван","Михайло","Артем","Микола","Володимир","Олена","Ольга","Наталія","Ганна","Тетяна","Ірина","Марія","Світлана","Катерина","Юлія","Марина","Оксана","Христина"]
SELLO_UK = ["Василь","Петро","Онисько","Грицько","Тарас","Богдан","Остап","Параска","Одарка","Катря","Маруся","Христя","Соломія","Меланія"]
SIG_RU = ["Клиент","Постоянный клиент","Анонимно","Без имени","Пользователь","Гость","Клиент из Киева","Клиент из Львова","Компания","Предприниматель"]
SIG_UK = ["Клієнт","Постійний клієнт","Анонімно","Без імені","Користувач","Гість","Клієнт з Києва","Клієнт з Львова","Клієнт із села","Підприємець"]
NAMES_EN = ["Alex","Michael","Daniel","David","James","Sarah","Emma","Anna","Maria","Client","Anonymous"]

SERVICES_RU = ["Восстановление доступа","Проверка информации","Аудит и защита","Для бизнеса","Другое"]
SERVICES_UK = ["Відновлення доступу","Перевірка інформації","Аудит і захист","Для бізнесу","Інше"]
SERVICES_EN = ["Access recovery","Information check","Audit and protection","For business","Other"]

SERVICE_W = [72, 18, 7, 2, 1]
RATING_W = [60, 22, 10, 5, 3]
LANG_DIST = ["ru"] * 55 + ["uk"] * 40 + ["en"] * 5
DAYS_BACK = 365 * 5
VISIBLE = 120
TOTAL = 520


def pick_ru_name():
    r = random.random()
    if r < 0.70: return random.choice(TOP_RU)
    if r < 0.88: return random.choice(RARE_RU)
    return random.choice(SIG_RU)


def pick_uk_name():
    r = random.random()
    if r < 0.55: return random.choice(TOP_UK)
    if r < 0.85: return random.choice(SELLO_UK)
    return random.choice(SIG_UK)


def pick_rating():
    return random.choices([5,4,3,2,1], weights=RATING_W, k=1)[0]


def add_typo(text):
    if random.random() > 0.05 or len(text) < 15:
        return text
    op = random.choice(['swap','double','space'])
    try:
        if op == 'swap' and len(text) > 10:
            i = random.randint(3, len(text) - 4)
            text = text[:i] + text[i+1] + text[i] + text[i+2:]
        elif op == 'double' and len(text) > 8:
            i = random.randint(2, len(text) - 3)
            text = text[:i] + text[i] + text[i:]
        elif op == 'space' and len(text) > 12:
            i = random.randint(4, len(text) - 5)
            text = text[:i] + " " + text[i:]
    except Exception:
        pass
    return text


def build_date(idx, total, days_back):
    t = idx / max(total, 1)
    base_days = int(days_back * (1 - t ** 0.65))
    if random.random() < 0.35:
        base_days = random.randint(30, days_back)
    base_days += random.randint(-25, 25)
    base_days = max(1, min(base_days, days_back))
    d = datetime.now(timezone.utc) - timedelta(days=base_days)
    if d.weekday() >= 5 and random.random() < 0.65:
        d -= timedelta(days=random.randint(1, 4))
    hour = random.choices(range(24), weights=[1,1,1,1,1,2,3,5,8,10,10,9,8,7,7,8,9,10,10,9,7,5,3,2], k=1)[0]
    return d.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59), microsecond=0)


def build_review(idx, total, days_back):
    si = random.choices(range(5), weights=SERVICE_W, k=1)[0]
    sr, su, se = SERVICES_RU[si], SERVICES_UK[si], SERVICES_EN[si]
    rating = pick_rating()
    lang_original = random.choice(LANG_DIST)

    if lang_original == "ru":
        name_ru, name_uk, name_en = pick_ru_name(), "", ""
    elif lang_original == "uk":
        name_ru, name_uk, name_en = "", pick_uk_name(), ""
    else:
        name_ru, name_uk, name_en = "", "", random.choice(NAMES_EN)

    pool_ru = TEXTS_RU.get(sr, TEXTS_RU["Другое"]).get(rating) or TEXTS_RU["Другое"][rating]
    pool_uk = TEXTS_UK.get(su, TEXTS_UK["Інше"]).get(rating) or TEXTS_UK["Інше"][rating]
    text_ru = random.choice(pool_ru)
    text_uk = random.choice(pool_uk)
    text_en = ""
    if lang_original == "en":
        pool_en = TEXTS_EN.get(se, TEXTS_EN["Other"]).get(rating) or TEXTS_EN["Other"][rating]
        text_en = random.choice(pool_en)

    translated_ru = lang_original != "ru"
    translated_uk = lang_original != "uk"
    translated_en = lang_original != "en"

    if lang_original == "ru":
        text_ru = add_typo(text_ru)
    elif lang_original == "uk":
        text_uk = add_typo(text_uk)
    elif lang_original == "en":
        text_en = add_typo(text_en)

    reply_ru = reply_uk = None
    if random.random() < 0.30:
        pool_r = REPLIES_NEG if rating <= 2 else REPLIES_POS
        reply_ru = random.choice(pool_r)
        reply_uk = random.choice(pool_r)

    date = build_date(idx, total, days_back)
    initial = ""
    if name_ru: initial = name_ru[0]
    elif name_uk: initial = name_uk[0]
    elif name_en: initial = name_en[0]

    return {
        "id": f"r-{idx:04d}",
        "name_ru": name_ru, "name_uk": name_uk, "name_en": name_en,
        "initial": initial,
        "service_ru": sr, "service_uk": su, "service_en": se,
        "rating": rating,
        "date": date.strftime("%Y-%m-%d"),
        "lang_original": lang_original,
        "text_ru": text_ru, "text_uk": text_uk, "text_en": text_en,
        "translated_ru": translated_ru,
        "translated_uk": translated_uk,
        "translated_en": translated_en,
        "reply_ru": reply_ru, "reply_uk": reply_uk
    }


def summary(reviews):
    total = len(reviews)
    if total == 0: return {"rating": 0, "total": 0, "distribution": {}}
    s = sum(r["rating"] for r in reviews)
    dist = {5:0,4:0,3:0,2:0,1:0}
    for r in reviews:
        dist[r["rating"]] += 1
    rating = round(s / total + random.uniform(-0.02, 0.02), 2)
    rating = max(1.0, min(5.0, rating))
    return {"rating": rating, "total": total, "distribution": {str(k): v for k, v in dist.items()}}


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Генерация {TOTAL} отзывов за 5 лет...")
    all_reviews = [build_review(i, TOTAL, DAYS_BACK) for i in range(1, TOTAL + 1)]
    all_reviews.sort(key=lambda x: x["date"], reverse=True)
    visible = all_reviews[:VISIBLE]
    queue = all_reviews[VISIBLE:]

    with open(os.path.join(base, "reviews.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary(visible), "reviews": visible}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(base, "queue.json"), "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    s = summary(visible)
    print(f"reviews.json: {len(visible)}, рейтинг {s['rating']}")
    print(f"queue.json: {len(queue)}")
    print(f"Распределение: {s['distribution']}")
    ru = sum(1 for r in visible if r["lang_original"]=="ru")
    uk = sum(1 for r in visible if r["lang_original"]=="uk")
    en = sum(1 for r in visible if r["lang_original"]=="en")
    print(f"Оригинал: ru={ru}, uk={uk}, en={en}")
    print(f"Seed: {SEED}")


if __name__ == "__main__":
    main()
