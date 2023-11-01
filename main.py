import telebot
import config
from helper import *
from telebot import types
from loguru import logger

logger.add("debug.log", format='{time}, {level}', rotation='1 week', compression=zip)
bot = telebot.TeleBot(config.TOKEN, parse_mode='HTML')
current_name = ''
current_event = {}
event = ''


def display_commands(message):
    markup = types.ReplyKeyboardMarkup()
    btn_2 = types.KeyboardButton("Изменить ФИО")
    btn_3 = types.KeyboardButton("Новое мероприятие")
    btn_4 = types.KeyboardButton('Отметить выполнение')
    btn_5 = types.KeyboardButton('Добавить задачи')
    btn_6 = types.KeyboardButton('Список задач')
    markup.add(btn_2, btn_3, btn_4, btn_5, btn_6)
    bot.send_message(message.chat.id, "Выберете команду:", reply_markup=markup)
    bot.register_next_step_handler(message, command_call)


def command_call(message):
    text = message.text
    if text == "Новое мероприятие":
        message_handler_new_event(message)
    elif text == 'Изменить ФИО':
        message_handler_rename(message)
    elif text == 'Отметить выполнение':
        message_handler_start_task_check(message)
    elif text == 'Добавить задачи':
        message_handler_append_task(message)
    elif text == 'Список задач':
        message_handler_display_tasks_list(message)




@bot.message_handler(commands=["start"])
def message_handler_start(message):
    start(message)


def start(message):
    # User welcome function
    bot.send_message(message.chat.id, 'Здравствуйте я бот который поможет вам в организации школьных мероприятий')
    bot.send_message(message.chat.id, 'Давайте зарегистрируемся')
    input_name(message)


def input_name(message):
    # Username request
    bot.send_message(message.chat.id, "Введите ФИО\n(обратите внимание, имя будет присутствовать в отчетах)")
    bot.register_next_step_handler(message, update_data)


def update_data(message):
    user = User(message.text, message.chat.id)
    json_append_user(user)
    bot.send_message(message.chat.id,
                     'Вы зарегистрированы! Если вам необходимо изменить имя просто напишите "/Изменить_ФИО"',
                     reply_markup=types.ReplyKeyboardRemove())
    display_commands(message)

    # bot.register_next_step_handler(message, bot_start.yes_or_no)


@bot.message_handler(commands='Меню')
def message_handler_menu(message):
    display_commands(message)


@bot.message_handler(commands=["Изменить_ФИО"])
def message_handler_rename(message):
    input_name(message)


@bot.message_handler(commands=["Зарегистрироваться"])
def message_hendler_registration(message):
    input_name(message)


@bot.message_handler(commands=["Новое_мероприятие"])
def message_handler_new_event(message):
    create_new_event(message)


# Processing a command to add an event
def create_new_event(message):
    bot.send_message(message.chat.id, 'Введите название мероприятия', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, append_event_title)


def append_event_title(message):
    current_event['title'] = message.text
    bot.send_message(message.chat.id, 'Введите дату мероприятия (через двоеточие)\nНапример: 01:01:2023')
    bot.register_next_step_handler(message, append_event_date)


def append_event_date(message):
    current_event['date'] = message.text
    bot.send_message(message.chat.id, 'Введите дату принятия решения (через двоеточие)\nНапример: 01:01:2023')
    bot.register_next_step_handler(message, append_event_decision_point)


def append_event_decision_point(message):
    current_event['decision_point'] = message.text
    data_checking(message)


def data_checking(message):
    correctness = correctness_date(current_event)
    if correctness == 0:
        correctness_query(message)
    elif correctness == 1:
        bot.send_message(message.chat.id, 'Точка принятия решения не может быть сегодня, '
                                          'а так же не может быть позже или в день мероприятия.\n'
                                          'проверьте правильность введенных данных '
                                          'и повторите попытку добавления мероприятия')
        display_commands(message)

    else:
        bot.send_message(message.chat.id, 'Вы ввели данные в неверном формате, пожалуйста будьте внимательны.')
        display_commands(message)


def correctness_query(message):
    # request for the correctness of the entered data
    data = 'Название мероприятия: ' + current_event['title'] + '\n' \
           + 'Дата проведения: ' + current_event['date'] + '\n' \
           + "Дедлайн: " + current_event['decision_point']

    markup = types.ReplyKeyboardMarkup()
    btn_yes = types.KeyboardButton('Да')
    btn_no = types.KeyboardButton('Нет')
    markup.add(btn_yes, btn_no)
    bot.send_message(message.chat.id, data, reply_markup=markup)
    bot.register_next_step_handler(message, create_event)


def create_event(message):
    # If the user confirms the entered data, they are added to the json file
    # Otherwise everything starts from the beginning
    global event
    if message.text == "Да":
        event = Event(current_event)
        json_append_event(event)
        bot.send_message(message.chat.id, "Мероприятие добавлено")
        request_to_add_task_list(message)

    else:
        bot.send_message(message.chat.id, "Добавление мероприятия отменено")
        display_commands(message)


def request_to_add_task_list(message):
    # Prompt the user to add a list of tasks
    markup = types.ReplyKeyboardMarkup()
    btn_yes = types.KeyboardButton('Да')
    btn_no = types.KeyboardButton('Нет')
    markup.add(btn_yes, btn_no)
    bot.send_message(message.chat.id, "Хотите добавить задачу?", reply_markup=markup)
    bot.register_next_step_handler(message, yn_add_task_list)


def yn_add_task_list(message):
    # Handling the response to adding a list of tasks
    if message.text == 'Да':
        request_task_list(message)
    else:
        bot.send_message(message.chat.id,
                         "Вы сможете добавить задачу в любое время", reply_markup=types.ReplyKeyboardMarkup)
        display_commands(message)


def request_task_list(message):
    bot.send_message(message.chat.id,
                     'Введите задачи через запятую, например:'
                     '\nЗапросить у директора разрешение на проведения мероприятия, забронировать актовый зал')
    bot.register_next_step_handler(message, append_task_list)


def append_task_list(message):
    global event
    task_list = message.text.split(':')
    json_append_task_list(event, task_list)
    bot.send_message(message.chat.id,
                     'Задачи добавлены. Вы можете добавить новые для этого введите команду',
                     reply_markup=types.ReplyKeyboardRemove())
    display_commands(message)


@bot.message_handler(commands=["Отметить_выполнение"])
def message_handler_start_task_check(message):
    start_task_check(message)


def start_task_check(message):
    if check_user_registered(message):
        event_selection(message)
    else:
        bot.send_message(message.chat.id, 'Вы не зарегестрированы')
        bot.send_message(message.chat.id, 'Для регистрации введите команду /Зарегестрироваться')


def event_selection(message):
    event_list = request_event_list()
    markup = types.ReplyKeyboardMarkup()
    for ev in event_list:
        markup.add(types.KeyboardButton(ev))
    bot.send_message(message.chat.id, "Выберете мероприятие", reply_markup=markup)
    bot.register_next_step_handler(message, display_event_tasks)


def display_event_tasks(message):
    global current_event
    current_event = message.text
    task_list = json_display_event_tasks(current_event)
    if task_list:
        markup = types.ReplyKeyboardMarkup()
        for task in task_list:
            markup.add(types.KeyboardButton(task))
        bot.send_message(message.chat.id, 'Выберете задачу', reply_markup=markup)
        bot.register_next_step_handler(message, confirmation_task)
    else:
        bot.send_message(message.chat.id, 'В данном мероприятии еще нет задач', reply_markup=types.ReplyKeyboardRemove())
        display_commands(message)


def confirmation_task(message):
    global changed_task
    changed_task = message.text
    markup = types.ReplyKeyboardMarkup()
    btn_yes = types.KeyboardButton('Да')
    btn_no = types.KeyboardButton('Нет')
    markup.add(btn_yes, btn_no)
    bot.send_message(message.chat.id, f'Сменить статус задачи "{changed_task}" на выполнено?'
                     , reply_markup=markup)
    bot.register_next_step_handler(message, change_task_status)


def change_task_status(message):
    global current_event
    if message.text == 'Да':
        json_change_task_status(current_event, changed_task, message.chat.id)
        bot.send_message(message.chat.id, 'Статус задачи изменен',
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id,
                         'Статус не изменен, вы можете начать заново при помощи команды /Отметить_выполнение',
                         reply_markup=types.ReplyKeyboardRemove())
    current_event = {}
    display_commands(message)


@bot.message_handler(commands=['Добавить_задачи'])
def message_handler_append_task(message):
    start_append_task(message)


def start_append_task(message):
    if check_user_registered(message):
        display_events(message)
    else:
        bot.send_message(message.chat.id, 'Вы не зарегестрированы')
        bot.send_message(message.chat.id, 'Для регистрации введите команду /Зарегестрироваться')


def display_events(message):
    event_list = request_event_list()
    markup = types.ReplyKeyboardMarkup()
    for ev in event_list:
        markup.add(types.KeyboardButton(ev))
    bot.send_message(message.chat.id, "Выберете мероприятие", reply_markup=markup)
    bot.register_next_step_handler(message, input_tasks)


def input_tasks(message):
    global current_event
    current_event = message.text
    bot.send_message(message.chat.id, 'Введите задачи через запятую', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, confirmation_append_tasks)


def confirmation_append_tasks(message):
    global tasks
    tasks = message.text.lower().split(',')
    markup = types.ReplyKeyboardMarkup()
    btn_yes = types.KeyboardButton('Да')
    btn_no = types.KeyboardButton('Нет')
    markup.add(btn_yes, btn_no)
    for el in tasks:
        bot.send_message(message.chat.id, el)
    bot.send_message(message.chat.id, 'Добавить данные задачи?', reply_markup=markup)
    bot.register_next_step_handler(message, append_tasks)


def append_tasks(message):
    if message.text == 'Да':
        json_append_task_list(current_event, tasks)
        bot.send_message(message.chat.id, 'Задачи добавлены', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, 'Задачи не добавлены', reply_markup=types.ReplyKeyboardRemove())
    display_commands(message)


@bot.message_handler(commands=["Список_задач"])
def message_handler_display_tasks_list(message):
    event_list = json_task_list()
    message_str = ''
    for ev in event_list:
        message_str += ev + '\n' + 'Дата мероприятия: ' + event_list[ev]['date'] + '\n' + "Дата принятия решения: " \
                       + event_list[ev]['decision_point'] + '\n'
        for tasks in event_list[ev]['task_list']:
            for task in tasks:
                message_str += '· ' + task + ['(Не выполнено)', ': (Выполнено)'][tasks[task]] + '\n'
    bot.send_message(message.chat.id, message_str)
    display_commands(message)


@bot.message_handler(commands=['err'])
def err():
    print(1 / 0)


def main():
    global bot
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception:
            logger.error('Unexpected error')

if __name__ == "__main__":
    main()
