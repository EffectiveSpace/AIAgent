import ollama
from tools.whether_scanner import get_whether
from tools.servo import set_servo_angle
import json

print("Отправка запроса")

tools = {
    "set_servo_angle": {
        "function": set_servo_angle,
        "description": "Устанавливает угол поворота сервомотора. Принимает целое число от 0 до 180.",
        "parameters": {
            "angle": {"type": "int", "description": "Угол в градусах (0–180)"}
        }
    },
    
    "get_whether": {
        "function": get_whether,
        "description": "Данные о погоде в конкретном городе",
        "parameters": {
            "city": {"type": "str", "description": "Название города"}
        }
    },
}

def choose_tool(user_query: str):

    system_prompt = """
        Ты - ИИ-диспетчер. Твоя задача - проанализировать запрос пользователя и выбрать один из следующих инструментов для его выполненния:
        Доступные инструменты:
        - 'search_engine': для поиска актуальной информации в интернете, новостей,  фактов.
        - 'get_whether': для поиска информации о погоде в каком-либо городе.
        - 'calculator': для выполнения математических операций.
        - 'file_reader': для чтения содержимого локальных файлов.
        - 'general_conversation': если запрос не требует специальных инструментов и на него можно ответить общими знаниями.
        - 'set_servo_angle': Устанавливает угол поворота сервомотора. Аргумент: {"angle": int от 0 до 180}.

        Формат ответа: только JSON вида {"tool_name": "...", "arguments": {...}}.
        Не отвечай ничего кроме этого JSON.
        
        Примеры:
        Пользователь: Какая погода сегодня в Москве?
        Твой ответ:'{"tool_name": "get_whether", "arguments": {"city": "Москва"}}'
        
        Пользователь: Прочитать файл text.txt?
        Твой ответ:'{"tool_name": "file_reader", "arguments": {"filename": "text.txt"}}'
        
    """

    try:
        response = ollama.chat(
            model='llama3',
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_query,
                }
            ]
        )
        llm_output = response['message']['content']
        return llm_output
    except Exception as e:
        print(f'Произошла ошибка: {e}')


query1 = input('Введите Ваш запрос: ')
# query2 = 'Кто стал победителем последнего чемпионата мира по футболу?'
# query3 = 'Расскажи мне анекдот про Чебурашку'
# query4 = 'Мне нужно обработать текстовые данные'
# query5 = 'Обработка данных'
# query6 = ''

print(f'Запрос: {query1} -> Выбранный инструмент: {choose_tool(query1)}')

# print(choose_tool(query1))
call_data = json.loads(choose_tool(query1))
tool_name = call_data['tool_name']
arguments = call_data['arguments']

if tool_name in tools:
    result = tools[tool_name]["function"](**arguments)
    print("Результат:", result)
else:
    print("Неизвестный инструмент:", tool_name)

    




# print(f'Запрос: {query2} -> Выбранный инструмент: {choose_tool(query2)}')
# print(f'Запрос: {query3} -> Выбранный инструмент: {choose_tool(query3)}')
# print(f'Запрос: {query4} -> Выбранный инструмент: {choose_tool(query4)}')
# print(f'Запрос: {query5} -> Выбранный инструмент: {choose_tool(query5)}')