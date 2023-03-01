from bot_helper.Database.DB_Handler import Database
from config.config import Config
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters
from bot_helper.Others.Helper_Functions import get_human_size, get_size


#////////////////////////////////////Variables////////////////////////////////////#
if Config.SAVE_TO_DATABASE:
    db = Database()
    save_id = Config.SAVE_ID
DATA = Config.DATA
LOGGER = Config.LOGGER
TASK_LIMIT = Config.RUNNING_TASK_LIMIT


#////////////////////////////////////Task_Limit////////////////////////////////////#

###############------Return_Task_Limit------###############
def get_task_limit():
    return TASK_LIMIT

def change_task_limit(new_limit):
    global TASK_LIMIT
    TASK_LIMIT = new_limit
    return


#////////////////////////////////////Database////////////////////////////////////#

###############------Return_Database------###############
def get_data():
    return DATA

###############------New_User------###############
async def new_user(user_id, dbsave):
        DATA[user_id] = {}
        DATA[user_id]['watermark'] = {}
        DATA[user_id]['watermark']['position'] = '5:5'
        DATA[user_id]['watermark']['size'] = '15'
        DATA[user_id]['watermark']['crf'] = '23'
        DATA[user_id]['watermark']['use_queue_size'] = False
        DATA[user_id]['watermark']['queue_size'] = '9999'
        DATA[user_id]['watermark']['use_crf'] = False
        DATA[user_id]['watermark']['encode'] = True
        DATA[user_id]['watermark']['encoder'] = 'libx265'
        DATA[user_id]['watermark']['preset'] = 'ultrafast'
        DATA[user_id]['watermark']['map_audio'] = True
        DATA[user_id]['watermark']['copy_sub'] = True
        DATA[user_id]['watermark']['map'] = True
        DATA[user_id]['watermark']['sync'] = False
        DATA[user_id]['softmux'] = {}
        DATA[user_id]['softmux']['preset'] = 'ultrafast'
        DATA[user_id]['softmux']['use_crf'] = False
        DATA[user_id]['softmux']['crf'] = '23'
        DATA[user_id]['softmux']['sub_codec'] = 'copy'
        DATA[user_id]['softmux']['map_audio'] = False
        DATA[user_id]['softmux']['map_sub'] = False
        DATA[user_id]['softmux']['map'] = False
        DATA[user_id]['softmux']['encode'] = False
        DATA[user_id]['softmux']['encoder'] = 'libx265'
        DATA[user_id]['softremux'] = {}
        DATA[user_id]['softremux']['preset'] = 'ultrafast'
        DATA[user_id]['softremux']['use_crf'] = False
        DATA[user_id]['softremux']['crf'] = '23'
        DATA[user_id]['softremux']['sub_codec'] = 'copy'
        DATA[user_id]['softremux']['map_audio'] = False
        DATA[user_id]['softremux']['map_sub'] = False
        DATA[user_id]['softremux']['map'] = False
        DATA[user_id]['softremux']['encode'] = False
        DATA[user_id]['softremux']['encoder'] = 'libx265'
        DATA[user_id]['hardmux'] = {}
        DATA[user_id]['hardmux']['preset'] = 'ultrafast'
        DATA[user_id]['hardmux']['crf'] = '23'
        DATA[user_id]['hardmux']['encode_video'] = True
        DATA[user_id]['hardmux']['encoder'] = 'libx265'
        DATA[user_id]['hardmux']['use_queue_size'] = False
        DATA[user_id]['hardmux']['queue_size'] = '9999'
        DATA[user_id]['hardmux']['sync'] = False
        DATA[user_id]['compress'] = {}
        DATA[user_id]['compress']['preset'] = 'ultrafast'
        DATA[user_id]['compress']['crf'] = '23'
        DATA[user_id]['compress']['use_queue_size'] = False
        DATA[user_id]['compress']['sync'] = False
        DATA[user_id]['compress']['queue_size'] = '9999'
        DATA[user_id]['compress']['map_audio'] = True
        DATA[user_id]['compress']['map_sub'] = True
        DATA[user_id]['compress']['map'] = True
        DATA[user_id]['compress']['copy_sub'] = False
        DATA[user_id]['compress']['encoder'] = 'libx265'
        DATA[user_id]['compression'] = False
        DATA[user_id]['select_stream'] = False
        DATA[user_id]['stream'] = 'ENG'
        DATA[user_id]['split_video'] = False
        DATA[user_id]['split'] = '2GB'
        DATA[user_id]['upload_tg'] = True
        DATA[user_id]['rclone'] = False
        DATA[user_id]['rclone_config_link'] = False
        DATA[user_id]['drive_name'] = False
        DATA[user_id]['merge'] = {}
        DATA[user_id]['merge']['map_audio'] = True
        DATA[user_id]['merge']['map_sub'] = True
        DATA[user_id]['merge']['map'] = True
        DATA[user_id]['merge']['fix_blank'] = False
        DATA[user_id]['custom_thumbnail'] = False
        DATA[user_id]['convert_video'] = False
        DATA[user_id]['convert_quality'] = [720, 480]
        DATA[user_id]['convert'] = {}
        DATA[user_id]['convert']['preset'] = 'ultrafast'
        DATA[user_id]['convert']['use_crf'] = False
        DATA[user_id]['convert']['crf'] = '23'
        DATA[user_id]['convert']['map'] = True
        DATA[user_id]['convert']['encode'] = True
        DATA[user_id]['convert']['encoder'] = 'libx265'
        DATA[user_id]['convert']['copy_sub'] = False
        DATA[user_id]['convert']['use_queue_size'] = False
        DATA[user_id]['convert']['sync'] = False
        DATA[user_id]['convert']['queue_size'] = '9999'
        DATA[user_id]['convert']['convert_list'] = [720, 480]
        DATA[user_id]['custom_name'] = False
        DATA[user_id]['custom_metadata'] = False
        DATA[user_id]['metadata'] = "Nik66Bots"
        DATA[user_id]['detailed_messages'] = True
        DATA[user_id]['show_stats'] = True
        DATA[user_id]['show_botuptime'] = True
        DATA[user_id]['update_time'] = 7
        DATA[user_id]['ffmpeg_log'] = True
        DATA[user_id]['ffmpeg_size'] = True
        DATA[user_id]['ffmpeg_ptime'] = True
        DATA[user_id]['auto_drive'] = False
        DATA[user_id]['show_time'] = True
        DATA[user_id]['gen_ss'] = True
        DATA[user_id]['ss_no'] = 5
        DATA[user_id]['gen_sample'] = False
        DATA[user_id]['tgdownload'] = "Telethon"
        DATA[user_id]['tgupload'] = "Telethon"
        DATA[user_id]['upload_all'] = True
        if dbsave:
            data = await db.save_data(str(DATA))
        else:
            data = True
        return data

###############------Save_Config------###############
async def saveoptions(user_id, dname, value, dbsave):
    try:
        if user_id not in DATA:
            DATA[user_id] = {}
            DATA[user_id][dname] = {}
            DATA[user_id][dname] = value
        else:
            DATA[user_id][dname] = value
        if dbsave:
            data = await db.save_data(str(DATA))
        else:
            data = True
        return data
    except Exception as e:
        LOGGER.info(e)
        return False

###############------Reset_Database------###############
async def resetdatabase(dbsave):
    try:
        DATA.clear()
        if dbsave:
            await db.save_data(str(DATA))
        return True
    except Exception as e:
        LOGGER.info(e)
        return False

###############------Save_Sub_Config------###############
async def saveconfig(user_id, dname, pos, value, dbsave):
    try:
        if user_id not in DATA:
            DATA[user_id] = {}
            DATA[user_id][dname] = {}
            DATA[user_id][dname][pos] = value
        else:
            DATA[user_id][dname][pos] = value
        if dbsave:
            data = await db.save_data(str(DATA))
        else:
            data = True
        return data
    except Exception as e:
        LOGGER.info(e)
        return False

###############------Save_Restart_IDs------###############
async def save_restart(chat_id, msg_id):
    try:
        if 'restart' not in DATA:
            DATA['restart'] = []
            DATA['restart'].append([chat_id, msg_id])
        else:
            DATA['restart'].append([chat_id, msg_id])
        await db.save_data(str(DATA))
        return
    except Exception as e:
        LOGGER.info(e)
        return False
    
###############------Clear_Restart_IDs------###############
async def clear_restart():
    try:
        DATA['restart'] = []
        await db.save_data(str(DATA))
        return
    except Exception as e:
        LOGGER.info(e)
        return False



#////////////////////////////////////Database////////////////////////////////////#
###############------Get_Bot_Stats------###############
def get_stats(userx):
        if DATA[userx]['show_stats']:
            total, used, free, disk = disk_usage('/')
            memory = virtual_memory()
            stats =f'🚀CPU Usage: {cpu_percent(interval=0.5)}%\n'\
                        f'⚡RAM Usage: {memory.percent}%\n'\
                        f'🚛Total Space: {get_human_size(total)}\n'\
                        f'🧡Free Space: {get_human_size(free)}\n'\
                        f'🚂Total Ram: {get_human_size(memory.total)}\n'\
                        f'⚓Free Ram: {get_human_size(memory.available)}'
        else:
            stats =f'🚀CPU Usage: {cpu_percent(interval=0.5)}%'
        return stats


###############------Get_Stats_Message------###############
def get_host_stats():
        total, used, free, disk = disk_usage('/')
        swap = swap_memory()
        memory = virtual_memory()
        stats =f'<b>Total Disk Space:</b> {get_size(total)}\n'\
                    f'<b>Used:</b> {get_size(used)} | <b>Free:</b> {get_size(free)}\n\n'\
                    f'<b>Upload:</b> {get_size(net_io_counters().bytes_sent)}\n'\
                    f'<b>Download:</b> {get_size(net_io_counters().bytes_recv)}\n\n'\
                    f'<b>CPU:</b> {cpu_percent(interval=0.5)}%\n'\
                    f'<b>RAM:</b> {memory.percent}%\n'\
                    f'<b>DISK:</b> {disk}%\n\n'\
                    f'<b>Physical Cores:</b> {cpu_count(logical=False)}\n'\
                    f'<b>Total Cores:</b> {cpu_count(logical=True)}\n\n'\
                    f'<b>SWAP:</b> {get_size(swap.total)} | <b>Used:</b> {swap.percent}%\n'\
                    f'<b>Memory Total:</b> {get_size(memory.total)}\n'\
                    f'<b>Memory Free:</b> {get_size(memory.available)}\n'\
                    f'<b>Memory Used:</b> {get_size(memory.used)}'
        return stats


###############------Detailed_Message------###############
def get_details(pmode, userx, head):
    if DATA[userx]['detailed_messages']:
        if pmode=="compress":
            compress_encoder = DATA[userx]['compress']['encoder']
            compress_preset = DATA[userx]['compress']['preset']
            compress_crf = DATA[userx]['compress']['crf']
            compress_map = DATA[userx]['compress']['map']
            compress_copysub = DATA[userx]['compress']['copy_sub']
            compress_use_queue_size = DATA[userx]['compress']['use_queue_size']
            compress_queue_size = DATA[userx]['compress']['queue_size']
            if compress_use_queue_size:
                qsize_text = f"🎹Queue Size: {str(compress_queue_size)}"
            else:
                qsize_text = f"📻Use Queue Size: False"
            text =f'🍬Encoder: {compress_encoder}\n'\
                            f'♒Preset: {compress_preset}\n'\
                            f'⚡CRF: {compress_crf}\n'\
                            f'🍓Map: {compress_map}\n'\
                            f'{qsize_text}\n'\
                            f'🍄Copy Subtitles: {compress_copysub}'
            if head:
                text = f'Compression Settings:\n{text}'
            else:
                text = f'🍫Mode: Compression\n{text}'
            return text
        
        elif pmode=="merge":
            merge_map = get_data()[userx]['merge']['map']
            text =f'🍓Map: {merge_map}'
            if head:
                text = f'Merge Settings:\n{text}'
            else:
                text = f'🍫Mode: Merge\n{text}'
            return text
        
        elif pmode=="watermark":
            watermark_position = DATA[userx]['watermark']['position']
            watermark_size = DATA[userx]['watermark']['size']
            watermark_encoder = DATA[userx]['watermark']['encoder']
            watermark_preset = DATA[userx]['watermark']['preset']
            watermark_crf = DATA[userx]['watermark']['crf']
            watermark_map = DATA[userx]['watermark']['map']
            watermark_copysub = DATA[userx]['watermark']['copy_sub']
            watermark_encode = DATA[userx]['watermark']['encode']
            watermark_use_queue_size = DATA[userx]['watermark']['use_queue_size']
            watermark_queue_size = DATA[userx]['watermark']['queue_size']
            if watermark_use_queue_size:
                qsize_text = f"🎹Queue Size: {str(watermark_queue_size)}"
            else:
                qsize_text = f"📻Use Queue Size: False"
            if watermark_encode:
                encode_text = f"{watermark_encoder}"
            else:
                encode_text = f"False"
            text =f'🥽Position: {watermark_position}\n'\
                            f'🛸Size: {watermark_size}\n'\
                            f'🍬Encoder: {encode_text}\n'\
                            f'♒Preset: {watermark_preset}\n'\
                            f'⚡CRF: {watermark_crf}\n'\
                            f'🍓Map: {watermark_map}\n'\
                            f'{qsize_text}\n'\
                            f'🍄Copy Subtitles: {watermark_copysub}'
            if head:
                text = f'Watermark Settings:\n{text}'
            else:
                text = f'🍫Mode: Watermark\n{text}'
            return text
    else:
        return False