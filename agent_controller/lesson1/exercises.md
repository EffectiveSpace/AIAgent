# Упражнения к Lesson AC-1: Введение в ИИ-агентов и микроконтроллеры через протоколы

## Упражнение AC-1.1: Подготовка среды разработки

### Цель
Настроить среду для взаимодействия ИИ-агента с микроконтроллером Arduino.

### Задание
1. Установите Arduino IDE с официального сайта
2. Установите Python библиотеку `pyserial`
3. Подключите Arduino к компьютеру и определите, какой порт она использует
4. Загрузите тестовую прошивку в Arduino, которая отвечает на команду "test" сообщением "Hello from Arduino!"

### Файл для прошивки Arduino
```cpp
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readString();
    input.trim();
    if (input == "test") {
      Serial.println("Hello from Arduino!");
    } else {
      Serial.println("Unknown command");
    }
  }
}
```

### Python-скрипт для тестирования
```python
import serial
import time

# ПОМНИТЕ: замените 'COM3' на правильный порт вашей Arduino!
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Даем время на сброс Arduino

ser.write(b'test\n')
response = ser.readline().decode().strip()
print(f"Ответ от Arduino: {response}")

ser.close()
```

### Контрольный вопрос
Что выведет Python-скрипт, если все подключено правильно?

<details>
<summary>Ответ</summary>
"Ответ от Arduino: Hello from Arduino!"
</details>

## Упражнение AC-1.2: Создание инструмента для ИИ-агента

### Цель
Реализовать базовый инструмент, который позволяет ИИ-агенту отправлять простые команды на Arduino.

### Задание
1. Создайте Python-класс `ArduinoInterface`, который:
   - Подключается к Arduino через последовательный порт
   - Может отправлять текстовые команды
   - Может получать ответы от Arduino
   - Обрабатывает ошибки подключения

2. Реализуйте метод `send_command(command)` который:
   - Отправляет команду на Arduino
   - Возвращает ответ
   - Обрабатывает таймауты

### Пример реализации
```python
import serial
import time
from typing import Optional

class ArduinoInterface:
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.ser: Optional[serial.Serial] = None
        self.connect()
    
    def connect(self):
        """Подключается к Arduino"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Время на сброс Arduino
            print(f"Подключено к Arduino на порту {self.port}")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
    
    def send_command(self, command: str) -> str:
        """Отправляет команду на Arduino и возвращает ответ"""
        if not self.ser or not self.ser.is_open:
            return "Ошибка: нет подключения к Arduino"
        
        try:
            # Отправляем команду
            self.ser.write(f"{command}\n".encode())
            
            # Читаем ответ
            response = self.ser.readline().decode().strip()
            
            return response if response else "Нет ответа"
        except Exception as e:
            return f"Ошибка при отправке команды: {e}"
    
    def close(self):
        """Закрывает соединение"""
        if self.ser and self.ser.is_open:
            self.ser.close()

# Использование
if __name__ == "__main__":
    arduino = ArduinoInterface('COM3')  # Замените на ваш порт
    
    # Тестируем
    response = arduino.send_command("test")
    print(f"Ответ: {response}")
    
    arduino.close()
```

### Проверка
Протестируйте ваш класс с командой "test" и убедитесь, что получаете правильный ответ от Arduino.

## Упражнение AC-1.3: Интеграция инструмента в ИИ-агента

### Цель
Интегрировать наш Arduino-инструмент в архитектуру ИИ-агента.

### Задание
Создайте простого ИИ-агента (на основе логики из урока 3), который может:
1. Принимать пользовательские запросы
2. Определять, нужно ли выполнить команду на Arduino
3. Использовать наш `ArduinoInterface` как инструмент
4. Возвращать результат пользователю

### Шаги реализации:
1. Создайте функцию `choose_tool(user_request)` которая:
   - Анализирует запрос пользователя
   - Возвращает название инструмента и аргументы

2. Добавьте в агента инструмент `send_to_arduino`

3. Создайте цикл выполнения, который:
   - Выбирает инструмент
   - Выполняет его
   - Возвращает результат

### Пример архитектуры
```python
import json
from arduino_interface import ArduinoInterface  # ваш класс из упражнения 2

class SimpleAgent:
    def __init__(self, arduino_port: str):
        self.arduino = ArduinoInterface(arduino_port)
        self.tools = {
            "send_to_arduino": self.arduino.send_command,
            "general_response": self.general_response
        }
    
    def general_response(self, query: str) -> str:
        """Ответ на общие запросы"""
        return f"Я не могу выполнить запрос '{query}' напрямую. Возможно, вам нужна информация из интернета?"
    
    def choose_tool(self, user_query: str) -> dict:
        """Определяет, какой инструмент использовать"""
        # Простая логика для определения запросов, связанных с Arduino
        arduino_keywords = ["ардуино", "светодиод", "led", "устройство", "физическое"]
        
        if any(keyword in user_query.lower() for keyword in arduino_keywords):
            # Извлекаем команду из запроса
            if "вкл" in user_query.lower() or "включ" in user_query.lower():
                command = "led_on"
            elif "выкл" in user_query.lower() or "откл" in user_query.lower():
                command = "led_off"
            else:
                command = "status"
            
            return {
                "tool_name": "send_to_arduino",
                "arguments": {"command": command}
            }
        else:
            return {
                "tool_name": "general_response",
                "arguments": {"query": user_query}
            }
    
    def run(self, user_request: str) -> str:
        """Запускает выполнение запроса"""
        tool_choice = self.choose_tool(user_request)
        tool_name = tool_choice["tool_name"]
        arguments = tool_choice["arguments"]
        
        if tool_name in self.tools:
            result = self.tools[tool_name](**arguments)
            return result
        else:
            return f"Неизвестный инструмент: {tool_name}"

# Тестирование
if __name__ == "__main__":
    agent = SimpleAgent("COM3")  # Замените на ваш порт
    
    test_queries = [
        "Включи светодиод на Arduino",
        "Как дела?",
        "Отправь статус на Arduino",
        "Покажи статус устройства"
    ]
    
    for query in test_queries:
        print(f"\nЗапрос: {query}")
        result = agent.run(query)
        print(f"Результат: {result}")
```

### Тестирование
Проверьте, что ваш агент корректно распознает запросы, связанные с Arduino, и выполняет соответствующие команды.

## Упражнение AC-1.4: Анализ архитектуры "ИИ-агент ↔ Arduino"

### Цель
Понять, как компоненты ИИ-агента взаимодействуют с физическими устройствами.

### Задание
Ответьте на следующие вопросы:

1. Какую роль в архитектуре "ИИ-агент ↔ протокол ↔ Arduino" играет каждый компонент агента?
   - Мозг (LLM)
   - Инструменты
   - Память
   - Планировщик

2. В чем преимущества использования протокола вместо прямого текстового общения с Arduino?

3. Какие потенциальные проблемы могут возникнуть при физическом взаимодействии ИИ-агента?

### Пример рассуждения для вопроса 1:
- **Мозг (LLM)**: Принимает решение, когда и какую команду отправить на Arduino
- **Инструменты**: Реализуют физическую отправку команд и получение ответов
- **Память**: Может хранить состояния устройств, историю команд и т.д.
- **Планировщик**: Может строить многошаговые планы, включающие физические действия

## Упражнение AC-1.5: Расширение функциональности Arduino

### Цель
Добавить новые возможности к Arduino для расширения возможностей ИИ-агента.

### Задание
1. Модифицируйте прошивку Arduino так, чтобы она могла обрабатывать несколько команд:
   - `led_on` — включить встроенный светодиод
   - `led_off` — выключить встроенный светодиод
   - `get_temp` — симулировать чтение температуры
   - `status` — вернуть статус устройства

2. Обновите Python-интерфейс для поддержки этих новых команд

3. Протестируйте интеграцию с ИИ-агентом

### Пример обновленной прошивки
```cpp
// Определяем пины
const int LED_PIN = 13;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // Светодиод выключен по умолчанию
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    
    if (command == "led_on") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED turned ON");
    } else if (command == "led_off") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED turned OFF");
    } else if (command == "get_temp") {
      // Симулируем датчик температуры
      int temp = 23 + analogRead(A0) % 5;  // Симуляция с небольшими колебаниями
      Serial.println("Temperature: " + String(temp) + " C");
    } else if (command == "status") {
      String led_status = digitalRead(LED_PIN) ? "ON" : "OFF";
      Serial.println("Status - LED: " + led_status + ", Temp: ~23C");
    } else {
      Serial.println("Unknown command: " + command);
    }
  }
}
```

### Контрольные вопросы
1. Как ваш ИИ-агент может использовать команду `get_temp`?
2. Какие риски существуют при отправке команд вроде `led_on` и `led_off`?

## Упражнение AC-1.6: Проектирование безопасного взаимодействия

### Цель
Понять важность безопасности при взаимодействии ИИ-агентов с физическими устройствами.

### Задание
Разработайте систему безопасности для вашего Arduino-инструмента, которая:
1. Проверяет валидность команд перед их отправкой
2. Ограничивает частоту команд (чтобы избежать перегрузки Arduino)
3. Имеет "режим безопасного списка" команд

### Пример подхода
```python
import time
from typing import Set

class SafeArduinoInterface:
    def __init__(self, port: str, allowed_commands: Set[str] = None):
        self.port = port
        self.allowed_commands = allowed_commands or {"led_on", "led_off", "get_temp", "status"}
        self.last_command_time = 0
        self.min_command_interval = 0.1  # 100ms между командами
        # ... остальная реализация из предыдущих упражнений ...
    
    def send_command(self, command: str) -> str:
        # Проверка безопасности
        if command not in self.allowed_commands:
            return f"Ошибка: команда '{command}' не разрешена"
        
        # Проверка частоты команд
        current_time = time.time()
        if current_time - self.last_command_time < self.min_command_interval:
            return "Ошибка: слишком частые команды"
        
        self.last_command_time = current_time
        
        # Отправка команды (реализация как раньше)
        # ...
```

### Обсуждение
Почему безопасность особенно важна при взаимодействии ИИ-агентов с физическими устройствами, особенно в сравнении с обычными API-инструментами?