# Урок 1: Введение в управление микроконтроллерами с помощью ИИ-агента Ollama

## Оглавление
1. [Цель урока](#цель-урока)
2. [Введение](#введение)
3. [Основы протокола](#основы-протокола)
4. [Подготовка оборудования](#подготовка-оборудования)
5. [Установка и настройка](#установка-и-настройка)
6. [Первая связь между Ollama и Arduino](#первая-связь-между-ollama-и-arduino)
7. [Задание для практики](#задание-для-практики)

---

## Цель урока

Научиться устанавливать связь между ИИ-агентом Ollama и микроконтроллером Arduino UNO с использованием протокола связи, рассмотренного в туториале. После этого урока вы сможете отправлять команды с помощью ИИ-агента и управлять Arduino.

## Введение

Представьте, что вы можете говорить с физическим устройством на "человеческом языке", и оно будет вас понимать и выполнять действия! Это возможно благодаря соединению ИИ-агента Ollama с микроконтроллером Arduino.

Сегодня мы создадим систему, где:
- Ollama будет понимать наши инструкции на естественном языке
- Ollama будет преобразовывать эти инструкции в протокольные команды
- Arduino будет получать и выполнять эти команды

## Основы протокола

Как было описано в туториале, мы будем использовать следующую структуру пакета:

```
[SYNC1, SYNC2, LEN_DATA, DATA..., CRC]
```

Где:
- `SYNC1` (0xAA) — начальный байт синхронизации
- `SYNC2` (0x55) — дополнительный байт синхронизации
- `LEN_DATA` — количество байт данных
- `DATA` — полезные данные (команды и параметры)
- `CRC` — контрольная сумма

## Подготовка оборудования

Для этого урока вам потребуется:
- Плата Arduino UNO
- Компьютер с установленным Ollama
- USB кабель для подключения Arduino
- Макетная плата и провода (по желанию)
- Светодиод (для начального теста)

## Установка и настройка

### Шаг 1: Настройка Arduino

Сначала загрузим базовую программу на Arduino, которая будет использовать протокол связи из туториала:

```cpp
#include <SoftwareSerial.h>

// Определяем возможные команды через enum
enum CommandType {
  CMD_LED_ON = 0x01,
  CMD_LED_OFF = 0x02,
  CMD_LED_BLINK = 0x03,
  CMD_GET_SENSOR = 0x04
};

// FSM состояния приёма пакета
enum ReceiveState {
  WAIT_SYNC1,
  WAIT_SYNC2,
  WAIT_LEN,
  WAIT_DATA,
  WAIT_CRC
};

const int SYNC1 = 0xAA;
const int SYNC2 = 0x55;

// Переменные для FSM
ReceiveState currentState = WAIT_SYNC1;
byte buffer[256]; // буфер для данных
int dataIndex = 0;
int expectedDataLen = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // FSM для обработки входящих байтов
  while (Serial.available()) {
    byte incomingByte = Serial.read();

    switch (currentState) {
      case WAIT_SYNC1:
        if (incomingByte == SYNC1) {
          currentState = WAIT_SYNC2;
        }
        break;

      case WAIT_SYNC2:
        if (incomingByte == SYNC2) {
          currentState = WAIT_LEN;
        } else {
          currentState = WAIT_SYNC1; // ошибка синхронизации
        }
        break;

      case WAIT_LEN:
        expectedDataLen = incomingByte;
        dataIndex = 0;
        currentState = (expectedDataLen > 0) ? WAIT_DATA : WAIT_CRC;
        break;

      case WAIT_DATA:
        buffer[dataIndex] = incomingByte;
        dataIndex++;
        if (dataIndex >= expectedDataLen) {
          currentState = WAIT_CRC;
        }
        break;

      case WAIT_CRC:
        if (check_crc(buffer, expectedDataLen, incomingByte)) {
          // Пакет принят успешно - обрабатываем команду
          processCommand(buffer[0]);
        }
        currentState = WAIT_SYNC1; // возвращаемся к ожиданию следующего пакета
        break;
    }
  }
}

void processCommand(byte command) {
  switch(command) {
    case CMD_LED_ON:
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("LED ON");
      break;
    case CMD_LED_OFF:
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("LED OFF");
      break;
    case CMD_LED_BLINK:
      if (expectedDataLen > 1) {
        blinkLED(buffer[1]); // количество миганий
        Serial.print("LED BLINK ");
        Serial.println(buffer[1]);
      }
      break;
    case CMD_GET_SENSOR:
      sendSensorData();
      Serial.println("SENSOR REQUESTED");
      break;
    default:
      Serial.println("UNKNOWN COMMAND");
      break;
  }
}

void blinkLED(int times) {
  for(int i = 0; i < times; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
  }
}

void sendSensorData() {
  // отправляем фиктивные данные сенсора
  byte sensor_data[] = {0xAA, 0x55, 0x01, 25, 0xFF}; // температура 25°C
  Serial.write(sensor_data, 5);
}

bool check_crc(byte data[], int len, byte crc) {
  byte calc_crc = 0;
  for (int i = 0; i < len; i++) {
    calc_crc += data[i];
  }
  return (calc_crc & 0xFF) == crc;
}
```

Загрузите этот код в ваш Arduino UNO.

### Шаг 2: Подключение Python к Arduino

Теперь создадим Python-скрипт для ручной отправки команд:

```python
import serial
import time
import json

class ArduinoController:
    def __init__(self, port='COM3', baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
        time.sleep(2)  # ждем инициализации
    
    def send_command(self, command, params=[]):
        """Отправка команды по протоколу"""
        data = [command] + params
        crc = sum(data) & 0xFF
        
        packet = [0xAA, 0x55, len(data)] + data + [crc]
        
        self.ser.write(bytes(packet))
        print(f"Отправлена команда: {[hex(b) for b in packet]}")
        
        # Ждем ответ от Arduino
        if self.ser.in_waiting:
            response = self.ser.readline().decode().strip()
            print(f"Ответ Arduino: {response}")
    
    def led_on(self):
        self.send_command(0x01)  # CMD_LED_ON
    
    def led_off(self):
        self.send_command(0x02)  # CMD_LED_OFF
    
    def led_blink(self, count):
        self.send_command(0x03, [count])  # CMD_LED_BLINK
    
    def get_sensor(self):
        self.send_command(0x04)  # CMD_GET_SENSOR
    
    def close(self):
        self.ser.close()

# Пример использования
if __name__ == "__main__":
    controller = ArduinoController('COM3')  # Укажите правильный порт
    
    # Проверяем работу
    controller.led_on()
    time.sleep(1)
    controller.led_off()
    time.sleep(1)
    controller.led_blink(3)
    
    controller.close()
```

## Первая связь между Ollama и Arduino

Теперь мы готовы к настоящему взаимодействию с Ollama. Создадим специальный интерфейс, который будет переводить команды Ollama в протокол для Arduino.

Создайте файл `ai_arduino_interface.py`:

```python
import serial
import time
import json
import requests
import re
import ollama

class AI_Arduino_Interface:
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        self.arduino = serial.Serial(arduino_port, baudrate)
        time.sleep(2)  # ждем инициализации
        self.ollama_url = ollama_url
        self.use_local_ollama = use_local_ollama
        self.model = model
        
        # Определяем команды для Arduino (инструменты для LLM)
        self.commands = {
            'turn_on_led': {
                'command': 0x01,
                'params': [],
                'description': 'Включить светодиод на Arduino'
            },
            'turn_off_led': {
                'command': 0x02,
                'params': [],
                'description': 'Выключить светодиод на Arduino'
            },
            'blink_led': {
                'command': 0x03,
                'params': [3],  # по умолчанию 3 раза
                'description': 'Мигнуть светодиодом на Arduino. Аргумент: {"times": int}',
                'parameters': {
                    'times': {'type': 'int', 'description': 'Количество миганий (1-10)'}
                }
            },
            'get_temperature': {
                'command': 0x04,
                'params': [],
                'description': 'Получить температуру с датчика на Arduino'
            }
        }
    
    def parse_command_from_ai(self, ai_response):
        """Парсинг ответа от ИИ-агента для определения команды"""
        # Простой парсер - в реальности может быть более сложным
        ai_response_lower = ai_response.lower()
        
        if 'turn on' in ai_response_lower and ('light' in ai_response_lower or 'led' in ai_response_lower):
            return 'turn_on_led'
        elif 'turn off' in ai_response_lower and ('light' in ai_response_lower or 'led' in ai_response_lower):
            return 'turn_off_led'
        elif 'blink' in ai_response_lower or 'flash' in ai_response_lower:
            return 'blink_led'
        elif 'temperature' in ai_response_lower or 'temp' in ai_response_lower:
            return 'get_temperature'
        
        return None
    
    def call_arduino_command(self, command_name, arguments=None):
        """Вызов команды Arduino на основе результата LLM с аргументами"""
        if command_name not in self.commands:
            print(f"Неизвестная команда: {command_name}")
            return None

        cmd_info = self.commands[command_name]

        # Подготовим параметры на основе аргументов
        params = []

        if arguments and isinstance(arguments, dict):
            if command_name == 'blink_led' and 'times' in arguments:
                # Для blink_led используем количество миганий из аргументов
                times = min(10, max(1, int(arguments['times'])))  # Ограничиваем от 1 до 10
                params = [times]

        # Если параметры не были заданы аргументами, используем параметры по умолчанию
        if not params and 'params' in cmd_info:
            params = cmd_info['params']

        # Отправляем команду на Arduino
        data = [cmd_info['command']] + params
        crc = sum(data) & 0xFF
        packet = [0xAA, 0x55, len(data)] + data + [crc]

        self.arduino.write(bytes(packet))
        print(f"Отправлена команда {command_name} с параметрами {params}: {[hex(b) for b in packet]}")

        # Возвращаем команду и параметры для дальнейшей обработки
        return command_name, params

    def process_request_with_tools(self, user_request):
        """Обработка пользовательского запроса через ИИ с использованием инструментов и выполнение на Arduino"""
        print(f"Пользовательский запрос: {user_request}")

        # Запрашиваем у LLM выбор команды
        ai_response = self.query_ollama_with_tools(user_request)
        print(f"Ответ от ИИ (JSON): {ai_response.strip()}")

        try:
            # Парсим JSON ответ от ИИ
            response_data = json.loads(ai_response.strip())
            command_name = response_data.get('command_name')
            arguments = response_data.get('arguments', {})

            if command_name:
                # Выполняем команду на Arduino
                result = self.call_arduino_command(command_name, arguments)

                if result:
                    # Ждем ответ от Arduino (если есть)
                    start_time = time.time()
                    while self.arduino.in_waiting == 0 and time.time() - start_time < 2:
                        time.sleep(0.1)

                    if self.arduino.in_waiting:
                        response = self.arduino.readline().decode().strip()
                        print(f"Ответ Arduino: {response}")
                else:
                    print("Команда не выполнена из-за ошибки")
            else:
                print("Команда не распознана или не требует выполнения на Arduino")
        except json.JSONDecodeError:
            print("Ошибка парсинга JSON ответа от ИИ")
            print("Пытаемся использовать старый метод...")
            # В случае ошибки используем старый метод
            self.process_request(user_request)
        except Exception as e:
            print(f"Ошибка при обработке запроса: {e}")

    def send_to_arduino(self, command_name, params=None):
        """Отправка команды на Arduino (старый метод для совместимости)"""
        if command_name in self.commands:
            cmd_info = self.commands[command_name]

            if params is not None:
                data = [cmd_info['command']] + params
            else:
                data = [cmd_info['command']] + cmd_info['params']

            crc = sum(data) & 0xFF
            packet = [0xAA, 0x55, len(data)] + data + [crc]

            self.arduino.write(bytes(packet))
            print(f"Отправлена команда {command_name}: {[hex(b) for b in packet]}")

        else:
            print(f"Неизвестная команда: {command_name}")
    
    def query_ollama_with_tools(self, user_query):
        """Запрос к Ollama с использованием системного промпта для выбора команд Arduino"""
        # Формируем описания доступных команд для системного промпта
        available_commands = []
        for cmd_name, cmd_info in self.commands.items():
            cmd_desc = f"- '{cmd_name}': {cmd_info['description']}"
            if 'parameters' in cmd_info:
                params_desc = ", ".join([f"{param}: {details['type']}" for param, details in cmd_info['parameters'].items()])
                cmd_desc += f". Аргументы: {{{params_desc}}}"
            available_commands.append(cmd_desc)

        system_prompt = f"""
        Ты - ИИ-диспетчер для Arduino. Твоя задача - проанализировать запрос пользователя и выбрать подходящую команду для Arduino.

        Доступные команды:
        {'; '.join(available_commands)}

        Формат ответа: только JSON вида {{"command_name": "...", "arguments": {{...}}}}.
        Не отвечай ничего кроме этого JSON.

        Примеры:
        Пользователь: Включи свет
        Твой ответ: {{"command_name": "turn_on_led", "arguments": {{}}}}

        Пользователь: Помигай 5 раз
        Твой ответ: {{"command_name": "blink_led", "arguments": {{"times": 5}}}}

        Пользователь: Какая температура?
        Твой ответ: {{"command_name": "get_temperature", "arguments": {{}}}}
        """

        if self.use_local_ollama:
            # Используем локальную библиотеку ollama
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {
                            'role': 'system',
                            'content': system_prompt
                        },
                        {
                            'role': 'user',
                            'content': user_query,
                        },
                    ]
                )
                return response['message']['content']
            except Exception as e:
                print(f"Ошибка при запросе к локальной модели Ollama: {e}")
                return ""
        else:
            # Используем HTTP API
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                "stream": False
            }

            response = requests.post(self.ollama_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', result.get('response', ''))
            else:
                print(f"Ошибка при запросе к Ollama: {response.status_code}")
                return ""
    
    def process_request(self, user_request):
        """Обработка пользовательского запроса через ИИ и выполнение на Arduino"""
        print(f"Пользовательский запрос: {user_request}")
        
        # Формируем промпт для ИИ, чтобы он распознал команды для Arduino
        ai_prompt = f"""
        Пользователь дал команду: "{user_request}"
        
        Возможные команды для Arduino:
        - turn_on_led: включить светодиод
        - turn_off_led: выключить светодиод  
        - blink_led: мигнуть светодиодом (по умолчанию 3 раза)
        - get_temperature: получить температуру с датчика
        
        Ответь только названием команды, которую нужно выполнить, или "none", если команда не относится к Arduino.
        Примеры:
        Запрос: "Turn on the LED" -> Ответ: turn_on_led
        Запрос: "Make the light flash" -> Ответ: blink_led
        """
        
        ai_response = self.query_ollama(ai_prompt)
        print(f"Ответ от ИИ: {ai_response.strip()}")
        
        # Определяем команду
        command = self.parse_command_from_ai(ai_response)
        
        if command:
            # Выполняем команду на Arduino
            self.send_to_arduino(command)
            
            # Ждем ответ от Arduino (если есть)
            start_time = time.time()
            while self.arduino.in_waiting == 0 and time.time() - start_time < 2:
                time.sleep(0.1)
            
            if self.arduino.in_waiting:
                response = self.arduino.readline().decode().strip()
                print(f"Ответ Arduino: {response}")
        else:
            print("Команда не распознана или не требует выполнения на Arduino")
    
    def close(self):
        self.arduino.close()

# Пример использования
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    interface = AI_Arduino_Interface('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # interface = AI_Arduino_Interface('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")

    print("=== Демонстрация работы с инструментами ===")
    # Примеры запросов с новой системой инструментов
    interface.process_request_with_tools("Turn on the LED")
    time.sleep(2)
    interface.process_request_with_tools("Blink the LED 3 times")
    time.sleep(2)
    interface.process_request_with_tools("Turn off the LED")

    print("\n=== Для сравнения: старый метод ===")
    interface.process_request("Turn on the LED")
    time.sleep(2)
    interface.process_request("Turn off the LED")

    interface.close()
```

## Задание для практики

1. Установите Ollama на ваш компьютер, если еще не установлен
2. Загрузите код в Arduino UNO
3. Подключите Arduino к компьютеру и определите правильный COM-порт
4. Запустите Python-скрипт и проверьте, что команда `process_request("Turn on the LED")` действительно включает светодиод на Arduino
5. Попробуйте другие команды: "Make the LED blink 3 times", "Turn off the LED"

Продолжение следует во втором уроке, где мы усложним взаимодействие и добавим больше функций!