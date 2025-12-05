# Урок 4: Голосовое управление и продвинутые ИИ-взаимодействия

## Оглавление
1. [Цель урока](#цель-урока)
2. [Обзор предыдущих уроков](#обзор-предыдущих-уроков)
3. [Добавление голосового управления](#добавление-голосового-управления)
4. [Интеграция с ASR/TTS системами](#интеграция-с-asr/tts-системами)
5. [Продвинутые ИИ-модели для анализа](#продвинутые-ии-модели-для-анализа)
6. [Обновление Python-интерфейса с голосом](#обновление-python-интерфейса-с-голосом)
7. [Создание умного помощника для Arduino](#создание-умного-помощника-для-arduino)
8. [Задание для практики](#задание-для-практики)

---

## Цель урока

Научиться интегрировать голосовое управление с системой Ollama-Arduino. После этого урока вы сможете управлять Arduino с помощью голосовых команд и получать голосовые отчеты о состоянии системы.

## Обзор предыдущих уроков

В предыдущих уроках мы:
- Создали базовую связь между Ollama и Arduino
- Научились управлять светодиодом и сервоприводом
- Добавили датчики и создали замкнутую систему управления
- Научились анализировать данные датчиков с помощью ИИ

## Добавление голосового управления

Для голосового управления нам понадобятся:
1. Библиотека распознавания речи (Speech Recognition)
2. Библиотека синтеза речи (pyttsx3 или gTTS)
3. Микрофон для захвата голоса
4. Колонки для вывода речи

Установим необходимые библиотеки:
```bash
pip install speechrecognition pyttsx3 pyaudio
```

## Интеграция с ASR/TTS системами

Создадим модуль голосового интерфейса:

```python
import speech_recognition as sr
import pyttsx3
import threading
import time

class VoiceInterface:
    def __init__(self):
        # Инициализация распознавания речи
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Настройка параметров микрофона
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)  # Адаптация к шуму
        
        # Инициализация синтеза речи
        self.tts_engine = pyttsx3.init()
        
        # Настройка голоса (по желанию)
        voices = self.tts_engine.getProperty('voices')
        # Можете выбрать подходящий голос
        # self.tts_engine.setProperty('voice', voices[0].id)
        
        # Настройка скорости речи
        self.tts_engine.setProperty('rate', 150)
        
        # Состояние прослушивания
        self.listening = False
        self.listener_thread = None
    
    def listen_for_command(self, timeout=5):
        """Прослушивание голосовой команды"""
        try:
            with self.microphone as source:
                print("Слушаю...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            print("Распознаю...")
            # Используем Google Speech Recognition (требует подключение к интернету)
            command = self.recognizer.recognize_google(audio, language="ru-RU")
            print(f"Распознанная команда: {command}")
            return command
            
        except sr.WaitTimeoutError:
            print("Не дождался команды")
            return None
        except sr.UnknownValueError:
            print("Не удалось распознать речь")
            return None
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            return None
    
    def speak(self, text):
        """Воспроизведение текста голосом"""
        print(f"Говорю: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def start_continuous_listening(self, callback_function):
        """Начать непрерывное прослушивание с переданной функцией обратного вызова"""
        if self.listening:
            print("Прослушивание уже активно")
            return
        
        self.listening = True
        self.listener_thread = threading.Thread(
            target=self._continuous_listening_worker,
            args=(callback_function,)
        )
        self.listener_thread.start()
    
    def stop_listening(self):
        """Остановить непрерывное прослушивание"""
        self.listening = False
        if self.listener_thread:
            self.listener_thread.join()
    
    def _continuous_listening_worker(self, callback_function):
        """Рабочий поток для непрерывного прослушивания"""
        while self.listening:
            try:
                with self.microphone as source:
                    # Не используем timeout, чтобы постоянно слушать
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                
                try:
                    command = self.recognizer.recognize_google(audio, language="ru-RU")
                    print(f"Распознанная команда: {command}")
                    
                    # Вызываем функцию обратного вызова в отдельном потоке
                    callback_thread = threading.Thread(
                        target=callback_function,
                        args=(command,)
                    )
                    callback_thread.start()
                    
                except sr.UnknownValueError:
                    # Продолжаем прослушивание, если не удалось распознать
                    continue
                except sr.RequestError:
                    # Продолжаем прослушивание, если ошибка сервиса
                    continue
            except sr.WaitTimeoutError:
                # Продолжаем ожидать команду
                continue
```

## Продвинутые ИИ-модели для анализа

Создадим полный интегрированный класс с голосовым управлением:

```python
import serial
import time
import json
import requests
import re
import threading
import speech_recognition as sr
import pyttsx3

class AdvancedVoiceAIController:
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        # Инициализация Arduino
        self.arduino = serial.Serial(arduino_port, baudrate)
        time.sleep(2)

        # Инициализация Ollama
        self.ollama_url = ollama_url
        self.use_local_ollama = use_local_ollama
        self.model = model

        # Инициализация распознавания речи
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Адаптация к шуму
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # Синтезатор речи
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        # Команды Arduino
        self.commands = {
            'turn_on_led': {'command': 0x01, 'params': []},
            'turn_off_led': {'command': 0x02, 'params': []},
            'blink_led': {'command': 0x03, 'params': [3]},
            'get_temperature': {'command': 0x07, 'params': []},
            'get_light': {'command': 0x08, 'params': []},
            'get_all_sensors': {'command': 0x09, 'params': []},
            'set_servo_angle': {'command': 0x05, 'params': [90]},
            'get_servo_angle': {'command': 0x06, 'params': []},
            'set_auto_mode': {'command': 0x0A, 'params': [0]}
        }
        
        # Состояние системы
        self.running = False
        self.mode = 'manual'  # 'manual', 'voice', 'smart_assistant'
    
    def speak(self, text):
        """Озвучивание текста"""
        print(f"Говорю: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_for_command(self, timeout=5):
        """Прослушивание голосовой команды"""
        try:
            with self.microphone as source:
                print("Слушаю...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            print("Распознаю...")
            command = self.recognizer.recognize_google(audio, language="ru-RU")
            print(f"Распознанная команда: {command}")
            return command
            
        except sr.WaitTimeoutError:
            print("Не дождался команды")
            return None
        except sr.UnknownValueError:
            print("Не удалось распознать речь")
            return None
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            return None
    
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
    
    def process_command_with_ai(self, user_input):
        """Обработка команды с помощью ИИ"""
        # Формируем промпт для ИИ
        ai_prompt = f"""
        Пользователь сказал или ввел: "{user_input}"
        
        Определи, какие действия нужно выполнить с помощью Arduino.
        Возможные действия:
        - turn_on_led: включить светодиод
        - turn_off_led: выключить светодиод
        - blink_led: мигнуть светодиодом (по умолчанию 3 раза)
        - get_temperature: получить температуру с датчика
        - get_light: получить уровень освещенности
        - set_servo_angle: установить угол сервопривода (ожидает параметр - угол в градусах 0-180)
        - get_all_sensors: получить показания всех датчиков
        
        Если пользователь спрашивает о текущем состоянии устройств, используй соответствующие get-команды.
        Если в команде указано число (например, "поверни на 90"), используй его как параметр.
        
        Ответь в формате JSON: {{"actions": [{"action": "action_name", "params": [param1, param2, ...]}, ...]}}
        
        Примеры:
        Ввод: "Зажги свет" -> Ответ: {{"actions": [{{"action": "turn_on_led", "params": []}}]}}
        Ввод: "Какая температура?" -> Ответ: {{"actions": [{{"action": "get_temperature", "params": []}}]}}
        Ввод: "Поверни серво на 45 градусов" -> Ответ: {{"actions": [{{"action": "set_servo_angle", "params": [45]}}]}}
        """
        
        ai_response = self.query_ollama(ai_prompt)
        print(f"Ответ ИИ: {ai_response}")
        
        try:
            response_json = json.loads(ai_response)
            actions = response_json.get('actions', [])
            return actions
        except json.JSONDecodeError:
            print("Ошибка парсинга ответа ИИ")
            return []
    
    def execute_actions(self, actions):
        """Выполнение списка действий"""
        for action in actions:
            action_name = action.get('action')
            params = action.get('params', [])
            
            if action_name in self.commands:
                command_info = self.commands[action_name]
                
                # Формирование данных для отправки
                if params:
                    data = [command_info['command']] + params
                else:
                    data = [command_info['command']] + command_info['params']
                
                # CRC
                crc = sum(data) & 0xFF
                packet = [0xAA, 0x55, len(data)] + data + [crc]
                
                # Отправка
                self.arduino.write(bytes(packet))
                print(f"Отправлена команда {action_name}: {[hex(b) for b in packet]}")
                
                # Обработка специфичных команд
                if action_name in ['get_temperature', 'get_light', 'get_all_sensors', 'get_servo_angle']:
                    result = self.wait_for_sensor_response(command_info['command'])
                    if result is not None:
                        self.report_sensor_data(action_name, result)
            else:
                print(f"Неизвестная команда: {action_name}")
    
    def wait_for_sensor_response(self, command_code):
        """Ожидание и обработка ответа от датчиков"""
        start_time = time.time()
        timeout = 3
        
        while time.time() - start_time < timeout:
            if self.arduino.in_waiting:
                raw_data = self.arduino.read_all()
                
                if len(raw_data) >= 6 and raw_data[0] == 0xAA and raw_data[1] == 0x55:
                    data_len = raw_data[2]
                    if len(raw_data) >= 4 + data_len + 1:
                        data_bytes = raw_data[3:3+data_len]
                        
                        if data_bytes[0] == command_code:
                            if command_code == 0x07:  # Температура
                                if len(data_bytes) >= 3:
                                    temp_raw = data_bytes[1] + (data_bytes[2] << 8)
                                    voltage = (temp_raw / 1024.0) * 5.0
                                    temp_celsius = (voltage - 0.5) * 100
                                    return temp_celsius
                            elif command_code == 0x08:  # Освещенность
                                if len(data_bytes) >= 3:
                                    light_raw = data_bytes[1] + (data_bytes[2] << 8)
                                    return light_raw
                            elif command_code == 0x09:  # Все датчики
                                if len(data_bytes) >= 5:
                                    temp_raw = data_bytes[1] + (data_bytes[2] << 8)
                                    light_raw = data_bytes[3] + (data_bytes[4] << 8)
                                    
                                    voltage = (temp_raw / 1024.0) * 5.0
                                    temp_celsius = (voltage - 0.5) * 100
                                    
                                    return {"temperature": temp_celsius, "light": light_raw}
            
            time.sleep(0.1)
        
        return None
    
    def report_sensor_data(self, command, data):
        """Озвучивание данных датчиков"""
        if command == 'get_temperature':
            response = f"Температура составляет {data:.1f} градусов Цельсия"
        elif command == 'get_light':
            response = f"Уровень освещенности {data} единиц"
        elif command == 'get_all_sensors':
            response = f"Температура {data['temperature']:.1f} градусов, освещенность {data['light']} единиц"
        else:
            response = f"Данные получены: {data}"
        
        print(f"Результат: {response}")
        self.speak(response)
    
    def manual_mode(self):
        """Режим ручного управления"""
        self.mode = 'manual'
        self.speak("Ручной режим активирован. Введите команду текстом или скажите 'голос' для переключения.")
        
        while self.running:
            try:
                user_input = input("Введите команду (или 'голос' для переключения, 'стоп' для выхода): ")
                
                if user_input.lower() == 'стоп':
                    break
                elif user_input.lower() == 'голос':
                    self.voice_mode()
                    break
                else:
                    actions = self.process_command_with_ai(user_input)
                    self.execute_actions(actions)
            except KeyboardInterrupt:
                break
    
    def voice_mode(self):
        """Режим голосового управления"""
        self.mode = 'voice'
        self.speak("Голосовой режим активирован. Скажите команду или скажите 'стоп' для выхода, 'ручной' для переключения.")
        
        while self.running:
            command = self.listen_for_command(timeout=10)
            
            if command:
                if 'стоп' in command.lower():
                    break
                elif 'ручной' in command.lower():
                    self.manual_mode()
                    break
                else:
                    actions = self.process_command_with_ai(command)
                    self.execute_actions(actions)
            else:
                # Продолжаем прослушивание
                continue
    
    def smart_assistant_mode(self):
        """Режим умного помощника"""
        self.mode = 'smart_assistant'
        self.speak("Режим умного помощника активирован. Я слушаю и помогаю управлять устройствами.")
        
        # Приветствие
        self.speak("Здравствуйте. Я ваш умный помощник для управления электроникой. Что вы хотите сделать?")
        
        while self.running:
            command = self.listen_for_command(timeout=15)
            
            if command:
                if any(word in command.lower() for word in ['стоп', 'хватит', 'выход']):
                    self.speak("Умный помощник остановлен")
                    break
                elif any(word in command.lower() for word in ['как дела', 'привет', 'здравствуй']):
                    self.speak("Привет! Я в порядке. Готов помочь вам управлять устройствами.")
                elif any(word in command.lower() for word in ['расскажи', 'информация', 'статус']):
                    # Получаем и озвучиваем текущий статус системы
                    self.speak("Проверяю статус системы...")
                    actions = [{"action": "get_all_sensors", "params": []}]
                    self.execute_actions(actions)
                else:
                    actions = self.process_command_with_ai(command)
                    self.execute_actions(actions)
                    
                    # Спрашиваем, нужна ли еще помощь
                    self.speak("Еще чем могу помочь?")
            else:
                # Если не было команды в течение таймаута, спрашиваем снова
                self.speak("Я слушаю. Чем могу помочь?")
    
    def run(self):
        """Запуск системы"""
        self.running = True
        self.speak("Система управления Arduino с ИИ и голосом запущена")
        
        print("Выберите режим:")
        print("1. Ручной режим (ввод команд текстом)")
        print("2. Голосовой режим")
        print("3. Умный помощник")
        
        mode_choice = input("Введите 1, 2 или 3: ")
        
        if mode_choice == "1":
            self.manual_mode()
        elif mode_choice == "2":
            self.voice_mode()
        elif mode_choice == "3":
            self.smart_assistant_mode()
        
        self.speak("Система остановлена")
    
    def close(self):
        self.arduino.close()

# Запуск системы
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    controller = AdvancedVoiceAIController('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # controller = AdvancedVoiceAIController('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")

    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    finally:
        controller.close()
```

## Обновление Python-интерфейса с голосом

Теперь создадим продвинутый режим с предсказательной аналитикой:

```python
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from datetime import datetime

class PredictiveVoiceController(AdvancedVoiceAIController):
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        super().__init__(arduino_port, baudrate, ollama_url, use_local_ollama, model)

        # Хранилище исторических данных
        self.temperature_history = deque(maxlen=100)
        self.light_history = deque(maxlen=100)
        self.time_history = deque(maxlen=100)

        # Режим предсказания
        self.prediction_mode = False
        self.anomaly_detection = True
    
    def collect_sensor_data(self):
        """Сбор и сохранение данных с датчиков"""
        # Получаем данные
        self.send_to_arduino('get_all_sensors')
        sensor_data = self.wait_for_sensor_response(0x09)
        
        if sensor_data:
            temp = sensor_data['temperature']
            light = sensor_data['light']
            current_time = datetime.now().timestamp()
            
            # Сохраняем данные
            self.temperature_history.append(temp)
            self.light_history.append(light)
            self.time_history.append(current_time)
            
            return sensor_data
        return None
    
    def predict_temperature_trend(self, look_ahead_minutes=5):
        """Предсказание температуры на основе исторических данных"""
        if len(self.temperature_history) < 5:
            return None
            
        # Простейший трендовый анализ
        temps = list(self.temperature_history)
        times = list(self.time_history)
        
        # Нормализуем временные метки
        time_norm = [t - times[0] for t in times]
        
        # Линейная регрессия вручную (упрощенная)
        n = len(temps)
        sum_x = sum(time_norm)
        sum_y = sum(temps)
        sum_xx = sum(x * x for x in time_norm)
        sum_xy = sum(time_norm[i] * temps[i] for i in range(n))
        
        if n * sum_xx - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Предсказание для будущего времени
            future_time = time_norm[-1] + look_ahead_minutes * 60  # минуты в секунды
            predicted_temp = slope * future_time + intercept
            
            return predicted_temp
        else:
            # Если деление на 0, возвращаем последнее значение
            return temps[-1]
    
    def detect_anomalies(self):
        """Обнаружение аномалий в данных датчиков"""
        if len(self.temperature_history) < 5:
            return []
        
        temps = list(self.temperature_history)
        lights = list(self.light_history)
        
        anomalies = []
        
        # Обнаружение аномалий по температуре (простейший метод)
        mean_temp = sum(temps) / len(temps)
        std_temp = (sum((t - mean_temp) ** 2 for t in temps) / len(temps)) ** 0.5
        
        current_temp = temps[-1]
        if abs(current_temp - mean_temp) > 2 * std_temp:  # Если отклонение > 2 стандартных отклонений
            anomalies.append(f"Аномалия температуры: {current_temp:.2f}°C (среднее {mean_temp:.2f}°C)")
        
        # Обнаружение аномалий по свету
        if len(lights) > 0:
            mean_light = sum(lights) / len(lights)
            std_light = (sum((l - mean_light) ** 2 for l in lights) / len(lights)) ** 0.5
            
            current_light = lights[-1]
            if abs(current_light - mean_light) > 2 * std_light:
                anomalies.append(f"Аномалия освещенности: {current_light} (среднее {mean_light:.2f})")
        
        return anomalies
    
    def run_predictive_mode(self):
        """Режим с предсказательной аналитикой"""
        self.mode = 'predictive'
        self.speak("Режим предсказательной аналитики активирован.")
        
        print("Запуск сбора данных и анализа...")
        
        while self.running:
            # Собираем данные
            sensor_data = self.collect_sensor_data()
            
            if sensor_data:
                print(f"Текущие данные: темп. {sensor_data['temperature']:.2f}°C, свет {sensor_data['light']}")
                
                # Проверяем аномалии
                anomalies = self.detect_anomalies()
                if anomalies:
                    self.speak("Обнаружены аномалии:")
                    for anomaly in anomalies:
                        print(f"- {anomaly}")
                        self.speak(anomaly)
                
                # Делаем предсказание температуры
                predicted_temp = self.predict_temperature_trend(look_ahead_minutes=5)
                if predicted_temp:
                    print(f"Прогнозируемая температура через 5 минут: {predicted_temp:.2f}°C")
                    
                    # Принимаем решения на основе предсказания
                    if predicted_temp > 28:  # Если ожидается жара
                        self.speak(f"Прогноз: температура поднимется до {predicted_temp:.1f}°C. Рекомендую открыть вентиляцию.")
                        self.send_to_arduino('set_servo_angle', [90])
                    elif predicted_temp < 18:  # Если ожидается холод
                        self.speak(f"Прогноз: температура опустится до {predicted_temp:.1f}°C. Рекомендую закрыть вентиляцию.")
                        self.send_to_arduino('set_servo_angle', [0])
            
            # Ожидаем 30 секунд перед следующим измерением
            time.sleep(30)
    
    def visualize_data(self):
        """Визуализация исторических данных"""
        if len(self.temperature_history) < 2:
            print("Недостаточно данных для визуализации")
            return
        
        # Подготавливаем данные для графика
        temps = list(self.temperature_history)
        lights = list(self.light_history)
        times = list(range(len(temps)))  # Используем индексы вместо временных меток для простоты
        
        # Создаем график
        plt.figure(figsize=(12, 6))
        
        plt.subplot(2, 1, 1)
        plt.plot(times, temps, 'r-', label='Температура')
        plt.title('История температуры')
        plt.ylabel('Температура (°C)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 1, 2)
        plt.plot(times, lights, 'b-', label='Освещенность')
        plt.title('История освещенности')
        plt.xlabel('Время')
        plt.ylabel('Уровень освещенности')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()

# Запуск предсказательного режима
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    controller = PredictiveVoiceController('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # controller = PredictiveVoiceController('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")
    
    try:
        controller.running = True
        print("Выберите режим:")
        print("1. Обычный голосовой режим")
        print("2. Предсказательный режим")
        print("3. Визуализация данных")
        
        mode_choice = input("Введите 1, 2 или 3: ")
        
        if mode_choice == "1":
            controller.run()
        elif mode_choice == "2":
            controller.run_predictive_mode()
        elif mode_choice == "3":
            controller.collect_sensor_data()  # Собираем немного данных
            time.sleep(1)  # Ждем
            controller.collect_sensor_data()
            controller.visualize_data()
    
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    finally:
        controller.close()
```

## Создание умного помощника для Arduino

Теперь объединим все возможности в одну систему:

```python
class UltimateAIController(PredictiveVoiceController):
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        super().__init__(arduino_port, baudrate, ollama_url, use_local_ollama, model)

        # Дополнительные возможности
        self.machine_learning_enabled = True
        self.autonomous_operation = False
        self.user_preferences = {}  # Словарь с предпочтениями пользователя
    
    def learn_user_preferences(self, command, sensor_response):
        """Изучение предпочтений пользователя по его командам"""
        # Простой метод: запоминать, какие команды пользователь выполняет при каких условиях
        if sensor_response:
            temp = sensor_response.get('temperature', 0)
            light = sensor_response.get('light', 0)
            
            # Если пользователь включает свет при низкой освещенности, запоминаем предпочтение
            if 'turn_on_led' in str(command) and light < 100:
                self.user_preferences['light_threshold'] = 100
            elif 'set_servo_angle' in str(command) and temp > 25:
                self.user_preferences['temp_threshold'] = temp
    
    def autonomous_step(self):
        """Автономный шаг принятия решения"""
        if not self.autonomous_operation:
            return
            
        # Получаем текущие данные
        sensor_data = self.collect_sensor_data()
        
        if sensor_data:
            temp = sensor_data['temperature']
            light = sensor_data['light']
            
            # Применяем изученные предпочтения пользователя
            if 'light_threshold' in self.user_preferences:
                threshold = self.user_preferences['light_threshold']
                if light < threshold and temp > 18:  # Если темно и не слишком холодно
                    self.speak("Обнаружено низкое освещение. Включаю свет.")
                    self.send_to_arduino('turn_on_led')
            
            if 'temp_threshold' in self.user_preferences:
                threshold = self.user_preferences['temp_threshold']
                if temp > threshold + 2:  # Если жарче установленного порога
                    self.speak(f"Обнаружена высокая температура {temp:.1f}°C. Регулирую вентиляцию.")
                    self.send_to_arduino('set_servo_angle', [90])
        
        # Также используем предсказательную аналитику
        predicted_temp = self.predict_temperature_trend(look_ahead_minutes=10)
        if predicted_temp and predicted_temp > 28:
            self.speak(f"Прогноз: температура повысится. Рекомендую открыть вентиляцию.")
            self.send_to_arduino('set_servo_angle', [90])
    
    def run_autonomous_mode(self):
        """Режим автономной работы с машинным обучением"""
        self.mode = 'autonomous'
        self.autonomous_operation = True
        self.speak("Режим автономной работы с машинным обучением активирован.")
        
        print("Система начинает автономно наблюдать за параметрами и принимать решения...")
        
        while self.running and self.autonomous_operation:
            self.autonomous_step()
            time.sleep(15)  # Проверяем каждые 15 секунд
    
    def run(self):
        """Расширенное меню запуска"""
        self.running = True
        self.speak("Универсальный контроллер Arduino запущен")
        
        print("\n=== Универсальный контроллер Arduino ===")
        print("Выберите режим работы:")
        print("1. Ручной режим (управление текстом)")
        print("2. Голосовой режим")
        print("3. Умный помощник")
        print("4. Предсказательный режим")
        print("5. Автономный режим с машинным обучением")
        print("6. Визуализация данных")
        
        mode_choice = input("\nВведите номер режима (1-6): ")
        
        if mode_choice == "1":
            self.manual_mode()
        elif mode_choice == "2":
            self.voice_mode()
        elif mode_choice == "3":
            self.smart_assistant_mode()
        elif mode_choice == "4":
            self.run_predictive_mode()
        elif mode_choice == "5":
            self.run_autonomous_mode()
        elif mode_choice == "6":
            self.collect_sensor_data()
            time.sleep(1)
            self.collect_sensor_data()
            self.visualize_data()
        else:
            print("Неверный выбор")
        
        self.speak("Работа контроллера завершена")

# Основной запуск
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    controller = UltimateAIController('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # controller = UltimateAIController('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")
    
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    finally:
        controller.close()
```

## Задание для практики

1. Установите необходимые библиотеки для голосового управления:
   ```bash
   pip install speechrecognition pyttsx3 pyaudio numpy matplotlib
   ```

2. Подключите микрофон и колонки к компьютеру

3. Создайте полный скрипт с интеграцией голосового управления и предсказательной аналитики

4. Протестируйте голосовые команды:
   - "Зажги свет"
   - "Какая температура?"
   - "Поверни серво на 90 градусов"
   - "Все датчики"

5. Включите предсказательный режим и наблюдайте за тем, как система предсказывает изменения температуры и принимает проактивные действия

6. Попробуйте автономный режим с машинным обучением, где система начинает предсказывать ваши предпочтения и действовать заранее

7. Используйте визуализацию данных для анализа исторических тенденций

В следующем уроке мы рассмотрим машинное обучение для предсказания и автоматизации более сложных сценариев!