"""Music Service — веб-сервис «Каталог музыкальных треков».

Лабораторная работа №1: развертывание сервиса на Render.com.
Стек: Python + Flask. Запуск в облаке: gunicorn app:app

Один и тот же адрес отвечает по-разному в зависимости от клиента:
  * браузер (Accept: text/html)  -> красивая HTML-страница
  * curl / скрипты (Accept: */*) -> JSON
Формат можно задать явно: добавить к адресу ?format=json или ?format=html
"""
import os
import random

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.json.ensure_ascii = False      # чтобы кириллица в JSON не экранировалась
app.json.sort_keys = False

# Небольшая "база данных" треков в памяти
TRACKS = [
    {"id": 1, "title": "Bohemian Rhapsody", "artist": "Queen", "genre": "rock", "year": 1975, "duration_sec": 354},
    {"id": 2, "title": "Hotel California", "artist": "Eagles", "genre": "rock", "year": 1976, "duration_sec": 391},
    {"id": 3, "title": "Smells Like Teen Spirit", "artist": "Nirvana", "genre": "grunge", "year": 1991, "duration_sec": 301},
    {"id": 4, "title": "Billie Jean", "artist": "Michael Jackson", "genre": "pop", "year": 1982, "duration_sec": 294},
    {"id": 5, "title": "Blinding Lights", "artist": "The Weeknd", "genre": "synth-pop", "year": 2019, "duration_sec": 200},
    {"id": 6, "title": "Get Lucky", "artist": "Daft Punk", "genre": "electronic", "year": 2013, "duration_sec": 369},
    {"id": 7, "title": "Take Five", "artist": "Dave Brubeck Quartet", "genre": "jazz", "year": 1959, "duration_sec": 324},
    {"id": 8, "title": "So What", "artist": "Miles Davis", "genre": "jazz", "year": 1959, "duration_sec": 562},
    {"id": 9, "title": "Lose Yourself", "artist": "Eminem", "genre": "hip-hop", "year": 2002, "duration_sec": 326},
    {"id": 10, "title": "Группа крови", "artist": "Кино", "genre": "rock", "year": 1988, "duration_sec": 288},
]


def wants_html():
    """Определяем, кому отвечаем: браузеру (HTML) или программе (JSON)."""
    fmt = request.args.get("format", "").lower()
    if fmt == "json":
        return False
    if fmt == "html":
        return True
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "text/html"


@app.template_filter("mmss")
def mmss(seconds):
    """354 -> '5:54'"""
    return f"{seconds // 60}:{seconds % 60:02d}"


def genre_counts():
    counts = {}
    for t in TRACKS:
        counts[t["genre"]] = counts.get(t["genre"], 0) + 1
    return counts


# ----------------------------------------------------------------- страницы

@app.route("/")
def index():
    """GET / — главная страница (HTML) или описание сервиса (JSON)."""
    if wants_html():
        return render_template("index.html", total=len(TRACKS),
                               genres_total=len(genre_counts()),
                               featured=random.choice(TRACKS))
    return jsonify({
        "service": "Music Service",
        "description": "Каталог музыкальных треков (учебный проект, ЛР №1)",
        "tracks_total": len(TRACKS),
        "endpoints": {
            "GET /": "главная страница / информация о сервисе",
            "GET /tracks": "список треков (фильтры: ?genre=rock&artist=Queen&year=1975)",
            "GET /tracks/<id>": "информация о треке по id",
            "GET /genres": "список жанров и количество треков в каждом",
            "GET /random": "случайный трек",
            "GET /health": "проверка работоспособности",
        },
    })


@app.route("/tracks")
def list_tracks():
    """Список треков с необязательной фильтрацией."""
    genre = request.args.get("genre", "").strip().lower()
    artist = request.args.get("artist", "").strip().lower()
    year = request.args.get("year", type=int)

    result = TRACKS
    if genre:
        result = [t for t in result if t["genre"].lower() == genre]
    if artist:
        result = [t for t in result if artist in t["artist"].lower()]
    if year:
        result = [t for t in result if t["year"] == year]

    if wants_html():
        return render_template("tracks.html", tracks=result,
                               genres=sorted(genre_counts()),
                               f_genre=genre, f_artist=artist,
                               f_year=year or "")
    return jsonify({"count": len(result), "tracks": result})


@app.route("/tracks/<int:track_id>")
def get_track(track_id):
    """Один трек по id."""
    for track in TRACKS:
        if track["id"] == track_id:
            if wants_html():
                return render_template("track.html", track=track)
            return jsonify(track)
    return not_found(None, f"Трек с id={track_id} не найден")


@app.route("/genres")
def genres():
    """Жанры и количество треков в каждом."""
    counts = genre_counts()
    if wants_html():
        return render_template("genres.html", genres=counts)
    return jsonify(counts)


@app.route("/random")
def random_track():
    """Случайный трек."""
    track = random.choice(TRACKS)
    if wants_html():
        return render_template("track.html", track=track, is_random=True)
    return jsonify(track)


@app.route("/health")
def health():
    """Проверка работоспособности (всегда JSON)."""
    return jsonify({"status": "ok"})


@app.errorhandler(404)
def not_found(error, message="Страница не найдена"):
    if wants_html():
        return render_template("404.html", message=message), 404
    return jsonify({"error": message}), 404


if __name__ == "__main__":
    # Локальный запуск: python app.py
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
