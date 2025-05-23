# Документация мультиагентной системы для недвижимости

## Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура системы](#архитектура-системы)
3. [Компоненты системы](#компоненты-системы)
   - [Агент сбора данных](#агент-сбора-данных)
   - [Агент продаж](#агент-продаж)
   - [База данных недвижимости](#база-данных-недвижимости)
   - [API](#api)
   - [Веб-интерфейс](#веб-интерфейс)
4. [Веб-скраперы](#веб-скраперы)
5. [Планировщик задач](#планировщик-задач)
6. [Развертывание](#развертывание)
   - [Локальное развертывание](#локальное-развертывание)
   - [Docker развертывание](#docker-развертывание)
7. [Конфигурация](#конфигурация)
8. [Примеры использования](#примеры-использования)

## Обзор проекта

Мультиагентная система для недвижимости представляет собой комплексное решение, состоящее из двух основных агентов:

1. **Агент сбора данных** - собирает информацию о недвижимости с различных веб-сайтов, обрабатывает и структурирует данные.
2. **Агент продаж** - взаимодействует с клиентами, понимает их потребности и подбирает подходящие объекты недвижимости из базы данных.

Система предоставляет веб-интерфейс для взаимодействия с пользователями и API для интеграции с другими сервисами.

## Архитектура системы

Система построена на модульной архитектуре, где каждый компонент выполняет определенную функцию:

```
┌─────────────────┐     ┌─────────────────┐
│  Веб-интерфейс  │◄────┤       API       │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Агент продаж   │◄────┤  База данных    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       │
         │               ┌───────▼────────┐
         │               │  Агент сбора   │
         │               │     данных     │
         │               └───────┬────────┘
         │                       │
         │                       │
         │               ┌───────▼────────┐
         └───────────────►  Веб-скраперы  │
                         └────────────────┘
```

## Компоненты системы

### Агент сбора данных

**Файл:** `real_estate_agents/data_collector/agent.py`

Агент сбора данных отвечает за:
- Извлечение структурированной информации из описаний недвижимости
- Управление веб-скраперами для сбора данных с различных сайтов
- Обработку и нормализацию данных перед сохранением в базу данных

Агент использует OpenAI API для анализа текстовых описаний и извлечения ключевых параметров недвижимости. В случае отсутствия действительного API-ключа, используется заглушка (mock-реализация).

**Пример использования:**

```python
from real_estate_agents.data_collector.agent import DataCollectionAgent

agent = DataCollectionAgent()
property_data = agent.process_property_description(
    "Роскошная квартира в центре города с 2 спальнями и 2 ванными комнатами. Площадь 120 кв.м."
)
```

### Агент продаж

**Файл:** `real_estate_agents/sales_agent/agent.py`

Агент продаж отвечает за:
- Взаимодействие с клиентами через чат-интерфейс
- Понимание требований клиента к недвижимости
- Поиск подходящих объектов в базе данных
- Предоставление рекомендаций и ответы на вопросы

Агент использует OpenAI API для обработки естественного языка и генерации ответов. В случае отсутствия действительного API-ключа, используется заглушка (mock-реализация).

**Пример использования:**

```python
from real_estate_agents.sales_agent.agent import SalesAgent

agent = SalesAgent()
response = agent.chat("Я ищу 2-комнатную квартиру в центре города")
```

### База данных недвижимости

**Файл:** `real_estate_agents/database/property_db.py`

База данных недвижимости отвечает за:
- Хранение информации о объектах недвижимости
- Поиск объектов по различным критериям
- Добавление новых объектов

База данных реализована как класс Python, который хранит данные в памяти и может сохранять/загружать их из JSON-файла.

**Пример использования:**

```python
from real_estate_agents.database.property_db import PropertyDatabase

db = PropertyDatabase()
properties = db.search(location="Москва", min_bedrooms=2)
```

### API

**Файл:** `real_estate_agents/api/routes.py`

API предоставляет следующие эндпоинты:
- `/query` - поиск объектов недвижимости по критериям
- `/chat` - взаимодействие с агентом продаж
- `/scrape` - запуск сбора данных с веб-сайтов

API реализовано с использованием FastAPI.

**Пример запроса к API:**

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"location": "Москва", "bedrooms": 2}'
```

### Веб-интерфейс

**Файл:** `static/index.html`

Веб-интерфейс предоставляет:
- Чат с агентом продаж
- Форму поиска недвижимости
- Отображение результатов поиска

Интерфейс реализован с использованием HTML, CSS и JavaScript.

## Веб-скраперы

**Директория:** `real_estate_agents/data_collector/scrapers/`

Система включает скраперы для следующих сайтов:
- DDProperty (`ddproperty_scraper.py`)
- M2Agent (`m2agent_scraper.py`)

Все скраперы наследуются от базового класса `BaseScraper` и реализуют метод `scrape()`.

**Пример использования скрапера:**

```python
from real_estate_agents.data_collector.scrapers.ddproperty_scraper import DDPropertyScraper

scraper = DDPropertyScraper()
properties = scraper.scrape(location="Bangkok", limit=10)
```

## Планировщик задач

**Файл:** `schedule_scraping.py`

Планировщик задач позволяет настроить регулярный сбор данных с веб-сайтов. По умолчанию сбор данных выполняется раз в день.

**Запуск планировщика:**

```bash
python schedule_scraping.py
```

## Развертывание

### Локальное развертывание

**Файл:** `run.sh`

Для локального запуска системы используйте скрипт `run.sh`:

```bash
./run.sh
```

Скрипт поддерживает следующие режимы:
- `app` - запуск только веб-приложения
- `scraper` - запуск только скрапера
- `both` - запуск и приложения, и скрапера (по умолчанию)

### Docker развертывание

**Файлы:** `Dockerfile`, `docker-compose.yml`, `docker-run.sh`

Для развертывания с использованием Docker:

```bash
./docker-run.sh
```

Docker-композиция включает два сервиса:
- `app` - веб-приложение
- `scraper` - сервис сбора данных

## Конфигурация

**Файл:** `.env`

Система настраивается через переменные окружения:

```
OPENAI_API_KEY=your_api_key_here
PORT=8000
DATA_DIR=./data
SCRAPING_INTERVAL=24  # часы
```

## Примеры использования

### Поиск недвижимости

1. Откройте веб-интерфейс по адресу `http://localhost:8000`
2. Заполните форму поиска (местоположение, количество спален и т.д.)
3. Нажмите кнопку "Поиск"

### Чат с агентом

1. Откройте веб-интерфейс по адресу `http://localhost:8000`
2. В поле чата введите запрос, например: "Я ищу 2-комнатную квартиру в центре города"
3. Агент ответит и предложит подходящие варианты

---

# Real Estate Multi-Agent System Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [System Components](#system-components)
   - [Data Collection Agent](#data-collection-agent)
   - [Sales Agent](#sales-agent)
   - [Property Database](#property-database)
   - [API](#api)
   - [Web Interface](#web-interface)
4. [Web Scrapers](#web-scrapers)
5. [Task Scheduler](#task-scheduler)
6. [Deployment](#deployment)
   - [Local Deployment](#local-deployment)
   - [Docker Deployment](#docker-deployment)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)

## Project Overview

The Real Estate Multi-Agent System is a comprehensive solution consisting of two main agents:

1. **Data Collection Agent** - collects information about properties from various websites, processes and structures the data.
2. **Sales Agent** - interacts with clients, understands their needs, and selects suitable properties from the database.

The system provides a web interface for user interaction and an API for integration with other services.

## System Architecture

The system is built on a modular architecture where each component performs a specific function:

```
┌─────────────────┐     ┌─────────────────┐
│  Web Interface  │◄────┤       API       │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Sales Agent   │◄────┤     Database    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       │
         │               ┌───────▼────────┐
         │               │ Data Collection │
         │               │     Agent      │
         │               └───────┬────────┘
         │                       │
         │                       │
         │               ┌───────▼────────┐
         └───────────────►  Web Scrapers  │
                         └────────────────┘
```

## System Components

### Data Collection Agent

**File:** `real_estate_agents/data_collector/agent.py`

The Data Collection Agent is responsible for:
- Extracting structured information from property descriptions
- Managing web scrapers to collect data from various websites
- Processing and normalizing data before saving to the database

The agent uses the OpenAI API to analyze text descriptions and extract key property parameters. If no valid API key is available, a mock implementation is used.

**Usage Example:**

```python
from real_estate_agents.data_collector.agent import DataCollectionAgent

agent = DataCollectionAgent()
property_data = agent.process_property_description(
    "Luxurious apartment in the city center with 2 bedrooms and 2 bathrooms. Area 120 sq.m."
)
```

### Sales Agent

**File:** `real_estate_agents/sales_agent/agent.py`

The Sales Agent is responsible for:
- Interacting with clients through a chat interface
- Understanding client requirements for properties
- Finding suitable properties in the database
- Providing recommendations and answering questions

The agent uses the OpenAI API for natural language processing and response generation. If no valid API key is available, a mock implementation is used.

**Usage Example:**

```python
from real_estate_agents.sales_agent.agent import SalesAgent

agent = SalesAgent()
response = agent.chat("I'm looking for a 2-bedroom apartment in the city center")
```

### Property Database

**File:** `real_estate_agents/database/property_db.py`

The Property Database is responsible for:
- Storing information about properties
- Searching for properties based on various criteria
- Adding new properties

The database is implemented as a Python class that stores data in memory and can save/load it from a JSON file.

**Usage Example:**

```python
from real_estate_agents.database.property_db import PropertyDatabase

db = PropertyDatabase()
properties = db.search(location="New York", min_bedrooms=2)
```

### API

**File:** `real_estate_agents/api/routes.py`

The API provides the following endpoints:
- `/query` - search for properties based on criteria
- `/chat` - interact with the sales agent
- `/scrape` - initiate data collection from websites

The API is implemented using FastAPI.

**Example API Request:**

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"location": "New York", "bedrooms": 2}'
```

### Web Interface

**File:** `static/index.html`

The Web Interface provides:
- Chat with the sales agent
- Property search form
- Display of search results

The interface is implemented using HTML, CSS, and JavaScript.

## Web Scrapers

**Directory:** `real_estate_agents/data_collector/scrapers/`

The system includes scrapers for the following websites:
- DDProperty (`ddproperty_scraper.py`)
- M2Agent (`m2agent_scraper.py`)

All scrapers inherit from the base class `BaseScraper` and implement the `scrape()` method.

**Scraper Usage Example:**

```python
from real_estate_agents.data_collector.scrapers.ddproperty_scraper import DDPropertyScraper

scraper = DDPropertyScraper()
properties = scraper.scrape(location="Bangkok", limit=10)
```

## Task Scheduler

**File:** `schedule_scraping.py`

The Task Scheduler allows you to set up regular data collection from websites. By default, data collection is performed once a day.

**Starting the Scheduler:**

```bash
python schedule_scraping.py
```

## Deployment

### Local Deployment

**File:** `run.sh`

For local system deployment, use the `run.sh` script:

```bash
./run.sh
```

The script supports the following modes:
- `app` - run only the web application
- `scraper` - run only the scraper
- `both` - run both the application and the scraper (default)

### Docker Deployment

**Files:** `Dockerfile`, `docker-compose.yml`, `docker-run.sh`

For deployment using Docker:

```bash
./docker-run.sh
```

The Docker composition includes two services:
- `app` - web application
- `scraper` - data collection service

## Configuration

**File:** `.env`

The system is configured through environment variables:

```
OPENAI_API_KEY=your_api_key_here
PORT=8000
DATA_DIR=./data
SCRAPING_INTERVAL=24  # hours
```

## Usage Examples

### Property Search

1. Open the web interface at `http://localhost:8000`
2. Fill out the search form (location, number of bedrooms, etc.)
3. Click the "Search" button

### Chat with the Agent

1. Open the web interface at `http://localhost:8000`
2. In the chat field, enter a query, for example: "I'm looking for a 2-bedroom apartment in the city center"
3. The agent will respond and suggest suitable options