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
	didclose := false
	Loop {
		if WinExist(crosschat-discord) {
			WinClose, crosschat-discord
			WinWaitClose, crosschat-discord
			didclose := true
		}
		if WinExist(crosschat-game) {
			WinClose, crosschat-game
			WinWaitClose, crosschat-game
			didclose := true
		}
		if WinExist(World Of Warcraft) {
			WinClose, World of Warcraft
			WinWaitClose, World Of Warcraft
			didclose := true
		}
		sleep(1000)
	} Until not didclose
}

open() {
	didopen := false
	Loop {
		if not WinExist(crosschat-discord) {
			Run, crosschat-discord.py
			WinWait, crosschat-discord
			didopen := true
		}
		if not WinExist(crosschat-game) {
			Run, crosschat-game.py
			WinWait, crosschat-game
			didopen := true
		}
		if not WinExist(World Of Warcraft) {
			IniRead, gamepath, config.ini, wow, GAME_PATH
			Run, %gamepath%
			WinWait, World of Warcraft
			didopen := true
		}
		sleep(1000)
	} Until not didopen
}

launch() {
	close()
	open()
	sleep(3000) ;Wait for programs to open
}

login() {
	launch() ;Close and relaunch the processes
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
		login() ;Login to the game
	}
}

^Esc::
	Pause
return
^q::
	main(true) ;CTRL-Q to close, relaunch, and login
return
^e::
	main(false) ;CTRL-E to relog
return
^r::
	Reload ;CTRL-R to reload the script
return
