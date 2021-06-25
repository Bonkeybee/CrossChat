GUILDINFO_ADDON_NAME, GUILDINFO = ...
GUILDINFO.VERSION = GetAddOnMetadata(GUILDINFO_ADDON_NAME, "Version")
GUILDINFO.FRAME = CreateFrame("Frame")


local INFO_KEEP_DURATION_S = 60 * 5


local function GetTimestamp()
  return tonumber(GetServerTime().."."..(GetTime()*1000))
end

local function onEvent(_, event, isLogin, isReload)
  -- Do not get guild info on login
  if (isLogin) then
    return
  end

  -- Load or create the saved variable
  if (not GUILDINFO) then
    GUILDINFO = {}
  end

  -- Save guild info
  GuildRoster()
  for i = 1, 1000 do
    local name, rank, _, level, _, zone, note, officernote, online, status, class = GetGuildRosterInfo(i)
    if (name) then
      local timestamp = GetTimestamp()
      GUILDINFO[name] = {i, timestamp, rank, level, zone, note, officernote, online, status, class}
    end
  end

  -- Clean up older info
  for name,data in pairs(GUILDINFO) do
    local timestamp = data[2] or 0
    if (tonumber((timestamp) + INFO_KEEP_DURATION_S) < GetTimestamp()) then
      GUILDINFO[name] = nil
    end
  end
end


GUILDINFO.FRAME:RegisterEvent("PLAYER_ENTERING_WORLD")
GUILDINFO.FRAME:SetScript("OnEvent", onEvent)
