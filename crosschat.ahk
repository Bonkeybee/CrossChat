#SingleInstance force
CoordMode, Mouse, Window
SetKeyDelay, 100, 100


sleep(min, max*) {
	if (!max[1]) {
		Random, randsleep, min, min+1000
		Sleep, %randsleep%
	} else {
		Random, randsleep, min, max[1]
		Sleep, %randsleep%
	}
}

launch() {
	WinClose, crosschat-discord
	WinClose, crosschat-game
	WinClose, World of Warcraft
	sleep(2000) ;Wait for things to close
	Run, "C:\Users\prs10\Desktop\CrossChat\crosschat-discord.py"
	Run, "C:\Users\prs10\Desktop\CrossChat\crosschat-game.py"
	Run, "C:\Program Files (x86)\World of Warcraft\_classic_\WowClassic.exe"
	sleep(6000) ;Wait for programs to open
}

login() {
	launch()
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
	If (login)
	{
		login()
	}
	IniRead, loopamount, config.ini, wow, LOOP_AMOUNT
	While True {
		Loop, %loopamount% { ;Loop 300 times before relogging
			reload() ;Flush chatlog to file to be read by external script
			crosschat() ;Copy text from discord in-game
		}
		login()
	}
}

^Esc::
	Pause
return
^q::
	main(true)
return
^e::
	main(false)
return
^r::
	Reload
return
