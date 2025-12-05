# Lesson AC-2: Реализация протокола связи в ИИ-агенте

## Цели урока

После изучения этого урока вы сможете:
- Реализовать структуру протокола в Python для общения с микроконтроллерами
- Создать систему кодирования и декодирования пакетов по протоколу
- Интегрировать протокол в архитектуру ИИ-агента как инструмент
- Обеспечить надежную передачу данных между ИИ-агентом и Arduino
- Объяснить важность контрольных сумм и синхронизации в протоколах

## 1. Введение: Почему простой текст недостаточен

В первом уроке мы использовали простую текстовую передачу данных между ИИ-агентом и Arduino. Это подходящий способ для начального тестирования, но он имеет серьезные ограничения:

1. **Отсутствие структуры**: Нет четкого разделения между командой и параметрами
2. **Отсутствие проверки целостности**: Мы не можем быть уверены, что данные не были повреждены при передаче
3. **Проблемы синхронизации**: Если соединение прерывается, трудно определить начало и конец сообщения
4. **Низкая эффективность**: Текст занимает больше места, чем бинарные данные

Для создания надежной системы взаимодействия нам нужен **хорошо определенный протокол**.

## 2. Структура протокола: Основные компоненты

Из туториала по протоколам мы уже знаем стандартную структуру пакета:

```
[SYNC1, SYNC2, LEN_DATA, DATA..., CRC]
```

Где:
- **SYNC1, SYNC2**: Байты синхронизации (0xAA, 0x55) - маркируют начало пакета
- **LEN_DATA**: Длина данных в байтах
- **DATA**: Полезная нагрузка (команда и параметры)
- **CRC**: Контрольная сумма для проверки целостности

### Пример полного пакета:
```
[0xAA, 0x55, 0x02, 0x01, 0x90, 0xF8]
```
- `0xAA, 0x55`: Синхронизация
- `0x02`: 2 байта данных
- `0x01, 0x90`: Данные (например, команда и параметр)
- `0xF8`: CRC (рассчитанная по байтам данных)

## 3. Реализация протокола в Python

Теперь мы создадим Python-класс, который будет:
1. Кодировать команды в пакеты по протоколу
2. Декодировать полученные пакеты
3. Проверять целостность данных с помощью CRC

```python
# protocol.py
import struct
from typing import List, Tuple, Optional

class Protocol:
    # Синхронизационные байты
    SYNC1 = 0xAA
    SYNC2 = 0x55
    
    def __init__(self):
        self.buffer = bytearray()  # Буфер для входящих данных
    
    def calculate_crc(self, data: bytes) -> int:
        """
        Вычисляет простую контрольную сумму (XOR всех байтов)
        """
        crc = 0
        for byte in data:
            crc ^= byte
        return crc & 0xFF  # Ограничиваем до 1 байта
    
    def encode_packet(self, data: List[int]) -> bytes:
        """
        Кодирует данные в пакет по протоколу
        """
        # Проверяем, что данных не больше 255 байт (ограничение для LEN_DATA)
        if len(data) > 255:
            raise ValueError("Слишком много данных для одного пакета")
        
        # Формируем пакет: SYNC1 + SYNC2 + LEN_DATA + DATA + CRC
        packet = bytearray()
        packet.append(self.SYNC1)
        packet.append(self.SYNC2)
        packet.append(len(data))  # Длина данных
        
        # Добавляем данные
        for byte in data:
            packet.append(byte & 0xFF)  # Ограничиваем до 1 байта
        
        # Вычисляем CRC от данных
        crc = self.calculate_crc(data)
        packet.append(crc)
        
        return bytes(packet)
    
    def decode_packet(self, packet_bytes: bytes) -> Optional[List[int]]:
        """
        Декодирует пакет и возвращает данные, если контрольная сумма верна
        """
        if len(packet_bytes) < 5:  # Минимальный размер пакета
            return None
        
        if packet_bytes[0] != self.SYNC1 or packet_bytes[1] != self.SYNC2:
            return None  # Неправильная синхронизация
        
        expected_len = packet_bytes[2]
        if len(packet_bytes) != 4 + expected_len:  # 4 = SYNC1, SYNC2, LEN, CRC + данные
            return None  # Неправильная длина
        
        data = list(packet_bytes[3:-1])  # Извлекаем данные (без синхронизации, длины и CRC)
        received_crc = packet_bytes[-1]  # Последний байт - CRC
        
        # Проверяем CRC
        calculated_crc = self.calculate_crc(data)
        if calculated_crc != received_crc:
            return None  # CRC не совпадает
        
        return data
    
    def feed_byte(self, byte: int) -> Optional[List[int]]:
        """
        Обрабатывает один байт из последовательного порта и возвращает пакет если он полный
        """
        self.buffer.append(byte)
        
        # Проверяем, есть ли в буфере полный пакет
        while len(self.buffer) >= 5:  # Минимальный размер пакета
            # Ищем начало пакета
            if self.buffer[0] == self.SYNC1 and self.buffer[1] == self.SYNC2:
                expected_len = self.buffer[2]
                packet_size = 4 + expected_len  # SYNC1, SYNC2, LEN, DATA, CRC
                
                if len(self.buffer) >= packet_size:
                    # Извлекаем полный пакет
                    packet = bytes(self.buffer[:packet_size])
                    self.buffer = self.buffer[packet_size:]  # Удаляем из буфера
                    
                    # Пытаемся декодировать
                    return self.decode_packet(packet)
                else:
                    # Пакет еще не полный, ждем больше байтов
                    break
            else:
                # Неправильная синхронизация, удаляем первый байт
                self.buffer.pop(0)
        
        return None

# Тестирование протокола
if __name__ == "__main__":
    proto = Protocol()
    
    # Тест кодирования
    test_data = [0x01, 0x90]  # Команда и параметр
    encoded = proto.encode_packet(test_data)
    print(f"Закодированный пакет: {[hex(b) for b in encoded]}")
    
    # Тест декодирования
    decoded = proto.decode_packet(encoded)
    print(f"Декодированные данные: {[hex(b) for b in decoded] if decoded else 'None'}")
    print(f"Совпадают ли данные: {test_data == decoded}")
    
    # Тест обработки байтов
    for byte in encoded:
        result = proto.feed_byte(byte)
        if result:
            print(f"Получен пакет: {[hex(b) for b in result]}")
```

## 4. Интеграция протокола в Arduino-инструмент

Теперь мы обновим наш Arduino-инструмент, чтобы он использовал протокол для передачи данных:

```python
# arduino_protocol.py
import serial
import time
from typing import Dict, Any, Optional
from protocol import Protocol

class ArduinoProtocolInterface:
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.protocol = Protocol()
        self.connect()
    
    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Время на сброс Arduino
            print(f"Подключено к Arduino на порту {self.port}")
        except Exception as e:
            print(f"Ошибка подключения к Arduino: {e}")
    
    def send_command(self, command: int, params: Optional[list] = None) -> str:
        """
        Отправляет команду на Arduino через протокол
        command: байт команды (0x00-0xFF)
        params: список параметров (каждый параметр - байт)
        """
        # Формируем данные: [COMMAND, PARAM1, PARAM2, ...]
        if params is None:
            data = [command]
        else:
            data = [command] + [p & 0xFF for p in params]  # Ограничиваем до 1 байта
        
        # Кодируем в пакет
        packet = self.protocol.encode_packet(data)
        
        try:
            # Отправляем пакет
            self.ser.write(packet)
            
            # Ждем ответ
            response = self.wait_for_response(timeout=2.0)
            if response:
                return f"Команда {hex(command)} выполнена. Ответ: {[hex(b) for b in response]}"
            else:
                return f"Команда {hex(command)} отправлена, но ответ не получен"
        except Exception as e:
            return f"Ошибка выполнения команды: {e}"
    
    def wait_for_response(self, timeout: float = 2.0) -> Optional[list]:
        """
        Ждет ответ от Arduino с таймаутом
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                byte = self.ser.read(1)[0]
                result = self.protocol.feed_byte(byte)
                if result:
                    return result
            time.sleep(0.01)  # Небольшая задержка, чтобы не перегружать процессор
        return None
    
    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

# Спецификация команд для Arduino
ARDUINO_COMMANDS = {
    'LED_ON': 0x01,
    'LED_OFF': 0x02,
    'SET_SERVO_ANGLE': 0x03,
    'READ_SENSOR': 0x04,
    'GET_STATUS': 0x05
}

# Пример использования как инструмента для ИИ-агента
def create_protocol_arduino_tool(port: str = 'COM3'):
    arduino = ArduinoProtocolInterface(port)
    
    def send_command_to_arduino(command: str, params: Dict[str, Any] = None) -> str:
        # Преобразуем текстовую команду в байт
        cmd_byte = ARDUINO_COMMANDS.get(command.upper())
        if cmd_byte is None:
            return f"Неизвестная команда: {command}"
        
        # Подготовим параметры
        param_list = None
        if params:
            param_list = []
            for value in params.values():
                # Преобразуем значение в байт (или список байтов)
                if isinstance(value, list):
                    param_list.extend([int(v) & 0xFF for v in value])
                else:
                    param_list.append(int(value) & 0xFF)
        
        result = arduino.send_command(cmd_byte, param_list)
        return result
    
    # Закрываем соединение при завершении
    import atexit
    atexit.register(arduino.close)
    
    return send_command_to_arduino

# Тестирование
if __name__ == "__main__":
    # Создаем инструмент
    arduino_tool = create_protocol_arduino_tool()
    
    # Тестируем команды
    print(arduino_tool("LED_ON"))
    time.sleep(1)
    print(arduino_tool("LED_OFF"))
```

## 5. Обновленная прошивка Arduino для работы с протоколом

Для работы с протоколом мы также должны обновить прошивку Arduino:

```cpp
// arduino_protocol_firmware.ino
#include <stdint.h>

// Определяем возможные команды через enum (как в туториале по протоколам)
enum CommandType {
  CMD_LED_ON = 0x01,
  CMD_LED_OFF = 0x02,
  CMD_SET_SERVO_ANGLE = 0x03,
  CMD_READ_SENSOR = 0x04,
  CMD_GET_STATUS = 0x05
};

// FSM состояния приёма пакета
enum ReceiveState {
  WAIT_SYNC1,
  WAIT_SYNC2,
  WAIT_LEN,
  WAIT_DATA,
  WAIT_CRC
};

// Константы протокола
const uint8_t SYNC1 = 0xAA;
const uint8_t SYNC2 = 0x55;

// Переменные для FSM
ReceiveState currentState = WAIT_SYNC1;
uint8_t buffer[256]; // буфер для данных
int dataIndex = 0;
int expectedDataLen = 0;

// Пины
const int LED_PIN = 13;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // Светодиод выключен по умолчанию
}

void loop() {
  // FSM для обработки входящих байтов
  while (Serial.available()) {
    uint8_t incomingByte = Serial.read();

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
          processCommand(buffer[0]); // первый байт данных - это команда
        } else {
          Serial.println("CRC_ERROR");
        }
        currentState = WAIT_SYNC1; // возвращаемся к ожиданию следующего пакета
        break;
    }
  }
}

void processCommand(uint8_t command) {
  switch(command) {
    case CMD_LED_ON:
      digitalWrite(LED_PIN, HIGH);
      sendAck(command);
      break;
      
    case CMD_LED_OFF:
      digitalWrite(LED_PIN, LOW);
      sendAck(command);
      break;
      
    case CMD_SET_SERVO_ANGLE:
      if (expectedDataLen > 1) {
        setServoAngle(buffer[1]); // второй байт данных - угол
      }
      sendAck(command);
      break;
      
    case CMD_READ_SENSOR:
      sendSensorData();
      break;
      
    case CMD_GET_STATUS:
      sendStatus();
      break;
      
    default:
      Serial.println("UNKNOWN_CMD");
      break;
  }
}

void sendAck(uint8_t command) {
  // Отправляем подтверждение выполнения команды
  uint8_t data[] = {0xFF, command}; // 0xFF - код подтверждения
  sendPacket(data, sizeof(data));
}

void sendSensorData() {
  // Симулируем чтение сенсора
  int sensorValue = analogRead(A0);  // Чтение с аналогового пина
  uint8_t data[] = {CMD_READ_SENSOR, (uint8_t)(sensorValue & 0xFF), (uint8_t)(sensorValue >> 8)};
  sendPacket(data, sizeof(data));
}

void sendStatus() {
  uint8_t ledStatus = digitalRead(LED_PIN);
  uint8_t data[] = {CMD_GET_STATUS, ledStatus};
  sendPacket(data, sizeof(data));
}

void setServoAngle(uint8_t angle) {
  // Здесь должна быть реализация управления сервоприводом
  // Пока что просто выводим значение
  Serial.print("Servo angle set to: ");
  Serial.println(angle);
}

void sendPacket(uint8_t* data, int len) {
  // Отправляем пакет по протоколу: [SYNC1, SYNC2, LEN, DATA..., CRC]
  Serial.write(SYNC1);
  Serial.write(SYNC2);
  Serial.write((uint8_t)len);
  
  for (int i = 0; i < len; i++) {
    Serial.write(data[i]);
  }
  
  // Отправляем CRC
  uint8_t crc = calculateCRC(data, len);
  Serial.write(crc);
}

uint8_t calculateCRC(uint8_t* data, int len) {
  uint8_t crc = 0;
  for (int i = 0; i < len; i++) {
    crc ^= data[i];
  }
  return crc;
}

bool check_crc(uint8_t data[], int len, uint8_t received_crc) {
  uint8_t calc_crc = 0;
  for (int i = 0; i < len; i++) {
    calc_crc ^= data[i];
  }
  return calc_crc == received_crc;
}
```

## 6. Интеграция протокола в архитектуру Ollama ИИ-агента

Теперь мы интегрируем протокольный инструмент в архитектуру Ollama ИИ-агента:

```python
# ollama_agent_with_protocol.py
import ollama
import json
from arduino_protocol import create_protocol_arduino_tool

class OllamaProtocolAgent:
    def __init__(self, arduino_port: str = 'COM3'):
        self.arduino_tool = create_protocol_arduino_tool(arduino_port)

        # Определяем инструменты для Ollama
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "send_command_to_arduino",
                    "description": "Отправка команды на Arduino устройство через протокол",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "enum": ["LED_ON", "LED_OFF", "SET_SERVO_ANGLE", "READ_SENSOR", "GET_STATUS"],
                                "description": "Команда для Arduino"
                            },
                            "params": {
                                "type": "object",
                                "description": "Параметры команды, например угол для сервопривода"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

    def run_with_ollama(self, user_request: str) -> str:
        """
        Выполняет запрос пользователя через Ollama с использованием инструментов
        """
        system_prompt = """
        Ты — ИИ-агент, способный управлять Arduino устройствами через протокол.
        Используй инструмент send_command_to_arduino для взаимодействия с Arduino.
        Команды могут быть: LED_ON, LED_OFF, SET_SERVO_ANGLE, READ_SENSOR, GET_STATUS.
        Для SET_SERVO_ANGLE используй параметр angle.
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
                tools=self.tools,
                options={"temperature": 0.3}
            )

            message = response['message']

            # Проверяем, вызваны ли инструменты
            if 'tool_calls' in message and message['tool_calls']:
                results = []
                for tool_call in message['tool_calls']:
                    function_name = tool_call['function']['name']
                    arguments = json.loads(tool_call['function']['arguments'])

                    if function_name == "send_command_to_arduino":
                        # Выполняем команду Arduino через протокол
                        result = self.arduino_tool(
                            command=arguments.get('command'),
                            params=arguments.get('params', {})
                        )
                        results.append(result)

                # Если были вызовы инструментов, получаем финальный ответ
                if results:
                    tool_results_content = "Результаты выполнения команд: " + "; ".join(results)

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

# Тестирование Ollama протокольного агента
if __name__ == "__main__":
    print("=== Тестирование Ollama протокольного агента ===")

    agent = OllamaProtocolAgent()  # Можно указать конкретный порт

    test_queries = [
        "Включи светодиод на Arduino",
        "Выключи светодиод на Arduino",
        "Покажи статус устройства",
        "Установи угол сервопривода на 45 градусов",
        "Прочитай значение с датчика"
    ]

    for query in test_queries:
        print(f"\n--- Запрос: {query} ---")
        result = agent.run_with_ollama(query)
        print(f"Результат: {result}")
        print("-" * 50)
```

## 7. Проверка надежности протокола

Один из ключевых аспектов протокола - его надежность. Давайте создадим тест, который проверит, как наша система справляется с различными проблемами передачи:

```python
# protocol_tests.py
import random
from protocol import Protocol

def test_protocol_basic():
    """Тест основной функциональности протокола"""
    proto = Protocol()
    
    # Тестируем разные наборы данных
    test_cases = [
        [0x01],
        [0x01, 0x90],
        [0x01, 0x02, 0x03, 0x04, 0x05],
        list(range(20))  # 20 байт данных
    ]
    
    all_passed = True
    for data in test_cases:
        encoded = proto.encode_packet(data)
        decoded = proto.decode_packet(encoded)
        if decoded != data:
            print(f"Ошибка: данные {data} не совпали после кодирования/декодирования")
            all_passed = False
    
    if all_passed:
        print("✓ Все базовые тесты протокола пройдены")

def test_protocol_with_noise():
    """Тест устойчивости к шуму в данных"""
    proto = Protocol()
    
    original_data = [0x01, 0x90, 0x02]
    encoded = proto.encode_packet(original_data)
    
    # Симулируем передачу с возможными ошибками
    encoded_list = list(encoded)
    
    # Иногда добавляем лишние байты (шум)
    noisy_data = [0xFF, 0xFE] + encoded_list  # Добавляем мусор в начало
    
    # Проверяем, сможет ли протокол извлечь правильный пакет
    extracted = []
    for byte in noisy_data:
        result = proto.feed_byte(byte)
        if result:
            extracted = result
            break
    
    if extracted == original_data:
        print("✓ Протокол корректно обработал шум")
    else:
        print(f"✗ Протокол не справился с шумом. Оригинал: {original_data}, извлечено: {extracted}")

def test_protocol_crc():
    """Тест проверки CRC"""
    proto = Protocol()
    
    original_data = [0x01, 0x90, 0x02]
    encoded = list(proto.encode_packet(original_data))
    
    # Меняем один байт данных, чтобы сломать CRC
    if len(encoded) > 4:  # Убедимся, что у нас есть данные для изменения
        encoded[3] ^= 0xFF  # Изменяем первый байт данных
    
    # Попробуем декодировать поврежденный пакет
    result = proto.decode_packet(bytes(encoded))
    
    if result is None:
        print("✓ CRC корректно обнаружил повреждение данных")
    else:
        print("✗ CRC не обнаружил повреждение данных")

if __name__ == "__main__":
    print("=== Тестирование протокола ===")
    test_protocol_basic()
    test_protocol_with_noise() 
    test_protocol_crc()
```

## 8. Заключение: Мощь структурированного взаимодействия с Ollama

В этом уроке мы:
- Создали полноценную реализацию протокола для надежной связи Python ↔ Arduino
- Обеспечили проверку целостности данных с помощью CRC
- Реализовали систему синхронизации для надежного определения начала и конца пакетов
- Интегрировали протокол в архитектуру Ollama ИИ-агента как надежный инструмент
- Протестировали устойчивость протокола к ошибкам передачи
- Научились использовать Ollama для понимания естественного языка и вызова протокольных инструментов

Теперь наш Ollama ИИ-агент может надежно взаимодействовать с физическими устройствами, понимая команды на естественном языке и зная, что команды будут доставлены корректно и ответы не будут искажены. Это фундамент для создания надежных систем автоматизации, робототехники и IoT-устройств на базе локальных LLM.

В следующем уроке мы рассмотрим, как Ollama ИИ-агент может не только отправлять команды в Arduino, но и корректно обрабатывать ответы от него, создавая полноценный двунаправленный канал коммуникации с использованием Ollama.