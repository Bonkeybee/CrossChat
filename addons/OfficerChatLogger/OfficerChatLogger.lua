OFFICERCHATLOGGER_ADDON_NAME, OFFICERCHATLOGGER = ...
OFFICERCHATLOGGER.VERSION = GetAddOnMetadata(OFFICERCHATLOGGER_ADDON_NAME, "Version")
OFFICERCHATLOGGER.FRAME = CreateFrame("Frame")


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
  if (not OFFICERCHATLOG) then
    OFFICERCHATLOG = {}
  end

  -- Save the message
  OFFICERCHATLOG[GetTimestamp()] = {name, message}

  -- Clean up older messages
  for timestamp,data in pairs(OFFICERCHATLOG) do
    if (tonumber((timestamp) + MESSAGE_KEEP_DURATION_S) < GetTimestamp()) then
      OFFICERCHATLOG[timestamp] = nil
    end
  end
end


OFFICERCHATLOGGER.FRAME:RegisterEvent("CHAT_MSG_OFFICER")
OFFICERCHATLOGGER.FRAME:SetScript("OnEvent", onEvent)
