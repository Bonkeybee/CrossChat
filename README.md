#Requirements:
[python 3.9+](https://www.python.org/downloads/)
<br>
python -m pip install --upgrade pip
<br>
pip install pipenv
<br>
pipenv shell
<br>
pipenv install
<br>
pipenv run python crosschat.py

#Dependencies:
`pip install pipenv`
<br>
`pipenv install`

#Configuration:
Rename `config.sample` to `config.ini` and make any necessary changes.

###wow

`game_path` your absolute path to the World of Warcraft executable
<br>
`addon_path` your absolute path to the World of Warcraft interface addons folder
<br>
`guild_chat_log_file` your absolute path to your World of Warcraft realm saved variables folder for GuildChatLogger
<br>
`officer_chat_log_file` your absolute path to your World of Warcraft realm saved variables folder for OfficerChatLogger
<br>
`system_chat_log_file` your absolute path to your World of Warcraft realm saved variables folder for SystemChatLogger
<br>
`lfg_chat_log_file` your absolute path to your World of Warcraft realm saved variables folder for LFGChatLogger
<br>
`password` your World of Warcraft password
<br>
`loop_amount` the loop count before restarting the script
###discord

`token` your Discord bot token
<br>
`guild_chat_webhook_url` your Discord integration webhook URL for guild chat
<br>
`officer_chat_webhook_url` your Discord integration webhook URL for officer chat
<br>
`system_chat_webhook_url` your Discord integration webhook URL for system chat
<br>
`lfg_chat_webhook_url` your Discord integration webhook URL for lfg chat
<br>
`guild_id` your Discord guild ID
<br>
`admin_id` your Discord account ID
<br>
`admin_role` your Discord admin/moderator role ID
<br>
`member_role` your Discord member role ID
<br>
`tank_role` your Discord tank role ID
<br>
`heal_role` your Discord heal role ID
<br>
`dps_role` your Discord dps role ID
<br>
`guild_crosschat_channel_id` your designated Discord guild CROSSCHAT channel id
<br>
`officer_crosschat_channel_id` your designated Discord officer CROSSCHAT channel id
<br>
`lfg_crosschat_channel_id` your designated Discord LFG CROSSCHAT channel id
<br>
`skull_emoji` your Discord emoji replacement for World of Warcraft's skull icon
<br>
`cross_emoji` your Discord emoji replacement for World of Warcraft's skull icon
<br>
`square_emoji` your Discord emoji replacement for World of Warcraft's skull icon
<br>
`moon_emoji` your Discord emoji replacement for World of Warcraft's skull icon
<br>
`triangle_emoji` your Discord emoji replacement for World of Warcraft's skull icon
<br>
`diamond_emoji` <your Discord emoji replacement for World of Warcraft's skull icon
<br>
`circle_emoji` your Discord emoji replacement for World of Warcraft's skull icon
<br>
`star_emoji` your Discord emoji replacement for World of Warcraft's skull icon

###state

`guild_timestamp` the initial World of Warcraft timestamp to start reading guild chat from
<br>
`officer_timestamp` the initial World of Warcraft timestamp to start reading officer chat from
<br>
`lfg_embed_message_id` the Discord message id of the LFG embed
<br>
`lfg_timestamp` the last timestamp LFG was updated at

#Execution:
Launch AHK script and press `CTRL+R` followed by `CTRL+Q`
<br>
`CTRL+R` will reload the AHK script and pull from this repo to update.
<br>
`CTRL+Q` will start World of Warcraft and the CROSSCHAT services.
<br>
`CTRL+E` will restart the in-game reloading process without restarting World of Warcraft.
