# Упражнения к Lesson 10: Многоагентные системы

## Упражнение 1: Анализ архитектур многоагентных систем

### Цель
Понять, в каких случаях использовать разные архитектуры многоагентных систем.

### Задание
Для каждого из следующих сценариев определите, какая архитектура (иерархическая, одноранговая, с брокером) будет наиболее подходящей и объясните, почему:

1. **Система мониторинга серверов**: Несколько агентов мониторят различные серверы и отправляют уведомления при ошибках
2. **Команда для написания научной статьи**: Исследователь, аналитик, писатель и редактор работают последовательно
3. **Система оптимизации логистики**: Агенты управляют поставками, складом и доставкой, координируя действия
4. **Биржа ИИ-агентов**: Агенты конкурируют за выполнение различных задач
5. **Команда по исследованию рынка**: Агенты специализируются на разных аспектах (финансы, технологии, маркетинг) и ведут дискуссию

### Вопросы для анализа
1. Какие факторы определяют выбор архитектуры?
2. Какие компромиссы приходится делать при выборе?
3. Можно ли комбинировать разные архитектуры?

## Упражнение 2: Создание иерархической команды с CrewAI

### Цель
Создать команду с четкой иерархией и распределением ролей.

### Задание
Создайте команду из 4 агентов для выполнения задачи: "Подготовить коммерческое предложение по внедрению ИИ-агента для автоматизации поддержки клиентов".

### Роли:
1. **Менеджер проекта**: Координирует работу, определяет приоритеты, принимает финальное решение
2. **Технический специалист**: Оценивает техническую осуществимость, выбирает технологии
3. **Бизнес-аналитик**: Анализирует бизнес-ценность, ROI, преимущества для клиентов
4. **Писатель коммерческих предложений**: Формирует финальный документ

### Требования
- Использовать CrewAI
- Каждый агент должен иметь уникальный промпт (role, goal, backstory)
- Задачи должны быть связаны последовательно
- Реализовать механизм передачи информации между агентами

### Пример структуры
```python
from crewai import Agent, Task, Crew
from crewai_tools import tool

# 1. Определите инструменты
@tool("market_research")
def market_research_tool(query: str) -> str:
    """Инструмент для поиска рыночной информации."""
    pass

# 2. Создайте агентов
project_manager = Agent(
    role="Project Manager",
    goal="Coordinate team members to deliver high-quality proposal within deadline",
    backstory="Experienced project manager with strong technical background...",
    verbose=True,
    allow_delegation=True,
    tools=[market_research_tool]
)

tech_specialist = Agent(
    role="Senior Technical Specialist",
    goal="Assess technical feasibility and propose suitable technologies",
    backstory="Expert in AI/ML systems and integration...",
    verbose=True,
    allow_delegation=False
)

business_analyst = Agent(
    role="Business Analyst",
    goal="Analyze business value and ROI of the solution",
    backstory="Finance and business strategy expert...",
    verbose=True,
    allow_delegation=False
)

proposal_writer = Agent(
    role="Proposal Writer",
    goal="Create compelling commercial proposal document",
    backstory="Professional writer with experience in tech proposals...",
    verbose=True,
    allow_delegation=True
)

# 3. Создайте связанные задачи
tech_analysis_task = Task(
    description="Analyze technical requirements for AI customer support agent...",
    expected_output="Technical feasibility report with technology recommendations",
    agent=tech_specialist
)

# ... создайте остальные задачи

# 4. Создайте команду
team = Crew(
    agents=[project_manager, tech_specialist, business_analyst, proposal_writer],
    tasks=[tech_analysis_task, ...],  # добавьте все задачи
    verbose=2
)
```

### Вопросы для анализа
1. Как происходит делегирование в иерархической команде?
2. Как обеспечивается согласованность между агентами?
3. Какие проблемы могут возникнуть при такой архитектуре?

## Упражнение 3: Создание одноранговой команды с AutoGen

### Цель
Понять динамику взаимодействия в одноранговой системе.

### Задание
Создайте систему из 3 агентов, которые ведут совместное исследование:
- Цель: "Проанализировать состояние рынка LLM в 2025 году, выявить тренды и сделать прогнозы"

#### Агенты:
1. **Технологический эксперт**: Сосредотачивается на архитектурах моделей, инновациях
2. **Бизнес-эксперт**: Сосредотачивается на рынке, стоимости, коммерческом применении
3. **Аналитик данных**: Сосредотачивается на статистике, числах, метриках

### Требования
- Использовать AutoGen
- Агенты должны обмениваться сообщениями и комментировать друг друга
- Реализовать механизм достижения консенсуса
- Включить обработку конфликтов мнений

### Пример реализации
```python
import autogen

config_list = [
    {
        "model": "gpt-4",
        "api_key": "YOUR_API_KEY"
    }
]

llm_config = {"config_list": config_list}

# Создаем агентов
tech_expert = autogen.AssistantAgent(
    name="TechExpert",
    system_message="You are a technology expert focusing on LLM architectures, innovations, open-source models, and technical trends.",
    llm_config=llm_config
)

business_expert = autogen.AssistantAgent(
    name="BusinessExpert",
    system_message="You are a business expert focusing on market dynamics, pricing, enterprise adoption, and financial trends of LLMs.",
    llm_config=llm_config
)

data_analyst = autogen.AssistantAgent(
    name="DataAnalyst",
    system_message="You are a data analyst focusing on statistics, market numbers, growth rates, and quantitative trends for LLMs.",
    llm_config=llm_config
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: "FINAL REPORT" in x.get("content", ""),
    code_execution_config={"work_dir": "research"},
    llm_config=llm_config
)

# Создаем групповой чат
groupchat = autogen.GroupChat(
    agents=[user_proxy, tech_expert, business_expert, data_analyst],
    messages=[],
    max_round=20,
    speaker_selection_method="round_robin"  # или "auto" для динамического выбора
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Запускаем исследование
user_proxy.initiate_chat(
    manager,
    message="Let's conduct a comprehensive analysis of the LLM market for 2025. Each expert should share their perspective and findings. Let's aim for a unified report with consensus on key trends."
)
```

### Анализ
1. Как происходит обмен информацией между агентами?
2. Как достигается консенсус?
3. Какие проблемы могут возникнуть при отсутствии центрального координатора?

## Упражнение 4: Паттерн "Критик-Редактор-Автор"

### Цель
Реализовать продвинутый паттерн взаимодействия для создания качественного контента.

### Задание
Создайте три агента, реализующих паттерн CEA (Critic-Editor-Writer):
- **Автор**: Создает первый черновик статьи
- **Редактор**: Структурирует и улучшает черновик
- **Критик**: Находит ошибки и предлагает улучшения

Цель: Написать статью "Будущее ИИ-агентов: Тренды 2025-2030"

### Требования
- Каждый агент должен иметь свою уникальную роль и персонализированный промпт
- Реализовать циклическую итерацию: Автор → Редактор → Критик → Автор (с правками)
- Остановить цикл по достижении консенсуса или максимального числа итераций

### Пример реализации
```python
class CEAPattern:
    def __init__(self):
        self.writer = autogen.AssistantAgent(
            name="Writer",
            system_message="You write the initial draft of articles. Focus on content and initial structure.",
            llm_config=llm_config
        )
        
        self.editor = autogen.AssistantAgent(
            name="Editor", 
            system_message="You improve the structure, flow, and readability of drafts. Make them more coherent.",
            llm_config=llm_config
        )
        
        self.critic = autogen.AssistantAgent(
            name="Critic",
            system_message="You critically review content. Identify logical errors, inconsistencies, lack of evidence, and areas for improvement.",
            llm_config=llm_config
        )
        
        self.user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10
        )
    
    def run_cea_cycle(self, topic, max_iterations=5):
        initial_task = f"Write an article about: {topic}"
        
        # Шаг 1: Автор создает черновик
        draft = self.user_proxy.initiate_chat(
            self.writer,
            message=initial_task
        )
        
        current_content = draft.summary
        
        for i in range(max_iterations):
            print(f"\n--- Iteration {i+1} ---")
            
            # Шаг 2: Редактор улучшает
            edited_draft = self.user_proxy.send(
                message=f"Please improve this draft:\n\n{current_content}",
                recipient=self.editor
            )
            
            # Шаг 3: Критик анализирует
            critique = self.user_proxy.send(
                message=f"Critically review this content. Point out flaws, inconsistencies, and suggest improvements:\n\n{edited_draft.last_message()['content']}",
                recipient=self.critic
            )
            
            critique_text = critique.last_message()["content"]
            
            # Шаг 4: Проверяем, есть ли улучшения
            if "no major issues" in critique_text.lower() or "well-written" in critique_text.lower():
                print("Consensus reached. Finalizing article.")
                return edited_draft.last_message()["content"]
            
            # Шаг 5: Автор вносит правки
            revised_draft = self.user_proxy.send(
                message=f"Here is the critique of your content:\n{critique_text}\n\nPlease revise your article taking these points into account.",
                recipient=self.writer
            )
            
            current_content = revised_draft.last_message()["content"]
        
        return current_content
```

### Вопросы для анализа
1. Как эффективно передавать информацию между агентами?
2. Как измерить качество улучшения на каждом этапе?
3. Как определить, когда цикл можно остановить?

## Упражнение 5: Система с делегированием задач

### Цель
Реализовать систему, где агенты могут делегировать задачи другим агентам.

### Задание
Создайте команду из 4 агентов, каждый из которых специализируется на определенной области:
- **Главный агент**: Принимает задачи от пользователя, распределяет между специалистами
- **Исследователь**: Может искать информацию в интернете
- **Аналитик**: Может анализировать данные и делать выводы
- **Писатель**: Может форматировать и писать тексты

Организуйте систему, где главный агент может делегировать задачи специалистам.

### Требования
- Использовать AutoGen или CrewAI
- Главный агент должен оценивать, какой агент лучше всего подходит для задачи
- Реализовать механизм обратной связи от специалистов к главному агенту
- Главный агент собирает результаты и формирует финальный ответ

### Пример реализации
```python
class DelegationManager:
    def __init__(self):
        self.specialists = {
            "researcher": autogen.AssistantAgent(
                name="Researcher",
                system_message="You are a research specialist. You search for information and provide factual data.",
                llm_config=llm_config
            ),
            "analyst": autogen.AssistantAgent(
                name="Analyst", 
                system_message="You are an analyst. You interpret data and draw conclusions.",
                llm_config=llm_config
            ),
            "writer": autogen.AssistantAgent(
                name="Writer",
                system_message="You are a writer. You create well-structured textual content.",
                llm_config=llm_config
            )
        }
        
        self.coordinator = autogen.AssistantAgent(
            name="Coordinator",
            system_message="You are the coordinator. You analyze incoming tasks, determine which specialist should handle them, delegate tasks, and compile final reports from specialists' outputs.",
            llm_config=llm_config
        )
    
    def assign_task(self, task_description):
        # Этот метод должен определить, какой специалист лучше всего подходит
        # для задачи, делегировать ей задачу и вернуть результат
        pass
```

### Анализ
1. Как оценить, какой агент лучше всего подходит для задачи?
2. Как обеспечить эффективную передачу контекста между агентами?
3. Как обрабатывать ситуации, когда специалист не может выполнить задачу?

## Упражнение 6: Адаптивная команда агентов

### Цель
Создать команду, которая может адаптироваться к изменениям в задаче или среде.

### Задание
Создайте систему, в которой:
- Агенты могут добавляться или удаляться динамически
- Агенты могут менять роли при необходимости
- Команда адаптируется к изменению целей

### Сценарий
Изначально задача: "Подготовить технический отчет о LLM". 
Затем задача изменяется: "Подготовить маркетинговый материал о преимуществах LLM для бизнеса".

### Требования
- Использовать механизм, который позволяет команде "переконфигурироваться"
- Агенты должны обнаруживать изменения в задаче
- Реализовать логику переназначения ролей или перепланирования

### Вопросы для анализа
1. Как агенты могут обнаруживать изменение целей?
2. Как эффективно перераспределять роли?
3. Какие метрики могут указывать на необходимость адаптации?

## Упражнение 7: Коммуникационный протокол между агентами

### Цель
Создать стандартизированный протокол обмена сообщениями.

### Задание
Реализуйте систему обмена сообщениями между агентами:
- Определите формат сообщения (какие поля обязательны)
- Реализуйте сериализацию/десериализацию
- Добавьте валидацию сообщений
- Реализуйте логирование всех сообщений

### Пример структуры сообщения
```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class AgentMessage:
    sender_id: str
    recipient_id: str
    message_type: str  # "task", "result", "request", "notification", "error"
    content: str
    timestamp: datetime = None
    correlation_id: Optional[str] = None  # Для отслеживания связанных сообщений
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_json(self) -> str:
        """Сериализует сообщение в JSON."""
        data = {
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "metadata": self.metadata
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Десериализует сообщение из JSON."""
        data = json.loads(json_str)
        return cls(
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"], 
            message_type=data["message_type"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            metadata=data.get("metadata", {})
        )
    
    def validate(self) -> bool:
        """Проверяет валидность сообщения."""
        required_fields = ["sender_id", "recipient_id", "message_type", "content"]
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True
```

### Использование протокола
```python
class CommunicationHub:
    def __init__(self):
        self.message_log = []
    
    def send_message(self, message: AgentMessage):
        """Отправляет сообщение одному или нескольким агентам."""
        if not message.validate():
            raise ValueError("Invalid message format")
        
        # Здесь логика доставки сообщения
        self.message_log.append(message)
        print(f"[{message.timestamp}] {message.sender_id} -> {message.recipient_id}: {message.message_type}")
    
    def broadcast_message(self, message: AgentMessage, target_agents: list):
        """Отправляет сообщение нескольким агентам."""
        for agent in target_agents:
            new_msg = AgentMessage(
                sender_id=message.sender_id,
                recipient_id=agent.id,
                message_type=message.message_type,
                content=message.content,
                correlation_id=message.correlation_id,
                metadata=message.metadata.copy()
            )
            self.send_message(new_msg)
```

### Вопросы для анализа
1. Какие поля обязательны в сообщении?
2. Как обеспечить надежность доставки?
3. Как использовать логирование для отладки?

## Упражнение 8: Система мониторинга и отладки многоагентной системы

### Цель
Создать систему для отслеживания работы команды агентов.

### Задание
Реализуйте:
- Систему логирования всех действий агентов
- Механизм сбора метрик (время выполнения, количество вызовов инструментов и т.п.)
- Визуализацию потока задач между агентами
- Механизм оповещения о сбоях

### Требования
- Использовать структурированное логирование
- Сохранять логи в файл или базу данных
- Реализовать основные метрики производительности
- Создать простую систему оповещений

### Пример реализации
```python
import logging
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AgentMetric:
    agent_name: str
    task_count: int
    avg_response_time: float
    error_rate: float
    token_usage: int

class AgentMonitor:
    def __init__(self):
        self.logger = self._setup_logger()
        self.metrics: Dict[str, List[float]] = {}
        self.start_times = {}
    
    def _setup_logger(self):
        """Настраивает структурированное логирование."""
        logger = logging.getLogger("MultiAgentSystem")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler("agent_system.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def log_agent_action(self, agent_name: str, action: str, result: str):
        """Логирует действие агента."""
        self.logger.info(f"AGENT={agent_name}, ACTION={action}, RESULT={result}")
    
    def start_timer(self, task_id: str):
        """Запускает таймер для задачи."""
        self.start_times[task_id] = time.time()
    
    def stop_timer(self, task_id: str):
        """Останавливает таймер и возвращает время выполнения."""
        if task_id in self.start_times:
            elapsed = time.time() - self.start_times[task_id]
            del self.start_times[task_id]
            return elapsed
        return 0
    
    def record_metric(self, agent_name: str, metric_name: str, value: float):
        """Записывает метрику для агента."""
        if agent_name not in self.metrics:
            self.metrics[agent_name] = []
        self.metrics[agent_name].append(value)
    
    def get_agent_stats(self, agent_name: str) -> AgentMetric:
        """Возвращает статистику по агенту."""
        if agent_name not in self.metrics:
            return AgentMetric(agent_name, 0, 0, 0, 0)
        
        values = self.metrics[agent_name]
        return AgentMetric(
            agent_name=agent_name,
            task_count=len(values),
            avg_response_time=sum(values) / len(values) if values else 0,
            error_rate=self._calculate_error_rate(agent_name),
            token_usage=self._calculate_token_usage(agent_name)
        )
    
    def alert_on_failure(self, agent_name: str, error: str):
        """Отправляет оповещение о сбое."""
        self.logger.error(f"CRITICAL FAILURE: Agent {agent_name} failed with error: {error}")
        # Здесь можно добавить отправку уведомления (email, Slack, etc.)
```

### Анализ
1. Какие метрики наиболее важны для оценки эффективности команды?
2. Как использовать логи для отладки?
3. Какие алерты должны срабатывать?

## Упражнение 9: Масштабирование многоагентной системы

### Цель
Понять проблемы и решения при масштабировании команд агентов.

### Задание
Рассмотрите систему из 10 агентов, работающих над сложной задачей. Определите:
- Возможные проблемы масштабирования
- Решения для повышения эффективности
- Архитектурные изменения, необходимые для масштабирования

### Проблемы для анализа:
1. Коммуникационная сложность (каждый с каждым)
2. Конкуренция за ресурсы (LLM API, базы данных)
3. Управление состоянием и синхронизация
4. Мониторинг и отладка

### Задание
Разработайте архитектурные решения:
1. Введение групп агентов (агенты по 3-4 в группе)
2. Использование очередей задач
3. Кэширование результатов
4. Управление пропускной способностью

### Вопросы
1. Как уменьшить количество прямых коммуникаций?
2. Как распределить нагрузку между агентами?
3. Какие компромиссы приходится делать при масштабировании?

## Упражнение 10: Интеграция с внешними системами

### Цель
Научиться интегрировать многоагентную систему с внешними сервисами.

### Задание
Создайте команду агентов, которая взаимодействует с внешними API:
- CRM система (для получения информации о клиентах)
- База данных (для хранения результатов)
- Система уведомлений (для отправки результатов)

### Сценарий
Команда агентов должна обработать запрос: "Подготовить персонализированное предложение для клиента с ID 12345"

### Требования
- Один агент получает информацию о клиенте из CRM
- Второй анализирует данные и готовит предложение
- Третий сохраняет результат в базу данных
- Четвертый отправляет уведомление клиенту

### Реализация интеграции
```python
import requests
from typing import Dict, Any

class ExternalServiceIntegration:
    def __init__(self, crm_url: str, db_url: str, notification_url: str):
        self.crm_url = crm_url
        self.db_url = db_url
        self.notification_url = notification_url
    
    def get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Получает данные клиента из CRM."""
        response = requests.get(f"{self.crm_url}/customers/{customer_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch customer data: {response.status_code}")
    
    def save_proposal(self, proposal_data: Dict[str, Any]) -> str:
        """Сохраняет предложение в базу данных."""
        response = requests.post(f"{self.db_url}/proposals", json=proposal_data)
        if response.status_code == 201:
            return response.json()["id"]
        else:
            raise Exception(f"Failed to save proposal: {response.status_code}")
    
    def send_notification(self, customer_id: str, message: str):
        """Отправляет уведомление клиенту."""
        payload = {"customer_id": customer_id, "message": message}
        response = requests.post(f"{self.notification_url}/notifications", json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send notification: {response.status_code}")

# Создаем инструмент, доступный агентам
external_integration = ExternalServiceIntegration(
    crm_url="https://api.yourcrm.com",
    db_url="https://api.yourdb.com", 
    notification_url="https://api.notifications.com"
)
```

### Вопросы для анализа
1. Как обеспечить безопасность при работе с внешними API?
2. Как обрабатывать сбои внешних сервисов?
3. Как кэшировать данные из внешних источников?

---

## Дополнительные задания для продвинутых

### Задание 11: Гибридная архитектура
Реализуйте систему, сочетающую несколько архитектур (например, иерархическую структуру с одноранговыми подгруппами).

### Задание 12: Обучение с подкреплением для координации
Исследуйте, как алгоритмы обучения с подкреплением могут улучшить координацию между агентами.

---

После выполнения упражнений сравните эффективность разных архитектур многоагентных систем и подумайте, как бы вы применили эти знания в реальных проектах ИИ-агентов.