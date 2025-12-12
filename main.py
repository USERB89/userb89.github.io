#!/usr/bin/env python3
# build_arabic_corpus_test.py
"""
Тестовый сборщик арабских слов из нескольких источников.
- Работает в TEST_MODE (по умолчанию True) — скачивает только первые TEST_BYTES байт каждого файла,
  извлекает арабские последовательности (слова/формы) и сохраняет в CSV.
- При TEST_MODE=False можно расширять логику для полного скачивания / распаковки.
"""

import os
import re
import csv
import sys
import requests
import zipfile
from io import BytesIO

# ========== Настройки ==========
TEST_MODE = False          # True = тестовый режим (маленькие загрузки); False = полный режим
TEST_BYTES = 50 * 1024   # сколько байт скачивать в тестовом режиме (50 KB) — можно уменьшить/увеличить
DATA_DIR = os.path.join(os.path.dirname(__file__), "datasets")
OUT_CSV = os.path.join(os.path.dirname(__file__), "arabic_words_test.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# Список источников. Для каждого: name, url, type_hint (txt|zip|raw)
SOURCES = [
    ("quranic", "https://corpus.quran.com/download/wordbyword.txt", "txt"),
    ("arabic_wordlist_cjki", "https://raw.githubusercontent.com/linuxscout/arabic-wordlist/master/arabic.txt", "txt"),
    ("qabas", "https://github.com/arabic-tools/qabas/archive/refs/heads/main.zip", "zip"),
    ("arablex", "https://www.cjk.org/data/arabic/nlp/arablex-arabic-full-form-lexicon/arablex.zip", "zip"),  # пример
    ("camel", "https://github.com/CAMeL-Lab/Camel_Arabic_Frequency_Lists/archive/refs/heads/master.zip", "zip"),
    ("kalimat", "https://sourceforge.net/projects/kalimat/files/kalimat/kalimat.zip/download", "zip"),
]

# Регулярное выражение для арабских букв + огласовок (включая тревиальные диапазоны)
ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]+")

# Диакритики/огласовки (для удаления при создании word_without_tashkeel)
DIACRITICS_RE = re.compile(
    "[" +
    "\u0610-\u061A" +  # Quranic annotation signs
    "\u064B-\u0652" +  # tashkeel
    "\u06D6-\u06ED" +  # more signs
    "\u0670" +
    "]"
)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; arabic-corpus-test/1.0)"}

# ========== Функции ==========
def fetch_head_bytes(url, max_bytes=TEST_BYTES):
    """Скачивает первые max_bytes байт ресурса (stream). Возвращает bytes."""
    try:
        # Попробуем запрос с Range заголовком (работает не везде, но часто)
        headers = dict(HEADERS)
        headers["Range"] = f"bytes=0-{max_bytes-1}"
        r = requests.get(url, headers=headers, timeout=30, stream=True)
        if r.status_code in (200, 206):
            chunk = r.content
            return chunk
        else:
            # fallback: обычный запрос, но читаем только первую часть
            r = requests.get(url, headers=HEADERS, stream=True, timeout=30)
            content = b""
            for part in r.iter_content(chunk_size=8192):
                content += part
                if len(content) >= max_bytes:
                    break
            return content
    except Exception as e:
        print(f"⚠️ Ошибка при загрузке {url}: {e}")
        return b""

def extract_arabic_from_bytes(bdata):
    """Ищет арабские последовательности в bytes, пытаясь декодировать в utf-8/latin1."""
    if not bdata:
        return []
    for encoding in ("utf-8", "windows-1256", "latin1"):
        try:
            text = bdata.decode(encoding, errors="ignore")
            words = ARABIC_RE.findall(text)
            if words:
                return words
        except Exception:
            continue
    return []

def process_txt_source(name, url, out_set):
    print(f"\n🔽 Текстовый источник: {name} -> {url}")
    data = fetch_head_bytes(url)
    words = extract_arabic_from_bytes(data)
    n = 0
    for w in words:
        out_set.add((w, DIACRITICS_RE.sub("", w), name))
        n += 1
        if TEST_MODE and n >= 20:  # в тестовом режиме ограничиваем по словам/источнику
            break
    print(f"   добавлено {min(len(words), 20) if TEST_MODE else len(words)} слов (примерно)")

def process_zip_source(name, url, out_set):
    print(f"\n🔽 ZIP источник: {name} -> {url}")
    # Скачиваем первые bytes; затем пытаемся открыть как zip (в тестовом режиме может не сработать)
    data = fetch_head_bytes(url)
    # Попробуем открыть как zip полностью — если тестовый кусок неполный, zipfile.BadZipFile может возникнуть
    try:
        bio = BytesIO(data)
        with zipfile.ZipFile(bio) as z:
            # проходим по первым файлам в архиве
            members = z.namelist()
            count = 0
            for member in members:
                if member.endswith((".txt", ".csv", ".tsv")):
                    with z.open(member) as f:
                        try:
                            text = f.read().decode("utf-8", errors="ignore")
                        except:
                            continue
                        words = ARABIC_RE.findall(text)
                        for w in words:
                            out_set.add((w, DIACRITICS_RE.sub("", w), name))
                            count += 1
                            if TEST_MODE and count >= 20:
                                break
                if TEST_MODE and count >= 20:
                    break
            print(f"   извлечено {count} слов из архива (если архив доступен)")
            return
    except zipfile.BadZipFile:
        # Не полный ZIP — попробуем искать арабские последовательности в сыром байт-куске
        words = extract_arabic_from_bytes(data)
        cnt = 0
        for w in words:
            out_set.add((w, DIACRITICS_RE.sub("", w), name))
            cnt += 1
            if TEST_MODE and cnt >= 20:
                break
        print(f"   ZIP неполный/недоступен — найдено {cnt} арабских последовательностей в скачанном куске")
    except Exception as e:
        print(f"   ошибка при обработке ZIP: {e}")

# ========== MAIN ==========
def main():
    all_words = set()  # (with_tashkeel, without_tashkeel, source)

    for name, url, kind in SOURCES:
        if kind == "txt":
            process_txt_source(name, url, all_words)
        elif kind == "zip":
            process_zip_source(name, url, all_words)
        else:
            # общий путь: скачать кусок и искать арабские последовательности
            print(f"\n🔽 (generic) {name} -> {url}")
            data = fetch_head_bytes(url)
            words = extract_arabic_from_bytes(data)
            cnt = 0
            for w in words:
                all_words.add((w, DIACRITICS_RE.sub("", w), name))
                cnt += 1
                if TEST_MODE and cnt >= 20:
                    break
            print(f"   найдено {cnt} слов (generic)")

       # Сохраняем результат в CSV
    print(f"\n💾 Сохраняю результат в {OUT_CSV} ...")
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["word_with_tashkeel", "word_without_tashkeel", "source"])
        # сортируем для воспроизводимости
        for w_with, w_no, src in sorted(all_words, key=lambda x: (x[2], x[0])):
            writer.writerow([w_with, w_no, src])

    print(f"✅ Готово. Всего уникальных записей: {len(all_words)}")
    print(f"Файл: {OUT_CSV}")
    if TEST_MODE:
        print("\n🔎 Тестовый режим: скачано только небольшие куски (TEST_BYTES).")
        print("Если всё ок — переключи TEST_MODE = False и запусти снова для полного скачивания/обработки.")
    else:
        print("\nℹ️ Полный режим: скрипт должен быть доработан для безопасной загрузки больших архивов и их последовательной обработки.")

if __name__ == "__main__":
    main()
