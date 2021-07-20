#Requirements:
[python 3.9+](https://www.python.org/downloads/)

#Dependencies:
`pip install pipenv`

`pipenv install`

#Configuration:
Rename `config.sample` to `config.ini` and make any necessary changes.

###wow

`game_path` your absolute path to the World of Warcraft executable

`addon_path` your absolute path to the World of Warcraft interface addons folder

`guild_chat_log_file` your absolute path to your World of Warcraft realm saved variables folder for GuildChatLogger

`officer_chat_log_file` your absolute path to your World of Warcraft realm saved variables folder for OfficerChatLogger

`system_chat_log_file` your absolute path to your World of Warcraft realm saved variables folder for SystemChatLogger

`lfg_chat_log_file` your absolute path to your World of Warcraft realm saved variables folder for LFGChatLogger

`password` your World of Warcraft password

`loop_amount` the loop count before restarting the script

###discord

`token` your Discord bot token

`guild_chat_webhook_url` your Discord integration webhook URL for guild chat

`officer_chat_webhook_url` your Discord integration webhook URL for officer chat

`system_chat_webhook_url` your Discord integration webhook URL for system chat

`lfg_chat_webhook_url` your Discord integration webhook URL for lfg chat

`guild_id` your Discord guild ID

`admin_id` your Discord account ID

`admin_role` your Discord admin/moderator role ID

`member_role` your Discord member role ID

`tank_role` your Discord tank role ID

`heal_role` your Discord heal role ID

`dps_role` your Discord dps role ID

`guild_crosschat_channel_id` your designated Discord guild CROSSCHAT channel id

`officer_crosschat_channel_id` your designated Discord officer CROSSCHAT channel id

`lfg_crosschat_channel_id` your designated Discord LFG CROSSCHAT channel id

`skull_emoji` your Discord emoji replacement for World of Warcraft's skull icon

`cross_emoji` your Discord emoji replacement for World of Warcraft's skull icon

`square_emoji` your Discord emoji replacement for World of Warcraft's skull icon

`moon_emoji` your Discord emoji replacement for World of Warcraft's skull icon

`triangle_emoji` your Discord emoji replacement for World of Warcraft's skull icon

`diamond_emoji` <your Discord emoji replacement for World of Warcraft's skull icon

`circle_emoji` your Discord emoji replacement for World of Warcraft's skull icon

`star_emoji` your Discord emoji replacement for World of Warcraft's skull icon

###state

`guild_timestamp` the initial World of Warcraft timestamp to start reading guild chat from

`officer_timestamp` the initial World of Warcraft timestamp to start reading officer chat from

`lfg_embed_message_id` the Discord message id of the LFG embed

`lfg_timestamp` the last timestamp LFG was updated at

#Execution:
Launch AHK script and press `CTRL+R` followed by `CTRL+Q`

`CTRL+R` will reload the AHK script and pull from this repo to update.

`CTRL+Q` will start World of Warcraft and the CROSSCHAT services.

`CTRL+E` will restart the in-game reloading process without restarting World of Warcraft.
