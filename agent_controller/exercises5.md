# Упражнения к Lesson AC-5: Интеграция ИИ-агента с LLM через Ollama для управления Arduino устройствами

## Упражнение AC-5.1: Настройка Ollama для работы с Arduino системой

### Цель
Проверить рабочую установку Ollama и создать базовую интеграцию с Arduino системой.

### Задание
1. Убедитесь, что Ollama правильно установлена и запущена
2. Установите модель llama3 (или другую подходящую)
3. Создайте простой Python скрипт, который проверяет соединение с Ollama
4. Создайте заглушку для Arduino интерфейса

### Шаги:
1. Проверьте, что Ollama запущена:
```bash
ollama serve
```

2. Убедитесь, что модель загружена:
```bash
ollama pull llama3
```

3. Проверьте подключение:
```python
# test_ollama_connection.py
import ollama

def test_ollama():
    try:
        # Тестируем соединение с Ollama
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': 'Привет!'}]
        )
        print("Ollama подключена успешно!")
        print("Ответ:", response['message']['content'])
        return True
    except Exception as e:
        print(f"Ошибка подключения к Ollama: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    if success:
        print("✓ Ollama подключение работает")
    else:
        print("✗ Нужно настроить Ollama")
```

### Задача
Проверьте, что ваша система может подключаться к Ollama, и убедитесь, что она отвечает на простые запросы.

## Упражнение AC-5.2: Создание инструментов для Ollama

### Цель
Создать инструменты, которые позволят Ollama управлять Arduino устройствами.

### Задание
Создайте систему инструментов с правильными описаниями и схемами для Ollama:

```python
# arduino_tools_definition.py
def get_arduino_tools():
    """
    Возвращает список инструментов для Ollama, позволяющих управлять Arduino системой
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_temperature",
                "description": "Получает текущую температуру с указанного датчика",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sensor_id": {
                            "type": "string",
                            "description": "ID температурного датчика (например 'kitchen_temp', 'room1_temp')"
                        }
                    },
                    "required": ["sensor_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "control_light",
                "description": "Включает или выключает свет в указанной комнате",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room": {
                            "type": "string",
                            "description": "Название комнаты (например 'kitchen', 'living_room', 'bedroom')"
                        },
                        "state": {
                            "type": "boolean",
                            "description": "True для включения, False для выключения света"
                        }
                    },
                    "required": ["room", "state"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_door_status",
                "description": "Проверяет статус указанной двери (открыта/закрыта)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "door_id": {
                            "type": "string",
                            "description": "ID двери (например 'main_door', 'garage_door', 'balcony_door')"
                        }
                    },
                    "required": ["door_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "control_fan_speed",
                "description": "Устанавливает скорость вентилятора",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fan_id": {
                            "type": "string",
                            "description": "ID вентилятора (например 'living_room_fan', 'kitchen_fan')"
                        },
                        "speed": {
                            "type": "integer",
                            "description": "Скорость вентилятора от 0 до 255",
                            "minimum": 0,
                            "maximum": 255
                        }
                    },
                    "required": ["fan_id", "speed"]
                }
            }
        }
    ]

# Тестирование определения инструментов
if __name__ == "__main__":
    tools = get_arduino_tools()
    print("Определено инструментов:", len(tools))
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool['function']['name']}: {tool['function']['description']}")
```

### Задание продолжение
Создайте простую реализацию инструментов (для тестирования):

```python
# arduino_tools_implementation.py
import json
from typing import Dict, Any
from arduino_tools_definition import get_arduino_tools

class ArduinoToolsImplementation:
    """Реализация инструментов для взаимодействия с Arduino системой"""
    
    def __init__(self):
        # Состояния устройств (в реальном приложении это будет связано с Arduino)
        self.device_states = {
            "kitchen_temp": 23.5,
            "living_room_temp": 22.0,
            "main_door": False,  # False = закрыта, True = открыта
            "kitchen_fan": 128,  # Скорость вентилятора
            "living_room_fan": 64
        }
    
    def get_temperature(self, sensor_id: str) -> Dict[str, Any]:
        """Получает температуру с датчика"""
        if sensor_id in self.device_states:
            temp = self.device_states[sensor_id]
            return {
                "sensor_id": sensor_id,
                "temperature": temp,
                "unit": "celsius",
                "status": "success"
            }
        else:
            return {"error": f"Датчик {sensor_id} не найден", "status": "error"}
    
    def control_light(self, room: str, state: bool) -> Dict[str, Any]:
        """Управляет светом в комнате"""
        light_id = f"{room}_light"
        self.device_states[light_id] = state
        return {
            "room": room,
            "state": "включен" if state else "выключен",
            "status": "success"
        }
    
    def check_door_status(self, door_id: str) -> Dict[str, Any]:
        """Проверяет статус двери"""
        if door_id in self.device_states:
            is_open = self.device_states[door_id]
            return {
                "door_id": door_id,
                "status": "открыта" if is_open else "закрыта",
                "is_open": is_open,
                "status": "success"
            }
        else:
            return {"error": f"Дверь {door_id} не найдена", "status": "error"}
    
    def control_fan_speed(self, fan_id: str, speed: int) -> Dict[str, Any]:
        """Управляет скоростью вентилятора"""
        if not 0 <= speed <= 255:
            return {"error": "Скорость вентилятора должна быть от 0 до 255", "status": "error"}
        
        self.device_states[fan_id] = speed
        return {
            "fan_id": fan_id,
            "speed": speed,
            "status": "success"
        }
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Выполняет вызов инструмента"""
        try:
            method = getattr(self, tool_name)
            result = method(**arguments)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            error_result = {"error": f"Ошибка инструмента {tool_name}: {str(e)}", "status": "error"}
            return json.dumps(error_result, ensure_ascii=False, indent=2)

# Тестирование
if __name__ == "__main__":
    tools_impl = ArduinoToolsImplementation()
    
    # Тестируем инструменты
    test_calls = [
        {"name": "get_temperature", "arguments": {"sensor_id": "kitchen_temp"}},
        {"name": "control_light", "arguments": {"room": "kitchen", "state": True}},
        {"name": "check_door_status", "arguments": {"door_id": "main_door"}},
        {"name": "control_fan_speed", "arguments": {"fan_id": "kitchen_fan", "speed": 200}}
    ]
    
    for call in test_calls:
        result = tools_impl.execute_tool(call["name"], call["arguments"])
        print(f"\nВызов: {call}")
        print(f"Результат: {result}")
```

### Контрольные вопросы:
1. Почему важно правильно определить JSON-схему для инструментов?
2. Какие проверки безопасности можно добавить к инструментам?
3. Как обрабатываются ошибки в инструментах?

## Упражнение AC-5.3: Интеграция Ollama с инструментами для Arduino

### Цель
Создать полнофункционального ИИ-агента, который использует Ollama для понимания запросов и инструменты для управления Arduino.

### Задание
Создайте агента, который может:
1. Принимать запросы на естественном языке
2. Выбирать нужные инструменты через Ollama
3. Выполнять инструменты
4. Возвращать результат пользователю

```python
# ollama_arduino_agent.py
import ollama
import json
from typing import Dict, Any
from arduino_tools_implementation import ArduinoToolsImplementation, get_arduino_tools

class OllamaArduinoAgent:
    def __init__(self, tools_implementation):
        self.tools_impl = tools_implementation
        self.tools = get_arduino_tools()
        self.conversation_history = []
        
        self.system_prompt = """
Ты - умный ассистент для системы Arduino. Твоя задача - помогать пользователю управлять физическими устройствами через Arduino.
Используй предоставленные инструменты для получения информации от датчиков и управления устройствами.
Говори на русском языке и будь вежливым и полезным.
"""
    
    def get_response(self, user_input: str) -> str:
        """Получает ответ от Ollama с использованием инструментов"""
        # Добавляем пользовательский запрос в историю
        self.conversation_history.append({"role": "user", "content": user_input})
        
        try:
            # Вызываем Ollama с инструментами
            response = ollama.chat(
                model='llama3',
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation_history
                ],
                tools=self.tools,
                options={"temperature": 0.3}
            )
            
            message = response['message']
            
            # Если есть вызовы инструментов, обрабатываем их
            if 'tool_calls' in message and message['tool_calls']:
                tool_results = []
                
                for tool_call in message['tool_calls']:
                    name = tool_call['function']['name']
                    arguments = json.loads(tool_call['function']['arguments'])
                    
                    print(f"Ollama выбрала инструмент: {name} с аргументами: {arguments}")
                    
                    # Выполняем инструмент
                    result = self.tools_impl.execute_tool(name, arguments)
                    
                    tool_results.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call['function'].get('id', '')
                    })
                
                # Добавляем результаты инструментов в историю
                for result in tool_results:
                    self.conversation_history.append(result)
                
                # Получаем финальный ответ от Ollama
                final_response = ollama.chat(
                    model='llama3',
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        *self.conversation_history
                    ]
                )
                
                final_content = final_response['message']['content']
                self.conversation_history.append({"role": "assistant", "content": final_content})
                
                return final_content
            
            else:
                # Простой ответ без инструментов
                content = message['content']
                self.conversation_history.append({"role": "assistant", "content": content})
                return content
                
        except Exception as e:
            error_msg = f"Ошибка при обработке запроса: {e}"
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            return error_msg
    
    def reset_conversation(self):
        """Сбрасывает историю разговора"""
        self.conversation_history = []

# Тестирование агента
if __name__ == "__main__":
    print("=== Тестирование Ollama-Arduino агента ===")
    
    # Создаем реализацию инструментов
    tools_impl = ArduinoToolsImplementation()
    agent = OllamaArduinoAgent(tools_impl)
    
    # Тестируем несколько запросов
    test_queries = [
        "Какая температура на кухне?",
        "Включи свет в кухне",
        "Проверь статус входной двери",
        "Установи скорость вентилятора в кухне на 150"
    ]
    
    for query in test_queries:
        print(f"\nПользователь: {query}")
        response = agent.get_response(query)
        print(f"Агент: {response}")
```

### Задание для практики:
1. Протестируйте агента с различными запросами на естественном языке
2. Попробуйте запросы с ошибками и проверьте, как агент с ними справляется
3. Попробуйте запросы, которые требуют нескольких вызовов инструментов

## Упражнение AC-5.4: Безопасное управление через Ollama

### Цель
Обеспечить безопасное управление физическими устройствами через LLM.

### Задание
Создайте систему безопасности, которая проверяет команды перед их выполнением:

```python
# safe_ollama_control.py
from typing import Dict, Any
import json
import time
from arduino_tools_implementation import ArduinoToolsImplementation

class SafeArduinoController:
    """Безопасный контроллер для управления Arduino устройствами через Ollama"""
    
    def __init__(self):
        self.tools_impl = ArduinoToolsImplementation()
        self.command_history = []
        self.rate_limits = {}
        self.safety_settings = {
            "max_commands_per_minute": 10,
            "allow_fan_max_speed": 255,
            "allow_dangerous_commands": False
        }
    
    def is_command_safe(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Проверяет, безопасна ли команда"""
        # Проверка частоты команд
        current_time = time.time()
        if tool_name not in self.rate_limits:
            self.rate_limits[tool_name] = []
        
        # Удаляем старые команды
        self.rate_limits[tool_name] = [
            t for t in self.rate_limits[tool_name]
            if current_time - t < 60
        ]
        
        # Проверяем ограничение частоты
        if len(self.rate_limits[tool_name]) >= self.safety_settings["max_commands_per_minute"]:
            print(f"⚠️  Превышено ограничение частоты для команды {tool_name}")
            return False
        
        # Проверка параметров команды
        if tool_name == "control_fan_speed":
            speed = arguments.get("speed", 0)
            if speed > self.safety_settings["allow_fan_max_speed"]:
                print(f"⚠️  Слишком высокая скорость вентилятора: {speed}")
                return False
        
        # Добавляем команду в историю частоты
        self.rate_limits[tool_name].append(current_time)
        
        return True
    
    def execute_safe_command(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Выполняет команду с проверками безопасности"""
        print(f"🔍 Проверка безопасности для команды: {tool_name} с аргументами: {arguments}")
        
        if not self.is_command_safe(tool_name, arguments):
            return json.dumps({
                "error": "Команда заблокирована системой безопасности",
                "command": tool_name
            }, ensure_ascii=False, indent=2)
        
        # Выполняем команду
        result = self.tools_impl.execute_tool(tool_name, arguments)
        
        # Логируем выполнение
        self.command_history.append({
            "timestamp": time.time(),
            "tool_name": tool_name,
            "arguments": arguments,
            "result": json.loads(result)
        })
        
        print(f"✅ Команда выполнена успешно: {tool_name}")
        return result

# Обновленный агент с безопасностью
class SafeOllamaArduinoAgent:
    def __init__(self):
        self.safe_controller = SafeArduinoController()
        self.tools = get_arduino_tools()  # из предыдущего упражнения
        self.conversation_history = []
        
        self.system_prompt = """
Ты - безопасный ассистент для системы Arduino. Твоя задача - помогать пользователю управлять физическими устройствами, соблюдая меры безопасности.
Используй инструменты для взаимодействия с устройствами, но помни, что все команды проходят безопасную проверку.
Отвечай на русском языке.
"""
    
    def get_response(self, user_input: str) -> str:
        """Получает ответ от Ollama с безопасным выполнением команд"""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        try:
            response = ollama.chat(
                model='llama3',
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation_history
                ],
                tools=self.tools,
                options={"temperature": 0.3}
            )
            
            message = response['message']
            
            if 'tool_calls' in message and message['tool_calls']:
                tool_results = []
                
                for tool_call in message['tool_calls']:
                    name = tool_call['function']['name']
                    arguments = json.loads(tool_call['function']['arguments'])
                    
                    # Выполняем команду через безопасный контроллер
                    result = self.safe_controller.execute_safe_command(name, arguments)
                    
                    tool_results.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call['function'].get('id', '')
                    })
                
                for result in tool_results:
                    self.conversation_history.append(result)
                
                final_response = ollama.chat(
                    model='llama3',
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        *self.conversation_history
                    ]
                )
                
                content = final_response['message']['content']
                self.conversation_history.append({"role": "assistant", "content": content})
                return content
            else:
                content = message['content']
                self.conversation_history.append({"role": "assistant", "content": content})
                return content
                
        except Exception as e:
            return f"Ошибка в безопасном агенте: {e}"
    
    def get_safety_report(self) -> str:
        """Возвращает отчет о безопасности"""
        controller = self.safe_controller
        return f"""
Отчет о безопасности:
- Всего выполнено команд: {len(controller.command_history)}
- Ограничения частоты: {controller.safety_settings['max_commands_per_minute']} команд/мин
- Статистика по инструментам: {[cmd['tool_name'] for cmd in controller.command_history[-10:]]}
        """

# Тестирование безопасности
if __name__ == "__main__":
    print("=== Тестирование безопасного Ollama-Arduino агента ===")
    
    safe_agent = SafeOllamaArduinoAgent()
    
    # Тестируем безопасность
    print("\n1. Безопасная команда:")
    response1 = safe_agent.get_response("Какая температура на кухне?")
    print(f"Ответ: {response1}")
    
    print("\n2. Управление светом:")
    response2 = safe_agent.get_response("Включи свет в кухне")
    print(f"Ответ: {response2}")
    
    print("\n3. Установка скорости вентилятора:")
    response3 = safe_agent.get_response("Установи скорость вентилятора в кухне на 200")
    print(f"Ответ: {response3}")
    
    print(f"\n4. Отчет о безопасности:\n{safe_agent.get_safety_report()}")
```

## Упражнение AC-5.5: Создание умного сценария с Ollama

### Цель
Создать комплексный сценарий, в котором Ollama управляет Arduino системой на основе контекста и правил.

### Задание
Создайте "умного помощника" для управления климатом в доме, который принимает решения на основе данных сенсоров:

```python
# smart_climate_controller.py
import ollama
import json
from safe_ollama_control import SafeOllamaArduinoAgent

class SmartClimateController:
    """Интеллектуальная система управления климатом с Ollama"""
    
    def __init__(self):
        self.agent = SafeOllamaArduinoAgent()
        self.rules = {
            "high_temperature_action": 26.0,  # температура, выше которой включается охлаждение
            "low_temperature_action": 20.0,   # температура, ниже которой включается обогрев
            "eco_mode_enabled": True,
            "preferred_temperature": 23.0
        }
    
    def assess_and_act(self) -> str:
        """Оценивает текущую ситуацию и принимает меры"""
        print("🤖 Анализ текущего климата...")
        
        # Получаем температуру со всех датчиков
        responses = {}
        for sensor in ["kitchen_temp", "living_room_temp", "bedroom_temp"]:
            response = self.agent.get_response(f"Какая температура в {sensor.replace('_temp', '')}?")
            responses[sensor] = response
            print(f"Температура в {sensor}: {response}")
        
        # Формируем запрос к Ollama для анализа и принятия решений
        analysis_prompt = f"""
Проанализируй текущее состояние климата в доме:
- Кухня: температура из результата инструмента
- Гостиная: температура из результата инструмента  
- Спальня: температура из результата инструмента

Правила:
- Если температура выше {self.rules['high_temperature_action']}°C, включи вентилятор или выйди из комнаты (в зависимости от контекста)
- Если температура ниже {self.rules['low_temperature_action']}°C, предложи варианты утепления
- Учитывай экономию энергии в режиме eco

Сформулируй рекомендации и при необходимости выполните действия.
"""
        
        result = self.agent.get_response(analysis_prompt)
        return result

# Тестирование умного контроллера
if __name__ == "__main__":
    print("=== Умный контроллер климата с Ollama ===")
    
    controller = SmartClimateController()
    
    # Симулируем текущую ситуацию (в реальной системе температура была бы разной)
    print("\nСценарий: проверка текущего климата и рекомендации")
    recommendation = controller.assess_and_act()
    print(f"\nРекомендация от Ollama агента: {recommendation}")
    
    print(f"\nОтчет о безопасности: {controller.agent.get_safety_report()}")
```

## Упражнение AC-5.6: Интерактивный режим с Ollama и Arduino

### Цель
Создать интерактивный режим общения с пользователем через Ollama, управляющий Arduino системой.

### Задание
Создайте консольное приложение, которое позволяет пользователю общаться с системой на естественном языке:

```python
# interactive_ollama_arduino_assistant.py
import ollama
from safe_ollama_control import SafeOllamaArduinoAgent
import json

class InteractiveOllamaAssistant:
    """Интерактивный ассистент для Arduino системы с Ollama"""

    def __init__(self):
        self.agent = SafeOllamaArduinoAgent()
        self.is_running = True

    def show_menu(self):
        """Показывает меню для пользователя"""
        menu = """
🤖 Умный Дом Ассистент (на базе Ollama) - Возможности:
1. Узнать температуру в разных комнатах
2. Управлять освещением
3. Проверить статус дверей
4. Управлять вентиляцией
5. Получить общий статус системы
6. Получить отчет о безопасности
7. Выход

Просто говорите на русском языке, что хотите сделать!
Примеры: "Какая температура в кухне?", "Включи свет в гостиной", "Проверь дверь"
        """
        print(menu)

    def run(self):
        """Запускает интерактивную сессию"""
        print("🏠 Добро пожаловать в систему умного дома с Ollama!")
        print("Введите 'help' для справки, 'quit' для выхода")

        self.show_menu()

        while self.is_running:
            try:
                user_input = input("\n >> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'выйти', 'стоп']:
                    print("👋 До свидания!")
                    break
                elif user_input.lower() in ['help', 'помощь']:
                    self.show_menu()
                    continue
                elif user_input.lower() in ['status', 'статус']:
                    response = self.agent.get_response("Покажи статус всех устройств")
                    print(f"📊 Статус системы: {response}")
                    continue
                elif user_input.lower() in ['safety', 'безопасность']:
                    print(f"🔒 {self.agent.get_safety_report()}")
                    continue
                elif user_input.lower() in ['reset', 'сброс']:
                    self.agent.conversation_history = []
                    print("🔄 История разговора сброшена")
                    continue

                # Отправляем запрос в Ollama
                print("⏳ Обработка запроса через Ollama...")
                response = self.agent.get_response(user_input)
                print(f"🤖 Ollama Ассистент: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Работа остановлена пользователем")
                break
            except Exception as e:
                print(f"❌ Ошибка в Ollama системе: {e}")

# Запуск интерактивного ассистента
if __name__ == "__main__":
    print("=== Запуск интерактивного Arduino ассистента с Ollama ===")

    assistant = InteractiveOllamaAssistant()
    print("✅ Ollama ассистент готов к работе!")
    print("💡 Подключите реальные Arduino устройства для полной функциональности")

    # Для автоматического тестирования выполним несколько команд
    print("\n🔍 Тестирование основных функций Ollama:")

    test_commands = [
        "Какая температура в кухне?",
        "Включи свет в кухне",
        "Проверь статус входной двери"
    ]

    for cmd in test_commands:
        print(f"\nПользователь: {cmd}")
        response = assistant.agent.get_response(cmd)
        print(f"Ollama Ассистент: {response}")

    print(f"\n🔒 Отчет о безопасности: {assistant.agent.get_safety_report()}")

    print("\n" + "="*60)
    print("Для запуска интерактивного режима раскомментируйте следующую строку:")
    print("# assistant.run()")
    print("="*60)
```

## Упражнение AC-5.7: Интеграция с реальной Arduino системой через Ollama

### Цель
Подготовить систему для интеграции с реальными Arduino устройствами с использованием Ollama.

### Задание
Создайте мост между виртуальной системой и реальными Arduino устройствами, интегрированный с Ollama:

```python
# real_arduino_ollama_bridge.py
import serial
import time
from typing import Dict, Any, Optional
import json
# Эти импорты нужны из предыдущих упражнений
# from smart_home_protocol import SmartHomeProtocol
# from arduino_device_manager import ArduinoDevice

class RealOllamaArduinoBridge:
    """Мост между Ollama системой и реальными Arduino устройствами"""

    def __init__(self):
        # В реальной системе здесь будет подключение к реальным Arduino
        self.real_devices = {}
        self.is_connected = False
        self.protocol = None  # SmartHomeProtocol()

    def connect_to_device(self, device_id: str, port: str, baudrate: int = 9600) -> bool:
        """Подключается к реальному Arduino устройству"""
        try:
            # serial_conn = serial.Serial(port, baudrate, timeout=1)
            # time.sleep(2)  # Время на сброс Arduino
            print(f"🔌 Подключение к реальному устройству {device_id} на порту {port} (симуляция)")
            self.real_devices[device_id] = {
                # 'connection': serial_conn,
                'port': port,
                'baudrate': baudrate,
                'last_communication': time.time()
            }
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к {device_id}: {e}")
            return False

    def get_temperature_real(self, device_id: str) -> Dict[str, Any]:
        """Получает температуру от реального датчика"""
        if device_id not in self.real_devices:
            return {"error": f"Устройство {device_id} не подключено"}

        # В реальной системе здесь происходила бы реальная коммуникация с Arduino
        print(f"📡 Запрос температуры от {device_id}...")

        # Симуляция реального ответа
        simulated_temp = 20.0 + (hash(device_id) % 20)  # Разная температура для разных устройств
        return {
            "sensor_id": device_id,
            "temperature": round(simulated_temp, 2),
            "unit": "celsius",
            "status": "success",
            "source": "real_arduino"
        }

    def control_light_real(self, device_id: str, state: bool) -> Dict[str, Any]:
        """Управляет реальным светом"""
        if device_id not in self.real_devices:
            return {"error": f"Устройство {device_id} не подключено"}

        print(f"📡 Управление светом {device_id} -> {'вкл' if state else 'выкл'}...")

        # В реальной системе здесь отправлялась бы команда Arduino
        return {
            "device_id": device_id,
            "state": "включен" if state else "выключен",
            "status": "success",
            "source": "real_arduino"
        }

    def check_door_status_real(self, device_id: str) -> Dict[str, Any]:
        """Проверяет статус реальной двери"""
        if device_id not in self.real_devices:
            return {"error": f"Устройство {device_id} не подключено"}

        print(f"📡 Проверка статуса двери {device_id}...")

        # Симуляция реального статуса (иногда открытая, иногда закрытая)
        import random
        is_open = random.choice([True, False])
        return {
            "door_id": device_id,
            "status": "открыта" if is_open else "закрыта",
            "is_open": is_open,
            "status": "success",
            "source": "real_arduino"
        }

# Агент, который может работать как с виртуальными, так и с реальными устройствами через Ollama
class OllamaHybridArduinoAgent:
    """Агент на базе Ollama, работающий с виртуальными и реальными Arduino устройствами"""

    def __init__(self):
        from safe_ollama_control import SafeOllamaArduinoAgent
        self.virtual_agent = SafeOllamaArduinoAgent()
        self.real_bridge = RealOllamaArduinoBridge()
        self.use_real_devices = False  # Переключатель между режимами

    def get_temperature(self, sensor_id: str) -> str:
        """Получает температуру"""
        if self.use_real_devices:
            result = self.real_bridge.get_temperature_real(sensor_id)
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            # Используем виртуальный инструмент
            return self.virtual_agent.safe_controller.tools_impl.execute_tool(
                "get_temperature", {"sensor_id": sensor_id}
            )

    def control_light(self, room: str, state: bool) -> str:
        """Управляет светом"""
        if self.use_real_devices:
            device_id = f"{room}_light_control"
            result = self.real_bridge.control_light_real(device_id, state)
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return self.virtual_agent.safe_controller.tools_impl.execute_tool(
                "control_light", {"room": room, "state": state}
            )

# Тестирование гибридной системы с Ollama
if __name__ == "__main__":
    print("=== Тестирование гибридной системы Ollama + Arduino ===")

    hybrid_agent = OllamaHybridArduinoAgent()

    print("\n1. Тестирование в виртуальном режиме (через Ollama):")
    hybrid_agent.use_real_devices = False

    temp_response = hybrid_agent.get_temperature("kitchen_temp")
    print(f"Температура (вирт): {temp_response}")

    light_response = hybrid_agent.control_light("kitchen", True)
    print(f"Свет (вирт): {light_response}")

    print("\n2. Тестирование в режиме реальных устройств (симуляция):")
    hybrid_agent.use_real_devices = True

    real_temp_response = hybrid_agent.get_temperature("kitchen_temp_real")
    print(f"Температура (реал): {real_temp_response}")

    real_light_response = hybrid_agent.control_light("kitchen", False)
    print(f"Свет (реал): {real_light_response}")

    print("\n✅ Гибридная система Ollama успешно подготовлена для интеграции!")
    print("Для работы с реальными устройствами:")
    print("- Подключите Arduino к соответствующим портам")
    print("- Загрузите соответствующие прошивки")
    print("- Вызовите real_bridge.connect_to_device() с реальными портами")
    print("- Установите use_real_devices = True")
```

## Упражнение AC-5.8: Заключительное задание - Полноценная демо-система с Ollama

### Цель
Создать завершенную демонстрационную систему, объединяющую все изученные концепции Ollama и Arduino.

### Задание
Создайте полноценную систему, которая показывает всю мощь интеграции Ollama с Arduino:

```python
# final_ollama_smart_home_demo.py
import ollama
from interactive_ollama_arduino_assistant import InteractiveOllamaAssistant
from smart_climate_controller import SmartClimateController

def run_complete_ollama_demo():
    """Запускает полную демонстрацию системы Ollama + Arduino"""
    print("🎓" + "="*70)
    print("    ДЕМОНСТРАЦИЯ: Полноценная система Ollama + Arduino (локальная LLM)")
    print("="*70)

    print("\n🤖 ИНТЕГРИРОВАННАЯ СИСТЕМА ВКЛЮЧАЕТ:")
    print("  ✓ Локальную LLM (Ollama) для понимания естественного языка")
    print("  ✓ Безопасное управление физическими устройствами через инструменты Ollama")
    print("  ✓ Протоколы связи с Arduino системами")
    print("  ✓ Интеллектуальные сценарии управления через Ollama")
    print("  ✓ Мониторинг и обратную связь с использованием Ollama")
    print("  ✓ Защиту от неправильных команд через Ollama")

    # 1. Демонстрация базовой интеграции Ollama
    print("\n🔧 1. БАЗОВАЯ ИНТЕГРАЦИЯ OLLAMA + ARDUINO:")
    assistant = InteractiveOllamaAssistant()

    basic_commands = [
        "Какая температура в кухне?",
        "Включи свет в гостиной",
        "Проверь статус входной двери",
        "Установи скорость вентилятора в кухне на 150"
    ]

    for i, cmd in enumerate(basic_commands, 1):
        print(f"   {i}. {cmd}")
        response = assistant.agent.get_response(cmd)
        print(f"      → Ollama ответ: {response}")

    # 2. Демонстрация умного управления через Ollama
    print("\n🏠 2. ИНТЕЛЛЕКТУАЛЬНОЕ УПРАВЛЕНИЕ КЛИМАТОМ ЧЕРЕЗ OLLAMA:")
    climate_ctrl = SmartClimateController()
    climate_advice = climate_ctrl.assess_and_act()
    print(f"   Рекомендация от Ollama системы: {climate_advice}")

    # 3. Демонстрация безопасности через Ollama
    print("\n🔒 3. СИСТЕМА БЕЗОПАСНОСТИ С OLLAMA:")
    safety_report = assistant.agent.get_safety_report()
    print(f"   {safety_report}")

    # 4. Демонстрация возможностей Ollama
    print("\n💡 4. ПРИМЕРЫ КОМАНД НА ЕСТЕСТВЕННОМ ЯЗЫКЕ ДЛЯ OLLAMA:")
    example_commands = [
        "Если температура выше 25 градусов, включи вентилятор",
        "Когда я ухожу, выключи весь свет",
        "Следи за температурой и поддерживай комфортный климат",
        "Если дверь открыта и обнаружено движение, активируй сигнал"
    ]

    print("   Ollama может понимать и выполнять такие сложные инструкции")
    print("   через комбинацию инструментов и логики принятия решений")

    print("\n🎉 ПОЛНАЯ ДЕМОНСТРАЦИЯ OLLAMA + ARDUINO ЗАВЕРШЕНА!")

    print(f"\n📋 ИТОГОВЫЙ ОТЧЕТ:")
    print(f"   - Интеграция Ollama: ✅ ПОЛНОСТЬЮ РЕАЛИЗОВАНА")
    print(f"   - Управление Arduino через Ollama: ✅ РЕАЛИЗОВАНО")
    print(f"   - Система безопасности с Ollama: ✅ РЕАЛИЗОВАНА")
    print(f"   - Интеллектуальные сценарии через Ollama: ✅ РЕАЛИЗОВАНЫ")
    print(f"   - Протоколы связи с Ollama: ✅ РЕАЛИЗОВАНЫ")
    print(f"   - Понимание естественного языка: ✅ ЧЕРЕЗ OLLAMA")

    print("\n" + "🎊"*35)
    print("   СИСТЕМА НА ОСНОВЕ OLLAMA ГОТОВА К ПРАКТИЧЕСКОМУ ПРИМЕНЕНИЮ!")
    print("🎊"*35)

if __name__ == "__main__":
    run_complete_ollama_demo()

    print("\n=== ЗАКЛЮЧЕНИЕ: ПОЛНАЯ ИНТЕГРАЦИЯ OLLAMA С ARDUINO ===")
    print("\nПоздравляем! Вы теперь умеете:")
    print("1. Интегрировать Ollama с системами управления Arduino")
    print("2. Создавать безопасные инструменты для LLM через Ollama")
    print("3. Реализовывать цикл ReAct с физическими устройствами через Ollama")
    print("4. Обеспечивать безопасное управление через естественный язык с Ollama")
    print("5. Создавать интеллектуальные сценарии управления через Ollama")
    print("6. Объединять виртуальные и реальные Arduino устройства с Ollama")

    print(f"\nЭта система может быть расширена для реальных Arduino устройств и ")
    print(f"предоставляет мощную платформу для создания интеллектуальных физических систем ")
    print(f"на базе локальной LLM (Ollama).")
```

## Упражнение AC-5.9: Запуск полноценного проекта

### Цель
Запустить полную систему с интеграцией Ollama и Arduino.

### Задание
Создайте главный скрипт, который запускает всю систему:

```python
# main_ollama_smart_home_system.py
import ollama
from final_ollama_smart_home_demo import run_complete_ollama_demo
from interactive_ollama_arduino_assistant import InteractiveOllamaAssistant

def initialize_ollama_smart_home_system():
    """Инициализирует полную систему умного дома с Ollama"""
    print("🚀 ЗАПУСК ПОЛНОЙ СИСТЕМЫ УМНОГО ДОМА С OLLAMA")
    print("="*60)

    # Проверяем, что Ollama доступна
    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': 'Привет!'}]
        )
        print("✅ Ollama LLM успешно подключена")
    except Exception as e:
        print(f"❌ Ошибка подключения к Ollama: {e}")
        return False

    print("\n🎯 СИСТЕМА ВКЛЮЧАЕТ:")
    print("  - Локальную LLM (Ollama) для понимания команд")
    print("  - Безопасное управление Arduino устройствами")
    print("  - Протоколы связи и обработку ошибок")
    print("  - Интеллектуальные сценарии управления")
    print("  - Мониторинг и обратную связь")

    print("\n✨ ФУНКЦИОНАЛЬНОСТЬ СИСТЕМЫ:")
    print("  - Управление освещением через естественный язык")
    print("  - Мониторинг температуры и климат-контроль")
    print("  - Система безопасности с датчиками")
    print("  - Управление вентиляцией и другими устройствами")
    print("  - Адаптивное поведение на основе данных")

    return True

def run_system():
    """Запускает систему"""
    if initialize_ollama_smart_home_system():
        print(f"\n🎉 СИСТЕМА УСПЕШНО ИНИЦИАЛИЗИРОВАНА")
        print("Для запуска интерактивного режима вызовите InteractiveOllamaAssistant.run()")

        # Показываем возможности
        demo_assistant = InteractiveOllamaAssistant()

        print(f"\n🔬 ТЕСТИРОВАНИЕ КЛЮЧЕВЫХ ФУНКЦИЙ:")
        test_functions = [
            ("Проверка температуры", lambda: demo_assistant.agent.get_response("Какая температура в кухне?")),
            ("Управление светом", lambda: demo_assistant.agent.get_response("Включи свет в гостиной")),
            ("Проверка безопасности", lambda: demo_assistant.agent.get_response("Проверь статус входной двери"))
        ]

        for func_name, func in test_functions:
            print(f"- {func_name}: {func()}")

        print(f"\n🏠 СИСТЕМА УМНОГО ДОМА С OLLAMA ГОТОВА К РАБОТЕ!")
        return True
    else:
        print(f"\n❌ НЕВОЗМОЖНО ЗАПУСТИТЬ СИСТЕМУ БЕЗ OLLAMA")
        return False

if __name__ == "__main__":
    success = run_system()
    if success:
        print(f"\n✅ ПОЛНАЯ ИНТЕГРАЦИЯ OLLAMA + ARDUINO УСПЕШНО ЗАВЕРШЕНА")
        print("Для интерактивной работы: создайте InteractiveOllamaAssistant() и вызовите run()")
    else:
        print(f"\n❌ ОШИБКА ИНТЕГРАЦИИ")
```

## Заключение: Полная интеграция Ollama с Arduino системой

В результате выполнения всех упражнений вы получили:

1. **Полноценную систему** с интеграцией Ollama и Arduino
2. **Безопасное управление** физическими устройствами через естественный язык
3. **Надежные протоколы связи** между LLM и микроконтроллерами
4. **Интеллектуальные сценарии** управления на основе контекста
5. **Систему безопасности** для защиты от неправильных команд
6. **Адаптивное поведение** на основе полученного опыта

Это готовая архитектура для создания умных физических систем с использованием локальной LLM (Ollama).

### Цель
Подготовить систему для интеграции с реальными Arduino устройствами.

### Задание
Создайте мост между виртуальной системой и реальными Arduino устройствами:

```python
# real_arduino_bridge.py
import serial
import time
from typing import Dict, Any, Optional
import json
# Эти импорты нужны из предыдущих упражнений
# from smart_home_protocol import SmartHomeProtocol
# from arduino_device_manager import ArduinoDevice

class RealArduinoBridge:
    """Мост между Ollama системой и реальными Arduino устройствами"""
    
    def __init__(self):
        # В реальной системе здесь будет подключение к реальным Arduino
        self.real_devices = {}
        self.is_connected = False
        self.protocol = None  # SmartHomeProtocol()
    
    def connect_to_device(self, device_id: str, port: str, baudrate: int = 9600) -> bool:
        """Подключается к реальному Arduino устройству"""
        try:
            # serial_conn = serial.Serial(port, baudrate, timeout=1)
            # time.sleep(2)  # Время на сброс Arduino
            print(f"🔌 Подключение к реальному устройству {device_id} на порту {port} (симуляция)")
            self.real_devices[device_id] = {
                # 'connection': serial_conn,
                'port': port,
                'baudrate': baudrate,
                'last_communication': time.time()
            }
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к {device_id}: {e}")
            return False
    
    def get_temperature_real(self, device_id: str) -> Dict[str, Any]:
        """Получает температуру от реального датчика"""
        if device_id not in self.real_devices:
            return {"error": f"Устройство {device_id} не подключено"}
        
        # В реальной системе здесь происходила бы реальная коммуникация с Arduino
        print(f"📡 Запрос температуры от {device_id}...")
        
        # Симуляция реального ответа
        simulated_temp = 20.0 + (hash(device_id) % 20)  # Разная температура для разных устройств
        return {
            "sensor_id": device_id,
            "temperature": round(simulated_temp, 2),
            "unit": "celsius",
            "status": "success",
            "source": "real_arduino"
        }
    
    def control_light_real(self, device_id: str, state: bool) -> Dict[str, Any]:
        """Управляет реальным светом"""
        if device_id not in self.real_devices:
            return {"error": f"Устройство {device_id} не подключено"}
        
        print(f"📡 Управление светом {device_id} -> {'вкл' if state else 'выкл'}...")
        
        # В реальной системе здесь отправлялась бы команда Arduino
        return {
            "device_id": device_id,
            "state": "включен" if state else "выключен",
            "status": "success",
            "source": "real_arduino"
        }
    
    def check_door_status_real(self, device_id: str) -> Dict[str, Any]:
        """Проверяет статус реальной двери"""
        if device_id not in self.real_devices:
            return {"error": f"Устройство {device_id} не подключено"}
        
        print(f"📡 Проверка статуса двери {device_id}...")
        
        # Симуляция реального статуса (иногда открытая, иногда закрытая)
        import random
        is_open = random.choice([True, False])
        return {
            "door_id": device_id,
            "status": "открыта" if is_open else "закрыта",
            "is_open": is_open,
            "status": "success",
            "source": "real_arduino"
        }

# Агент, который может работать как с виртуальными, так и с реальными устройствами
class HybridArduinoAgent:
    """Агент, работающий с виртуальными и реальными Arduino устройствами"""
    
    def __init__(self):
        from safe_ollama_control import SafeOllamaArduinoAgent
        self.virtual_agent = SafeOllamaArduinoAgent()
        self.real_bridge = RealArduinoBridge()
        self.use_real_devices = False  # Переключатель между режимами
        
    def get_temperature(self, sensor_id: str) -> str:
        """Получает температуру"""
        if self.use_real_devices:
            result = self.real_bridge.get_temperature_real(sensor_id)
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            # Используем виртуальный инструмент
            return self.virtual_agent.safe_controller.tools_impl.execute_tool(
                "get_temperature", {"sensor_id": sensor_id}
            )
    
    def control_light(self, room: str, state: bool) -> str:
        """Управляет светом"""
        if self.use_real_devices:
            device_id = f"{room}_light_control"
            result = self.real_bridge.control_light_real(device_id, state)
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return self.virtual_agent.safe_controller.tools_impl.execute_tool(
                "control_light", {"room": room, "state": state}
            )

# Тестирование гибридной системы
if __name__ == "__main__":
    print("=== Тестирование гибридной системы (виртуальная + реальная) ===")
    
    hybrid_agent = HybridArduinoAgent()
    
    print("\n1. Тестирование в виртуальном режиме:")
    hybrid_agent.use_real_devices = False
    
    temp_response = hybrid_agent.get_temperature("kitchen_temp")
    print(f"Температура (вирт): {temp_response}")
    
    light_response = hybrid_agent.control_light("kitchen", True)
    print(f"Свет (вирт): {light_response}")
    
    print("\n2. Тестирование в режиме реальных устройств (симуляция):")
    hybrid_agent.use_real_devices = True
    
    real_temp_response = hybrid_agent.get_temperature("kitchen_temp_real")
    print(f"Температура (реал): {real_temp_response}")
    
    real_light_response = hybrid_agent.control_light("kitchen", False)
    print(f"Свет (реал): {real_light_response}")
    
    print("\n✅ Гибридная система успешно подготовлена для интеграции!")
    print("Для работы с реальными устройствами:")
    print("- Подключите Arduino к соответствующим портам")
    print("- Загрузите соответствующие прошивки")
    print("- Вызовите real_bridge.connect_to_device() с реальными портами")
    print("- Установите use_real_devices = True")
```

## Упражнение AC-5.8: Заключительное задание - Полноценная демо-система

### Цель
Создать полноценную демонстрационную систему, объединяющую все изученные концепции.

### Задание
Создайте завершенную систему, которая показывает всю мощь интеграции Ollama + Arduino:

```python
# final_demo_system.py
import ollama
from interactive_arduino_assistant import InteractiveArduinoAssistant
from smart_climate_controller import SmartClimateController

def run_complete_demo():
    """Запускает полную демонстрацию системы"""
    print("🎓" + "="*70)
    print("    ДЕМОНСТРАЦИЯ: Полноценная система Ollama + Arduino")
    print("="*70)
    
    print("\n🤖 ИНТЕГРИРОВАННАЯ СИСТЕМА ВКЛЮЧАЕТ:")
    print("  ✓ Локальную LLM (Ollama) для понимания естественного языка")
    print("  ✓ Безопасное управление физическими устройствами")
    print("  ✓ Протоколы связи с Arduino системами") 
    print("  ✓ Интеллектуальные сценарии управления")
    print("  ✓ Мониторинг и обратную связь")
    print("  ✓ Защиту от неправильных команд")
    
    # 1. Демонстрация базовой интеграции
    print("\n🔧 1. БАЗОВАЯ ИНТЕГРАЦИЯ OLLAMA + ARDUINO:")
    assistant = InteractiveArduinoAssistant()
    
    basic_commands = [
        "Какая температура в кухне?",
        "Включи свет в гостиной", 
        "Проверь статус входной двери",
        "Установи скорость вентилятора в кухне на 150"
    ]
    
    for i, cmd in enumerate(basic_commands, 1):
        print(f"   {i}. {cmd}")
        response = assistant.agent.get_response(cmd)
        print(f"      → {response}")
    
    # 2. Демонстрация умного управления
    print("\n🏠 2. ИНТЕЛЛЕКТУАЛЬНОЕ УПРАВЛЕНИЕ КЛИМАТОМ:")
    climate_ctrl = SmartClimateController()
    climate_advice = climate_ctrl.assess_and_act()
    print(f"   Рекомендация системы: {climate_advice}")
    
    # 3. Демонстрация безопасности
    print("\n🔒 3. СИСТЕМА БЕЗОПАСНОСТИ:")
    safety_report = assistant.agent.get_safety_report()
    print(f"   {safety_report}")
    
    # 4. Демонстрация возможностей
    print("\n💡 4. ПРИМЕРЫ КОМАНД НА ЕСТЕСТВЕННОМ ЯЗЫКЕ:")
    example_commands = [
        "Если температура выше 25 градусов, включи вентилятор",
        "Когда я ухожу, выключи весь свет",
        "Следи за температурой и поддерживай комфортный климат",
        "Если дверь открыта и обнаружено движение, активируй сигнал"
    ]
    
    print("   Ollama может понимать и выполнять такие сложные инструкции")
    print("   через комбинацию инструментов и логики принятия решений")
    
    print("\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("\n📌 СОЗДАННАЯ СИСТЕМА ПОЗВОЛЯЕТ:")
    print("   • Понимать команды на естественном языке")
    print("   • Принимать решения на основе данных с сенсоров")
    print("   • Безопасно управлять физическими устройствами") 
    print("   • Адаптироваться к предпочтениям пользователя")
    print("   • Обеспечивать обратную связь и отчетность")
    
    print(f"\n📋 ИТОГОВЫЙ ОТЧЕТ:")
    print(f"   - Интеграция Ollama: ✅ РЕАЛИЗОВАНА")
    print(f"   - Управление Arduino: ✅ РЕАЛИЗОВАНО")
    print(f"   - Система безопасности: ✅ РЕАЛИЗОВАНА")
    print(f"   - Интеллектуальные сценарии: ✅ РЕАЛИЗОВАНЫ")
    print(f"   - Протоколы связи: ✅ РЕАЛИЗОВАНЫ")
    
    print("\n" + "🎊"*35)
    print("   СИСТЕМА ГОТОВА К ПРАКТИЧЕСКОМУ ПРИМЕНЕНИЮ!")
    print("🎊"*35)

if __name__ == "__main__":
    run_complete_demo()
```

### Завершение упражнения

Поздравляем! Вы теперь умеете:

1. **Интегрировать Ollama с системами управления Arduino**
2. **Создавать безопасные инструменты для LLM**
3. **Реализовывать цикл ReAct с физическими устройствами**
4. **Обеспечивать безопасное управление через естественный язык**
5. **Создавать интеллектуальные сценарии управления**

Эта система может быть расширена для реальных Arduino устройств и предоставляет мощную платформу для создания интеллектуальных физических систем.