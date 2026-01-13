# Лабораторная работа 9 (MVC + SQLite + CRUD)

## Запуск
1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Запустите сервер:

```bash
python app.py
```

3. Откройте в браузере:
- http://127.0.0.1:8000/

## Маршруты
- `/` — главная страница
- `/author` — автор
- `/users` — список пользователей
- `/user?id=1` — страница пользователя и подписки
- `/user/subscribe?id=1&currency_id=2` — подписка
- `/user/unsubscribe?id=1&currency_id=2` — отписка
- `/currencies` — список валют + CRUD
- `/currency/create?...` — создание валюты (GET)
- `/currency/update?USD=91.2` — обновление курса (GET)
- `/currency/delete?id=1` — удаление валюты (GET)
- `/currency/show` — вывод валют в консоль (для отладки)

## Тесты
```bash
python -m unittest discover -s tests -v
```
