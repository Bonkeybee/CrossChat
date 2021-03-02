GUILDCHATLOGGER_ADDON_NAME, GUILDCHATLOGGER = ...
GUILDCHATLOGGER.VERSION = GetAddOnMetadata(GUILDCHATLOGGER_ADDON_NAME, "Version")
GUILDCHATLOGGER.FRAME = CreateFrame("Frame")


local function GetTimestamp()
  return tonumber(GetServerTime().."."..(GetTime()*1000))
end

local function onEvent(_, event, message, author)
  -- Do not log empty messages
  if (not message) then
    return
  end

  -- Do not log messages sent by the player
  if (author) then
    name, realm = strsplit("-", author)
    -- if (name == UnitName("player")) then
    --   return
    -- end
  end

  if (not GUILDCHATLOG) then
    GUILDCHATLOG = {}
  end

  if (event == "CHAT_MSG_GUILD") then
    if (not GUILDCHATLOG) then
      GUILDCHATLOG = {}
    end
    for timestamp,data in pairs(GUILDCHATLOG) do
      if (tonumber((timestamp + 10800)) < GetTimestamp()) then
        GUILDCHATLOG[timestamp] = nil
      end
    end
    GUILDCHATLOG[GetTimestamp()] = {name, message}
  end
end


GUILDCHATLOGGER.FRAME:RegisterEvent("CHAT_MSG_GUILD")
GUILDCHATLOGGER.FRAME:SetScript("OnEvent", onEvent)
