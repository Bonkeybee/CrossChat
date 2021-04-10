LFGCHATLOGGER_ADDON_NAME, GUILDCHATLOGGER = ...
LFGCHATLOGGER.VERSION = GetAddOnMetadata(LFGCHATLOGGER_ADDON_NAME, "Version")
LFGCHATLOGGER.FRAME = CreateFrame("Frame")


local MESSAGE_KEEP_DURATION_S = 60 * 60 * 3


local function GetTimestamp()
  return tonumber(GetServerTime().."."..(GetTime()*1000))
end

local function onEvent(_, event, message, author, language, channel)
  -- Do not log empty messages
  if (not message) then
    return
  end

  -- Do not log non-LFG messages
  if (not strfind(channel, "LookingForGroup")) then
    return
  end

  -- Simplify the message author name
  local name = author
  if (name) then
    name = strsplit("-", author)
  end

  -- Load or create the saved variable
  if (not LFGCHATLOG) then
    LFGCHATLOG = {}
  end

  -- Save the message
  LFGCHATLOG[GetTimestamp()] = {name, message}

  -- Clean up older messages
  for timestamp,data in pairs(LFGCHATLOG) do
    if (tonumber((timestamp) + MESSAGE_KEEP_DURATION_S) < GetTimestamp()) then
      LFGCHATLOG[timestamp] = nil
    end
  end
end


LFGCHATLOGGER.FRAME:RegisterEvent("CHAT_MSG_CHANNEL")
LFGCHATLOGGER.FRAME:SetScript("OnEvent", onEvent)
JoinChannelByName("LookingForGroup")
