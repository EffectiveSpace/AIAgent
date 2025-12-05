# Урок 2: Создаём умную лампу с помощью ИИ-робота и Arduino 🏠💡

## Цели урока

После этого урока ты:
- Соберёшь свою первую "умную лампу" с Arduino
- Научишь ИИ-робота понимать команды для управления светом
- Создашь систему, которая включает свет при темноте
- Поймёшь, как устроены "умные дома"

## 1. Что такое "умная лампа"? 🧠

Обычная лампа включается и выключается вручную. "Умная лампа" может:
- **Автоматически** включаться и выключаться
- **ИИ-агент** может управлять ею по команде
- Она может "чувствовать" свет в комнате и включаться при необходимости

Какие умные лампы бывают в реальной жизни:
- Лампы, которые включаются при входе в комнату
- Лампы, которые светят ярко днём и тускло ночью
- Лампы, которые включаются по голосу
- Лампы, которые включаются по таймеру

## 2. Собираем умную лампу с Arduino ⚡

### Что нам понадобится:
- Плата Arduino (Uno или Nano)
- 1-2 светодиода (жёлтый и красный)
- 1 резистор (220 Ом)
- Печатная плата (breadboard)
- Провода (много!)
- Датчик освещённости (LDR или фотодиод)

### Схема подключения:
```
Arduino Uno:
- 5V → красный провод → питание на breadboard
- GND → чёрный провод → земля на breadboard
- Pin 13 → через резистор → длинная ножка светодиода → короткая ножка → GND
- Pin 12 → через резистор → другой светодиод (для автономного включения)
- A0 → датчик света (LDR) → GND, и через резистор → 5V
```

![Схема подключения умной лампы](lamp_diagram.png) *(нарисуй на бумаге или представь визуально)*

## 3. Прошивка Arduino для умной лампы 🧑‍💻

Создадим программу для Arduino, которая будет управлять светом:

```cpp
// smart_lamp.ino

// Пины
const int LIGHT_SENSOR = A0;    // Датчик освещенности
const int LED_PIN = 13;         // Главный светодиод
const int AUTO_LED_PIN = 12;    // Автоматический светодиод
const int THRESHOLD = 300;      // Порог срабатывания (0-1023)

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  pinMode(AUTO_LED_PIN, OUTPUT);
  
  digitalWrite(LED_PIN, LOW);
  digitalWrite(AUTO_LED_PIN, LOW);
  
  Serial.println("🤖 Умная лампа запущена!");
  Serial.println("Команды: 'on', 'off', 'auto_on', 'auto_off', 'status'");
}

void loop() {
  // Автоматический контроль света
  autoControlLights();
  
  // Обработка команд с компьютера
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    processCommand(command);
  }
  
  delay(100);  // Не перегружаем процессор
}

void autoControlLights() {
  int lightLevel = analogRead(LIGHT_SENSOR);
  
  // Если темно и автоматическое управление включено
  if (lightLevel < THRESHOLD && autoMode) {
    digitalWrite(AUTO_LED_PIN, HIGH);
  } else {
    digitalWrite(AUTO_LED_PIN, LOW);
  }
}

void processCommand(String command) {
  if (command == "on") {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("✅ Лампа включена по команде");
  } 
  else if (command == "off") {
    digitalWrite(LED_PIN, LOW);
    Serial.println("❌ Лампа выключена по команде");
  } 
  else if (command == "auto_on") {
    autoMode = true;
    Serial.println("🤖 Автоматический режим включён");
  } 
  else if (command == "auto_off") {
    autoMode = false;
    digitalWrite(AUTO_LED_PIN, LOW);
    Serial.println("🤖 Автоматический режим выключен");
  } 
  else if (command == "status") {
    int light = analogRead(LIGHT_SENSOR);
    int ledManual = digitalRead(LED_PIN);
    int ledAuto = digitalRead(AUTO_LED_PIN);
    
    Serial.print("📊 Статус: Свет=");
    Serial.print(light);
    Serial.print(", Ручной свет=");
    Serial.print(ledManual ? "вкл" : "выкл");
    Serial.print(", Авто свет=");
    Serial.println(ledAuto ? "вкл" : "выкл");
  } 
  else {
    Serial.println("❓ Неизвестная команда. Используй: on, off, auto_on, auto_off, status");
  }
}

bool autoMode = false;  // Режим автоматического включения
```

## 4. ИИ-агент для управления лампой 🤖

Теперь создадим ИИ-агента, который будет понимать наши команды:

```python
# smart_lamp_agent.py
import ollama
import serial
import time

class SmartLampAgent:
    def __init__(self, port='COM3'):
        self.lamp = LampController(port)
        self.auto_mode = False
        self.name = "Ламповый Робот"
        
        self.system_prompt = f"""
Ты - дружелюбный ИИ-помощник '{self.name}'! Ты управляешь умной лампой и хочешь помогать человеку.
Ты понимаешь команды вроде 'включи свет', 'выключи свет', 'автоматический режим'.
Ты отвечаешь весело, с эмоциями и хочешь помогать!
Используй инструменты для управления лампой.
"""
    
    def chat(self, user_input):
        """Обработка команд от пользователя"""
        user_input_lower = user_input.lower()
        
        # Проверяем команды управления лампой
        if 'свет' in user_input_lower or 'ламп' in user_input_lower:
            if 'вкл' in user_input_lower or 'включ' in user_input_lower:
                result = self.lamp.turn_on()
                return f"✨ Свет включён! {result}"
            elif 'выкл' in user_input_lower or 'откл' in user_input_lower:
                result = self.lamp.turn_off()
                return f"🌙 Свет выключен! {result}"
            elif 'авто' in user_input_lower or 'автомат' in user_input_lower:
                if 'вкл' in user_input_lower or 'включ' in user_input_lower:
                    result = self.lamp.auto_on()
                    self.auto_mode = True
                    return f"🤖 Автоматический режим включён! Теперь лампа будет включаться в темноте. {result}"
                elif 'выкл' in user_input_lower or 'откл' in user_input_lower:
                    result = self.lamp.auto_off()
                    self.auto_mode = False
                    return f"🤖 Автоматический режим выключен. {result}"
        
        # Обычное общение через ИИ
        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': user_input}
            ]
        )
        return response['message']['content']

class LampController:
    def __init__(self, port):
        try:
            self.ser = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Даем Arduino время на старт
            print("✅ Подключено к умной лампе")
            # Приветствие
            self.ser.write(b'status\n')
            welcome = self.ser.readline().decode().strip()
            print(f"Arduino: {welcome}")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            self.ser = None
    
    def turn_on(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'on\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def turn_off(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'off\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def auto_on(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'auto_on\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def auto_off(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'auto_off\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def get_status(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'status\n')
        response = self.ser.readline().decode().strip()
        return response

# Программа для запуска
def run_smart_lamp():
    print("🌟 Добро пожаловать в Умную Лампу с ИИ! 🌟")
    print("Подключите Arduino с умной лампой и запустите программу")
    
    agent = SmartLampAgent()  # Укажите правильный порт, если нужно
    
    print("\n🤖 Говорите с ИИ-лампой! Примеры команд:")
    print("• 'Включи свет' — включит ручной свет")
    print("• 'Выключи свет' — выключит ручной свет")
    print("• 'Включи автоматический режим' — лампа будет включаться в темноте")
    print("• 'Выключи автоматический режим' — выключит автоматику")
    print("• 'Какой свет?' — проверит статус")
    print("• 'Расскажи что умеешь' — расскажет возможности")
    print("\nЧтобы выйти, скажи 'пока' или 'стоп'\n")
    
    while True:
        try:
            user_input = input("Ты: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ['пока', 'стоп', 'выход', 'quit']:
                print("🤖 Пока! Спасибо за игру с умной лампой!")
                break
            
            response = agent.chat(user_input)
            print(f"Лампа: {response}")
            
        except KeyboardInterrupt:
            print("\n🤖 Программа остановлена. Пока!")
            break

if __name__ == "__main__":
    run_smart_lamp()
```

## 5. Делаем лампу еще умнее с ИИ! 🧠✨

ИИ может делать лампу еще умнее:

### Умный режим по времени:
```python
import datetime

def smart_time_mode(self):
    """Включает свет в зависимости от времени суток"""
    now = datetime.datetime.now()
    hour = now.hour
    
    if 7 <= hour < 22:  # День (7 утра до 10 вечера)
        brightness = "яркий"
    else:  # Ночь
        brightness = "тусклый"
    
    return f"Сейчас {hour} часов. Лампа светит {brightness}."
```

### Умный режим по присутствию:
```python
def presence_mode(self):
    """Включает свет, когда в комнате кто-то есть"""
    # Мы можем использовать датчик движения
    # и ИИ будет включать свет при обнаружении движения
    return "Свет включится, когда я замечу, что ты вошел в комнату!"
```

## 6. Игра: Угадай освещённость 🎯

Сделаем игру с нашей лампой:

```python
def play_light_game():
    """Игра 'Угадай освещённость'"""
    agent = SmartLampAgent()
    
    print("🎮 Давай поиграем! Я загадал уровень освещённости.")
    print("Угадай, сколько света в комнате (0-100, где 0 - темно, 100 - светло)!")
    print("Я буду говорить, ближе ты или дальше.\n")
    
    # Получаем настоящий уровень света
    status = agent.lamp.get_status()
    import re
    light_match = re.search(r'Свет=(\d+)', status)
    if light_match:
        actual_light = int(light_match.group(1)) * 100 // 1023  # Нормализуем к 0-100
        print(f"(Чит: настоящее освещение = {actual_light})")
    
    attempts = 0
    while True:
        try:
            guess = int(input("Твой вариант (0-100): "))
            attempts += 1
            
            difference = abs(actual_light - guess)
            
            if difference < 5:
                print(f"🎉 Потрясающе! Ты угадал! Освещение = {actual_light}")
                print(f"Ты справился за {attempts} попыток!")
                
                # Победная анимация лампы
                for _ in range(3):
                    agent.lamp.turn_on()
                    time.sleep(0.3)
                    agent.lamp.turn_off()
                    time.sleep(0.3)
                agent.lamp.turn_on()  # Оставить включенным
                break
            elif difference < 15:
                print("🔥 Горячо! Ты близко!")
            elif difference < 30:
                print("🌡️ Тепло!")
            else:
                print("❄️ Холодно!")
                
            if guess < actual_light:
                print("💡 Нужно больше света!")
            else:
                print("🌑 Нужно меньше света!")
                
        except ValueError:
            print("Введите число от 0 до 100!")
        except KeyboardInterrupt:
            print("\nИгра прервана. Пока!")
            break
```

## 7. Идеи для улучшения лампы 🚀

Вот что можно добавить в свою умную лампу:

### Цветные светодиоды:
- RGB светодиоды для цветного света
- Менять цвет в зависимости от времени
- Плавное включение и выключение (.fade)

### Датчики:
- Датчик движения - включает свет при входе
- Термометр - показывает температуру цветом
- Микрофон - реагирует на хлопки

### ИИ-улучшения:
- Учить лампу предпочтениям пользователя
- Умные расписания освещения
- Игры и развлечения с лампой

## 8. Безопасность и уважение к пользователям 🛡️

Важно помнить:
- Не включать свет слишком ярко внезапно (может испугать)
- Давать пользователю контроль над всем
- Уважать приватность (не записывать голос без разрешения)
- Делать всё понятным и безопасным

## 9. Демонстрация проекта 📹

Когда закончишь проект:
1. Сними видео, как работает твоя лампа
2. Расскажи, что ты сделал
3. Покажи, как она реагирует на команды
4. Поделись своими идеями для улучшения

## 10. Реальные аналоги 🏠

В реальных "умных домах" есть такие же лампы:
- Philips Hue
- Xiaomi Yeelight
- IKEA TRÅDFRI
- Яндекс.Станция управляет светом

Но твоя лампа особенная - ты её сам сделал! 💪🌟

---
**Поздравляешь!** Ты создал настоящую умную лампу с ИИ-управлением! Ты понял, как работает "умный дом", и сделал его сам. Продолжай экспериментировать и улучшать свою лампу!