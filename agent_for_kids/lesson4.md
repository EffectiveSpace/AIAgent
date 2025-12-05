# Урок 4: Робот-помощник и игры с ИИ и Arduino 🤖🎮

## Цели урока

После этого урока ты:
- Создашь робота-помощника на Arduino с сервомоторами и сенсорами
- Научишь ИИ говорить через Arduino (голосовые команды)
- Создашь несколько игровых проектов с физическими устройствами
- Поймёшь, как устроены настоящие роботы

## 1. Знакомство с роботами 🤖

Робот - это устройство, которое:
- **Воспринимает** мир через сенсоры (видит, слышит, чувствует)
- **Думает** (обрабатывает информацию)
- **Действует** (двигается, говорит, включает/выключает)

Виды роботов:
- Промышленные (на заводах)
- Домашние (пылесосы, помощники)
- Медицинские
- Игрушечные
- Исследовательские

Наш робот-помощник будет:
- Узнавать команды
- Поворачивать глаза/голову
- Включать свет
- "Говорить" через звук
- Играть с тобой!

## 2. Собираем робота-помощника 🏗️

### Что понадобится:
- Arduino Uno
- 2-3 сервомотора (для движущихся частей)
- Ультразвуковой датчик (HC-SR04 - для "зрения")
- Датчик расстояния
- Пьезоизлучатель (для "речи")
- Светодиоды (разных цветов)
- Кнопки
- Печатная плата, резисторы, провода
- Материалы для корпуса (картон, пластик, 3D-печать)

### Схема робота-помощника:
```
Arduino Uno:
- 5V/GND: общее питание
- Pin 9: Серво-мотор для "глаз" (головы)
- Pin 10: Серво-мотор для "руки"
- Pin 11: Пьезоизлучатель (речь)
- Pin 12: Светодиод "глаз"
- Pin 2: Ультразвуковой датчик (Trig)
- Pin 3: Ультразвуковой датчик (Echo)
- Pin 4: Кнопка для активации
```

## 3. Прошивка Arduino для робота-помощника 🔧

```cpp
// robot_helper.ino
#include <Servo.h>

// Пины
const int EYE_SERVO_PIN = 9;      // Серво для глаз/головы
const int ARM_SERVO_PIN = 10;     // Серво для руки
const int BUZZER_PIN = 11;        // "Голос" робота
const int EYE_LED_PIN = 12;       // "Глаз" робота
const int TRIG_PIN = 2;           // Ультразвук Trig
const int ECHO_PIN = 3;           // Ультразвук Echo
const int BUTTON_PIN = 4;         // Кнопка активации

// Объекты
Servo eyeServo;
Servo armServo;

// Переменные
long duration;
int distance;

void setup() {
  Serial.begin(9600);
  
  // Настройка серво
  eyeServo.attach(EYE_SERVO_PIN);
  armServo.attach(ARM_SERVO_PIN);
  
  // Установка начальных позиций
  eyeServo.write(90);  // Глаза в центр
  armServo.write(0);   // Рука опущена
  
  // Пины
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(EYE_LED_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Инициализация
  digitalWrite(EYE_LED_PIN, HIGH);
  delay(1000);
  digitalWrite(EYE_LED_PIN, LOW);
  
  Serial.println("🤖 Робот-помощник запущен!");
  Serial.println("Команды: 'look_around', 'wave_hand', 'speak', 'detect_obstacle', 'sleep', 'wake_up', 'dance'");
}

void loop() {
  // Проверяем команды
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    processCommand(command);
  }
  
  // Делаем периодические действия
  if (millis() % 10000 < 50) {  // Каждые 10 секунд смотрим вперед
    lookForward();
  }
  
  delay(100);
}

void processCommand(String command) {
  if (command == "look_around") {
    lookAround();
    Serial.println("👀 Оглядываюсь вокруг!");
  }
  else if (command == "wave_hand") {
    waveHand();
    Serial.println("👋 Машу рукой!");
  }
  else if (command == "speak") {
    speak();
    Serial.println("📢 Привет! Я робот-помощник!");
  }
  else if (command == "detect_obstacle") {
    detectObstacle();
  }
  else if (command == "sleep") {
    sleepMode();
    Serial.println("😴 Робот спит...");
  }
  else if (command == "wake_up") {
    wakeUp();
    Serial.println("😴 Робот просыпается...");
  }
  else if (command == "dance") {
    dance();
    Serial.println("🕺 Танцую!");
  }
  else {
    Serial.println("❓ Неизвестная команда. Используй: look_around, wave_hand, speak, detect_obstacle, sleep, wake_up, dance");
  }
}

void lookAround() {
  // Поворот глаз от 30 до 150 градусов
  for (int pos = 30; pos <= 150; pos += 1) {
    eyeServo.write(pos);
    delay(15);
  }
  for (int pos = 150; pos >= 30; pos -= 1) {
    eyeServo.write(pos);
    delay(15);
  }
  eyeServo.write(90); // Вернуть в центр
}

void lookForward() {
  eyeServo.write(90);
}

void waveHand() {
  // Поднятие руки и махание
  for (int i = 0; i < 3; i++) {
    armServo.write(90);  // Поднять руку
    delay(500);
    armServo.write(0);   // Опустить руку
    delay(500);
  }
  armServo.write(0); // Рука опущена
}

void speak() {
  // "Говорит" через пьезоизлучатель
  tone(BUZZER_PIN, 1000, 500);
  delay(1000);
  tone(BUZZER_PIN, 1200, 300);
  delay(500);
  tone(BUZZER_PIN, 1500, 200);
}

void detectObstacle() {
  // Запуск ультразвукового датчика
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;
  
  Serial.print("📏 Объект на расстоянии: ");
  Serial.print(distance);
  Serial.println(" см");
  
  if (distance < 20) {
    Serial.println("⚠️ Обнаружен объект рядом!");
    digitalWrite(EYE_LED_PIN, HIGH);
    tone(BUZZER_PIN, 2000, 300);
  } else {
    digitalWrite(EYE_LED_PIN, LOW);
  }
}

void sleepMode() {
  // Режим сна: выключает глаза, опускает голову
  digitalWrite(EYE_LED_PIN, LOW);
  eyeServo.write(180); // Наклонить голову вниз
  armServo.write(0);   // Руку опустить
  noTone(BUZZER_PIN);
}

void wakeUp() {
  // Режим бодрствования: включает глаза, поднимает голову
  digitalWrite(EYE_LED_PIN, HIGH);
  eyeServo.write(90); // Голову в центр
  armServo.write(0);  // Рука опущена
}

void dance() {
  // Простой "танец": движение глаз и руки
  for (int i = 0; i < 5; i++) {
    eyeServo.write(60);
    armServo.write(90);
    tone(BUZZER_PIN, 1000, 200);
    delay(300);
    
    eyeServo.write(120);
    armServo.write(0);
    tone(BUZZER_PIN, 1500, 200);
    delay(300);
  }
  
  eyeServo.write(90);
  armServo.write(0);
}

String getStatus() {
  detectObstacle();
  String status = "Статус робота:";
  status += "\nГлаза: ";
  status += digitalRead(EYE_LED_PIN) ? "открыты" : "закрыты";
  status += "\nРука: ";
  status += armServo.read() == 0 ? "опущена" : "поднята";
  status += "\nОбъект рядом: ";
  status += distance < 20 ? "да" : "нет";
  return status;
}
```

## 4. ИИ-робот с голосом и действиями 🧠Voice

```python
# ai_robot_helper.py
import ollama
import serial
import time

class AIRobotHelper:
    def __init__(self, port='COM3'):
        self.robot = RobotController(port)
        self.name = "РобоПомощник"
        
        self.system_prompt = f"""
Ты - {self.name}, добрый и весёлый робот-помощник! Ты любишь помогать людям и играть!
Ты хочешь быть полезным и весёлым другом!
Ты можешь управлять физическими действиями: смотреть, махать рукой, говорить, танцевать.
Ты говоришь радостно, с эмоциями, и хочешь играть!
Используй инструменты для управления роботом.
Отвечай на русском языке.
"""
    
    def respond_to_user(self, user_input):
        """Реагирует на команды пользователя"""
        user_input_lower = user_input.lower()
        
        # Команды для управления роботом
        if 'посмотри' in user_input_lower or 'глаз' in user_input_lower or 'осмотр' in user_input_lower:
            result = self.robot.look_around()
            return f"👀 Я осмотрелся! {result}"
        
        elif 'махай' in user_input_lower or 'рука' in user_input_lower or 'привет' in user_input_lower:
            result = self.robot.wave_hand()
            return f"👋 Привет! Я помахал рукой! {result}"
        
        elif 'говори' in user_input_lower or 'голос' in user_input_lower or 'привет' in user_input_lower:
            result = self.robot.speak()
            return f"📢 {result}"
        
        elif 'танц' in user_input_lower or 'пляш' in user_input_lower or 'весел' in user_input_lower:
            result = self.robot.dance()
            return f"🕺 Танцую! {result}"
        
        elif 'спи' in user_input_lower or 'сон' in user_input_lower:
            result = self.robot.sleep_mode()
            return f"😴 Ложусь спать! {result}"
        
        elif 'проснись' in user_input_lower or 'вставай' in user_input_lower:
            result = self.robot.wake_up()
            return f"😊 Просыпаюсь! {result}"
        
        elif 'объект' in user_input_lower or 'рядом' in user_input_lower or 'датчик' in user_input_lower:
            result = self.robot.detect_obstacle()
            return f"📏 {result}"
        
        elif 'статус' in user_input_lower or 'робот' in user_input_lower:
            result = self.robot.get_status()
            return f"🤖 Вот статус моего робота-помощника:\n{result}"

        # Обычное общение через ИИ
        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': user_input}
            ]
        )
        return response['message']['content']

class RobotController:
    def __init__(self, port):
        try:
            self.ser = serial.Serial(port, 9600, timeout=2)
            time.sleep(2)  # Время на старт Arduino
            print("✅ Подключено к роботу-помощнику")
            
            # Приветствие
            self.ser.write(b'status\n')
            welcome = self.ser.readline().decode().strip()
            print(f"Arduino: {welcome}")
            
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            self.ser = None
    
    def look_around(self):
        if not self.ser:
            return "Робот не подключен!"
        self.ser.write(b'look_around\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def wave_hand(self):
        if not self.ser:
            return "Робот не подключен!"
        self.ser.write(b'wave_hand\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def speak(self):
        if not self.ser:
            return "Робот не подключен!"
        self.ser.write(b'speak\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def dance(self):
        if not self.ser:
            return "Робот не подключен!"
        self.ser.write(b'dance\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def sleep_mode(self):
        if not self.ser:
            return "Робот не подключен!"
        self.ser.write(b'sleep\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def wake_up(self):
        if not self.ser:
            return "Робот не подключен!"
        self.ser.write(b'wake_up\n')
        response = self.ser.readline().decode().strip()
        return response
    
    def detect_obstacle(self):
        if not self.ser:
            return "Робот не подключен!"
        self.ser.write(b'detect_obstacle\n')
        responses = []
        for _ in range(2):  # Читаем 2 строки: расстояние и обнаружение
            line = self.ser.readline().decode().strip()
            responses.append(line)
        return " ".join(responses)
    
    def get_status(self):
        if not self.ser:
            return "Робот не подключен!"
        self.ser.write(b'status\n')
        time.sleep(0.5)  # Даем время для формирования статуса
        
        status_lines = []
        for _ in range(4):  # Читаем строки статуса
            line = self.ser.readline().decode().strip()
            if line:
                status_lines.append(line)
        return "\n".join(status_lines)

# Программа запуска
def run_robot_helper():
    print("🤖 Добро пожаловать к Роботу-Помощнику! 🤖")
    print("Подключите Arduino с роботом и запустите программу")
    
    agent = AIRobotHelper()  # Укажите правильный порт
    
    print("\n🤖 Говорите с Роботом-Помощником! Примеры команд:")
    print("• 'Посмотри вокруг' — робот поворачивает глаза/голову")
    print("• 'Помахай рукой' — робот машет рукой")
    print("• 'Поговори со мной' — робот издает звуки")
    print("• 'Потанцуй!' — робот танцует")
    print("• 'Ложись спать' — робот переходит в спящий режим")
    print("• 'Просыпайся' — робот просыпается")
    print("• 'Есть ли кто рядом?' — робот проверяет датчик")
    print("• 'Покажи статус' — покажет состояние робота")
    print("\nЧтобы выйти, скажи 'пока' или 'стоп'\n")
    
    while True:
        try:
            user_input = input("Ты: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ['пока', 'стоп', 'выйти', 'quit']:
                print("🤖 Пока! Спасибо за общение!")
                break
            
            response = agent.respond_to_user(user_input)
            print(f"Робот: {response}")
            
        except KeyboardInterrupt:
            print("\n🤖 Программа остановлена. Пока!")
            break

if __name__ == "__main__":
    run_robot_helper()
```

## 5. Игра: Угадай, что делает робот 🎮

```python
def play_robot_guess_game():
    """Игра 'Угадай, что делает робот'"""
    agent = AIRobotHelper()
    
    print("🎮 Игра: Угадай, что делает робот!")
    print("Я буду делать разные действия с роботом, а ты угадай, что я делаю.")
    print("Варианты: смотрит, машет, говорит, танцует, спит")
    print("У тебя 3 попытки на каждое действие!\n")
    
    actions = [("посмотри вокруг", "смотреть"), 
               ("помахай", "махать"), 
               ("поговори", "говорить"), 
               ("потанцуй", "танцевать"), 
               ("пошли спать", "спать")]
    
    score = 0
    total = len(actions)
    
    for action_cmd, action_name in actions:
        print(f"\n--- Раунд: {action_name} ---")
        
        # Случайно выполняем действие
        import random
        chosen_action = random.choice(actions)
        agent.robot.look_around() if "смотреть" in chosen_action[1] else None
        agent.robot.wave_hand() if "махать" in chosen_action[1] else None
        agent.robot.speak() if "говорить" in chosen_action[1] else None
        agent.robot.dance() if "танцевать" in chosen_action[1] else None
        agent.robot.sleep_mode() if "спать" in chosen_action[1] else None
        
        for attempt in range(3):
            guess = input(f"Попытка {attempt + 1}. Что делает робот? ").lower()
            
            if action_name in guess:
                print("🎉 Правильно!")
                score += (3 - attempt)  # Больше очков за меньшее число попыток
                break
            else:
                print("❌ Неправильно.")
                if attempt < 2:
                    print("Попробуй еще раз!")
        
        if action_name not in input().lower():  # Печатаем правильный ответ, если не угадал за 3 попытки
            print(f"Правильный ответ: {action_name}")
    
    print(f"\n🏆 Игра окончена! Твой счёт: {score}/{total * 3} баллов")
    if score >= total * 3 * 0.7:
        print("🎉 Отлично! Ты настоящий эксперт по роботам!")
    elif score >= total * 3 * 0.4:
        print("👍 Хорошо! Ты многое знаешь о роботах!")
    else:
        print("📚 Тренируйся больше, и ты станешь профи по роботам!")
```

## 6. Игра: Робот-охранник 🛡️

```python
def play_guard_robot_game():
    """Игра 'Робот-охранник'"""
    agent = AIRobotHelper()
    
    print("🤖 Игра: Робот-охранник!")
    print("Робот-помощник теперь охранник. Он должен обнаруживать объекты и реагировать.")
    print("Когда робот обнаруживает 'предмет' (ты имитируешь), он должен сработать.")
    print("Ты будешь подставлять предмет перед датчиком, а я скажу, заметил ли робот.\n")
    
    print("Начинаем тренировку охранника...")
    time.sleep(2)
    
    correct_detections = 0
    total_checks = 5
    
    for i in range(total_checks):
        print(f"\nПроверка {i + 1} из {total_checks}: Подставь что-нибудь перед робота!")
        input("Нажми Enter, когда сделаешь...")
        
        # Проверяем, обнаружил ли робот
        result = agent.robot.detect_obstacle()
        print(f"Робот проверил: {result}")
        
        if "обнаружен" in result or "см" in result.split()[:3]:  # грубо проверяем результат
            distance_str = [s for s in result.split() if "см" in s]
            if distance_str and float(distance_str[0].replace("см", "")) < 20:
                print("🤖 Робот заметил! Правильная реакция!")
                correct_detections += 1
            else:
                print("🤖 Робот не заметил объект. Попробуй ближе.")
        else:
            print("🤖 Робот не сработал. Попробуй еще раз.")
    
    print(f"\n🏆 Тренировка окончена! Робот правильно обнаружил {correct_detections}/{total_checks} объектов")
    
    if correct_detections == total_checks:
        print("🥇 Отлично! Твой робот-охранник лучший!")
    elif correct_detections >= total_checks * 0.7:
        print("🥈 Хорошо! Робот неплохо справляется!")
    else:
        print("🥉 Тренируй робота дальше, и он станет отличным охранником!")
```

## 7. Робот-рассказчик 📖

Сделаем робота, который может рассказывать истории:

```python
def robot_storyteller():
    """Робот-рассказчик"""
    agent = AIRobotHelper()
    
    print("📖 Робот-рассказчик!") 
    print("Я буду рассказывать тебе истории, а робот будет их сопровождать действиями.")
    print("Например, когда в истории что-то происходит, робот будет реагировать!")
    
    story_elements = [
        ("Жил-был робот", lambda: agent.robot.look_around()),
        ("Он любил всех встречных", lambda: agent.robot.wave_hand()),
        ("Он мог говорить", lambda: agent.robot.speak()),
        ("И даже танцевать", lambda: agent.robot.dance()),
        ("Однажды он пошёл спать", lambda: agent.robot.sleep_mode()),
        ("А утром проснулся", lambda: agent.robot.wake_up()),
        ("И снова пошёл играть", lambda: agent.robot.dance())
    ]
    
    print("\nНачинаю историю...")
    for element, action in story_elements:
        print(f"\n{element}...")
        action()  # Выполняем действие
        time.sleep(2)  # Пауза для эффекта
    
    print("\n📖 История закончилась! Робот молодец!")
```

## 8. Робот-учитель 🎓

Робот может стать твоим учителем:

```python
def robot_teacher():
    """Робот-учитель"""
    agent = AIRobotHelper()
    
    print("🎓 Робот-учитель!")
    print("Я буду задавать тебе вопросы, а робот будет проверять твой ответ.")
    
    questions = [
        ("Сколько будет 2+2?", "4"),
        ("Какого цвета небо?", "голубое"),
        ("Сколько дней в неделе?", "7"),
        ("Как зовут твоего робота-помощника?", "робопомощник"),
        ("Что говорит робот, когда здоровается?", "привет")
    ]
    
    correct_answers = 0
    
    for question, correct_answer in questions:
        print(f"\nВопрос: {question}")
        user_answer = input("Твой ответ: ").lower()
        
        if correct_answer in user_answer:
            print("✅ Правильно!")
            agent.robot.wave_hand()
            correct_answers += 1
        else:
            print("❌ Не совсем... Правильный ответ:", correct_answer)
            agent.robot.look_around()  # "подумай"
    
    print(f"\n🎓 Урок окончен! Ты ответил правильно на {correct_answers} из {len(questions)} вопросов")
    
    if correct_answers == len(questions):
        print("🥇 Отличник! Робот гордится тобой!")
        agent.robot.dance()
    elif correct_answers >= len(questions) * 0.7:
        print("👍 Хорошо! Продолжай учиться!")
    else:
        print("📚 Учись больше, и будет еще лучше!")
```

## 9. Идеи для улучшения робота 🚀

- Добавить голосовой модуль (чтобы робот говорил по-настоящему)
- Подключить камеру (чтобы робот "видел" людей)
- Сделать мобильного робота (на колесах)
- Добавить пульт управления
- Создать несколько роботов, которые могут общаться между собой
- Сделать робота-музыканта (играет музыку)
- Робот-художник (рисует)
- Робот-повар (управляет простыми кухонными устройствами)

## 10. Безопасность при работе с роботом 🛡️

- Никогда не заставляй робота делать что-то опасное
- Проверяй, не мешают ли провода движению
- Не оставляй робота без присмотра с маленькими детьми
- Уважай персональные границы (робот не должен "трогать" людей)

## 11. Настоящие роботы-помощники 🏢

В реальности существуют:
- ASIMO (Honda)
- Pepper (SoftBank)
- NAO (Aldebaran)
- Sophia (Hanson Robotics)
- Amazon Astro
- Tesla Bot

Но твой робот особенный - ты его сам сделал! 💪🌟

---
**Поздравляем!** Ты создал настоящего робота-помощника с ИИ-управлением! Ты понял, как работают движущиеся роботы, и сделал его сам. Теперь ты можешь создавать роботов для любой задачи. Продолжай исследовать и создавать!