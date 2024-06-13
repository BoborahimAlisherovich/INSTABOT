from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram import F
from aiogram.types import Message
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands  import set_default_commands
from baza.sqlite import Database
from filtery.admin import IsBotAdminFilter
from filtery.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext
from middlewares.throttling import ThrottlingMiddleware 
from states.reklama import Adverts
from aiogram.types import InlineKeyboardButton,FSInputFile,InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time 
from tik_tok import tiktok_save
from insta import insta_save
from yutube import youtube_save
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN

CHANNELS = config.CHANNELS


from aiogram.client.session.aiohttp import AiohttpSession

session = AiohttpSession(proxy='http://proxy.server:3128')

bot = Bot(token=..., session=session)

dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message:Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name,telegram_id=telegram_id)
        await message.answer(text=f"Assalomu alaykum,{full_name} botimizga hush kelibsiz\nTikTok Youtube Instagramdan link yuboring men sizga video yuklab beraman")
    except:
        await message.answer(text=f"Assalomu alaykum,{full_name} botimizga hush kelibsiz\nTikTok Youtube Instagramdan link yuboring men sizga video yuklab beraman")


@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message:Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index,channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
    inline_channel.adjust(1,repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)




@dp.message(Command("help"))
async def is_admin(message:Message):
    await message.answer(text="Bu botimiz instagram teligram youTobe dan vidyo skschat qilib beradi")


#Admin panel uchun
@dp.message(Command("admin"),IsBotAdminFilter(ADMINS))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)


@dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
async def users_count(message:Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text=="Reklama yuborish",IsBotAdminFilter(ADMINS))
async def advert_dp(message:Message,state:FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message:Message,state:FSMContext):
    
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],from_chat_id=from_chat_id,message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.5)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()

@dp.message(F.text.contains("instagram"))
async def instagram_download(message:Message):
    
  
        await message.answer(text="video yuklanmoqda 🚀")
        link = message.text
        
        result = insta_save(link)
        await message.answer(text="Video tayyor")
      
        if result[0]=="video":
            await message.answer_video(video=result[1],caption="""Admin: @Alisherov1ch_002 """)
        elif result[0]=="rasm":
            await message.answer_photo(photo=result[1], caption="Admin: @Alisherov1ch_002")
        else:
            await message.answer("You sent the wrong link")

@dp.message(F.text.contains("youtube"))
async def youtube_download(message:Message):
        try:
            await message.answer(text="Sizning so'rovingiz ko'rib chiqilmoqda...")

            result = youtube_save(message.text)
            video = FSInputFile(result) 
            await message.answer_video(video=video, caption="ADMIN: @Alisherov1ch_002")
        except:
            await message.answer(text="Bu videoni yuklay olmadi.")


@dp.message(F.text.contains("tiktok"))
async def tiktok_download(message:Message):
    await message.answer(text="video yuklanmoqda 🚀")
    link = message.text
    tiktok = tiktok_save(link)
    
    video=tiktok.get("video")
    music=tiktok.get("music")
    rasmlar=tiktok.get("images")
    if rasmlar: 
        rasm = []
        for i,r in enumerate(rasmlar):
            rasm.append(InputMediaPhoto(media=r))
            if (i+1)%10==0:
                await message.answer_media_group(rasm)
                rasm=[]
        if rasm:
            await message.answer_media_group(rasm)
    elif video:
        await message.answer_video(video=video,caption="Admin: @Alisherov1ch_002")
    if music: 
        await message.answer_audio(audio=music)



@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)

#bot ishga tushganini xabarini yuborish
@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)

async def main() -> None:
    global bot,db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML, session=session)
    db = Database(path_to_db="main.db")
    db.create_table_users()
    await set_default_commands(bot)
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())
