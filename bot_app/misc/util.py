import json
import os
from dotenv import load_dotenv
from typing import Union, Optional, List

from aiogram import types
from aiogram.filters import Command
from aiogram.utils.formatting import Text
from aiogram.fsm.context import FSMContext

from misc.db import update_data, set_data
from misc.opt import texts, keyboards
from misc.bot import bot, Contact

load_dotenv(".env")

user_content_types = (
    'text','animation','audio','document',
    'paid_media','photo','sticker','story',
    'video','video_note','voice','contact',
    'dice','game','poll','venue','location'
)

service_content_types = (
    'new_chat_members','left_chat_member','new_chat_title','new_chat_photo',
    'delete_chat_photo','group_chat_created','supergroup_chat_created','channel_chat_created',
    'message_auto_delete_timer_changed','migrate_to_chat_id','migrate_from_chat_id',
    'pinned_message','invoice','successful_payment','refunded_payment','users_shared',
    'chat_shared','connected_website','write_access_allowed','passport_data',
    'proximity_alert_triggered','boost_added','chat_background_set','forum_topic_created',
    'forum_topic_edited','forum_topic_closed','forum_topic_reopened',
    'general_forum_topic_hidden','general_forum_topic_unhidden',
    'giveaway_created','giveaway','giveaway_winners','giveaway_completed',
    'video_chat_scheduled','video_chat_started','video_chat_ended',
    'video_chat_participants_invited','web_app_data','user_shared')


async def save_refs(state: FSMContext, ref: str) -> None:
    """
    appends referal numbers to db
    """
    refs = await state.get_value("refs")

    if isinstance(refs, List):
        if ref not in refs:
            refs.append(ref)

    else:
        refs = [ref]
    await state.update_data(refs=refs)



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
            chat_id=os.getenv("SUPERCHAT_ID"),
            message_thread_id=thread_id)

    except:
        full_name = await state.get_value("full_name")
        topic = await bot.create_forum_topic(
            chat_id=os.getenv("SUPERCHAT_ID"),
            name=full_name)
        thread_id = topic.message_thread_id
        await state.update_data(thread_id=thread_id)

    finally:
        chat_id = await state.get_value("chat_id")
        await set_data(int(thread_id), {"chat_id": chat_id})
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
            chat_id=os.getenv("SUPERCHAT_ID"),
            message_thread_id=thread_id)
        await set_data(int(thread_id), {"chat_id": -message.chat.id})
        
        if message:
            return await bot.send_message(
                chat_id=message.chat.id,
                **texts.a_end_dialog.as_kwargs())
    except:
        pass


async def update_keyboard(
        current_message_id: int,
        state: Optional[FSMContext] = None,
        reply_markup: Optional[types.InlineKeyboardMarkup] = None,
        previous_message_id: Optional[int] = None,
        chat_id: Optional[int] = None) -> None:
    """
    deletes inline keyboard from previous message 
    and saves data about current message with keyboard
    """
    if state:
        previous_message_id = await state.get_value("ik_message_id")
        chat_id = await state.get_value("chat_id")

    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=previous_message_id)
        
    except:
         pass

    if reply_markup:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=current_message_id,
            reply_markup=reply_markup)
    
    else:
        current_message_id = None
        
    if state:
        await state.update_data(
             ik_message_id = current_message_id)

    else:
        await update_data(chat_id,
            {"ik_message_id":current_message_id})
        
             
        

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
                phone_number = "+7" + phone_number[-10:]
            elif len(phone_number) == 10:
                phone_number = "+7" + phone_number
                 
        else:
            phone_number = None

    await state.update_data(
        contact_full_name = full_name, 
        contact_phone_number = phone_number)

    return Contact(full_name, phone_number)


async def redirect_message(message: types.Message, chat_id: int, thread_id: int = None) -> types.Message:

    content_type = str(message.content_type).split(".")[1].lower()

    if message.caption:
        caption = message.caption
    else:
        caption = None
    
    if content_type in ('paid_media','story','dice',
                        'game','poll','venue','location'):
        await bot.delete_message(
            chat_id=message.chat.id, 
            message_id=message.message_id)
        message_answer = await message.answer(**texts.a_wrong_type.as_kwargs())
        # бот удаляет это сообщение с вышеперечисленными типам контента
        # и отправляет предупреждение

    elif content_type == "text":
        message_answer = await bot.send_message(
                            text=message.md_text, 
                            chat_id=chat_id, 
                            message_thread_id=thread_id)
        
    elif content_type == "photo":
        message_answer = await bot.send_photo(
                            photo=message.photo[-1].file_id, 
                            chat_id=chat_id, 
                            message_thread_id=thread_id,
                            caption=caption)
    else:
        message_answer = await eval(
            f"""bot.send_{content_type}(
                {f"{content_type}=message.{content_type}.file_id"}, 
                chat_id=chat_id, 
                message_thread_id=thread_id,
                caption=caption
            )""")
        # если прислали другие типы контента 
        # (в нашем случае это "sticker", "animation", "photo", "video", "voice", "video_note", "contact"), 


    return message_answer


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
    