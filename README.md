<h1 align="center">
<img src="assets/logo.png" width="450" align="center">

Dimir Poker Bot <br>
для ведения статистики покерных игр

</h1>

---
## 📝 О проекте
**Dimir Poker Bot** — это Telegram-бот для учета и анализа статистики домашних покерных игр.

Бот помогает:
- 📊 Вести учет результатов прошедших игр
- 👥 Управлять списком игроков
- 🏆 Формировать рейтинги участников
- 📈 Анализировать динамику результатов
---
## 🛠️ Технологии
### Основные технологии
- Python 3.10+
- Aiogram 3.17 (асинхронный фреймворк для Telegram Bot API)
- SQLAlchemy 2.0 (ORM для работы с базой данных)
- Alembic (миграции базы данных)
- PostgreSQL/asyncpg (асинхронное взаимодействие с БД)
### Вспомогательные библиотеки
- Pydantic (валидация данных)
- Pandas (анализ статистики)
- Matplotlib (визуализация данных)
---
## ⚙️ Установка и настройка
1. Клонируйте репозиторий:
   ```bash
    git clone https://github.com/DiMiRka/dimirka_poker_bot.git
    cd DimirPokerBot
   ```
2. Настройка окружения:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate  # Windows
   ```
3. Установка зависимостей:
    ```bash
    pip install -r requirements.txt
   ```
4. Настройка конфигурации:\
Создайте файл .env в корне проекта:
    ```ini
    TOKEN=ваш_токен_бота
    ADMINS=ваш_telegram_id
    PG_LINK=postgresql+asyncpg://user:password@localhost/dbname
    ROOT_PASS=пароль для класса DatabaseManager для защиты от несанкционированного доступа
   ```
5. Запуск проекта:
    ```bash
    python aiogram_run.py
   ```
---
### 🗂 Структура проекта
```
DimirPokerBot/
├──alembic/                    # Миграции базы данных
│   ├── versions/              # Файлы миграций
│   ├── env.py                 # Конфигурация Alembic
│   └── script.py.mako         # Шаблон для генерации миграций
│
├── assests/                   # Логотипы и скриншоты приложения 
│
├── db/                        # Конфигурация базы данных(Postgres)
│
├── filters/                   # Фильтры Telegram бота
│   ├── __init__.py
│   └── is_admin.py            # Фильтр администратора Telegram бота
│
├── handlers/                  # Обработчики сообщений Telegram бота
│   ├── __init__.py
│   ├── game.py                # Управление играми
│   ├── player.py              # Работа с игроками
│   ├── player_statistics.py   # Статистика игроков 
│   └── start.py               # Стартовые команды
│
├── keyboards/                 # Оформление кнопок Telegram бота
│   ├── __init__.py
│   ├── game.py                # Кпопки игрового процесса 
│   └── start.py               # Стартовые кнопки
│
├── models/                    # Модели SQLAlchemy
│
├── repositories/              # Репозитории для абстракции работы с базой данных
│   ├── __init__.py
│   ├── base.py                # Базовый репозиторий
│   ├── game.py                # Репозиторий для работы с играми
│   └── start.py               # Репозиторий для работы с игроками
│
├── services/                  # Бизнес логика
│   ├── __init__.py
│   ├── game.py                # Сервис игр
│   └── player.py              # Сервис игроков
│
├── tests/                     # Тестирование (в разработке)
│
├── utils/                     # Вспомогательные функции
│   ├── photo/                 # Визуальное оформление игр и статистики
│   ├── __init__.py
│   ├── game_utils.py          # Функции для организации игр
│   └── statistic_utils.py     # Функции для подведения статистики
│
├── .env                       # Файл локального кружения
├── .gitignore                 # Игнорируемые файлы Git
├── aiogram_run.py             # Запуск Telegram бота
├── alembic.ini                # Конфигурация Alembic
├── create_bot.py              # Инициализация бота
├── README.md
└── requirements.txt           # Список зависимостей
```
---
## 📋 Основные команды бота
| Команда    | Назначение                           |
|------------|--------------------------------------|
| start      | Запустить бота                       |
| start_game | Запустить процесс игры               |
| new_player | Добавить нового игрока в базу данных |
| statics    | Показать статистику игроков          |

---
## 🃏 Пример работы

### Процесс игры
<div align="center">
  <table>
    <tr>
      <td width="60%" valign="top">
        <ol>
          <li>Выбор коэффициента одной фишки к рублю</li>
          <li>Поэтапно добавить всех участвующих игроков</li>
          <li>Нажать готово и старт</li>
        </ol>
      </td>
      <td width="40%">
        <img src="assets/demo/start_game.gif" alt="Как создать новую игру" width="300">
      </td>
    </tr>
  </table>
</div>