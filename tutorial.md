# Создание ИИ агентов с использованием Python и LLM API

Этот краткий туториал основан на книге Павла Рощина "Создаём ИИ агентов на Python и LLM API".

## Введение

ИИ-агенты — это интеллектуальные системы, которые могут воспринимать окружающую среду, принимать решения и выполнять действия для достижения поставленных целей. Современные ИИ-агенты часто используют большие языковые модели (LLM) для обработки информации и принятия решений.

## Основные компоненты ИИ-агента

1. **Восприятие (Perception)**: Способность получать информацию из окружающей среды
2. **Память (Memory)**: Хранение и извлечение информации
3. **Рассуждение (Reasoning)**: Обработка информации и принятие решений
4. **Действие (Action)**: Выполнение действий во внешней среде

## Пример базового ИИ-агента с использованием Python

```python
import openai
from typing import Dict, List, Any

class SimpleAIAgent:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.memory = []
    
    def perceive(self, environment_info: str) -> None:
        """Получает информацию из окружающей среды"""
        self.memory.append({"role": "user", "content": environment_info})
    
    def reason(self) -> str:
        """Обрабатывает информацию и принимает решение"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.memory,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка при рассуждении: {str(e)}"
    
    def act(self) -> str:
        """Выполняет действие на основе рассуждений"""
        decision = self.reason()
        self.memory.append({"role": "assistant", "content": decision})
        return decision

# Пример использования
if __name__ == "__main__":
    # Замените на ваш API-ключ
    agent = SimpleAIAgent(api_key="your-api-key-here")
    
    # Агент воспринимает запрос пользователя
    agent.perceive("Привет! Как дела?")
    
    # Агент думает и отвечает
    response = agent.act()
    print(f"Агент: {response}")
```

## Инструменты и библиотеки

### Основные библиотеки для создания ИИ-агентов:

1. **OpenAI API**: Для доступа к мощным LLM
2. **LangChain**: Фреймворк для работы с LLM и создания цепочек
3. **Hugging Face Transformers**: Библиотека для работы с предобученными моделями
4. **Requests**: Для работы с HTTP-запросами
5. **Pandas**: Для обработки данных

### Установка необходимых библиотек:

```bash
pip install openai langchain requests pandas transformers
```

## Расширенный пример с LangChain

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

def calculator_tool(numeric_expression: str) -> str:
    """Простой инструмент для вычисления математических выражений"""
    try:
        result = eval(numeric_expression)
        return str(result)
    except:
        return "Ошибка вычисления"

# Создание агента с инструментами
llm = ChatOpenAI(temperature=0)
tools = [
    Tool(
        name="Calculator",
        func=calculator_tool,
        description="Позволяет вычислять математические выражения"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Использование агента
response = agent.run("Чему равно 2 в степени 10?")
print(response)
```

## Типичные шаблоны для ИИ-агентов

1. **ReAct (Reasoning + Acting)**: Пошаговое принятие решений с выполнением действий
2. **Self-Ask**: Агент задает себе промежуточные вопросы для лучшего понимания задачи
3. **Chain-of-Thought**: Логическая цепочка рассуждений
4. **Multi-Modal**: Использование различных типов данных (текст, изображения и т.д.)

## Практические рекомендации

1. **Кэширование результатов**: Для экономии ресурсов сохраняйте результаты выполнения
2. **Управление контекстом**: Следите за размером контекста, особенно при использовании LLM
3. **Обработка ошибок**: Реализуйте надежную обработку ошибок
4. **Тестирование**: Проверяйте работу агента в различных сценариях
5. **Безопасность**: Не передавайте конфиденциальную информацию без защиты

## Заключение

Создание ИИ-агентов — это сочетание программирования, машинного обучения и системного мышления. Начните с простого агента, как показано выше, а затем постепенно усложняйте его функциональность, добавляя новые инструменты, память и возможности принятия решений.

Для более глубокого изучения темы рекомендуется обратиться к полной версии книги Павла Рощина, где рассматриваются продвинутые техники создания ИИ-агентов.