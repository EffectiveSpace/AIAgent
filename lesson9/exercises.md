# Упражнения к Lesson 9: Фреймворки ИИ-агентов: LangChain, AutoGen и CrewAI

## Упражнение 1: Анализ архитектурных различий между фреймворками

### Цель
Понять, в каких случаях лучше использовать каждый из фреймворков.

### Задание
Для каждой из задач ниже определите, какой фреймворк (LangChain/LangGraph, CrewAI или AutoGen) будет наиболее подходящим и объясните, почему:

1. **Создание ассистента для поиска информации по внутренней документации компании**
2. **Команда для автоматического написания аналитических отчетов (исследователь, писатель, редактор)**
3. **Агент для решения сложной математической задачи с генерацией кода и его тестированием**
4. **Система для мониторинга и реагирования на упоминания бренда в социальных сетях**
5. **Исследовательский агент для генерации новых идей для продуктовой стратегии**

### Вопросы для анализа
1. Какие архитектурные особенности делают каждый фреймворк подходящим для определенных задач?
2. Какие компромиссы приходится делать при выборе фреймворка?
3. Можно ли комбинировать фреймворки в одном проекте?

## Упражнение 2: Создание простого агента на LangChain

### Цель
Практически реализовать агента с использованием LangChain.

### Задание
Создайте агента, который может:
- Искать информацию в интернете (используя duckduckgo-search или serpapi)
- Выполнять математические вычисления
- Сохранять результаты в файл

### Шаги реализации
1. Установите необходимые зависимости:
```bash
pip install langchain langchain-openai langchainhub duckduckgo-search
```

2. Реализуйте инструменты:
```python
from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """
    Выполняет поиск в интернете по заданному запросу.
    """
    from duckduckgo_search import DDGS
    results = []
    for r in DDGS().text(query, max_results=3):
        results.append(f"Title: {r['title']}\nSnippet: {r['body']}")
    return "\n\n".join(results)

@tool
def calculate(expression: str) -> str:
    """
    Выполняет математические вычисления.
    """
    try:
        # В реальном проекте используйте более безопасный парсер
        result = eval(expression)
        return str(result)
    except:
        return "Error in calculation"
```

3. Создайте агента и запустите его на задаче:
"Найди текущий курс доллара к рублю, умножь его на 100 и сохрани результат в файл 'currency_calculation.txt'"

### Вопросы для анализа
1. Как LangChain управляет циклом ReAct?
2. Какие преимущества дает использование готовых шаблонов промптов?
3. Как обрабатываются ошибки инструментов?

## Упражнение 3: Реализация мульти-агентной команды с CrewAI

### Цель
Создать структурированную команду агентов с четкими ролями.

### Задание
Создайте команду из 3 агентов для решения задачи: "Подготовить презентацию о перспективах ИИ в образовании на 2025-2030 гг."

#### Роли:
1. **Исследователь** (Researcher): Собирает информацию, анализирует тренды
2. **Аналитик** (Analyst): Анализирует gathered данные, выделяет ключевые тенденции
3. **Презентатор** (Presenter): Создает структурированную презентацию

### Требования
- Каждый агент должен иметь четко определенную роль, цель и backstory
- Задачи должны быть связаны между собой (результат одного становится входом для другого)
- Использовать подходящие инструменты для каждой роли

### Пример структуры
```python
from crewai import Agent, Task, Crew
from crewai_tools import tool

# Определите инструменты для каждого агента
@tool("internet_search")
def internet_search_tool(query: str) -> str:
    """Searches the internet for information."""
    # Реализация поиска
    pass

# Создайте агентов
researcher = Agent(
    role="Senior Educational Technology Researcher",
    goal="Find and analyze the latest trends and developments in AI for education",
    backstory="You are an expert in educational technology with 15 years of experience...",
    tools=[internet_search_tool]
)

# Создайте задачи
research_task = Task(
    description="Research the current state and future trends of AI in education for 2025-2030",
    expected_output="Detailed report with key findings and trends",
    agent=researcher
)

# Создайте команду и запустите
crew = Crew(
    agents=[researcher, analyst, presenter],
    tasks=[research_task, analysis_task, presentation_task],
    verbose=2
)
```

### Вопросы для анализа
1. Как происходит передача данных между агентами?
2. Как обеспечивается согласованность результатов?
3. Какие проблемы могут возникнуть при масштабировании команды?

## Упражнение 4: Создание диалоговой системы с AutoGen

### Цель
Понять динамическое взаимодействие между агентами в AutoGen.

### Задание
Создайте систему из двух агентов:
- **User Proxy Agent**: Имитирует пользователя
- **Assistant Agent**: Помогает решать задачи

Реализуйте сценарий: пользователь хочет решить математическую задачу, но не знает, как её сформулировать. Агенты должны вести диалог, уточнить задачу и решить её.

### Требования
1. Использовать code execution capabilities
2. Реализовать обработку ошибок
3. Позволить агентам задавать уточняющие вопросы

### Пример реализации
```python
import autogen

config_list = [
    {
        "model": "gpt-4-turbo",
        "api_key": "YOUR_API_KEY"
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
}

# Создайте агентов
user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",  # Для автоматического режима
    max_consecutive_auto_reply=10,
    llm_config=llm_config,
    code_execution_config={"work_dir": "coding"}
)

assistant = autogen.AssistantAgent(
    name="MathAssistant",
    llm_config=llm_config,
    system_message="You are a helpful assistant for solving math problems."
)

# Запустите диалог
user_proxy.initiate_chat(
    assistant,
    message="Помоги мне решить задачу по алгебре, но я не помню, как она точно формулируется. Она была про какие-то x и y..."
)
```

### Анализ
1. Как происходит процесс уточнения задачи?
2. Какие преимущества дает диалоговая модель по сравнению с линейной?
3. В каких случаях диалоговая модель предпочтительнее?

## Упражнение 5: LangGraph - создание сложного рабочего процесса

### Цель
Использовать LangGraph для создания циклического агента с состоянием.

### Задание
Создайте агента, который:
1. Получает задачу от пользователя
2. Планирует действия
3. Выполняет действия
4. Оценивает результат
5. При необходимости корректирует план и повторяет

### Требования
- Использовать LangGraph для моделирования цикла
- Реализовать состояние (state) для отслеживания прогресса
- Добавить узлы для планирования, выполнения, оценки
- Использовать условные ребра для принятия решений

### Пример структуры
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class AgentState(TypedDict):
    task: str
    plan: List[str]
    executed_steps: List[str]
    current_step: int
    result: str
    need_correction: bool

def plan_step(state: AgentState):
    # Логика планирования
    pass

def execute_step(state: AgentState):
    # Логика выполнения шага
    pass

def evaluate_step(state: AgentState):
    # Логика оценки результата
    pass

def route_step(state: AgentState):
    # Маршрутизация к следующему узлу
    if state['need_correction']:
        return "plan_step"
    elif state['current_step'] >= len(state['plan']):
        return "finish"
    else:
        return "execute_step"

# Создание графа
workflow = StateGraph(AgentState)

# Добавление узлов
workflow.add_node("plan_step", plan_step)
workflow.add_node("execute_step", execute_step)
workflow.add_node("evaluate_step", evaluate_step)

# Добавление ребер
workflow.set_entry_point("plan_step")
workflow.add_conditional_edges(
    "evaluate_step",
    route_step,
    {
        "plan_step": "plan_step",
        "execute_step": "execute_step", 
        "finish": END
    }
)

app = workflow.compile()
```

### Вопросы
1. Как LangGraph упрощает реализацию циклических процессов?
2. Как управляется состояние агента?
3. В чем преимущества графовой архитектуры перед линейной?

## Упражнение 6: Сравнение производительности фреймворков

### Цель
Сравнить различные фреймворки по производительности и сложности.

### Задача
Реализуйте одну и ту же задачу (например, "анализ сайта конкурента") с использованием:
1. Чистого LangChain
2. CrewAI
3. AutoGen

### Метрики для сравнения
- Время выполнения
- Количество строк кода
- Читаемость и поддерживаемость
- Гибкость в изменении логики

### Тестовая задача
"Проанализировать главную страницу сайта крупного конкурента в вашей нише, извлечь информацию о продуктах и ценах, и сформировать сводку."

### Анализ
1. Какой фреймворк был самым быстрым для реализации?
2. Какой дал самый точный результат?
3. Какой будет проще масштабировать?

## Упражнение 7: Интеграция с внешними инструментами

### Цель
Научиться интегрировать сторонние API и инструменты в агентов.

### Задание
Создайте агента, который использует внешний API (например, GitHub API, Weather API или News API) как инструмент.

### Пример: GitHub-агент
Создайте агента, который может:
- Получать информацию о репозитории
- Искать открытые issue
- Анализировать активность в репозитории

### Реализация инструмента
```python
from langchain.tools import BaseTool
import requests

class GithubRepoInfoTool(BaseTool):
    name = "github_repo_info"
    description = "Get information about a GitHub repository"
    
    def _run(self, owner: str, repo: str):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return f"Name: {data['name']}\nDescription: {data['description']}\nStars: {data['stargazers_count']}"
        else:
            return "Repository not found"
    
    def _arun(self, owner: str, repo: str):
        raise NotImplementedError("Async not implemented")

# Использование в агенте
tools = [GithubRepoInfoTool()]
# ... остальная логика агента
```

### Вопросы
1. Как обеспечивается безопасность при работе с внешними API?
2. Как обрабатываются ошибки API?
3. Как кэшируются результаты для повышения эффективности?

## Упражнение 8: Обработка ошибок и отказоустойчивость

### Цель
Реализовать надежную систему обработки ошибок в агенте.

### Задание
Модифицируйте одного из агентов, созданного ранее, чтобы он:
1. Обнаруживал ошибки инструментов
2. Пытался исправить проблему (повторный вызов, альтернативный инструмент)
3. Сообщал о неустранимых ошибках

### Стратегии обработки ошибок
- Retry с экспоненциальной задержкой
- Использование резервных инструментов
- Перепланирование при сбоях
- Логирование и мониторинг

### Пример реализации
```python
import time
import random
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def robust_tool_call(tool_func, *args, **kwargs):
    """Обертка для надежного вызова инструмента."""
    return tool_func(*args, **kwargs)
```

### Вопросы для анализа
1. Какие типы ошибок наиболее распространены в агентских системах?
2. Как обеспечить "человека в цикле" при критических ошибках?
3. Какие метрики следует отслеживать для оценки надежности?

## Упражнение 9: Кастомизация и расширение фреймворков

### Цель
Научиться создавать кастомные компоненты для фреймворков.

### Задание
Создайте кастомный компонент для одного из фреймворков:
1. Кастомный инструмент с дополнительной логикой
2. Кастомный агент с уникальным поведением
3. Кастомный обработчик памяти

### Пример: Кастомный инструмент с кэшированием
```python
import hashlib
from datetime import datetime, timedelta
from langchain.tools import BaseTool

class CachedWebSearchTool(BaseTool):
    name = "cached_web_search"
    description = "Web search with caching to avoid repeated API calls"
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(minutes=30)
        super().__init__()
    
    def _run(self, query: str):
        cache_key = hashlib.md5(query.encode()).hexdigest()
        
        # Проверяем кэш
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                print("Результат взят из кэша")
                return cached_result
        
        # Выполняем реальный поиск
        result = self._perform_search(query)
        
        # Сохраняем в кэш
        self.cache[cache_key] = (result, datetime.now())
        return result
    
    def _perform_search(self, query: str) -> str:
        # Реализация поиска
        pass
```

### Вопросы
1. Какие компоненты чаще всего требуют кастомизации?
2. Как обеспечить совместимость кастомных компонентов с основным фреймворком?
3. Как тестировать кастомные компоненты?

## Упражнение 10: Производственный деплоймент

### Цель
Подготовить агента к работе в production среде.

### Задание
Создайте конфигурацию для запуска агента в виде сервиса с:
- Мониторингом и логированием
- Управлением API-ключами
- Обработкой параллельных запросов
- Ограничением по токенам/запросам

### Требования
- Использовать Docker для контейнеризации
- Реализовать REST API для взаимодействия с агентом
- Добавить систему аутентификации
- Создать систему отчетности об использовании

### Структура приложения
```
production_agent/
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── tools.py
│   └── api.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── config.yaml
```

### Вопросы для анализа
1. Какие особенности production-развертывания агентов?
2. Как обеспечить безопасность при работе с API?
3. Какие метрики мониторинга наиболее важны?

---

## Дополнительные задания для продвинутых

### Задание 11: Гибридная архитектура
Исследуйте возможность объединения нескольких фреймворков в одной системе. Создайте систему, где:
- LangChain используется для обработки данных
- CrewAI для управления командой агентов
- LangGraph для сложной логики принятия решений

### Задание 12: Адаптивное обучение
Реализуйте систему, в которой агент адаптируется к новым данным и улучшает свои стратегии на основе прошлого опыта.

---

После выполнения упражнений сравните подходы, используемые в разных фреймворках, и подумайте, как бы вы применили эти знания в реальных проектах ИИ-агентов. Оцените, какой фреймворк лучше подходит для ваших текущих и будущих задач.