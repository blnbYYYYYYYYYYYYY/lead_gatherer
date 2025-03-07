from aiogram.filters import Command
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from misc.config import config
from misc.opt import keyboards, texts
from misc.filters import ChatTypeFilter
from misc.bot import bot, HotLine, Verification, Contact
from misc.util import (open_topic, 
                       close_topic, 
                       get_start_message, 
                       update_keyboard, 
                       extract_contact_info)

router = Router() 
router.message.filter(ChatTypeFilter(chat_type="private"))


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, command: Command = None):
    await state.set_state(state=None)
    await state.update_data(
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        chat_id=message.chat.id)
    await close_topic(state, message)

    is_verified = await state.get_value("is_verified")
    message_text = await get_start_message(state, command)
    message_answer = await message.answer(
        **message_text.as_kwargs())
    
    await update_keyboard(message_answer.message_id, state, keyboards.ikb_default(is_verified))


@router.callback_query(F.data == "start_hotline")
async def start_hotline(callback: types.CallbackQuery, state: FSMContext):

    await state.set_state(HotLine.enabled)
    thread_id = await open_topic(state)

    await callback.message.answer(**texts.a_start_dialog.as_kwargs())
    message_answer = await callback.message.answer(**texts.i_start_dialog.as_kwargs())
    await update_keyboard(message_answer.message_id, state, keyboards.ik_end_chat)

    refs = await state.get_value("refs")
    await bot.send_message(
        chat_id=config.superchat_id.get_secret_value(),
        message_thread_id=thread_id,
        **texts.bi_2hotline(callback, refs).as_kwargs())


@router.message(HotLine.enabled)
async def redirect_user_message(message: types.Message, state: FSMContext):

    code_to_execute = """bot.send_{0}(
                            {1}, 
                            chat_id=config.superchat_id.get_secret_value(), 
                            message_thread_id=thread_id
                        )"""

    content_type = (str(message.content_type).split(".")[1].lower())  # парсим тип контента
    thread_id = await state.get_value("thread_id")
    
    if content_type in ("venue", "location", "poll"):
        await bot.delete_message(
            chat_id=message.chat.id, 
            message_id=message.message_id)
        message_answer = await message.answer(**texts.a_wrong_type.as_kwargs())
        await update_keyboard(message_answer.message_id, state, keyboards.ik_end_chat)

    elif content_type == "text":
        content = message.md_text
        await eval(code_to_execute.format(
            "message", "text=content"))

    elif content_type == "photo":
        await eval(code_to_execute.format(
            content_type, f"{content_type}=message.{content_type}[-1].file_id"))
        
    else:
        await eval(code_to_execute.format(
            content_type, f"{content_type}=message.{content_type}.file_id"))


@router.callback_query(F.data == "end_hotline")
async def end_hotline(callback: types.CallbackQuery, state:FSMContext):
    await state.set_state(state=None)
    message_answer = await close_topic(state, callback.message)

    is_verified = await state.get_value("is_verified")
    await update_keyboard(message_answer.message_id, state, keyboards.ikb_default(is_verified))


@router.callback_query(F.data == "verify_number")
async def contact_verification(callback: types.CallbackQuery, state:FSMContext):
    await state.set_state(Verification.share_contact)

    message_answer = await callback.message.answer(
        **texts.i_share_contact.as_kwargs(),
        reply_markup=keyboards.rk_share_contact)
    await update_keyboard(message_answer.message_id, state)

    await state.update_data(
        verification_message_id=message_answer.message_id)
    await callback.answer()


@router.message(Verification.share_contact)
async def phone_number_verification(message: types.Message, state: FSMContext):
    refs = await state.get_value("refs")
    verification_message_id = await state.get_value("verification_message_id")
    contact = await extract_contact_info(message, state)

    if contact.phone_number:
        await state.set_state(Verification.share_name)
        thread_id = await open_topic(state)
         
        business_message = await bot.send_message(
            chat_id=config.superchat_id.get_secret_value(),
            message_thread_id=thread_id,
            **texts.bi_2hotline(message, refs, contact).as_kwargs())
        await state.update_data(business_message_id = business_message.message_id)
        await close_topic(state)

        await bot.delete_message(                   # deletes the message with reply keyboard
            chat_id=message.chat.id,                # because telegram refuses to edit the text of such a message
            message_id=verification_message_id) 
 
    await bot.delete_message(                       # deletes users message with phone number
        chat_id=message.chat.id,
        message_id=message.message_id)  
    verification_message = await bot.send_message(  # sends new verification message
        chat_id=message.chat.id,                    # w/o reply keyboard
        **texts.bi_phone_confirm(contact.phone_number).as_kwargs())
    await state.update_data(verification_message_id = verification_message.message_id)


@router.message(Verification.share_name)
async def name_verification(message: types.Message, state:FSMContext):
    verification_message_id = await state.get_value("verification_message_id")
    phone_number = await state.get_value("contact_phone_number")
    refs = await state.get_value("refs")
    business_message_id = await state.get_value("business_message_id")
    
    contact = Contact(message.md_text, phone_number)
    await state.set_state(None)
    await state.update_data(
        is_verified=1,
        contact_full_name=contact.full_name)
    
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=verification_message_id,
        **texts.bi_contact_confirm(contact.full_name, phone_number).as_kwargs())
    await update_keyboard(verification_message_id, state, keyboards.ikb_default(is_verified=1),)

    await bot.edit_message_text(
        chat_id=config.superchat_id.get_secret_value(),
        message_id=business_message_id,
        **texts.bi_2hotline(message, refs, contact).as_kwargs())

