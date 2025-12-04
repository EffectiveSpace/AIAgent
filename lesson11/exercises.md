# Упражнения к Lesson 11: Производительность и оптимизация ИИ-агентов

## Упражнение 1: Анализ стоимости и производительности агента

### Цель
Понять, как различные факторы влияют на стоимость и производительность ИИ-агента.

### Задание
Создайте простого агента, который выполняет задачу анализа текста, и проанализируйте его производительность по следующим метрикам:
- Время выполнения
- Количество вызовов LLM
- Количество токенов (входных и выходных)
- Стоимость по разным моделям

### Шаги
1. Создайте агента, который:
   - Принимает длинный текст (1000+ слов)
   - Анализирует его (находит ключевые темы, делает краткое содержание, выделяет эмоциональный тон)
   - Возвращает структурированный отчет

2. Измерьте:
   - Время выполнения (используйте `time.time()`)
   - Количество вызовов LLM
   - Использование токенов (через `tiktoken` или через объект ответа API)

3. Тестируйте на разных моделях:
   - GPT-3.5-Turbo (дешевая, быстрая)
   - GPT-4o (дорогая, мощная)
   - Claude 3 Sonnet (сбалансированная)

### Код-заготовка
```python
import time
import tiktoken
from openai import OpenAI

client = OpenAI()

def analyze_text_basic(text: str) -> str:
    """Базовая реализация анализа текста."""
    start_time = time.time()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Поменяйте модель для тестирования
        messages=[
            {"role": "system", "content": "Ты аналитик текстов. Сделай краткий анализ."},
            {"role": "user", "content": f"Проанализируй этот текст: {text}"}
        ]
    )
    
    execution_time = time.time() - start_time
    
    # Подсчет токенов
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    input_tokens = len(encoding.encode(text))
    output_tokens = len(encoding.encode(response.choices[0].message.content))
    
    return {
        "result": response.choices[0].message.content,
        "execution_time": execution_time,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens
    }

# Тестирование разных подходов
text_for_analysis = "Вставьте сюда длинный текст для анализа..."
basic_result = analyze_text_basic(text_for_analysis)
```

### Вопросы для анализа
1. Как различаются метрики между разными моделями?
2. Как соотносятся время выполнения и качество результата?
3. Какие факторы больше всего влияют на стоимость?

## Упражнение 2: Реализация кэширования на разных уровнях

### Цель
Практически реализовать несколько стратегий кэширования и сравнить их эффективность.

### Задание
Реализуйте 3 уровня кэширования для ИИ-агента:

1. **Кэш простых вызовов LLM** - кэширование по точному совпадению промпта
2. **Семантический кэш** - кэширование по сходству запросов
3. **Кэш инструментов** - кэширование результатов вызова инструментов

### Код-заготовка для точного кэширования
```python
import hashlib
from typing import Dict, Any
import pickle
import os

class ExactMatchCache:
    def __init__(self, cache_dir="./llm_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Создает уникальный ключ из промпта и модели."""
        key_string = f"{prompt}_{model}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> str:
        """Получает результат из кэша, если он существует."""
        key = self._get_cache_key(prompt, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, prompt: str, model: str, result: str):
        """Сохраняет результат в кэш."""
        key = self._get_cache_key(prompt, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

# Пример использования
cache = ExactMatchCache()
cache_result = cache.get("Какая цена на BTC?", "gpt-3.5-turbo")
if cache_result is None:
    # Выполнить вызов LLM
    result = call_llm("Какая цена на BTC?", "gpt-3.5-turbo")
    cache.set("Какая цена на BTC?", "gpt-3.5-turbo", result)
else:
    result = cache_result
```

### Задание: Реализовать семантический кэш
```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticCache:
    def __init__(self, similarity_threshold=0.9):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = similarity_threshold
        self.questions = []  # Хранит эмбеддинги вопросов
        self.responses = []  # Хранит ответы
    
    def add(self, question: str, response: str):
        """Добавляет новую пару вопрос-ответ в кэш."""
        question_embedding = self.model.encode([question])
        self.questions.append(question_embedding)
        self.responses.append(response)
    
    def find_similar(self, question: str) -> str:
        """Находит наиболее похожий вопрос и возвращает его ответ."""
        if not self.questions:
            return None
        
        question_embedding = self.model.encode([question])
        
        # Сравниваем с каждым вопросом в кэше
        similarities = []
        for cached_question_emb in self.questions:
            sim = cosine_similarity(question_embedding, cached_question_emb)[0][0]
            similarities.append(sim)
        
        # Находим максимальное сходство
        max_sim_idx = np.argmax(similarities)
        if similarities[max_sim_idx] >= self.similarity_threshold:
            return self.responses[max_sim_idx]  # Возвращаем похожий ответ
        else:
            return None  # Нет похожего вопроса
```

### Задание: Кэш инструментов
Создайте кэш для результатов вызова инструментов (например, веб-поиска):

```python
class ToolResultCache:
    def __init__(self, ttl_minutes=30):
        self.cache = {}
        self.ttl = ttl_minutes
    
    def get(self, tool_name: str, args: dict) -> Any:
        """Получает результат инструмента из кэша."""
        cache_key = self._make_key(tool_name, args)
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl * 60:
                return result
            else:
                del self.cache[cache_key]  # Удаляем просроченный кэш
        return None
    
    def set(self, tool_name: str, args: dict, result: Any):
        """Сохраняет результат инструмента в кэш."""
        cache_key = self._make_key(tool_name, args)
        self.cache[cache_key] = (result, time.time())
    
    def _make_key(self, tool_name: str, args: dict) -> str:
        """Создает уникальный ключ для кэша."""
        import json
        key_string = f"{tool_name}_{json.dumps(args, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
```

### Сравнение стратегий
Протестируйте все три стратегии на одинаковом наборе задач:
- Часто повторяющиеся вопросы
- Сlightly переформулированные вопросы
- Инструменты с медленным ответом (симуляция)

### Вопросы для анализа
1. Какая стратегия дает лучший коэффициент попадания в кэш?
2. Какие компромиссы между точностью и эффективностью?
3. Какие накладные расходы у каждой стратегии?

## Упражнение 3: Модель-маршрутизация

### Цель
Реализовать систему, которая автоматически выбирает подходящую модель для задачи.

### Задание
Создайте класс ModelRouter, который:
1. Определяет тип задачи (простая классификация, анализ, генерация, сложное планирование)
2. Выбирает наиболее подходящую (с учетом стоимости и производительности) модель
3. Выполняет задачу с выбранной моделью

### Типы задач для распознавания:
- **Simple Query**: Простой вопрос-ответ ("Кто президент РФ?")
- **Classification**: Классификация текста ("Положительный/отрицательный отзыв")
- **Analysis**: Анализ текста ("Какие проблемы в этом отчете?")
- **Generation**: Генерация текста ("Напиши статью о...")
- **Complex Planning**: Планирование ("Разработай стратегию на год...")

### Код-заготовка
```python
from enum import Enum
from openai import OpenAI

class TaskType(Enum):
    SIMPLE_QUERY = "simple_query"
    CLASSIFICATION = "classification"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    COMPLEX_PLANNING = "complex_planning"

class ModelRouter:
    def __init__(self):
        # Определите модели и их стоимости
        self.model_costs = {
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},  # за 1k токенов
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015}
        }
        
        self.client = OpenAI()
    
    def classify_task(self, user_input: str) -> TaskType:
        """Определяет тип задачи с помощью LLM."""
        # Реализуйте логику классификации задачи
        # Это может быть простой промпт к дешевой модели
        pass
    
    def select_model(self, task_type: TaskType) -> str:
        """Выбирает модель на основе типа задачи."""
        model_mapping = {
            TaskType.SIMPLE_QUERY: "gpt-3.5-turbo",
            TaskType.CLASSIFICATION: "claude-3-haiku", 
            TaskType.ANALYSIS: "claude-3-sonnet",
            TaskType.GENERATION: "gpt-4o",
            TaskType.COMPLEX_PLANNING: "gpt-4o"
        }
        return model_mapping[task_type]
    
    def execute_task(self, user_input: str) -> dict:
        """Выполняет задачу с оптимальной моделью."""
        task_type = self.classify_task(user_input)
        model = self.select_model(task_type)
        
        # Выполнить вызов LLM с выбранной моделью
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_input}]
        )
        
        return {
            "result": response.choices[0].message.content,
            "selected_model": model,
            "task_type": task_type.value,
            "cost_estimate": self.estimate_cost(user_input, response.choices[0].message.content, model)
        }
    
    def estimate_cost(self, input_text: str, output_text: str, model: str) -> float:
        """Оценивает стоимость вызова."""
        # Подсчитайте приблизительную стоимость на основе количества токенов
        pass
```

### Тестирование
Протестируйте роутер на 10-15 различных задачах и сравните:
- Выбранные модели
- Предполагаемые стоимости
- Качество ответов
- Время выполнения

### Вопросы анализа
1. Насколько точной была классификация задач?
2. Как изменяется стоимость в зависимости от типа задачи?
3. Какие типы задач hardest для классификации?
4. Как можно улучшить алгоритм выбора модели?

## Упражнение 4: Оптимизация промптов

### Цель
Понять, как структура и содержание промпта влияет на эффективность и стоимость.

### Задание
Для одной и той же задачи (например, "Проанализируй этот отчет: [длинный текст]") создайте 4 версии промпта:

1. **Длинный промпт** - с подробными инструкциями, несколькими примерами
2. **Краткий промпт** - только суть задачи
3. **Структурированный промпт** - с жесткой структурой ответа (JSON)
4. **Промпт с шаблоном** - с указанием формата и ключевых точек

### Метрики для сравнения
- Количество входных токенов (длина промпта)
- Количество выходных токенов (длина ответа)
- Время генерации
- Качество результата (по шкале 1-10, оценка человека)
- Соответствие формату

### Примеры промптов
```python
# 1. Длинный промпт
LONG_PROMPT = """
Ты - опытный бизнес-аналитик с более чем 10-летним стажем работы в ведущих консалтинговых компаниях...
(много текста о роли, целях, примерах)
"""

# 2. Краткий промпт  
SHORT_PROMPT = """
Проанализируй отчет. Найди основные моменты, проблемы и рекомендации.
"""

# 3. Структурированный промпт
STRUCTURED_PROMPT = """
Анализируй отчет. Ответь в формате JSON:
{
  "main_points": [...],
  "problems": [...],
  "recommendations": [...]
}
"""

# 4. Промпт с шаблоном
TEMPLATE_PROMPT = """
Проанализируй отчет.

Формат ответа:
1. Основные моменты:
2. Проблемы:
3. Рекомендации:

Текст отчета:
[вставка текста]
"""
```

### Инструмент для сравнения
Создайте табличный сравнитель:

| Промпт | Входные токены | Выходные токены | Время | Качество (1-10) | Соответствие |
|--------|----------------|-----------------|-------|-----------------|--------------|
| Длинный | ? | ? | ? | ? | ? |
| Краткий | ? | ? | ? | ? | ? |
| Структурированный | ? | ? | ? | ? | ? |
| С шаблоном | ? | ? | ? | ? | ? |

### Вопросы для анализа
1. Какой промпт дал лучшее соотношение стоимость/качество?
2. Как структурированный промпт повлиял на формат ответа?
3. Насколько длинные промпты влияют на стоимость?
4. Какие элементы промпта оказались "лишними"?

## Упражнение 5: Параллелизм в агентских системах

### Цель
Понять, как параллельное выполнение улучшает производительность.

### Задание
Создайте систему, которая:
1. Принимает 5 разных запросов от пользователей
2. Выполняет их **последовательно** - один за другим
3. Выполняет их **параллельно** - все одновременно
4. Сравнивает время выполнения и общую эффективность

### Реализация последовательной обработки
```python
import time

def sequential_processing(requests: list) -> list:
    """Обрабатывает запросы последовательно."""
    start_time = time.time()
    results = []
    
    for request in requests:
        # Симулируем вызов LLM (добавляем задержку)
        time.sleep(1)  # Имитация работы LLM
        result = f"Результат для запроса: {request}"
        results.append(result)
    
    total_time = time.time() - start_time
    return results, total_time
```

### Реализация параллельной обработки
```python
import asyncio

async def process_request_async(request: str) -> str:
    """Асинхронная обработка одного запроса."""
    await asyncio.sleep(1)  # Имитация работы LLM
    return f"Результат для запроса: {request}"

async def parallel_processing(requests: list) -> tuple:
    """Обрабатывает запросы параллельно."""
    start_time = time.time()
    
    tasks = [process_request_async(req) for req in requests]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    return results, total_time

# Тестирование
requests = ["Запрос 1", "Запрос 2", "Запрос 3", "Запрос 4", "Запрос 5"]

print("Последовательная обработка:")
seq_results, seq_time = sequential_processing(requests)
print(f"Время: {seq_time:.2f} сек")

print("\nПараллельная обработка:")
par_results, par_time = asyncio.run(parallel_processing(requests))
print(f"Время: {par_time:.2f} сек")
print(f"Ускорение: {seq_time / par_time:.2f}x")
```

### Расширенное задание
Реализуйте асинхронный агент, который может:
1. Получать несколько задач одновременно
2. Выполнять независимые инструменты параллельно
3. Объединять результаты в финальный ответ

### Вопросы для анализа
1. В чем разница между последовательным и параллельным выполнением?
2. Какие ограничения могут помешать полной параллелизации?
3. Как параллелизм влияет на использование API?
4. Могут ли все агентные задачи быть распараллелены?

## Упражнение 6: Управление контекстным окном

### Цель
Научиться эффективно управлять размером контекста.

### Задание
Создайте агента с "умным" управлением контекстом, который:
1. Отслеживает размер текущего контекста
2. Автоматически удаляет наименее релевантные сообщения при приближении к лимиту
3. Использует стратегии "сжатия" истории

### Основные стратегии
1. **Sliding Window**: Хранить только последние N сообщений
2. **Summary-based**: Регулярно суммировать старую историю
3. **Importance-based**: Оценивать важность сообщений и сохранять только важные

### Реализация
```python
class ContextManager:
    def __init__(self, max_tokens=120000):  # 120k из 128k для GPT-4o
        self.max_tokens = max_tokens
        self.messages = []
        self.token_counter = ...  # TikToken или аналог
    
    def add_message(self, role: str, content: str):
        """Добавляет сообщение в историю."""
        self.messages.append({"role": role, "content": content})
        self._enforce_limit()
    
    def _enforce_limit(self):
        """Проверяет лимит и при необходимости обрезает историю."""
        total_tokens = self._count_tokens()
        
        if total_tokens > self.max_tokens * 0.8:  # 80% от лимита
            # Применить стратегию обрезки
            self._apply_truncation_strategy()
    
    def _apply_truncation_strategy(self):
        """Применяет стратегию обрезки (реализуйте одну из):"""
        # 1. Удалить половину самых старых сообщений (sliding window)
        # 2. Суммировать старые сообщения (summary-based)
        # 3. Оценить важность и удалить неважные
        pass
    
    def _count_tokens(self) -> int:
        """Подсчитывает общее количество токенов в истории."""
        # Реализуйте подсчет токенов
        pass
    
    def get_context(self) -> list:
        """Возвращает оптимизированный контекст для передачи в LLM."""
        return self.messages
```

### Тестирование
1. Создайте длинную сессию с 50+ сообщениями
2. Примените разные стратегии обрезки
3. Оцените, как это влияет на:
   - Размер контекста
   - Скорость работы
   - Качество ответов

### Вопросы
1. Какая стратегия лучше сохраняет важную информацию?
2. Как обрезка влияет на понимание контекста?
3. Какие сообщения важнее всего сохранять?

## Упражнение 7: Мониторинг и профилирование

### Цель
Создать систему мониторинга для отслеживания производительности агентов.

### Задание
Разработайте систему метрик, которая отслеживает:
- Количество вызовов LLM
- Расход токенов по типам (вход/выход)
- Время выполнения задач
- Частоту ошибок
- Стоимость сессий

### Реализация
```python
from datetime import datetime
import json

class AgentMetrics:
    def __init__(self):
        self.session_start_time = datetime.now()
        self.llm_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.errors = 0
        self.tasks_completed = 0
        self.call_details = []
    
    def log_llm_call(self, model: str, input_tokens: int, output_tokens: int, duration: float):
        """Фиксирует вызов LLM."""
        self.llm_calls += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        call_record = {
            "timestamp": datetime.now(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration": duration
        }
        self.call_details.append(call_record)
    
    def log_error(self):
        """Фиксирует ошибку."""
        self.errors += 1
    
    def log_task_completion(self):
        """Фиксирует выполнение задачи."""
        self.tasks_completed += 1
    
    def calculate_cost(self, pricing_map: dict) -> float:
        """Рассчитывает приблизительную стоимость."""
        # pricing_map = {"gpt-4o": {"input": 0.005, "output": 0.015}, ...}
        total_cost = 0
        for call in self.call_details:
            model_prices = pricing_map.get(call["model"], {"input": 0, "output": 0})
            cost = (call["input_tokens"] * model_prices["input"] / 1000) + \
                   (call["output_tokens"] * model_prices["output"] / 1000)
            total_cost += cost
        return total_cost
    
    def get_report(self) -> dict:
        """Возвращает отчет о метриках."""
        return {
            "session_duration": (datetime.now() - self.session_start_time).seconds,
            "llm_calls": self.llm_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "errors": self.errors,
            "tasks_completed": self.tasks_completed,
            "error_rate": self.errors / max(self.llm_calls, 1),
            "average_tokens_per_call": (self.total_input_tokens + self.total_output_tokens) / max(self.llm_calls, 1)
        }

# Пример использования
metrics = AgentMetrics()

# В вашем агентском коде:
start_time = time.time()
try:
    response = llm_call(...)
    duration = time.time() - start_time
    
    # Подсчитать токены
    input_tokens = count_tokens(prompt)
    output_tokens = count_tokens(response)
    
    # Зафиксировать вызов
    metrics.log_llm_call("gpt-4o", input_tokens, output_tokens, duration)
except Exception as e:
    metrics.log_error()
```

### Вопросы для анализа
1. Какие метрики наиболее важны для оптимизации?
2. Как часто следует собирать метрики?
3. Как использовать метрики для улучшения агента?
4. Какие пороговые значения стоит установить для алертов?

## Упражнение 8: Интеграция оптимизаций в реального агента

### Цель
Объединить все изученные техники в одном агенте.

### Задание
Создайте комплексного агента, который использует:
- Модель-маршрутизацию
- Кэширование
- Параллельную обработку
- Управление контекстом
- Мониторинг производительности

### Структура агента
```python
class OptimizedAgent:
    def __init__(self):
        self.model_router = ModelRouter()
        self.cache = SemanticCache()
        self.context_manager = ContextManager()
        self.metrics = AgentMetrics()
        self.token_estimator = ...  # Подсчет токенов
    
    def run(self, goal: str):
        """Запускает оптимизированный цикл выполнения задачи."""
        # 1. Классифицировать задачу
        task_type = self.model_router.classify_task(goal)
        
        # 2. Проверить кэш
        cached_result = self.cache.find_similar(goal)
        if cached_result:
            self.metrics.log_cache_hit()
            return cached_result
        
        # 3. Выбрать модель
        model = self.model_router.select_model(task_type)
        
        # 4. Управление контекстом
        context = self.context_manager.get_context()
        
        # 5. Выполнить задачу
        start_time = time.time()
        response = self._execute_with_model(model, context, goal)
        duration = time.time() - start_time
        
        # 6. Залогировать метрики
        tokens_in = self.token_estimator.count(context + goal)
        tokens_out = self.token_estimator.count(response)
        self.metrics.log_llm_call(model, tokens_in, tokens_out, duration)
        
        # 7. Сохранить в кэш
        self.cache.add(goal, response)
        
        return response
```

### Тестирование
Протестируйте агента на различных сценариях:
- Простые вопросы (должны использовать кэш)
- Сложные аналитические задачи (должны использовать мощные модели)
- Повторяющиеся запросы (должны быть быстрыми за счет кэша)
- Длинные сессии (должны управлять контекстом)

### Анализ
1. Насколько эффективной оказалась каждая оптимизация?
2. Как они взаимодействуют между собой?
3. Какие компромиссы пришлось сделать?
4. Как улучшить интеграцию техник?

---

## Дополнительные задания для продвинутых

### Задание 9: Оптимизация с использованием LangChain
Используйте LangChain для создания оптимизированного агента с встроенными возможностями кэширования, управления цепочками и мониторинга.

### Задание 10: Сравнение с готовыми решениями
Сравните вашу оптимизацию с решениями от CrewAI, AutoGen и LangChain. Что делает лучше/эффективнее?

---

После выполнения упражнений вы получите практические навыки оптимизации ИИ-агентов, позволяющие создавать эффективные, масштабируемые и экономически целесообразные системы.