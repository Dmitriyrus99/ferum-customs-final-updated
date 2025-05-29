# Ferum

**ferum** - Python project by Dmitriyrus99

Here you will find customized solutions and tools for automation, data analysis, and more, specifically tailored for an ERPNext instance. This app is named `ferum_customs`.

## Installation
```bash
# This assumes you have a Frappe Bench initialized.
# From your bench directory:
bench get-app https://github.com/Dmitriyrus99/ferum.git
bench --site [your-site-name] install-app ferum_customs
```

## Использование
Настройки применяются автоматически при установке и интегрируются в систему ERPNext. Это включает в себя пользовательские типы документов, скрипты и рабочие процессы.

## Структура проекта
Проект следует стандартной структуре приложения Frappe:
- `ferum_customs/` - Основной каталог приложения, содержащий:
  - `custom_logic/` - Хуки и бизнес-логика Python.
  - `doctype/` - Пользовательские определения DocType (JSON, Python, JS).
  - `fixtures/` - Данные по умолчанию, такие как роли, рабочие процессы.
  - `notifications/` - Настройки уведомлений.
  - `permissions/` - Пользовательская логика разрешений.
  - `patches/` - Исправления схемы базы данных.
  - `client_scripts/` - Клиентский JavaScript для DocTypes.
  - `hooks.py` - Подключает пользовательскую логику к событиям DocType и определяет конфигурации приложения.
  - `requirements.txt` - Зависимости пакета Python для этого приложения.
  - `setup.py` - Информация о настройке пакета.
  - `tests/` - (В идеале) Модульные тесты для пользовательского приложения.
  - `README.md` - Этот файл описания.
  - `LICENSE` - Информация о лицензии (MIT).
- **Вклад**  
  Запросы на извлечение приветствуются! Открытые вопросы по ошибкам или предложениям.
- **Лицензия**  
  Этот проект лицензирован в соответствии с лицензией MIT — см. `LICENSE`.
