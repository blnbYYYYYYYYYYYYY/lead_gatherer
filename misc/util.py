import json
from typing import Union

from aiogram import types
from aiogram.filters import Command
from aiogram.utils.formatting import Text
from aiogram.fsm.context import FSMContext

from misc import db
from misc.opt import texts
from misc.config import config
from misc.bot import bot, Contact

content_types = (
    "text", "sticker", "animation", "photo", 
    "video", "voice", "video_note", "contact", 
    "location", "venue", "document"
)


async def save_refs(state: FSMContext, ref: str) -> None:
    """
    appends referal numbers to db
    """
    refs = await state.get_value("refs")

    if not refs:
        state.update_data(refs=[ref])
    elif ref not in refs:
        state.update_data(refs=refs.append(ref))


async def get_start_message(state: FSMContext, command: Command = None) -> Text:
    """
    gets args and creates texts for start messages
    """
    args = command.args or None

    if args:
        ref = args.split("_")[1]
        await save_refs(state, ref)
        return texts.bi_start(ref)
    else:
        return texts.i_start
    

async def open_topic(state: FSMContext) -> int:
    """
    the aim of this funcion is to keep one topic for one person
    and prevent creating too much topics
    """
    try:
        thread_id = await state.get_value("thread_id")
        await bot.reopen_forum_topic(
            chat_id=config.superchat_id.get_secret_value(),
            message_thread_id=thread_id)

    except:
        full_name = await state.get_value("full_name")
        topic = await bot.create_forum_topic(
            chat_id=config.superchat_id.get_secret_value(),
            name=full_name)
        thread_id = topic.message_thread_id
        await state.update_data(thread_id=thread_id)

    finally:
        chat_id = await state.get_value("chat_id")
        await db.set_data(thread_id, chat_id)
        return thread_id    
    

async def close_topic(state: FSMContext,
        message: Union[types.Message, None] = None) -> Union[types.Message, None]:
    """
    tries* to close opened topic
    and then send notification to user about that
    *in case of user send /start command in HotLine mode
    """
    thread_id = await state.get_value("thread_id")

    try:
        await bot.close_forum_topic( 
            chat_id=config.superchat_id.get_secret_value(),
            message_thread_id=thread_id)
        await db.set_data(thread_id, -message.chat.id)
        
        if message:
            return await bot.send_message(
                chat_id=message.chat.id,
                **texts.a_end_dialog.as_kwargs())
    except:
        pass


async def update_keyboard(current_message_id: int, 
                          state: FSMContext,
                          reply_markup: Union[types.InlineKeyboardMarkup, None] = None) -> None:
    """
    deletes inline keyboard from previous message 
    and saves data about current message with keyboard
    """
    ik_message_id = await state.get_value("ik_message_id")
    chat_id = await state.get_value("chat_id")

    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=ik_message_id)
        
    except:
         pass
        
    finally:
        if reply_markup:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=current_message_id,
                reply_markup=reply_markup)
            await state.update_data(
                ik_message_id=current_message_id)
        else:
            await state.update_data(
                ik_message_id=None)
        

async def extract_contact_info(message: types.Message, state: FSMContext) -> Union[str, None]:
    """
    extracts full name and phone number
    """

    if message.contact:
        full_name = message.contact.first_name
        if isinstance(message.contact.last_name, str):
            full_name += " " + message.contact.last_name
        phone_number = message.contact.phone_number
    
    else:
        full_name = message.from_user.full_name

        if message.entities:
            for id, entitie in enumerate(message.entities):
                if entitie.type == "phone_number":
                    phone_number = str(message.entities[id].extract_from(message.text))
                    break
            if phone_number[0] == "8" and len(phone_number) == 11:
                phone_number = "+7" + phone_number[:-10]
        else:
            phone_number = None

    await state.update_data(
        contact_full_name = full_name, 
        contact_phone_number = phone_number)

    return Contact(full_name, phone_number)


def io_json(variable:str, mode:str="r", data:dict|None=None) -> dict | None:

	"""
	variable: name of variable,

	mode: "r" - read, "w" - write

	data: data to be writed
	"""

	if mode == "w":

		with open(file=f"data/{variable}.json", mode=mode) as outfile:

			json.dump(data, outfile)
			return True

	elif mode == "r":

		with open(file=f"data/{variable}.json", mode=mode) as outfile:

			try:
				data = json.load(outfile)

			except json.decoder.JSONDecodeError:
				print("json file is empty")

		if data != None and data != {}:

			try:
				data_w_corr_data_type = {int(key):int(val) for key, val in data.items() if val != None}
			
			except: 
				data_w_corr_data_type = {int(key):val for key, val in data.items() if val != None}
			
			finally:
				return data_w_corr_data_type
		else:
			return {}

	else:
		raise Exception("unsupported mode type")
    