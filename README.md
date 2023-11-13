# SMART BLOGGING PLATFORM | AI Squad


## Менеджер пакетів

Будемо використовувати `poetry`. Це допоможе відслідковувати залежності та дасть змогу всім членам команди користуватись однаковими версіями бібліотек.

Після клонування репозиторію в папці проекту що встановити залежності які визначені у файлі `pyproject.toml` виконайте команду:

```
poetry update
```

Та ініціалізуйте віртуальне середовище:

```
poetry shell
```

Додавайте нові залежності за допомогою команди:

```
poetry add <dependency>
```

## Налаштування змінних середовища

Переіменуйте файл `.env.example` -> `.env` та зазначте власні дані.

Доступитись до даних можна:

```
from src.conf.config import settings

DATABASE_URL = settings.sqlalchemy_database_url
```

## Бази даних

Використовуємо ДБ `postgres`

Міграції будуть відбуватиь з `alembic`. Щодо них не заморочуйтесь, будуть сетапитись вже перед деплоєм. Під час розробки робіть як зручно.

В `src.database.db` є функція `create_db_and_tables` яка при виклику заселяє базу відповідно до визначени моделей.

> Застосунок працює з БД асинхронно тому використовуємо замість:
> - `Session` -> `AsyncSession`
> - `get_db` -> `get_async_db`

У робочій папці є файл `docker-compose.yml` можете його використовувати для запуску порібних контейнерів.


## Структура проекту
```
├── src
│   ├── api
│   ├── migrations (not implemented)
│   ├── conf
│   │   └── config.py
│   ├── database
│   │   └── models
│   ├── repository
│   ├── schemas
│   └── services
└── tests
    └── conftest.py
```

`api` - тут маю бути ендпоінти. Для окремої фічі створюється окремий файл.  
`migrations` - тут будуть зберігатись міграції БД   
`conf` - тут лежить файл з налаштуваннями змінних середовища    
`database` - тут лежать файл підключення до бази та моделі  
`database/models` - для окремих фіч створюєте окремі файли для моделей. Не забувайте імпортувати з `database/db` клас `Base`.   
`repository` - тут зберігаються функції для роботи з базою даних    
`schemas` - тут зберігаються моделі `pydantic`  
`services` - тут зберігаються утиліти які розширюють функціонал застосунку  
`tests` - тут лежать тести  

## Тестування та документування

Використовуємо `pytest`

Документуємо функції та класи у docstring у стилі Google за допомогою `sphinx`

[Trelent](https://marketplace.visualstudio.com/items?itemName=Trelent.trelent) - АІ помічник (розширення) для створення __docstring__.

> На початку __docstring__ ставте `\f` щоб вона не відображалсь в документації

Приклад:

```
def add(a: int, b: int) -> int:
    """
    Returns the sum of two integers.

    :param a: The first integer.
    :type a: int
    :param b: The second integer.
    :type b: int
    :return: The sum of a and b.
    :rtype: int
    """
    return a + b
```

## Форматування коду відповідно до PEP8

Встановіть наступні розширення:

1. [isort](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)
2. [black-formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter&ssr=false#review-details)
3. [flake8](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8)

Потрібно активувати __Workspace__ натиснуванши в правому кутку кнопку яка з'явиться у відкритому файлі `project_workspace.code-workspace`.

> Форматування буде відбуватись під час збереження змін 
> Не забуваємо що згідно PEP8 довжина стрічки має бути не більше 79 символів    

Приклад налаштувань для Workspace у VSCode:

```
settings:{
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,      
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        },
    },
        "isort.args": [
        "--profile",
        "black",
        "--src", "${workspaceFolder}", "-l", "99"
        ],
}
```


Для читабельності коду можна використовувати `Annotated` тип з бібліотеки `typing`

```
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_async_db

app = FastAPI()

# Asign annotated type to a variable
get_db = Annotated[AsyncSession, Depends(get_async_db)]


@app.get("/items/")
async def read_items(db: get_db): # use it as a regular type without defining dependencies
    return db.query().all()
```







