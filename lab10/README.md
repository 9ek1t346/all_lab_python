# Лабораторная работа №10 — оптимизация вычислений (потоки, процессы, Cython, отпускание GIL)

Автор: **Затонских Никита Денисович**, группа **P-3123**

## Структура проекта

- `src/lab10/integrate.py` — базовая реализация и параллельные версии (threads/processes)
- `src/lab10/integrate_cy.pyx` — Cython-ускоренные версии + `nogil`/OpenMP
- `tests/` — тесты `pytest`
- `report/` — отчет (`.docx`) и артефакты замеров (`bench_results.json`, `profile_stats.txt`)

## Установка

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

> Для сборки Cython нужна среда компиляции C/C++ (Linux: `build-essential`, Windows: Build Tools for Visual Studio).

## Запуск тестов

```bash
pytest -q
python -m doctest -v src/lab10/integrate.py
```

## Замеры времени и профилирование

```bash
python -m lab10.bench
python -m lab10.profile
```

## Примечание по GIL

Для CPU-bound задач с Python-callable (например, `math.sin`) **потоки** обычно не ускоряют вычисления из-за GIL.
Ускорение обычно достигается либо через **процессы**, либо через перенос горячего цикла в C/Cython с `nogil`.



## Запуск без сборки Cython (если нет компилятора/заголовков)

Можно запускать тесты и бенчмарки без установки пакета, просто добавив `src` в `PYTHONPATH`:

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m doctest -v src/lab10/integrate.py
PYTHONPATH=src python -m lab10.bench
```

## Сборка Cython (опционально)

На Ubuntu/Debian обычно требуется:

```bash
sudo apt-get install -y build-essential python3-dev
```

После этого:

```bash
pip install -e .
```

