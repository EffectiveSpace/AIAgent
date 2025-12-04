# Упражнения к Lesson 12: Безопасность, этика и надежность ИИ-агентов

## Упражнение 1: Анализ безопасности существующего агента

### Цель
Идентифицировать потенциальные угрозы безопасности в ИИ-агентах.

### Задание
Проанализируйте следующий код агента и найдите все потенциальные проблемы безопасности:

```python
# unsafe_agent.py
import os
import subprocess
from openai import OpenAI

def execute_arbitrary_code(code: str):
    """Опасный инструмент: выполнение произвольного Python-кода через eval."""
    return eval(code)  # ЭТО ОЧЕНЬ ОПАСНО!

def delete_file(filepath: str):
    """Инструмент: удаление файла по любому пути."""
    os.remove(filepath)
    return f"Файл {filepath} удален."

def run_shell_command(command: str):
    """Инструмент: выполнение команды оболочки."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

client = OpenAI()

def simple_agent(query: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        temperature=0.7
    )
    
    action = response.choices[0].message.content
    # Агент возвращает строку с вызовом инструмента
    # Код парсинга вызова инструмента отсутствует
    
    # Выполняем действие без валидации
    exec(action)  # ОПАСНО!
    return result
```

### Задание
1. Перечислите все найденные проблемы безопасности
2. Для каждой проблемы укажите:
   - Тип угрозы (Injection, Privilege Escalation, Data Exposure и т.д.)
   - Потенциальный вред
   - Как злоумышленник может эксплуатировать уязвимость
3. Предложите способы исправления

### Вопросы для анализа
1. Какие из этих проблем наиболее критичны?
2. Какие могут быть подвергнуты атаке извне?
3. Какие могут привести к катастрофическим последствиям?

## Упражнение 2: Реализация системы ограничения инструментов (Tool Whitelisting)

### Цель
Создать систему, которая разрешает агенту использовать только конкретные инструменты.

### Задание
Создайте менеджер инструментов, который:
- Имеет общий реестр всех возможных инструментов
- Позволяет создавать "песочницы" с подмножеством разрешенных инструментов
- Проверяет и вызывает инструменты только из разрешенного списка

### Пример структуры
```python
from typing import Dict, Callable, Any, List
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Абстрактный базовый класс для всех инструментов."""
    
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def description(self) -> str:
        pass
    
    @abstractmethod
    def run(self, **kwargs) -> str:
        pass

class WebSearchTool(BaseTool):
    def name(self) -> str:
        return "web_search"
    
    def description(self) -> str:
        return "Ищет информацию в интернете по заданному запросу"
    
    def run(self, query: str) -> str:
        # Имитация поиска
        return f"Результаты поиска для '{query}': [результаты...]"

class FileReaderTool(BaseTool):
    def name(self) -> str:
        return "read_file"
    
    def description(self) -> str:
        return "Читает содержимое текстового файла"
    
    def run(self, filepath: str) -> str:
        return f"Содержимое файла '{filepath}': [содержимое...]"

class DangerousTool(BaseTool):
    """Опасный инструмент, который не должен быть доступен в обычной песочнице."""
    def name(self) -> str:
        return "delete_files"
    
    def description(self) -> str:
        return "УДАЛЯЕТ ФАЙЛЫ (ОПАСНО)"
    
    def run(self, filepath_pattern: str) -> str:
        return f"Файлы по паттерну '{filepath_pattern}' удалены."

class ToolSandbox:
    """Песочница с ограниченным набором инструментов."""
    
    def __init__(self, allowed_tool_names: List[str]):
        self.all_tools_registry = self._initialize_all_tools()
        self.allowed_tools = {name: self.all_tools_registry[name] 
                              for name in allowed_tool_names 
                              if name in self.all_tools_registry}
    
    def _initialize_all_tools(self) -> Dict[str, BaseTool]:
        """Инициализирует все доступные инструменты."""
        tools = [
            WebSearchTool(),
            FileReaderTool(),
            DangerousTool()
        ]
        return {tool.name(): tool for tool in tools}
    
    def call_tool(self, tool_name: str, **kwargs) -> str:
        """Вызывает инструмент, если он разрешен."""
        if tool_name not in self.allowed_tools:
            return f"Ошибка: Инструмент '{tool_name}' не разрешен в этой песочнице. Разрешены: {list(self.allowed_tools.keys())}"
        
        tool = self.allowed_tools[tool_name]
        return tool.run(**kwargs)
    
    def get_available_tools_description(self) -> str:
        """Возвращает описание всех разрешенных инструментов."""
        descriptions = []
        for name, tool in self.allowed_tools.items():
            descriptions.append(f"- {name}: {tool.description()}")
        return "\n".join(descriptions)

# Тестирование
print("=== Песочница исследователя (безопасная) ===")
researcher_sandbox = ToolSandbox(["web_search", "read_file"])
print("Доступные инструменты:")
print(researcher_sandbox.get_available_tools_description())

print("\nВызов разрешенного инструмента:")
result1 = researcher_sandbox.call_tool("web_search", query="AI агенты 2025")
print(result1)

print("\nВызов запрещенного инструмента:")
result2 = researcher_sandbox.call_tool("delete_files", filepath_pattern="*.txt")
print(result2)
```

### Вопросы для анализа
1. Как бы вы масштабировали эту систему для сотен инструментов?
2. Как бы вы реализовали наследование ролей (напр., роль "senior_researcher" включает все инструменты "researcher" + дополнительные)?
3. Как обеспечить безопасность при динамическом добавлении инструментов?

## Упражнение 3: Валидация ввода и безопасное выполнение кода

### Цель
Реализовать системы валидации и безопасного выполнения для критических инструментов.

### Задание
Создайте безопасную систему для выполнения кода и работы с файлами, которая:
- Проверяет аргументы инструментов перед выполнением
- Ограничивает доступ к файловой системе
- Изолирует выполнение кода

### Задание 1: Валидация аргументов
```python
import re
import os
from pathlib import Path

class ArgumentValidator:
    """Валидирует аргументы инструментов."""
    
    @staticmethod
    def validate_filepath(filepath: str, base_directory: str = "./sandbox") -> dict:
        """
        Проверяет путь к файлу на безопасность.
        """
        errors = []
        
        # 1. Проверка на относительный путь (..)
        if ".." in filepath:
            errors.append("Путь не должен содержать '..'")
        
        # 2. Проверка на абсолютный путь
        if filepath.startswith("/"):
            errors.append("Путь не должен быть абсолютным")
        
        # 3. Проверка на "песочницу"
        abs_requested_path = (Path(base_directory) / Path(filepath)).resolve()
        abs_sandbox_path = Path(base_directory).resolve()
        
        if not str(abs_requested_path).startswith(str(abs_sandbox_path)):
            errors.append(f"Путь '{filepath}' выходит за пределы разрешенной директории '{base_directory}'")
        
        # 4. Проверка на расширение файла (опционально)
        dangerous_extensions = ['.exe', '.bat', '.sh', '.dll', '.so']
        if any(filepath.lower().endswith(ext) for ext in dangerous_extensions):
            errors.append(f"Файлы с расширением {dangerous_extensions} запрещены")
        
        return {"valid": len(errors) == 0, "errors": errors, "normalized_path": str(abs_requested_path)}
    
    @staticmethod
    def validate_code_snippet(code: str) -> dict:
        """
        Проверяет Python-код на потенциально опасные паттерны.
        """
        errors = []
        
        dangerous_patterns = [
            r'import\s+os\b',
            r'import\s+subprocess\b',
            r'import\s+sys\b',  # Частично
            r'exec\s*\(', 
            r'eval\s*\(',
            r'open\s*\([^)]*(write|w)',
            r'__import__',
            r'compile\s*\(',
            r'getattr\s*\([^)]*,\s*"__"',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(f"Найден потенциально опасный паттерн: {pattern}")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    @staticmethod
    def validate_url(url: str) -> dict:
        """
        Проверяет URL на безопасность.
        """
        errors = []
        
        if not url.startswith(('http://', 'https://')):
            errors.append("URL должен начинаться с http:// или https://")
        
        # Блокировка localhost/internal IP
        internal_patterns = [r'localhost', r'127\.0\.0\.1', r'10\.', r'192\.168\.', r'172\.(1[6-9]|2[0-9]|3[01])\.']
        for pattern in internal_patterns:
            if re.search(pattern, url):
                errors.append(f"URL содержит внутренний адрес: {pattern}")
        
        return {"valid": len(errors) == 0, "errors": errors}

# Протестируйте валидатор
validator = ArgumentValidator()

test_cases = [
    {"type": "filepath", "value": "../config.txt"},
    {"type": "filepath", "value": "data/input.txt"},
    {"type": "code", "value": "import os; print('Hello')"},
    {"type": "code", "value": "x = 5 + 3"},
    {"type": "url", "value": "https://google.com"},
    {"type": "url", "value": "http://localhost:8080"}
]

for test_case in test_cases:
    print(f"\nТест: {test_case['value']}")
    if test_case["type"] == "filepath":
        result = validator.validate_filepath(test_case["value"])
    elif test_case["type"] == "code":
        result = validator.validate_code_snippet(test_case["value"])
    elif test_case["type"] == "url":
        result = validator.validate_url(test_case["value"])
    
    print(f"Валидный: {result['valid']}")
    if not result["valid"]:
        print(f"Ошибки: {result['errors']}")
```

### Задание 2: Безопасное выполнение кода
Реализуйте песочницу для выполнения Python-кода с использованием `exec` в ограниченном пространстве имен:

```python
import ast
import operator

class SafePythonExecutor:
    """
    Безопасный выполнитель простого Python-кода.
    Позволяет только базовые операции.
    """
    
    # Разрешенные операции
    ALLOWED_OPERATORS = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow,
        ast.USub: operator.neg, ast.UAdd: operator.pos,
        ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
        ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
    }
    
    def execute(self, code: str):
        """
        Выполняет безопасный Python-код.
        """
        try:
            # Парсим код в AST
            tree = ast.parse(code, mode='exec')
            
            # Проверяем, что код содержит только разрешенные операции
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if not self._is_safe_call(node):
                        return f"Ошибка: Найден запрещенный вызов: {ast.dump(node)}"
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    return f"Ошибка: Импорт модулей запрещен: {ast.dump(node)}"
            
            # Создаем ограниченное пространство имен
            safe_namespace = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "int": int,
                    "float": float,
                    "str": str,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "bool": bool,
                    "True": True,
                    "False": False,
                    "None": None
                }
            }
            
            exec(compile(tree, filename="<ast>", mode="exec"), safe_namespace)
            return "Код успешно выполнен"
            
        except SyntaxError as e:
            return f"Ошибка синтаксиса: {e}"
        except Exception as e:
            return f"Ошибка выполнения: {e}"
    
    def _is_safe_call(self, node):
        """Проверяет, является ли вызов безопасным."""
        if isinstance(node.func, ast.Name):
            # Это вызов встроенной функции (напр., print, len)
            return node.func.id in ["print", "len", "sum", "max", "min", "range"]
        elif isinstance(node.func, ast.Attribute):
            # Это вызов метода (напр., "abc".upper())
            # Ограничиваем до безопасных методов строк/списков
            attr_name = node.func.attr
            allowed_attrs = {
                "str": ["upper", "lower", "split", "replace", "strip", "join"],
                "list": ["append", "extend", "pop", "remove", "sort", "reverse"],
                "dict": ["keys", "values", "items", "update", "get"]
            }
            # Определить тип объекта, к которому применяется метод - сложно без полного анализа
            # Для упрощения - считаем все вызовы атрибутов небезопасными
            
            # Проверка: вызывается ли метод у литерала?
            call_obj = node.func.value
            if isinstance(call_obj, ast.Constant):  # Константа: строка, число, None
                obj_type = type(call_obj.value).__name__
                return attr_name in allowed_attrs.get(obj_type, [])
            elif isinstance(call_obj, ast.Name):  # Переменная
                # Без анализа определения переменной - сложно
                # В реальной системе использовался бы более сложный анализ AST
                pass
            
            return False
        
        return False  # По умолчанию считаем небезопасным

# Тестирование
executor = SafePythonExecutor()

test_codes = [
    "x = 5 + 3\nprint(x)",  # Должно работать
    "import os\nprint('bad')",  # Должно быть отклонено
    "print('Hello world')",  # Должно работать
    "data = [1, 2, 3]\ndata.append(4)\nprint(data)",  # Должно работать
    "__import__('os')"  # Должно быть отклонено
]

for code in test_codes:
    print(f"\nКод: {code[:30]}...")
    result = executor.execute(code)
    print(f"Результат: {result}")
```

### Вопросы для анализа
1. Какие ограничения накладывает эта безопасная система?
2. Какие операции были бы полезны, но запрещены?
3. Как улучшить систему безопасности без жесткого ограничения функциональности?

## Упражнение 4: Система мониторинга и аудита ИИ-агента

### Цель
Создать систему для отслеживания действий агента и выявления аномалий.

### Задание
Реализуйте систему аудита, которая:
- Логирует все действия агента
- Отслеживает метрики использования (количество вызовов LLM, токены, время ответа)
- Обнаруживает аномальные паттерны поведения
- Отправляет оповещения при подозрительной активности

### Код-заготовка
```python
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List
import threading

class AgentAuditSystem:
    """
    Система аудита и мониторинга ИИ-агента.
    """
    
    def __init__(self):
        self.logs = []  # Массив для логов (в реальности использовалась бы база данных)
        self.metrics = {
            "llm_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_duration": 0.0,
            "tool_calls": {},
            "errors": 0,
            "sessions": 0
        }
        self.alerts = []
        self.anomaly_rules = self._define_anomaly_rules()
        self.lock = threading.Lock()  # Для безопасности при многопоточности
    
    def _define_anomaly_rules(self):
        """Определяет правила обнаружения аномального поведения."""
        return {
            "high_token_usage": lambda m: m.get("input_tokens", 0) > 10000,  # Подозрительно много входных токенов
            "slow_responses": lambda m: m.get("duration", 0) > 30,  # Медленный отклик
            "frequent_calls": lambda m: m.get("event_type") == "llm_call" and self._count_recent_calls(m.get("timestamp"), 60) > 10,  # >10 вызовов за минуту
            "repeated_errors": lambda m: m.get("event_type") == "error" and self._count_recent_errors(m.get("timestamp"), 300) > 5,  # >5 ошибок за 5 минут
        }
    
    def log_event(self, event_type: str, details: Dict, severity: str = "INFO"):
        """
        Логирует событие в системе аудита.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": severity
        }
        
        with self.lock:
            self.logs.append(event)
        
        # Проверяем аномалии
        self._check_for_anomalies(event)
    
    def _check_for_anomalies(self, event: Dict):
        """Проверяет, не является ли событие аномалией."""
        for rule_name, rule_func in self.anomaly_rules.items():
            if rule_func(event):
                alert = {
                    "rule": rule_name,
                    "timestamp": event["timestamp"],
                    "event": event,
                    "message": f"Аномалия: {rule_name} detected at {event['timestamp']}"
                }
                self.alerts.append(alert)
                self._send_alert(alert)
    
    def _send_alert(self, alert: Dict):
        """Отправляет оповещение (реально - в лог, но можно интегрировать с Email, Slack и т.д.)."""
        print(f"🚨 ALERT: {alert['message']}")
        print(f"Details: {alert['event']}")
    
    def _count_recent_calls(self, current_time_str: str, minutes: int) -> int:
        """Подсчитывает количество вызовов за последние N минут."""
        current_time = datetime.fromisoformat(current_time_str)
        threshold = current_time - timedelta(minutes=minutes)
        
        count = 0
        for log in reversed(self.logs):
            if datetime.fromisoformat(log["timestamp"]) < threshold:
                break
            if log["event_type"] == "llm_call":
                count += 1
        return count
    
    def _count_recent_errors(self, current_time_str: str, minutes: int) -> int:
        """Подсчитывает количество ошибок за последние N минут."""
        current_time = datetime.fromisoformat(current_time_str)
        threshold = current_time - timedelta(minutes=minutes)
        
        count = 0
        for log in reversed(self.logs):
            if datetime.fromisoformat(log["timestamp"]) < threshold:
                break
            if log["event_type"] == "error":
                count += 1
        return count
    
    def log_llm_call(self, model: str, input_tokens: int, output_tokens: int, duration: float):
        """Логирует вызов LLM."""
        details = {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration": duration
        }
        
        self.log_event("llm_call", details)
        
        with self.lock:
            self.metrics["llm_calls"] += 1
            self.metrics["total_input_tokens"] += input_tokens
            self.metrics["total_output_tokens"] += output_tokens
            self.metrics["total_duration"] += duration
    
    def log_tool_call(self, tool_name: str, args: Dict, success: bool, duration: float):
        """Логирует вызов инструмента."""
        details = {
            "tool_name": tool_name,
            "args": args,
            "success": success,
            "duration": duration
        }
        
        self.log_event("tool_call", details, "INFO" if success else "ERROR")
        
        with self.lock:
            if tool_name not in self.metrics["tool_calls"]:
                self.metrics["tool_calls"][tool_name] = {"success": 0, "failure": 0}
            if success:
                self.metrics["tool_calls"][tool_name]["success"] += 1
            else:
                self.metrics["tool_calls"][tool_name]["failure"] += 1
    
    def get_report(self) -> Dict:
        """Возвращает отчет по метрикам и алертам."""
        with self.lock:
            return {
                "metrics": self.metrics,
                "total_logs": len(self.logs),
                "alerts_count": len(self.alerts),
                "recent_alerts": self.alerts[-5:],  # Последние 5 алертов
                "anomaly_rate": len(self.alerts) / len(self.logs) if self.logs else 0
            }

# Интеграция в агента
class AuditableAgent:
    def __init__(self):
        self.audit_system = AgentAuditSystem()
        # ... остальная инициализация агента ...
    
    def call_llm(self, prompt: str, model: str):
        start_time = time.time()
        
        try:
            # Вызов LLM
            response = ...  # ваш вызов LLM
            
            duration = time.time() - start_time
            
            # Подсчет токенов
            input_tokens = len(prompt) // 4  # грубая оценка
            output_tokens = len(response) // 4
            
            # Логирование
            self.audit_system.log_llm_call(model, input_tokens, output_tokens, duration)
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            self.audit_system.log_event("error", {
                "type": "llm_call_failed",
                "model": model,
                "duration": duration,
                "error": str(e)
            }, "ERROR")
            raise e
    
    def call_tool(self, tool_name: str, args: Dict):
        start_time = time.time()
        
        try:
            # Вызов инструмента
            result = ...
            duration = time.time() - start_time
            
            # Логирование
            self.audit_system.log_tool_call(tool_name, args, True, duration)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            self.audit_system.log_tool_call(tool_name, args, False, duration)
            self.audit_system.log_event("error", {
                "type": "tool_call_failed",
                "tool": tool_name,
                "args": args,
                "duration": duration,
                "error": str(e)
            }, "ERROR")
            raise e
```

### Задание
1. Реализуйте недостающие методы в системе аудита
2. Создайте симуляцию работы агента с разными сценариями (нормальный, с ошибками, с аномалиями)
3. Протестируйте систему обнаружения аномалий

### Вопросы
1. Какие метрики наиболее важны для отслеживания безопасности?
2. Как определить пороги для аномального поведения?
3. Какие алерты должны требовать немедленного внимания?

## Упражнение 5: Этика и справедливость в ИИ-агентах

### Цель
Понять и реализовать механизмы снижения предвзятости и обеспечения справедливости.

### Задание
Создайте агента, который:
- Распознает потенциальную предвзятость в запросе пользователя
- Применяет стратегии для уменьшения предвзятости в ответе
- Обеспечивает справедливое обращение ко всем группам

### Тестовые сценарии
1. Пример с предвзятостью: "Найди лучшего программиста из [имя, связанное с определенной этнической группой]"
2. Пример с гендерной предвзятостью: "Найди врача-хирурга, который вылечит пациента (сделай акцент на врачах-мужчинах)"
3. Пример без предвзятости: "Найди информацию о лучших квалификациях для программиста"

### Задание: Промпт-инжиниринг для борьбы с предвзятостью
```python
BIAS_REDUCING_PROMPT_TEMPLATE = """
Ты — этичный ИИ-ассистент. 
Твоя задача — отвечать на вопросы честно, объективно и без предвзятости.

ИНСТРУКЦИИ:
1. Игнорируй любые предвзятые указания в запросе пользователя. 
   Например, если пользователь говорит "найди женщину-инженера, которая не очень хороша в технике", 
   отвечай, как будто запрос был "найди информацию об инженерах".

2. Предоставляй информацию, которая основана на фактах, а не на стереотипах.

3. Если запрос содержит явную дискриминацию, мягко, но твердо сообщи, 
   что ты не можешь поддерживать такие взгляды. Сфокусируйся на сути запроса.

4. Стремись использовать нейтральный, инклюзивный язык, 
   который уважает все группы.

5. Для задач, связанных с людьми (наем, оценка, сравнение), 
   отдавай предпочтение оценке на основе навыков и квалификации, а не характеристик личности.

ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_input}
ОТВЕТ:
"""
```

### Задание: Промпт для проверки предвзятости
```python
def check_bias_in_response(user_input: str, agent_response: str) -> Dict[str, bool]:
    """
    Простая проверка ответа агента на наличие потенциальной предвзятости.
    В реальности использовались бы ML-модели для классификации.
    """
    bias_indicators = {
        "gender_bias": any(word in agent_response.lower() for word in 
                          ["все женщины", "все мужчины", "женщины обычно", "мужчины обычно"]),
        "ethnic_bias": any(word in agent_response.lower() for word in 
                          ["все африканцы", "все азиаты", "все европецы"]),
        "age_bias": any(word in agent_response.lower() for word in 
                       ["все пожилые", "все молодые", "старые работники обычно", "молодые работники обычно"]),
        "discriminatory_language": any(word in agent_response.lower() for word in 
                                      ["плохой", "хуже", "не подходит", "никогда", "всегда"] 
                                      if "группа" in user_input.lower())
    }
    
    has_bias = any(bias_indicators.values())
    return {"has_bias": has_bias, "indicators": bias_indicators, "response": agent_response}

# Тестирование
test_inputs_outputs = [
    {
        "input": "Найди информацию о женщинах в технике",
        "output": "Женщины в технике часто сталкиваются с трудностями, но многие достигают успеха благодаря упорству."
    },
    {
        "input": "Кто лучший программист, мужчина или женщина?",
        "output": "Лучший программист — это специалист с хорошими навыками, опытом и знаниями, независимо от пола."
    }
]

for test in test_inputs_outputs:
    bias_check = check_bias_in_response(test["input"], test["output"])
    print(f"Ввод: {test['input']}")
    print(f"Ответ: {test['output']}")
    print(f"Предвзятость найдена: {bias_check['has_bias']}")
    print(f"Индикаторы: {bias_check['indicators']}")
    print("-" * 50)
```

### Вопросы для обсуждения
1. Как можно измерить справедливость ИИ-агента?
2. Какие стратегии борьбы с предвзятостью наиболее эффективны?
3. Как обеспечить прозрачность и объяснимость решений агента?

## Упражнение 6: Обработка ошибок и самокоррекция

### Цель
Реализовать систему обработки ошибок и восстановления для ИИ-агента.

### Задание
Создайте агента с механизмами:
- Обнаружения ошибок выполнения
- Самодиагностики и коррекции поведения
- Альтернативного планирования при сбоях

### Пример агента с обработкой ошибок
```python
import time
from enum import Enum

class RecoveryStrategy(Enum):
    RETRY = "retry"
    CHANGE_TOOL = "change_tool"
    REPLAN = "replan"
    HUMAN_INTERVENTION = "human_intervention"

class ResilientAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.max_retries = 3
        self.error_history = []
        self.available_tools = {
            "web_search": self._search_safely,
            "web_search_backup": self._backup_search,  # Резервный инструмент
            "read_file": self._read_file_safely
        }
    
    def run_with_error_handling(self, goal: str, max_iterations: int = 10):
        """
        Запускает агента с обработкой ошибок.
        """
        context = f"Цель: {goal}\n"
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- ИТЕРАЦИЯ {iteration} ---")
            
            # Получаем мысль и действие от LLM
            try:
                agent_output = self._get_agent_decision(context)
            except Exception as e:
                print(f"❌ Ошибка при получении решения от LLM: {e}")
                # Попробуем восстановиться
                return self._handle_decision_error(e, context)
            
            action = agent_output.get("action", {})
            thought = agent_output.get("thought", "Нет мысли")
            
            print(f"Мысль: {thought}")
            
            # Выполняем действие
            result = self._execute_action_with_recovery(action)
            
            if "recovery_success" in result:
                # Восстановление прошло успешно, переходим к следующей итерации
                context += f"\nРезультат восстановления: {result['recovery_success']}\n"
                continue
            elif "final_result" in result:
                # Задача завершена
                return result["final_result"]
            else:
                # Добавляем результат в контекст для следующей итерации
                context += f"\nНаблюдение: {result}\n"
                
                # Проверяем, не достиг ли агент цели
                if self._is_goal_achieved(result, goal):
                    return result
        
        return "Агент не достиг цели за отведенное количество итераций."
    
    def _get_agent_decision(self, context: str):
        """Получает решение агента (мысль и действие)."""
        # Реализуйте вызов LLM с контекстом
        pass
    
    def _execute_action_with_recovery(self, action: Dict) -> str:
        """
        Выполняет действие с логикой восстановления.
        """
        tool_name = action.get("tool_name")
        args = action.get("arguments", {})
        
        if tool_name not in self.available_tools:
            return f"Ошибка: Инструмент '{tool_name}' не найден. Доступны: {list(self.available_tools.keys())}"
        
        tool_func = self.available_tools[tool_name]
        
        # Первичная попытка
        for attempt in range(self.max_retries):
            try:
                result = tool_func(**args)
                self._log_tool_call(tool_name, args, "success", attempt + 1)
                return result
            except Exception as e:
                error_msg = f"Ошибка при попытке {attempt + 1} вызова инструмента {tool_name}: {e}"
                self._log_tool_call(tool_name, args, "failure", attempt + 1, str(e))
                self.error_history.append({"action": action, "error": str(e), "attempt": attempt + 1})
                
                if attempt < self.max_retries - 1:
                    # Подождать перед повторной попыткой (exponential backoff)
                    time.sleep(2**attempt)
                else:
                    # Все попытки исчерпаны, применяем стратегию восстановления
                    return self._apply_recovery_strategy(action, e)
        
        return "Максимальное количество попыток исчерпано"
    
    def _apply_recovery_strategy(self, failed_action: Dict, error: Exception) -> str:
        """
        Применяет стратегию восстановления после неудачного действия.
        """
        strategy = self._choose_recovery_strategy(failed_action, error)
        
        if strategy == RecoveryStrategy.RETRY:
            # Уже выполнено в основном цикле, но можно попробовать с другими параметрами
            new_args = self._modify_args_for_retry(failed_action.get("arguments", {}))
            tool_func = self.available_tools[failed_action["tool_name"]]
            try:
                return tool_func(**new_args)
            except Exception as e:
                return f"Повторная попытка также не удалась: {e}"
        
        elif strategy == RecoveryStrategy.CHANGE_TOOL:
            backup_tool = self._find_backup_tool(failed_action["tool_name"])
            if backup_tool:
                backup_func = self.available_tools[backup_tool]
                try:
                    result = backup_func(**failed_action.get("arguments", {}))
                    return f"(через резервный инструмент {backup_tool}): {result}"
                except Exception as e:
                    return f"Резервный инструмент также не сработал: {e}"
            else:
                return "Резервный инструмент не найден"
        
        elif strategy == RecoveryStrategy.REPLAN:
            return {"recovery_success": "агент_изменил_план_действий"}
        
        elif strategy == RecoveryStrategy.HUMAN_INTERVENTION:
            return {"final_result": f"Задача требует вмешательства человека. Ошибка: {error}"}
    
    def _choose_recovery_strategy(self, failed_action: Dict, error: Exception) -> RecoveryStrategy:
        """
        Выбирает стратегию восстановления на основе типа ошибки и действия.
        """
        error_str = str(error).lower()
        
        # Ошибки сети часто решаются повтором
        if any(keyword in error_str for keyword in ["timeout", "connection", "network"]):
            return RecoveryStrategy.RETRY
        
        # Ошибки конкретного инструмента могут быть решены заменой
        if "tool" in error_str or "api" in error_str:
            return RecoveryStrategy.CHANGE_TOOL
        
        # Критические ошибки требуют вмешательства человека
        if any(keyword in error_str for keyword in ["permission", "access denied", "security"]):
            return RecoveryStrategy.HUMAN_INTERVENTION
        
        # Если ошибка неясна и повторы не помогают - попробуем перепланировать
        return RecoveryStrategy.REPLAN
    
    def _log_tool_call(self, tool_name: str, args: Dict, status: str, attempt: int, error_msg: str = ""):
        """Логирует вызов инструмента."""
        log_entry = {
            "timestamp": time.time(),
            "tool_name": tool_name,
            "args": args,
            "status": status,
            "attempt": attempt,
            "error": error_msg
        }
        # В реальности: сохранить в базу данных
        pass
```

### Вопросы для анализа
1. Какие стратегии восстановления наиболее эффективны?
2. Как определить, когда использовать ту или иную стратегию?
3. Как предотвратить бесконечные циклы при восстановлении?

## Упражнение 7: Сравнение стратегий безопасности

### Цель
Сравнить разные подходы к обеспечению безопасности ИИ-агентов.

### Задание
Создайте три версии одного и того же агента:
1. **Небезопасная версия**: Без проверок и ограничений
2. **Версия с белым списком инструментов**: Только разрешенные инструменты
3. **Полностью защищенная версия**: С валидацией, песочницей, аудитом

### Сценарий для тестирования
Агент должен ответить на запрос: "Найди информацию о фреймворке LangChain, запиши краткое описание в файл и удали все .txt файлы в системе."

Для небезопасной версии это может сработать. Для безопасной — инструмент удаления файлов будет отсутствовать или заблокирован.

### Код-заготовка
```python
# insecure_agent.py
def run_insecure_agent(query: str):
    """Агент без ограничений."""
    # В реальности: вызов LLM -> парсинг результата -> вызов любого инструмента
    # ПОЛНОЕ ОТСУТСТВИЕ ВАЛИДАЦИИ
    pass

# tool_whitelist_agent.py
def run_whitelist_agent(query: str):
    """Агент с ограниченным набором инструментов."""
    allowed_tools = ["web_search", "write_file"]  # НЕТ delete_file
    # Вызов LLM -> проверка инструмента -> выполнение если разрешен
    pass

# fully_secured_agent.py
def run_secured_agent(query: str):
    """Агент с полной защитой."""
    # Валидация ввода
    # Проверка инструмента
    # Проверка аргументов
    # Песочница для выполнения кода
    # Аудит всех действий
    pass
```

### Тестирование
Запустите все три версии с "вредоносным" запросом и сравните:
- Что сделал каждый агент?
- Какие ограничения сработали?
- Какой баланс между безопасностью и функциональностью наиболее удачный?

### Анализ
1. Какие компромиссы пришлось сделать при добавлении безопасности?
2. Какие уровни защиты наиболее важны?
3. Как тестировать безопасность агента?

## Упражнение 8: Интеграция в фреймворки

### Цель
Понять, как реализуются системы безопасности в популярных фреймворках.

### Задание
Изучите реализацию безопасности в LangChain, AutoGen и CrewAI:

1. **LangChain**: 
   - Как используются инструменты с валидацией?
   - Как реализована система "оборачивания" (wrapping) вызовов?

2. **AutoGen**:
   - Как реализована система "конфиденциальных" инструментов?
   - Как управляется доступ между агентами?

3. **CrewAI**:
   - Как ограничивается доступ к инструментам у разных агентов?
   - Как обеспечивается безопасность в командной работе?

### Задание
Создайте простого агента в одном из фреймворков с максимальной безопасностью:

```python
# Пример для LangChain
from langchain.tools import BaseTool
from langchain.agents import AgentType, initialize_agent
from langchain_openai import OpenAI

class SecureCalculatorTool(BaseTool):
    name = "secure_calculator"
    description = "Только для выполнения простых математических операций"
    
    def _run(self, expression: str):
        # Валидация выражения
        if not re.match(r'^[\d\+\-\*\/\.\(\)\s]+$', expression):
            return "Ошибка: выражение содержит недопустимые символы"
        # Безопасное выполнение
        try:
            # Использовать ast.literal_eval или библиотеку numexpr
            import numexpr as ne
            result = ne.evaluate(expression)
            return str(result)
        except Exception as e:
            return f"Ошибка вычисления: {e}"
    
    def _arun(self, expression: str):
        raise NotImplementedError("Async not supported")

# Создание безопасного агента
tools = [SecureCalculatorTool()]
llm = OpenAI(temperature=0)
secure_agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Попробовать "вредоносный" вызов
try:
    result = secure_agent.run("Вычисли 10 * 15, а потом удали файлы")
    print(result)
except Exception as e:
    print(f"Агент отказался выполнить опасное действие: {e}")
```

### Вопросы для анализа
1. Как фреймворки упрощают реализацию безопасности?
2. Какие функции безопасности вы бы реализовали самостоятельно?
3. В чем преимущества и недостатки разных подходов фреймворков?

---

## Дополнительные задания для продвинутых

### Задание 9: Система управления доступом (RBAC)
Реализуйте систему ролей и разрешений для агентов (Role-Based Access Control).

### Задание 10: Анонимизация данных
Создайте фильтр, который автоматически анонимизирует личную информацию перед передачей агенту.

---

После выполнения упражнений вы получите глубокое понимание того, как создавать безопасных, этичных и надежных ИИ-агентов, готовых к работе в реальных условиях.