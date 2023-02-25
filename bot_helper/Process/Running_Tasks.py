from asyncio import Lock
from config.config import Config
from asyncio import create_task, create_subprocess_exec, sleep
from asyncio.subprocess import PIPE as asyncioPIPE
from bot_helper.Telegram.Telegram_Client import Telegram
from bot_helper.Process.Running_Process import append_running_process, remove_running_process, check_running_process
from shutil import rmtree
from bot_helper.Others.Names import Names
from bot_helper.FFMPEG.FFMPEG_Commands import get_commands
from bot_helper.FFMPEG.FFMPEG_Status import FfmpegStatus
from bot_helper.Database.User_Data import get_task_limit, get_data
from os.path import isfile
from time import time
from bot_helper.FFMPEG.FFMPEG_Processes import FFMPEG
from os.path import exists
from bot_helper.Others.Helper_Functions import verify_rclone_account
from bot_helper.Rclone.Rclone_Upload import upload_drive
from os import remove


async def clear_trash(task, trash_objects):
    async with working_task_lock:
        working_task.remove(task)
    await remove_running_process(task['process_status'].process_id)
    try:
        rmtree(task['process_status'].dir)
    except:
        pass
    del task['process_status']
    for trash in trash_objects:
        del trash
    del task
    return

async def upload_files(process_status):
    drive_uplaod = False
    if not get_data()[process_status.user_id]['upload_tg']:
        r_config = f'./userdata/{str(process_status.user_id)}_rclone.conf'
        if exists(r_config):
            drive_name = get_data()[process_status.user_id]['drive_name']
            if verify_rclone_account(r_config, drive_name):
                drive_uplaod = True
    if not drive_uplaod:
        await Telegram.upload_videos(process_status)
    else:
        await upload_drive(process_status)
    return


LOGGER = Config.LOGGER
working_task=[]
working_task_lock = Lock()
queued_task = []
queued_task_lock = Lock()



async def add_task(task):
    async with working_task_lock:
        if len(working_task)<get_task_limit():
            LOGGER.info(f"Add Task: Adding Task To Working")
            create_task(start_task(task))
            working_task.append(task)
        else:
            async with queued_task_lock:
                queued_task.append(task)
                LOGGER.info(f"Add Task: Adding Task To Queue")
    return


async def task_manager():
        async with working_task_lock:
            if len(working_task)<get_task_limit():
                async with queued_task_lock:
                    if len(queued_task):
                        task = queued_task[0]
                        LOGGER.info(f"Task Manager: Adding Task From Queue To Working")
                        create_task(start_task(task))
                        working_task.append(task)
                        queued_task.pop(0)
        return


async def refresh_tasks():
    while True:
        async with working_task_lock:
            if len(working_task)<get_task_limit():
                async with queued_task_lock:
                    if len(queued_task):
                        task = queued_task[0]
                        create_task(start_task(task))
                        working_task.append(task)
                        queued_task.pop(0)
                    else:
                        break
            else:
                break
        return


def get_queued_tasks_len():
        return len(queued_task)


async def get_status_message(reply):
                if not len(working_task) and not len(queued_task):
                        return False
                else:
                        retry = 0
                        if not len(working_task):
                            await reply.edit('⏳Waiting For Task To Start, Please Wait')
                            while True:
                                if len(working_task):
                                    break
                                if retry==30:
                                    break
                                await sleep(1)
                                retry+=1
                        if len(working_task):
                                final_status = ""
                                for task in working_task:
                                        final_status+= task['process_status'].status_message + "\n\n"
                                return final_status
                        else:
                            return False

def get_user_id(process_id):
    for task in working_task:
        if task['process_status'].process_id==process_id:
            return task['process_status'].user_id
    return False

async def start_task(task):
    process_status = task['process_status']
    process_status.update_start_time(time())
    await append_running_process(process_status.process_id)
    process_completed = False
    loop_range = len(task['functions'])
    trash_objects = []
    for i in range(loop_range):
        dw_index = f"{str(i+1)}/{str(loop_range)}"
        if task['functions'][i][0]==Names.aria:
            process_status.set_dw_index(dw_index)
            download, aria2_status = await task['functions'][i][1](*task['functions'][i][2])
            if not download:
                await process_status.event.reply(process_status.status_message)
                break
            trash_objects.append(aria2_status)
            await process_status.update_status(aria2_status)
            if aria2_status.process_status!=1:
                await process_status.event.reply(process_status.message)
                break
            else:
                process_status.move_dw_file(aria2_status.name())
        else:
            download = await Telegram.download_tg_file(process_status, task['functions'][i][1], dw_index)
            if not download:
                break
        if not check_running_process(process_status.process_id):
            break
        if i==loop_range-1:
            process_completed = True
    if process_completed and process_status.process_type in Names.FFMPEG_PROCESSES:
            process_completed = False
            if process_status.process_type!=Names.merge:
                    await FFMPEG.select_audio(process_status)
                    await FFMPEG.change_metadata(process_status)
            command, log_file, input_file, output_file, file_duration = get_commands(process_status)
            LOGGER.info(str(command))
            ffmpeg_process = await create_subprocess_exec(
                                                                                                                    *command,
                                                                                                                    stdout=asyncioPIPE,
                                                                                                                    stderr=asyncioPIPE,
                                                                                                                    )
            ffmpeg_status = FfmpegStatus(ffmpeg_process, log_file, input_file, output_file, file_duration)
            trash_objects.append(ffmpeg_status)
            while True:
                if isfile(log_file):
                    break
            await process_status.update_status(ffmpeg_status)
            if not check_running_process(process_status.process_id):
                ffmpeg_process.kill()
            else:
                await ffmpeg_process.wait()
                return_code = ffmpeg_process.returncode
                if return_code==0:
                        process_status.replace_send_files(output_file)
                        process_completed = True
                else:
                    with open(f"{process_status.dir}/FFMPEG_LOG.txt", "w", encoding="utf-8") as f:
                                f.write(str(ffmpeg_status.process_logs))
                    await process_status.event.client.send_file(process_status.chat_id, file=f"{process_status.dir}/FFMPEG_LOG.txt", allow_cache=False, reply_to=process_status.event.message, caption=f"❌{process_status.process_type} Process Error\n\nReturn Code: {return_code}\n\nFileName: {input_file.split('/')[-1]}")
                    remove(f"{process_status.dir}/FFMPEG_LOG.txt")
    if process_completed:
        await upload_files(process_status)
        if process_status.generate_sample_video:
                await FFMPEG.gen_sample_video(process_status)
        if process_status.generate_screenshoots:
                await FFMPEG.generate_ss(process_status)
    await clear_trash(task, trash_objects)
    await task_manager()
    return