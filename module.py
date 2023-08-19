import telebot
from telebot import types


def create_category_keyboard(categories):
    # Разделение категорий на списки для двух столбцов
    categories_columns = [categories[i:i+2] for i in range(0, len(categories), 2)]

    keyboard = types.InlineKeyboardMarkup()

    # Создание кнопок для каждого столбца категорий
    for column in categories_columns:
        category_buttons = [types.InlineKeyboardButton(category, callback_data=f'category:{category}') for category in column]
        keyboard.row(*category_buttons)

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_main_menu"))

    return keyboard

def category_keyboard__for_view(categories):
    # Разделение категорий на списки для двух столбцов
    categories_columns = [categories[i:i+2] for i in range(0, len(categories), 2)]

    keyboard = types.InlineKeyboardMarkup()

    # Создание кнопок для каждого столбца категорий
    for column in categories_columns:
        category_buttons = [types.InlineKeyboardButton(category, callback_data=f'category|{category}') for category in column]
        keyboard.row(*category_buttons)

    keyboard.add(types.InlineKeyboardButton("Мои объявления", callback_data="my_ads"))
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_main_menu"))
    return keyboard

def prev_next_buttons():
    # Разделение категорий на списки для двух столбцов

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(*[types.InlineKeyboardButton("Назад", callback_data="to_view_category"), types.InlineKeyboardButton("Следующее", callback_data="next")])

    return keyboard

def edit_delete_next_buttons(ad_index):
    # Разделение категорий на списки для двух столбцов

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(*[types.InlineKeyboardButton("Удалить", callback_data="delete"), types.InlineKeyboardButton("Редактировать", callback_data=f"edit")])
    keyboard.row(*[types.InlineKeyboardButton("Назад", callback_data="to_view_category"), types.InlineKeyboardButton("Следующее", callback_data="next")])

    return keyboard

def main_menu_buttons():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(*[types.InlineKeyboardButton("Опубликовать объявление", callback_data='publish'),
                   types.InlineKeyboardButton("Смотреть объявления", callback_data='view')])
    keyboard.add(types.InlineKeyboardButton("Мои объявления", callback_data='my_ads'))

    return keyboard

def back_button():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_main_menu"))
    return keyboard

def back_to_view_category():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="to_view_category"))
    return keyboard