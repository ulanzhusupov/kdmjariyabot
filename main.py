import sqlite3
import telebot
from telebot import types
from module import main_menu_buttons, create_category_keyboard, category_keyboard__for_view, prev_next_buttons, edit_delete_next_buttons, back_button, back_to_view_category
from database import AdDatabase
from user_database import UserDatabase
from Ad import Ad
import os

TOKEN = os.environ['TOKEN']

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('ads.db')
cursor = conn.cursor()
db = AdDatabase()
user_db = UserDatabase()
user_db.create_table()

categories = [
    "Авто",
    "Недвижимость",
    "Работа",
    "Услуги",
    "Личные вещи",
    "Дом и Хозяйство"
]

@bot.message_handler(commands=['gtusrs'])
def start(message):
    users = user_db.get_all_users()
    msg = ''
    for user in users:
        msg += f'Username: {user[2]}\nChat ID: {user[1]}\nAds num: {user[3]}\n------------\n'
    bot.send_message(chat_id=message.chat.id, text=msg)


# Обработчик команды "/start"
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    # Проверяем, есть ли пользователь в таблице
    user_data = user_db.get_user(user_id)

    if user_data is None:
        # Если пользователя нет в таблице, добавляем его
        user_db.create_user(user_id, chat_id, username)
    else:
        # Если пользователь уже есть в таблице, получаем значение num_ads и chat_id
        num_ads = user_data[3]
        saved_chat_id = user_data[1]

        # Обновляем chat_id, если оно изменилось
        if saved_chat_id != chat_id:
            user_db.update_chatid(chat_id, user_id)
    
    num_ads = len(db.get_ads_by_user(username))
    user_db.update_user_ad_num(num_ads, username)
    

    # Создание клавиатуры с кнопками
    keyboard = main_menu_buttons()
    # Отправка сообщения с кнопками
    bot.send_message(chat_id=message.chat.id, text='Выберите действие:', reply_markup=keyboard)

category_view = ""
current_ads = []  # Список текущих объявлений
current_index = 0  # Индекс текущего объявления в списке
current_category = ''

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def button_click(call):
    global current_ads
    global current_index
    # Обработка выбранной кнопки
    if call.data == 'publish':
        keyboard = create_category_keyboard(categories)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите категорию объявления:', reply_markup=keyboard)
        # Здесь можно добавить код для обработки команды "Опубликовать объявление"
    elif call.data == 'view':
        keyboard = category_keyboard__for_view(categories)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите категорию для просмотра объявлений:', reply_markup=keyboard)
    elif call.data == 'my_ads':
        show_user_ads(call, call.from_user.username)
    elif call.data.startswith('category|'): # Для показа объявлений по категориям
        category = call.data.split('|')[1]
        show_ads_by_category(call, category)
    elif call.data.startswith('category:'): # Для создания объявлений по категориям
        category = call.data.split(':')[1]
        ask_for_photo(call.message.chat.id, category)
    elif call.data == 'next':
        last_message_id = call.message.message_id
        if current_index < len(current_ads) - 1:
            current_index += 1
            show_ad(call)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("Назад", callback_data="view"))
            bot.send_message(chat_id=call.message.chat.id, text='Больше объявлений нет.', reply_markup=keyboard)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=last_message_id, reply_markup=None)
    elif call.data == 'back_to_main_menu':
        last_message_id = call.message.message_id
        keyboard = main_menu_buttons()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите действие:', reply_markup=keyboard)
    elif call.data == 'to_view_category':
        last_message_id = call.message.message_id
        keyboard = category_keyboard__for_view(categories)
        bot.send_message(chat_id=call.message.chat.id, text='Выберите категорию для просмотра объявлений:', reply_markup=keyboard)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=last_message_id, reply_markup=None)
    elif call.data.startswith('edit'):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(*[types.InlineKeyboardButton("Изменить фото", callback_data=f"change_photo"), types.InlineKeyboardButton("Изменить текст", callback_data=f"change_text")])
        keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_main_menu"))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
    elif call.data == 'delete':
        last_message_id = call.message.message_id
        chat_id = call.message.chat.id
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=last_message_id, reply_markup=None)
        delete_ad(call)
    elif call.data.startswith('change_photo'):
        chat_id = call.message.chat.id
        bot.send_message(chat_id=chat_id, text='Отправьте новую фотографию для объявления:')
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message:update_photo(call, message))
    elif call.data.startswith('change_text'):
        chat_id = call.message.chat.id
        bot.send_message(chat_id=chat_id, text='Отправьте новый текст для объявления:')
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message:update_text(call, message))

def update_photo(call, message):
    global current_ads
    global current_ad_id
    global current_category
    chat_id = call.message.chat.id
    photo_data = None
    if message.photo:
        photo_data = message.photo[-1].file_id

    if photo_data:
        db.update_photo_by_id(photo_data, current_ad_id)
        bot.send_message(chat_id=chat_id, text='Фото успешно обновлено.')
        update_local_ads(current_category)
        show_ad(call)
    else:
        bot.send_message(chat_id=chat_id, text='Фото не найдено. Попробуйте еще раз.')
        show_ad(call)

def update_text(call, message):
    global current_ads
    global current_ad_id
    global current_category
    chat_id = call.message.chat.id

    if message.text:
        db.update_description_by_id(message.text, current_ad_id)
        bot.send_message(chat_id=chat_id, text='Текст успешно обновлен.')
        update_local_ads(current_category)
        show_ad(call)
    else:
        bot.send_message(chat_id=chat_id, text='Текст не найден. Попробуйте еще раз, заново.')
        show_ad(call)


# Запрос отправки фото
def ask_for_photo(chat_id, category):
    bot.send_message(chat_id=chat_id, text='Отправьте фотографию для объявления:')
    bot.register_next_step_handler_by_chat_id(chat_id, lambda message: save_photo(chat_id, category, message))

# Сохранение фото и запрос описания
def save_photo(chat_id, category, message):
    photo = None

    # Проверка, что сообщение содержит фотографию
    if message.photo:
        photo = message.photo[-1].file_id

    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    ad_obj = Ad(category=category, photo=photo, description="empty", username=username)

    if photo:
        bot.send_message(chat_id=chat_id, text='Фотография успешно сохранена. Отправьте описание для объявления:')
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message: save_description(chat_id, message, ad_obj))
    else:
        bot.send_message(chat_id=chat_id, text='Фотография не найдена. Отправьте фотографию для объявления:')
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message: save_photo(chat_id, category, message))


# Сохранение описания объявления
def save_description(chat_id, message, ad):
    if message.text:
        ad.description = message.text.strip()
        db.save(ad)
        num_ads = len(db.get_ads_by_user(ad.username))
        user_db.update_user_ad_num(num_ads, ad.username)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Смотреть  объявления", callback_data='view'))
        keyboard.add(types.InlineKeyboardButton("Мои объявления", callback_data='my_ads'))
        bot.send_message(chat_id=chat_id, text='Объявление успешно сохранено.\nПожалуйста, не забывайте удалять объявление при неактульности!', reply_markup=keyboard)
        return
    else:
        bot.send_message(chat_id=chat_id, text='Не найдено описание. Отправьте описание объявления:')
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message: save_description(bot, chat_id, message, ad))
######################################################################################################

def update_local_ads(category):
    global current_ads
    current_ads = db.get_all_ads_by_category(category)

def show_user_ads(call, username):
    global current_ads
    global current_index
    chat_id = call.message.chat.id

    current_ads = db.get_ads_by_user(username)
    current_index = 0

    if current_ads:
        show_ad(call)
    else:
        keyboard = back_button()
        bot.send_message(chat_id=chat_id, text='У вас нет объявлений.', reply_markup=keyboard)


# Показ объявлений в выбранной категории
def show_ads_by_category(call, category=category_view):
    global current_ads
    global current_index
    global current_category
    chat_id = call.message.chat.id
    current_category = category
    update_local_ads(category=current_category)
    # current_ads = db.get_all_ads_by_category(category)
    current_index = 0

    if current_ads:
        show_ad(call)
    else:
        keyboard = back_button()
        bot.send_message(chat_id=chat_id, text='Нет объявлений в данной категории.', reply_markup=keyboard)


def show_ad(call):
    global current_ads
    global current_index
    global current_ad_id
    chat_id = call.message.chat.id

    if current_ads:
        ad = current_ads[current_index]
        ad_message = f'Идентификатор объявления: {ad[0]}\nКатегория: {ad[1]}\nОписание: {ad[3]}\nАвтор: @{ad[4]}'
        current_category = ad[1]
        current_ad_id = ad[0]
        keyboard = prev_next_buttons()

        if call.from_user.username == ad[4]:
            keyboard = edit_delete_next_buttons(ad_index=current_index)

        if ad[2]:
            bot.send_photo(chat_id=chat_id, photo=ad[2], caption=ad_message, reply_markup=keyboard)
        else:
            bot.send_message(chat_id=chat_id, text=ad_message, reply_markup=keyboard)
    else:
        keyboard = back_to_view_category()
        bot.send_message(chat_id=chat_id, text='Больше объявлений нет.', reply_markup=keyboard)


def delete_ad(call):
    chat_id = call.message.chat.id
    global current_ad_id
    global current_category
    global current_ads
    global current_index
    db.delete(current_ad_id)
    check_ad = db.get_ad_by_id(current_ad_id)
    if check_ad:
        bot.send_message(chat_id=chat_id, text=f'Объявление с id {check_ad[0][0]} не удалось удалить.')
        show_ad(call)
    else:
        bot.send_message(chat_id=chat_id, text=f'Объявление с id {current_ad_id} успешно удалена.')
        update_local_ads(current_category)
        if current_index > len(current_ads) - 1:
            current_index -= 1
        show_ad(call)


# Запуск бота
bot.polling()
