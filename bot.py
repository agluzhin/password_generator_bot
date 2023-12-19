import telebot
from telebot import types

import random
import string

bot = telebot.TeleBot('API_TOKEN')


def markup_generation(**kwargs):
    kwargs_keys = list(kwargs.keys())
    markup = types.InlineKeyboardMarkup(row_width=2)
    for key in kwargs_keys:
        text = f'{kwargs[key]}'
        callback_data = f'{key}'
        markup.add(types.InlineKeyboardButton(
            text=text, callback_data=callback_data))
    return markup


@bot.message_handler(commands=['start'])
def greetings(message):
    if message.from_user.last_name == None:
        user_name = message.from_user.first_name
    elif message.from_user.last_name != None:
        user_name = message.from_user.first_name + message.from_user.last_name

    global greetings_text
    greetings_text = f'''Hello, <b>{
        user_name}</b>! 👋\nI'm a telegram-bot created to generate castom password.\nTo start the generation process use the command: "/generate".'''

    bot.send_message(message.chat.id, greetings_text, parse_mode='HTML')


@bot.message_handler(commands=['generate'])
def user_password_length(message):
    bot.send_message(
        message.chat.id, 'Please, write a number that represents the length of the password:', parse_mode='HTML')
    bot.register_next_step_handler(message, password_generation)


def password_generation(message):
    global password_length
    password_length = message.text.strip()
    try:
        password_length = int(message.text.strip())
        bot.send_message(message.chat.id, 'Do you want to use <b>digits</b> in your password?',
                         reply_markup=markup_generation(dg_yes='Yes', dg_no='No'), parse_mode='HTML')
        return password_length
    except:
        bot.send_message(
            message.chat.id, '''Error... Maybe you have used the wrong number format, please, try entering an integer. Restart with command: "/generate".''')
        bot.register_next_step_handler(message, user_password_length)


@bot.callback_query_handler(func=lambda call: True)
def callback_function_list(call):
    if call.data in ['dg_yes', 'dg_no']:
        global elements
        elements = string.ascii_lowercase

        if call.data == 'dg_yes':
            elements += string.digits
            bot.edit_message_text('Do you need to add <b>special symbols</b>?', call.message.chat.id,
                                  call.message.id, reply_markup=markup_generation(sym_yes='Yes', sym_no='No'), parse_mode='HTML')
        else:
            bot.edit_message_text('Do you need to add <b>special symbols</b>?', call.message.chat.id,
                                  call.message.id, reply_markup=markup_generation(sym_yes='Yes', sym_no='No'), parse_mode='HTML')

    if call.data in ['sym_yes', 'sym_no']:
        def randomize(elements, password_length):
            new_password = ''.join(
                random.choice(elements)
                for _ in range(password_length)
            )
            return new_password

        if call.data == 'sym_yes':
            elements += string.punctuation
            bot.edit_message_text(f'Your new password: {randomize(
                elements, password_length)}', call.message.chat.id, call.message.id)
            bot.send_message(
                call.message.chat.id, 'To generate another password use command: "/generate".')

        else:
            bot.edit_message_text(f'Your new password: {randomize(
                elements, password_length)}', call.message.chat.id, call.message.id)
            bot.send_message(
                call.message.chat.id, 'To generate another password use command: "/generate".')


bot.polling(none_stop=True)
