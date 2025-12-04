# Упражнения к Lesson 13: Реальные кейсы ИИ-агентов

## Упражнение 1: Анализ реальных кейсов ИИ-агентов

### Цель
Понять, как ИИ-агенты применяются в реальных бизнес-сценариях.

### Задание
Исследуйте 3 реальных кейса использования ИИ-агентов в бизнесе (например, из публичных отчетов компаний или кейсов с конференций):
1. Автоматизация обслуживания клиентов
2. Анализ данных/финансовый анализ
3. Автоматизация разработки ПО

Для каждого кейса проанализируйте:
- Какую задачу решает агент
- Какие компоненты используются (LLM, инструменты, память)
- Какие метрики эффективности отслеживаются
- Какие ограничения и проблемы были решены

### Вопросы для анализа
1. Какой кейс показался вам наиболее интересным и почему?
2. Какие паттерны вы заметили в различных кейсах?
3. Какие риски были упомянуты в кейсах?

## Упражнение 2: Создание агента-исследователя рынка

### Цель
Создать функционального агента для анализа рынка с использованием всех изученных компонентов.

### Задание
Реализуйте агента, который:
- Принимает цель анализа рынка (например, "анализ рынка электромобилей в Европе 2025")
- Использует веб-поиск для сбора данных
- Применяет RAG для хранения и извлечения информации
- Генерирует структурированный отчет
- Предоставляет рекомендации

### Требования
- Использовать векторную базу данных (ChromaDB или другую)
- Реализовать систему инструментов
- Включить механизм планирования
- Обеспечить обработку ошибок
- Создать систему метрик

### Базовая структура
```python
# market_research_agent.py
from typing import Dict, List, Any
import json
from datetime import datetime

class MarketResearchAgent:
    def __init__(self, llm_client, vector_store):
        self.client = llm_client
        self.vector_store = vector_store
        self.tools = {
            "web_search": self.web_search,
            "analyze_data": self.analyze_data,
            "generate_report": self.generate_report
        }
        self.metrics = {
            "total_queries": 0,
            "successful_searches": 0,
            "reports_generated": 0,
            "total_tokens": 0
        }
    
    def web_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Выполняет веб-поиск и сохраняет результаты в векторную базу."""
        # Реализуйте вызов поискового API
        pass
    
    def analyze_data(self, data: List[Dict]) -> Dict[str, Any]:
        """Анализирует собранные данные и выделяет ключевые тенденции."""
        # Реализуйте анализ данных
        pass
    
    def generate_report(self, analysis: Dict, goal: str) -> str:
        """Генерирует финальный отчет."""
        # Реализуйте генерацию отчета
        pass
    
    def run_analysis(self, goal: str) -> str:
        """Запускает полный цикл анализа."""
        # 1. Планирование
        plan = self.create_analysis_plan(goal)
        
        # 2. Извлечение контекста
        context = self.retrieve_context(goal)
        
        # 3. Выполнение плана
        results = []
        for step in plan:
            result = self.execute_step(step, context)
            results.append(result)
        
        # 4. Генерация отчета
        report = self.generate_final_report(results, goal)
        
        # 5. Сохранение в память и обновление метрик
        self.save_to_memory(goal, report)
        self.update_metrics()
        
        return report

# Пример использования
# agent = MarketResearchAgent(client, vector_store)
# report = agent.run_analysis("Анализировать рынок ИИ-агентов в сфере финансов в 2025 году")
# print(report)
```

### Проверка результата
Запустите агента с несколькими разными целями анализа и оцените:
- Качество собранных данных
- Структурированность отчета
- Время выполнения
- Количество токенов использовано

## Упражнение 3: Агент-помощник разработчика

### Цель
Создать агента, который помогает разработчикам с задачами программирования.

### Задание
Реализуйте агента-помощника, который может:
- Читать и анализировать код
- Писать документацию
- Писать unit-тесты
- Исправлять ошибки
- Оптимизировать производительность

### Требования
- Поддержка работы с файлами
- Инструмент для выполнения кода (безопасно)
- Инструмент для поиска в документации
- Система проверки качества кода
- Память для хранения контекста проекта

### Пример сценариев
1. "Напиши юнит-тесты для функции calculate_distance в файле geo_utils.py"
2. "Объясни, как работает функция authenticate_user и добавь документацию"
3. "Оптимизируй функцию process_large_dataset для лучшей производительности"

### Код-заготовка
```python
# developer_agent.py
import ast
import inspect
import tempfile
import os

class DeveloperAssistantAgent:
    def __init__(self, llm_client, project_directory: str = "./project"):
        self.client = llm_client
        self.project_dir = project_directory
        self.tools = {
            "read_code": self.read_code_file,
            "write_code": self.write_code_file,
            "analyze_code": self.analyze_code_quality,
            "generate_tests": self.generate_unit_tests,
            "explain_code": self.explain_code_logic,
            "execute_code": self.execute_code_safely
        }
    
    def read_code_file(self, filepath: str) -> str:
        """Безопасно читает файл с исходным кодом."""
        full_path = os.path.join(self.project_dir, filepath)
        # Добавьте проверки безопасности
        pass
    
    def generate_unit_tests(self, code_snippet: str, function_name: str) -> str:
        """Генерирует unit-тесты для указанной функции."""
        prompt = f"""
        Ты — специалист по тестированию Python-кода.
        Напиши unit-тесты для следующей функции:
        
        ```python
        {code_snippet}
        ```
        
        Функция: {function_name}
        
        Учитывай следующие аспекты:
        1. Проверь нормальные сценарии использования
        2. Проверь крайние случаи
        3. Проверь обработку ошибок
        4. Используй библиотеку pytest
        
        Верни код тестов в формате Python.
        """
        # Вызов LLM для генерации тестов
        pass
    
    def explain_code_logic(self, code_snippet: str) -> str:
        """Объясняет логику работы кода."""
        # Реализуйте объяснение кода
        pass
    
    def execute_code_safely(self, code: str, inputs: List[Any] = None) -> Dict[str, Any]:
        """
        Безопасно выполняет Python-код в изолированной среде.
        Возвращает результаты выполнения и возможные ошибки.
        """
        # Используйте exec в изолированном пространстве имен
        # или внешнюю песочницу
        pass

# Тестирование
# dev_agent = DeveloperAssistantAgent(client, project_dir="./my_project")
# test_result = dev_agent.generate_unit_tests(
#     code_snippet=get_function_code("calculate_distance"),
#     function_name="calculate_distance"
# )
# print(test_result)
```

### Оценка
1. Насколько точно агент генерирует тесты?
2. Каково качество объяснений кода?
3. Безопасно ли выполнение кода?

## Упражнение 4: Агент для автоматизации бизнес-процессов

### Цель
Создать агента, который может автоматизировать рутинные бизнес-задачи.

### Задание
Разработайте агента, который:
- Получает задачу в естественной форме
- Планирует выполнение
- Использует инструменты для работы с электронной почтой, календарем, документами
- Выполняет комплексную задачу
- Генерирует отчет о выполнении

### Возможные задачи для агента:
1. "Организуй встречу с командой по проекту 'Альфа' на следующей неделе"
2. "Подготовь отчет по продажам за прошлый квартал и отправь его менеджерам"
3. "Найди информацию о конкуренте X и подготовь сводку для руководства"

### Требования
- Интеграция с Gmail/Outlook
- Интеграция с Google Calendar/Outlook Calendar
- Работа с Google Docs/Sheets или Excel
- Механизмы подтверждения человека для критических действий
- Система логирования действий

### Пример интеграции с Gmail
```python
# business_automation_agent.py
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class BusinessAutomationAgent:
    def __init__(self, llm_client, email_config, calendar_config):
        self.client = llm_client
        self.email_config = email_config
        self.calendar_config = calendar_config
        self.tools = {
            "send_email": self.send_email,
            "check_calendar": self.check_calendar_availability,
            "create_calendar_event": self.create_calendar_event,
            "read_document": self.read_google_doc,
            "write_document": self.write_google_doc,
            "search_emails": self.search_emails
        }
    
    def send_email(self, to: str, subject: str, body: str) -> str:
        """Отправляет email с проверкой и подтверждением."""
        # Обертка для отправки email с безопасностью
        pass
    
    def check_calendar_availability(self, person_emails: List[str], time_range: str) -> str:
        """Проверяет доступность участников для встречи."""
        # Интеграция с календарем
        pass
    
    def plan_business_task(self, goal: str) -> Dict[str, Any]:
        """Создает план выполнения бизнес-задачи."""
        planning_prompt = f"""
        Ты — бизнес-ассистент. Твоя задача — разбить бизнес-задачу на конкретные шаги.
        
        Задача: {goal}
        
        Создай план в формате JSON:
        {{
            "steps": [
                {{"order": 1, "action": "search_emails", "params": {{"query": "..."}}, "description": "..."}},
                {{"order": 2, "action": "check_calendar", "params": {{"person_emails": [], "time_range": "..."}}, "description": "..."}},
                ...
            ],
            "critical_confirmations": ["send_email", "delete_document"]  # Действия, требующие подтверждения
        }}
        """
        # Вызов LLM для планирования
        pass

# Пример задачи
# business_agent = BusinessAutomationAgent(client, email_cfg, calendar_cfg)
# plan = business_agent.plan_business_task("Организовать встречу с командой по проекту 'Альфа' на следующей неделе")
# result = business_agent.execute_plan(plan)
```

### Вопросы для анализа
1. Какие бизнес-процессы можно автоматизировать с помощью таких агентов?
2. Какие риски безопасности возникают при автоматизации с критическими инструментами?
3. Как обеспечить "человека в цикле" для контроля?

## Упражнение 5: Оптимизация производительности агента

### Цель
Применить техники оптимизации к реализованному агенту.

### Задание
Возьмите одного из созданных агентов и реализуйте следующие оптимизации:

1. **Кэширование результатов поиска**: Не выполнять повторный поиск для одинаковых запросов
2. **Оптимизация LLM выбора**: Использовать дешевые модели для простых задач и дорогие для сложных
3. **Параллельное выполнение независимых действий**: Выполнять несколько поисковых запросов одновременно
4. **Управление контекстным окном**: Ограничивать историю для снижения стоимости

### Пример реализации кэширования
```python
import hashlib
from functools import wraps

def cache_search_results(func):
    """Декоратор для кэширования результатов поиска."""
    cache = {}
    
    @wraps(func)
    def wrapper(query, *args, **kwargs):
        cache_key = hashlib.md5(query.encode()).hexdigest()
        
        if cache_key in cache:
            print(f"🔍 Результат взят из кэша для запроса: {query[:30]}...")
            return cache[cache_key]
        
        result = func(query, *args, **kwargs)
        cache[cache_key] = result
        print(f"💾 Результат закэширован для запроса: {query[:30]}...")
        return result
    
    return wrapper

@cache_search_results
def search_web(query: str) -> str:
    # Реализация поиска
    pass
```

### Модельный маршрутизатор
```python
class ModelRouter:
    def __init__(self):
        self.models = {
            "simple": "gpt-3.5-turbo",      # Дешевая, быстрая модель
            "complex": "gpt-4o",            # Дорогая, мощная модель
            "balanced": "claude-3-sonnet"   # Сбалансированная
        }
    
    def route_request(self, task_description: str) -> str:
        """Определяет, какую модель использовать для задачи."""
        # Простая классификация задачи
        simple_keywords = ["сколько", "что такое", "кто такой", "где", "когда"]
        complex_keywords = ["анализ", "сравнение", "стратегия", "планирование", "объяснить"]
        
        task_lower = task_description.lower()
        
        if any(kw in task_lower for kw in simple_keywords) and not any(kw in task_lower for kw in complex_keywords):
            return self.models["simple"]
        elif any(kw in task_lower for kw in complex_keywords):
            return self.models["complex"]
        else:
            return self.models["balanced"]
```

### Задание для анализа
1. Измерьте время выполнения и стоимость до и после оптимизаций
2. Сравните качество результата
3. Определите, какие оптимизации дали наибольший эффект

## Упражнение 6: Интеграция с реальными API

### Цель
Научиться интегрировать агентов с реальными внешними сервисами.

### Задание
Интегрируйте одного из агентов с реальными API:

1. **Поиск**: SerpAPI, Tavily, или другая поисковая система
2. **Хранилище**: Google Drive, Dropbox, или S3
3. **Коммуникация**: Gmail, Slack, или Discord
4. **База данных**: PostgreSQL, MongoDB, или другая

### Пример интеграции с Tavily
```python
import requests

class TavilySearchTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
    
    def search(self, query: str, max_results: int = 5) -> Dict:
        """
        Выполняет поиск через Tavily API.
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",  # Использовать расширенный поиск
            "include_answer": True,      # Включить краткий ответ
            "include_images": False,
            "include_raw_content": False
        }
        
        response = requests.post(self.base_url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Tavily API Error: {response.status_code}, {response.text}")

# Использование в агенте
# tavily_tool = TavilySearchTool(api_key="your-api-key")
# result = tavily_tool.search("рынок ИИ-агентов 2025")
```

### Вопросы для анализа
1. Какие проблемы безопасности возникают при интеграции с внешними API?
2. Как обрабатывать ошибки API?
3. Как управлять лимитами и скоростью вызовов?

## Упражнение 7: Создание системы мониторинга и аудита

### Цель
Реализовать систему отслеживания действий и эффективности агента.

### Задание
Создайте систему логирования и мониторинга для одного из ваших агентов:

1. **Логирование**: Записывать все действия агента (мысли, действия, наблюдения)
2. **Метрики**: Отслеживать количество вызовов LLM, токены, время выполнения
3. **Аудит безопасности**: Отслеживать попытки доступа к критическим ресурсам
4. **Отчеты**: Генерировать отчеты о производительности и использовании

### Код-заготовка
```python
import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class AgentLogEntry:
    """Запись лога агента."""
    timestamp: float
    session_id: str
    agent_id: str
    action_type: str  # "thought", "tool_call", "llm_call", "error"
    content: str
    metadata: Dict[str, Any]

class AgentMonitoringSystem:
    def __init__(self):
        self.logs: List[AgentLogEntry] = []
        self.metrics = {
            "total_sessions": 0,
            "total_llm_calls": 0,
            "total_tokens_used": 0,
            "average_response_time": 0.0,
            "success_rate": 0.0
        }
    
    def log_action(self, agent_id: str, session_id: str, action_type: str, 
                   content: str, metadata: Dict[str, Any] = None):
        """Логирует действие агента."""
        log_entry = AgentLogEntry(
            timestamp=time.time(),
            session_id=session_id,
            agent_id=agent_id,
            action_type=action_type,
            content=content,
            metadata=metadata or {}
        )
        self.logs.append(log_entry)
    
    def update_metrics(self, llm_call_time: float, tokens_used: int, success: bool):
        """Обновляет метрики производительности."""
        self.metrics["total_llm_calls"] += 1
        self.metrics["total_tokens_used"] += tokens_used
        self.metrics["average_response_time"] = \
            (self.metrics["average_response_time"] * (self.metrics["total_llm_calls"] - 1) + llm_call_time) / \
            self.metrics["total_llm_calls"]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Генерирует отчет о производительности."""
        return {
            "period": "last_24_hours",
            "metrics": self.metrics,
            "recent_logs": self.logs[-20:],  # Последние 20 записей
            "potential_issues": self.detect_anomalies()
        }
    
    def detect_anomalies(self) -> List[str]:
        """Обнаруживает аномалии в поведении агента."""
        anomalies = []
        # Пример: слишком много вызовов инструмента за короткое время
        recent_logs = [log for log in self.logs if time.time() - log.timestamp < 60]  # За последнюю минуту
        tool_calls = [log for log in recent_logs if log.action_type == "tool_call"]
        if len(tool_calls) > 10:
            anomalies.append(f"Подозрительная активность: {len(tool_calls)} вызовов инструментов за 1 минуту")
        return anomalies

# Интеграция в агента
# monitoring_system = AgentMonitoringSystem()
# monitoring_system.log_action(
#     agent_id="researcher_agent_v1", 
#     session_id="sess_12345", 
#     action_type="llm_call", 
#     content="Планирование исследования", 
#     metadata={"model": "gpt-4o", "tokens_in": 500, "tokens_out": 200}
# )
```

### Тестирование системы
Запустите агента с мониторингом и проанализируйте:
- Как часто происходят вызовы LLM?
- Как распределяются затраты по токенам?
- Есть ли аномальное поведение?
- Какова средняя продолжительность сессии?

## Упражнение 8: Оценка эффективности и ROI

### Цель
Понять, как измерять эффективность агентов и рассчитывать возврат инвестиций (ROI).

### Задание
Для одного из созданных агентов реализуйте систему оценки:

1. **Время выполнения**: Сколько времени занимает задача агента против человека?
2. **Качество результата**: Как оценить, насколько хорош результат?
3. **Стоимость**: Сколько стоило выполнение задачи (токены API)?
4. **ROI**: Сравните стоимость и эффективность с ручным выполнением

### Пример расчета ROI
```python
class AgentROICalculator:
    def __init__(self, human_hourly_rate: float = 50.0):
        self.human_hourly_rate = human_hourly_rate
    
    def calculate_roi(self, agent_time_hours: float, agent_cost_usd: float, 
                      human_time_hours: float, human_cost_usd: float) -> Dict[str, float]:
        """
        Рассчитывает ROI для использования агента вместо человека.
        """
        time_saved_hours = human_time_hours - agent_time_hours
        cost_saved_usd = human_cost_usd - agent_cost_usd
        
        roi_percentage = (cost_saved_usd / agent_cost_usd) * 100 if agent_cost_usd > 0 else 0
        productivity_gain = human_time_hours / agent_time_hours if agent_time_hours > 0 else 0
        
        return {
            "time_saved_hours": time_saved_hours,
            "cost_saved_usd": cost_saved_usd,
            "roi_percentage": round(roi_percentage, 2),
            "productivity_gain_factor": round(productivity_gain, 2),
            "break_even_tasks": agent_cost_usd / (human_hourly_rate / 60)  # Задач через сколько окупится
        }

# Пример использования
# roi_calc = AgentROICalculator(human_hourly_rate=75.0)  # $75/час для специалиста
# 
# # Предположим:
# # Человек тратит 4 часа на задачу (=$300)
# # Агент тратит 0.1 часа и $0.50 на API
# results = roi_calc.calculate_roi(
#     agent_time_hours=0.1,
#     agent_cost_usd=0.50,
#     human_time_hours=4.0,
#     human_cost_usd=300.0
# )
# print(f"ROI: {results['roi_percentage']}%")
# print(f"Экономия времени: {results['time_saved_hours']} часов")
```

### Задание
1. Рассчитайте ROI для одного из ваших агентов
2. Оцените, при каком объеме использования агент окупится
3. Оцените, как ROI изменяется при увеличении сложности задачи

### Вопросы для анализа
1. При каких условиях использование агентов экономически оправдано?
2. Какие задачи лучше автоматизировать в первую очередь?
3. Какие скрытые затраты могут возникнуть при использовании агентов?

## Упражнение 9: Безопасность и этика в производственных агентах

### Цель
Практически реализовать меры безопасности и этические практики.

### Задание
Для одного из ваших агентов добавьте:

1. **Систему разрешений**: Ограничьте доступ к определенным инструментам
2. **Валидацию ввода**: Проверьте входные данные на безопасность
3. **Механизмы отключения**: Добавьте "стоп-слова" и ограничения
4. **Контроль приватности**: Обеспечьте защиту конфиденциальных данных

### Пример системы контроля
```python
class SafetyControlSystem:
    def __init__(self):
        self.forbidden_words = ["rm -rf", "delete", "password", "secret"]
        self.privileged_actions = ["delete_file", "send_email", "execute_code"]
        self.max_tool_calls_per_minute = 10
        self.action_count = {}
        self.last_reset_time = time.time()
    
    def check_input_safety(self, text: str) -> Dict[str, Any]:
        """Проверяет текст на наличие потенциально опасного содержимого."""
        violations = []
        
        for forbidden_word in self.forbidden_words:
            if forbidden_word.lower() in text.lower():
                violations.append(f"Обнаружено запрещенное словосочетание: {forbidden_word}")
        
        # Проверка на потенциально вредоносный код
        dangerous_patterns = [
            r"import\s+os", r"import\s+subprocess", r"__import__", r"exec\s*\("
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Обнаружен потенциально опасный паттерн: {pattern}")
        
        return {
            "is_safe": len(violations) == 0,
            "violations": violations
        }
    
    def check_action_permission(self, agent_role: str, tool_name: str) -> bool:
        """Проверяет, имеет ли агент с указанной ролью право выполнить действие."""
        # Реализуйте систему ролей и разрешений
        privileged_agents = ["admin", "system"]
        
        if tool_name in self.privileged_actions and agent_role not in privileged_agents:
            return False
        return True
    
    def check_rate_limit(self, agent_id: str) -> bool:
        """Проверяет лимит по частоте вызовов инструментов."""
        current_time = time.time()
        
        # Сброс счетчика каждую минуту
        if current_time - self.last_reset_time > 60:
            self.action_count = {}
            self.last_reset_time = current_time
        
        if agent_id not in self.action_count:
            self.action_count[agent_id] = 0
        
        self.action_count[agent_id] += 1
        
        if self.action_count[agent_id] > self.max_tool_calls_per_minute:
            return False  # Превышено количество вызовов
        
        return True

# Интеграция в агента
# safety_system = SafetyControlSystem()
# 
# # Перед выполнением действия
# input_check = safety_system.check_input_safety(user_input)
# if not input_check["is_safe"]:
#     raise ValueError(f"Ввод содержит нарушения: {input_check['violations']}")
# 
# if not safety_system.check_action_permission(agent_role, tool_name):
#     raise PermissionError(f"Агенту с ролью {agent_role} запрещено выполнять {tool_name}")
```

### Вопросы для обсуждения
1. Какие меры безопасности наиболее важны для вашей области применения?
2. Как можно автоматизировать проверку этичности решений агента?
3. Какие компромиссы между безопасностью и функциональностью пришлось сделать?

## Упражнение 10: Итоговый проект - Создание комплексного агента

### Цель
Применить все изученные концепции в одном комплексном агенте.

### Задание
Создайте полнофункционального агента для решения сложной, многошаговой задачи. Агент должен включать:

- **Память** (и краткосрочную, и долгосрочную)
- **Инструменты** (минимум 5 различных)
- **Планирование** (автоматическая декомпозиция задач)
- **Обработку ошибок** и самокоррекцию
- **Механизмы безопасности**
- **Систему мониторинга**
- **Оптимизацию** (маршрутизация моделей, кэширование)

### Пример задачи
Создайте агента-аналитика для стартапа, который:
1. Получает запрос: "Проанализировать конкурентов в сфере генеративного ИИ для бизнеса"
2. Планирует исследование
3. Ищет информацию о 5-7 ключевых игроках
4. Сравнивает их продукты по 10 критериям
5. Идентифицирует рыночные пробелы
6. Формирует рекомендации для собственной стратегии
7. Сохраняет результаты в документ

### Требования к проекту
1. Агент должен быть масштабируемым
2. Код должен быть документирован
3. Должны быть реализованы все основные компоненты агента
4. Должна быть система тестирования
5. Должна быть оценка эффективности

### Структура проекта
```
competitive_analyst_agent/
├── main.py                 # Входная точка
├── agent.py               # Основная логика агента
├── tools/                 # Модули инструментов
│   ├── web_search.py
│   ├── doc_writer.py
│   ├── competitor_analyzer.py
│   └── ...
├── memory/                # Модули памяти
│   ├── short_term.py
│   ├── long_term.py
│   └── ...
├── planning/              # Модули планирования
│   ├── task_decomposer.py
│   └── ...
├── security/              # Модули безопасности
│   ├── validator.py
│   └── ...
├── monitoring/            # Модули мониторинга
│   ├── metrics.py
│   └── ...
└── tests/                 # Тесты
    └── test_agent.py
```

### Финальный тест
Запустите агента с реальной задачей и оцените:
1. Полностью ли решена задача?
2. Насколько качественен результат?
3. Какова общая эффективность?
4. Какие проблемы были выявлены?
5. Как бы вы масштабировали этого агента?

---

После выполнения всех упражнений вы будете иметь полное понимание того, как создаются и развертываются реальные ИИ-агенты, способные решать сложные задачи в бизнесе и других областях.