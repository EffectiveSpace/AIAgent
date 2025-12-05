# Lesson AC-4: Продвинутые взаимодействия ИИ-агента и микроконтроллера

## Цели урока

После изучения этого урока вы сможете:
- Реализовать мультиагентные взаимодействия с несколькими Arduino
- Создать систему распределенного управления и мониторинга
- Реализовать безопасные и отказоустойчивые протоколы взаимодействия
- Использовать продвинутые паттерны ReAct с физическими устройствами
- Создать системы обратной связи и адаптивного поведения

## 1. Введение: Масштабирование взаимодействия

До этого момента мы работали с одиночным ИИ-агентом, управляющим одним Arduino. Однако в реальных приложениях часто требуется:

- **Управление несколькими устройствами** одновременно
- **Координация действий** между разными физическими системами
- **Распределенный мониторинг** нескольких участков/сенсоров
- **Адаптивное поведение** на основе данных от множества источников

Примеры таких систем:
- Умный дом с несколькими комнатами
- Система безопасности с множеством сенсоров
- Индустриальный IoT с распределенными датчиками и исполнительными устройствами

## 2. Архитектура мультиустройств: Управление несколькими Arduino

Для масштабирования системы до управления несколькими Arduino, мы создадим архитектуру с централизованным ИИ-агентом:

```
Центральный ИИ-агент
      ↓
[Устройство 1: Arduino Port COM3]
[Устройство 2: Arduino Port COM4] 
[Устройство 3: Arduino Port COM5]
      ↓
Физические устройства и сенсоры
```

### Реализация MultipleArduinoManager
```python
# multi_arduino_manager.py
import threading
import time
from typing import Dict, List, Any, Optional
from enhanced_arduino_interface import EnhancedArduinoInterface

class ArduinoDevice:
    """Инкапсулирует одно Arduino устройство"""
    def __init__(self, device_id: str, port: str, baudrate: int = 9600):
        self.device_id = device_id
        self.port = port
        self.baudrate = baudrate
        self.interface = EnhancedArduinoInterface(port, baudrate)
        self.last_communication = time.time()
        self.status = "connected"
        self.device_type = "unknown"
        self.location = "unknown"
    
    def send_command(self, command: int, params: Optional[list] = None, timeout: float = 2.0):
        """Отправляет команду на устройство"""
        self.last_communication = time.time()
        try:
            response = self.interface.send_command_get_response(command, params, timeout)
            return response
        except Exception as e:
            self.status = "error"
            return {"type": "ERROR", "message": f"Ошибка связи: {str(e)}"}
    
    def get_status(self):
        """Возвращает статус устройства"""
        return {
            "device_id": self.device_id,
            "port": self.port,
            "status": self.status,
            "last_communication": self.last_communication,
            "type": self.device_type,
            "location": self.location
        }

class MultipleArduinoManager:
    """Управляет несколькими Arduino устройствами"""
    
    def __init__(self):
        self.devices: Dict[str, ArduinoDevice] = {}
        self.device_configs = {}  # Конфигурации устройств
        self.lock = threading.Lock()  # Блокировка для потокобезопасности
    
    def register_device(self, device_id: str, port: str, device_type: str = "generic", 
                       location: str = "unknown", baudrate: int = 9600):
        """Регистрирует новое устройство"""
        with self.lock:
            if device_id in self.devices:
                raise ValueError(f"Устройство с ID {device_id} уже зарегистрировано")
            
            device = ArduinoDevice(device_id, port, baudrate)
            device.device_type = device_type
            device.location = location
            
            self.devices[device_id] = device
            self.device_configs[device_id] = {
                "type": device_type,
                "location": location,
                "port": port
            }
            
            print(f"Зарегистрировано устройство: {device_id} на порту {port}")
    
    def send_command_to_device(self, device_id: str, command: int, 
                              params: Optional[list] = None, timeout: float = 2.0):
        """Отправляет команду конкретному устройству"""
        with self.lock:
            if device_id not in self.devices:
                return {"type": "ERROR", "message": f"Устройство {device_id} не найдено"}
            
            device = self.devices[device_id]
            return device.send_command(command, params, timeout)
    
    def send_command_to_all(self, command: int, params: Optional[list] = None):
        """Отправляет команду всем устройствам"""
        results = {}
        with self.lock:
            for device_id, device in self.devices.items():
                try:
                    result = device.send_command(command, params)
                    results[device_id] = result
                except Exception as e:
                    results[device_id] = {"type": "ERROR", "message": str(e)}
        return results
    
    def broadcast_read_sensor(self, sensor_type: str = "temperature"):
        """Считывает сенсор со всех устройств"""
        results = {}
        command_map = {
            "temperature": 0x04,
            "status": 0x05
        }
        
        command = command_map.get(sensor_type, 0x04)  # по умолчанию температура
        
        with self.lock:
            for device_id, device in self.devices.items():
                try:
                    result = device.send_command(command)
                    results[device_id] = result
                except Exception as e:
                    results[device_id] = {"type": "ERROR", "message": str(e)}
        
        return results
    
    def get_all_statuses(self):
        """Получает статусы всех устройств"""
        statuses = {}
        with self.lock:
            for device_id, device in self.devices.items():
                statuses[device_id] = device.get_status()
        return statuses
    
    def close_all_connections(self):
        """Закрывает соединения со всеми устройствами"""
        with self.lock:
            for device in self.devices.values():
                try:
                    device.interface.close()
                except:
                    pass

# Пример использования
if __name__ == "__main__":
    manager = MultipleArduinoManager()
    
    # Регистрируем несколько устройств (используя разные порты)
    # Примечание: на практике у вас может быть только одно Arduino подключено
    try:
        manager.register_device("arduino_1", "COM3", "temperature_monitor", "kitchen")
        manager.register_device("arduino_2", "COM4", "light_control", "living_room")
        manager.register_device("arduino_3", "COM5", "security_sensor", "front_door")
    except Exception as e:
        print(f"Ошибка при регистрации устройств (это нормально, если у вас нет нескольких Arduino): {e}")
    
    # Показать статусы
    statuses = manager.get_all_statuses()
    print("Статусы устройств:", statuses)
    
    manager.close_all_connections()
```

## 3. Координация между устройствами: Распределенные сценарии

Теперь мы реализуем сценарии, в которых ИИ-агент координирует действия между несколькими устройствами:

```python
# distributed_scenarios.py
import time
from typing import Dict, List, Any
from multi_arduino_manager import MultipleArduinoManager

class DistributedAgent:
    """ИИ-агент, управляющий распределенной системой устройств"""
    
    def __init__(self):
        self.manager = MultipleArduinoManager()
        self.known_devices = {}  # Инвентаризация устройств
        self.system_goals = {}   # Цели системы
        self.synchronization_points = {}  # Точки синхронизации
    
    def setup_home_automation_system(self):
        """Настройка системы умного дома"""
        # Регистрируем устройства различных типов
        device_configs = [
            ("kitchen_temp", "COM3", "temperature", "kitchen"),
            ("living_room_light", "COM4", "light_control", "living_room"),
            ("front_door_sensor", "COM5", "door_sensor", "front_door")
        ]
        
        for device_id, port, device_type, location in device_configs:
            try:
                self.manager.register_device(device_id, port, device_type, location)
                self.known_devices[device_id] = {
                    "type": device_type,
                    "location": location,
                    "last_value": None
                }
            except Exception as e:
                print(f"Не удалось подключиться к {device_id} на {port}: {e}")
    
    def synchronize_device_readings(self, device_ids: List[str], 
                                  command: int = 0x04, timeout: float = 2.0) -> Dict[str, Any]:
        """
        Синхронно читает данные с нескольких устройств
        """
        results = {}
        
        # Отправляем команды одновременно
        threads = []
        thread_results = {}
        
        def read_from_device(device_id):
            result = self.manager.send_command_to_device(device_id, command)
            thread_results[device_id] = result
        
        # Запускаем все чтения параллельно
        for device_id in device_ids:
            thread = threading.Thread(target=read_from_device, args=(device_id,))
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех операций
        for thread in threads:
            thread.join(timeout)
        
        return thread_results
    
    def home_security_scenario(self) -> str:
        """
        Сценарий системы безопасности: если дверь открыта И есть движение,
        включить свет и отправить уведомление
        """
        print("=== Сценарий безопасности дома ===")
        
        # Синхронное чтение состояний критических сенсоров
        security_devices = [did for did, info in self.known_devices.items() 
                           if "door" in info["type"] or "motion" in info["type"]]
        
        if not security_devices:
            return "Нет устройств безопасности для мониторинга"
        
        sensor_readings = self.synchronize_device_readings(security_devices)
        
        print(f"Чтения сенсоров безопасности: {sensor_readings}")
        
        # Анализ состояний
        door_open = False
        motion_detected = False
        
        for device_id, reading in sensor_readings.items():
            if reading.get('type') == 'SENSOR_DATA':
                value = reading.get('value', 0)
                device_type = self.known_devices[device_id]['type']
                
                if "door" in device_type and value == 1:
                    door_open = True
                elif "motion" in device_type and value == 1:
                    motion_detected = True
        
        # Принятие решения на основе комплексного анализа
        if door_open and motion_detected:
            print("Обнаружена потенциальная угроза: дверь открыта и обнаружено движение")
            
            # Найти устройства освещения и включить их
            light_devices = [did for did, info in self.known_devices.items() 
                            if "light" in info["type"]]
            
            for light_device in light_devices:
                response = self.manager.send_command_to_device(light_device, 0x01)  # LED_ON
                print(f"Включено освещение на {light_device}: {response}")
            
            return "Угроза обнаружена, освещение активировано"
        elif door_open:
            print("Дверь открыта, но движение не обнаружено")
            return "Дверь открыта, но угрозы не обнаружено"
        else:
            return "Безопасность в норме"
    
    def temperature_coordination_scenario(self) -> str:
        """
        Сценарий координации температур: усреднение и согласование
        """
        print("\n=== Сценарий координации температур ===")
        
        # Получаем температуры со всех температурных сенсоров
        temp_devices = [did for did, info in self.known_devices.items() 
                       if "temperature" in info["type"]]
        
        if not temp_devices:
            return "Нет температурных сенсоров для мониторинга"
        
        temp_readings = self.synchronize_device_readings(temp_devices, command=0x04)
        
        print(f"Температурные показания: {temp_readings}")
        
        # Собираем только действительные показания
        valid_temps = []
        for device_id, reading in temp_readings.items():
            if reading.get('type') == 'SENSOR_DATA':
                temp = reading.get('value', 0)
                valid_temps.append(temp)
                self.known_devices[device_id]['last_value'] = temp
        
        if not valid_temps:
            return "Не удалось получить действительные температурные показания"
        
        # Вычисляем среднюю температуру
        avg_temp = sum(valid_temps) / len(valid_temps)
        print(f"Средняя температура: {avg_temp:.2f}°C")
        
        # Принимаем решения на основе средней температуры
        if avg_temp > 25:
            print("Средняя температура выше нормы, активирую охлаждение...")
            # Включаем охлаждение в нужных зонах
            response = self.manager.send_command_to_all(0x01)  # Предполагаем, что это включение вентиляции
            return f"Средняя температура {avg_temp:.2f}°C слишком высока, активировано охлаждение"
        elif avg_temp < 18:
            print("Средняя температура ниже нормы, активирую обогрев...")
            return f"Средняя температура {avg_temp:.2f}°C слишком низка, рекомендовано включить обогрев"
        else:
            return f"Средняя температура {avg_temp:.2f}°C в норме"
    
    def execute_distributed_task(self, task_name: str, **kwargs) -> str:
        """Выполняет распределенную задачу"""
        if task_name == "home_security":
            return self.home_security_scenario()
        elif task_name == "temperature_coordination":
            return self.temperature_coordination_scenario()
        else:
            return f"Неизвестная распределенная задача: {task_name}"

# Тестирование распределенных сценариев
if __name__ == "__main__":
    agent = DistributedAgent()
    
    # Настройка (с ожиданием возможных ошибок)
    agent.setup_home_automation_system()
    
    # Выполнение сценариев
    security_result = agent.execute_distributed_task("home_security")
    print(f"Результат безопасности: {security_result}")
    
    temp_result = agent.execute_distributed_task("temperature_coordination")
    print(f"Результат температурной координации: {temp_result}")
    
    agent.manager.close_all_connections()
```

## 4. Продвинутые паттерны ReAct с физическими устройствами

Реализуем расширенный паттерн ReAct (Reason-Act-Observe) с учетом физических устройств:

```python
# advanced_react_patterns.py
import time
import threading
from typing import Dict, Any, List, Callable
from distributed_scenarios import DistributedAgent

class AdvancedReActAgent(DistributedAgent):
    """
    ИИ-агент с расширенным паттерном ReAct для физических устройств
    """
    
    def __init__(self):
        super().__init__()
        self.thought_history = []  # История мыслей
        self.action_history = []   # История действий
        self.observation_history = []  # История наблюдений
        self.goals = []  # Текущие и прошлые цели
        self.belief_state = {}  # Внутреннее состояние убеждений о мире
    
    def advanced_react_cycle(self, goal: str) -> str:
        """
        Расширенный цикл ReAct: 
        Reason → Plan → Act → (Wait for Physical Response) → Observe → Update Beliefs → Reason Again
        """
        print(f"\n=== Запуск расширенного ReAct цикла для цели: {goal} ===")
        
        self.goals.append({
            "goal": goal,
            "start_time": time.time(),
            "status": "in_progress"
        })
        
        # Формируем план
        plan = self.develop_plan(goal)
        print(f"Разработанный план: {plan}")
        
        # Выполняем план пошагово
        for step_idx, step in enumerate(plan):
            print(f"\n--- Шаг {step_idx + 1}: {step['description']} ---")
            
            # Reason (рассуждение)
            reason = self.reason_about_step(step, goal)
            self.thought_history.append({
                "step": step_idx,
                "reason": reason,
                "timestamp": time.time()
            })
            print(f"Рассуждение: {reason}")
            
            # Act (действие)
            action_result = self.execute_step_action(step)
            self.action_history.append({
                "step": step_idx,
                "action": step,
                "result": action_result,
                "timestamp": time.time()
            })
            print(f"Результат действия: {action_result}")
            
            # Wait and Observe (ожидание физического отклика и наблюдение)
            observation = self.observe_physical_response(step, action_result)
            self.observation_history.append({
                "step": step_idx,
                "action_result": action_result,
                "observation": observation,
                "timestamp": time.time()
            })
            print(f"Наблюдение: {observation}")
            
            # Update beliefs (обновление убеждений о состоянии мира)
            self.update_beliefs_from_observation(observation, step)
            
            # Проверяем, достигнута ли цель
            if self.is_goal_achieved(goal):
                self.update_goal_status(goal, "completed_successfully")
                return f"Цель '{goal}' достигнута успешно после {step_idx + 1} шагов"
        
        self.update_goal_status(goal, "completed_with_steps")
        return f"Цель '{goal}' обработана, выполнено {len(plan)} шагов"
    
    def develop_plan(self, goal: str) -> List[Dict[str, Any]]:
        """
        Разрабатывает план действий на основе цели
        """
        if "безопасность" in goal.lower():
            return [
                {
                    "description": "Проверить статус дверного сенсора",
                    "action": "read_sensor",
                    "device_type": "door_sensor",
                    "command": 0x04
                },
                {
                    "description": "Проверить сенсор движения",
                    "action": "read_sensor", 
                    "device_type": "motion_sensor",
                    "command": 0x04
                },
                {
                    "description": "Активировать систему безопасности при необходимости",
                    "action": "conditional_action",
                    "condition": "door_open_and_motion",
                    "command": 0x01
                }
            ]
        elif "температура" in goal.lower():
            return [
                {
                    "description": "Прочитать температуру в нескольких зонах",
                    "action": "read_multiple_sensors",
                    "device_types": ["temperature"],
                    "command": 0x04
                },
                {
                    "description": "Анализ средней температуры",
                    "action": "analyze_data",
                    "data_type": "temperature"
                },
                {
                    "description": "Принять меры при необходимости",
                    "action": "conditional_action",
                    "condition": "temperature_threshold_breached",
                    "command": 0x01
                }
            ]
        else:
            # Общий план для других целей
            return [
                {
                    "description": "Оценить текущую ситуацию",
                    "action": "assess_environment",
                    "command": 0x05  # GET_STATUS
                }
            ]
    
    def reason_about_step(self, step: Dict[str, Any], goal: str) -> str:
        """
        Рассуждает о предстоящем шаге
        """
        return f"Для достижения цели '{goal}', я планирую выполнить: {step['description']}. " \
               f"Это поможет мне получить информацию о {self.describe_step_purpose(step)} " \
               f"и принять дальнейшие решения."
    
    def describe_step_purpose(self, step: Dict[str, Any]) -> str:
        """Описывает цель текущего шага"""
        if step['action'] == 'read_sensor':
            return f"состоянии {step.get('device_type', 'устройства')}"
        elif step['action'] == 'read_multiple_sensors':
            return f"температурах в разных зонах"
        else:
            return "текущем состоянии системы"
    
    def execute_step_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет действие шага
        """
        action_type = step['action']
        
        if action_type == 'read_sensor':
            # Найти подходящее устройство
            device_ids = [did for did, info in self.known_devices.items() 
                         if step.get('device_type', '') in info['type']]
            
            if device_ids:
                device_id = device_ids[0]  # Берем первое подходящее
                result = self.manager.send_command_to_device(
                    device_id, step['command']
                )
                return {
                    "status": "success", 
                    "action_type": action_type,
                    "device_id": device_id,
                    "result": result
                }
            else:
                return {"status": "error", "message": "Устройство не найдено"}
        
        elif action_type == 'read_multiple_sensors':
            device_ids = [did for did, info in self.known_devices.items() 
                         if any(dt in info['type'] for dt in step.get('device_types', []))]
            results = self.synchronize_device_readings(device_ids, step['command'])
            return {
                "status": "success",
                "action_type": action_type, 
                "device_ids": device_ids,
                "results": results
            }
        
        else:
            return {"status": "unknown_action", "action_type": action_type}
    
    def observe_physical_response(self, step: Dict[str, Any], action_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Наблюдает за физическим откликом на действие
        """
        # В реальных системах здесь может быть задержка для физических процессов
        time.sleep(0.5)  # Небольшая задержка для симуляции физического отклика
        
        # Обновляем наблюдение на основе результата действия
        observation = {
            "step": step,
            "action_result": action_result,
            "timestamp": time.time(),
            "physical_response_time": 0.5  # симулируем время отклика
        }
        
        # Если есть физический результат, добавляем его
        if action_result.get('status') == 'success':
            observation['physical_state_change'] = True
        else:
            observation['physical_state_change'] = False
            observation['error'] = action_result.get('message')
        
        return observation
    
    def update_beliefs_from_observation(self, observation: Dict[str, Any], step: Dict[str, Any]):
        """
        Обновляет внутреннее состояние убеждений агента на основе наблюдения
        """
        action_result = observation.get('action_result', {})
        
        if action_result.get('status') == 'success':
            if 'result' in action_result and 'device_id' in action_result:
                device_id = action_result['device_id']
                result_data = action_result['result']
                self.belief_state[device_id] = {
                    'last_reading': result_data,
                    'last_update': observation['timestamp'],
                    'status': result_data.get('type', 'unknown')
                }
            elif 'results' in action_result:
                for device_id, result in action_result['results'].items():
                    self.belief_state[device_id] = {
                        'last_reading': result,
                        'last_update': observation['timestamp'], 
                        'status': result.get('type', 'unknown')
                    }
    
    def is_goal_achieved(self, goal: str) -> bool:
        """
        Проверяет, достигнута ли цель
        """
        # Простая проверка - цель достигнута если есть положительное наблюдение
        recent_observations = [obs for obs in self.observation_history 
                              if time.time() - obs.get('timestamp', 0) < 10.0]  # последние 10 секунд
        
        # В реальной системе тут будет сложная логика проверки достижения цели
        return len(recent_observations) > 0
    
    def update_goal_status(self, goal: str, status: str):
        """Обновляет статус цели"""
        for g in self.goals:
            if g['goal'] == goal:
                g['status'] = status
                g['end_time'] = time.time()
                g['duration'] = g['end_time'] - g['start_time']
                break

# Тестирование продвинутого ReAct
if __name__ == "__main__":
    agent = AdvancedReActAgent()
    
    # Настройка системы (с ожиданием возможных ошибок подключения)
    agent.setup_home_automation_system()
    
    # Запуск расширенного ReAct цикла для разных целей
    goals_to_test = [
        "Проверить систему безопасности дома",
        "Проанализировать распределение температур в доме"
    ]
    
    for goal in goals_to_test:
        result = agent.advanced_react_cycle(goal)
        print(f"\nРезультат выполнения цели '{goal}': {result}")
    
    # Показать краткую статистику
    print(f"\nСтатистика агента:")
    print(f"- Выполнено целей: {len([g for g in agent.goals if 'completed' in g['status']])}")
    print(f"- Совершено действий: {len(agent.action_history)}")
    print(f"- Сделано наблюдений: {len(agent.observation_history)}")
    print(f"- Внутренних убеждений: {len(agent.belief_state)}")
    
    agent.manager.close_all_connections()
```

## 5. Безопасность и отказоустойчивость в протоколах

Реализуем безопасные и отказоустойчивые механизмы взаимодействия:

```python
# safety_and_reliability.py
import time
import threading
from typing import Dict, Any, List, Optional
from advanced_react_patterns import AdvancedReActAgent

class SafeAndReliableAgent(AdvancedReActAgent):
    """
    ИИ-агент с упором на безопасность и отказоустойчивость
    """
    
    def __init__(self):
        super().__init__()
        self.command_whitelist = set([0x01, 0x02, 0x03, 0x04, 0x05])  # Безопасные команды
        self.command_rate_limits = {}  # Ограничения частоты команд
        self.max_commands_per_minute = 60  # Максимум команд в минуту
        self.safety_zones = {}  # Зоны безопасности
        self.emergency_procedures = {}  # Аварийные процедуры
        self.monitoring_threads = []  # Потоки мониторинга
    
    def safe_send_command(self, device_id: str, command: int, 
                         params: Optional[list] = None) -> Dict[str, Any]:
        """
        Отправляет команду с проверкой безопасности
        """
        # Проверка безопасности команды
        if command not in self.command_whitelist:
            return {
                "type": "ERROR", 
                "message": f"Команда {hex(command)} не в белом списке безопасности"
            }
        
        # Проверка ограничения частоты
        if not self.check_rate_limit(device_id, command):
            return {
                "type": "ERROR",
                "message": f"Превышено ограничение частоты для устройства {device_id}"
            }
        
        # Отправка команды
        result = self.manager.send_command_to_device(device_id, command, params)
        
        # Логирование для аудита безопасности
        self.log_security_event("command_sent", {
            "device_id": device_id,
            "command": hex(command),
            "params": params,
            "result": result.get('type', 'unknown')
        })
        
        return result
    
    def check_rate_limit(self, device_id: str, command: int) -> bool:
        """
        Проверяет, не превышает ли частота отправки команд ограничения
        """
        key = f"{device_id}_{command}"
        current_time = time.time()
        
        if key not in self.command_rate_limits:
            self.command_rate_limits[key] = []
        
        # Удаляем старые записи (старше 60 секунд)
        self.command_rate_limits[key] = [
            t for t in self.command_rate_limits[key] 
            if current_time - t < 60
        ]
        
        # Проверяем ограничение
        if len(self.command_rate_limits[key]) >= self.max_commands_per_minute:
            return False
        
        # Добавляем текущую команду
        self.command_rate_limits[key].append(current_time)
        return True
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        Логирует события безопасности
        """
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        }
        # В реальной системе это бы писалось в безопасное хранилище
        print(f"[БЕЗОПАСНОСТЬ] {event_type}: {details}")
    
    def setup_safety_monitoring(self):
        """
        Настраивает постоянный мониторинг безопасности
        """
        # Создаем поток для мониторинга критических параметров
        monitoring_thread = threading.Thread(target=self.safety_monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        self.monitoring_threads.append(monitoring_thread)
        
        print("Мониторинг безопасности запущен")
    
    def safety_monitoring_loop(self):
        """
        Цикл постоянного мониторинга безопасности системы
        """
        while True:
            try:
                # Проверяем критические параметры
                self.check_system_safety()
                
                # Задержка между проверками
                time.sleep(5.0)
            except Exception as e:
                print(f"Ошибка в цикле мониторинга безопасности: {e}")
                time.sleep(1.0)  # Небольшая задержка перед повтором
    
    def check_system_safety(self):
        """
        Проверяет безопасность системы
        """
        # Проверяем статусы всех устройств
        statuses = self.manager.get_all_statuses()
        
        for device_id, status in statuses.items():
            if status['status'] == 'error':
                print(f"!!! ВНИМАНИЕ: Устройство {device_id} в состоянии ошибки !!!")
                self.trigger_emergency_procedure(device_id, "device_error", status)
    
    def trigger_emergency_procedure(self, device_id: str, error_type: str, error_details: Dict[str, Any]):
        """
        Активирует аварийную процедуру
        """
        print(f"Активация аварийной процедуры для {device_id}, причина: {error_type}")
        
        # Пример простой аварийной процедуры
        if error_type == "device_error":
            # Попытка переподключения
            self.attempt_device_recovery(device_id)
        elif error_type == "over_temperature":
            # Аварийное отключение
            self.emergency_device_shutdown(device_id)
    
    def attempt_device_recovery(self, device_id: str):
        """
        Пытается восстановить устройство после ошибки
        """
        print(f"Попытка восстановления устройства {device_id}")
        # В реальной системе тут могла бы быть попытка переподключения,
        # перезагрузки устройства и т.п.
    
    def emergency_device_shutdown(self, device_id: str):
        """
        Аварийное отключение устройства
        """
        print(f"Аварийное отключение устройства {device_id}")
        # В реальной системе тут могла бы быть команда на безопасное отключение
    
    def implement_defensive_commands(self):
        """
        Реализует защитные команды и процедуры
        """
        # Определяем безопасные команды
        self.command_whitelist.update([
            0x01,  # LED_ON (безопасная индикация)
            0x02,  # LED_OFF
            0x04,  # READ_SENSOR
            0x05,  # GET_STATUS
        ])
        
        # Определяем потенциально опасные команды (их нужно дополнительно проверять)
        self.potentially_risky_commands = {
            0x03: "SET_SERVO_ANGLE",  # Может вызвать физическое повреждение
            0x10: "ACTUATE_MOTOR",    # Может вызвать движение механизмов
        }
        
        print("Защитные механизмы инициализированы")

# Пример использования безопасного агента
if __name__ == "__main__":
    agent = SafeAndReliableAgent()
    
    # Инициализация защитных механизмов
    agent.implement_defensive_commands()
    agent.setup_safety_monitoring()
    
    # Настройка системы (с ожиданием возможных ошибок)
    agent.setup_home_automation_system()
    
    # Тестирование безопасной отправки команд
    test_commands = [
        (0x01, "LED_ON - безопасная команда"),
        (0x04, "READ_SENSOR - безопасная команда"),
        (0xFF, "НЕИЗВЕСТНАЯ_КОМАНДА - будет заблокирована")
    ]
    
    for cmd, description in test_commands:
        print(f"\nТест: {description}")
        result = agent.safe_send_command("kitchen_temp", cmd)
        print(f"Результат: {result}")
    
    # Запуск безопасного ReAct цикла
    safe_result = agent.advanced_react_cycle("Проверить систему безопасности")
    print(f"\nРезультат безопасного цикла: {safe_result}")
    
    # Завершение работы
    agent.manager.close_all_connections()
```

## 6. Адаптивное поведение и машинное обучение на лету

Теперь реализуем систему, которая может адаптировать свое поведение на основе предыдущих результатов:

```python
# adaptive_behavior.py
import time
import json
from typing import Dict, Any, List, Tuple
from collections import defaultdict, deque
from safety_and_reliability import SafeAndReliableAgent

class AdaptiveAgent(SafeAndReliableAgent):
    """
    ИИ-агент с адаптивным поведением, который учится на предыдущих результатах
    """
    
    def __init__(self):
        super().__init__()
        self.action_outcome_history = []  # История действий и результатов
        self.patterns = defaultdict(list)  # Обнаруженные паттерны
        self.performance_metrics = {}  # Метрики производительности
        self.adaptation_rules = {}  # Правила адаптации
        self.learning_buffer = deque(maxlen=100)  # Буфер для обучения
        self.experience_db = {}  # База знаний опыта
    
    def record_action_outcome(self, action: Dict[str, Any], outcome: Dict[str, Any], 
                            context: Dict[str, Any] = None):
        """
        Записывает результат действия для последующего обучения
        """
        record = {
            "timestamp": time.time(),
            "action": action,
            "outcome": outcome,
            "context": context or {},
            "success": self.is_outcome_successful(outcome)
        }
        
        self.action_outcome_history.append(record)
        self.learning_buffer.append(record)
        
        # Обновляем базу знаний
        self.update_experience_database(record)
        
        # Проверяем, нужно ли обновить правила адаптации
        self.check_for_adaptation_opportunities()
    
    def is_outcome_successful(self, outcome: Dict[str, Any]) -> bool:
        """
        Определяет, был ли результат успешным
        """
        outcome_type = outcome.get('type', '').upper()
        return outcome_type not in ['ERROR', 'TIMEOUT', 'EXCEPTION']
    
    def update_experience_database(self, record: Dict[str, Any]):
        """
        Обновляет базу знаний опыта
        """
        action_key = f"{record['action'].get('command', 'unknown')}_{record['action'].get('device_type', 'unknown')}"
        
        if action_key not in self.experience_db:
            self.experience_db[action_key] = {
                "attempts": 0,
                "successes": 0,
                "average_response_time": 0.0,
                "contexts": []
            }
        
        db_entry = self.experience_db[action_key]
        db_entry["attempts"] += 1
        
        if record["success"]:
            db_entry["successes"] += 1
        
        # Обновляем среднее время отклика
        if "response_time" in record.get("context", {}):
            current_avg = db_entry["average_response_time"]
            new_time = record["context"]["response_time"]
            total_attempts = db_entry["attempts"]
            db_entry["average_response_time"] = (
                (current_avg * (total_attempts - 1) + new_time) / total_attempts
            )
        
        db_entry["contexts"].append(record["context"])
    
    def check_for_adaptation_opportunities(self):
        """
        Проверяет, есть ли возможности для адаптации поведения
        """
        # Пример адаптации: если определенная команда часто неудачна, 
        # изменить подход к ней
        for action_key, stats in self.experience_db.items():
            if stats["attempts"] >= 5:  # Достаточно данных для анализа
                success_rate = stats["successes"] / stats["attempts"]
                
                if success_rate < 0.5:  # Менее 50% успеха
                    print(f"Низкий успех для {action_key}: {success_rate:.2%}")
                    
                    # Добавляем правило адаптации
                    if action_key not in self.adaptation_rules:
                        self.adaptation_rules[action_key] = {
                            "strategy": "retry_with_delay",
                            "parameters": {"delay_multiplier": 2.0}
                        }
    
    def adaptive_command_execution(self, device_id: str, command: int, 
                                 params: Optional[list] = None, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Выполняет команду с учетом предыдущего опыта и адаптации
        """
        start_time = time.time()
        
        # Проверяем, есть ли правила адаптации для этой команды
        action_key = f"{command}_{self.known_devices.get(device_id, {}).get('type', 'unknown')}"
        
        if action_key in self.adaptation_rules:
            rule = self.adaptation_rules[action_key]
            print(f"Применяю правило адаптации для {action_key}: {rule}")
            
            if rule["strategy"] == "retry_with_delay":
                delay = rule["parameters"].get("delay_multiplier", 1.0) * 0.1
                time.sleep(delay)
        
        # Выполняем команду
        result = self.safe_send_command(device_id, command, params)
        
        # Фиксируем результат
        outcome_time = time.time()
        execution_context = {
            "response_time": outcome_time - start_time,
            "command": command,
            "device_id": device_id,
            "original_context": context or {}
        }
        
        self.record_action_outcome(
            {"command": command, "device_id": device_id, "params": params},
            result,
            execution_context
        )
        
        return result
    
    def learn_from_environment(self):
        """
        Анализирует историю и извлекает уроки для будущих действий
        """
        if len(self.learning_buffer) < 10:
            return  # Нужно больше данных для анализа
        
        # Анализируем частые паттерны
        patterns_found = 0
        
        # Пример: ищем ситуации, когда определенные действия приводят к определенным результатам
        for i in range(len(self.learning_buffer) - 5):
            sequence = list(self.learning_buffer)[i:i+5]
            
            # Пример анализа: если после чтения температуры >30°C
            # часто включается охлаждение
            temp_readings = [r for r in sequence if 
                           r['action'].get('command') == 0x04 and 
                           r['outcome'].get('type') == 'SENSOR_DATA']
            
            if temp_readings:
                high_temp = any(r['outcome'].get('value', 0) > 30 for r in temp_readings)
                
                if high_temp:
                    subsequent_actions = [r for r in sequence[len(temp_readings):] 
                                        if r['action'].get('command') == 0x01]  # LED_ON
                    if subsequent_actions:
                        print(f"Обнаружен паттерн: высокая температура -> включение охлаждения")
                        patterns_found += 1
        
        print(f"Обнаружено паттернов: {patterns_found}")
    
    def get_advice_for_action(self, command: int, device_type: str) -> Dict[str, Any]:
        """
        Возвращает рекомендации по выполнению действия на основе опыта
        """
        action_key = f"{command}_{device_type}"
        
        if action_key in self.experience_db:
            stats = self.experience_db[action_key]
            success_rate = stats["successes"] / stats["attempts"] if stats["attempts"] > 0 else 0
            
            advice = {
                "estimated_success_rate": success_rate,
                "average_response_time": stats["average_response_time"],
                "recommendation": "proceed" if success_rate > 0.7 else "consider_alternative"
            }
            
            # Предлагаем адаптацию, если успех невысок
            if success_rate < 0.5:
                advice["suggestion"] = "Try with increased delay or alternative approach"
            
            return advice
        
        # Если опыта нет, возвращаем нейтральные рекомендации
        return {
            "estimated_success_rate": 0.8,  # Предполагаем высокий успех по умолчанию
            "average_response_time": 0.5,
            "recommendation": "proceed",
            "note": "No historical data available"
        }
    
    def adaptive_react_cycle(self, goal: str) -> str:
        """
        Адаптивный ReAct цикл с самообучением
        """
        print(f"\n=== Адаптивный ReAct цикл для цели: {goal} ===")
        
        # Сначала извлекаем уроки из опыта
        self.learn_from_environment()
        
        # Разрабатываем план как обычно
        plan = self.develop_plan(goal)
        
        for step_idx, step in enumerate(plan):
            print(f"\n--- Адаптивный шаг {step_idx + 1}: {step['description']} ---")
            
            # Получаем рекомендации для этого действия
            device_type = step.get('device_type', 'generic')
            advice = self.get_advice_for_action(step.get('command', 0), device_type)
            print(f"Рекомендации: {advice}")
            
            # Формируем рассуждение с учетом опыта
            reason = (f"На основе предыдущего опыта, я планирую выполнить: {step['description']}. "
                     f"Ожидаемый успех: {advice['estimated_success_rate']:.1%}")
            
            self.thought_history.append({
                "step": step_idx,
                "reason": reason,
                "advice_used": advice,
                "timestamp": time.time()
            })
            
            # Выполняем действие с адаптацией
            action_result = self.execute_adaptive_step(step)
            self.action_history.append({
                "step": step_idx,
                "action": step,
                "result": action_result,
                "timestamp": time.time()
            })
            
            # Наблюдаем результат
            observation = self.observe_physical_response(step, action_result)
            self.observation_history.append({
                "step": step_idx,
                "action_result": action_result,
                "observation": observation,
                "timestamp": time.time()
            })
            
            # Обновляем убеждения
            self.update_beliefs_from_observation(observation, step)
            
            # Записываем результат для обучения
            self.record_action_outcome(
                step, 
                action_result, 
                {"step": step_idx, "goal": goal}
            )
            
            # Проверяем достижение цели
            if self.is_goal_achieved(goal):
                return f"Цель '{goal}' достигнута адаптивно после {step_idx + 1} шагов"
        
        return f"Адаптивный цикл для цели '{goal}' завершен, выполнено {len(plan)} шагов"
    
    def execute_adaptive_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет шаг с адаптацией на основе опыта
        """
        if step['action'] in ['read_sensor', 'read_multiple_sensors']:
            device_ids = [did for did, info in self.known_devices.items() 
                         if step.get('device_type', '') in info['type']]
            
            if device_ids:
                device_id = device_ids[0]
                
                # Используем адаптивное выполнение
                result = self.adaptive_command_execution(
                    device_id, 
                    step['command'],
                    context={"step": step}
                )
                
                return {
                    "status": "success", 
                    "action_type": step['action'],
                    "device_id": device_id,
                    "result": result
                }
            else:
                return {"status": "error", "message": "Устройство не найдено"}
        
        return {"status": "unknown_action", "action_type": step['action']}

# Тестирование адаптивного агента
if __name__ == "__main__":
    agent = AdaptiveAgent()
    
    # Инициализация защитных механизмов
    agent.implement_defensive_commands()
    agent.setup_safety_monitoring()
    
    # Настройка системы
    agent.setup_home_automation_system()
    
    # Выполняем агент несколько раз, чтобы накопить опыт
    goals = [
        "Мониторинг температуры в кухне",
        "Проверка системы безопасности",
        "Анализ состояния освещения"
    ]
    
    for i, goal in enumerate(goals):
        print(f"\n{'='*60}")
        print(f"ИТЕРАЦИЯ {i+1}: {goal}")
        print(f"{'='*60}")
        
        result = agent.adaptive_react_cycle(goal)
        print(f"Результат: {result}")
        
        # Показываем накопленный опыт
        print(f"\nНакоплено записей опыта: {len(agent.action_outcome_history)}")
        print(f"Известных паттернов: {len(agent.experience_db)}")
    
    # Показываем статистику обучения
    print(f"\nСтатистика обучения:")
    print(f"- Всего действий: {len(agent.action_outcome_history)}")
    print(f"- Успешных действий: {sum(1 for r in agent.action_outcome_history if r['success'])}")
    print(f"- Записей опыта: {len(agent.experience_db)}")
    print(f"- Правил адаптации: {len(agent.adaptation_rules)}")
    
    agent.manager.close_all_connections()
```

## 7. Заключение: Современные подходы к ИИ-агентам с физическим миром

В этом уроке мы реализовали:

1. **Масштабируемую архитектуру** для управления несколькими Arduino
2. **Систему координации** между устройствами с распределенными сценариями
3. **Расширенный паттерн ReAct** с учетом физических задержек и откликов
4. **Механизмы безопасности и надежности** для защиты от ошибок
5. **Адаптивное поведение** с обучением на предыдущем опыте

Теперь ваш ИИ-агент может:
- Управлять распределенной системой из нескольких физических устройств
- Принимать комплексные решения на основе данных с нескольких сенсоров
- Адаптироваться к изменениям в окружающей среде
- Обеспечивать безопасность физических взаимодействий
- Непрерывно улучшать свое поведение на основе опыта

Это мощная архитектура для создания умных систем, способных взаимодействовать с физическим миром, как в приложениях IoT, так и в робототехнике, автоматизации зданий и индустриальных системах.

В следующем уроке мы создадим финальный проект, объединяющий все изученные концепции в комплексной системе.