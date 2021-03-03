#SingleInstance force
CoordMode, Mouse, Window
SetKeyDelay, 100, 100


sleep(min, max*) {
	if not max[1] {
		Random, randsleep, min, min+1000
		Sleep, %randsleep%
	} else {
		Random, randsleep, min, max[1]
		Sleep, %randsleep%
	}
}

close() {
	Loop {
		didclose = false
		if WinExist("crosschat-discord") {
			WinClose, crosschat-discord
			didclose = true
		}
		if WinExist("crosschat-game") {
			WinClose, crosschat-game
			didclose = true
		}
		if WinExist("World of Warcraft") {
			WinClose, World of Warcraft
			didclose = true
		}
		if %didclose% {
			sleep(1000)
		}
	} Until not %didclose%
}

open() {
	Loop {
		didopen = false
		if not WinExist("crosschat-discord") {
			Run, crosschat-discord.py
			didopen = true
		}
		if not WinExist("crosschat-game") {
			Run, crosschat-game.py
			didopen = true
		}
		if not WinExist("World of Warcraft") {
			IniRead, gamepath, config.ini, wow, GAME_PATH
			Run, %gamepath%
			didopen = true
		}
		if %didopen% {
			sleep(1000)
		}
	} Until not %didopen%
}

launch() {
	close()
	open()
	sleep(3000) ;Wait for programs to open
}

login() {
	launch() ;Close and open the processes
	IniRead, password, config.ini, wow, PASSWORD
	ControlSendRaw,, %password%, World of Warcraft
	ControlSend,, {Enter}, World of Warcraft
	sleep(30000) ;Wait for login
	ControlSend,, {Enter}, World of Warcraft
	sleep(10000) ;Wait for entering world
}

relog() {
	ControlSend,, 2, World of Warcraft
	sleep(2000) ;Wait for logout
	ControlSend,, {Enter}, World of Warcraft
	sleep(10000) ;Wait for entering world
}

reload() {
	ControlSend,, 1, World of Warcraft
	sleep(10000) ;Wait for reloading
}

crosschat() {
	if FileExist("crosschat.txt") {
		Loop {
			FileReadLine, line, crosschat.txt, %A_Index%
			if ErrorLevel
				break
			Clipboard := ("/g " + line)
			ClipWait
			ControlSend,, {Enter}{Control Down}v{Control Up}{Enter}, World of Warcraft
			sleep(100, 200) ;Wait for all copied text to paste
		}
		FileDelete, crosschat.txt
		sleep(1000) ;Wait for file to be deleted
	}
}

main(login) {
	if login
	{
		login()  ;Login to the game
	}
	IniRead, loopamount, config.ini, wow, LOOP_AMOUNT
	While True {
		Loop, %loopamount% { ;Loop sometime before relogging
			reload() ;Flush chatlog to file to be read by external script
			crosschat() ;Copy text from discord in-game
		}
		sleep(1000)
		login() ;Login to the game
	}
}

^Esc:: ;CTRL-ESC
	Pause
return
^q:: ;CTRL-Q
	main(true) ;Close, open, and login
return
^e:: ;CTRL-E
	main(false) ;Restarts reload loop
return
^r:: ;CTRL-R
	Run, git-pull.py ;Pulls the latest from the repository
	Reload ;Reloads the script
return
