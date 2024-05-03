# telegram_bot.py
import telebot
import re
from database import set_user_notion_id, get_user_notion_id
from notion_api import create_task_for_user, get_tasks_assigned_to_user
from config import TELEGRAM_TOKEN
import datetime
import locale

# Установка локали на русский язык
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

commands = [
    telebot.types.BotCommand(command="/setnotionid", description="Установить ваш Notion user ID"),
    telebot.types.BotCommand(command="/addtask", description="Добавить новую задачу в ваш список в Notion"),
    telebot.types.BotCommand(command="/mytasks", description="Показать все задачи, назначенные на вас в Notion")
]

bot.set_my_commands(commands)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_message = (
        "Привет! Я бот, который помогает управлять задачами в Notion.\n"
        "Вот что я могу делать:\n"
        "/start или /help - показать это сообщение.\n"
        "/setnotionid - установить ваш Notion user ID для связи с вашими задачами.\n"
        "/addtask <название задачи> - добавить новую задачу в ваш список в Notion.\n"
        "/mytasks - показать все задачи, назначенные на вас в Notion.\n"
        "\nПожалуйста, введите ваш Notion user ID для настройки или используйте команду /setnotionid, чтобы его установить."
    )
    bot.send_message(message.chat.id, welcome_message)



@bot.message_handler(commands=['addtask'])
def handle_add_task(message):
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        task_name = parts[1]
        notion_user_id = get_user_notion_id(user_id)
        if notion_user_id:
            result = create_task_for_user(task_name, notion_user_id)
            if result and 'id' in result:  # Проверяем, содержит ли результат ID новой страницы
                bot.reply_to(message, f"Task '{task_name}' added successfully!")
            else:
                bot.reply_to(message, "Failed to add the task to Notion. Please try again.")
        else:
            bot.reply_to(message, "Your Notion user ID is not set. Please update it using /setnotionid.")
    else:
        bot.reply_to(message, "Please provide the name of the task after the command.")


@bot.message_handler(commands=['mytasks'])
def handle_my_tasks(message):
    user_id = message.from_user.id
    notion_user_id = get_user_notion_id(user_id)
    if notion_user_id:
        tasks = get_tasks_assigned_to_user(notion_user_id)
        if tasks:
            tasks_list = []
            for task in tasks:
                task_name = (task.get('properties', {})
                             .get('Name', {})
                             .get('title', [{}])[0]
                             .get('text', {})
                             .get('content', 'No Task Name'))

                date_info = task.get('properties', {}).get('Date', {}).get('date', None)
                location_rich_text = task.get('properties', {}).get('Location', {}).get('rich_text', [])
                location_info = location_rich_text[0].get('text', {}).get('content') if location_rich_text else None

                task_details = [f"*{task_name}*"]

                if date_info:
                    task_date = date_info.get('start')
                    if task_date:
                        date_object = datetime.datetime.fromisoformat(task_date)
                        if date_object.year == datetime.datetime.now().year:
                            formatted_date = date_object.strftime('%d %B %H:%M')
                        else:
                            formatted_date = date_object.strftime('%d %B %Y %H:%M')
                        task_details.append(f"_Дата: {formatted_date}_")

                if location_info:
                    task_details.append(f"_Место: {location_info}_")

                tasks_list.append('\n'.join(task_details))

            tasks_message = '\n\n'.join(tasks_list)
            bot.reply_to(message, f"Твои задачи:\n{tasks_message}", parse_mode='Markdown', disable_web_page_preview=True)
        else:
            bot.reply_to(message, "Задачи не найдены.")
    else:
        bot.reply_to(message,
                     "ID пользователя Notion не установлен. Пожалуйста, обновите его с помощью команды /setnotionid.")



@bot.message_handler(commands=['setnotionid'])
def handle_set_notion_id(message):
    msg = bot.send_message(message.chat.id, "Please enter your Notion user ID:")
    bot.register_next_step_handler(msg, save_notion_user_id)

def save_notion_user_id(message):
    user_id = message.from_user.id
    notion_user_id = message.text
    # Проверка формата UUID
    uuid_pattern = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    if uuid_pattern.match(notion_user_id):
        set_user_notion_id(user_id, notion_user_id)
        bot.reply_to(message, "Your Notion user ID has been successfully updated.")
    else:
        bot.reply_to(message, "Please enter a valid Notion user ID.")


if __name__ == "__main__":
    bot.polling()
