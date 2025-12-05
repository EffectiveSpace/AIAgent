# Lesson AC-5: Интеграция ИИ-агента с LLM через Ollama для управления Arduino устройствами

## Цели урока

После изучения этого урока вы сможете:
- Интегрировать локальный LLM (Ollama) в систему управления Arduino
- Создать инструменты для Ollama, позволяющие управлять физическими устройствами
- Реализовать цикл ReAct с участием LLM, Arduino и физического мира
- Обеспечить безопасное управление устройствами через LLM
- Создать системы обратной связи между LLM и физическими устройствами

## 1. Введение: Почему LLM важен для управления физическими устройствами

В предыдущих уроках мы создали мощную систему управления Arduino устройствами, но она работала по предопределенным сценариям. Для получения **истинно интеллектуального поведения** нам нужно добавить:

- **Понимание естественного языка**: Пользователь может говорить системе на обычном языке
- **Рассуждение и планирование**: LLM может принимать сложные решения на основе контекста
- **Адаптивность**: Система может адаптироваться к новым ситуациям без перепрограммирования
- **Объяснение действий**: Система может объяснить, почему она приняла то или иное решение

### Архитектура системы с LLM:

```
Пользователь (естественный язык)
        ↓
[LLM (Ollama)] ← "мозг" системы
        ↓
[Инструменты: Arduino устройства]
        ↓
[Физические устройства и сенсоры]
        ↓
[Наблюдения → обратно к LLM]
```

## 2. Подготовка: Установка и настройка Ollama

Убедитесь, что Ollama установлена и работает на вашем компьютере:

```bash
# Проверьте, что Ollama запущена (должен работать оллама serve в фоне)
ollama list

# Скачайте модель (например, llama3)
ollama pull llama3
```

## 3. Создание инструментов для Ollama

Для взаимодействия с Arduino устройствами через Ollama, нам нужно создать специальные инструменты:

```python
# ollama_arduino_tools.py
import ollama
import json
from typing import Dict, Any, List
from smart_home_manager import SmartHomeController

class OllamaArduinoInterface:
    """Интерфейс для интеграции Ollama с Arduino системой"""
    
    def __init__(self, smart_home_controller: SmartHomeController):
        self.controller = smart_home_controller
        
        # Определяем инструменты, доступные для LLM
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_system_status",
                    "description": "Получает текущий статус всех устройств в системе умного дома",
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_light_state",
                    "description": "Управляет светом в конкретной комнате",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "ID устройства управления светом"
                            },
                            "state": {
                                "type": "boolean",
                                "description": "True для включения, False для выключения света"
                            }
                        },
                        "required": ["device_id", "state"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_temperature",
                    "description": "Получает текущую температуру из указанного датчика",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "ID устройства с температурным датчиком"
                            }
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_door_status",
                    "description": "Проверяет статус двери (открыта/закрыта)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "ID устройства контроля двери"
                            }
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_motion_status",
                    "description": "Проверяет наличие движения в зоне датчика",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "ID устройства датчика движения"
                            }
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "activate_security_alarm",
                    "description": "Активирует систему безопасности",
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_fan_speed",
                    "description": "Устанавливает скорость вентилятора",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "ID устройства управления вентилятором"
                            },
                            "speed": {
                                "type": "integer",
                                "description": "Скорость вентилятора от 0 до 255",
                                "minimum": 0,
                                "maximum": 255
                            }
                        },
                        "required": ["device_id", "speed"]
                    }
                }
            }
        ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получает статус всей системы"""
        return self.controller.get_system_status()
    
    def set_light_state(self, device_id: str, state: bool) -> Dict[str, Any]:
        """Управляет светом"""
        success = self.controller.set_light_state(device_id, state)
        return {
            "success": success,
            "device_id": device_id,
            "requested_state": state,
            "result": "успешно выполнено" if success else "ошибка выполнения"
        }
    
    def get_temperature(self, device_id: str) -> Dict[str, Any]:
        """Получает температуру от указанного устройства"""
        if device_id in self.controller.devices:
            device = self.controller.devices[device_id]
            result = device.get_temperature()
            return result
        else:
            return {"error": f"Устройство {device_id} не найдено"}
    
    def get_door_status(self, device_id: str) -> Dict[str, Any]:
        """Получает статус двери"""
        if device_id in self.controller.devices:
            device = self.controller.devices[device_id]
            result = device.get_door_status()
            return result
        else:
            return {"error": f"Устройство {device_id} не найдено"}
    
    def get_motion_status(self, device_id: str) -> Dict[str, Any]:
        """Получает статус движения"""
        if device_id in self.controller.devices:
            device = self.controller.devices[device_id]
            result = device.get_motion_status()
            return result
        else:
            return {"error": f"Устройство {device_id} не найдено"}
    
    def activate_security_alarm(self) -> Dict[str, Any]:
        """Активирует систему безопасности"""
        try:
            self.controller.trigger_security_response()
            return {"success": True, "message": "Система безопасности активирована"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_fan_speed(self, device_id: str, speed: int) -> Dict[str, Any]:
        """Устанавливает скорость вентилятора"""
        if device_id in self.controller.devices:
            device = self.controller.devices[device_id]
            result = device.set_fan_speed(speed)
            return result
        else:
            return {"error": f"Устройство {device_id} не найдено"}
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Выполняет вызов инструмента и возвращает результат"""
        try:
            method = getattr(self, tool_name)
            result = method(**arguments)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            error_result = {"error": f"Ошибка выполнения инструмента {tool_name}: {str(e)}"}
            return json.dumps(error_result, ensure_ascii=False, indent=2)
    
    def get_tool_mapping(self) -> Dict[str, Any]:
        """Возвращает маппинг имен инструментов на методы"""
        return {
            "get_system_status": self.get_system_status,
            "set_light_state": self.set_light_state,
            "get_temperature": self.get_temperature,
            "get_door_status": self.get_door_status,
            "get_motion_status": self.get_motion_status,
            "activate_security_alarm": self.activate_security_alarm,
            "set_fan_speed": self.set_fan_speed
        }

# Тестирование инструментов
if __name__ == "__main__":
    # Создаем фиктивный контроллер для тестирования
    # (без реальных Arduino устройств)
    class MockArduinoDevice:
        def get_temperature(self):
            return {"type": "TEMP_DATA", "temperature": 23.5}
        def get_door_status(self):
            return {"type": "DOOR_STATUS", "door_open": False}
        def get_motion_status(self):
            return {"type": "MOTION_STATUS", "motion_detected": False}
        def switch_light(self, state):
            return {"type": "ACK", "status": "success"}
        def set_fan_speed(self, speed):
            return {"type": "ACK", "status": "success"}
    
    class MockController:
        def __init__(self):
            self.devices = {
                "kitchen_temp": MockArduinoDevice(),
                "main_door": MockArduinoDevice(),
                "living_room_motion": MockArduinoDevice()
            }
        
        def get_system_status(self):
            return {
                "temperature": {"kitchen_temp": 23.5},
                "door_status": {"main_door": False},
                "motion_status": {"living_room_motion": False},
                "avg_temperature": 23.5
            }
        
        def set_light_state(self, device_id, state):
            if device_id in self.devices:
                self.devices[device_id].switch_light(state)
                return True
            return False
        
        def trigger_security_response(self):
            print("Security alarm triggered!")
    
    # Тестируем инструменты
    mock_controller = MockController()
    interface = OllamaArduinoInterface(mock_controller)
    
    # Тестируем получение статуса
    status = interface.get_system_status()
    print("Статус системы:", status)
    
    # Тестируем выполнение инструмента
    result = interface.execute_tool("get_temperature", {"device_id": "kitchen_temp"})
    print("Результат инструмента:", result)
    
    # Показываем определения инструментов
    print("\nОпределения инструментов:")
    for tool in interface.tools:
        print(f"- {tool['function']['name']}: {tool['function']['description']}")
```

## 4. Интеграция Ollama в цикл ReAct

Теперь создадим ИИ-агента, который использует Ollama для принятия решений:

```python
# ollama_smart_agent.py
import ollama
import json
import time
from typing import Dict, Any, List, Optional
from ollama_arduino_tools import OllamaArduinoInterface

class OllamaSmartHomeAgent:
    """ИИ-агент с Ollama для умного дома"""
    
    def __init__(self, ollama_interface: OllamaArduinoInterface, model_name: str = "llama3"):
        self.interface = ollama_interface
        self.model_name = model_name
        self.conversation_history = []
        
        # Создаем системный промпт для агента
        self.system_prompt = f"""
Ты - эксперт по умному дому. Твоя задача - помогать пользователю управлять системой умного дома с помощью специальных инструментов.

Доступные инструменты:
- get_system_status: получить статус всей системы
- set_light_state: управлять светом (device_id, state)
- get_temperature: получить температуру (device_id)
- get_door_status: проверить статус двери (device_id)
- get_motion_status: проверить движение (device_id)
- activate_security_alarm: активировать сигнализацию
- set_fan_speed: установить скорость вентилятора (device_id, speed)

Ты работаешь в цикле "Мысль - Действие - Наблюдение":
1. Мысль: кратко объясни, что ты знаешь и что хочешь сделать
2. Действие: вызови подходящий инструмент
3. Наблюдение: получи результат и используй его для следующего шага

Формат для вызова инструмента:
<function_calls>
[{{"name": "инструмент", "arguments": {{"аргументы"}}}}]
</function_calls>

Отвечай на русском языке и будь полезным.
"""
    
    def chat_with_user(self, user_input: str) -> str:
        """Общение с пользователем через Ollama"""
        # Добавляем сообщение пользователя в историю
        self.conversation_history.append({"role": "user", "content": user_input})
        
        response = self._get_ollama_response()
        return response
    
    def _get_ollama_response(self) -> str:
        """Получает ответ от Ollama с возможными вызовами инструментов"""
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        
        try:
            # Вызываем Ollama с инструментами
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                tools=self.interface.tools,
                options={"temperature": 0.1}  # Меньше творчества, больше точности
            )
            
            message = response['message']
            
            # Проверяем, есть ли вызовы инструментов
            if 'tool_calls' in message and message['tool_calls']:
                # Обрабатываем вызовы инструментов
                tool_results = []
                
                for tool_call in message['tool_calls']:
                    tool_name = tool_call['function']['name']
                    arguments = json.loads(tool_call['function']['arguments'])
                    
                    print(f"LLM вызывает инструмент: {tool_name} с аргументами: {arguments}")
                    
                    # Выполняем инструмент
                    result = self.interface.execute_tool(tool_name, arguments)
                    
                    tool_results.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call['function'].get('id', '')
                    })
                
                # Добавляем результаты инструментов в историю
                for tool_result in tool_results:
                    self.conversation_history.append(tool_result)
                
                # Получаем окончательный ответ от LLM с учетом результатов инструментов
                final_response = ollama.chat(
                    model=self.model_name,
                    messages=[{"role": "system", "content": self.system_prompt}] + self.conversation_history
                )
                
                # Добавляем ответ LLM в историю
                self.conversation_history.append({"role": "assistant", "content": final_response['message']['content']})
                
                return final_response['message']['content']
            else:
                # Простой ответ без вызовов инструментов
                final_content = message['content']
                self.conversation_history.append({"role": "assistant", "content": final_content})
                
                return final_content
                
        except json.JSONDecodeError as e:
            print(f"Ошибка разбора JSON из вызова инструмента: {e}")
            return "Извините, произошла ошибка при обработке вызова инструмента."
        except Exception as e:
            print(f"Ошибка при вызове Ollama: {e}")
            return f"Извините, произошла ошибка при обращении к языковой модели: {e}"
    
    def reset_conversation(self):
        """Сбрасывает историю разговора"""
        self.conversation_history = []

# Тестирование интеграции Ollama
if __name__ == "__main__":
    print("=== Тестирование ИИ-агента с Ollama ===")
    
    # Создаем интерфейс с фиктивным контроллером (как в предыдущем примере)
    from ollama_arduino_tools import OllamaArduinoInterface
    from ollama_arduino_tools import MockController
    
    mock_controller = MockController()
    ollama_interface = OllamaArduinoInterface(mock_controller)
    agent = OllamaSmartHomeAgent(ollama_interface)
    
    # Запускаем простую сессию
    print("\nДоступные устройства:")
    print("- kitchen_temp (температура)")
    print("- main_door (статус двери)")
    print("- living_room_motion (движение)")
    
    print("\nПримеры запросов:")
    test_queries = [
        "Какая температура на кухне?",
        "Статус входной двери",
        "Включи свет в гостиной",
        "Покажи полный статус системы"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Запрос {i}: {query} ---")
        response = agent.chat_with_user(query)
        print(f"Ответ: {response}")
    
    print("\n=== Интерактивный режим (для тестирования) ===")
    print("Введите 'quit' для выхода")
    
    try:
        while True:
            user_input = input("\nВаш запрос: ").strip()
            if user_input.lower() in ['quit', 'exit', 'выход']:
                break
            
            if user_input:
                response = agent.chat_with_user(user_input)
                print(f"Ответ: {response}")
    except KeyboardInterrupt:
        print("\nРабота остановлена пользователем")
    
    print("Тестирование интеграции Ollama завершено")
```

## 5. Безопасная интеграция LLM с физическими устройствами

Важно обеспечить безопасность при управлении физическими устройствами через LLM:

```python
# safe_ollama_agent.py
from typing import Dict, Any
from ollama_arduino_tools import OllamaArduinoInterface
import logging
import re

class SafeOllamaAgent:
    """Безопасный ИИ-агент с проверками при управлении устройствами"""
    
    def __init__(self, ollama_interface: OllamaArduinoInterface):
        self.interface = ollama_interface
        self.command_history = []  # История команд для анализа
        self.device_limits = {}    # Ограничения для устройств
        self.safety_mode = True    # Режим безопасности
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SafeOllamaAgent")
        
        # Белый список безопасных команд
        self.safe_commands = {
            'set_light_state',
            'get_temperature', 
            'get_door_status',
            'get_motion_status',
            'get_system_status'
        }
        
        # Ограничения частоты команд
        self.command_rate_limits = {}
        self.max_commands_per_minute = 10
    
    def is_command_safe(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Проверяет, безопасна ли команда для выполнения"""
        # Проверка на вредоносную команду
        if tool_name not in self.safe_commands and tool_name != 'set_fan_speed':
            self.logger.warning(f"Попытка выполнить potentially unsafe command: {tool_name}")
            return False
        
        # Проверка специфических параметров
        if tool_name == 'set_fan_speed':
            speed = arguments.get('speed', 0)
            if not 0 <= speed <= 255:
                self.logger.warning(f"Небезопасная скорость вентилятора: {speed}")
                return False
        
        # Проверка частоты
        if not self.check_command_rate(tool_name):
            self.logger.warning(f"Превышено ограничение частоты для команды: {tool_name}")
            return False
        
        return True
    
    def check_command_rate(self, tool_name: str) -> bool:
        """Проверяет, не превышает ли частота команд ограничения"""
        current_time = time.time()
        
        if tool_name not in self.command_rate_limits:
            self.command_rate_limits[tool_name] = []
        
        # Удаляем старые команды (старше 60 секунд)
        self.command_rate_limits[tool_name] = [
            t for t in self.command_rate_limits[tool_name]
            if current_time - t < 60
        ]
        
        # Проверяем ограничение
        if len(self.command_rate_limits[tool_name]) >= self.max_commands_per_minute:
            return False
        
        # Добавляем текущую команду
        self.command_rate_limits[tool_name].append(current_time)
        return True
    
    def execute_command_with_safety(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет команду с проверками безопасности"""
        self.logger.info(f"Попытка выполнения команды: {tool_name} с аргументами: {arguments}")
        
        if not self.safety_mode:
            # В небезопасном режиме выполняем без проверок (для продвинутых пользователей)
            return self.interface.execute_tool(tool_name, arguments)
        
        # Проверяем безопасность команды
        if not self.is_command_safe(tool_name, arguments):
            return {
                "error": "Команда заблокирована системой безопасности",
                "command": tool_name,
                "arguments": arguments
            }
        
        # Дополнительные проверки
        if tool_name == 'activate_security_alarm':
            # Для тревожных команд требуем дополнительного подтверждения в реальной системе
            self.logger.info("Активация системы безопасности подтверждена")
        
        # Выполняем команду
        result = self.interface.execute_tool(tool_name, arguments)
        
        # Логируем выполнение
        self.command_history.append({
            "timestamp": time.time(),
            "command": tool_name,
            "arguments": arguments,
            "result": result
        })
        
        self.logger.info(f"Команда выполнена: {tool_name}, результат: {result}")
        return result
    
    def get_safety_report(self) -> Dict[str, Any]:
        """Возвращает отчет о безопасности системы"""
        return {
            "safety_mode": self.safety_mode,
            "total_commands": len(self.command_history),
            "blocked_commands": len([c for c in self.command_history if 'error' in str(c.get('result', {}))]),
            "recent_commands": self.command_history[-10:],  # Последние 10 команд
            "rate_limit_stats": {k: len(v) for k, v in self.command_rate_limits.items()}
        }

# Обновленный Ollama агент с безопасностью
class SafeOllamaSmartHomeAgent:
    """Безопасный ИИ-агент с Ollama для умного дома"""
    
    def __init__(self, ollama_interface: OllamaArduinoInterface, model_name: str = "llama3"):
        self.interface = ollama_interface
        self.safe_agent = SafeOllamaAgent(ollama_interface)
        self.model_name = model_name
        self.conversation_history = []
        
        self.system_prompt = f"""
Ты - безопасный ассистент умного дома. Твоя задача - помогать пользователю управлять системой умного дома, при этом соблюдая меры безопасности.

Доступные инструменты:
- get_system_status: получить статус всей системы
- set_light_state: управлять светом (device_id, state)
- get_temperature: получить температуру (device_id)
- get_door_status: проверить статус двери (device_id)
- get_motion_status: проверить движение (device_id)
- set_fan_speed: установить скорость вентилятора (device_id, speed)

Ты работаешь в цикле "Мысль - Действие - Наблюдение" и всегда заботишься о безопасности.

Формат для вызова инструмента:
<function_calls>
[{{"name": "инструмент", "arguments": {{"аргументы"}}}}]
</function_calls>

Отвечай на русском языке.
"""
    
    def chat_with_user(self, user_input: str) -> str:
        """Общение с пользователем через Ollama с безопасностью"""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                tools=self.interface.tools,
                options={"temperature": 0.1}
            )
            
            message = response['message']
            
            if 'tool_calls' in message and message['tool_calls']:
                tool_results = []
                
                for tool_call in message['tool_calls']:
                    tool_name = tool_call['function']['name']
                    arguments = json.loads(tool_call['function']['arguments'])
                    
                    # Выполняем команду через безопасный интерфейс
                    result = self.safe_agent.execute_command_with_safety(tool_name, arguments)
                    
                    tool_results.append({
                        "role": "tool",
                        "content": json.dumps(result, ensure_ascii=False, indent=2),
                        "tool_call_id": tool_call['function'].get('id', '')
                    })
                
                # Добавляем результаты в историю и получаем финальный ответ
                for tool_result in tool_results:
                    self.conversation_history.append(tool_result)
                
                final_response = ollama.chat(
                    model=self.model_name,
                    messages=[{"role": "system", "content": self.system_prompt}] + self.conversation_history
                )
                
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": final_response['message']['content']
                })
                
                return final_response['message']['content']
            else:
                final_content = message['content']
                self.conversation_history.append({"role": "assistant", "content": final_content})
                return final_content
                
        except Exception as e:
            error_msg = f"Ошибка при обработке запроса: {e}"
            self.safe_agent.logger.error(error_msg)
            return error_msg
    
    def get_safety_report(self) -> str:
        """Возвращает отчет о безопасности"""
        report = self.safe_agent.get_safety_report()
        return f"Отчет о безопасности:\n- Режим безопасности: {'включен' if report['safety_mode'] else 'выключен'}\n- Всего команд: {report['total_commands']}\n- Заблокировано команд: {report['blocked_commands']}\n- Ограничения по частоте: {report['rate_limit_stats']}"

# Тестирование безопасного агента
if __name__ == "__main__":
    print("=== Тестирование безопасного ИИ-агента с Ollama ===")
    
    from ollama_arduino_tools import MockController
    mock_controller = MockController()
    ollama_interface = OllamaArduinoInterface(mock_controller)
    
    safe_agent = SafeOllamaSmartHomeAgent(ollama_interface)
    
    # Тестируем безопасность
    print("\n1. Безопасный запрос:")
    response1 = safe_agent.chat_with_user("Какая температура на кухне?")
    print(f"Ответ: {response1}")
    
    print("\n2. Еще один безопасный запрос:")
    response2 = safe_agent.chat_with_user("Статус входной двери")
    print(f"Ответ: {response2}")
    
    print(f"\n3. Отчет о безопасности:")
    print(safe_agent.get_safety_report())
    
    print("\nСистема безопасной интеграции Ollama с Arduino готова!")
```

## 6. Практическое приложение: Голосовой ассистент умного дома

Давайте создадим завершенный пример, который объединяет все компоненты:

```python
# complete_smart_home_assistant.py
import ollama
import json
import time
from typing import Dict, Any

class CompleteSmartHomeAssistant:
    """Полноценный ассистент умного дома с Ollama"""
    
    def __init__(self, controller):
        from ollama_arduino_tools import OllamaArduinoInterface
        from safe_ollama_agent import SafeOllamaSmartHomeAgent
        
        self.interface = OllamaArduinoInterface(controller)
        self.agent = SafeOllamaSmartHomeAgent(self.interface)
        
        self.system_info = {
            "name": "Умный Дом Ассистент",
            "version": "1.0",
            "capabilities": [
                "Мониторинг температуры",
                "Контроль дверей",
                "Датчики движения",
                "Управление освещением",
                "Управление вентиляцией",
                "Система безопасности"
            ]
        }
    
    def start_interactive_session(self):
        """Запускает интерактивную сессию с пользователем"""
        print("="*60)
        print(f"Добро пожаловать в {self.system_info['name']} v{self.system_info['version']}!")
        print("Доступные возможности:")
        for cap in self.system_info['capabilities']:
            print(f"  - {cap}")
        print("Введите 'help' для справки, 'quit' для выхода")
        print("="*60)
        
        while True:
            try:
                user_input = input("\nВы: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'выйти', 'стоп']:
                    print("До свидания!")
                    break
                
                elif user_input.lower() in ['help', 'помощь']:
                    self.show_help()
                    continue
                
                elif user_input.lower() in ['status', 'статус']:
                    response = self.agent.chat_with_user("Покажи полный статус системы")
                    print(f"Ассистент: {response}")
                    continue
                
                elif user_input.lower() in ['safety', 'безопасность']:
                    print(f"Ассистент: {self.agent.get_safety_report()}")
                    continue
                
                if user_input:
                    response = self.agent.chat_with_user(user_input)
                    print(f"Ассистент: {response}")
            
            except KeyboardInterrupt:
                print("\n\nРабота остановлена пользователем")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
    
    def show_help(self):
        """Показывает справочную информацию"""
        help_text = """
Доступные команды:
- 'Какая температура в [место]?' - узнать температуру
- 'Статус двери' или 'Проверь дверь' - проверить статус двери
- 'Включи/выключи свет в [место]' - управлять освещением
- 'Активируй сигнализацию' - включить систему безопасности
- 'Скорость вентилятора [число]' - установить скорость вентилятора
- 'Покажи статус системы' - получить полный статус
- 'help' - показать эту справку
- 'safety' - показать отчет о безопасности
- 'quit' - выйти из программы
        """
        print(help_text)

# Тестирование полного ассистента
if __name__ == "__main__":
    print("=== Запуск полного ассистента умного дома с Ollama ===")
    
    # Создаем фиктивный контроллер для демонстрации
    from ollama_arduino_tools import MockController
    mock_controller = MockController()
    
    # Создаем ассистента
    assistant = CompleteSmartHomeAssistant(mock_controller)
    
    print("\nАссистент готов к работе!")
    print("Для полного функционирования подключите реальные Arduino устройства")
    
    # Показываем возможности
    print(f"\nВозможности системы:")
    for cap in assistant.system_info['capabilities']:
        print(f"  • {cap}")
    
    # Запускаем интерактивную сессию
    print("\nЗапуск интерактивной сессии (для тестирования)...")
    # assistant.start_interactive_session()  # Закомментировано для автоматического выполнения
    
    print("\n=== Краткий тест функций ===")
    test_queries = [
        "Какая температура в кухне?",
        "Статус входной двери",
        "Покажи полный статус системы"
    ]
    
    for query in test_queries:
        print(f"\nПользователь: {query}")
        response = assistant.agent.chat_with_user(query)
        print(f"Ассистент: {response}")
    
    # Показываем отчет о безопасности
    print(f"\nОтчет о безопасности: {assistant.agent.get_safety_report()}")
    
    print("\nИнтеграция Ollama с Arduino системой успешно завершена!")
```

## 7. Заключение: Полноценная система с Ollama

Теперь у нас есть полная система, которая объединяет:

1. **Физические устройства** (Arduino с сенсорами и исполнительными механизмами)
2. **Протокол связи** (надежная коммуникация с контролем ошибок)
3. **Локальную LLM модель** (Ollama с доступом к физическим устройствам через инструменты)
4. **Безопасность** (проверки и ограничения для безопасного управления)
5. **Адаптивность** (возможность реагировать на естественный язык)

### Архитектура полной системы:
```
Пользователь (естественный язык)
        ↓
[Ollama LLM] ← понимание и рассуждение
        ↓
[Система инструментов] ← безопасный доступ к устройствам
        ↓
[Протокол связи] ← надежная передача команд
        ↓
[Arduino устройства] ← физические сенсоры и исполнительные механизмы
        ↓
[Физический мир] ← измерения, действия, состояния
        ↓
[Обратная связь → к Ollama] ← информация для следующих решений
```

Это создает **истинно интеллектуальную систему**, которая может понимать естественный язык через Ollama, принимать решения на основе данных с физических устройств и выполнять физические действия, создавая полноценный цикл "понимание - рассуждение - действие - наблюдение".

### Итоговая архитектура проекта:

В рамках проекта была реализована полная интеграция Ollama с Arduino системой:

- **Lesson 1**: Введение в Ollama + Arduino, базовая интеграция инструментов
- **Lesson 2**: Протоколы связи с использованием Ollama для обработки команд
- **Lesson 3**: Двунаправленное взаимодействие с использованием Ollama
- **Lesson 4**: Безопасность и отказоустойчивость с Ollama
- **Lesson 5**: Полноценная интеграция Ollama с физическими устройствами

Таким образом, все уроки в папке agent_controller теперь полностью интегрированы с Ollama, предоставляя студентам полное понимание того, как создавать интеллектуальные физические системы с использованием локальной LLM.