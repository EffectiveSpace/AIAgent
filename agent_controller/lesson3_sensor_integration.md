# Урок 3: Замкнутая система с датчиками и ИИ-агентом

## Оглавление
1. [Цель урока](#цель-урока)
2. [Обзор предыдущих уроков](#обзор-предыдущих-уроков)
3. [Добавление датчиков к Arduino](#добавление-датчиков-к-arduino)
4. [Расширение протокола для работы с датчиками](#расширение-протокола-для-работы-с-датчиками)
5. [Обновление Arduino кода с датчиками](#обновление-arduino-кода-с-датчиками)
6. [Интеграция с Ollama для анализа датчиков](#интеграция-с-ollama-для-анализа-датчиков)
7. [Создание замкнутой системы управления](#создание-замкнутой-системы-управления)
8. [Задание для практики](#задание-для-практики)

---

## Цель урока

Научиться создавать замкнутую систему управления, где ИИ-агент Ollama может получать данные от датчиков на Arduino, анализировать их и принимать решения. После этого урока вы сможете создавать системы, которые реагируют на окружающую среду.

## Обзор предыдущих урока

В предыдущих уроках мы:
- Настроили базовую связь между Ollama и Arduino
- Научились управлять светодиодом через ИИ
- Добавили управление сервоприводом
- Создали протокол передачи данных с использованием FSM

## Добавление датчиков к Arduino

Для этого урока мы добавим два датчика:
1. Датчик температуры (DS18B20 или TMP36)
2. Датчик освещенности (фоторезистор)

### Подключение датчика температуры (TMP36):
- Красный провод (VCC) → 5V на Arduino
- Черный провод (GND) → GND на Arduino
- Зеленый/синий провод (сигнал) → Analog pin A0 на Arduino

### Подключение датчика освещенности:
- Один вывод фоторезистора → 5V на Arduino
- Второй вывод фоторезистора → Analog pin A1 на Arduino и через резистор 10 кОм к GND

## Расширение протокола для работы с датчиками

Добавим новые команды в enum для работы с датчиками:

```cpp
// Новые команды для работы с датчиками
enum CommandType {
  CMD_LED_ON = 0x01,
  CMD_LED_OFF = 0x02,
  CMD_LED_BLINK = 0x03,
  CMD_GET_SENSOR = 0x04,
  CMD_SERVO_ANGLE = 0x05,
  CMD_GET_SERVO_ANGLE = 0x06,
  CMD_GET_TEMPERATURE = 0x07,
  CMD_GET_LIGHT = 0x08,
  CMD_GET_ALL_SENSORS = 0x09,
  CMD_AUTO_MODE = 0x0A    // Автоматический режим (ИИ управляет системой)
};
```

## Обновление Arduino кода с датчиками

Новый Arduino код с поддержкой датчиков:

```cpp
#include <Servo.h>  // Подключаем библиотеку для работы с сервоприводами

// Определяем возможные команды через enum
enum CommandType {
  CMD_LED_ON = 0x01,
  CMD_LED_OFF = 0x02,
  CMD_LED_BLINK = 0x03,
  CMD_GET_SENSOR = 0x04,
  CMD_SERVO_ANGLE = 0x05,
  CMD_GET_SERVO_ANGLE = 0x06,
  CMD_GET_TEMPERATURE = 0x07,
  CMD_GET_LIGHT = 0x08,
  CMD_GET_ALL_SENSORS = 0x09,
  CMD_AUTO_MODE = 0x0A    // Автоматический режим (ИИ управляет системой)
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

// Пины подключения
const int TEMP_PIN = A0;
const int LIGHT_PIN = A1;
const int SERVO_PIN = 9;
const int LED_PIN = 13;

// Переменные для FSM
ReceiveState currentState = WAIT_SYNC1;
byte buffer[256]; // буфер для данных
int dataIndex = 0;
int expectedDataLen = 0;

// Объект сервопривода
Servo myservo;
int current_servo_angle = 0;  // Текущий угол сервопривода
bool auto_mode = false;       // Флаг автоматического режима

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  
  // Подключаем сервопривод
  myservo.attach(SERVO_PIN);
  myservo.write(0);  // Устанавливаем начальный угол 0 градусов
  
  // Инициализируем пины
  pinMode(TEMP_PIN, INPUT);
  pinMode(LIGHT_PIN, INPUT);
}

void loop() {
  // Проверяем автоматический режим
  if (auto_mode) {
    // В автоматическом режиме мы можем выполнять предопределенные действия
    // в зависимости от показаний датчиков
    int light_level = analogRead(LIGHT_PIN);
    
    // Если темно, включаем светодиод
    if (light_level < 200) {  // Уровень темноты
      digitalWrite(LED_PIN, HIGH);
    } else {
      digitalWrite(LED_PIN, LOW);
    }
    
    // Если жарко, поворачиваем сервопривод (например, для вентиляции)
    int temp_value = getTemperatureRaw();
    if (temp_value > 300) {  // Уровень высокой температуры
      setServoAngle(90);  // Открываем "вентиляцию"
    } else {
      setServoAngle(0);   // Закрываем "вентиляцию"
    }
    
    delay(1000); // Обновляем показания каждую секунду
  } else {
    // FSM для обработки входящих байтов (режим ручного управления)
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
}

void processCommand(byte command) {
  switch(command) {
    case CMD_LED_ON:
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED ON");
      break;
    case CMD_LED_OFF:
      digitalWrite(LED_PIN, LOW);
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
    case CMD_SERVO_ANGLE:
      if (expectedDataLen > 1) {
        setServoAngle(buffer[1]); // угол в градусах (0-180)
        Serial.print("SERVO ANGLE SET TO: ");
        Serial.println(buffer[1]);
      }
      break;
    case CMD_GET_SERVO_ANGLE:
      returnServoAngle();
      Serial.println("SERVO ANGLE REQUESTED");
      break;
    case CMD_GET_TEMPERATURE:
      returnTemperature();
      Serial.println("TEMPERATURE REQUESTED");
      break;
    case CMD_GET_LIGHT:
      returnLightLevel();
      Serial.println("LIGHT LEVEL REQUESTED");
      break;
    case CMD_GET_ALL_SENSORS:
      returnAllSensors();
      Serial.println("ALL SENSORS REQUESTED");
      break;
    case CMD_AUTO_MODE:
      if (expectedDataLen > 1) {
        auto_mode = (buffer[1] == 1);
        Serial.print("AUTO MODE SET TO: ");
        Serial.println(auto_mode ? "ON" : "OFF");
      }
      break;
    default:
      Serial.println("UNKNOWN COMMAND");
      break;
  }
}

void blinkLED(int times) {
  for(int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
}

void setServoAngle(int angle) {
  // Ограничиваем угол от 0 до 180 градусов
  if (angle < 0) angle = 0;
  if (angle > 180) angle = 180;
  
  myservo.write(angle);
  current_servo_angle = angle;
}

void returnServoAngle() {
  // Отправляем текущий угол сервопривода обратно
  byte angle_data[] = {0xAA, 0x55, 0x02, CMD_GET_SERVO_ANGLE, (byte)current_servo_angle, 0x00};
  angle_data[5] = check_crc(&angle_data[2], 2, 0); // Пересчитываем CRC
  Serial.write(angle_data, 6);
}

void sendSensorData() {
  // отправляем фиктивные данные сенсора
  byte sensor_data[] = {0xAA, 0x55, 0x01, 25, 0xFF}; // температура 25°C
  Serial.write(sensor_data, 5);
}

int getTemperatureRaw() {
  // Считываем значение с датчика температуры (TMP36)
  int tempReading = analogRead(TEMP_PIN);
  return tempReading;
}

void returnTemperature() {
  int tempReading = getTemperatureRaw();
  
  // Формируем пакет с температурой (2 байта для значения)
  byte temp_data[] = {0xAA, 0x55, 0x03, CMD_GET_TEMPERATURE, (byte)(tempReading & 0xFF), (byte)((tempReading >> 8) & 0xFF), 0x00};
  temp_data[6] = check_crc(&temp_data[2], 3, 0); // Пересчитываем CRC
  Serial.write(temp_data, 7);
}

void returnLightLevel() {
  int lightReading = analogRead(LIGHT_PIN);
  
  // Формируем пакет с уровнем освещенности (2 байта для значения)
  byte light_data[] = {0xAA, 0x55, 0x03, CMD_GET_LIGHT, (byte)(lightReading & 0xFF), (byte)((lightReading >> 8) & 0xFF), 0x00};
  light_data[6] = check_crc(&light_data[2], 3, 0); // Пересчитываем CRC
  Serial.write(light_data, 7);
}

void returnAllSensors() {
  int tempReading = getTemperatureRaw();
  int lightReading = analogRead(LIGHT_PIN);
  
  // Формируем пакет со всеми показаниями датчиков
  byte all_data[] = {0xAA, 0x55, 0x05, CMD_GET_ALL_SENSORS, 
                     (byte)(tempReading & 0xFF), (byte)((tempReading >> 8) & 0xFF),
                     (byte)(lightReading & 0xFF), (byte)((lightReading >> 8) & 0xFF), 0x00};
  all_data[8] = check_crc(&all_data[2], 5, 0); // Пересчитываем CRC
  Serial.write(all_data, 9);
}

bool check_crc(byte data[], int len, byte crc) {
  byte calc_crc = 0;
  for (int i = 0; i < len; i++) {
    calc_crc += data[i];
  }
  return (calc_crc & 0xFF) == crc;
}
```

## Интеграция с Ollama для анализа датчиков

Обновленный Python-интерфейс с поддержкой датчиков:

```python
import serial
import time
import json
import requests
import re
import ollama

class Smart_AI_Arduino_Interface:
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
                'params': [3],
                'description': 'Мигнуть светодиодом на Arduino. Аргумент: {"times": int}',
                'parameters': {
                    'times': {'type': 'int', 'description': 'Количество миганий (1-10)'}
                }
            },
            'get_old_sensor': {
                'command': 0x04,
                'params': [],
                'description': 'Получить устаревшие данные сенсора с Arduino'
            },
            'set_servo_angle': {
                'command': 0x05,
                'params': [90],
                'description': 'Установить угол сервопривода на Arduino. Аргумент: {"angle": int}',
                'parameters': {
                    'angle': {'type': 'int', 'description': 'Угол в градусах (0-180)'}
                }
            },
            'get_servo_angle': {
                'command': 0x06,
                'params': [],
                'description': 'Получить текущий угол сервопривода на Arduino'
            },
            'get_temperature': {
                'command': 0x07,
                'params': [],
                'description': 'Получить температуру с датчика на Arduino'
            },
            'get_light': {
                'command': 0x08,
                'params': [],
                'description': 'Получить уровень освещенности с датчика на Arduino'
            },
            'get_all_sensors': {
                'command': 0x09,
                'params': [],
                'description': 'Получить данные всех датчиков на Arduino'
            },
            'set_auto_mode': {
                'command': 0x0A,
                'params': [0],  # 0=выкл, 1=вкл
                'description': 'Включить/выключить автоматический режим. Аргумент: {"enabled": bool}',
                'parameters': {
                    'enabled': {'type': 'int', 'description': '1 для включения, 0 для выключения'}
                }
            }
        }
    
    def parse_command_from_ai(self, ai_response):
        """Парсинг ответа от ИИ-агента для определения команды и параметров"""
        ai_response_lower = ai_response.lower()
        
        # Парсинг команд
        if 'turn on' in ai_response_lower and ('light' in ai_response_lower or 'led' in ai_response_lower):
            return 'turn_on_led', []
        elif 'turn off' in ai_response_lower and ('light' in ai_response_lower or 'led' in ai_response_lower):
            return 'turn_off_led', []
        elif 'blink' in ai_response_lower or 'flash' in ai_response_lower:
            return 'blink_led', [3]
        elif 'temperature' in ai_response_lower or 'temp' in ai_response_lower:
            return 'get_temperature', []
        elif 'light' in ai_response_lower or 'brightness' in ai_response_lower:
            return 'get_light', []
        elif 'servo' in ai_response_lower or 'servomotor' in ai_response_lower or 'rotate' in ai_response_lower:
            angle_match = re.search(r'(\d+)', ai_response)
            if angle_match:
                angle = min(180, max(0, int(angle_match.group(1))))
                return 'set_servo_angle', [angle]
            else:
                return 'set_servo_angle', [90]
        elif 'all sensors' in ai_response_lower or 'sensors' in ai_response_lower and 'all' in ai_response_lower:
            return 'get_all_sensors', []
        elif 'auto mode' in ai_response_lower or 'automatic' in ai_response_lower:
            if 'start' in ai_response_lower or 'enable' in ai_response_lower or 'on' in ai_response_lower:
                return 'set_auto_mode', [1]
            elif 'stop' in ai_response_lower or 'disable' in ai_response_lower or 'off' in ai_response_lower:
                return 'set_auto_mode', [0]
        
        return None, []
    
    def send_to_arduino(self, command_name, params=None):
        """Отправка команды на Arduino"""
        if command_name in self.commands:
            cmd_info = self.commands[command_name]
            
            if params is not None:
                data = [cmd_info['command']] + params
            else:
                data = [cmd_info['command']] + cmd_info['params']
                
            crc = sum(data) & 0xFF
            packet = [0xAA, 0x55, len(data)] + data + [crc]
            
            self.arduino.write(bytes(packet))
            print(f"Отправлена команда {command_name} с параметрами {params}: {[hex(b) for b in packet]}")
            
            return cmd_info['command']  # Возвращаем код команды для дальнейшей обработки ответа
        else:
            print(f"Неизвестная команда: {command_name}")
            return None
    
    def read_sensor_response(self, command_code):
        """Чтение и обработка ответа от Arduino для команд с датчиками"""
        start_time = time.time()
        timeout = 3  # 3 секунды таймаута
        
        # Ждем данные от Arduino
        while time.time() - start_time < timeout:
            if self.arduino.in_waiting:
                # Читаем байты (для датчиков нам нужно больше данных)
                raw_data = self.arduino.read_all()
                
                # Анализируем принятый пакет
                if len(raw_data) >= 6:  # Минимальная длина пакета
                    try:
                        # Проверяем заголовок пакета
                        if raw_data[0] == 0xAA and raw_data[1] == 0x55:
                            data_len = raw_data[2]
                            
                            if len(raw_data) >= 4 + data_len + 1:  # Проверяем полную длину
                                # Извлекаем данные
                                data_bytes = raw_data[3:3+data_len]
                                
                                # Проверяем команду
                                if data_bytes[0] == command_code:
                                    if command_code == 0x07:  # Температура
                                        if len(data_bytes) >= 3:
                                            temp_value = data_bytes[1] + (data_bytes[2] << 8)
                                            print(f"Температура: {temp_value} (сырое значение)")
                                            # Переводим в градусы Цельсия (для TMP36)
                                            voltage = (temp_value / 1024.0) * 5.0
                                            temperature_c = (voltage - 0.5) * 100
                                            print(f"Температура: {temperature_c:.2f}°C")
                                            return temperature_c
                                    elif command_code == 0x08:  # Освещенность
                                        if len(data_bytes) >= 3:
                                            light_value = data_bytes[1] + (data_bytes[2] << 8)
                                            print(f"Уровень освещенности: {light_value}")
                                            return light_value
                                    elif command_code == 0x09:  # Все датчики
                                        if len(data_bytes) >= 5:
                                            temp_raw = data_bytes[1] + (data_bytes[2] << 8)
                                            light_raw = data_bytes[3] + (data_bytes[4] << 8)
                                            
                                            # Переводим температуру в градусы
                                            voltage = (temp_raw / 1024.0) * 5.0
                                            temperature_c = (voltage - 0.5) * 100
                                            
                                            print(f"Все датчики - Температура: {temperature_c:.2f}°C, Освещенность: {light_raw}")
                                            return {"temperature": temperature_c, "light": light_raw}
                    except Exception as e:
                        print(f"Ошибка при обработке ответа: {e}")
            
            time.sleep(0.1)
        
        print("Таймаут ожидания ответа от Arduino")
        return None
    
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

        Пользователь: Поверни серво на 90 градусов
        Твой ответ: {{"command_name": "set_servo_angle", "arguments": {{"angle": 90}}}}

        Пользователь: Какая температура?
        Твой ответ: {{"command_name": "get_temperature", "arguments": {{}}}}

        Пользователь: Включи автоматический режим
        Твой ответ: {{"command_name": "set_auto_mode", "arguments": {{"enabled": 1}}}}
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
            elif command_name == 'set_servo_angle' and 'angle' in arguments:
                # Для set_servo_angle используем угол из аргументов
                angle = min(180, max(0, int(arguments['angle'])))  # Ограничиваем от 0 до 180
                params = [angle]
            elif command_name == 'set_auto_mode' and 'enabled' in arguments:
                # Для set_auto_mode используем значение enabled из аргументов
                enabled = 1 if arguments['enabled'] else 0
                params = [enabled]

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

    def query_ollama(self, prompt):
        """Запрос к Ollama - использует либо HTTP API, либо локальную библиотеку ollama (старый метод для совместимости)"""
        if self.use_local_ollama:
            # Используем локальную библиотеку ollama
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {
                            'role': 'user',
                            'content': prompt,
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
                "model": self.model,  # или другой доступный модуль
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(self.ollama_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                print(f"Ошибка при запросе к Ollama: {response.status_code}")
                return ""
    
    def process_request(self, user_request):
        """Обработка пользовательского запроса через ИИ и выполнение на Arduino"""
        print(f"Пользовательский запрос: {user_request}")
        
        # Формируем промпт для ИИ
        ai_prompt = f"""
        Пользователь дал команду: "{user_request}"
        
        Возможные команды для Arduino:
        - turn_on_led: включить светодиод
        - turn_off_led: выключить светодиод  
        - blink_led: мигнуть светодиодом (по умолчанию 3 раза)
        - get_temperature: получить температуру с датчика
        - get_light: получить уровень освещенности
        - set_servo_angle: установить угол сервопривода (ожидает параметр - угол в градусах 0-180)
        - get_servo_angle: получить текущий угол сервопривода
        - get_all_sensors: получить показания всех датчиков
        - set_auto_mode: включить/выключить автоматический режим
        
        Ответь в формате JSON: {{"command": "command_name", "params": [param1, param2, ...]}}
        Если команда не относится к Arduino, ответь: {{"command": "none", "params": []}}
        
        Примеры:
        Запрос: "Turn on the LED" -> Ответ: {{"command": "turn_on_led", "params": []}}
        Запрос: "What is the temperature?" -> Ответ: {{"command": "get_temperature", "params": []}}
        Запрос: "Rotate servo to 90 degrees" -> Ответ: {{"command": "set_servo_angle", "params": [90]}}
        """
        
        ai_response = self.query_ollama(ai_prompt)
        print(f"Ответ от ИИ: {ai_response.strip()}")
        
        try:
            parsed_response = json.loads(ai_response.strip())
            command = parsed_response.get('command')
            params = parsed_response.get('params', [])
        except json.JSONDecodeError:
            command, params = self.parse_command_from_ai(ai_response)
        
        if command and command != 'none':
            # Отправляем команду на Arduino
            command_code = self.send_to_arduino(command, params)
            
            # Для команд с датчиками ждем ответ
            if command in ['get_temperature', 'get_light', 'get_all_sensors', 'get_servo_angle']:
                if command_code is not None:
                    sensor_data = self.read_sensor_response(command_code)
                    if sensor_data is not None:
                        # Отправляем данные обратно в Ollama для анализа
                        self.analyze_sensor_data_with_ai(command, sensor_data)
            else:
                # Для остальных команд просто ждем ответ от Arduino
                start_time = time.time()
                while self.arduino.in_waiting == 0 and time.time() - start_time < 2:
                    time.sleep(0.1)
                
                if self.arduino.in_waiting:
                    response = self.arduino.readline().decode().strip()
                    print(f"Ответ Arduino: {response}")
        else:
            print("Команда не распознана или не требует выполнения на Arduino")
    
    def analyze_sensor_data_with_ai(self, command, sensor_data):
        """Анализ данных датчиков с помощью ИИ"""
        if command == 'get_temperature':
            prompt = f"Температура в помещении: {sensor_data:.2f}°C. Комментируй это значение с точки зрения комфорта человека."
        elif command == 'get_light':
            prompt = f"Уровень освещенности: {sensor_data}. Оцени, достаточно ли света для работы или чтения."
        elif command == 'get_all_sensors':
            temp = sensor_data['temperature']
            light = sensor_data['light']
            prompt = f"Данные датчиков: температура {temp:.2f}°C, уровень освещенности {light}. Какие рекомендации ты можешь дать для улучшения условий в помещении?"
        
        ai_analysis = self.query_ollama(prompt)
        print(f"Анализ ИИ: {ai_analysis.strip()}")
    
    def smart_environment_control(self):
        """Интеллектуальное управление окружающей средой на основе датчиков"""
        print("Запуск интеллектуального управления окружающей средой...")
        
        while True:
            try:
                # Получаем данные всех датчиков
                self.send_to_arduino('get_all_sensors')
                sensor_data = self.read_sensor_response(0x09)
                
                if sensor_data:
                    temp = sensor_data['temperature']
                    light = sensor_data['light']
                    
                    print(f"Текущие показания - Температура: {temp:.2f}°C, Освещенность: {light}")
                    
                    # Формируем промпт для ИИ с просьбой проанализировать данные и предложить действия
                    ai_prompt = f"""
                    Текущие условия в помещении:
                    - Температура: {temp:.2f}°C
                    - Уровень освещенности: {light}
                    
                    Проанализируй эти данные и предложи возможные действия для улучшения условий:
                    - включить/выключить светодиод (если темно)
                    - изменить угол сервопривода (например, для вентиляции при высокой температуре)
                    - другие действия
                    
                    Ответь в формате JSON: {{"actions": [{"action": "action_name", "params": [param1, param2, ...]}, ...]}}
                    Возможные действия: "turn_on_led", "turn_off_led", "set_servo_angle"
                    """
                    
                    ai_response = self.query_ollama(ai_prompt)
                    print(f"Рекомендации ИИ: {ai_response}")
                    
                    try:
                        parsed_actions = json.loads(ai_response)
                        actions = parsed_actions.get('actions', [])
                        
                        # Выполняем рекомендованные действия
                        for action in actions:
                            action_name = action.get('action')
                            action_params = action.get('params', [])
                            
                            if action_name:
                                self.send_to_arduino(action_name, action_params)
                                
                                # Ждем подтверждения
                                time.sleep(0.5)
                                if self.arduino.in_waiting:
                                    response = self.arduino.readline().decode().strip()
                                    print(f"Ответ Arduino: {response}")
                    except json.JSONDecodeError:
                        print("Не удалось распарсить рекомендации ИИ")
                
                # Ждем 5 секунд перед следующим циклом
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\nОстановка интеллектуального управления...")
                break
    
    def close(self):
        self.arduino.close()

# Пример использования
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    interface = Smart_AI_Arduino_Interface('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # interface = Smart_AI_Arduino_Interface('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")

    print("=== Демонстрация работы с инструментами ===")
    # Примеры запросов с новой системой инструментов
    interface.process_request_with_tools("What is the temperature?")
    time.sleep(2)
    interface.process_request_with_tools("What is the light level?")
    time.sleep(2)
    interface.process_request_with_tools("Rotate servo to 45 degrees")
    time.sleep(2)
    interface.process_request_with_tools("Get all sensor readings")
    time.sleep(2)

    print("\n=== Для сравнения: старый метод ===")
    interface.process_request("What is the temperature?")
    time.sleep(2)
    interface.process_request("Get all sensor readings")

    print("\n=== Демонстрация интеллектуального управления ===")
    print("Для демонстрации непрерывного контроля запустите метод smart_environment_control()")
    print("Для остановки нажмите Ctrl+C")

    # Для демонстрации непрерывного контроля (закомментировано для безопасности)
    # interface.smart_environment_control()

    interface.close()
```

## Создание замкнутой системы управления

Теперь создадим пример полноценной замкнутой системы, где ИИ анализирует данные и принимает решения:

```python
def create_closed_loop_system():
    """Пример замкнутой системы управления с ИИ и датчиками"""
    interface = Smart_AI_Arduino_Interface('COM3')

    print("Запуск замкнутой системы управления...")
    print("Система будет регулярно опрашивать датчики и принимать решения на основе данных")

    try:
        while True:
            # Считываем данные датчиков
            interface.send_to_arduino('get_all_sensors')
            sensor_data = interface.read_sensor_response(0x09)

            if sensor_data:
                temp = sensor_data['temperature']
                light = sensor_data['light']

                print(f"Текущее состояние: Температура {temp:.2f}°C, Освещенность {light}")

                # Принимаем решения на основе данных
                if light < 200:  # Темно
                    print("Обнаружено низкое освещение - включаем светодиод")
                    interface.send_to_arduino('turn_on_led')
                elif light > 500:  # Слишком светло
                    print("Обнаружено высокое освещение - выключаем светодиод")
                    interface.send_to_arduino('turn_off_led')

                if temp > 27:  # Жарко
                    print("Обнаружена высокая температура - поворачиваем сервопривод для вентиляции")
                    interface.send_to_arduino('set_servo_angle', [90])
                elif temp < 20:  # Холодно
                    print("Обнаружена низкая температура - закрываем вентиляцию")
                    interface.send_to_arduino('set_servo_angle', [0])

            # Ждем 10 секунд перед следующим измерением
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nЗамкнутая система остановлена пользователем")
    finally:
        interface.close()

# Запуск замкнутой системы (закомментировано для безопасности)
# create_closed_loop_system()
```

## Задание для практики

1. Подключите датчики к Arduino согласно схеме из урока
2. Загрузите обновленный код в Arduino
3. Обновите Python-интерфейс с поддержкой датчиков
4. Протестируйте команды:
   - "What is the temperature?"
   - "Get light level"
   - "Get all sensor readings"
5. Создайте собственную замкнутую систему, которая:
   - Регулярно опрашивает датчики
   - Принимает решения на основе данных (например, включает светодиод при низкой освещенности)
   - Отправляет результаты анализа обратно пользователю
6. Попробуйте запустить систему на длительное время и наблюдать за её поведением

В следующем уроке мы добавим голосовое управление и машинное обучение для более сложных сценариев взаимодействия!