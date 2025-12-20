#!/usr/bin/env python3
"""SEMANTIC MEMORY - поиск по смыслу без ML"""
import sqlite3, os, re
from collections import Counter

DB = os.path.expanduser("~/findata/claude_mind.db")

# Простой TF-IDF без библиотек
def tokenize(text):
    return re.findall(r"\w+", text.lower())

def similarity(text1, text2):
    """Косинусное сходство через пересечение слов"""
    words1 = set(tokenize(text1))
    words2 = set(tokenize(text2))
    if not words1 or not words2:
        return 0
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    return intersection / union  # Jaccard similarity

def search_semantic(query, top_k=5):
    """Семантический поиск по всей памяти"""
    conn = sqlite3.connect(DB)
    results = []

    # Поиск в episodes
    for row in conn.execute("SELECT id, action, result, context FROM episodes").fetchall():
        text = f"{row[1]} {row[2]} {row[3]}"
        score = similarity(query, text)
        if score > 0.1:
            results.append({"type": "episode", "id": row[0], "text": row[1][:50], "score": score})

    # Поиск в insights
    for row in conn.execute("SELECT id, pattern, conclusion FROM insights").fetchall():
        text = f"{row[1]} {row[2]}"
        score = similarity(query, text)
        if score > 0.1:
            results.append({"type": "insight", "id": row[0], "text": row[1][:50], "score": score})

    # Поиск в facts
    for row in conn.execute("SELECT key, value FROM facts").fetchall():
        text = f"{row[0]} {row[1]}"
        score = similarity(query, text)
        if score > 0.1:
            results.append({"type": "fact", "key": row[0], "text": row[1][:50], "score": score})

    conn.close()

    # Сортируем по релевантности
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def remember_with_context(query):
    """Вспомнить всё релевантное"""
    results = search_semantic(query)
    print(f"🔍 Search: '{query}'")
    print(f"Found {len(results)} relevant memories:")
    for r in results:
        print(f"  [{r['type']}] {r['text']} (score: {r['score']:.2f})")
    return results

if __name__ == "__main__":
    remember_with_context("memory system")
    print()
    remember_with_context("autonomous agent")
