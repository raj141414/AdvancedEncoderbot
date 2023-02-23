from time import time
from os import remove, mkdir
from shutil import rmtree
from asyncio import get_event_loop
from os.path import exists, isdir
from subprocess import PIPE as subprocessPIPE, STDOUT as subprocessSTDOUT
from subprocess import run as subprocessrun
from shlex import split as shlexsplit
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from typing import Tuple
from configparser import ConfigParser
from datetime import datetime
from pytz import timezone
from string import ascii_lowercase, digits
from random import choices
from config.config import Config


#////////////////////////////////////Variables////////////////////////////////////#
IST = timezone('Asia/Kolkata')
botStartTime = time()
LOGGER = Config.LOGGER



#////////////////////////////////////Functions////////////////////////////////////#

###############------Time_Functions------###############
def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


class Timer:
    def __init__(self, time_between=5):
        self.start_time = time()
        self.time_between = time_between

    def can_send(self):
        if time() > (self.start_time + self.time_between):
            self.start_time = time()
            return True
        return False

def get_time():
    return time()


def getbotuptime():
    return get_readable_time(time() - botStartTime)


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]


def get_current_time():
    return str(datetime.now(IST).strftime('%I:%M:%S %p (%d-%b)'))


def get_time_from_string(check_time):
    try:
        return datetime.strptime(check_time, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(IST).strftime('%I:%M:%S %p (%d-%b)')
    except:
        return check_time
    

###############------Size_Functions------###############
def get_human_size(num):
    base = 1024.0
    sufix_list = ['B','KB','MB','GB','TB','PB','EB','ZB', 'YB']
    for unit in sufix_list:
        if abs(num) < base:
            return f"{round(num, 2)} {unit}"
        num /= base

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


def hrb(value, digits= 2, delim= "", postfix=""):
    """Return a human-readable file size.
    """
    if value is None:
        return None
    chosen_unit = "B"
    for unit in ("KB", "MB", "GB", "TB"):
        if value > 1000:
            value /= 1024
            chosen_unit = unit
        else:
            break
    return f"{value:.{digits}f}" + delim + chosen_unit + postfix


#////////////////////////////////////File_System_Functions////////////////////////////////////#

###############------Delete_File------###############
async def delete_trash(file):
    try:
        remove(file)
    except:
        pass
    return

###############------Delete_Directory------###############
async def delete_all(dir):
    try:
        rmtree(dir)
    except:
        pass
    return


###############------Create_Progress_File------###############
async def create_process_file(file):
    if exists(file):
        remove(file)
    with open(file, 'w') as fp:
            pass
    return

###############------Make_Directory------###############
async def make_direc(direc):
    try:
        if not isdir(direc):
            mkdir(direc)
    except:
        pass
    return direc


###############------Check_File_Exists------###############
async def check_file_exists(file):
    if exists(file):
        return True
    else:
        return False
    

###############------Check_Files_Exists------###############
async def check_files_exists(files):
    for file in files:
        if not exists(file):
            return False
    return True


###############------Get_Logs_From_File------###############
def get_logs_msg(log_file):
    with open(log_file, 'r', encoding="utf-8") as f:
                logFileLines = f.read().splitlines()
    Loglines = ''
    ind = 1
    if len(logFileLines):
        while len(Loglines) <= 3000:
            Loglines = logFileLines[-ind]+'\n'+Loglines
            if ind == len(logFileLines): break
            ind += 1
        startLine = f"Generated Last {ind} Lines from {str(log_file)}: \n\n---------------- START LOG -----------------\n\n"
        endLine = "\n---------------- END LOG -----------------"
        return startLine+Loglines+endLine
    else:
        return "Currently there is no error log"


###############------Clear_Trash_List------###############
async def clear_trash_list(trash_list):
    for t in trash_list:
            try:
                remove(t)
                trash_list.remove(t)
            except:
                pass
    return


#////////////////////////////////////Commands////////////////////////////////////#

###############------Create_Background_Task------###############
async def create_backgroud_task(x):
    task = get_event_loop().create_task(x)
    return task



###############------Get_Media_Duration------###############
def get_video_duration(filename):
    result = subprocessrun(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocessPIPE,
        stderr=subprocessSTDOUT)
    try:
        duration = int(float(result.stdout))
    except:
        duration = 0
    return duration



###############------Get_Process_Output------###############
async def execute(cmnd: str) -> Tuple[str, str, int, int]:
    LOGGER.info(cmnd)
    cmnds = shlexsplit(cmnd)
    process = await create_subprocess_exec(
        *cmnds,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode('utf-8', 'replace').strip()



#////////////////////////////////////Other_Functions////////////////////////////////////#


###############------Rclone_Accounts------###############
async def get_config(file):
    try:
        config = ConfigParser(default_section=False)
        config.read(file, encoding="utf-8")
        accounts = []
        for d in config:
            if d:
                accounts.append(str(d))
        if len(accounts):
            return accounts
        else:
            return False
    except Exception as e:
        LOGGER.info(e)
        return False


###############------Get_Rclone_Account_Type------###############
async def get_account_type(file, drive_name):
    try:
        config = ConfigParser(default_section=False)
        config.read(file, encoding="utf-8")
        if drive_name in config:
            if "type" in config[drive_name]:
                return str(config[drive_name].get('type')).strip()
        return False
    except Exception as e:
        LOGGER.info(e)
        return False

###############------Verify_Rclone------###############
def verify_rclone_account(file, drive_name):
    try:
        config = ConfigParser(default_section=False)
        config.read(file, encoding="utf-8")
        if drive_name in config:
            return True
        return False
    except Exception as e:
        LOGGER.info(e)
        return False

###############------Generate_Random_String------###############
def gen_random_string(k):
    return str(''.join(choices(ascii_lowercase + digits, k=k)))


###############------Check_Process------###############
async def process_checker(check_data):
    for data in check_data:
        if data[0] not in data[1]:
            return False
    return True

###############------Get_Values_FFMPEG------###############
def get_value(dlist, dtype, value):
    if len(dlist):
        try:
            return dtype(dlist[-1].strip())
        except:
            return value
    else:
        return value
