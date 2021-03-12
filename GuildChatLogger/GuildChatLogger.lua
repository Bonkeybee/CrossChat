GUILDCHATLOGGER_ADDON_NAME, GUILDCHATLOGGER = ...
GUILDCHATLOGGER.VERSION = GetAddOnMetadata(GUILDCHATLOGGER_ADDON_NAME, "Version")
GUILDCHATLOGGER.FRAME = CreateFrame("Frame")


local MESSAGE_KEEP_DURATION_S = 60 * 60 * 3


local function GetTimestamp()
  return tonumber(GetServerTime().."."..(GetTime()*1000))
end

local function onEvent(_, event, message, author)
  -- Do not log empty messages
  if (not message) then
    return
  end

  -- Simplify the message author name
  local name = author
  if (name) then
    name = strsplit("-", author)
  end

  -- Load or create the saved variable
  if (not GUILDCHATLOG) then
    GUILDCHATLOG = {}
  end

  -- Save the message
  GUILDCHATLOG[GetTimestamp()] = {name, message}

  -- Clean up older messages
  for timestamp,data in pairs(GUILDCHATLOG) do
    if (tonumber((timestamp) + MESSAGE_KEEP_DURATION_S) < GetTimestamp()) then
      GUILDCHATLOG[timestamp] = nil
    end
  end
end


GUILDCHATLOGGER.FRAME:RegisterEvent("CHAT_MSG_GUILD")
GUILDCHATLOGGER.FRAME:SetScript("OnEvent", onEvent)
