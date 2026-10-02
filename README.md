<h1 align="center">
<img src="assets/logo.png" width="450" align="center">

Dimir Poker Bot <br>
для ведения статистики покерных игр

</h1>

---
## 📝 О проекте
**Dimir Poker Bot** — это Telegram-бот для учета и анализа статистики домашних покерных игр

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
- Pandas (анализ статистики)
- Matplotlib (визуализация данных)
---
## 🐳 Запуск через Docker Compose

Нужен Docker с поддержкой команды `docker compose`.
Скопируйте `.env.example` в `.env`, заполните `TOKEN`, `ADMINS`, `ROOT_PASS`
и задайте пароль PostgreSQL в `POSTGRES_PASSWORD`.
`POSTGRES_USER` и `POSTGRES_DB` определяют пользователя и имя контейнерной БД.

```bash
docker compose up --build -d
```

Бот ждёт готовности PostgreSQL, применяет миграции Alembic и запускает polling.
Compose задаёт `PG_HOST=db`; адрес подключения собирается из `POSTGRES_*`.
`PG_LINK` используется при запуске без Docker.

Логи и остановка:

```bash
docker compose logs -f bot
docker compose down
```

База хранится в volume `postgres_data` и сохраняется после `docker compose down`.
PostgreSQL доступен только внутри сети Compose. Перезапуск бота сбрасывает текущие игры в памяти;
результаты завершённых игр сохраняются в БД.

## ⚙️ Установка и настройка без Docker
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
Скопируйте `.env.example` в `.env` в корне проекта и заполните своими значениями:
    ```ini
    TOKEN=ваш_токен_бота
    ADMINS=ваш_telegram_id
    PG_LINK=postgresql+asyncpg://user:password@localhost/dbname
    ROOT_PASS=пароль для класса DatabaseManager для защиты от несанкционированного доступа
   ```
5. Запуск проекта:
    ```bash
    python -m alembic upgrade head
    python aiogram_run.py
   ```
---
## 🧪 Тестирование

Тесты проверяют расчёт статистики, изоляцию игр по чатам, ввод фишек и отрисовку таблиц
Telegram и PostgreSQL заменены моками: для запуска тестов `.env` и внешние сервисы не нужны

```bash
python -m unittest discover -s tests -t . -v
```

GitHub Actions запускает тесты на Python 3.10 и 3.11 при push и pull request.
После тестов CI проверяет конфигурацию Compose и собирает Docker-образ.

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
├── tests/                     # Тесты статистики, состояния игр, ввода и отрисовки
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
| past_games | Показать результаты прошлых игр      |



---
## 🃏 Пример работы

### Запуск бота
Команда **start** запускает стартовое меню бота

<img src="assets/start.jpg" width="300">

### Добавить игрока в базу данных
<div>
   <table>
      <td width="60%" valign="top">
         <h3 >До запуска игры необходимо наличие всех игроков в базе данных</h3>
         Используем команду <b>new_player</b><br> 
         Или кнопку "<b>🦈 Добавить игрока</b>" при старте бота<br>
         → Вводим ник игрока
      </td>
      <td width="40%">
         <img src="assets/new_player.jpg" height="200">
      </td>
   </table>
</div>

### Процесс игры
<div>
  <table>
    <tr>
      <td width="60%" valign="top" >
        <ol>
          <li>Запуск процесса игры</li>
          Выбор коэффициента одной фишки к рублю<br> 
          → Поэтапно добавить всех участвующих игроков<br>
          → Нажать готово и старт<br>
          <img src="assets/start_game.jpg" alt="Таблица учета игры">
          <li>Добавить игрока в игру</li>
          Нажимаем "Добавить игрока 🎣"<br>
          → Выбираем из списка нужного игрока<br>
          <img src="assets/add_player.jpg" alt="Таблица учета игры">
          <li>Докупить игрока</li>
          Нажимаем "Докупить игрока 💲"<br>
          → Выбираем из списка нужного игрока<br>
          → Выбираем количество фишек для докупа<br>
          <img src="assets/add_on.jpg" alt="Таблица учета игры">
          <li>Выход игрока из игры</li>
          Нажимаем "Выход игрока 🚪"<br>
          → Выбираем из списка нужного игрока→<br>
          → Отправляем количество фишек на выходе<br>
          <img src="assets/player_exit.jpg" alt="Таблица учета игры">
          <li>Окончание игры</li>
          Нажимаем "Закончить игру 🔚"<br>
          → Бот поэтапно запросит количество фишек у оставшихся игроков<br>
          → Отправляем количество фишек на выходе<br>
          <img src="assets/end_game.jpg" alt="Таблица учета игры">
        </ol>
      </td>
      <td width="40%" valign="top">
        <img src="assets/demo/start_game.gif" alt="Процесс игры" width="300">
      </td>
    </tr>
  </table>
</div>

### Статистика игроков 
Используем команду **statics**\
Или кнопку "**📋 Статистика игроков**" при старте бота
<img src="assets/statics.jpg" width="80%">\
*Планируется доработать статистику (добавить выбор общей статистики
или отдельно по игроку с результатами по каждой игре)*

### Результаты прошедших игр
Используем команду **past_games**\
Или кнопку "**📅 Прошлые игры**" при старте бота\
→ Выбираем из списка нужную нам игру
лориило
<img src="assets/demo/last_game.gif" alt="Посмотреть прошлую игру" width="300">
