SYSTEMCHATLOGGER_ADDON_NAME, SYSTEMCHATLOGGER = ...
SYSTEMCHATLOGGER.VERSION = GetAddOnMetadata(SYSTEMCHATLOGGER_ADDON_NAME, "Version")
SYSTEMCHATLOGGER.FRAME = CreateFrame("Frame")


local MESSAGE_KEEP_DURATION_S = 60 * 60 * 3


local function GetTimestamp()
  return tonumber(GetServerTime().."."..(GetTime()*1000))
end

local function onEvent(_, event, message)
  -- Do not log empty messages
  if (not message) then
    return
  end

  -- Filter useless messages
  if (strfind(message, "Guild created")) then
	return
  end
  if (strfind(message, "Guild:")) then
	return
  end
  if (strfind(message, "has invited you to join a group.")) then
    return
  end
  if (strfind(message, "invites you to join")) then
    return
  end
  if (strfind(message, "Discovered")) then
    return
  end

  -- Load or create the saved variable
  if (not SYSTEMCHATLOG) then
    SYSTEMCHATLOG = {}
  end

  -- Save the message
  SYSTEMCHATLOG[GetTimestamp()] = {"SYSTEM", message}

  -- Clean up older messages
  for timestamp,data in pairs(SYSTEMCHATLOG) do
    if (tonumber((timestamp) + MESSAGE_KEEP_DURATION_S) < GetTimestamp()) then
      SYSTEMCHATLOG[timestamp] = nil
    end
  end
end


SYSTEMCHATLOGGER.FRAME:RegisterEvent("CHAT_MSG_SYSTEM")
SYSTEMCHATLOGGER.FRAME:SetScript("OnEvent", onEvent)
