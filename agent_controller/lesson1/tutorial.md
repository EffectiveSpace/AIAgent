# Lesson AC-1: Введение в ИИ-агентов и микроконтроллеры через протоколы

## Цели урока

После изучения этого урока вы сможете:
- Объяснить, как ИИ-агент может взаимодействовать с физическим миром через микроконтроллеры
- Понять основы протоколов связи между компьютером и микроконтроллером
- Описать архитектуру системы "ИИ-агент ↔ протокол ↔ микроконтроллер"
- Подготовить среду для разработки и тестирования взаимодействия ИИ-агента с Arduino

## 1. Введение: Мост между цифровым и физическим миром

Мы изучили, как ИИ-агенты могут анализировать информацию, принимать решения и взаимодействовать с цифровыми системами (базами данных, API, файлами). Но настоящая сила ИИ-агентов раскрывается, когда они могут **влиять на физический мир**.

Представьте:
- ИИ-агент, который наблюдает за уровнем влажности в теплице через сенсоры и управляет системой полива
- ИИ-агент, который анализирует трафик и управляет светофорами в реальном времени
- ИИ-агент, который следит за безопасностью дома и управляет замками, камерами и сигнализацией

Все это возможно благодаря **протоколам связи** — стандартизированным способам обмена информацией между цифровым интеллектом и физическими устройствами.

### Архитектура системы "ИИ-агент ↔ протокол ↔ микроконтроллер"

```
[ИИ-агент в Python]
        ↓ (рассуждение → команда)
[Протокол (Python ↔ Arduino)]
        ↓ (последовательная передача данных)
[Микроконтроллер (Arduino)]
        ↓ (физическое выполнение)
[Сенсоры, исполнительные механизмы]
```

ИИ-агент остается "мозгом" системы, но теперь у нее есть "руки и ноги" — физические устройства, управляемые микроконтроллерами. Протокол — это язык, на котором они общаются.

## 2. Почему микроконтроллеры и протоколы?

### Микроконтроллеры (например, Arduino) — это:
- **Недорогие**: Стоят от $5 до $50
- **Простые в программировании**: Доступный язык C/C++
- **Интерфейсные**: Имеют GPIO пины для подключения сенсоров и исполнительных устройств
- **Реал-тайм**: Могут обрабатывать сигналы в реальном времени

### Протоколы связи — это:
- **Надежные**: Обеспечивают корректную передачу данных
- **Стандартизированные**: Могут быть поняты как Python, так и Arduino кодом
- **Гибкие**: Могут передавать любые данные (команды, сенсорную информацию и т.д.)

### Сравнение подходов

| Подход | Плюсы | Минусы |
|--------|--------|--------|
| Только Python | Простой код, мощные вычисления | Ограниченное взаимодействие с физическим миром |
| Python ↔ API устройства | Простая интеграция с готовыми системами | Зависимость от производителя, ограниченная гибкость |
| **Python ↔ протокол ↔ микроконтроллер** | **Полный контроль, низкая цена, гибкость** | **Требуется знание электроники и протоколов** |

## 3. Архитектура ИИ-агента для физического взаимодействия с использованием Ollama

В главах 1-4 мы изучили архитектуру ИИ-агента:
- **Мозг (LLM)**: Принимает решения
- **Инструменты**: Выполняют действия
- **Память**: Сохраняет контекст
- **Планировщик и цикл ReAct**: Управляет процессом

Теперь мы **расширим инструменты**, добавив туда **функции для общения с микроконтроллерами**, и интегрируем **локальную LLM (Ollama)**:

```
Новая архитектура:
[Ollama LLM] → [Инструменты: web_search, calculator, file_reader, ... , send_command_to_arduino] → [Физическое выполнение]
```

### Подготовка Ollama для работы с Arduino

Прежде чем интегрировать LLM, убедитесь, что Ollama установлена и запущена:

```bash
# Проверьте, что Ollama запущена в фоне
ollama serve

# Скачайте модель
ollama pull llama3
```

### Пример расширенного системного промпта для Ollama:

```
Ты — ИИ-агент "PhysicalAgent-Ollama", способный управлять физическими устройствами через Arduino.

Ты имеешь доступ к следующим инструментам:
- `search_web(query: str)`: Поиск в интернете
- `send_command_to_arduino(command: str, params: dict)`: Отправка команды на Arduino
  Примеры команд: "led_on", "led_off", "read_sensor", "set_servo_angle"
- `finish_task(final_answer: str)`: Финальный ответ

Ты работаешь в цикле "Мысль → Действие → Наблюдение" и можешь управлять физическими устройствами.
```

### Интеграция Ollama с Arduino инструментами

Теперь мы можем использовать Ollama для понимания команд пользователя и выбора подходящих инструментов:

```python
# ollama_arduino_integration.py
import ollama
import json
from arduino_tool import create_arduino_tool

# Создаем инструмент для Arduino
arduino_tool = create_arduino_tool()

# Определяем инструменты для Ollama
tools = [
    {
        "type": "function",
        "function": {
            "name": "send_command_to_arduino",
            "description": "Отправка команды на Arduino устройство",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Команда для Arduino (led_on, led_off, read_sensor, set_servo_angle)"
                    },
                    "params": {
                        "type": "object",
                        "description": "Параметры команды"
                    }
                },
                "required": ["command"]
            }
        }
    }
]

def run_ollama_agent_with_arduino(user_request: str) -> str:
    """
    Запускает Ollama агент, который может управлять Arduino
    """
    system_prompt = """
    Ты — ИИ-агент, способный управлять физическими устройствами через Arduino.
    Используй инструмент send_command_to_arduino для взаимодействия с Arduino.
    command может быть: "led_on", "led_off", "read_sensor", "set_servo_angle".
    params может содержать дополнительные параметры, если они требуются.
    Отвечай на русском языке.
    """

    try:
        # Вызываем Ollama с инструментами
        response = ollama.chat(
            model='llama3',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            tools=tools,
            options={"temperature": 0.3}  # Меньше творчества, больше точности
        )

        message = response['message']

        # Проверяем, вызваны ли инструменты
        if 'tool_calls' in message and message['tool_calls']:
            # Обрабатываем вызовы инструментов
            for tool_call in message['tool_calls']:
                function_name = tool_call['function']['name']
                arguments = json.loads(tool_call['function']['arguments'])

                if function_name == "send_command_to_arduino":
                    # Выполняем команду Arduino
                    result = arduino_tool(arguments.get('command'), arguments.get('params'))

                    # Получаем финальный ответ от Ollama с учетом результата инструмента
                    final_response = ollama.chat(
                        model='llama3',
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_request},
                            {"role": "tool", "content": result}
                        ]
                    )

                    return final_response['message']['content']

        # Если инструменты не вызваны, возвращаем обычный ответ
        return message['content']

    except Exception as e:
        return f"Ошибка при работе с Ollama: {e}"

# Тестирование интеграции Ollama + Arduino
if __name__ == "__main__":
    print("=== Тестирование Ollama агента с Arduino ===")

    test_queries = [
        "Включи светодиод на Arduino",
        "Прочитай значение с датчика",
        "Найди информацию о датчиках температуры"  # Эта команда не будет использовать Arduino
    ]

    for query in test_queries:
        print(f"\nЗапрос: {query}")
        result = run_ollama_agent_with_arduino(query)
        print(f"Результат: {result}")
```

## 4. Введение в протоколы: Структура пакета для Arduino

Из нашего туториала по протоколам мы знаем, что эффективный протокол должен быть:

```
[SYNC1, SYNC2, LEN_DATA, DATA..., CRC]
```

### Объяснение:
- `SYNC1, SYNC2`: Синхронизация (например, 0xAA, 0x55)
- `LEN_DATA`: Количество байт данных
- `DATA`: Полезная нагрузка
- `CRC`: Контрольная сумма

### Примеры пакетов:

**Команда "включить светодиод"**:
```
[0xAA, 0x55, 0x01, 0x01, 0x57]  // 0x01 = команда включения LED
```

**Команда "установить угол сервопривода"**:
```
[0xAA, 0x55, 0x02, 0x03, 0x90, 0xE8]  // 0x03 = команда серво, 0x90 = 144 градуса
```

**Ответ с данными сенсора**:
```
[0xAA, 0x55, 0x02, 0x04, 0x19, 0x7E]  // 0x04 = команда чтения сенсора, 0x19 = 25 (температура)
```

## 5. Подготовка среды: Установка и настройка

### Шаг 1: Установка Arduino IDE
Скачайте и установите Arduino IDE с официального сайта: https://www.arduino.cc/en/software

### Шаг 2: Подключение Arduino
Подключите вашу Arduino (например, Arduino Uno) к компьютеру через USB

### Шаг 3: Установка Python библиотек
```bash
pip install pyserial
```

### Шаг 4: Тестирование соединения
```python
import serial
import time

# Найдите правильный порт (в Windows это COM3, COM4 и т.д.)
# В Arduino IDE: Инструменты → Порт, чтобы увидеть правильный порт
ser = serial.Serial('COM3', 9600, timeout=1)  # Замените COM3 на ваш порт
time.sleep(2)

ser.write(b'test\n')  # Отправить тестовое сообщение
response = ser.readline()  # Прочитать ответ
print(f"Ответ от Arduino: {response}")

ser.close()
```

### Шаг 5: Тестовая прошивка для Arduino
Загрузите следующий простой код в вашу Arduino:

```cpp
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readString();
    input.trim(); // удаляем пробелы
    if (input == "test") {
      Serial.println("Hello from Arduino!");
    }
  }
}
```

## 6. Создание первого инструмента для ИИ-агента с поддержкой Ollama

Теперь мы создадим **инструмент**, который наш ИИ-агент на базе Ollama сможет использовать для общения с Arduino.

```python
# arduino_tool.py
import serial
import time
from typing import Dict, Any

class ArduinoProtocol:
    def __init__(self, port: str = 'COM3', baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connect()

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Время на сброс Arduino
            print(f"Подключено к Arduino на порту {self.port}")
        except Exception as e:
            print(f"Ошибка подключения к Arduino: {e}")

    def send_command_to_arduino(self, command: str, params: Dict[str, Any] = None) -> str:
        """
        Отправляет команду на Arduino через протокол
        """
        # В реальности здесь будет отправка байтового пакета по протоколу
        # Для простоты сейчас отправляем текстовую команду

        if params:
            message = f"{command}:{params}\n"
        else:
            message = f"{command}\n"

        try:
            self.ser.write(message.encode())
            # Ждем ответ
            response = self.ser.readline().decode().strip()
            return f"Команда '{command}' выполнена. Ответ: {response}"
        except Exception as e:
            return f"Ошибка выполнения команды '{command}': {e}"

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

# Пример использования как инструмента для Ollama ИИ-агента
def create_arduino_tool():
    arduino = ArduinoProtocol()

    def send_command_to_arduino(command: str, params: Dict[str, Any] = None) -> str:
        result = arduino.send_command_to_arduino(command, params)
        return result

    # Закрываем соединение при завершении
    import atexit
    atexit.register(arduino.close)

    return send_command_to_arduino

# Тестирование
if __name__ == "__main__":
    # Создаем инструмент
    arduino_tool = create_arduino_tool()

    # Тестируем
    result = arduino_tool("test", {})
    print(result)
```

## 7. Интеграция инструмента в Ollama ИИ-агента

Теперь наш Ollama ИИ-агент сможет использовать физическое устройство как один из своих инструментов. В предыдущем примере мы уже видели базовую интеграцию, теперь рассмотрим более продвинутую реализацию:

```python
# ollama_agent_with_arduino.py
import ollama
import json
from arduino_tool import create_arduino_tool

# Создаем инструмент для Arduino
arduino_tool = create_arduino_tool()

# Определяем инструменты для Ollama
tools = [
    {
        "type": "function",
        "function": {
            "name": "send_command_to_arduino",
            "description": "Отправка команды на Arduino устройство",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": ["led_on", "led_off", "read_sensor", "set_servo_angle", "get_status"],
                        "description": "Команда для Arduino"
                    },
                    "params": {
                        "type": "object",
                        "description": "Дополнительные параметры команды"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Поиск информации в интернете",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def run_advanced_ollama_agent_with_arduino(user_request: str):
    """
    Запускает продвинутый Ollama агент с Arduino интеграцией
    """
    system_prompt = """
    Ты — ИИ-агент, способный управлять физическими устройствами через Arduino и искать информацию в интернете.
    Используй доступные инструменты в зависимости от запроса пользователя.
    Для управления Arduino используй инструмент send_command_to_arduino.
    Для поиска информации используй инструмент search_web.
    Отвечай на русском языке и будь максимально полезным.
    """

    try:
        # Вызываем Ollama с инструментами
        response = ollama.chat(
            model='llama3',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            tools=tools,
            options={"temperature": 0.3}
        )

        message = response['message']

        print(f"Ollama ответ: {message}")

        # Проверяем, вызваны ли инструменты
        if 'tool_calls' in message and message['tool_calls']:
            results = []
            for tool_call in message['tool_calls']:
                function_name = tool_call['function']['name']
                arguments = json.loads(tool_call['function']['arguments'])

                print(f"Вызов инструмента: {function_name} с аргументами: {arguments}")

                if function_name == "send_command_to_arduino":
                    result = arduino_tool(arguments.get('command'), arguments.get('params', {}))
                    results.append(result)
                    print(f"Результат от Arduino: {result}")

                elif function_name == "search_web":
                    # В реальном приложении тут будет реальный веб-поиск
                    result = f"Результат поиска для запроса '{arguments.get('query')}': [симуляция поиска]"
                    results.append(result)
                    print(f"Результат поиска: {result}")

            # Если были вызовы инструментов, получаем финальный ответ
            if results:
                # Формируем сообщение с результатами инструментов
                tool_results_content = "Результаты инструментов: " + "; ".join(results)

                final_response = ollama.chat(
                    model='llama3',
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_request},
                        {"role": "tool", "content": tool_results_content}
                    ]
                )

                return final_response['message']['content']

        # Если инструменты не вызваны, возвращаем обычный ответ
        return message['content']

    except Exception as e:
        return f"Ошибка при работе с Ollama: {e}"

# Тестирование продвинутой интеграции Ollama + Arduino
if __name__ == "__main__":
    print("=== Тестирование продвинутого Ollama агента с Arduino ===")

    test_queries = [
        "Включи светодиод на Arduino",
        "Прочитай значение с датчика на Arduino",
        "Найди мне информацию о датчиках температуры для Arduino"
    ]

    for query in test_queries:
        print(f"\n--- Запрос: {query} ---")
        result = run_advanced_ollama_agent_with_arduino(query)
        print(f"Финальный результат: {result}")
        print("-" * 50)
```

## 8. Заключение: Новый уровень ИИ-агентов с Ollama

В этой главе мы:
- Поняли концепцию интеграции ИИ-агентов с физическими устройствами
- Узнали, почему микроконтроллеры и протоколы являются идеальной платформой для этого
- Настроили среду для разработки, включая локальную LLM Ollama
- Создали первый инструмент для взаимодействия с Arduino
- Интегрировали этот инструмент в архитектуру Ollama ИИ-агента
- Научились использовать Ollama для понимания естественного языка и управления физическими устройствами

Теперь ваш Ollama ИИ-агент может не только мыслить, но и **действовать в физическом мире**, понимая команды на естественном языке. Это открывает безграничные возможности: от умного дома до робототехники, от автоматизации процессов до интерактивных инсталляций.

Следующие уроки будут развивать эту идею, добавляя более сложные протоколы, обработку данных сенсоров, FSM для надежного взаимодействия и продвинутые сценарии использования Ollama ИИ-агентов с микроконтроллерами.