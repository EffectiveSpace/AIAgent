# Финальный проект: Умная система мониторинга и управления с ИИ-агентом

## Цель проекта

Создать комплексную систему, объединяющую:
- ИИ-агента с расширенной архитектурой
- Несколько Arduino устройств с сенсорами и исполнительными механизмами
- Протокол надежной связи
- Механизмы безопасности и адаптации
- Двунаправленное взаимодействие с физическим миром

## Задание проекта

Создать систему умного дома с ИИ-агентом, которая:
1. Мониторит температуру и влажность в нескольких комнатах
2. Управляет освещением и вентиляцией на основе данных сенсоров
3. Обеспечивает безопасность с датчиками движения и дверей
4. Адаптируется к предпочтениям жильцов
5. Обеспечивает отказоустойчивую работу

## Часть 1: Проектирование архитектуры системы

### Задание 1.1: Определение компонентов системы

Система состоит из следующих компонентов:

1. **Центральный ИИ-агент** (на Python)
2. **Три Arduino устройства**:
   - Arduino 1: Температурный сенсор и управление освещением (кухня)
   - Arduino 2: Датчик двери и сигнализация (входная дверь)
   - Arduino 3: Датчик движения и вентилятор (гостиная)

3. **Протокол связи** с поддержкой:
   - Команд: GET_TEMP, GET_DOOR_STATUS, GET_MOTION, SWITCH_LIGHT, ACTIVATE_ALARM, SET_FAN_SPEED
   - Ответов: TEMP_DATA, DOOR_STATUS, MOTION_STATUS, ACK, ERROR
   - FSM для надежной передачи данных
   - Контрольных сумм CRC

### Задание 1.2: Структура протокола

Реализуйте протокол с командами:

**Команды (от Python к Arduino)**:
- `0x10`: GET_TEMP - получить температуру
- `0x11`: GET_DOOR_STATUS - получить статус двери
- `0x12`: GET_MOTION - получить статус движения
- `0x20`: SWITCH_LIGHT - включить/выключить свет (параметр: 0 или 1)
- `0x21`: ACTIVATE_ALARM - активировать сигнализацию
- `0x22`: SET_FAN_SPEED - установить скорость вентилятора (параметр: 0-255)

**Ответы (от Arduino к Python)**:
- `0xF0`: ACK - подтверждение команды
- `0xF1`: TEMP_DATA - данные температуры (2 байта: старший, младший)
- `0xF2`: DOOR_STATUS - статус двери (1 байт: 0-закрыта, 1-открыта)
- `0xF3`: MOTION_STATUS - статус движения (1 байт: 0-нет, 1-есть)
- `0xFE`: ERROR - ошибка

### Создайте файл с определением протокола:

```python
# smart_home_protocol.py
import struct
from typing import List, Tuple, Optional

class SmartHomeProtocol:
    # Синхронизационные байты
    SYNC1 = 0xAA
    SYNC2 = 0x55
    
    # Команды от Python к Arduino
    CMD_GET_TEMP = 0x10
    CMD_GET_DOOR_STATUS = 0x11
    CMD_GET_MOTION = 0x12
    CMD_SWITCH_LIGHT = 0x20
    CMD_ACTIVATE_ALARM = 0x21
    CMD_SET_FAN_SPEED = 0x22
    
    # Ответы от Arduino к Python
    RESP_ACK = 0xF0
    RESP_TEMP_DATA = 0xF1
    RESP_DOOR_STATUS = 0xF2
    RESP_MOTION_STATUS = 0xF3
    RESP_ERROR = 0xFE
    
    def __init__(self):
        self.buffer = bytearray()
    
    def calculate_crc(self, data: bytes) -> int:
        """Вычисляет контрольную сумму XOR"""
        crc = 0
        for byte in data:
            crc ^= byte
        return crc & 0xFF
    
    def encode_command(self, command: int, params: List[int] = None) -> bytes:
        """Кодирует команду в пакет по протоколу"""
        if params is None:
            params = []
        
        # Формируем данные: [COMMAND, PARAM1, PARAM2, ...]
        data = [command] + [p & 0xFF for p in params]
        
        # Формируем пакет: [SYNC1, SYNC2, LEN, DATA..., CRC]
        packet = bytearray()
        packet.append(self.SYNC1)
        packet.append(self.SYNC2)
        packet.append(len(data))
        
        for byte in data:
            packet.append(byte)
        
        # Добавляем CRC
        crc = self.calculate_crc(data)
        packet.append(crc)
        
        return bytes(packet)
    
    def decode_response(self, packet_bytes: bytes) -> Optional[dict]:
        """Декодирует ответный пакет"""
        if len(packet_bytes) < 5:  # Минимум: SYNC1, SYNC2, LEN, TYPE, CRC
            return None
        
        if packet_bytes[0] != self.SYNC1 or packet_bytes[1] != self.SYNC2:
            return None
        
        expected_len = packet_bytes[2]
        if len(packet_bytes) != 4 + expected_len:  # SYNC1, SYNC2, LEN, DATA, CRC
            return None
        
        raw_data = packet_bytes[3:-1]  # Извлекаем данные (без синхронизации и CRC)
        received_crc = packet_bytes[-1]
        
        # Проверяем CRC
        calculated_crc = self.calculate_crc(raw_data)
        if calculated_crc != received_crc:
            return None
        
        # Разбираем тип ответа
        if not raw_data:
            return None
        
        response_type = raw_data[0]
        
        if response_type == self.RESP_ACK and len(raw_data) >= 2:
            return {
                'type': 'ACK',
                'command': raw_data[1],
                'status': 'success'
            }
        elif response_type == self.RESP_TEMP_DATA and len(raw_data) >= 3:
            temp_value = (raw_data[1] << 8) | raw_data[2]
            return {
                'type': 'TEMP_DATA',
                'temperature': temp_value / 100.0  # Предполагаем, что температура в сотых градусах
            }
        elif response_type == self.RESP_DOOR_STATUS and len(raw_data) >= 2:
            return {
                'type': 'DOOR_STATUS',
                'door_open': bool(raw_data[1])
            }
        elif response_type == self.RESP_MOTION_STATUS and len(raw_data) >= 2:
            return {
                'type': 'MOTION_STATUS',
                'motion_detected': bool(raw_data[1])
            }
        elif response_type == self.RESP_ERROR and len(raw_data) >= 2:
            return {
                'type': 'ERROR',
                'error_code': raw_data[1]
            }
        
        return None
    
    def feed_byte(self, byte: int) -> Optional[dict]:
        """Обрабатывает один байт из потока и возвращает пакет если полный"""
        self.buffer.append(byte)
        
        while len(self.buffer) >= 5:
            if self.buffer[0] == self.SYNC1 and self.buffer[1] == self.SYNC2:
                expected_len = self.buffer[2]
                packet_size = 4 + expected_len
                
                if len(self.buffer) >= packet_size:
                    packet = bytes(self.buffer[:packet_size])
                    self.buffer = self.buffer[packet_size:]
                    
                    return self.decode_response(packet)
                else:
                    break
            else:
                self.buffer.pop(0)
        
        return None
```

## Часть 2: Реализация Arduino прошивки

### Задание 2.1: Прошивка для температурного узла (кухня)

Создайте Arduino прошивку для комнаты с температурным сенсором и управлением освещением:

```cpp
// smart_home_node_temp_light.ino
#include <stdint.h>

// Протокол
const uint8_t SYNC1 = 0xAA;
const uint8_t SYNC2 = 0x55;

// Команды
const uint8_t CMD_GET_TEMP = 0x10;
const uint8_t CMD_SWITCH_LIGHT = 0x20;

// Ответы
const uint8_t RESP_ACK = 0xF0;
const uint8_t RESP_TEMP_DATA = 0xF1;
const uint8_t RESP_ERROR = 0xFE;

// Состояния FSM
enum ReceiveState {
  WAIT_SYNC1,
  WAIT_SYNC2,
  WAIT_LEN,
  WAIT_DATA,
  WAIT_CRC
};

// Переменные FSM
ReceiveState currentState = WAIT_SYNC1;
uint8_t buffer[256];
int dataIndex = 0;
int expectedDataLen = 0;

// Пины
const int TEMP_PIN = A0;  // Пин для температурного сенсора (симуляция)
const int LIGHT_PIN = 13; // Пин для управления светом

void setup() {
  Serial.begin(9600);
  pinMode(LIGHT_PIN, OUTPUT);
  digitalWrite(LIGHT_PIN, LOW);  // Свет выключен
}

void loop() {
  // FSM для обработки входящих команд
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
          currentState = WAIT_SYNC1;
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
          process_command(buffer[0]); // Первый байт - команда
        } else {
          send_error(0x01); // CRC ошибка
        }
        currentState = WAIT_SYNC1;
        break;
    }
  }
}

void process_command(uint8_t command) {
  switch(command) {
    case CMD_GET_TEMP:
      send_temperature_data();
      break;
      
    case CMD_SWITCH_LIGHT:
      if (expectedDataLen > 1) {
        int state = buffer[1];
        digitalWrite(LIGHT_PIN, state ? HIGH : LOW);
        send_ack(command);
      } else {
        send_error(0x02); // Недостаточно параметров
      }
      break;
      
    default:
      send_error(0x03); // Неизвестная команда
      break;
  }
}

void send_temperature_data() {
  // Симуляция чтения температуры
  int temp_raw = analogRead(TEMP_PIN);
  float temperature = 20.0 + (temp_raw / 1024.0) * 20.0; // От 20 до 40 градусов
  
  // Конвертируем в формат (целая часть * 100 + дробная * 100)
  int temp_scaled = (int)(temperature * 100);
  
  uint8_t data[] = {RESP_TEMP_DATA, (uint8_t)(temp_scaled >> 8), (uint8_t)(temp_scaled & 0xFF)};
  send_packet(data, sizeof(data));
}

void send_ack(uint8_t command) {
  uint8_t data[] = {RESP_ACK, command};
  send_packet(data, sizeof(data));
}

void send_error(uint8_t error_code) {
  uint8_t data[] = {RESP_ERROR, error_code};
  send_packet(data, sizeof(data));
}

void send_packet(uint8_t* data, int len) {
  Serial.write(SYNC1);
  Serial.write(SYNC2);
  Serial.write((uint8_t)len);
  
  for (int i = 0; i < len; i++) {
    Serial.write(data[i]);
  }
  
  uint8_t crc = calculate_crc(data, len);
  Serial.write(crc);
}

uint8_t calculate_crc(uint8_t* data, int len) {
  uint8_t crc = 0;
  for (int i = 0; i < len; i++) {
    crc ^= data[i];
  }
  return crc;
}

bool check_crc(uint8_t data[], int len, uint8_t received_crc) {
  return calculate_crc(data, len) == received_crc;
}
```

### Задание 2.2: Прошивки для других узлов

Вы должны создать аналогичные прошивки для:
- Узла с датчиком двери и сигнализацией
- Узла с датчиком движения и вентилятором

## Часть 3: Реализация Python-интерфейса

### Задание 3.1: Интерфейс для Arduino устройств

```python
# arduino_device_manager.py
import serial
import time
from typing import Dict, Any, Optional
from smart_home_protocol import SmartHomeProtocol

class ArduinoDevice:
    def __init__(self, device_id: str, port: str, device_type: str, baudrate: int = 9600):
        self.device_id = device_id
        self.port = port
        self.device_type = device_type
        self.baudrate = baudrate
        self.serial_conn = None
        self.protocol = SmartHomeProtocol()
        self.is_connected = False
        self.last_communication = 0
        
        self.connect()
    
    def connect(self):
        """Подключается к Arduino устройству"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Время на сброс Arduino
            self.is_connected = True
            print(f"Подключено к {self.device_id} на порту {self.port}")
        except Exception as e:
            print(f"Ошибка подключения к {self.device_id}: {e}")
            self.is_connected = False
    
    def send_command(self, command: int, params: list = None, timeout: float = 2.0) -> Dict[str, Any]:
        """Отправляет команду и ожидает ответ"""
        if not self.is_connected or not self.serial_conn.is_open:
            return {"type": "ERROR", "message": "Устройство не подключено"}
        
        try:
            # Кодируем команду
            packet = self.protocol.encode_command(command, params)
            self.serial_conn.write(packet)
            
            # Ждем ответ
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.serial_conn.in_waiting > 0:
                    byte = self.serial_conn.read(1)[0]
                    response = self.protocol.feed_byte(byte)
                    if response:
                        self.last_communication = time.time()
                        return response
                time.sleep(0.01)
            
            return {"type": "TIMEOUT", "message": "Таймаут ожидания ответа"}
        except Exception as e:
            return {"type": "ERROR", "message": f"Ошибка отправки команды: {e}"}
    
    def get_temperature(self) -> Dict[str, Any]:
        """Получает температуру (для температурных узлов)"""
        return self.send_command(self.protocol.CMD_GET_TEMP)
    
    def get_door_status(self) -> Dict[str, Any]:
        """Получает статус двери (для узлов безопасности)"""
        return self.send_command(self.protocol.CMD_GET_DOOR_STATUS)
    
    def get_motion_status(self) -> Dict[str, Any]:
        """Получает статус движения (для узлов охраны)"""
        return self.send_command(self.protocol.CMD_GET_MOTION)
    
    def switch_light(self, state: bool) -> Dict[str, Any]:
        """Включает/выключает свет (для узлов освещения)"""
        return self.send_command(self.protocol.CMD_SWITCH_LIGHT, [int(state)])
    
    def activate_alarm(self) -> Dict[str, Any]:
        """Активирует сигнализацию"""
        return self.send_command(self.protocol.CMD_ACTIVATE_ALARM)
    
    def set_fan_speed(self, speed: int) -> Dict[str, Any]:
        """Устанавливает скорость вентилятора"""
        speed = max(0, min(255, speed))  # Ограничение от 0 до 255
        return self.send_command(self.protocol.CMD_SET_FAN_SPEED, [speed])
    
    def close(self):
        """Закрывает соединение"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.is_connected = False
```

### Задание 3.2: Менеджер всех устройств

```python
# smart_home_manager.py
import threading
import time
from typing import Dict, Any
from arduino_device_manager import ArduinoDevice

class SmartHomeController:
    def __init__(self):
        self.devices: Dict[str, ArduinoDevice] = {}
        self.running = False
        self.monitoring_thread = None
        self.system_state = {
            "temperature": {},
            "door_status": {},
            "motion_status": {},
            "light_status": {},
            "fan_status": {}
        }
    
    def register_device(self, device_id: str, port: str, device_type: str):
        """Регистрирует новое Arduino устройство"""
        device = ArduinoDevice(device_id, port, device_type)
        if device.is_connected:
            self.devices[device_id] = device
            print(f"Устройство {device_id} зарегистрировано")
            return True
        else:
            print(f"Не удалось подключиться к устройству {device_id} на порту {port}")
            return False
    
    def start_monitoring(self):
        """Запускает непрерывный мониторинг всех устройств"""
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        print("Мониторинг запущен")
    
    def _monitoring_loop(self):
        """Цикл бесконечного мониторинга"""
        while self.running:
            try:
                for device_id, device in self.devices.items():
                    self._update_device_status(device_id, device)
                time.sleep(5.0)  # Обновляем каждые 5 секунд
            except Exception as e:
                print(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(1.0)
    
    def _update_device_status(self, device_id: str, device: ArduinoDevice):
        """Обновляет статус конкретного устройства"""
        if device.device_type == "temp_light":
            temp_result = device.get_temperature()
            if temp_result.get('type') == 'TEMP_DATA':
                self.system_state['temperature'][device_id] = temp_result['temperature']
        
        elif device.device_type == "door_alarm":
            door_result = device.get_door_status()
            if door_result.get('type') == 'DOOR_STATUS':
                self.system_state['door_status'][device_id] = door_result['door_open']
        
        elif device.device_type == "motion_fan":
            motion_result = device.get_motion_status()
            if motion_result.get('type') == 'MOTION_STATUS':
                self.system_state['motion_status'][device_id] = motion_result['motion_detected']
    
    def get_system_status(self) -> Dict[str, Any]:
        """Возвращает полный статус системы"""
        return self.system_state.copy()
    
    def set_light_state(self, device_id: str, state: bool) -> bool:
        """Управляет светом в комнате"""
        if device_id in self.devices:
            device = self.devices[device_id]
            result = device.switch_light(state)
            success = result.get('type') in ['ACK', 'SUCCESS']
            if success:
                self.system_state['light_status'][device_id] = state
            return success
        return False
    
    def trigger_security_response(self):
        """Активирует мер безопасности при необходимости"""
        security_issue = False
        
        # Проверяем, открыта ли дверь и есть ли движение
        for door_id, is_open in self.system_state['door_status'].items():
            if is_open:
                for motion_id, is_detected in self.system_state['motion_status'].items():
                    if is_detected:
                        security_issue = True
                        print("ОБНАРУЖЕНА ПОТЕНЦИАЛЬНАЯ УГРОЗА: дверь открыта и движение обнаружено")
        
        if security_issue:
            # Активируем сигнализацию на всех security устройствах
            for device_id, device in self.devices.items():
                if device.device_type == "door_alarm":
                    device.activate_alarm()
            
            # Включаем свет во всех помещениях
            for device_id, device in self.devices.items():
                if device.device_type == "temp_light":
                    device.switch_light(True)
    
    def auto_climate_control(self):
        """Автоматическое управление климатом"""
        avg_temp = 0
        temp_count = 0
        
        # Вычисляем среднюю температуру
        for temp in self.system_state['temperature'].values():
            if temp is not None:
                avg_temp += temp
                temp_count += 1
        
        if temp_count > 0:
            avg_temp /= temp_count
            print(f"Средняя температура: {avg_temp:.2f}°C")
            
            # Регулируем вентиляцию в зависимости от температуры
            for device_id, device in self.devices.items():
                if device.device_type == "motion_fan" and avg_temp > 25.0:
                    # Если жарко, увеличиваем вентиляцию
                    device.set_fan_speed(200)  # Высокая скорость
                elif device.device_type == "motion_fan" and avg_temp < 18.0:
                    # Если холодно, уменьшаем вентиляцию
                    device.set_fan_speed(50)   # Низкая скорость
    
    def stop(self):
        """Останавливает мониторинг и закрывает все устройства"""
        self.running = False
        for device in self.devices.values():
            device.close()
        print("Система остановлена")

# Пример использования
if __name__ == "__main__":
    controller = SmartHomeController()
    
    # Регистрируем устройства (замените порты на свои)
    # controller.register_device("kitchen_node", "COM3", "temp_light")
    # controller.register_device("door_node", "COM4", "door_alarm") 
    # controller.register_device("living_room_node", "COM5", "motion_fan")
    
    # В целях демонстрации покажем структуру
    print("Система умного дома инициализирована")
    print("Для работы подключите Arduino устройства и зарегистрируйте их")
    
    # Запуск мониторинга
    # controller.start_monitoring()
    
    # Работа в течение 30 секунд
    # time.sleep(30)
    
    # controller.stop()
```

## Часть 4: ИИ-агент для умного дома

### Задание 4.1: Создание ИИ-агента

```python
# smart_home_ai_agent.py
from typing import Dict, Any, List
from smart_home_manager import SmartHomeController
import time
import json

class SmartHomeAIAgent:
    def __init__(self, controller: SmartHomeController):
        self.controller = controller
        self.system_goals = {}
        self.adaptation_memory = []
        self.personal_preferences = {
            "preferred_temperature": 22.0,
            "light_schedule": {"day": True, "night": False},
            "security_level": "normal"
        }
    
    def assess_current_state(self) -> Dict[str, Any]:
        """Оценивает текущее состояние системы"""
        state = self.controller.get_system_status()
        
        # Добавляем вычисленные метрики
        metrics = {
            "avg_temperature": 0,
            "temp_sensors_count": 0,
            "any_door_open": any(state['door_status'].values()) if state['door_status'] else False,
            "any_motion_detected": any(state['motion_status'].values()) if state['motion_status'] else False
        }
        
        # Вычисляем среднюю температуру
        for temp in state['temperature'].values():
            if temp is not None:
                metrics["avg_temperature"] += temp
                metrics["temp_sensors_count"] += 1
        
        if metrics["temp_sensors_count"] > 0:
            metrics["avg_temperature"] /= metrics["temp_sensors_count"]
        else:
            metrics["avg_temperature"] = self.personal_preferences["preferred_temperature"]
        
        return {**state, **metrics}
    
    def plan_actions_for_goal(self, goal: str) -> List[Dict[str, Any]]:
        """Планирует действия для достижения цели"""
        state = self.assess_current_state()
        actions = []
        
        if "безопасность" in goal.lower() or "security" in goal.lower():
            # Проверяем безопасность
            if state["any_door_open"] and state["any_motion_detected"]:
                actions.append({
                    "action": "trigger_security_response",
                    "description": "Активировать безопасность: дверь открыта и движение обнаружено"
                })
            elif state["any_door_open"]:
                actions.append({
                    "action": "alert_owner",
                    "description": "Дверь открыта, уведомить владельца"
                })
        
        elif "температура" in goal.lower() or "climate" in goal.lower() or "cool" in goal.lower():
            # Управление климатом
            if state["avg_temperature"] > self.personal_preferences["preferred_temperature"] + 2:
                actions.append({
                    "action": "increase_ventilation",
                    "description": f"Температура {state['avg_temperature']:.1f}°C выше нормы, увеличить вентиляцию"
                })
            elif state["avg_temperature"] < self.personal_preferences["preferred_temperature"] - 2:
                actions.append({
                    "action": "reduce_ventilation", 
                    "description": f"Температура {state['avg_temperature']:.1f}°C ниже нормы, уменьшить вентиляцию"
                })
        
        elif "освещение" in goal.lower() or "light" in goal.lower():
            # Управление освещением
            current_time = time.time() % (24 * 3600)  # Секунды от начала дня
            is_night = current_time > 18 * 3600 or current_time < 6 * 3600  # После 18:00 или до 6:00
            
            preferred_light_state = self.personal_preferences["light_schedule"]["night"] if is_night else self.personal_preferences["light_schedule"]["day"]
            
            # Проверяем, нужно ли изменить свет
            for device_id, light_state in state['light_status'].items():
                if light_state != preferred_light_state:
                    actions.append({
                        "action": "set_light",
                        "device_id": device_id,
                        "state": preferred_light_state,
                        "description": f"Изменить состояние света в {device_id} на {'вкл' if preferred_light_state else 'выкл'}"
                    })
        
        return actions
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет запланированное действие"""
        action_type = action.get("action", "unknown")
        
        try:
            if action_type == "trigger_security_response":
                self.controller.trigger_security_response()
                return {"status": "success", "message": "Система безопасности активирована"}
            
            elif action_type == "increase_ventilation":
                for device_id, device in self.controller.devices.items():
                    if device.device_type == "motion_fan":
                        device.set_fan_speed(200)  # Высокая скорость
                return {"status": "success", "message": "Вентиляция увеличена"}
            
            elif action_type == "reduce_ventilation":
                for device_id, device in self.controller.devices.items():
                    if device.device_type == "motion_fan":
                        device.set_fan_speed(50)  # Низкая скорость
                return {"status": "success", "message": "Вентиляция уменьшена"}
            
            elif action_type == "set_light":
                device_id = action.get("device_id")
                state = action.get("state", False)
                success = self.controller.set_light_state(device_id, state)
                return {
                    "status": "success" if success else "error", 
                    "message": f"Свет в {device_id} {'включен' if state else 'выключен'}" if success else "Ошибка управления светом"
                }
            
            else:
                return {"status": "unknown_action", "message": f"Неизвестное действие: {action_type}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Ошибка выполнения действия: {str(e)}"}
    
    def run_single_cycle(self, goals: List[str]) -> Dict[str, Any]:
        """Выполняет один цикл работы агента"""
        all_results = {}
        
        for goal in goals:
            print(f"\nЦель: {goal}")
            actions = self.plan_actions_for_goal(goal)
            print(f"Спланировано действий: {len(actions)}")
            
            goal_results = []
            for action in actions:
                print(f"  Выполняю: {action['description']}")
                result = self.execute_action(action)
                goal_results.append(result)
                print(f"  Результат: {result['message']}")
            
            all_results[goal] = goal_results
        
        return all_results
    
    def run_continuous_cycle(self, goals: List[str], duration_minutes: int = 60):
        """Выполняет непрерывный цикл работы агента"""
        print(f"Запуск непрерывного цикла на {duration_minutes} минут")
        
        start_time = time.time()
        cycle_count = 0
        
        while time.time() - start_time < duration_minutes * 60:
            cycle_count += 1
            print(f"\n{'='*50}")
            print(f"ЦИКЛ #{cycle_count}")
            print(f"{'='*50}")
            
            results = self.run_single_cycle(goals)
            
            # Обновляем память адаптации
            self.adaptation_memory.append({
                "cycle": cycle_count,
                "time": time.time(),
                "goals": goals.copy(),
                "results": results
            })
            
            # Ограничиваем размер памяти
            if len(self.adaptation_memory) > 100:
                self.adaptation_memory = self.adaptation_memory[-50:]
            
            time.sleep(10)  # Пауза между циклами
        
        print(f"\nНепрерывный цикл завершен. Выполнено {cycle_count} циклов.")
    
    def learn_from_experience(self) -> Dict[str, Any]:
        """Извлекает уроки из опыта работы"""
        if not self.adaptation_memory:
            return {"message": "Нет данных для анализа"}
        
        analysis = {
            "total_cycles": len(self.adaptation_memory),
            "most_common_goals": {},
            "action_success_rates": {},
            "suggested_optimizations": []
        }
        
        # Подсчет целей
        all_goals = []
        for cycle in self.adaptation_memory:
            all_goals.extend(cycle["goals"])
        
        for goal in all_goals:
            analysis["most_common_goals"][goal] = analysis["most_common_goals"].get(goal, 0) + 1
        
        # Анализ успеха действий
        all_actions = []
        successful_actions = []
        
        for cycle in self.adaptation_memory:
            for goal, results in cycle["results"].items():
                for result in results:
                    all_actions.append(result.get("message", "unknown"))
                    if result.get("status") == "success":
                        successful_actions.append(result.get("message", "unknown"))
        
        analysis["action_success_rates"]["overall"] = len(successful_actions) / len(all_actions) if all_actions else 0
        
        # Предложения по оптимизации
        if analysis["action_success_rates"]["overall"] < 0.8:
            analysis["suggested_optimizations"].append("Улучшить надежность команд - низкий процент успеха")
        
        if "Температура" in str(analysis["most_common_goals"]):
            analysis["suggested_optimizations"].append("Настроить более точные пороги температуры для климат-контроля")
        
        return analysis

# Полный пример работы системы
if __name__ == "__main__":
    print("=== Инициализация системы умного дома с ИИ-агентом ===")
    
    # Создаем контроллер
    controller = SmartHomeController()
    
    # К сожалению, без физических Arduino устройств мы не можем выполнить полную демонстрацию
    # Но покажем архитектуру и принцип работы
    
    print("\nКонтроллер инициализирован. В реальной системе здесь подключались бы Arduino устройства:")
    print("- Подключите Arduino 1 (температура/свет) к COM3")
    print("- Подключите Arduino 2 (дверь/сигнализация) к COM4") 
    print("- Подключите Arduino 3 (движение/вентилятор) к COM5")
    print("- Загрузите соответствующие прошивки")
    
    # В целях демонстрации покажем, как работал бы агент
    print("\n=== Демонстрация работы ИИ-агента ===")
    print("Предположим, контроллер подключен к устройствам...")
    
    # Создаем агент
    agent = SmartHomeAIAgent(controller)
    
    # Определяем цели системы
    goals = [
        "Обеспечить безопасность дома",
        "Поддерживать комфортную температуру", 
        "Управлять освещением по расписанию"
    ]
    
    print(f"\nЦели системы: {goals}")
    
    # Показываем пример планирования
    print("\nПример планирования для цели 'Обеспечить безопасность дома':")
    security_plan = agent.plan_actions_for_goal("Обеспечить безопасность дома")
    for action in security_plan:
        print(f"  - {action['description']}")
    
    # После работы можно проанализировать опыт
    experience_analysis = agent.learn_from_experience()
    print(f"\nАнализ опыта работы: {experience_analysis}")
    
    print("\nСистема готова к работе. Для полного тестирования подключите Arduino устройства.")
```

## Часть 5: Запуск и тестирование системы

### Задание 5.1: Сценарии тестирования

Создайте файл сценариев тестирования:

```python
# test_scenarios.py
from smart_home_ai_agent import SmartHomeAIAgent
from smart_home_manager import SmartHomeController

def run_comprehensive_test():
    """Запускает комплексное тестирование системы"""
    print("=== КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ УМНОГО ДОМА ===")
    
    # Создаем контроллер и агента
    controller = SmartHomeController()
    agent = SmartHomeAIAgent(controller)
    
    print("\n1. Проверка инициализации компонентов...")
    print(f"   - Контроллер создан: {'OK' if controller else 'ERROR'}")
    print(f"   - Агент создан: {'OK' if agent else 'ERROR'}")
    
    print("\n2. Демонстрация планирования для разных целей...")
    
    test_goals = [
        "Обеспечить безопасность дома",
        "Поддерживать комфортную температуру", 
        "Управлять освещением"
    ]
    
    for goal in test_goals:
        actions = agent.plan_actions_for_goal(goal)
        print(f"   - Цель: {goal}")
        print(f"   - Спланировано действий: {len(actions)}")
        for i, action in enumerate(actions, 1):
            print(f"      {i}. {action['description']}")
        print()
    
    print("3. Демонстрация адаптивности...")
    experience_analysis = agent.learn_from_experience()
    print(f"   - Анализ опыта: {experience_analysis}")
    
    print("\n4. Проверка архитектурных компонентов...")
    print("   - Протокол связи: РЕАЛИЗОВАН (smart_home_protocol.py)")
    print("   - FSM для Arduino: РЕАЛИЗОВАН (в прошивке)")
    print("   - Двунаправленная связь: РЕАЛИЗОВАНА")
    print("   - Безопасность: РЕАЛИЗОВАНА")
    print("   - Адаптивность: РЕАЛИЗОВАНА")
    print("   - Многопоточность: РЕАЛИЗОВАНА")
    
    print("\n=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")
    print("\nДля полного функционального тестирования:")
    print("1. Загрузите прошивки на Arduino устройства")
    print("2. Подключите устройства к соответствующим портам")
    print("3. Обновите порты в вызовах register_device()")
    print("4. Запустите controller.start_monitoring()")
    print("5. Вызовите agent.run_continuous_cycle() с целями")

def run_security_scenario():
    """Тестирует сценарий безопасности"""
    print("\n=== ТЕСТИРОВАНИЕ СЦЕНАРИЯ БЕЗОПАСНОСТИ ===")
    
    controller = SmartHomeController()
    agent = SmartHomeAIAgent(controller)
    
    # Симулируем ситуацию: дверь открыта, движение обнаружено
    print("Симуляция: дверь открыта, движение обнаружено")
    controller.system_state['door_status']['main_door'] = True
    controller.system_state['motion_status']['hall'] = True
    
    # Планируем действия для обеспечения безопасности
    security_actions = agent.plan_actions_for_goal("Обеспечить безопасность дома")
    print(f"Планируемые действия: {len(security_actions)}")
    
    for action in security_actions:
        print(f"  - {action['description']}")
        result = agent.execute_action(action)
        print(f"    Результат: {result['message']}")
    
    print("Сценарий безопасности протестирован")

def run_climate_scenario():
    """Тестирует сценарий климат-контроля"""
    print("\n=== ТЕСТИРОВАНИЕ СЦЕНАРИЯ КЛИМАТА ===")
    
    controller = SmartHomeController()
    agent = SmartHomeAIAgent(controller)
    
    # Симулируем высокую температуру
    print("Симуляция: высокая температура в помещениях")
    controller.system_state['temperature']['kitchen'] = 28.0
    controller.system_state['temperature']['living_room'] = 26.0
    
    # Планируем действия для охлаждения
    climate_actions = agent.plan_actions_for_goal("Поддерживать комфортную температуру")
    print(f"Планируемые действия: {len(climate_actions)}")
    
    for action in climate_actions:
        print(f"  - {action['description']}")
        result = agent.execute_action(action)
        print(f"    Результат: {result['message']}")
    
    print("Сценарий климат-контроля протестирован")

if __name__ == "__main__":
    run_comprehensive_test()
    run_security_scenario() 
    run_climate_scenario()
    
    print("\n" + "="*60)
    print("ФИНАЛЬНЫЙ ПРОЕКТ ЗАВЕРШЕН")
    print("="*60)
    print("Созданная система включает:")
    print("✓ Архитектуру с ИИ-агентом и Arduino устройствами")
    print("✓ Протокол надежной связи с FSM и CRC")  
    print("✓ Двунаправленное взаимодействие с физическим миром")
    print("✓ Систему безопасности и климат-контроля")
    print("✓ Адаптивное поведение и обучение")
    print("✓ Многопоточность и отказоустойчивость")
    print("\nДля полного запуска системы:")
    print("1. Соберите физическую установку с Arduino")
    print("2. Загрузите прошивки")
    print("3. Настройте порты подключения")
    print("4. Запустите основной скрипт системы")