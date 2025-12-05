# Lesson AC-3: Обработка ответов от Arduino в ИИ-агенте

## Цели урока

После изучения этого урока вы сможете:
- Декодировать и интерпретировать ответы от микроконтроллера
- Создать систему обработки различных типов ответов (статус, данные сенсоров, подтверждения)
- Интегрировать получение данных от Arduino в цикл ReAct ИИ-агента
- Реализовать двунаправленное взаимодействие между ИИ-агентом и микроконтроллером
- Обеспечить надежную обработку ошибок и исключительных ситуаций

## 1. Введение: Двунаправленное взаимодействие

В предыдущих уроках мы реализовали отправку команд от ИИ-агента к Arduino. Однако настоящая мощь системы раскрывается при **двунаправленном взаимодействии**, когда:

1. ИИ-агент отправляет команду на Arduino
2. Arduino выполняет команду и отправляет ответ
3. ИИ-агент обрабатывает ответ и принимает новое решение

Этот цикл позволяет реализовать:
- **Мониторинг состояния**: ИИ-агент может получать текущие данные с сенсоров
- **Обратную связь**: Подтверждение выполнения команд
- **Адаптивное поведение**: Реакция на изменения в физическом мире

### Примеры двунаправленного взаимодействия:

```
ИИ-агент: "Измерь температуру" → Arduino: "25°C"
ИИ-агент: "Включить отопление" → Arduino: "Выполнено" → ИИ-агент: "Подожди 5 минут" → ИИ-агент: "Проверь температуру" → Arduino: "27°C"
```

## 2. Структура ответов от Arduino: Кодирование информации

В предыдущем уроке мы определили структуру протокола для отправки команд. Теперь расширим её для обработки ответов.

### Формат ответа от Arduino:

```
[SYNC1, SYNC2, LEN_DATA, RESPONSE_TYPE, PAYLOAD..., CRC]
```

Где:
- `SYNC1, SYNC2`: Байты синхронизации (0xAA, 0x55)
- `LEN_DATA`: Общая длина данных (RESPONSE_TYPE + PAYLOAD)
- `RESPONSE_TYPE`: Тип ответа (код, описывающий содержимое)
- `PAYLOAD`: Полезная нагрузка (данные сенсора, статус и т.д.)
- `CRC`: Контрольная сумма

### Типы ответов:
- `0xF0`: Подтверждение выполнения команды (ACK)
- `0xF1`: Ответ с данными сенсора
- `0xF2`: Ответ со статусом устройства
- `0xFE`: Ошибка выполнения команды
- `0xFF`: Системное сообщение

### Примеры ответных пакетов:

**Подтверждение команды:**
```
[0xAA, 0x55, 0x02, 0xF0, 0x01, 0x3A]  // ACK для команды 0x01 (LED_ON)
```

**Данные сенсора:**
```
[0xAA, 0x55, 0x03, 0xF1, 0x04, 0x19, 0x2C]  // Температура 25°C (0x19) для команды 0x04
```

**Команда с ошибкой:**
```
[0xAA, 0x55, 0x02, 0xFE, 0x05, 0xCB]  // Ошибка для команды 0x05
```

## 3. Реализация обработки ответов в Python

Обновим наш протокол для обработки разных типов ответов:

```python
# response_handler.py
from typing import Dict, Any, Optional, Tuple
from protocol import Protocol

class ResponseType:
    """Типы ответов от Arduino"""
    ACK = 0xF0       # Подтверждение выполнения команды
    SENSOR_DATA = 0xF1  # Данные сенсора
    DEVICE_STATUS = 0xF2  # Статус устройства
    ERROR = 0xFE     # Ошибка выполнения команды
    SYSTEM_MSG = 0xFF  # Системное сообщение

class ResponseHandler:
    def __init__(self):
        self.protocol = Protocol()
        self.command_callbacks = {}  # Коллбэки для обработки ответов на команды
    
    def register_callback(self, command_code: int, callback_func):
        """Регистрирует callback для обработки ответа на конкретную команду"""
        self.command_callbacks[command_code] = callback_func
    
    def process_response(self, raw_data: list) -> Optional[Dict[str, Any]]:
        """
        Обрабатывает декодированные данные ответа от Arduino
        Возвращает структурированный ответ или None если данные некорректны
        """
        if not raw_data or len(raw_data) < 1:
            return None
        
        response_type = raw_data[0]
        
        if response_type == ResponseType.ACK:
            if len(raw_data) >= 2:
                command_code = raw_data[1]
                return {
                    "type": "ACK",
                    "command": command_code,
                    "status": "success",
                    "message": f"Команда {hex(command_code)} выполнена успешно"
                }
        
        elif response_type == ResponseType.SENSOR_DATA:
            if len(raw_data) >= 3:
                command_code = raw_data[1]
                # Предполагаем, что данные - это 16-битное значение (2 байта)
                value = (raw_data[2] << 8) | raw_data[3] if len(raw_data) >= 4 else raw_data[2]
                return {
                    "type": "SENSOR_DATA",
                    "command": command_code,
                    "value": value,
                    "raw_data": raw_data[2:],
                    "message": f"Данные сенсора: {value}"
                }
        
        elif response_type == ResponseType.DEVICE_STATUS:
            if len(raw_data) >= 2:
                led_status = raw_data[1]  # 1 = ON, 0 = OFF
                return {
                    "type": "DEVICE_STATUS",
                    "led_status": bool(led_status),
                    "message": f"Светодиод {'включен' if led_status else 'выключен'}"
                }
        
        elif response_type == ResponseType.ERROR:
            if len(raw_data) >= 2:
                error_code = raw_data[1]
                error_messages = {
                    0x01: "Неизвестная команда",
                    0x02: "Неверные параметры",
                    0x03: "Устройство занято",
                    0x04: "Ошибка сенсора"
                }
                message = error_messages.get(error_code, f"Неизвестная ошибка: {hex(error_code)}")
                return {
                    "type": "ERROR",
                    "error_code": error_code,
                    "message": message
                }
        
        elif response_type == ResponseType.SYSTEM_MSG:
            message = "".join(chr(b) for b in raw_data[1:] if 32 <= b <= 126)  # Только печатные символы
            return {
                "type": "SYSTEM_MSG",
                "message": message
            }
        
        return None  # Неизвестный тип ответа
    
    def handle_streaming_responses(self, byte_stream) -> Dict[str, Any]:
        """
        Обрабатывает поток байтов и возвращает информацию о полученном ответе
        """
        # В реальной реализации здесь будет обработка данных из serial порта
        # Пока что возвращаем заглушку
        pass

# Тестирование обработчика
if __name__ == "__main__":
    handler = ResponseHandler()
    
    # Тестовые ответы
    test_responses = [
        [0xF0, 0x01],  # ACK для команды 0x01
        [0xF1, 0x04, 0x00, 0x19],  # Данные сенсора: 25 (температура)
        [0xF2, 0x01],  # Статус: светодиод включен
        [0xFE, 0x01]   # Ошибка: неизвестная команда
    ]
    
    for response_data in test_responses:
        result = handler.process_response(response_data)
        print(f"Ответ: {response_data} -> {result}")
```

## 4. Обновленный интерфейс Arduino с обработкой ответов

Теперь мы обновим наш Arduino-интерфейс для полной обработки ответов:

```python
# enhanced_arduino_interface.py
import serial
import time
from typing import Dict, Any, Optional, Callable
from response_handler import ResponseHandler, ResponseType

class EnhancedArduinoInterface:
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.response_handler = ResponseHandler()
        self.connect()
    
    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Время на сброс Arduino
            print(f"Подключено к Arduino на порту {self.port}")
        except Exception as e:
            print(f"Ошибка подключения к Arduino: {e}")
            raise
    
    def send_command_get_response(self, command: int, params: Optional[list] = None, 
                                 timeout: float = 2.0) -> Dict[str, Any]:
        """
        Отправляет команду и ожидает ответ
        """
        # Формируем и отправляем пакет
        data = [command] + (params or [])
        packet = self.response_handler.protocol.encode_packet(data)
        
        try:
            self.ser.write(packet)
            print(f"Отправили команду: {hex(command)}, пакет: {[hex(b) for b in packet]}")
            
            # Ждем ответ
            response = self.wait_for_response(timeout)
            if response:
                return response
            else:
                return {
                    "type": "TIMEOUT",
                    "message": f"Таймаут ожидания ответа на команду {hex(command)}"
                }
        except Exception as e:
            return {
                "type": "EXCEPTION",
                "message": f"Ошибка при отправке команды: {e}"
            }
    
    def wait_for_response(self, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
        """
        Ожидает ответ от Arduino и обрабатывает его
        """
        start_time = time.time()
        buffer = bytearray()
        
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                byte = self.ser.read(1)[0]
                buffer.append(byte)
                
                # Проверяем, есть ли в буфере полный пакет
                result = self.response_handler.protocol.feed_byte(byte)
                if result is not None:
                    # Обрабатываем полученный пакет
                    processed = self.response_handler.process_response(result)
                    print(f"Получили и обработали пакет: {result} -> {processed}")
                    return processed
            else:
                # Небольшая задержка, чтобы не перегружать процессор
                time.sleep(0.001)
        
        return None
    
    def read_sensor(self, sensor_type: str = "temperature") -> Dict[str, Any]:
        """
        Удобная функция для чтения данных сенсора
        """
        if sensor_type == "temperature":
            # Команда чтения сенсора (0x04)
            return self.send_command_get_response(0x04, [1])  # Параметр: тип сенсора
        elif sensor_type == "light":
            return self.send_command_get_response(0x04, [2])  # Другой тип сенсора
        else:
            return {"type": "ERROR", "message": f"Неизвестный тип сенсора: {sensor_type}"}
    
    def get_device_status(self) -> Dict[str, Any]:
        """
        Получает статус устройства
        """
        return self.send_command_get_response(0x05)  # Команда получения статуса
    
    def set_servo_angle(self, angle: int) -> Dict[str, Any]:
        """
        Устанавливает угол сервопривода и ожидает подтверждения
        """
        if not 0 <= angle <= 180:
            return {"type": "ERROR", "message": "Угол должен быть от 0 до 180 градусов"}
        
        response = self.send_command_get_response(0x03, [angle])
        return response
    
    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

# Пример использования
if __name__ == "__main__":
    # Подключитесь к вашей Arduino
    arduino = EnhancedArduinoInterface('COM3')  # Замените на ваш порт
    
    print("=== Тестирование двунаправленного взаимодействия ===")
    
    # Тестируем команды с ожиданием ответов
    tests = [
        ("Статус устройства", lambda: arduino.get_device_status()),
        ("Чтение температуры", lambda: arduino.read_sensor("temperature")),
        ("Включить LED", lambda: arduino.send_command_get_response(0x01)),
        ("Выключить LED", lambda: arduino.send_command_get_response(0x02)),
        ("Чтение температуры после команды", lambda: arduino.read_sensor("temperature"))
    ]
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            print(f"  Результат: {result}")
        except Exception as e:
            print(f"  Ошибка: {e}")
    
    arduino.close()
```

## 5. Интеграция ответов в архитектуру ИИ-агента

Теперь мы интегрируем обработку ответов в архитектуру ИИ-агента, чтобы он мог использовать полученную информацию для принятия решений:

```python
# agent_with_responses.py
import json
import time
from typing import Dict, Any
from enhanced_arduino_interface import EnhancedArduinoInterface

class AgentWithResponses:
    def __init__(self, arduino_port: str = 'COM3'):
        self.arduino = EnhancedArduinoInterface(arduino_port)
        self.tools = {
            'send_command_get_response': self._send_command_get_response,
            'read_sensor': self._read_sensor,
            'get_device_status': self._get_device_status,
            'general_response': self._general_response
        }
        
        # История наблюдений для памяти агента
        self.observation_history = []
    
    def _send_command_get_response(self, command: str, params: Dict[str, Any] = None) -> str:
        """Отправляет команду и возвращает структурированный ответ"""
        command_map = {
            'LED_ON': 0x01,
            'LED_OFF': 0x02,
            'SET_SERVO_ANGLE': 0x03,
            'READ_SENSOR': 0x04,
            'GET_STATUS': 0x05
        }
        
        cmd_code = command_map.get(command)
        if cmd_code is None:
            return f"Неизвестная команда: {command}"
        
        # Подготовим параметры
        param_list = None
        if params:
            param_list = []
            for value in params.values():
                if isinstance(value, list):
                    param_list.extend([int(v) for v in value])
                else:
                    param_list.append(int(value))
        
        response = self.arduino.send_command_get_response(cmd_code, param_list)
        
        # Сохраняем наблюдение в истории
        self.observation_history.append({
            'command': command,
            'response': response,
            'timestamp': time.time()
        })
        
        return self._format_response(response)
    
    def _read_sensor(self, sensor_type: str = 'temperature') -> str:
        """Читает данные с сенсора"""
        response = self.arduino.read_sensor(sensor_type)
        
        # Сохраняем наблюдение
        self.observation_history.append({
            'command': f'READ_{sensor_type.upper()}_SENSOR',
            'response': response,
            'timestamp': time.time()
        })
        
        return self._format_response(response)
    
    def _get_device_status(self) -> str:
        """Получает статус устройства"""
        response = self.arduino.get_device_status()
        
        # Сохраняем наблюдение
        self.observation_history.append({
            'command': 'GET_DEVICE_STATUS',
            'response': response,
            'timestamp': time.time()
        })
        
        return self._format_response(response)
    
    def _format_response(self, response: Dict[str, Any]) -> str:
        """Форматирует ответ для пользователя"""
        if response.get('type') == 'SENSOR_DATA':
            return f"Данные сенсора: {response.get('value', 'неизвестно')}"
        elif response.get('type') == 'DEVICE_STATUS':
            led_status = response.get('led_status', False)
            return f"Статус устройства: светодиод {'включен' if led_status else 'выключен'}"
        elif response.get('type') == 'ACK':
            return f"Команда выполнена успешно: {response.get('message', '')}"
        elif response.get('type') == 'ERROR':
            return f"Ошибка выполнения команды: {response.get('message', '')}"
        elif response.get('type') == 'TIMEOUT':
            return f"Таймаут: {response.get('message', '')}"
        else:
            return str(response)
    
    def _general_response(self, query: str) -> str:
        return f"Я понимаю ваш запрос: '{query}', но не могу выполнить его без специальных инструментов."
    
    def choose_tool(self, user_query: str) -> dict:
        """Определяет, какой инструмент использовать"""
        # Анализируем запрос и выбираем подходящий инструмент
        if "температура" in user_query.lower() or "сенсор" in user_query.lower():
            return {
                "tool_name": "read_sensor",
                "arguments": {"sensor_type": "temperature"}
            }
        elif "статус" in user_query.lower() or "состояние" in user_query.lower():
            return {
                "tool_name": "get_device_status",
                "arguments": {}
            }
        elif "вкл" in user_query.lower() or "включ" in user_query.lower():
            return {
                "tool_name": "send_command_get_response",
                "arguments": {"command": "LED_ON", "params": {}}
            }
        elif "выкл" in user_query.lower() or "откл" in user_query.lower():
            return {
                "tool_name": "send_command_get_response",
                "arguments": {"command": "LED_OFF", "params": {}}
            }
        elif "угол" in user_query.lower() or "серво" in user_query.lower():
            import re
            angle_match = re.search(r'(\d+)', user_query)
            angle = int(angle_match.group(1)) if angle_match else 90
            return {
                "tool_name": "send_command_get_response",
                "arguments": {"command": "SET_SERVO_ANGLE", "params": {"angle": angle}}
            }
        else:
            return {
                "tool_name": "general_response",
                "arguments": {"query": user_query}
            }
    
    def run(self, user_request: str) -> str:
        """Выполняет запрос пользователя"""
        tool_choice = self.choose_tool(user_request)
        tool_name = tool_choice["tool_name"]
        arguments = tool_choice["arguments"]
        
        if tool_name in self.tools:
            result = self.tools[tool_name](**arguments)
            return result
        else:
            return f"Неизвестный инструмент: {tool_name}"

# Демонстрация цикла ReAct с использованием ответов
def demonstrate_react_cycle():
    """
    Демонстрирует, как ответы от Arduino влияют на принятие решений ИИ-агентом
    """
    print("=== Демонстрация цикла ReAct с ответами от Arduino ===")
    
    agent = AgentWithResponses()
    
    # Сценарий: "Если температура выше 25, включи вентилятор"
    print("\nСценарий: Проверка температуры и управление по результату")
    
    # 1. Получаем текущую температуру
    temp_response = agent.read_sensor("temperature")
    print(f"Мышль: Анализирую текущую температуру: {temp_response}")
    
    # 2. Извлекаем значение температуры из ответа
    try:
        temp_value = int(temp_response.split()[-1]) if "Данные сенсора:" in temp_response else 0
    except:
        temp_value = 0
    
    # 3. Принимаем решение на основе полученной информации
    if temp_value > 25:
        print(f"Действие: Температура {temp_value} > 25, включаю светодиод (вентилятор)")
        fan_response = agent.send_command_get_response("LED_ON")
        print(f"Наблюдение: {fan_response}")
    else:
        print(f"Действие: Температура {temp_value} <= 25, ничего не делаю")
    
    # 4. Проверяем конечное состояние
    status_response = agent.get_device_status()
    print(f"Завершено. Статус: {status_response}")

if __name__ == "__main__":
    # Тестируем обычного агента
    agent = AgentWithResponses()
    
    test_queries = [
        "Какая температура?",
        "Покажи статус устройства",
        "Включи светодиод",
        "Выключи светодиод"
    ]
    
    print("=== Тестирование агента с обработкой ответов ===")
    for query in test_queries:
        print(f"\nЗапрос: {query}")
        result = agent.run(query)
        print(f"Ответ: {result}")
    
    # Демонстрация цикла ReAct
    demonstrate_react_cycle()
    
    agent.arduino.close()
```

## 6. Продвинутая обработка ответов: Понимание контекста

В реальных приложениях ответ от Arduino должен быть интерпретирован в контексте предыдущих действий и текущей цели. Создадим систему, которая учитывает этот контекст:

```python
# contextual_response_processor.py
from typing import Dict, List, Any, Optional
import time

class ContextualResponseProcessor:
    """
    Обрабатывает ответы от Arduino в контексте текущей цели и истории действий
    """
    
    def __init__(self):
        self.action_history = []  # История отправленных команд
        self.observation_history = []  # История полученных ответов
        self.current_goal = None  # Текущая цель агента
        self.context_variables = {}  # Переменные контекста
    
    def set_goal(self, goal: str):
        """Устанавливает текущую цель агента"""
        self.current_goal = goal
        print(f"Установлена цель: {goal}")
    
    def record_action(self, action: Dict[str, Any]):
        """Записывает отправленное действие в историю"""
        record = {
            'timestamp': time.time(),
            'action': action,
            'goal_context': self.current_goal
        }
        self.action_history.append(record)
        print(f"Записано действие: {action}")
    
    def process_response_in_context(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает ответ в контексте текущей цели и истории действий
        """
        # Определяем, что это за ответ и как он соотносится с последним действием
        latest_action = self.action_history[-1] if self.action_history else None
        
        processed_response = {
            'original_response': response,
            'context_analysis': {},
            'recommendations': []
        }
        
        if latest_action:
            action_type = latest_action['action'].get('command', 'unknown')
            
            if response.get('type') == 'ACK':
                processed_response['context_analysis']['success'] = True
                processed_response['context_analysis']['action_completed'] = action_type
                
                # В зависимости от типа действия, можем добавить дополнительный контекст
                if action_type == 'READ_SENSOR':
                    processed_response['recommendations'].append("Проанализировать полученное значение")
                elif action_type == 'LED_ON':
                    processed_response['recommendations'].append("Подождать и проверить результат")
            
            elif response.get('type') == 'SENSOR_DATA':
                value = response.get('value', 0)
                processed_response['context_analysis']['sensor_value'] = value
                
                # Анализ значения в контексте цели
                if self.current_goal and 'температура' in self.current_goal.lower():
                    if value > 30:
                        processed_response['recommendations'].append("Температура высокая - активировать охлаждение")
                    elif value < 18:
                        processed_response['recommendations'].append("Температура низкая - активировать обогрев")
                    else:
                        processed_response['recommendations'].append("Температура в норме")
        
        # Сохраняем наблюдение
        observation = {
            'timestamp': time.time(),
            'response': response,
            'processed': processed_response,
            'goal_context': self.current_goal
        }
        self.observation_history.append(observation)
        
        return processed_response
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Возвращает краткое состояние контекста"""
        return {
            'current_goal': self.current_goal,
            'actions_count': len(self.action_history),
            'observations_count': len(self.observation_history),
            'latest_observation': self.observation_history[-1] if self.observation_history else None,
            'context_variables': self.context_variables
        }

# Интеграция с агентом
class ContextAwareAgent(AgentWithResponses):
    def __init__(self, arduino_port: str = 'COM3'):
        super().__init__(arduino_port)
        self.context_processor = ContextualResponseProcessor()
    
    def run_with_context(self, user_request: str):
        """Запускает агента с учетом контекста"""
        self.context_processor.set_goal(user_request)
        
        # Выбираем инструмент как обычно
        tool_choice = self.choose_tool(user_request)
        tool_name = tool_choice["tool_name"]
        arguments = tool_choice["arguments"]
        
        # Записываем действие в контекст
        action_record = {
            'tool_name': tool_name,
            'arguments': arguments
        }
        self.context_processor.record_action(action_record)
        
        # Выполняем действие
        if tool_name in self.tools:
            result = self.tools[tool_name](**arguments)
            
            # Если результат - это ответ от Arduino, обрабатываем его в контексте
            if isinstance(result, str) and "Данные сенсора:" in result:
                # Это упрощенная демонстрация - в реальности нужно парсить структурированные ответы
                response_obj = {
                    'type': 'SENSOR_DATA',
                    'value': self._extract_value(result)
                }
                processed = self.context_processor.process_response_in_context(response_obj)
                print(f"Контекстная обработка: {processed}")
                
            return result
        else:
            return f"Неизвестный инструмент: {tool_name}"
    
    def _extract_value(self, response_str: str) -> int:
        """Извлекает числовое значение из строкового ответа (для демонстрации)"""
        try:
            import re
            numbers = re.findall(r'\d+', response_str)
            return int(numbers[0]) if numbers else 0
        except:
            return 0

# Демонстрация контекстной обработки
if __name__ == "__main__":
    print("=== Демонстрация контекстной обработки ответов ===")
    
    agent = ContextAwareAgent()
    
    # Сценарий: Управление температурой
    goal = "Поддерживать температуру в диапазоне 20-25 градусов"
    print(f"Цель: {goal}")
    
    # Шаг 1: Проверить текущую температуру
    temp_result = agent.run_with_context("Какая температура?")
    print(f"Температура: {temp_result}")
    
    # Показать контекст
    context = agent.context_processor.get_context_summary()
    print(f"Контекст: {context}")
    
    agent.arduino.close()
```

## 7. Обработка ошибок и отказов

Важной частью надежного взаимодействия является корректная обработка ошибок:

```python
# error_handling.py
from typing import Dict, Any

class RobustResponseHandler:
    """
    Обработка ответов с учетом возможных ошибок
    """
    
    def __init__(self):
        self.error_history = []
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
    
    def handle_response_with_error_checking(self, response: Dict[str, Any], 
                                          original_command: str = None) -> Dict[str, Any]:
        """
        Обрабатывает ответ и проверяет на ошибки
        """
        if response.get('type') == 'ERROR':
            error_code = response.get('error_code')
            error_msg = response.get('message', 'Неизвестная ошибка')
            
            print(f"Ошибка выполнения команды: {original_command}, код: {error_code}, сообщение: {error_msg}")
            
            # Записываем ошибку в историю
            error_record = {
                'timestamp': time.time(),
                'original_command': original_command,
                'error_code': error_code,
                'error_message': error_msg
            }
            self.error_history.append(error_record)
            
            # Пытаемся восстановиться
            recovery_result = self.attempt_recovery(error_code, original_command)
            return {
                'type': 'ERROR_HANDLED',
                'original_error': response,
                'recovery_attempt': recovery_result
            }
        
        elif response.get('type') == 'TIMEOUT':
            error_record = {
                'timestamp': time.time(),
                'original_command': original_command,
                'error_code': 'TIMEOUT',
                'error_message': response.get('message', 'Таймаут соединения')
            }
            self.error_history.append(error_record)
            
            print(f"Таймаут команды: {original_command}")
            recovery_result = self.attempt_recovery('TIMEOUT', original_command)
            return {
                'type': 'TIMEOUT_HANDLED',
                'original_error': response,
                'recovery_attempt': recovery_result
            }
        
        # Если ошибок нет, просто возвращаем оригинальный ответ
        return response
    
    def attempt_recovery(self, error_code: Any, command: str) -> str:
        """
        Пытается восстановиться после ошибки
        """
        attempt_key = f"{command}_{error_code}"
        
        if attempt_key not in self.recovery_attempts:
            self.recovery_attempts[attempt_key] = 0
        
        self.recovery_attempts[attempt_key] += 1
        attempt_num = self.recovery_attempts[attempt_key]
        
        if attempt_num > self.max_recovery_attempts:
            print(f"Достигнуто максимальное количество попыток восстановления для {command}")
            return f"FAILED_AFTER_{self.max_recovery_attempts}_ATTEMPTS"
        
        # В зависимости от типа ошибки, можно предпринять разные действия
        if error_code in ['TIMEOUT', '0xFE']:  # Таймаут или общая ошибка
            print(f"Попытка восстановления {attempt_num}/{self.max_recovery_attempts}")
            time.sleep(0.5 * attempt_num)  # Увеличиваем задержку с каждой попыткой
            return f"RETRY_ATTEMPT_{attempt_num}"
        else:
            print(f"Невозможно восстановиться от ошибки: {error_code}")
            return "CANNOT_RECOVER"
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по ошибкам"""
        return {
            'total_errors': len(self.error_history),
            'recent_errors': self.error_history[-5:],  # Последние 5 ошибок
            'recovery_stats': self.recovery_attempts
        }

# Интеграция в агент
class ErrorHandlingAgent(ContextAwareAgent):
    def __init__(self, arduino_port: str = 'COM3'):
        super().__init__(arduino_port)
        self.error_handler = RobustResponseProcessor()
    
    def _format_response(self, response: Dict[str, Any]) -> str:
        """Форматирует ответ, обрабатывая ошибки"""
        handled_response = self.error_handler.handle_response_with_error_checking(
            response, self._get_last_command()
        )
        
        # Показываем статистику ошибок периодически
        if len(self.error_handler.error_history) % 5 == 0 and self.error_handler.error_history:
            error_summary = self.error_handler.get_error_summary()
            print(f"Статистика ошибок: {error_summary}")
        
        return super()._format_response(handled_response)

def _get_last_command(self):
    """Получает последнюю отправленную команду (для демонстрации)"""
    # В реальной реализации это будет извлекаться из истории
    return "UNKNOWN_COMMAND"
```

## 8. Заключение: Замкнутый цикл взаимодействия

В этом уроке мы:
- Реализовали полноценную систему обработки ответов от Arduino
- Создали механизм интерпретации ответов в контексте цели агента
- Обеспечили двунаправленное взаимодействие "команда → ответ → новое решение"
- Добавили надежную обработку ошибок и восстановление
- Демонстрировали, как ИИ-агент может принимать решения на основе полученной информации

Теперь у нас есть **замкнутая система**, где ИИ-агент может:
1. **Воспринимать** информацию от физических устройств (сенсоры)
2. **Рассуждать** на основе полученных данных
3. **Действовать** на физические устройства (команды)
4. **Наблюдать** результаты своих действий

Это реализация полного цикла "Восприятие – Рассуждение – Действие – Наблюдение", который делает ИИ-агентов по-настоящему мощными инструментами для взаимодействия с физическим миром.

В следующем уроке мы углубимся в реализацию FSM и enum на стороне Arduino для более надежной обработки протокола, что еще больше повысит надежность и функциональность системы.