# Music Service

Учебный веб-сервис «Каталог музыкальных треков» (Python + Flask).
В браузере отдаёт HTML-страницы, в curl / скриптах — JSON.

## Локальный запуск
```bash
pip install -r requirements.txt
python app.py
```
Открыть: http://localhost:5000/

## Страницы и эндпоинты
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | главная страница / информация о сервисе |
| GET | `/tracks` | каталог, фильтры `?genre=`, `?artist=`, `?year=` |
| GET | `/tracks/<id>` | страница трека |
| GET | `/genres` | жанры и количество треков |
| GET | `/random` | случайный трек |
| GET | `/health` | проверка работоспособности (JSON) |

Формат ответа можно задать явно: `?format=json` или `?format=html`.

## Деплой на Render.com
- Language: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Instance Type: Free
