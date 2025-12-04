# Упражнения к Lesson 8: Планирование и автономия

## Упражнение 1: Анализ стратегий декомпозиции задач

### Цель
Понять, как разные подходы к декомпозиции влияют на эффективность агента.

### Задание
Рассмотрите задачу: "Написать статью о плюсах и минусах разных фреймворков для ИИ-агентов".

Реализуйте для нее две разные стратегии декомпозиции:

1. **Линейная стратегия (Chain-of-Thought)**: Последовательные шаги
2. **Ветвящаяся стратегия (Tree-of-Thought)**: Разные варианты подходов

### Шаг 1: Линейная декомпозиция
Разбейте задачу на 5-7 последовательных шагов.

Пример:
```
Шаг 1: Найти список популярных фреймворков
Шаг 2: Изучить плюсы каждого фреймворка
Шаг 3: Изучить минусы каждого фреймворка
...
```

### Шаг 2: Ветвящаяся декомпозиция
Определите ключевые точки ветвления, где нужно выбрать между разными подходами.

Пример:
```
Цель: Написать статью
Вариант 1: Сравнительный обзор (LangChain vs AutoGen vs CrewAI)
Вариант 2: Рекомендации по выбору (в зависимости от задачи)
Вариант 3: История развития (как развивались фреймворки)
```

### Вопросы для анализа
1. В каких случаях линейный подход эффективнее?
2. Когда лучше использовать ветвящуюся стратегию?
3. Какие задачи сложнее декомпозировать?

## Упражнение 2: Реализация цикла ReAct с логированием

### Цель
Практически реализовать цикл ReAct и добавить механизм логирования для отладки.

### Задание
Создайте класс `ReActAgent`, который реализует цикл "Мысль-Действие-Наблюдение" с подробным логированием всех шагов.

### Требования
1. Сохранять каждую итерацию (thought, action, observation) в лог
2. Возможность восстановления состояния из лога
3. Механизм остановки при достижении цели или превышении лимита итераций
4. Обработка ошибок инструментов

### Пример структуры
```python
import json
from datetime import datetime
from typing import Dict, Any, List

class ReActStep:
    def __init__(self, thought: str, action: Dict[str, Any], observation: str):
        self.timestamp = datetime.now()
        self.thought = thought
        self.action = action
        self.observation = observation

class ReActAgent:
    def __init__(self, goal: str, tools: Dict[str, callable], max_iterations: int = 10):
        self.goal = goal
        self.tools = tools
        self.max_iterations = max_iterations
        self.log: List[ReActStep] = []
        self.current_iteration = 0
    
    def think(self) -> str:
        """Генерирует мысль для следующего шага."""
        # Реализуйте логику генерации мысли
        pass
    
    def act(self, action: Dict[str, Any]) -> str:
        """Выполняет действие и возвращает результат."""
        # Реализуйте вызов инструмента
        pass
    
    def observe(self, result: str) -> str:
        """Обрабатывает результат действия."""
        # Здесь может быть логика анализа результата
        return result
    
    def run(self):
        """Запускает цикл ReAct."""
        for i in range(self.max_iterations):
            self.current_iteration = i
            
            # 1. Think
            thought = self.think()
            
            # 2. Act
            # Здесь получаем действие от LLM (в реальности)
            action = {"tool_name": "web_search", "args": {"query": "test"}}
            try:
                observation = self.act(action)
            except Exception as e:
                observation = f"Ошибка выполнения действия: {e}"
            
            # 3. Observe
            processed_obs = self.observe(observation)
            
            # 4. Log step
            step = ReActStep(thought, action, processed_obs)
            self.log.append(step)
            
            # 5. Check termination condition
            if self.is_goal_achieved():
                break
    
    def is_goal_achieved(self) -> bool:
        """Проверяет, достигнута ли цель."""
        # Реализуйте логику проверки достижения цели
        pass
    
    def get_execution_log(self) -> str:
        """Возвращает полный лог выполнения."""
        log_str = f"Лог выполнения для цели: {self.goal}\n"
        log_str += f"Всего итераций: {len(self.log)}\n\n"
        
        for i, step in enumerate(self.log):
            log_str += f"--- ИТЕРАЦИЯ {i+1} ---\n"
            log_str += f"Время: {step.timestamp}\n"
            log_str += f"Мысль: {step.thought}\n"
            log_str += f"Действие: {json.dumps(step.action, indent=2, ensure_ascii=False)}\n"
            log_str += f"Наблюдение: {step.observation}\n\n"
        
        return log_str
```

### Вопросы для анализа
1. Как логирование помогает в отладке?
2. Какие метрики вы бы добавили для анализа эффективности?
3. Как бы вы реализовали "откат" при ошибке?

## Упражнение 3: Планирование с перепланированием

### Цель
Реализовать систему планирования, которая может адаптировать план при возникновении ошибок.

### Задание
Создайте систему, которая:
1. Создает начальный план для выполнения задачи
2. Начинает выполнение шагов плана
3. При ошибке анализирует причину
4. Пересматривает и корректирует план
5. Продолжает выполнение с обновленным планом

### Пример задачи
"Подготовить отчет о ценах на серверы AWS за последние 3 месяца"
- План 1: Использовать AWS Pricing API
- Ошибка: API требует сложной аутентификации
- Коррекция: Использовать веб-скрапинг вместо API

### Задание
```python
class AdaptivePlanner:
    def __init__(self):
        self.original_plan = []
        self.current_plan = []
        self.executed_steps = []
        self.failed_steps = []
    
    def create_initial_plan(self, goal: str) -> List[Dict]:
        """Создает изначальный план."""
        # Реализуйте генерацию плана
        pass
    
    def execute_next_step(self):
        """Выполняет следующий шаг из плана."""
        if not self.current_plan:
            return "План завершен"
        
        step = self.current_plan[0]
        try:
            # Выполнить шаг
            result = self.execute_step(step)
            self.executed_steps.append({"step": step, "result": result})
            self.current_plan = self.current_plan[1:]  # Удаляем выполненный шаг
            return result
        except Exception as e:
            self.failed_steps.append({"step": step, "error": str(e)})
            self.replan_after_failure(step, e)
            return f"Ошибка: {e}. План скорректирован."
    
    def repian_after_failure(self, failed_step, error):
        """Анализирует ошибку и пересматривает план."""
        # Реализуйте логику перепланирования
        pass
    
    def execute_step(self, step: Dict) -> str:
        """Выполняет конкретный шаг."""
        # Здесь вызов соответствующего инструмента
        pass
```

### Вопросы для анализа
1. Какие стратегии перепланирования вы бы использовали?
2. Как оценить эффективность адаптации плана?
3. Какие типы ошибок можно автоматически исправить?

## Упражнение 4: Chain-of-Thought vs Tree-of-Thought сравнение

### Цель
Сравнить эффективность двух подходов для сложных задач.

### Задание
Реализуйте два агента, решающих одну и ту же сложную задачу (например, "Как оптимизировать бизнес-процесс в компании?") с использованием:

1. **Chain-of-Thought** агента с линейным мышлением
2. **Tree-of-Thought** агента с ветвящимся мышлением

### Задача для обоих агентов
"Предложить стратегию повышения клиентской лояльности для онлайн-магазина электроники."

### Реализация CoT агента
```python
class CoTAgent:
    def __init__(self, goal, tools):
        self.goal = goal
        self.tools = tools
        self.thought_history = []
    
    def generate_thought(self, context: str) -> str:
        """Генерирует одну мысль в цепочке."""
        # Реализуйте генерацию мысли
        pass
    
    def run(self):
        """Запускает выполнение с Chain-of-Thought."""
        current_context = self.goal
        for _ in range(5):  # Ограничиваем количество шагов
            thought = self.generate_thought(current_context)
            self.thought_history.append(thought)
            # Обновляем контекст для следующей мысли
            current_context += f"\nПредыдущая мысль: {thought}"
        
        return self.thought_history
```

### Реализация ToT агента (упрощенная)
```python
class ToTNode:
    def __init__(self, thought: str, parent=None):
        self.thought = thought
        self.parent = parent
        self.children = []
        self.value = 0  # Оценка качества мысли

class ToTAgent:
    def __init__(self, goal, tools):
        self.goal = goal
        self.tools = tools
        self.root = ToTNode("Начало решения")
    
    def generate_thoughts(self, context: str, num_branches: int = 3) -> List[str]:
        """Генерирует несколько возможных мыслей."""
        # Реализуйте генерацию нескольких мыслей
        pass
    
    def evaluate_thought(self, thought: str, context: str) -> float:
        """Оценивает качество мысли."""
        # Реализуйте оценку мысли
        pass
    
    def run(self):
        """Запускает выполнение с Tree-of-Thought."""
        queue = [self.root]
        max_depth = 3
        
        while queue:
            current_node = queue.pop(0)
            if hasattr(current_node, 'depth') and current_node.depth >= max_depth:
                continue
                
            # Генерируем потомков
            thoughts = self.generate_thoughts(str(current_node.thought))
            for thought in thoughts:
                child_node = ToTNode(thought, parent=current_node)
                child_node.value = self.evaluate_thought(thought, str(current_node.thought))
                child_node.depth = getattr(current_node, 'depth', 0) + 1
                current_node.children.append(child_node)
                queue.append(child_node)
        
        # Найти лучший путь
        return self.find_best_path()
    
    def find_best_path(self):
        """Находит путь с наивысшей общей оценкой."""
        # Реализуйте поиск лучшего пути
        pass
```

### Сравнение
1. Какой подход дал более комплексное решение?
2. Какой подход был быстрее?
3. В каких задачах эффективнее каждый подход?

## Упражнение 5: Обработка ошибок в реальном времени

### Цель
Реализовать системы обработки различных типов ошибок в агенте.

### Задание
Создайте агента с системой обработки следующих типов ошибок:
1. **Технические ошибки инструментов** (API недоступен, тайм-аут)
2. **Логические ошибки** (неправильный план, зацикливание)
3. **Галлюцинации** (выдуманные факты, неверные данные)

### Пример реализации
```python
from enum import Enum

class ErrorType(Enum):
    TECHNICAL = "technical"
    LOGICAL = "logical"
    HALLUCINATION = "hallucination"

class ErrorHandler:
    def __init__(self):
        self.error_handlers = {
            ErrorType.TECHNICAL: self.handle_technical_error,
            ErrorType.LOGICAL: self.handle_logical_error,
            ErrorType.HALLUCINATION: self.handle_hallucination
        }
    
    def handle_error(self, error_type: ErrorType, context: Dict) -> Dict:
        """Обрабатывает ошибку и возвращает рекомендации."""
        handler = self.error_handlers.get(error_type)
        if handler:
            return handler(context)
        return {"action": "unknown_error", "next_steps": []}
    
    def handle_technical_error(self, context: Dict) -> Dict:
        """Обработка технической ошибки."""
        return {
            "action": "retry_or_alternative",
            "alternative_tool": self.suggest_alternative_tool(context.get('failed_tool')),
            "retry_count": context.get('retry_count', 0) + 1
        }
    
    def handle_logical_error(self, context: Dict) -> Dict:
        """Обработка логической ошибки."""
        return {
            "action": "replan",
            "new_strategy": self.propose_new_strategy(context.get('failed_plan'))
        }
    
    def handle_hallucination(self, context: Dict) -> Dict:
        """Обработка галлюцинации."""
        return {
            "action": "verify_and_correct",
            "verification_sources": self.find_verification_sources(context.get('hallucinated_fact'))
        }
    
    def suggest_alternative_tool(self, failed_tool: str) -> str:
        """Предлагает альтернативный инструмент."""
        # Реализуйте логику поиска альтернативы
        pass
    
    def propose_new_strategy(self, failed_plan: List) -> List:
        """Предлагает новую стратегию."""
        # Реализуйте логику перепланирования
        pass
    
    def find_verification_sources(self, fact: str) -> List[str]:
        """Находит источники для проверки факта."""
        # Реализуйте поиск источников
        pass

class ResilientAgent:
    def __init__(self, goal, tools):
        self.goal = goal
        self.tools = tools
        self.error_handler = ErrorHandler()
        self.failure_history = []
    
    def safe_execute_action(self, action: Dict) -> str:
        """Безопасно выполняет действие с обработкой ошибок."""
        try:
            result = self.execute_action(action)
            return result
        except TechnicalError as e:
            context = {"failed_tool": action["tool_name"], "error": str(e)}
            recovery_plan = self.error_handler.handle_error(ErrorType.TECHNICAL, context)
            return self.apply_recovery_plan(recovery_plan)
        except LogicalError as e:
            context = {"failed_plan": self.current_plan, "error": str(e)}
            recovery_plan = self.error_handler.handle_error(ErrorType.LOGICAL, context)
            return self.apply_recovery_plan(recovery_plan)
    
    def apply_recovery_plan(self, plan: Dict) -> str:
        """Применяет план восстановления."""
        # Реализуйте применение плана восстановления
        pass
```

### Вопросы для анализа
1. Какие еще типы ошибок вы бы добавили?
2. Как автоматически обучать систему обработки ошибок?
3. Как оценить эффективность восстановления?

## Упражнение 6: Интеграция с системой долговременной памяти

### Цель
Объединить планирование с долговременной памятью (RAG).

### Задание
Создайте агента, который использует векторную базу данных для:
1. Извлечения релевантной информации для принятия решений
2. Хранения результатов выполнения задач
3. Обучения на прошлых ошибках

### Пример архитектуры
```
Планировщик -> (Цель) -> RAG (поиск контекста) -> Агент ReAct -> (результат) -> RAG (хранение)
```

### Задание
```python
class RAGAwareAgent:
    def __init__(self, goal, tools, vector_store):
        self.goal = goal
        self.tools = tools
        self.vector_store = vector_store  # Ваша векторная база (ChromaDB, FAISS и т.д.)
    
    def retrieve_context(self, query: str) -> List[str]:
        """Извлекает релевантный контекст из памяти."""
        # Реализуйте поиск в векторной базе
        pass
    
    def plan_with_context(self) -> List[Dict]:
        """Создает план с учетом извлеченного контекста."""
        context = self.retrieve_context(self.goal)
        # Используйте контекст для создания более информированного плана
        pass
    
    def store_result(self, goal: str, plan: List[Dict], result: str, success: bool):
        """Сохраняет результат выполнения в долговременной памяти."""
        # Реализуйте сохранение для последующего использования
        pass
    
    def run(self):
        """Основной цикл работы агента с использованием памяти."""
        plan = self.plan_with_context()
        # Выполнить план с агентом ReAct
        result = self.execute_plan(plan)
        
        # Сохранить результат в память
        success = self.evaluate_success(result)
        self.store_result(self.goal, plan, result, success)
        
        return result
```

### Вопросы для анализа
1. Как память влияет на эффективность планирования?
2. Какие типы информации полезно хранить?
3. Как избегать переобучения на прошлых ошибках?

## Упражнение 7: Сравнение с фреймворками

### Цель
Сравнить собственную реализацию с готовыми фреймворками.

### Задание
Реализуйте того же агента (из упражнения 6) с использованием LangChain и сравните:

1. Сложность реализации
2. Гибкость и настраиваемость
3. Возможности отладки и логирования
4. Производительность

### Задание
```python
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI

def compare_implementations():
    """Сравнивает собственную реализацию с LangChain."""
    
    # Собственная реализация
    custom_agent = RAGAwareAgent(...)
    
    # Реализация с LangChain
    tools = [
        Tool(
            name="web_search",
            func=lambda x: "...",
            description="Поиск в интернете"
        ),
        # Добавьте другие инструменты
    ]
    
    memory = ConversationBufferMemory(memory_key="chat_history")
    
    llm = OpenAI(temperature=0)
    langchain_agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, 
        verbose=True, 
        memory=memory
    )
    
    # Сравните результаты
    pass
```

### Вопросы для анализа
1. В каких случаях лучше использовать фреймворки?
2. Когда стоит реализовывать свои решения?
3. Какие компромиссы приходится делать?

## Упражнение 8: Производительность и оптимизация

### Цель
Оптимизировать агента для более эффективной работы.

### Задание
Реализуйте следующие оптимизации:

1. **Кэширование результатов инструментов**
2. **Параллельное выполнение независимых действий**
3. **Ранняя остановка при достижении цели**
4. **Адаптивное изменение стратегии в зависимости от сложности задачи**

### Задание
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools

class OptimizedAgent:
    def __init__(self, goal, tools):
        self.goal = goal
        self.tools = tools
        self.result_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def cached_tool_call(self, tool_name: str, args: Dict) -> str:
        """Вызов инструмента с кэшированием."""
        cache_key = f"{tool_name}:{hash(str(args))}"
        if cache_key in self.result_cache:
            print(f"Результат взят из кэша для {tool_name}")
            return self.result_cache[cache_key]
        
        result = self.tools[tool_name](**args)
        self.result_cache[cache_key] = result
        return result
    
    async def parallel_tool_calls(self, actions: List[Dict]) -> List[str]:
        """Асинхронный параллельный вызов нескольких инструментов."""
        loop = asyncio.get_event_loop()
        tasks = []
        
        for action in actions:
            task = loop.run_in_executor(
                self.executor,
                functools.partial(self.tools[action["tool_name"]], **action["args"])
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    def run_optimized(self):
        """Запуск оптимизированного агента."""
        # Реализуйте логику с оптимизациями
        pass
```

### Вопросы для анализа
1. Какие оптимизации дали наибольший выигрыш?
2. Как измерить производительность агента?
3. Какие компромиссы между скоростью и точностью?

---

## Дополнительные задания для продвинутых

### Задание 9: Многоуровневое планирование
Реализуйте систему планирования с разными уровнями абстракции (стратегический, тактический, операционный).

### Задание 10: Обучение с подкреплением
Исследуйте возможность использования RL для обучения агентов более эффективному планированию.

---

После выполнения упражнений сравните эффективность разных подходов к планированию и автономии, и подумайте, как бы вы применили эти знания в реальных проектах ИИ-агентов.