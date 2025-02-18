from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.formatting import Text, as_list

from opt import keyboards, texts
from filters.filters import ChatTypeFilter, IsHotlineMode
from config import config
from bot_init import bot, io_json

router = Router()	# создание роутера для клиентских хендлеров
router.message.filter(ChatTypeFilter(chat_type="private"))	# прикрепление фильтра на тип чата к роутеру

hotline_chat = io_json("hotline_chat")	# загрузка кешированных данных
inline_keyboard_msg_id = io_json("inline_keyboard_msg_id")
auth_status = io_json("auth_status")
refs = io_json("refs")

@router.message(Command("start"))
async def cmd_start(message: types.Message, command: Command = None):

	try:

		if auth_status[message.chat.id] == 0:
			auth_status.update({message.chat.id: -1})	

	finally:

		auth_status.setdefault(message.chat.id, -1)	

	"""
	попытка установить значение (-1), в случае если клиент зарестартил бота в процессе аутентификации
	
	наконец установка дефолтного значения для нового юзера

	(-1) - не проходил аутентификацию,
	(0) - в процессе аутентификации,
	(1) - прошел аутентификацию
	"""

	try:

		await bot.close_forum_topic(
			chat_id=config.superchat_id.get_secret_value(),
			message_thread_id=hotline_chat[message.chat.id]
			)
		
		hotline_chat.update({
			message.chat.id: int(-hotline_chat[message.chat.id])
			})
		
	except:

		pass

	"""
	пробуем закрыть топик, на случай если юзер перезапустил бота во время хотлайн мода
	"""

	args = command.args or None	# получение реферальных аргументов для команды старт

	if args:
		args = args.split("_")[1]	# аргументы генерируются в формате ...?start=request_{message_id}
		msg_text = texts.start_ref(args)	# оборачиваем в текст сообщения нужную гиперссылку

		if message.chat.id in refs.keys():
			if args not in refs[message.chat.id]:
				refs[message.chat.id].append(args)

		else:
			refs.setdefault(message.chat.id, [args])

		"""
		проверка были ли прежде у клиента переходы по реферальным ссылкам в кеше,
		кеширование факта перехода
		"""

	else:
		msg_text = texts.start	# дефолтное стартовое сообщение без рефов

	await message.answer(
		**msg_text.as_kwargs(),
		reply_markup=keyboards.ikb_default(
			auth_status[message.chat.id]
		)
	)
	
	inline_keyboard_msg_id.update({message.chat.id: message.message_id}) # обновление позиции инлайн клавиатуры в кеше


@router.callback_query(F.data == "start_hotline_chat")
async def start_hotline_chat(callback: types.CallbackQuery):	

	await callback.message.edit_reply_markup()	# убирает инлайн клавиатуру с предыдущего сообщения
	await callback.message.answer(**texts.start_hotline_alert_1.as_kwargs())

	message = await callback.message.answer(
		**texts.start_hotline_alert_2.as_kwargs(),
		reply_markup=keyboards.ik_end_chat
		)
	
	inline_keyboard_msg_id.update({message.chat.id: message.message_id}) 
	
	try:

		await bot.reopen_forum_topic(
			chat_id=config.superchat_id.get_secret_value(),
			message_thread_id=int(-hotline_chat[callback.message.chat.id])
			)
		
		hotline_chat.update({
			callback.message.chat.id: int(-hotline_chat[callback.message.chat.id])
			})
	
	except:
		topic = await bot.create_forum_topic(
			chat_id=config.superchat_id.get_secret_value(), 
			name=callback.from_user.full_name
			)
		
		hotline_chat.update({callback.message.chat.id: topic.message_thread_id})

	"""
	попытка открыть топик, если он был создан и закрыт
	иначе создаем новый топик
	"""

	await bot.send_message(
		chat_id=config.superchat_id.get_secret_value(), 
		message_thread_id=hotline_chat[callback.message.chat.id],
		**texts.start_to_hotline(callback=callback, mode=None, refs=refs).as_kwargs()
		)	# отправляем сформированное приветственное сообщение стаффу
	

@router.message(IsHotlineMode(hotline_chat=hotline_chat))	
async def send_msg_to_htln(message: types.Message):

	code_to_execute = """bot.send_{0}(
							{1}, 
							chat_id=config.superchat_id.get_secret_value(), 
							message_thread_id=hotline_chat[message.chat.id]
						)"""
	
	"""
	редиректит сообщение от пользователя в стафф супергруппу в конкретный топик
	делаю через эвал, чтобы уменьшить колличество строк кода, 
	т.к вызываются шаблонные функции для различных типов данных
	"""
	
	content_type = str(message.content_type).split(".")[1].lower()	# парсим тип контента
	
	if content_type == "text":
		content = message.md_text
		await eval(code_to_execute.format(
			"message", 
			"text=content")
			)
	
	elif content_type == "photo":
		await eval(
			code_to_execute.format(
				content_type, 
				f"{content_type}=message.{content_type}[-1].file_id"
			)
		)	
		"""
		т.к. message.photo это список файл айди для фото с 
		разным разрешением, то приходится так изворчиваться
		"""

	elif content_type in ("venue", "location", "poll"):
		await bot.delete_message(
			chat_id=message.chat.id, 
			message_id=message.message_id
			)
		await bot.edit_message_reply_markup(
			chat_id=message.chat.id, 
			message_id=inline_keyboard_msg_id[message.chat.id], 
			reply_markup=None
			)
		content = as_list(
			Text("Упссс... Что-то пошло не так...:(("), 
			Text("Возможно обмен данным типом контента не поддерживается")
		)

		warn_message = await message.answer( 
			reply_markup=keyboards.ik_end_chat,
			**content.as_kwargs())
		
		inline_keyboard_msg_id.update({message.chat.id: warn_message.message_id})

		"""
		на самом деле поддержка завозится в 5 строк кода, но мне лень
		"""

	else:
		await eval(
			code_to_execute.format
			(
				content_type, 
				f"{content_type}=message.{content_type}.file_id"
			)
		)

	 

@router.callback_query(F.data == "end_hotline_chat")
async def end_hotline_chat(callback: types.CallbackQuery):

	await bot.close_forum_topic(
			chat_id=config.superchat_id.get_secret_value(),
			message_thread_id=hotline_chat[callback.message.chat.id]
			)
	
	hotline_chat.update({callback.message.chat.id: int(-hotline_chat[callback.message.chat.id])})	

	await callback.message.edit_reply_markup()
	
	message = await callback.message.answer(
		**texts.end_hotline_alert.as_kwargs(),
		reply_markup=keyboards.ikb_default(
			auth_status[callback.message.chat.id]
		)
	)
	
	inline_keyboard_msg_id.update({message.chat.id: message.message_id})

	"""
	закрываем необходимый топик
	инвертируем айди топика в словаре
	удаляем с текущего сообщения инлайн клавиатуру
	отправляем сообщение, что хотлайн мод выключен
	обновляем айди сообщения с инлайн клавиатурой
	"""
	

@router.callback_query(F.data == "clt_auth")
async def auth_query(callback: types.CallbackQuery):

	await callback.message.edit_reply_markup()
	message = await callback.message.answer(
		**texts.auth_info.as_kwargs(), 
		reply_markup=keyboards.rk_share_contact
		)
	
	auth_status.update({message.chat.id: 0})
	inline_keyboard_msg_id.update({message.chat.id: 0})

	try:
		if [item for item in callback.message.entities if item.type == "phone_number"] != []:
			await bot.delete_message(
				chat_id=callback.message.chat.id, 
				message_id=callback.message.message_id
				)

	except TypeError:
		pass

	"""
	проверка на то, есть ли в предыдущем сообщении номер телефона
	нужна т.к. клиент может неправильно ввести номер телефона, 
	затем при нажатии на кнопку "Номер не верный"
	его снова примет этот хендлер, а предыдущее сообщение удалиться, чтобы не засорять чат
	"""

	await callback.answer()

@router.message(lambda m: auth_status[m.chat.id] == 0)
async def auth_update(message: types.Message):

	await bot.delete_messages(
		chat_id=message.chat.id, 
		message_ids=[message.message_id-1, message.message_id]
	)	# удаляет алерт бота и сообщение юзера с номером

	message_entities = message.entities or []

	if message.content_type == "contact":
		phone_number = str(message.contact.phone_number)
		reply_markup = keyboards.ik_auth
		
	elif message_entities != []:
		phone_number = str(message.entities[0].extract_from(message.text))
		reply_markup = keyboards.ik_auth

	else:
		phone_number = None
		reply_markup = None

	"""
	если юзер прислал контакт, то достаем из объекта контакта номер
	если юзер прислал номер, как энтити, то достаем его из сообщения
	если номер не распознается как энтити, то считаем его недействительным
	"""

	await message.answer(
			reply_markup=reply_markup, 
			**texts.auth_info_b(phone_number).as_kwargs()
		)	# логика формирования сообщений в функции
	
	inline_keyboard_msg_id.update({message.chat.id: message.message_id})


@router.callback_query(F.data.startswith("contact_"))
async def contact_(callback: types.CallbackQuery):

	mode = callback.data.split("_")[1] # парсим данные колбэка

	auth_status.update({callback.message.chat.id: 1})
	
	await callback.message.edit_text(**texts.auth_alert_b(callback).as_kwargs())

	await callback.message.edit_reply_markup(
		inline_message_id=str(inline_keyboard_msg_id[callback.message.chat.id]),
		reply_markup=keyboards.ikb_default(
			auth_status[callback.message.chat.id]
		)
	)

	"""
	меняем текст текущего сообщения на новый и клавиатуру на дефолтную
	"""

	try:
		await bot.reopen_forum_topic(
			chat_id=config.superchat_id.get_secret_value(),
			message_thread_id=int(-hotline_chat[callback.message.chat.id])
		)

		topic_message_thread_id = int(-hotline_chat[callback.message.chat.id])
		
	except:
		topic = await bot.create_forum_topic(
			chat_id=config.superchat_id.get_secret_value(), 
			name=str(callback.from_user.full_name)
		)

		topic_message_thread_id = topic.message_thread_id

	finally:

		await bot.send_message(
			chat_id=config.superchat_id.get_secret_value(), 
			message_thread_id=topic_message_thread_id,
			**texts.start_to_hotline(callback, mode=mode, refs=refs).as_kwargs()
		)

		await bot.close_forum_topic(
			chat_id=config.superchat_id.get_secret_value(),
			message_thread_id=topic_message_thread_id
		)

		hotline_chat.update({callback.message.chat.id: int(-topic_message_thread_id)})

	"""
	пытаемся открыть топик, отправить информирующее сообщение стаффу и сохранить топик айди
	иначе создаем топик, отправляем сообщение и сохраняем топик айди
	в итоге закрываем топик по сохраненному топик айди и вносим изменения в кеш

	"""

	await callback.answer()
