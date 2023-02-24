from config.config import Config
from telethon import events, Button
from bot_helper.Others.Helper_Functions import getbotuptime, get_config, delete_trash, get_logs_msg, gen_random_string, get_readable_time, get_human_size, botStartTime, get_current_time
from os.path import exists
from asyncio import sleep as asynciosleep
from os import execl
from sys import argv, executable
from bot_helper.Aria2.Aria2_Engine import Aria2, getDownloadByGid
from bot_helper.Process.Process_Status import ProcessStatus
from time import time
from asyncio import create_task
from bot_helper.Database.User_Data import get_data, new_user, change_task_limit, get_task_limit, saveoptions, save_restart, get_host_stats
from bot_helper.Telegram.Telegram_Client import Telegram
from bot_helper.Process.Running_Tasks import add_task, get_status_message, get_user_id, get_queued_tasks_len, refresh_tasks
from bot_helper.Process.Running_Process import remove_running_process
from asyncio import Lock
from psutil import virtual_memory, cpu_percent, disk_usage
from bot_helper.Others.Names import Names
from telethon.errors.rpcerrorlist import MessageIdInvalidError
from re import findall
from requests import get
from bot_helper.Others.SpeedTest import speedtest

status_update = {}
status_update_lock = Lock()



#////////////////////////////////////Variables////////////////////////////////////#
sudo_users = Config.SUDO_USERS
owner_id = Config.OWNER_ID
allowed_chats = Config.ALLOWED_CHATS
TELETHON_CLIENT = Telegram.TELETHON_CLIENT
LOGGER = Config.LOGGER
SAVE_TO_DATABASE = Config.SAVE_TO_DATABASE

#////////////////////////////////////Functions////////////////////////////////////#

###############------Download_From_Direct_Link------###############
def dw_file_from_url(url, filename):
        r = get(url, allow_redirects=True, stream=True)
        with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024 * 10):
                        if chunk:
                                fd.write(chunk)
        return

###############------Check_Magenet------###############
def is_magnet(url: str):
    magnet = findall(r"magnet:\?xt=urn:btih:[a-zA-Z0-9]*", url)
    return bool(magnet)



#////////////////////////////////////Telethon Functions////////////////////////////////////#

###############------Mention_User------###############
def get_mention(event):
    return "["+event.message.sender.first_name+"](tg://user?id="+str(event.message.sender.id)+")"

###############------Check_File_Or_URL_Event------###############
async def get_url_from_message(new_event):
        if new_event.message.file:
            return new_event
        else:
            return str(new_event.message.message)

###############------Get_Username------###############
def get_username(event):
    try:
        if event.message.sender.username:
            user_name = event.message.sender.username
        else:
            user_name = False
    except:
            user_name = False
    return user_name

###############------Check_Auth_User------###############
def user_auth_checker(event):
    if event.is_private:
        if event.message.sender.id == owner_id:
            return True
    else:
        if event.message.sender.id in sudo_users or event.message.sender.id in allowed_chats or event.message.sender.id == owner_id:
            return True
    return False

###############------Check_Sudo_User_Event------###############
def sudo_user_checker_event(event):
    if event.message.sender.id in sudo_users or event.message.sender.id == owner_id:
            return True
    return False

###############------Check_Sudo_User_ID------###############
def sudo_user_checker_id(user_id):
    if user_id in sudo_users or user_id == owner_id:
            return True
    return False

###############------Check_Owner_User_Event------###############
def owner_checker(event):
    if event.message.sender.id == owner_id:
            return True
    return False

###############------Get_Link------###############
async def get_link(event):
    custom_file_name = False
    if "|" in event.message.message:
        ext_data = event.message.message.split('|')
        custom_file_name = str(ext_data[-1]).strip()
        commands = ext_data[1].split(' ')
    else:
        commands = event.message.message.split(' ')
    if len(commands)==2:
            if str(commands[1]).startswith("http") or is_magnet(commands[1]):
                return commands[1], custom_file_name
            else:
                return "invalid", custom_file_name
    else:
            if event.reply_to_msg_id:
                msg_object = await TELETHON_CLIENT.get_messages(event.message.chat.id, ids=event.reply_to_msg_id)
                if not msg_object.file:
                    if str(msg_object.message).startswith("http") or is_magnet(str(msg_object.message)):
                        return str(msg_object.message), custom_file_name
                    else:
                        return "invalid", custom_file_name
                else:
                    return msg_object, custom_file_name
            else:
                return False, custom_file_name


###############------Get_Custom_Name------###############
async def get_custom_name(event):
    custom_file_name = False
    if "|" in event.message.message:
        ext_data = event.message.message.split('|')
        custom_file_name = str(ext_data[-1]).strip()
    return custom_file_name

###############------Ask_Text------###############
async def ask_text(chat_id, user_id, event, timeout, message, text_type):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'*️⃣ {str(message)} [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(e)
                return False
            try:
                return text_type(new_event.message.message)
            except:
                await new_event.reply(f'❌Invalid Limit')
                return False

###############------Ask Media OR URL------###############
async def ask_media_OR_url(event, chat_id, user_id, keywords, message, timeout, mtype, s_handle, allow_magnet=True, allow_url=True, message_hint=False, allow_command=False):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.file or str(e.message.message) in keywords or str(e.message.message).startswith("http")), timeout=timeout)
            msg = f"*️⃣ {str(message)} [{str(timeout)} secs]"
            if message_hint:
                msg += f"\n\n{message_hint}"
            ask = await event.reply(msg)
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(str(e))
                return False
            if new_event.message.file:
                if not str(new_event.message.file.mime_type).startswith(mtype):
                    await new_event.reply(f'❗[{str(new_event.message.file.mime_type)}] This is not a valid file.')
                    return False
                return new_event
            elif new_event.message.message:
                if str(new_event.message.message)=='stop':
                    if s_handle:
                        await ask.reply('✅Task Stopped')
                    return "stopped"
                elif str(new_event.message.message)=='cancel':
                    await ask.reply('✅Task Cancelled')
                    return "cancelled"
                elif str(new_event.message.message).startswith("http"):
                    if allow_url:
                        return new_event
                    else:
                        await ask.reply('❌HTTP Link Are Not Allowed.')
                        return "stopped"
                elif is_magnet(str(new_event.message.message)):
                    if allow_magnet:
                        return new_event
                    else:
                        await ask.reply('❌Magnet Link Are Not Allowed.')
                        return "stopped"
                else:
                    if allow_command:
                            await ask.reply(f'❗You have already started {str(new_event.message.message).replace("/", "")} task.')
                            return "pass"
                    else:
                            await ask.reply(f'❌You already started {str(new_event.message.message).replace("/", "")} task. Now send {str(new_event.message.message)} command again')
                            return "cancelled"

###############------Get_Thumbnail------###############
async def get_thumbnail(process_status, keywords, timeout):
    if get_data()[process_status.user_id]['custom_thumbnail']:
        async with TELETHON_CLIENT.conversation(process_status.chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=process_status.chat_id, incoming=True, from_users=[process_status.user_id], func=lambda e: e.message.media or str(e.message.message) in keywords), timeout=timeout)
            ask = await process_status.event.reply(f'*️⃣ Send Thumbnail [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Task Has Been Cancelled.')
                LOGGER.info(str(e))
                return
            if new_event.message.media:
                if not str(new_event.message.file.mime_type).startswith('image/'):
                    await new_event.reply(f'❗[{str(new_event.message.file.mime_type)}] This is not a valid thumbnail.')
                    return
            elif new_event.message.message:
                if str(new_event.message.message)=='pass':
                    await ask.reply('✅Task Passed')
                    return
                else:
                    await ask.reply(f'❗You already started a task, now send {str(new_event.message.message)} command again.')
                    return False
            custom_thumb = await new_event.download_media(file=f"{process_status.dir}/{process_status.process_id}.jpg")
            process_status.set_custom_thumbnail(custom_thumb)
            return
    else:
        return

###############------Ask_WaterMark------###############
async def ask_watermark(event, chat_id, user_id, cmd, wt_check):
    watermark_path = f'./userdata/{str(user_id)}_watermark.jpg'
    watermark_check = exists(watermark_path)
    if watermark_check:
            if wt_check:
                return True
            text = f"Watermark Already Present\n\n🔷Send Me New Watermark Image To Replace."
    else:
            text = f"Watermark Not Present\n\n🔶Send Me Watermark Image To Save."
    new_event = await ask_media_OR_url(event, chat_id, user_id, [f"/{cmd}", "stop"], text, 120, "image/", True, False, False)
    if new_event and new_event not in ["cancelled", "stopped"]:
        await TELETHON_CLIENT.download_media(new_event.message, watermark_path)
        if exists(watermark_path):
            return True
    return False


###############------Save_Rclone_Config------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/saveconfig', func=lambda e: user_auth_checker(e)))
async def _saverclone(event):
        user_id = event.message.sender.id
        chat_id = event.message.chat.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        r_config = f'./userdata/{str(user_id)}_rclone.conf'
        check_config = exists(r_config)
        link = False
        if check_config:
                text = f"Rclone Config Already Present\n\nSend Me New Config To Replace."
        else:
                text = f"Rclone Config Not Present\n\nSend Me Config To Save."
        new_event = await ask_media_OR_url(event, chat_id, user_id, ["/saveconfig", "stop"], text, 120, "text/", True, False)
        if new_event and new_event not in ["cancelled", "stopped"]:
            if new_event.message.file:
                await new_event.download_media(file=r_config)
            else:
                link = str(new_event.message.message)
                dw_file_from_url(link, r_config)
            if not exists(r_config):
                await new_event.reply("❌Failed To Download Config File.")
                return
            accounts = await get_config(r_config)
            if not accounts:
                await delete_trash(r_config)
                await new_event.reply("❌Invalid Config File Or Empty Config File.")
                return
            await saveoptions(user_id, 'drive_name', accounts[0], SAVE_TO_DATABASE)
            if link:
                await saveoptions(user_id, 'rclone_config_link', link, SAVE_TO_DATABASE)
            await new_event.reply(f"✅Config Saved Successfully\n\n🔶Using {str(get_data()[user_id]['drive_name'])} Drive For Uploading.")
        return


###############------Change_Task_Limit------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/tasklimit', func=lambda e: owner_checker(e)))
async def _changetasklimit(event):
        user_id = event.message.sender.id
        chat_id = event.message.chat.id
        limit = await ask_text(chat_id, user_id, event, 120, "Send New Task Limit", int)
        if limit:
            change_task_limit(int(limit))
            await refresh_tasks()
            await event.reply(f'✅Successfully Set New Limit: {get_task_limit()}')
            return


###############------Restart------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/restart', func=lambda e: owner_checker(e)))
async def _restart(event):
        chat_id = event.message.chat.id
        user_id = event.message.sender.id
        reply = await event.reply("♻Restarting...")
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        if SAVE_TO_DATABASE:
            await save_restart(chat_id, reply.id)
        execl(executable, executable, *argv)


###############------Get_Logs_Message------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/log', func=lambda e: sudo_user_checker_event(e)))
async def _log(event):
        user_id = event.message.sender.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        log_file = "Logging.txt"
        if exists(log_file):
                await event.reply(str(get_logs_msg(log_file)))
        else:
            await event.reply("❗Log File Not Found")
        return


###############------Get_Log_File------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/logs', func=lambda e: sudo_user_checker_event(e)))
async def _logs(event):
        chat_id = event.message.chat.id
        user_id = event.message.sender.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        log_file = "Logging.txt"
        if exists(log_file):
            try:
                await TELETHON_CLIENT.send_file(chat_id, file=log_file, allow_cache=False)
            except Exception as e:
                await event.reply(str(e))
        else:
            await event.reply("❗Log File Not Found")
        return


###############------Reset_Database------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/resetdb', func=lambda e: owner_checker(e)))
async def _resetdb(event):
        await event.reply("*️⃣Are you sure?\n\n🚫 This will reset your all database 🚫", buttons=[
                [Button.inline('Yes 🚫', 'resetdb_True')],
                [Button.inline('No 😓', 'resetdb_False')],
                [Button.inline('⭕Close', 'close_settings')]
            ])
        return


###############------Save_WaterMark_Image------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/savewatermark', func=lambda e: user_auth_checker(e)))
async def _savewatermark(event):
        chat_id = event.message.chat.id
        user_id = event.message.sender.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        check_watermark = await ask_watermark(event, chat_id, user_id, "savewatermark", False)
        if not check_watermark:
            await event.reply("❗Failed To Get Watermark.")
        else:
            await event.reply("✅Watermark saved successfully.")
        return


###############------Renew------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/renew', func=lambda e: owner_checker(e)))
async def _renew(event):
        user_id = event.message.sender.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        await event.reply("*️⃣Are you sure?\n\n🚫 This will delete all your downloads and saved watermark locally 🚫", buttons=[
                [Button.inline('Yes 🚫', 'renew_True')],
                [Button.inline('No 😓', 'renew_False')],
                [Button.inline('⭕Close', 'close_settings')]
            ])
        return

###############------Save_Stats------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/stats', func=lambda e: sudo_user_checker_event(e)))
async def _stats_msg(event):
    await event.reply(str(get_host_stats()), parse_mode='html')
    return


###############------Speed_Test------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/speedtest', func=lambda e: sudo_user_checker_event(e)))
async def _speed_test(event):
    chat_id = event.message.chat.id
    reply = await event.reply("⏳Running Speed Test, Please Wait.....")
    try:
        file_path, caption = await speedtest()
        await TELETHON_CLIENT.send_file(chat_id, file=file_path, caption=caption, reply_to=event.message, allow_cache=False, parse_mode='html')
    except Exception as e:
        await event.reply(str(e))
    await reply.delete()
    return


###############------Start_Message------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/start'))
async def _startmsg(event):
    text = f"Hi {get_mention(event)}, I Am Alive."
    await event.reply(text, buttons=[
    [Button.url('⭐ Bot By 𝚂𝚊𝚑𝚒𝚕 ⭐', 'https://t.me/nik66')],
    [Button.url('❤ Join Channel ❤', 'https://t.me/nik66x')]
])
    return

###############------Bot_UpTime------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/time', func=lambda e: sudo_user_checker_event(e)))
async def _timecmd(event):
    await event.reply(f'♻Bot Is Alive For {getbotuptime()}')
    return


###############------Cancel Process------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/cancel', func=lambda e: user_auth_checker(e)))
async def _cancel(event):
        user_id = event.message.sender.id
        commands = event.message.message.split(' ')
        if len(commands)==3:
                processx = commands[1]
                process_id = commands[2]
                try:
                        if processx=="aria":
                            if dl := getDownloadByGid(process_id):
                                if dl.listener().user_id==user_id or sudo_user_checker_id(user_id):
                                    await Aria2.cancel_download(process_id)
                                else:
                                    await event.reply(f'❗You Have No Permission To Delete')
                                    return
                            else:
                                await event.reply(f'❗No download with this id')
                                return
                        elif processx=="process":
                            add_user_id = get_user_id(process_id)
                            if add_user_id:
                                if add_user_id==user_id or sudo_user_checker_id(user_id):
                                    cancel_result = await remove_running_process(process_id)
                                    if not cancel_result:
                                            await event.reply(f'❗No process with this id')
                                            return
                            else:
                                if sudo_user_checker_id(user_id):
                                    cancel_result = await remove_running_process(process_id)
                                    if not cancel_result:
                                            await event.reply(f'❗No process with this id')
                                            return
                                else:
                                    await event.reply(f'❗Failed to verify user id')
                                    return
                        await event.reply(f'✅Successfully Cancelled.')
                except Exception as e:
                        await event.reply(str(e))
                return
        else:
                await event.reply(f'❗Give Me Process ID To Cancel.')
                return

###############------Compress------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/compress', func=lambda e: user_auth_checker(e)))
async def _compress_video(event):
        chat_id = event.message.chat.id
        user_id = event.message.sender.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        link, custom_file_name = await get_link(event)
        if link=="invalid":
            await event.reply("❗Invalid link")
            return
        elif not link:
            new_event = await ask_media_OR_url(event, chat_id, user_id, ["/compress", "stop"], "Send Video or URL", 120, "video/", True)
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event)
            else:
                return
        user_name = get_username(event)
        user_first_name = event.message.sender.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, event, Names.compress, custom_file_name)
        await get_thumbnail(process_status, ["/compress", "pass"], 120)
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]])
        create_task(add_task(task))
        await event.reply("✅Task Added\n\nCheck /status")
        return


###############------Status------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/status', func=lambda e: user_auth_checker(e)))
async def _status(event):
        reply  = await event.reply("⏳Please Wait")
        chat_id = event.message.chat.id
        user_id = event.message.sender.id
        status_update_id = gen_random_string(5)
        async with status_update_lock:
            if chat_id not in status_update:
                status_update[chat_id] = {}
            status_update[chat_id].clear()
            status_update[chat_id]['update_id'] = status_update_id
        await asynciosleep(2)
        while True:
            status_message = await get_status_message(reply)
            if not status_message:
                await reply.edit(f"No Running Process!\n\n**CPU:** {cpu_percent()}% | **FREE:** {get_human_size(disk_usage('/').free)}\n**RAM:** {virtual_memory().percent}% | **UPTIME:** {get_readable_time(time() - botStartTime)}\n**QUEUED:** {get_queued_tasks_len()} | **TASK LIMIT:** {get_task_limit()}")
                break
            if status_update[chat_id]['update_id'] != status_update_id:
                await reply.delete()
                break
            if get_data()[user_id]['show_stats']:
                status_message += f"**CPU:** {cpu_percent()}% | **FREE:** {get_human_size(disk_usage('/').free)}"
                status_message += f"\n**RAM:** {virtual_memory().percent}% | **UPTIME:** {get_readable_time(time() - botStartTime)}\n"
            if get_data()[user_id]['show_time']:
                    status_message+= "**Current Time:** " + get_current_time() + "\n"
            status_message += f"**QUEUED:** {get_queued_tasks_len()} | **TASK LIMIT:** {get_task_limit()}"
            try:
                await reply.edit(status_message, buttons=[
                        [Button.inline('⭕ Close', 'close_settings')]])
            except MessageIdInvalidError:
                break
            except Exception as e:
                LOGGER.info(f"Status Update Error: {str(e)}")
            await asynciosleep(get_data()[user_id]['update_time'])
        LOGGER.info(f"Status Updating Complete")
        return


###############------Settings------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/settings', func=lambda e: user_auth_checker(e)))
async def _settings(event):
        user_id = event.message.sender.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        text = f"⚙ Hi {get_mention(event)} Choose Your Settings"
        await event.reply(text, buttons=[
        [Button.inline('#️⃣ General', 'general_settings')],
        [Button.inline('❣ Telegram', 'telegram_settings')],
        [Button.inline('📝 Progress Bar', 'progress_settings')],
        [Button.inline('🏮 Compression', 'compression_settings')],
        [Button.inline('🛺 Watermark', 'watermark_settings')],
        [Button.inline('⭕Close Settings', 'close_settings')]
    ])
        return

###############------Watermark------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/watermark', func=lambda e: user_auth_checker(e)))
async def _add_watermark_to_video(event):
        chat_id = event.message.chat.id
        user_id = event.message.sender.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        check_watermark = await ask_watermark(event, chat_id, user_id, "watermark", True)
        if not check_watermark:
            await event.reply("❗Failed To Get Watermark.")
            return
        link, custom_file_name = await get_link(event)
        if link=="invalid":
            await event.reply("❗Invalid link")
            return
        elif not link:
            new_event = await ask_media_OR_url(event, chat_id, user_id, ["/watermark", "stop"], "Send Video or URL", 120, "video/", True)
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event)
            else:
                return
        user_name = get_username(event)
        user_first_name = event.message.sender.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, event, Names.watermark, custom_file_name)
        await get_thumbnail(process_status, ["/watermark", "pass"], 120)
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]])
        create_task(add_task(task))
        await event.reply("✅Task Added\n\nCheck /status")
        return


###############------Merge_Videos------###############
@TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/merge', func=lambda e: user_auth_checker(e)))
async def _merge_videos(event):
        chat_id = event.message.chat.id
        user_id = event.message.sender.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        custom_file_name = await get_custom_name(event)
        user_name = get_username(event)
        user_first_name = event.message.sender.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, event, Names.merge, custom_file_name)
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        file_index = 1
        Cancel = False
        while True:
            new_event = await ask_media_OR_url(event, chat_id, user_id, ["/merge", "stop", "cancel"], f"Send Video or URL No {file_index}", 120, "video/", False, message_hint=f"🔷Send `stop` To Process Merge\n🔷Send `cancel` To Cancel Merge Process", allow_command=True)
            if new_event and new_event not in ["cancelled", "stopped", "pass"]:
                link = await get_url_from_message(new_event)
                if type(link)==str:
                    task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
                else:
                    task['functions'].append(["TG", [link]])
                file_index+=1
            elif new_event=="stopped":
                break
            elif new_event=="cancelled":
                Cancel = True
                break
        if Cancel:
            del process_status
            return
        if len(task['functions'])<2:
            del process_status
            await event.reply("❗Atleast 2 Files Required To Merge")
            return
        await get_thumbnail(process_status, ["/merge", "pass"], 120)
        create_task(add_task(task))
        await event.reply("✅Task Added\n\nCheck /status")
        return