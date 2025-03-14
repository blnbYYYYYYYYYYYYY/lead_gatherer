import os

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from misc.util import update_keyboard
from misc.bot import bot, Post
from misc.opt import keyboards, texts
from misc.filters import ChatTypeFilter, IsStaffFilter, IsAllowedContentFilter

router = Router()
router.message.filter(ChatTypeFilter(chat_type="supergroup"), IsStaffFilter(mode="post"))


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.update_data(chat_id=message.chat.id)
    message_answer = await message.answer(**texts.istaff_help.as_kwargs())
    await update_keyboard(
        message_answer.message_id,
        state,
        keyboards.ikb_staff())
    
@router.callback_query(F.data == "help")
async def help(callback: types.CallbackQuery, state: FSMContext):
    message_answer = await callback.message.answer(**texts.istaff_help.as_kwargs())
    await update_keyboard(
        message_answer.message_id,
        state,
        keyboards.ikb_staff())
    
@router.callback_query(F.data == "send")
async def send(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state()
    post_message_text = await state.get_value("post_message_text")
    message_post = await bot.send_message(
        chat_id=os.getenv("CHANNEL_ID"), 
        text=post_message_text)

    await bot.edit_message_reply_markup(
        chat_id=os.getenv("CHANNEL_ID"), 
        message_id=message_post.message_id,
        reply_markup=keyboards.ikb_ref(message_post.message_id))

    await bot.delete_messages(
        chat_id=callback.message.chat.id, 
        message_ids=[callback.message.message_id - 1,
                     callback.message.message_id])

    message_answer = await callback.message.answer(
        **texts.istaff_success.as_kwargs())
    
    await update_keyboard(
        message_answer.message_id,
        state,
        keyboards.ikb_staff())

    
@router.message(IsAllowedContentFilter("text"))
async def redirect_message(message: types.Message, state: FSMContext):

    await state.update_data(post_message_text=message.md_text)
    state_state = await state.get_state()

    if state_state == Post.share_post:
        await bot.delete_messages(
        chat_id=message.chat.id, 
        message_ids=[message.message_id-2, 
                     message.message_id-1,
                     message.message_id])

    else:
        await bot.delete_message(
            chat_id=message.chat.id, 
            message_id=message.message_id)
    
    message_answer = await message.answer(
        text=message.md_text)

    await bot.edit_message_reply_markup(
        chat_id=message.chat.id, 
        message_id=message_answer.message_id,
        reply_markup=keyboards.ikb_ref())

    
    message_answer = await message.answer(
        **texts.istaff_post.as_kwargs())
    
    await update_keyboard(
        message_answer.message_id,
        state,
        keyboards.ikb_staff(True))

    await state.set_state(Post.share_post)
