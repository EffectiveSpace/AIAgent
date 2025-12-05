# Урок 5: Машинное обучение для предсказания и автоматизации

## Оглавление
1. [Цель урока](#цель-урока)
2. [Обзор предыдущих уроков](#обзор-предыдущих-уроков)
3. [Введение в машинное обучение для Arduino](#введение-в-машинное-обучение-для-arduino)
4. [Простые алгоритмы машинного обучения](#простые-алгоритмы-машинного-обучения)
5. [Обучение моделей на данных сенсоров](#обучение-моделей-на-данных-сенсоров)
6. [Предсказательная аналитика и автоматизация](#предсказательная-аналитика-и-автоматизация)
7. [Интеграция с Ollama для сложного анализа](#интеграция-с-ollama-для-сложного-анализа)
8. [Задание для практики](#задание-для-практики)

---

## Цель урока

Научиться применять методы машинного обучения для анализа данных с датчиков Arduino и создания предсказательных, автоматизированных систем. После этого урока вы сможете создавать интеллектуальные системы, которые учатся на данных и принимают решения на основе предсказаний.

## Обзор предыдущих уроков

В предыдущих уроках мы:
- Создали базовую связь между Ollama и Arduino
- Научились управлять светодиодом и сервоприводом
- Добавили датчики и создали замкнутую систему управления
- Внедрили голосовое управление и умного помощника
- Реализовали простые алгоритмы предсказания и обнаружения аномалий

## Введение в машинное обучение для Arduino

Машинное обучение в контексте Arduino и сенсорных данных позволяет:
- Прогнозировать изменения параметров окружающей среды
- Обнаруживать аномалии и нештатные ситуации
- Автоматизировать сложные сценарии на основе исторических данных
- Учиться предпочтениям пользователя и адаптировать систему

### Основные концепции:
- **Обучение с учителем**: Использование метки данных для обучения модели
- **Обучение без учителя**: Поиск паттернов в данных без меток
- **Обучение с подкреплением**: Система учится через вознаграждения и штрафы

## Простые алгоритмы машинного обучения

### 1. Линейная регрессия для предсказания трендов

Создадим класс для предсказания на основе исторических данных:

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from collections import deque
from datetime import datetime
import json
import requests
import serial
import time
import ollama

class MLArduinoController:
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        # Подключение к Arduino
        self.arduino = serial.Serial(arduino_port, baudrate)
        time.sleep(2)

        # Подключение к Ollama
        self.ollama_url = ollama_url
        self.use_local_ollama = use_local_ollama
        self.model = model

        # Исторические данные
        self.data_buffer = {
            'temperature': deque(maxlen=1000),
            'light': deque(maxlen=1000),
            'timestamp': deque(maxlen=1000)
        }

        # Модели машинного обучения
        self.models = {}

        # Состояние системы
        self.running = False

        print("MLArduinoController инициализирован")
    
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
    
    def read_sensors(self):
        """Считывание данных с датчиков"""
        # Отправляем команду получения всех сенсоров
        # Используем протокол из предыдущих уроков
        command = [0xAA, 0x55, 0x01, 0x09, 0xFF]  # CMD_GET_ALL_SENSORS
        self.arduino.write(bytes(command))
        
        # Читаем ответ
        start_time = time.time()
        timeout = 3
        while time.time() - start_time < timeout:
            if self.arduino.in_waiting:
                raw_data = self.arduino.read_all()
                
                if len(raw_data) >= 9 and raw_data[0] == 0xAA and raw_data[1] == 0x55:
                    data_len = raw_data[2]
                    if len(raw_data) >= 4 + data_len + 1:
                        data_bytes = raw_data[3:3+data_len]
                        
                        if data_bytes[0] == 0x09:  # CMD_GET_ALL_SENSORS
                            # Извлекаем температуру и свет
                            temp_raw = data_bytes[1] + (data_bytes[2] << 8)
                            light_raw = data_bytes[3] + (data_bytes[4] << 8)
                            
                            # Преобразуем температуру
                            voltage = (temp_raw / 1024.0) * 5.0
                            temperature_c = (voltage - 0.5) * 100
                            
                            return {
                                'temperature': temperature_c,
                                'light': light_raw,
                                'timestamp': datetime.now().timestamp()
                            }
            time.sleep(0.1)
        
        print("Не удалось получить данные с датчиков")
        return None
    
    def collect_data(self, duration_minutes=10):
        """Сбор данных с датчиков в течение заданного времени"""
        print(f"Сбор данных в течение {duration_minutes} минут...")
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            sensor_data = self.read_sensors()
            if sensor_data:
                # Сохраняем данные
                self.data_buffer['temperature'].append(sensor_data['temperature'])
                self.data_buffer['light'].append(sensor_data['light'])
                self.data_buffer['timestamp'].append(sensor_data['timestamp'])
                
                print(f"Данные сохранены: T={sensor_data['temperature']:.2f}, L={sensor_data['light']}")
            
            time.sleep(30)  # Сбор данных каждые 30 секунд
    
    def prepare_train_data(self):
        """Подготовка данных для обучения модели"""
        if len(self.data_buffer['temperature']) < 10:
            print("Недостаточно данных для подготовки обучения")
            return None, None
        
        # Подготовим признаки: время (в секундах с начала), скользящее среднее и т.д.
        timestamps = list(self.data_buffer['timestamp'])
        temperatures = list(self.data_buffer['temperature'])
        lights = list(self.data_buffer['light'])
        
        # Нормализуем временные метки
        base_time = timestamps[0] if timestamps else 0
        time_features = [(t - base_time) for t in timestamps]
        
        # Создаем признаки (время, скользящее среднее, производная и т.д.)
        features = []
        targets_temp = []
        targets_light = []
        
        # Используем окно для создания признаков
        window_size = 5
        for i in range(window_size, len(time_features)):
            # Текущие признаки
            feature_vector = [
                time_features[i],                    # время
                np.mean(temperatures[i-window_size:i]),  # средняя температура за окно
                np.mean(lights[i-window_size:i]),      # средний свет за окно
                temperatures[i-1],                   # предыдущее значение температуры
                lights[i-1]                         # предыдущее значение света
            ]
            
            features.append(feature_vector)
            targets_temp.append(temperatures[i])
            targets_light.append(lights[i])
        
        return np.array(features), (np.array(targets_temp), np.array(targets_light))
    
    def train_models(self):
        """Обучение моделей машинного обучения"""
        print("Начало обучения моделей...")
        
        features, (targets_temp, targets_light) = self.prepare_train_data()
        
        if features is None:
            return False
        
        if len(features) < 5:
            print("Недостаточно данных для обучения")
            return False
        
        # Обучение модели для предсказания температуры
        print(f"Размер обучающей выборки: {len(features)}")
        print(f"Размер целевых значений: температура={len(targets_temp)}, свет={len(targets_light)}")
        
        # Модель для температуры
        temp_model = make_pipeline(
            PolynomialFeatures(degree=2),  # Нелинейные отношения
            LinearRegression()
        )
        temp_model.fit(features, targets_temp)
        self.models['temperature'] = temp_model
        
        # Модель для света
        light_model = make_pipeline(
            PolynomialFeatures(degree=2),
            LinearRegression()
        )
        light_model.fit(features, targets_light)
        self.models['light'] = light_model
        
        print("Модели успешно обучены!")
        return True
    
    def predict(self, look_ahead_minutes=5):
        """Предсказание значений на заданное количество минут вперед"""
        if 'temperature' not in self.models or 'light' not in self.models:
            print("Модели не обучены")
            return None
        
        if len(self.data_buffer['timestamp']) < 5:
            print("Недостаточно текущих данных для предсказания")
            return None
        
        # Подготовим признаки для предсказания
        timestamps = list(self.data_buffer['timestamp'])
        temperatures = list(self.data_buffer['temperature'])
        lights = list(self.data_buffer['light'])
        
        base_time = timestamps[0] if timestamps else 0
        current_time = timestamps[-1]
        
        # Признаки для предсказания (на основе последних значений)
        feature_vector = [
            current_time + (look_ahead_minutes * 60),  # будущее время
            np.mean(temperatures[-5:]),                 # средняя температура за последние измерения
            np.mean(lights[-5:]),                      # средний свет за последние измерения
            temperatures[-1],                          # текущая температура
            lights[-1]                                # текущий свет
        ]
        
        # Предсказания
        pred_features = np.array([feature_vector])
        
        temp_pred = self.models['temperature'].predict(pred_features)[0]
        light_pred = self.models['light'].predict(pred_features)[0]
        
        return {
            'temperature': temp_pred,
            'light': light_pred,
            'time_ahead': look_ahead_minutes
        }
    
    def detect_anomalies(self):
        """Обнаружение аномалий с использованием статистических методов"""
        if len(self.data_buffer['temperature']) < 10:
            return []
        
        temps = np.array(self.data_buffer['temperature'])
        lights = np.array(self.data_buffer['light'])
        
        anomalies = []
        
        # Обнаружение аномалий температуры (метод Z-оценки)
        temp_mean = np.mean(temps)
        temp_std = np.std(temps)
        
        if temp_std > 0:
            current_temp = temps[-1]
            z_score = abs(current_temp - temp_mean) / temp_std
            
            if z_score > 2.5:  # Считаем аномалией если Z-оценка > 2.5
                anomalies.append({
                    'type': 'temperature',
                    'value': current_temp,
                    'anomaly': f"Аномалия температуры: {current_temp:.2f}°C (Z-score: {z_score:.2f})"
                })
        
        # Обнаружение аномалий освещенности
        light_mean = np.mean(lights)
        light_std = np.std(lights)
        
        if light_std > 0:
            current_light = lights[-1]
            z_score = abs(current_light - light_mean) / light_std
            
            if z_score > 2.5:
                anomalies.append({
                    'type': 'light',
                    'value': current_light,
                    'anomaly': f"Аномалия освещенности: {current_light} (Z-score: {z_score:.2f})"
                })
        
        return anomalies
    
    def run_autonomous_system(self):
        """Запуск автономной системы с машинным обучением"""
        self.running = True
        print("Запуск автономной системы с машинным обучением...")
        
        # Начальный сбор данных
        print("Сбор начальных данных...")
        self.collect_data(duration_minutes=1)  # Собираем 1 минуту данных для начала
        
        while self.running:
            try:
                # Считываем текущие данные
                current_data = self.read_sensors()
                
                if current_data:
                    # Сохраняем данные
                    self.data_buffer['temperature'].append(current_data['temperature'])
                    self.data_buffer['light'].append(current_data['light'])
                    self.data_buffer['timestamp'].append(current_data['timestamp'])
                    
                    print(f"Текущие данные: T={current_data['temperature']:.2f}°C, L={current_data['light']}")
                    
                    # Обнаружение аномалий
                    anomalies = self.detect_anomalies()
                    if anomalies:
                        print("ОБНАРУЖЕНЫ АНОМАЛИИ:")
                        for anomaly in anomalies:
                            print(f"  - {anomaly['anomaly']}")
                            
                            # Принимаем меры при аномалиях
                            if anomaly['type'] == 'temperature':
                                if anomaly['value'] > 30:  # Перегрев
                                    print("Обнаружен перегрев! Поворачиваем сервопривод для вентиляции")
                                    self.send_command(0x05, [90])  # set_servo_angle(90)
                                elif anomaly['value'] < 10:  # Переохлаждение
                                    print("Обнаружено переохлаждение! Закрываем вентиляцию")
                                    self.send_command(0x05, [0])   # set_servo_angle(0)
                    
                    # Периодическое обучение модели
                    if len(self.data_buffer['temperature']) % 20 == 0:  # Каждые 20 измерений
                        print("Обновление модели машинного обучения...")
                        self.train_models()
                    
                    # Делаем предсказания
                    prediction = self.predict(look_ahead_minutes=5)
                    if prediction:
                        print(f"Предсказания через {prediction['time_ahead']} мин: "
                              f"T={prediction['temperature']:.2f}°C, L={prediction['light']:.2f}")
                        
                        # Принимаем предиктивные меры
                        if prediction['temperature'] > 28:  # Скоро будет жарко
                            print("Предсказание: температура повысится. Открываем вентиляцию")
                            self.send_command(0x05, [90])  # set_servo_angle(90)
                        elif prediction['temperature'] < 18:  # Скоро будет холодно
                            print("Предсказание: температура понизится. Закрываем вентиляцию")
                            self.send_command(0x05, [0])   # set_servo_angle(0)
                
                # Ждем 60 секунд перед следующим циклом
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\nОстановка автономной системы по запросу пользователя")
                break
    
    def send_command(self, command_code, params=None):
        """Отправка команды на Arduino"""
        if params is None:
            params = []
        
        data = [command_code] + params
        crc = sum(data) & 0xFF
        packet = [0xAA, 0x55, len(data)] + data + [crc]
        
        self.arduino.write(bytes(packet))
        print(f"Отправлена команда: {[hex(b) for b in packet]}")
    
    def visualize_data(self):
        """Визуализация исторических данных и предсказаний"""
        if len(self.data_buffer['temperature']) < 2:
            print("Недостаточно данных для визуализации")
            return
        
        # Подготовка данных
        temps = list(self.data_buffer['temperature'])
        lights = list(self.data_buffer['light'])
        times = list(range(len(temps)))
        
        # Создаем график
        plt.figure(figsize=(15, 10))
        
        # Температура
        plt.subplot(2, 1, 1)
        plt.plot(times, temps, 'r-', label='Температура', linewidth=2)
        plt.title('История температуры')
        plt.ylabel('Температура (°C)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Освещенность
        plt.subplot(2, 1, 2)
        plt.plot(times, lights, 'b-', label='Освещенность', linewidth=2)
        plt.title('История освещенности')
        plt.xlabel('Время')
        plt.ylabel('Уровень освещенности')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def close(self):
        self.arduino.close()

# Пример использования
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    controller = MLArduinoController('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # controller = MLArduinoController('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")

    try:
        controller.run_autonomous_system()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    finally:
        controller.close()
```

## Обучение моделей на данных сенсоров

Теперь создадим более продвинутый класс с кластеризацией и обучением без учителя:

```python
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle

class AdvancedMLController(MLArduinoController):
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        super().__init__(arduino_port, baudrate, ollama_url, use_local_ollama, model)

        # Дополнительные модели
        self.clustering_model = None
        self.anomaly_model = None
        self.scaler = StandardScaler()

        # Режимы работы
        self.learning_phase = True  # Фаза обучения
        self.operational_phase = False  # Фаза операций
    
    def train_clustering_model(self):
        """Обучение модели кластеризации для обнаружения паттернов в данных"""
        if len(self.data_buffer['temperature']) < 10:
            print("Недостаточно данных для обучения кластеризации")
            return False
        
        # Подготовка данных
        temperatures = list(self.data_buffer['temperature'])
        lights = list(self.data_buffer['light'])
        
        # Создание признаков для кластеризации
        features = []
        for i in range(len(temperatures)):
            feature_vector = [temperatures[i], lights[i]]
            features.append(feature_vector)
        
        X = np.array(features)
        
        # Нормализация признаков
        X_scaled = self.scaler.fit_transform(X)
        
        # Определение оптимального числа кластеров (упрощенный способ)
        n_clusters = min(5, len(X))
        
        # Обучение K-means
        self.clustering_model = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = self.clustering_model.fit_predict(X_scaled)
        
        print(f"Модель кластеризации обучена. Обнаружено {n_clusters} паттернов")
        print(f"Кластеры: {list(set(cluster_labels))}")
        
        return True
    
    def train_anomaly_detection_model(self):
        """Обучение модели обнаружения аномалий"""
        if len(self.data_buffer['temperature']) < 10:
            print("Недостаточно данных для обучения модели аномалий")
            return False
        
        # Подготовка данных
        temperatures = list(self.data_buffer['temperature'])
        lights = list(self.data_buffer['light'])
        
        features = []
        for i in range(len(temperatures)):
            feature_vector = [temperatures[i], lights[i]]
            features.append(feature_vector)
        
        X = np.array(features)
        
        # Нормализация
        X_scaled = self.scaler.fit_transform(X)
        
        # Обучение Isolation Forest
        self.anomaly_model = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = self.anomaly_model.fit_predict(X_scaled)
        
        print(f"Модель обнаружения аномалий обучена. Найдено {sum(anomaly_labels == -1)} аномальных значений")
        
        return True
    
    def detect_pattern_changes(self):
        """Обнаружение изменений в паттернах поведения"""
        if self.clustering_model is None:
            print("Модель кластеризации не обучена")
            return None
        
        if len(self.data_buffer['temperature']) < 2:
            return None
        
        # Получаем последние значения
        current_temp = self.data_buffer['temperature'][-1]
        current_light = self.data_buffer['light'][-1]
        
        current_features = np.array([[current_temp, current_light]])
        current_features_scaled = self.scaler.transform(current_features)
        
        # Предсказываем кластер для текущих данных
        current_cluster = self.clustering_model.predict(current_features_scaled)[0]
        
        # Сравниваем с предыдущим кластером
        if len(self.data_buffer['temperature']) > 1:
            prev_temp = self.data_buffer['temperature'][-2]
            prev_light = self.data_buffer['light'][-2]
            
            prev_features = np.array([[prev_temp, prev_light]])
            prev_features_scaled = self.scaler.transform(prev_features)
            prev_cluster = self.clustering_model.predict(prev_features_scaled)[0]
            
            if current_cluster != prev_cluster:
                return {
                    'change_detected': True,
                    'from_cluster': prev_cluster,
                    'to_cluster': current_cluster,
                    'current_data': {'temp': current_temp, 'light': current_light}
                }
        
        return {'change_detected': False}
    
    def analyze_with_ollama(self, sensor_data, prediction=None, anomalies=None):
        """Анализ данных с помощью Ollama с использованием контекста ML"""
        context = f"""
        Проанализируй данные сенсоров и результаты машинного обучения:
        
        Текущие данные: 
        - Температура: {sensor_data['temperature']:.2f}°C
        - Освещенность: {sensor_data['light']}
        
        """
        
        if prediction:
            context += f"""
        Предсказания на 5 минут вперед:
        - Температура: {prediction['temperature']:.2f}°C
        - Освещенность: {prediction['light']:.2f}
        """
        
        if anomalies:
            context += f"""
        Обнаруженные аномалии: {len(anomalies)} шт.
        """
            for i, anomaly in enumerate(anomalies):
                context += f"  Аномалия {i+1}: {anomaly['anomaly']}\n"
        
        context += f"""
        На основе этих данных и использования моделей машинного обучения, 
        дай рекомендации по управлению устройствами Arduino.
        
        Возможные действия:
        - Включить/выключить светодиод
        - Изменить угол сервопривода
        - Запустить дополнительное измерение
        - Сообщить пользователю
        
        Ответь в формате JSON: {{"recommendations": ["рекомендация1", "рекомендация2", ...]}}
        """
        
        response = self.query_ollama(context)
        print(f"Анализ Ollama: {response}")
        
        try:
            result = json.loads(response)
            return result.get('recommendations', [])
        except json.JSONDecodeError:
            # Если JSON не удалось распарсить, возвращаем весь ответ
            return [response]
    
    def run_intelligent_system(self):
        """Запуск интеллектуальной системы с ML и Ollama"""
        self.running = True
        print("Запуск интеллектуальной системы с ML и Ollama...")
        
        # Сбор начальных данных для обучения
        print("Сбор начальных данных для обучения...")
        self.collect_data(duration_minutes=2)
        
        print("Обучение моделей машинного обучения...")
        self.train_models()
        self.train_clustering_model()
        self.train_anomaly_detection_model()
        
        print("Начало интеллектуального управления...")
        
        while self.running:
            try:
                # Считываем текущие данные
                current_data = self.read_sensors()
                
                if current_data:
                    # Сохраняем данные
                    self.data_buffer['temperature'].append(current_data['temperature'])
                    self.data_buffer['light'].append(current_data['light'])
                    self.data_buffer['timestamp'].append(current_data['timestamp'])
                    
                    print(f"Данные: T={current_data['temperature']:.2f}°C, L={current_data['light']}")
                    
                    # Обнаружение аномалий
                    anomalies = self.detect_anomalies()
                    
                    # Обнаружение изменений паттернов
                    pattern_change = self.detect_pattern_changes()
                    
                    # Предсказание
                    prediction = self.predict(look_ahead_minutes=5)
                    
                    # Анализ с помощью Ollama
                    recommendations = self.analyze_with_ollama(current_data, prediction, anomalies)
                    
                    print("Рекомендации Ollama:")
                    for rec in recommendations:
                        print(f"  - {rec}")
                    
                    # Выполнение рекомендаций
                    self.execute_recommendations(recommendations)
                    
                    # Периодическое переобучение
                    if len(self.data_buffer['temperature']) % 30 == 0:  # Каждые 30 измерений
                        print("Переобучение моделей...")
                        self.train_models()
                        self.train_clustering_model()
                        self.train_anomaly_detection_model()
                
                # Ждем 45 секунд перед следующим циклом
                time.sleep(45)
                
            except KeyboardInterrupt:
                print("\nОстановка интеллектуальной системы по запросу пользователя")
                break
    
    def execute_recommendations(self, recommendations):
        """Выполнение рекомендаций, полученных от Ollama"""
        for rec in recommendations:
            rec_lower = rec.lower()
            
            # Команды управления светодиодом
            if 'светодиод' in rec_lower or 'свет' in rec_lower:
                if 'включ' in rec_lower or 'зажги' in rec_lower:
                    print("Включение светодиода")
                    self.send_command(0x01)  # CMD_LED_ON
                elif 'выключ' in rec_lower or 'погаси' in rec_lower:
                    print("Выключение светодиода")
                    self.send_command(0x02)  # CMD_LED_OFF
            
            # Команды управления сервоприводом
            elif 'серво' in rec_lower or 'угол' in rec_lower or 'поворот' in rec_lower:
                angle_match = None
                import re
                angle_search = re.search(r'(\d+)', rec)
                if angle_search:
                    try:
                        angle = int(angle_search.group(1))
                        if 0 <= angle <= 180:
                            print(f"Установка угла сервопривода: {angle}°")
                            self.send_command(0x05, [min(180, max(0, angle))])  # CMD_SERVO_ANGLE
                    except ValueError:
                        pass
    
    def save_models(self, filepath):
        """Сохранение обученных моделей"""
        models_data = {
            'models': self.models,
            'clustering_model': self.clustering_model,
            'anomaly_model': self.anomaly_model,
            'scaler': self.scaler,
            'data_buffer': self.data_buffer
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(models_data, f)
        
        print(f"Модели сохранены в {filepath}")
    
    def load_models(self, filepath):
        """Загрузка обученных моделей"""
        with open(filepath, 'rb') as f:
            models_data = pickle.load(f)
        
        self.models = models_data['models']
        self.clustering_model = models_data['clustering_model']
        self.anomaly_model = models_data['anomaly_model']
        self.scaler = models_data['scaler']
        self.data_buffer = models_data['data_buffer']
        
        print(f"Модели загружены из {filepath}")
```

## Предсказательная аналитика и автоматизация

Создадим систему, которая может обнаруживать сложные паттерны и автоматизировать сложные сценарии:

```python
class PatternRecognitionController(AdvancedMLController):
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        super().__init__(arduino_port, baudrate, ollama_url, use_local_ollama, model)

        # Словарь с обнаруженными паттернами
        self.patterns = {
            'morning_routine': {'active': False, 'start_time': None},
            'night_mode': {'active': False, 'start_time': None},
            'high_activity': {'active': False, 'start_time': None},
            'low_activity': {'active': False, 'start_time': None}
        }

        # Пороги для разных паттернов
        self.pattern_thresholds = {
            'light_morning_threshold': 300,  # уровень света для "утреннего режима"
            'light_evening_threshold': 100,  # уровень света для "вечернего режима"
            'temp_comfort_range': (20, 26),  # комфортный диапазон температуры
            'activity_threshold': 10  # порог активности
        }
    
    def detect_daily_patterns(self):
        """Обнаружение ежедневных паттернов"""
        if len(self.data_buffer['timestamp']) < 5:
            return {}
        
        # Преобразуем временные метки в часы дня
        timestamps = list(self.data_buffer['timestamp'])
        temps = list(self.data_buffer['temperature'])
        lights = list(self.data_buffer['light'])
        
        # Определяем часы суток для последних значений
        import datetime
        current_time = datetime.datetime.fromtimestamp(timestamps[-1])
        current_hour = current_time.hour
        
        # Паттерн "утро" - высокий свет, умеренная температура
        if lights[-1] > self.pattern_thresholds['light_morning_threshold'] and current_hour < 12:
            self.patterns['morning_routine']['active'] = True
            self.patterns['morning_routine']['start_time'] = current_time
        
        # Паттерн "ночь" - низкий свет, может быть холоднее
        if lights[-1] < self.pattern_thresholds['light_evening_threshold'] and current_hour > 18:
            self.patterns['night_mode']['active'] = True
            self.patterns['night_mode']['start_time'] = current_time
        
        return self.patterns
    
    def adaptive_control(self):
        """Адаптивное управление на основе обнаруженных паттернов"""
        active_patterns = {k: v for k, v in self.patterns.items() if v['active']}
        
        if not active_patterns:
            return  # Нет активных паттернов
        
        print("Активные паттерны:")
        for pattern, info in active_patterns.items():
            print(f"  - {pattern}: с {info['start_time']}")
        
        # Применяем адаптивное управление
        current_temp = self.data_buffer['temperature'][-1] if self.data_buffer['temperature'] else 20
        current_light = self.data_buffer['light'][-1] if self.data_buffer['light'] else 300
        
        # Утренний режим - увеличиваем свет, готовимся к активности
        if self.patterns['morning_routine']['active']:
            print("Утренний режим активен")
            if current_light < self.pattern_thresholds['light_morning_threshold']:
                print("Увеличиваем освещение в утреннем режиме")
                self.send_command(0x01)  # Включить светодиод
        
        # Ночной режим - уменьшаем свет, снижаем активность
        if self.patterns['night_mode']['active']:
            print("Ночной режим активен")
            if current_light > self.pattern_thresholds['light_evening_threshold']:
                print("Снижаем освещение в ночном режиме")
                self.send_command(0x02)  # Выключить светодиод
            
            # В ночном режиме закрываем "вентиляцию" для экономии энергии
            print("Закрываем вентиляцию в ночном режиме")
            self.send_command(0x05, [0])  # Повернуть сервопривод в 0 градусов
    
    def run_pattern_detection_system(self):
        """Запуск системы обнаружения паттернов с адаптивным управлением"""
        self.running = True
        print("Запуск системы обнаружения паттернов...")
        
        # Сбор начальных данных
        print("Сбор начальных данных...")
        self.collect_data(duration_minutes=3)
        
        print("Обучение моделей...")
        self.train_models()
        self.train_clustering_model()
        self.train_anomaly_detection_model()
        
        print("Начало обнаружения паттернов и адаптивного управления...")
        
        while self.running:
            try:
                # Считываем текущие данные
                current_data = self.read_sensors()
                
                if current_data:
                    # Сохраняем данные
                    self.data_buffer['temperature'].append(current_data['temperature'])
                    self.data_buffer['light'].append(current_data['light'])
                    self.data_buffer['timestamp'].append(current_data['timestamp'])
                    
                    # Обнаружение паттернов
                    self.detect_daily_patterns()
                    
                    # Адаптивное управление
                    self.adaptive_control()
                    
                    # Обычные ML функции
                    anomalies = self.detect_anomalies()
                    prediction = self.predict(look_ahead_minutes=5)
                    
                    # Анализ Ollama
                    recommendations = self.analyze_with_ollama(current_data, prediction, anomalies)
                    
                    if recommendations:
                        print("Рекомендации Ollama:")
                        for rec in recommendations:
                            print(f"  - {rec}")
                        self.execute_recommendations(recommendations)
                
                # Периодическое переобучение и очистка паттернов
                if len(self.data_buffer['temperature']) % 50 == 0:
                    print("Переобучение моделей...")
                    self.train_models()
                    self.train_clustering_model()
                    self.train_anomaly_detection_model()
                
                # Проверяем, нужно ли сбросить какие-то паттерны
                self.reset_patterns_if_needed()
                
                # Ждем 60 секунд перед следующим циклом
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\nОстановка системы по запросу пользователя")
                break
    
    def reset_patterns_if_needed(self):
        """Сброс паттернов при определенных условиях"""
        import datetime
        
        if len(self.data_buffer['timestamp']) > 0:
            current_time = datetime.datetime.fromtimestamp(self.data_buffer['timestamp'][-1])
            current_hour = current_time.hour
            
            # Сбрасываем утренний режим после 12:00
            if self.patterns['morning_routine']['active'] and current_hour >= 12:
                self.patterns['morning_routine']['active'] = False
                print("Утренний режим завершен")
            
            # Сбрасываем ночной режим утром
            if self.patterns['night_mode']['active'] and current_hour < 6:
                self.patterns['night_mode']['active'] = False
                print("Ночной режим завершен")

# Запуск продвинутой системы
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    controller = PatternRecognitionController('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # controller = PatternRecognitionController('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")

    try:
        print("Выберите режим работы:")
        print("1. Автономная система с ML")
        print("2. Интеллектуальная система с Ollama")
        print("3. Система обнаружения паттернов")

        choice = input("Введите номер режима (1-3): ")

        if choice == "1":
            controller.run_autonomous_system()
        elif choice == "2":
            controller.run_intelligent_system()
        elif choice == "3":
            controller.run_pattern_detection_system()
        else:
            print("Неверный выбор, запуск системы обнаружения паттернов по умолчанию")
            controller.run_pattern_detection_system()
            
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    finally:
        controller.close()
```

## Интеграция с Ollama для сложного анализа

Создадим финальный класс с полной интеграцией всех возможностей:

```python
class UltimateMLController(PatternRecognitionController):
    def __init__(self, arduino_port='COM3', baudrate=9600, ollama_url="http://localhost:11434/api/generate", use_local_ollama=True, model="llama3"):
        super().__init__(arduino_port, baudrate, ollama_url, use_local_ollama, model)

        # История действий
        self.action_history = []

        # Система обратной связи
        self.feedback_enabled = True

        # Пользовательские профили
        self.user_profiles = {}
        self.current_user = "default"
    
    def learn_from_feedback(self, action, result):
        """Изучение на основе результата действия"""
        self.action_history.append({
            'action': action,
            'result': result,
            'timestamp': datetime.now().timestamp()
        })
        
        # Простой механизм изучения: если действие привело к улучшению ситуации,
        # увеличиваем вероятность его повторения в аналогичной ситуации
        if result.get('improvement', False):
            # Здесь можно добавить более сложную логику обучения
            print(f"Действие '{action}' дало положительный результат, увеличиваем его вес")
    
    def predict_user_preferences(self):
        """Предсказание предпочтений пользователя"""
        # Анализ истории действий для выявления предпочтений
        if len(self.action_history) < 5:
            return {}
        
        # Простой подсчет частых действий
        action_counts = {}
        for record in self.action_history:
            action = record['action']
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Возвращаем топ-3 наиболее частых действий
        sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        top_actions = [action for action, count in sorted_actions[:3]]
        
        return {
            'top_preferred_actions': top_actions,
            'learned_behavior': True
        }
    
    def run_complete_system(self):
        """Запуск полной системы с ML, Ollama и обучением"""
        self.running = True
        print("Запуск полной интеллектуальной системы...")
        
        # Инициализация системы
        print("Сбор начальных данных...")
        self.collect_data(duration_minutes=2)
        
        print("Обучение моделей машинного обучения...")
        self.train_models()
        self.train_clustering_model()
        self.train_anomaly_detection_model()
        
        print("Начало полного интеллектуального управления...")
        print("Система будет:")
        print("- Собирать данные с датчиков")
        print("- Обнаруживать аномалии и паттерны")
        print("- Делать предсказания")
        print("- Принимать решения с помощью Ollama")
        print("- Учиться на результатах действий")
        
        while self.running:
            try:
                # Считываем текущие данные
                current_data = self.read_sensors()
                
                if current_data:
                    # Сохраняем данные
                    self.data_buffer['temperature'].append(current_data['temperature'])
                    self.data_buffer['light'].append(current_data['light'])
                    self.data_buffer['timestamp'].append(current_data['timestamp'])
                    
                    print(f"\nТекущее состояние: T={current_data['temperature']:.2f}°C, L={current_data['light']}")
                    
                    # Обнаружение аномалий
                    anomalies = self.detect_anomalies()
                    
                    # Обнаружение паттернов
                    self.detect_daily_patterns()
                    
                    # Адаптивное управление
                    self.adaptive_control()
                    
                    # Предсказание
                    prediction = self.predict(look_ahead_minutes=5)
                    
                    # Анализ с помощью Ollama
                    recommendations = self.analyze_with_ollama(
                        current_data, prediction, anomalies
                    )
                    
                    print("Рекомендации Ollama:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"  {i}. {rec}")
                    
                    # Выполнение рекомендаций
                    for rec in recommendations:
                        action_taken = self.execute_single_recommendation(rec)
                        if action_taken:
                            # Фиксируем действие в истории
                            self.action_history.append({
                                'action': action_taken,
                                'input_data': current_data,
                                'result': 'executed',
                                'timestamp': datetime.now().timestamp()
                            })
                    
                    # Периодическое обучение
                    if len(self.data_buffer['temperature']) % 40 == 0:
                        print("\nПереобучение моделей...")
                        self.train_models()
                        self.train_clustering_model()
                        self.train_anomaly_detection_model()
                    
                    # Прогнозирование пользовательских предпочтений
                    if len(self.action_history) % 20 == 0:
                        user_prefs = self.predict_user_preferences()
                        if user_prefs.get('learned_behavior'):
                            print(f"Выявлены предпочтения пользователя: {user_prefs['top_preferred_actions']}")
                
                # Ждем 50 секунд перед следующим циклом
                time.sleep(50)
                
            except KeyboardInterrupt:
                print("\nОстановка полной системы по запросу пользователя")
                break
    
    def execute_single_recommendation(self, recommendation):
        """Выполнение одной рекомендации с возвратом выполненного действия"""
        rec_lower = recommendation.lower()
        
        # Команды управления светодиодом
        if 'светодиод' in rec_lower or 'свет' in rec_lower:
            if 'включ' in rec_lower or 'зажги' in rec_lower:
                print("Включение светодиода")
                self.send_command(0x01)  # CMD_LED_ON
                return "turn_on_led"
            elif 'выключ' in rec_lower or 'погаси' in rec_lower:
                print("Выключение светодиода")
                self.send_command(0x02)  # CMD_LED_OFF
                return "turn_off_led"
        
        # Команды управления сервоприводом
        elif 'серво' in rec_lower or 'угол' in rec_lower or 'поворот' in rec_lower:
            import re
            angle_search = re.search(r'(\d+)', recommendation)
            if angle_search:
                try:
                    angle = int(angle_search.group(1))
                    if 0 <= angle <= 180:
                        print(f"Установка угла сервопривода: {angle}°")
                        self.send_command(0x05, [min(180, max(0, angle))])  # CMD_SERVO_ANGLE
                        return f"set_servo_angle_{angle}"
                except ValueError:
                    pass
            else:
                # Если угол не указан, используем стандартное значение
                print("Поворот сервопривода (угол по умолчанию)")
                self.send_command(0x05, [45])  # CMD_SERVO_ANGLE
                return "set_servo_angle_45"
        
        return None  # Никакое действие не было выполнено

# Запуск системы
if __name__ == "__main__":
    # Использование с локальной моделью Ollama (рекомендуется)
    controller = UltimateMLController('COM3', use_local_ollama=True, model="llama3")  # Укажите правильный порт

    # Альтернатива: использование через HTTP API
    # controller = UltimateMLController('COM3', use_local_ollama=False, ollama_url="http://localhost:11434/api/generate", model="llama2")

    try:
        print("=== Полная интеллектуальная система управления ===")
        print("Система объединяет:")
        print("- Машинное обучение для анализа данных")
        print("- Обнаружение паттернов и аномалий")
        print("- Предсказательную аналитику")
        print("- Управление через Ollama")
        print("- Автоматическое обучение на результатах")

        print(f"\nОбнаруженные пороговые значения:")
        print(f"- Уровень света утром: {controller.pattern_thresholds['light_morning_threshold']}")
        print(f"- Уровень света вечером: {controller.pattern_thresholds['light_evening_threshold']}")
        print(f"- Комфортный диапазон температуры: {controller.pattern_thresholds['temp_comfort_range']}")
        
        controller.run_complete_system()
        
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        controller.close()
```

## Задание для практики

1. Установите необходимые библиотеки для машинного обучения:
   ```bash
   pip install scikit-learn numpy matplotlib
   ```

2. Создайте полный скрипт с интеграцией всех ML-компонентов

3. Запустите систему и дайте ей поработать несколько часов для сбора данных

4. Изучите, как система распознает паттерны в данных сенсоров

5. Попробуйте намеренно вызвать аномальные ситуации (например, резко изменить освещение или температуру) и наблюдайте, как система справляется с ними

6. Проанализируйте, как система учится на результатах своих действий

7. Создайте собственные алгоритмы предсказания и сравните их с встроенными

8. Попробуйте обучить персонализированные модели для разных пользователей

Поздравляем! Вы завершили все 5 уроков по созданию ИИ-агента для управления Arduino с помощью Ollama. Теперь у вас есть полноценная система, которая может:
- Устанавливать связь между Ollama и Arduino через протокол
- Управлять устройствами голосом
- Анализировать данные сенсоров с помощью машинного обучения
- Делать предсказания и автономно принимать решения
- Адаптироваться к предпочтениям пользователя