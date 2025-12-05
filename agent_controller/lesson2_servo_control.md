# Урок 2: Продвинутые команды и управление сервоприводом через Ollama

## Оглавление
1. [Цель урока](#цель-урока)
2. [Обзор предыдущего урока](#обзор-предыдущего-урока)
3. [Добавление сервопривода](#добавление-сервопривода)
4. [Расширение протокола для новых команд](#расширение-протокола-для-новых-команд)
5. [Обновление Arduino кода](#обновление-arduino-кода)
6. [Интеграция с Ollama для управления углом](#интеграция-с-ollama-для-управления-углом)
7. [Задание для практики](#задание-для-практики)

---

## Цель урока

Научиться расширять протокол связи между Ollama и Arduino для управления сервоприводом. После этого урока вы сможете отправлять команды вида "Поверни сервопривод на 90 градусов" и видеть физическое выполнение команды.

## Обзор предыдущего урока

В предыдущем уроке мы:
- Настроили базовую связь между Ollama и Arduino
- Создали протокол передачи данных с использованием SYNC, длины данных и контрольной суммы
- Научились управлять светодиодом через ИИ-агента
- Поняли структуру FSM (конечного автомата) для обработки данных

## Добавление сервопривода

Для этого урока нам понадобится:
- Сервопривод (например, SG90)
- Arduino UNO
- Макетная плата
- Соединительные провода

Подключение сервопривода к Arduino:
- Красный провод (питание) → 5V на Arduino
- Коричневый/черный провод (земля) → GND на Arduino
- Оранжевый/желтый провод (управление) → Digital pin 9 на Arduino

## Расширение протокола для новых команд

Добавим новые команды в enum для управления сервоприводом:

```cpp
// Новые команды для управления сервоприводом
enum CommandType {
  CMD_LED_ON = 0x01,
  CMD_LED_OFF = 0x02,
  CMD_LED_BLINK = 0x03,
  CMD_GET_SENSOR = 0x04,
  CMD_SERVO_ANGLE = 0x05,    // Установить угол сервопривода
  CMD_GET_SERVO_ANGLE = 0x06 // Получить текущий угол
};
```

## Обновление Arduino кода

Новый Arduino код с поддержкой сервопривода:

```cpp
#include <Servo.h>  // Подключаем библиотеку для работы с сервоприводами

// Определяем возможные команды через enum
enum CommandType {
  CMD_LED_ON = 0x01,
  CMD_LED_OFF = 0x02,
  CMD_LED_BLINK = 0x03,
  CMD_GET_SENSOR = 0x04,
  CMD_SERVO_ANGLE = 0x05,    // Установить угол сервопривода
  CMD_GET_SERVO_ANGLE = 0x06 // Получить текущий угол
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

// Объект сервопривода
Servo myservo;
int current_servo_angle = 0;  // Текущий угол сервопривода

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Подключаем сервопривод к пину 9
  myservo.attach(9);
  myservo.write(0);  // Устанавливаем начальный угол 0 градусов
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

void setServoAngle(int angle) {
  // Ограничиваем угол от 0 до 180 градусов
  if (angle < 0) angle = 0;
  if (angle > 180) angle = 180;
  
  myservo.write(angle);
  current_servo_angle = angle;
}

void returnServoAngle() {
  // Отправляем текущий угол сервопривода обратно
  byte angle_data[] = {0xAA, 0x55, 0x02, CMD_GET_SERVO_ANGLE, (byte)current_servo_angle, 0xFF};
  angle_data[5] = check_crc(&angle_data[2], 2, 0); // Пересчитываем CRC
  Serial.write(angle_data, 6);
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

## Интеграция с Ollama для управления углом

Теперь обновим Python-интерфейс для поддержки команд управления сервоприводом:

```python
import serial
import time
import json
import requests
import re
import ollama

class Advanced_AI_Arduino_Interface:
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        self.arduino = serial.Serial(arduino_port, baudrate)
        time.sleep(2)  # ждем инициализации
        self.ollama_url = ollama_url
        self.use_local_ollama = use_local_ollama
        self.model = model
        
        # Определяем команды для Arduino
        self.commands = {
            'turn_on_led': {'command': 0x01, 'params': []},
            'turn_off_led': {'command': 0x02, 'params': []},
            'blink_led': {'command': 0x03, 'params': [3]},  # по умолчанию 3 раза
            'get_temperature': {'command': 0x04, 'params': []},
            'set_servo_angle': {'command': 0x05, 'params': [90]},  # по умолчанию 90 градусов
            'get_servo_angle': {'command': 0x06, 'params': []}
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
        elif 'servo' in ai_response_lower or 'servomotor' in ai_response_lower or 'rotate' in ai_response_lower:
            # Ищем угол в тексте
            angle_match = re.search(r'(\d+)', ai_response)
            if angle_match:
                angle = min(180, max(0, int(angle_match.group(1))))  # Ограничиваем от 0 до 180
                return 'set_servo_angle', [angle]
            else:
                return 'set_servo_angle', [90]  # по умолчанию 90 градусов
        elif 'angle' in ai_response_lower and 'servo' in ai_response_lower and ('current' in ai_response_lower or 'what' in ai_response_lower):
            return 'get_servo_angle', []
        
        return None, []
    
    def send_to_arduino(self, command_name, params=None):
        """Отправка команды на Arduino"""
        if command_name in self.commands:
            cmd_info = self.commands[command_name]
            
            if params is not None:
                # Используем переданные параметры
                data = [cmd_info['command']] + params
            else:
                # Используем параметры по умолчанию
                data = [cmd_info['command']] + cmd_info['params']
                
            crc = sum(data) & 0xFF
            packet = [0xAA, 0x55, len(data)] + data + [crc]
            
            self.arduino.write(bytes(packet))
            print(f"Отправлена команда {command_name} с параметрами {params}: {[hex(b) for b in packet]}")
            
        else:
            print(f"Неизвестная команда: {command_name}")
    
    def query_ollama(self, prompt):
        """Запрос к Ollama - использует либо HTTP API, либо локальную библиотеку ollama"""
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
        
        # Формируем промпт для ИИ, чтобы он распознал команды для Arduino
        ai_prompt = f"""
        Пользователь дал команду: "{user_request}"
        
        Возможные команды для Arduino:
        - turn_on_led: включить светодиод
        - turn_off_led: выключить светодиод  
        - blink_led: мигнуть светодиодом (по умолчанию 3 раза)
        - get_temperature: получить температуру с датчика
        - set_servo_angle: установить угол сервопривода (ожидает параметр - угол в градусах 0-180)
        - get_servo_angle: получить текущий угол сервопривода
        
        Если в команде указан угол (например, "поверни на 90 градусов"), извлеки только число и передай как параметр.
        Ответь в формате JSON: {{"command": "command_name", "params": [param1, param2, ...]}}
        Если команда не относится к Arduino, ответь: {{"command": "none", "params": []}}
        
        Примеры:
        Запрос: "Turn on the LED" -> Ответ: {{"command": "turn_on_led", "params": []}}
        Запрос: "Rotate servo to 90 degrees" -> Ответ: {{"command": "set_servo_angle", "params": [90]}}
        Запрос: "What is the current servo angle?" -> Ответ: {{"command": "get_servo_angle", "params": []}}
        """
        
        ai_response = self.query_ollama(ai_prompt)
        print(f"Ответ от ИИ: {ai_response.strip()}")
        
        try:
            # Пытаемся распарсить JSON из ответа ИИ
            parsed_response = json.loads(ai_response.strip())
            command = parsed_response.get('command')
            params = parsed_response.get('params', [])
        except json.JSONDecodeError:
            # Если JSON не распарсился, используем старый метод
            command, params = self.parse_command_from_ai(ai_response)
        
        if command and command != 'none':
            # Выполняем команду на Arduino
            self.send_to_arduino(command, params)
            
            # Ждем ответ от Arduino (если есть)
            start_time = time.time()
            while self.arduino.in_waiting == 0 and time.time() - start_time < 2:
                time.sleep(0.1)
            
            if self.arduino.in_waiting:
                response = self.arduino.readline().decode().strip()
                print(f"Ответ Arduino: {response}")
                
                # Обработка ответа о текущем угле сервопривода
                if 'SERVO ANGLE SET TO' in response:
                    print(f"Сервопривод установлен на {response.split(': ')[1]} градусов")
        else:
            print("Команда не распознана или не требует выполнения на Arduino")
    
    def close(self):
        self.arduino.close()

# Пример использования
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    interface = Advanced_AI_Arduino_Interface('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # interface = Advanced_AI_Arduino_Interface('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")

    # Примеры запросов
    interface.process_request("Turn on the LED")
    time.sleep(2)
    interface.process_request("Rotate servo to 90 degrees")
    time.sleep(3)
    interface.process_request("Rotate servo to 180 degrees")
    time.sleep(3)
    interface.process_request("Rotate servo to 0 degrees")
    time.sleep(3)
    interface.process_request("Turn off the LED")
    time.sleep(2)
    interface.process_request("What is the current servo angle?")

    interface.close()
```

## Задание для практики

1. Подключите сервопривод к Arduino согласно схеме из урока
2. Загрузите обновленный код в Arduino
3. Обновите Python-интерфейс с поддержкой сервопривода
4. Протестируйте команды:
   - "Rotate servo to 45 degrees"
   - "Turn servo to 135 degrees"
   - "Move servo to 90 degrees"
   - "What is the servo position?"
5. Попробуйте создать диалог с ИИ, где вы управляете как светодиодом, так и сервоприводом

В следующем уроке мы добавим датчики и создадим замкнутую систему, где ИИ может получать информацию от Arduino и принимать более сложные решения!