from aiogram.utils.formatting import Text, as_list, TextLink, Bold, Underline

def start_ref (ref:str):
    return as_list(
        Text("Здравствуйте!"),
        Text("Я Елена, руководитель отдела ", TextLink("ОЗ Лубянка", url="https://t.me/remarket_msk"), "."),
        Text("Вы оставили ➕ под ", TextLink("постом", url=f"https://t.me/remarket_msk/{ref}"), "."),
        Text(
            "Нажмите на кнопку ", Bold("Оставить номер"), " и менеджер вышлет вам подробную презентацию о ",
            "ЖК в мессенджер, а также уточнит информацию по необходимым параметрам, чтобы составить ",
            "индивидуальную подборку точечно под Ваш запрос."
            )
    )

start = as_list(
    Text("Здравствуйте!"),
    Text("Я Елена, руководитель отдела ", TextLink("ОЗ Лубянка", url="https://t.me/remarket_msk"), "."),
    Text(
        "Нажмите на кнопку ", Bold("Оставить номер"), " и менеджер свяжется с вами любым удобным для Вас способом."
        )
)

def start_to_hotline(callback, mode, refs):
    if mode == "call":
        msg_text = Text(f"Пользователь @{callback.from_user.username}, ",
            f"под именем {callback.from_user.full_name}, ",
            f"просит связаться с ним через ", Underline("звонок "), "по номеру ",
            f"{callback.message.entities[0].extract_from(callback.message.text)}")

    elif mode == "chat":
        msg_text = Text(f"Пользователь @{callback.from_user.username}, ",
            f"под именем {callback.from_user.full_name}, ",
            f"просит связаться с ним через ", Underline("мессенджер "), "по номеру ",
            f"{callback.message.entities[0].extract_from(callback.message.text)}")
    
    else:
        msg_text = Text(f"Обращение пользователя @{callback.from_user.username}, ",
            f"под именем {callback.from_user.full_name}",
            )
    
    if callback.message.chat.id in refs.keys():

        links = ""

        for id, ref in enumerate(refs[callback.message.chat.id]):
            links += f"https://t.me/remarket_msk/{ref}"
            if (id + 1) < len(refs[callback.message.chat.id]):
                links +=", "

        msg_text = as_list(
            msg_text,
            as_list(
                "Предложения, которые его заинтересовали: ",
                links
            )
        )

    """
    формируем текст сообщения согласно запросу
    затем добавляем реферальные ссылки, если понадобится 
    """

    return msg_text

start_hotline_alert_1 = Text("Вы начали диалог с администратором бота 🙌")
start_hotline_alert_2 = Text("Напишите свой вопрос и я отвечу Вам в ближайшее время!")
end_hotline_alert = Text("Вы закончили диалог с администратором бота 👋")
auth_info = Text("Нажмите на кнопку или введите контактный номер телефона, если он не совпадает с текущим:")

def auth_info_b(phone_number):

    if phone_number == None:
        return as_list(
            Text(f"Неправильный формат номера"),
            Text("Введите ваш номер телефона в формате:"),
            Text("8XXX-XXX-XX-XX")
        )        
    
    if phone_number[0] == "8":
        phone_number = "7" + phone_number[1:]
    
    if phone_number[0] != "+":
        phone_number = "+" + phone_number
    
    return as_list(
            Text(f"Ваш номер телефона: {phone_number}"),
            Text("Выберите удобный способ связи:")
        )

def auth_alert_b(callback):
    return as_list(
        Text(f"Ваш номер телефона: {callback.message.entities[0].extract_from(callback.message.text)}"),
		Text("Вскоре менеджер свяжется с Вами")
    )

	