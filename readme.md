# A Multi-Feature Telegram Bot


### Configuration
To configure this bot add the environment variables stated below. Or add them in [sample_config.env](./sample_config.env) and change the name to `config.env`. Or add the environment variable `CONFIG_FILE_URL` and put config.env direct url in it.
- `API_ID` - (Required)Get it by creating an app on [https://my.telegram.org](https://my.telegram.org)
- `API_HASH` - (Required)Get it by creating an app on [https://my.telegram.org](https://my.telegram.org)
- `TOKEN` - (Required)Get it by creating a bot on [https://t.me/BotFather](https://t.me/BotFather)
- `SUDO_USERS` - (Required)Numerical User IDs of sudo users separated by space.
- `RESTART_NOTIFY_ID` - (Optional)Numerical user id of user or chat id of group/channel to notify on bot start, set it False if you don't want notification on start.
- `RUNNING_TASK_LIMIT` - (Required)Number Of Concurrent Tasks.
- `UNFINISHED_PROGRESS_STR` - (Required)Unfinished progress bar string value.
- `FINISHED_PROGRESS_STR` - (Required)Finished progress bar string value.
- `SAVE_TO_DATABASE` - (Required)Set value True if you want to use MongoDB Database else False.
- `MONGODB_URI` - (Optional*)MongoDB URL to save data, only required when SAVE_TO_DATABASE's value is True.
- `Use_Session_String` - (Required)Set value True if you want to use Telegram user session string to upload 4GB file to telegram else False.
- `Session_String` - (Optional*)Telethon Session String, only required when Use_Session_String's value is True.

### Commands
```
compress - Compress Video
merge - Merge Video
watermark - Add Watermark To Video
convert - Convert Video
hardmux - Hardmux Video
softmux - Softmux Video
softremux - Softremux Video
savewatermark - Save Watermark Image
saveconfig - Save Rclone Config
tasklimit - Change Task Limit
status - Check Process Status
log - Get Log Message
logs - Get Log File
renew - Renew Storage
resetdb - Reset Database
time - Get Bot Uptime
stats - Get Stats
speedtest - SpeedTest
settings - Settings Section
restart - Restart Bot
```



### Copyright & License
- Copyright &copy; 2023 &mdash; [Nik66](https://github.com/sahilgit55)
- Licensed under the terms of the [GNU General Public License Version 3 &dash; 29 June 2007](./LICENSE)