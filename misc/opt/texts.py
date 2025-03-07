from typing import Union

from aiogram import types
from aiogram.utils.formatting import Text, as_list, TextLink, Bold, Code, Italic

from misc.bot import Contact

i_start = as_list(
    Text("Здравствуйте!"),
    Text("Я Елена, руководитель отдела ", TextLink("ОЗ Лубянка", url="https://t.me/remarket_msk"), "."),
    Text("Нажмите на кнопку ", Bold("Оставить номер"), " и менеджер свяжется с вами любым удобным для Вас способом."))

a_start_dialog = as_list(
    Text("🤖"),
    Text("Вы начали диалог с администратором бота"))

i_start_dialog = as_list(
    Text("👩🏻‍💻"),
    Text("Напишите свой вопрос и я отвечу Вам в ближайшее время!"))

a_end_dialog = as_list(
    Text("🤖"),
    Text("Вы закончили диалог с администратором бота"))

i_share_contact = as_list(
    Text("🤖"),
    Text("Нажмите на кнопку или введите контактный номер телефона, если он не совпадает с текущим:"))

a_wrong_type = as_list(
    Text("🤖"),
    Text("Упссс... Что-то пошло не так...:(("),
    Text("Возможно обмен данным типом контента не поддерживается"),)

as_wrong_type = Text("Упссс... Что-то пошло не так...:((")

def bi_start (ref: str) -> Text:
    return as_list(
        Text("Здравствуйте!"),
        Text("Я администратор телеграм канала", TextLink("Отдел Застройщиков, Лубянка", url="https://t.me/remarket_msk"), "."),
        Text("Вы оставили ➕ под ", TextLink("постом", url=f"https://t.me/remarket_msk/{ref}"), "."),
        Text(
            "Нажмите на кнопку ", Bold("Оставить номер"), " и менеджер вышлет вам подробную презентацию о ",
            "ЖК в мессенджер, а также уточнит информацию по необходимым параметрам, чтобы составить ",
            "индивидуальную подборку точечно под Ваш запрос."
            )
    )

def bi_phone_confirm(phone_number: str) -> Text:

    if phone_number == None:
        return as_list(
            Text("🤖"),
            Text(f"Неправильный формат номера"),
            Text("Введите ваш номер телефона в формате:"),
            Text("8XXX-XXX-XX-XX")
        )        
    
    return as_list(
        Text("🤖"),
        Text(f"Ваш номер телефона: {phone_number}"),
        Text("Введите ваше имя:")
    )

def bi_contact_confirm(user_name: str, phone_number: str) -> Text:
    return as_list(
        Text("🤖"),
        Text("Ваши контактные данные:"),
        Text("📞    ", phone_number),
        Text("☑️    ", Code(user_name)),
        Text(" "),
		Text("Вскоре менеджер свяжется с Вами"),
        Italic("*если данные не верны, повторите верификацию"), 
    )
	
def bi_2hotline(
        obj: types.Message, 
        refs: Union[str, list, None], 
        contact: Union[Contact, None] = None) -> Text:

    if contact:
        if contact.full_name != obj.from_user.full_name:
            full_name = contact.full_name + " или " + obj.from_user.full_name

        else:
            full_name = obj.from_user.full_name

        msg_text = Text(
            f"Пользователь @{obj.from_user.username}, ",
            f"под именем {full_name}, ",
            f"просит связаться с ним по номеру ",
            f"{contact.phone_number}"
        )
        
    else:
        msg_text = Text(
            f"Обращение пользователя @{obj.from_user.username}, ",
            f"под именем {obj.from_user.full_name}",
        )
        
    if refs:
        if isinstance(refs, str):
            refs = f"https://t.me/remarket_msk/{refs}"

        elif isinstance(refs, list):
            refs = [f"https://t.me/remarket_msk/{ref}" for ref in refs]

        msg_text = as_list(
            msg_text,
            as_list(
                "Предложения, которые его заинтересовали: ", 
                refs
            )
        )

    """
    формируем текст сообщения согласно запросу
    затем добавляем реферальные ссылки, если понадобится 
    """

    return msg_text