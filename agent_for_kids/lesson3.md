# Урок 3: Умный дом с ИИ-роботом: Свет, температура и безопасность 🏠🤖

## Цели урока

После этого урока ты:
- Создашь простую систему "умного дома" с Arduino
- Добавишь датчики температуры и движения
- Научишь ИИ-робота следить за безопасностью дома
- Понимаешь, как работают настоящие умные дома

## 1. Что такое "умный дом"? 🧠

"Умный дом" - это дом, который:
- **Сам** включает свет, когда темнеет
- **Сам** регулирует температуру
- **Сам** следит за безопасностью
- **Слушает** команды человека
- **Помогает** в повседневных делах

Какие умные дома бывают:
- Управление освещением по расписанию
- Контроль температуры и влажности
- Уведомления о дверях и окнах
- Автоматический полив растений
- Системы безопасности

## 2. Собираем систему умного дома 🏗️

### Что понадобится:
- Arduino (Uno или Nano)
- Датчик температуры (DS18B20, TMP36 или DHT11)
- Датчик движения (PIR HC-SR501)
- Светодиоды (разных цветов)
- Сервопривод (для "замка")
- Буззер (для звука)
- Печатная плата, резисторы, провода

### Схема умного дома:
```
Arduino Uno:
- 5V/GND: питание всей системы
- Pin 2: Датчик движения → через резистор
- Pin A0: Датчик температуры → аналоговый вход
- Pin 13: Светодиод безопасности
- Pin 12: Светодиод температуры
- Pin 11: Управление сервомотором (дверной замок)
- Pin 10: Буззер (звуковой сигнал)
```

## 3. Прошивка Arduino для умного дома 🔧

```cpp
// smart_home_system.ino

#include <Servo.h>  // для управления сервомотором

// Пины
const int MOTION_SENSOR = 2;      // Датчик движения
const int TEMP_SENSOR = A0;       // Датчик температуры
const int SECURITY_LED = 13;      // Светодиод безопасности
const int TEMP_LED = 12;          // Светодиод температуры
const int SERVO_PIN = 11;         // Сервомотор (замок)
const int BUZZER = 10;            // Звуковой сигнал

// Параметры
const int TEMP_THRESHOLD_HIGH = 28;  // Температура, выше которой срабатывает сигнализация
const int TEMP_THRESHOLD_LOW = 18;   // Температура, ниже которой срабатывает обогрев
const int MOTION_DETECTION_DELAY = 5000; // Задержка перед повторным обнаружением движения

Servo doorLock;  // Сервомотор для замка

unsigned long lastMotionTime = 0;
bool alarmActive = false;
bool autoDoorLock = true;

void setup() {
  Serial.begin(9600);
  
  // Настройка пинов
  pinMode(MOTION_SENSOR, INPUT);
  pinMode(SECURITY_LED, OUTPUT);
  pinMode(TEMP_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  
  // Подключение сервомотора
  doorLock.attach(SERVO_PIN);
  doorLock.write(90);  // Замок в открытом состоянии по умолчанию
  
  // Инициализация
  digitalWrite(SECURITY_LED, LOW);
  digitalWrite(TEMP_LED, LOW);
  noTone(BUZZER);
  
  Serial.println("🏠 Умный дом запущен!");
  Serial.println("Команды: 'lock_door', 'unlock_door', 'check_temp', 'check_motion', 'alarm_on', 'alarm_off', 'status'");
}

void loop() {
  // Читаем команды с компьютера
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    processCommand(command);
  }
  
  // Проверяем датчик движения
  checkMotionSensor();
  
  // Проверяем температуру
  checkTemperature();
  
  delay(100);
}

void processCommand(String command) {
  if (command == "lock_door") {
    lockDoor();
    Serial.println("🔒 Дверь заперта");
  }
  else if (command == "unlock_door") {
    unlockDoor();
    Serial.println("🔓 Дверь отперта");
  }
  else if (command == "check_temp") {
    float temp = getTemperature();
    Serial.print("🌡️ Температура: ");
    Serial.print(temp);
    Serial.println("°C");
  }
  else if (command == "check_motion") {
    int motion = digitalRead(MOTION_SENSOR);
    Serial.print("👀 Движение: ");
    Serial.println(motion ? "обнаружено" : "нет");
  }
  else if (command == "alarm_on") {
    alarmActive = true;
    Serial.println("🚨 Сигнализация включена");
  }
  else if (command == "alarm_off") {
    alarmActive = false;
    noTone(BUZZER);
    Serial.println("✅ Сигнализация выключена");
  }
  else if (command == "status") {
    printSystemStatus();
  }
  else {
    Serial.println("❓ Неизвестная команда. Используй: lock_door, unlock_door, check_temp, check_motion, alarm_on, alarm_off, status");
  }
}

void checkMotionSensor() {
  int motionDetected = digitalRead(MOTION_SENSOR);
  
  if (motionDetected) {
    unsigned long currentTime = millis();
    
    // Проверяем, не было ли недавно срабатывания
    if (currentTime - lastMotionTime > MOTION_DETECTION_DELAY) {
      Serial.println("⚠️ Обнаружено движение!");
      digitalWrite(SECURITY_LED, HIGH);
      lastMotionTime = currentTime;
      
      // Если сигнализация включена, подаём звук
      if (alarmActive) {
        tone(BUZZER, 1000);
        delay(1000);
        noTone(BUZZER);
      }
    }
  } else {
    // Если движения нет, выключаем светодиод безопасности
    digitalWrite(SECURITY_LED, LOW);
  }
}

void checkTemperature() {
  float temp = getTemperature();
  
  // Управляем светодиодом температуры
  if (temp > TEMP_THRESHOLD_HIGH) {
    digitalWrite(TEMP_LED, HIGH);
    Serial.println("🌡️ Внимание! Температура выше нормы!");
  } else if (temp < TEMP_THRESHOLD_LOW) {
    digitalWrite(TEMP_LED, HIGH);
    Serial.println("🌡️ Внимание! Температура ниже нормы!");
  } else {
    digitalWrite(TEMP_LED, LOW);
  }
  
  // Автоматическая блокировка двери при высокой температуре
  if (temp > TEMP_THRESHOLD_HIGH + 5 && autoDoorLock) {
    lockDoor();
    Serial.println("🔒 Дверь автоматически заблокирована из-за высокой температуры!");
  }
}

float getTemperature() {
  int sensorValue = analogRead(TEMP_SENSOR);
  // Преобразуем значение в температуру (для TMP36)
  // Формула: (значение * 5.0 / 1024.0 - 0.5) * 100
  float voltage = sensorValue * 5.0 / 1024.0;
  float temperature = (voltage - 0.5) * 100;
  return temperature;
}

void lockDoor() {
  doorLock.write(0);  // Закрываем замок
}

void unlockDoor() {
  doorLock.write(90); // Открываем замок
}

void printSystemStatus() {
  float temp = getTemperature();
  int motion = digitalRead(MOTION_SENSOR);
  
  Serial.println("--- 🏠 Статус умного дома ---");
  Serial.print("Температура: ");
  Serial.print(temp);
  Serial.println("°C");
  
  Serial.print("Движение: ");
  Serial.println(motion ? "обнаружено" : "нет");
  
  Serial.print("Сигнализация: ");
  Serial.println(alarmActive ? "вкл" : "выкл");
  
  Serial.print("Замок: ");
  Serial.println(doorLock.read() == 0 ? "заперт" : "открыт");
  
  Serial.print("Время с последнего движения: ");
  Serial.print((millis() - lastMotionTime) / 1000);
  Serial.println(" сек");
  Serial.println("-----------------------------");
}
```

## 4. ИИ-робот для управления умным домом 🤖

```python
# smart_home_agent.py
import ollama
import serial
import time

class SmartHomeAgent:
    def __init__(self, port='COM3'):
        self.home = SmartHomeController(port)
        self.name = "Умный Дом Робот"
        
        self.system_prompt = f"""
Ты - {self.name}, добрый ИИ-помощник для умного дома! Ты следишь за домом и хочешь помочь человеку.
Ты управляешь светом, температурой, безопасностью и дверными замками.
Ты говоришь весело, с эмоциями, и хочешь помочь!
Используй инструменты для управления умным домом.
Отвечай на русском языке.
"""
    
    def respond_to_user(self, user_input):
        """Реагирует на команды пользователя"""
        user_input_lower = user_input.lower()
        
        # Команды для управления домом
        if 'температура' in user_input_lower or 'тепло' in user_input_lower or 'жарко' in user_input_lower or 'холодно' in user_input_lower:
            temp_result = self.home.check_temperature()
            return f"🌡️ Текущая температура в доме: {temp_result}. Я следлю за температурой и включу сигнал, если станет слишком жарко или холодно!"
        
        elif 'движение' in user_input_lower or 'кто' in user_input_lower or 'доме' in user_input_lower:
            motion_result = self.home.check_motion()
            if 'обнаружено' in motion_result:
                return f"👀 Я вижу, что в доме кто-то есть! {motion_result}. Все в порядке? Хочешь, я включу свет?"
            else:
                return f"🏠 В доме никого нет. {motion_result}. Спокойствие и порядок!"
        
        elif 'дверь' in user_input_lower or 'замок' in user_input_lower:
            if 'запер' in user_input_lower or 'закрой' in user_input_lower:
                lock_result = self.home.lock_door()
                return f"🔒 Я запер дверь! {lock_result}. Теперь дом в безопасности!"
            elif 'откр' in user_input_lower or 'отпер' in user_input_lower:
                unlock_result = self.home.unlock_door()
                return f"🔓 Я открыл дверь! {unlock_result}. Добро пожаловать домой!"
        
        elif 'сигнал' in user_input_lower or 'сирен' in user_input_lower or 'аварий' in user_input_lower:
            if 'вкл' in user_input_lower or 'включ' in user_input_lower:
                alarm_result = self.home.alarm_on()
                return f"🚨 Сигнализация включена! {alarm_result}. Я буду следить за безопасностью!"
            elif 'выкл' in user_input_lower or 'отключ' in user_input_lower:
                alarm_result = self.home.alarm_off()
                return f"✅ Сигнализация выключена! {alarm_result}. Спокойная ночь!"
        
        elif 'статус' in user_input_lower or 'дом' in user_input_lower:
            status_result = self.home.get_status()
            return f"🏠 Вот статус твоего умного дома:\n{status_result}"
        
        # Обычное общение через ИИ
        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': user_input}
            ]
        )
        return response['message']['content']

class SmartHomeController:
    def __init__(self, port):
        try:
            self.ser = serial.Serial(port, 9600, timeout=2)
            time.sleep(2)  # Время на старт Arduino
            print("✅ Подключено к умному дому")
            
            # Приветствие
            self.ser.write(b'status\n')
            welcome = self.ser.readline().decode().strip()
            print(f"Arduino: {welcome}")
            
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            self.ser = None
    
    def check_temperature(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'check_temp\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def check_motion(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'check_motion\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def lock_door(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'lock_door\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def unlock_door(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'unlock_door\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def alarm_on(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'alarm_on\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def alarm_off(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'alarm_off\n')
        response = self.ser.readline().decode().strip()
        # Также выключаем звук в Arduino
        return response
    
    def get_status(self):
        if not self.ser:
            return "Arduino не подключена!"
        self.ser.write(b'status\n')
        # Статус может занимать несколько строк
        status_lines = []
        for _ in range(8):  # Читаем 8 строк статуса
            line = self.ser.readline().decode().strip()
            if line:
                status_lines.append(line)
        return "\n".join(status_lines)

# Программа запуска
def run_smart_home():
    print("🏠 Добро пожаловать в систему Умного Дома с ИИ! 🏠")
    print("Подключите Arduino с системой умного дома и запустите программу")
    
    agent = SmartHomeAgent()  # Укажите правильный порт
    
    print("\n🤖 Говорите с ИИ-помощником умного дома! Примеры команд:")
    print("• 'Какая температура в доме?' — проверит температуру")
    print("• 'Закрой дверь' — запрёт дверь")
    print("• 'Открой дверь' — отпёрт дверь")
    print("• 'Есть ли движение в доме?' — проверит датчик движения")
    print("• 'Включи сигнализацию' — включит охранную систему")
    print("• 'Выключи сигнализацию' — выключит сигнализацию")
    print("• 'Покажи статус дома' — покажет все показатели")
    print("\nЧтобы выйти, скажи 'пока' или 'стоп'\n")
    
    while True:
        try:
            user_input = input("Ты: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ['пока', 'стоп', 'выйти', 'quit']:
                print("🤖 Пока! Береги свой умный дом!")
                break
            
            response = agent.respond_to_user(user_input)
            print(f"Умный Дом: {response}")
            
        except KeyboardInterrupt:
            print("\n🤖 Программа остановлена. Пока!")
            break

if __name__ == "__main__":
    run_smart_home()
```

## 5. Игра: Защити свой дом 🛡️🎮

Сделаем игру, где ты должен защитить свой виртуальный дом:

```python
def play_home_defense_game():
    """Игра 'Защити свой дом'"""
    agent = SmartHomeAgent()
    
    print("🏰 Игра: Защити свой дом!")
    print("Ты - хозяин умного дома. Твоя задача - следить за безопасностью и комфортной температурой.")
    print("Ты получишь уведомления о событиях и должен принять правильные решения.\n")
    
    score = 0
    game_round = 1
    
    events = [
        ("Температура в доме поднялась до 30°C!", "Требуется: понизить температуру", "Решение: вентилятор или кондиционер"),
        ("Обнаружено движение в доме!", "Требуется: проверить, кто это", "Решение: включить камеры или свет"),
        ("Температура опустилась до 10°C!", "Требуется: повысить температуру", "Решение: включить обогреватель"),
        ("Кто-то пытается открыть дверь!", "Требуется: проверить и при необходимости заблокировать", "Решение: проверить через камеру")
    ]
    
    for i in range(5):  # 5 раундов игры
        print(f"\n--- Раунд {game_round} ---")
        import random
        event = random.choice(events)
        
        print(f"🚨 СОБЫТИЕ: {event[0]}")
        print(f"💡 {event[1]}")
        
        action = input("Что ты будешь делать? ").lower()
        
        if 'температура' in event[0] and ('повыс' in action or 'пониз' in action or 'гре' in action or 'холод' in action):
            score += 10
            print(f"✅ Правильно! {event[2]}")
        elif 'движение' in event[0] and ('провер' in action or 'свет' in action or 'камер' in action):
            score += 10
            print(f"✅ Правильно! {event[2]}")
        elif 'дверь' in event[0] and ('провер' in action or 'камер' in action or 'заблок' in action):
            score += 10
            print(f"✅ Правильно! {event[2]}")
        else:
            print(f"🤔 Возможно, ты мог бы сделать что-то лучше. {event[2]}")
        
        game_round += 1
        time.sleep(1)
    
    print(f"\n🏆 Игра окончена! Твой счёт: {score}/50 баллов")
    if score >= 40:
        print("🎉 Отлично! Ты настоящий защитник дома!")
    elif score >= 20:
        print("👍 Неплохо! Ты уже хорошо разбираешься в безопасности!")
    else:
        print("📚 Практикуйся больше, и ты станешь настоящим экспертом по умным домам!")
    
    # Награда: включить свет в доме
    print("\n🎁 За хорошую игру - я включу свет в твоём виртуальном доме!")
    agent.home.check_temperature()  # Показать статус
```

## 6. Добавляем больше ума в дом 🧠✨

### Умный режим экономии энергии:
```python
def energy_saving_mode(self):
    """Режим экономии энергии"""
    # Снижает яркость света ночью
    # Отключает неиспользуемые устройства
    # Оптимизирует температуру
    return "Режим экономии энергии включён! Я буду использовать энергию эффективнее!"
```

### Умный график дня:
```python
def daily_schedule(self):
    """Следит за расписанием"""
    # Утром включает свет
    # Днём следит за температурой
    # Вечером создаёт уютную атмосферу
    # Ночью включает охрану
    return "Я слежу за твоим расписанием и делаю дом комфортным в любое время суток!"
```

## 7. Безопасность в умном доме 🔒

Важно понимать:
- Не все устройства должны управляться удалённо
- Нужно подтверждение важных действий
- Должна быть возможность быстро отключить всё
- Нужно уважать приватность

### Пример системы подтверждения:
```python
def secure_action(self, action):
    """Безопасное выполнение важных действий"""
    print(f"⚠️ Подтверждение: Ты действительно хочешь {action}? (да/нет)")
    confirmation = input().lower()
    if confirmation in ['да', 'yes', 'y']:
        return True
    else:
        print("❌ Действие отменено.")
        return False
```

## 8. Идеи для улучшения дома 🚀

- Добавить голосовое управление
- Подключить интернет для удалённого контроля
- Добавить календарь событий
- Сделать мобильное приложение
- Добавить умную покупку продуктов

## 9. Что дальше? 🌟

В следующих уроках ты:
- Создашь робота-помощника на Arduino
- Добавишь голосовое управление
- Сделаешь систему умного полива
- Создашь игры с физическими устройствами

## 10. Реальные умные дома 🏢

Настоящие умные дома включают:
- Amazon Alexa и Echo
- Google Home
- Apple HomeKit
- Samsung SmartThings
- Xiaomi Aqara

Но твой дом особенный - ты его сам сделал! 💪🌟

---
**Поздравляем!** Ты создал настоящую систему умного дома с ИИ-управлением! Теперь ты понимаешь, как работают умные устройства, которые окружают нас в повседневной жизни. Продолжай экспериментировать и улучшать свой дом!