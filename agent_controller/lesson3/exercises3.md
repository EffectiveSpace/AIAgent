# Упражнения к Lesson AC-3: Обработка ответов от Arduino в ИИ-агенте

## Упражнение AC-3.1: Анализ структуры ответов Arduino

### Цель
Понять структуру ответов от Arduino и как они кодируются.

### Задание
1. Изучите реализацию `ResponseType` и структуру ответных пакетов из урока.
2. Создайте функцию-декодер, которая принимает байтовый массив и определяет тип ответа.
3. Напишите тесты для всех типов ответов.

### Задача
```python
from response_handler import ResponseType

def analyze_response_packet(packet_bytes):
    """
    Анализирует байтовый пакет и возвращает информацию о типе ответа
    """
    # ВАШ КОД ЗДЕСЬ
    pass

# Тестовые пакеты
test_packets = [
    [0xF0, 0x01],  # ACK для команды 0x01
    [0xF1, 0x04, 0x00, 0x19],  # Данные сенсора (температура 25)
    [0xF2, 0x01],  # Статус устройства (LED включен)
    [0xFE, 0x02]   # Ошибка
]

for packet in test_packets:
    result = analyze_response_packet(packet)
    print(f"Пакет: {[hex(b) for b in packet]} -> Анализ: {result}")
```

### Контрольные вопросы
1. Какой байт определяет тип ответа?
2. Почему важно различать типы ответов?
3. Что произойдет, если Arduino пошлет неизвестный тип ответа?

## Упражнение AC-3.2: Расширение типов ответов

### Цель
Добавить новые типы ответов для расширенной функциональности.

### Задание
Добавьте следующие типы ответов в систему:
1. `RESPONSE_LOG_MESSAGE` (0xFD) - системные лог-сообщения
2. `RESPONSE_MULTIPLE_SENSORS` (0xF3) - данные с нескольких сенсоров
3. `RESPONSE_DEVICE_INFO` (0xF4) - информация об устройстве

### Шаги:
1. Добавьте новые типы в enum или класс
2. Реализуйте обработку новых типов в `ResponseHandler`
3. Обновите Arduino-прошивку для отправки новых типов ответов
4. Протестируйте все новые типы

### Пример расширения для Arduino
```cpp
// В enum CommandType добавьте:
CMD_GET_DEVICE_INFO = 0x09,
CMD_READ_MULTIPLE_SENSORS = 0x0A,

// В processCommand добавьте:
case CMD_GET_DEVICE_INFO:
  sendDeviceInfo();
  break;

case CMD_READ_MULTIPLE_SENSORS:
  sendMultipleSensorData();
  break;

void sendDeviceInfo() {
  uint8_t info[] = {RESPONSE_DEVICE_INFO, 'A', 'R', 'D', 'U', 'I', 'N', 'O', '_', 'U', 'N', 'O'};
  sendPacket(info, sizeof(info));
}

void sendMultipleSensorData() {
  int temp = analogRead(A0);
  int light = analogRead(A1);
  uint8_t data[] = {RESPONSE_MULTIPLE_SENSORS, 
                    (uint8_t)(temp >> 8), (uint8_t)(temp & 0xFF),
                    (uint8_t)(light >> 8), (uint8_t)(light & 0xFF)};
  sendPacket(data, sizeof(data));
}
```

### Тестирование новых ответов
Протестируйте все новые типы ответов и убедитесь, что они корректно обрабатываются в Python.

## Упражнение AC-3.3: Реализация FSM для обработки ответов в Arduino

### Цель
Реализовать FSM (конечный автомат) для надежной обработки ответов в Arduino.

### Задание
В прошлом уроке мы реализовали FSM для получения команд. Теперь реализуйте FSM для подготовки и отправки ответов.

### Структура FSM для ответов:
```
SEND_START → SEND_SYNC1 → SEND_SYNC2 → SEND_LEN → SEND_TYPE → SEND_DATA → SEND_CRC → SEND_COMPLETE
```

### Arduino реализация FSM для ответов:
```cpp
// Состояния FSM для отправки ответов
enum SendState {
  SEND_START,
  SEND_SYNC1,
  SEND_SYNC2,
  SEND_LEN,
  SEND_TYPE,
  SEND_DATA,
  SEND_CRC,
  SEND_COMPLETE
};

// Значения для отправки (буфер)
uint8_t send_buffer[256];
int send_buffer_len = 0;
int send_index = 0;
SendState send_state = SEND_COMPLETE;

void setupSendResponse(uint8_t* data, int len) {
  // Подготовить буфер с полным пакетом (включая SYNC, LEN, CRC)
  send_buffer[0] = SYNC1;
  send_buffer[1] = SYNC2;
  send_buffer[2] = len;
  
  for(int i = 0; i < len; i++) {
    send_buffer[3 + i] = data[i];
  }
  
  uint8_t crc = calculateCRC(&send_buffer[3], len);
  send_buffer[3 + len] = crc;
  
  send_buffer_len = 4 + len;
  send_index = 0;
  send_state = SEND_START;
}

void sendResponseFSM() {
  switch(send_state) {
    case SEND_START:
      send_index = 0;
      send_state = SEND_SYNC1;
      break;
      
    case SEND_SYNC1:
      if(Serial.availableForWrite() > 0) {
        Serial.write(send_buffer[send_index]);
        send_index++;
        send_state = SEND_SYNC2;
      }
      break;
      
    case SEND_SYNC2:
      if(Serial.availableForWrite() > 0) {
        Serial.write(send_buffer[send_index]);
        send_index++;
        send_state = SEND_LEN;
      }
      break;
      
    case SEND_LEN:
      if(Serial.availableForWrite() > 0) {
        Serial.write(send_buffer[send_index]);
        send_index++;
        send_state = SEND_TYPE;
      }
      break;
      
    case SEND_TYPE:
      if(Serial.availableForWrite() > 0) {
        Serial.write(send_buffer[send_index]);
        send_index++;
        if(send_index < send_buffer_len) {
          send_state = SEND_DATA;
        } else {
          send_state = SEND_COMPLETE;
        }
      }
      break;
      
    case SEND_DATA:
      if(Serial.availableForWrite() > 0) {
        Serial.write(send_buffer[send_index]);
        send_index++;
        if(send_index == send_buffer_len - 1) {
          send_state = SEND_CRC;
        }
      }
      break;
      
    case SEND_CRC:
      if(Serial.availableForWrite() > 0) {
        Serial.write(send_buffer[send_index]);
        send_index++;
        send_state = SEND_COMPLETE;
      }
      break;
      
    case SEND_COMPLETE:
      // Отправка завершена
      break;
  }
}

// Вызывайте sendResponseFSM() в основном цикле
void loop() {
  // Обработка входящих команд (ваш существующий FSM)
  handleIncomingCommands();
  
  // Отправка исходящих ответов (новый FSM)
  sendResponseFSM();
}
```

### Тестирование FSM
Протестируйте надежность отправки пакетов с использованием FSM, особенно при высокой нагрузке.

## Упражнение AC-3.4: Интеграция ответов в цикл ReAct ИИ-агента

### Цель
Обеспечить, чтобы ответы от Arduino влияли на принятие решений ИИ-агентом.

### Задание
Создайте сценарий, в котором ИИ-агент принимает решения на основе полученных ответов:

1. ИИ-агент запрашивает температуру
2. На основе результата включает или выключает светодиод
3. Проверяет результат своего действия
4. Делает вывод о выполнении задачи

### Реализация сценария
```python
class DecisionBasedAgent:
    def __init__(self, arduino_port: str = 'COM3'):
        self.arduino = EnhancedArduinoInterface(arduino_port)
        self.temperature_threshold = 25  # Порог температуры
    
    def temperature_control_scenario(self) -> str:
        """
        Сценарий управления температурой на основе данных сенсора
        """
        print("=== Сценарий управления температурой ===")
        
        # 1. Прочитать температуру
        temp_response = self.arduino.read_sensor("temperature")
        print(f"Получена температура: {temp_response}")
        
        # 2. Проанализировать результат и принять решение
        if temp_response.get('type') == 'SENSOR_DATA':
            current_temp = temp_response.get('value', 0)
            print(f"Текущая температура: {current_temp}")
            
            if current_temp > self.temperature_threshold:
                print("Температура выше порога, включаю индикацию (светодиод)")
                led_response = self.arduino.send_command_get_response(0x01)  # LED_ON
                print(f"Ответ на включение LED: {led_response}")
                return f"Температура {current_temp}°C выше порога {self.temperature_threshold}°C, включил индикацию"
            else:
                print("Температура в норме")
                return f"Температура {current_temp}°C в норме, действия не требуются"
        else:
            return f"Не удалось получить данные о температуре: {temp_response}"
    
    def security_monitoring_scenario(self) -> str:
        """
        Сценарий мониторинга безопасности
        """
        print("\n=== Сценарий мониторинга безопасности ===")
        
        # 1. Получить статус всех датчиков
        door_sensor_response = self.arduino.read_sensor("door")  # Условный датчик двери
        motion_sensor_response = self.arduino.read_sensor("motion")  # Условный датчик движения
        
        print(f"Статус двери: {door_sensor_response}")
        print(f"Статус движения: {motion_sensor_response}")
        
        # 2. Проанализировать статусы и принять решение
        door_open = door_sensor_response.get('value', 0) == 1 if door_sensor_response.get('type') == 'SENSOR_DATA' else False
        motion_detected = motion_sensor_response.get('value', 0) == 1 if motion_sensor_response.get('type') == 'SENSOR_DATA' else False
        
        if door_open and motion_detected:
            print("Обнаружена потенциальная угроза: дверь открыта, движение обнаружено")
            alarm_response = self.arduino.send_command_get_response(0x01)  # Включить сигнализацию (LED)
            print(f"Активирована сигнализация: {alarm_response}")
            return "Обнаружена потенциальная угроза: сигнализация активирована"
        elif door_open:
            print("Дверь открыта, но движение не обнаружено")
            return "Дверь открыта, но угрозы не обнаружено"
        else:
            print("Все спокойно")
            return "Безопасность в норме"

# Тестирование сценариев
if __name__ == "__main__":
    agent = DecisionBasedAgent()
    
    print("Тестируем сценарии принятия решений...")
    result1 = agent.temperature_control_scenario()
    print(f"Результат: {result1}")
    
    result2 = agent.security_monitoring_scenario()
    print(f"Результат: {result2}")
    
    agent.arduino.close()
```

### Анализ
1. Как ответы влияют на принятие решений?
2. Какие риски существуют в автоматическом принятии решений?
3. Как можно улучшить надежность принимаемых решений?

## Упражнение AC-3.5: Обработка ошибок и восстановление в ответах

### Цель
Обеспечить надежную обработку ошибок в ответах от Arduino.

### Задание
Реализуйте систему, которая:
1. Обнаруживает ошибки в ответах от Arduino
2. Принимает меры по восстановлению
3. Логирует ошибки для анализа

### Задача: Реализуйте обработчик с восстановлением
```python
class ErrorResilientAgent:
    def __init__(self, arduino_port: str = 'COM3'):
        self.arduino = EnhancedArduinoInterface(arduino_port)
        self.error_count = 0
        self.last_error_time = 0
        self.max_errors_before_reset = 5
        self.reset_cooldown = 10.0  # секунд
        
        # История команд для повтора в случае ошибки
        self.command_history = []
    
    def send_command_with_error_handling(self, command: int, params: list = None, 
                                       max_retries: int = 3) -> dict:
        """
        Отправляет команду с обработкой ошибок и повторными попытками
        """
        last_error = None
        final_response = None
        
        for attempt in range(max_retries):
            try:
                print(f"Попытка {attempt + 1} отправки команды {hex(command)}")
                response = self.arduino.send_command_get_response(command, params)
                
                if response.get('type') == 'ERROR' or response.get('type') == 'TIMEOUT':
                    print(f"Ошибка в попытке {attempt + 1}: {response}")
                    last_error = response
                    if attempt < max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))  # Увеличиваем задержку
                        continue
                else:
                    final_response = response
                    break
            except Exception as e:
                print(f"Исключение в попытке {attempt + 1}: {e}")
                last_error = {"type": "EXCEPTION", "message": str(e)}
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    return last_error
        
        if final_response:
            # Проверяем, не нужно ли выполнить восстановительные действия
            self.check_and_handle_errors(final_response, command)
            return final_response
        else:
            # Все попытки не удались
            self.record_error(command, last_error)
            return last_error
    
    def check_and_handle_errors(self, response: dict, command_sent: int):
        """
        Проверяет полученный ответ на наличие признаков ошибки и выполняет действия
        """
        if response.get('type') == 'ERROR':
            error_code = response.get('error_code')
            if error_code:
                self.error_count += 1
                self.last_error_time = time.time()
                
                # При определенных ошибках может потребоваться перезагрузка Arduino
                if error_code == 0x03:  # Устройство занято
                    print("Устройство занято, жду и повторяю команду")
                    time.sleep(1.0)
                elif error_code == 0x04:  # Ошибка сенсора
                    print("Ошибка сенсора, возможно, требуется калибровка")
        
        # Если количество ошибок превысило порог, выполнить восстановление
        if self.error_count >= self.max_errors_before_reset:
            time_since_last_error = time.time() - self.last_error_time
            if time_since_last_error < self.reset_cooldown:
                self.perform_device_reset()
    
    def perform_device_reset(self):
        """
        Выполняет восстановительные действия для Arduino
        """
        print("Превышено количество ошибок, выполняю восстановление...")
        # Здесь может быть:
        # - Повторное подключение к Arduino
        # - Отправка команды перезапуска (если поддерживается)
        # - Уведомление пользователя
        self.error_count = 0
        print("Восстановление завершено")
    
    def record_error(self, command: int, error_response: dict):
        """
        Записывает информацию об ошибке для анализа
        """
        error_record = {
            'timestamp': time.time(),
            'command': hex(command),
            'error': error_response,
            'attempt_number': len(self.command_history)
        }
        print(f"Записана ошибка: {error_record}")

# Тестирование обработки ошибок
if __name__ == "__main__":
    agent = ErrorResilientAgent()
    
    # Тестируем с нормальной командой
    response1 = agent.send_command_with_error_handling(0x05)  # GET_STATUS
    print(f"Ответ на статус: {response1}")
    
    # Тестируем с возможной ошибкой (неправильная команда)
    response2 = agent.send_command_with_error_handling(0xFF)  # Неизвестная команда
    print(f"Ответ на ошибочную команду: {response2}")
    
    agent.arduino.close()
```

### Анализ стратегии восстановления
1. Почему важно ограничивать количество попыток?
2. Какие стратегии восстановления вы бы использовали?
3. Как предотвратить бесконечные циклы ошибок?

## Упражнение AC-3.6: Контекстная обработка ответов

### Цель
Реализовать систему, которая интерпретирует ответы в контексте текущей задачи.

### Задание
Создайте систему, которая:
1. Хранит контекст текущей задачи
2. Интерпретирует ответы в соответствии с контекстом
3. Выполняет автоматические действия на основе интерпретации

### Пример реализации
```python
class ContextAwareResponseProcessor:
    def __init__(self):
        self.current_task = None
        self.task_context = {}
        self.response_interpretations = {}
    
    def set_current_task(self, task_name: str, context: dict = None):
        """
        Устанавливает текущую задачу и её контекст
        """
        self.current_task = task_name
        self.task_context = context or {}
        print(f"Установлена задача: {task_name}, контекст: {context}")
    
    def interpret_response(self, response: dict) -> dict:
        """
        Интерпретирует ответ в контексте текущей задачи
        """
        interpretation = {
            'original_response': response,
            'context': self.current_task,
            'meaning': None,
            'recommended_action': None
        }
        
        if self.current_task == "TEMPERATURE_MONITORING":
            if response.get('type') == 'SENSOR_DATA':
                temp = response.get('value', 0)
                threshold = self.task_context.get('threshold', 25)
                
                if temp > threshold:
                    interpretation['meaning'] = f"Температура ({temp}) превышает порог ({threshold})"
                    interpretation['recommended_action'] = "activate_cooling"
                else:
                    interpretation['meaning'] = f"Температура ({temp}) в норме"
                    interpretation['recommended_action'] = "no_action_needed"
        
        elif self.current_task == "SECURITY_SURVEILLANCE":
            if response.get('type') == 'SENSOR_DATA':
                sensor_value = response.get('value', 0)
                sensor_type = self.task_context.get('sensor_type', 'unknown')
                
                if sensor_type == 'motion' and sensor_value == 1:
                    interpretation['meaning'] = "Обнаружено движение"
                    interpretation['recommended_action'] = "alert_user"
                elif sensor_type == 'door' and sensor_value == 1:
                    interpretation['meaning'] = "Дверь открыта"
                    interpretation['recommended_action'] = "check_security_status"
        
        return interpretation
    
    def get_context_summary(self) -> dict:
        """
        Возвращает сводку по текущему контексту
        """
        return {
            'current_task': self.current_task,
            'task_context': self.task_context,
            'response_interpretations_count': len(self.response_interpretations)
        }

# Интеграция с агентом
class ContextualAgent:
    def __init__(self):
        self.response_processor = ContextAwareResponseProcessor()
        self.arduino = EnhancedArduinoInterface('COM3')  # Замените на ваш порт
    
    def run_contextual_task(self, task_name: str, context: dict, 
                          sensor_type: str) -> str:
        """
        Выполняет задачу с контекстной обработкой ответов
        """
        self.response_processor.set_current_task(task_name, context)
        
        # Выполнить измерение
        if sensor_type == "temperature":
            response = self.arduino.read_sensor("temperature")
        else:
            response = self.arduino.read_sensor(sensor_type)
        
        # Интерпретировать ответ в контексте
        interpretation = self.response_processor.interpret_response(response)
        
        print(f"Ответ: {response}")
        print(f"Интерпретация: {interpretation}")
        
        # Выполнить рекомендованное действие
        action = interpretation.get('recommended_action')
        if action == "activate_cooling":
            led_response = self.arduino.send_command_get_response(0x01)  # Включить LED (индикация)
            return f"Температура высокая, активирована индикация: {led_response}"
        elif action == "alert_user":
            return "Обнаружено движение, рекомендуется проверить"
        else:
            return f"Данные получены: {response.get('value', 'неизвестно')}"
    
    def close(self):
        self.arduino.close()

# Тестирование
if __name__ == "__main__":
    agent = ContextualAgent()
    
    # Задача мониторинга температуры
    result1 = agent.run_contextual_task(
        "TEMPERATURE_MONITORING",
        {"threshold": 25, "unit": "celsius"},
        "temperature"
    )
    print(f"Результат мониторинга: {result1}")
    
    # Задача наблюдения за движением
    result2 = agent.run_contextual_task(
        "SECURITY_SURVEILLANCE", 
        {"sensor_type": "motion", "location": "front_door"},
        "motion"  # Условный тип сенсора
    )
    print(f"Результат наблюдения: {result2}")
    
    agent.close()
```

### Обсуждение
1. Как контекст влияет на интерпретацию ответов?
2. В каких задачах особенно важна контекстная интерпретация?
3. Какие риски связаны с автоматической интерпретацией?

## Упражнение AC-3.7: Практическая отладка протокола ответов

### Цель
Научиться отлаживать проблемы в передаче и обработке ответов.

### Задание
Создайте систему логирования и диагностики для выявления проблем в коммуникации:

1. Логирование всех отправленных команд
2. Логирование всех полученных ответов
3. Сравнение ожидаемого и фактического поведения
4. Обнаружение таймаутов и ошибок синхронизации

### Задача: Система диагностики
```python
import logging
from datetime import datetime

class ProtocolDiagnostic:
    def __init__(self):
        self.command_log = []
        self.response_log = []
        self.error_log = []
        
        # Настроим логирование
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ProtocolDiagnostic")
    
    def log_command(self, command: int, params: list, timestamp: float = None):
        """Логирует отправленную команду"""
        timestamp = timestamp or time.time()
        log_entry = {
            'timestamp': timestamp,
            'type': 'command',
            'command': hex(command),
            'params': params,
            'time_str': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
        }
        self.command_log.append(log_entry)
        self.logger.info(f"CMD: {log_entry}")
    
    def log_response(self, response: dict, timestamp: float = None):
        """Логирует полученный ответ"""
        timestamp = timestamp or time.time()
        log_entry = {
            'timestamp': timestamp,
            'type': 'response',
            'response': response,
            'time_str': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
        }
        self.response_log.append(log_entry)
        self.logger.info(f"RESP: {log_entry}")
    
    def log_error(self, error: dict, context: str = ""):
        """Логирует ошибку"""
        log_entry = {
            'timestamp': time.time(),
            'type': 'error',
            'error': error,
            'context': context,
            'time_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        }
        self.error_log.append(log_entry)
        self.logger.error(f"ERR: {log_entry}")
    
    def analyze_communication(self) -> dict:
        """Анализирует коммуникацию и выявляет проблемы"""
        analysis = {
            'total_commands': len(self.command_log),
            'total_responses': len(self.response_log),
            'total_errors': len(self.error_log),
            'command_response_match': 0,
            'timeout_issues': 0,
            'crc_errors': 0
        }
        
        # Подсчет соответствий команд и ответов
        for cmd in self.command_log:
            for resp in self.response_log:
                # Это упрощённый анализ - в реальности нужно учитывать ID команд и т.п.
                if abs(resp['timestamp'] - cmd['timestamp']) < 2.0:  # 2 секунды
                    analysis['command_response_match'] += 1
                    break
        
        # Подсчет таймаутов
        for error in self.error_log:
            if 'TIMEOUT' in str(error.get('error', {})):
                analysis['timeout_issues'] += 1
            if 'CRC' in str(error.get('error', {})):
                analysis['crc_errors'] += 1
        
        return analysis
    
    def generate_report(self) -> str:
        """Генерирует отчет о диагностике"""
        analysis = self.analyze_communication()
        
        report = f"""
Диагностика протокола:
=======================
Всего команд: {analysis['total_commands']}
Всего ответов: {analysis['total_responses']}
Всего ошибок: {analysis['total_errors']}
Соответствий команда-ответ: {analysis['command_response_match']}
Проблемы с таймаутами: {analysis['timeout_issues']}
Проблемы с CRC: {analysis['crc_errors']}

Последние 3 команды:
{self.command_log[-3:] if self.command_log else 'Нет команд'}

Последние 3 ответа:
{self.response_log[-3:] if self.response_log else 'Нет ответов'}
        """
        
        return report

# Использование в агенте
class DiagnosticAgent:
    def __init__(self, arduino_port: str = 'COM3'):
        self.arduino = EnhancedArduinoInterface(arduino_port)
        self.diagnostic = ProtocolDiagnostic()
    
    def send_command_with_diagnostics(self, command: int, params: list = None):
        """Отправляет команду с полной диагностикой"""
        # Логируем команду
        self.diagnostic.log_command(command, params)
        
        try:
            # Отправляем команду
            response = self.arduino.send_command_get_response(command, params)
            
            # Логируем ответ
            self.diagnostic.log_response(response)
            
            return response
        except Exception as e:
            error_info = {"type": "EXCEPTION", "message": str(e)}
            self.diagnostic.log_error(error_info, f"Command {hex(command)}")
            return error_info
    
    def get_diagnostics_report(self):
        """Получает отчет о диагностике"""
        return self.diagnostic.generate_report()

# Тестирование диагностики
if __name__ == "__main__":
    diagnostic_agent = DiagnosticAgent()
    
    # Выполняем несколько команд для создания логов
    commands_to_test = [
        (0x05, [], "GET_STATUS"),
        (0x04, [1], "READ_SENSOR_TEMP"),
        (0x01, [], "LED_ON"),
        (0x02, [], "LED_OFF")
    ]
    
    for cmd, params, name in commands_to_test:
        print(f"\nТестирование: {name}")
        result = diagnostic_agent.send_command_with_diagnostics(cmd, params)
        print(f"Результат: {result}")
    
    # Генерируем отчет
    print("\n" + "="*50)
    print("ОТЧЕТ О ДИАГНОСТИКЕ")
    print("="*50)
    report = diagnostic_agent.get_diagnostics_report()
    print(report)
    
    diagnostic_agent.arduino.close()
```

### Анализ проблем
1. Какие типы проблем легче всего диагностировать?
2. Какие метрики были бы полезны для мониторинга?
3. Как автоматизировать обнаружение и устранение проблем?