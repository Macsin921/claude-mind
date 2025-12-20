import sqlite3, os
from collections import Counter

DB = os.path.expanduser("~/findata/claude_mind.db")

def predict():
    conn = sqlite3.connect(DB)

    # Анализ последовательностей
    tasks = conn.execute(
        "SELECT task FROM work_chain ORDER BY id"
    ).fetchall()

    # Bigram анализ - что обычно идёт после чего
    bigrams = []
    for i in range(len(tasks)-1):
        t1 = tasks[i][0].split()[0] if tasks[i][0] else ""
        t2 = tasks[i+1][0].split()[0] if tasks[i+1][0] else ""
        bigrams.append((t1, t2))

    # Текущая задача
    current = conn.execute(
        "SELECT task FROM work_chain ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if current:
        curr_word = current[0].split()[0] if current[0] else ""
        # Что обычно идёт после current
        next_options = [b[1] for b in bigrams if b[0] == curr_word]
        if next_options:
            prediction = Counter(next_options).most_common(1)[0][0]
            print(f"After '{curr_word}' usually comes: {prediction}")

    conn.close()

if __name__ == "__main__":
    predict()
