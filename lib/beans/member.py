import logging

LOG = logging.getLogger(__name__)

class Member:
    def __init__(self, index, timestamp, name, rank ,level, zone, note, officernote, online, status, clazz):
        self.index = index
        self.timestamp = timestamp
        self.name = name.encode("UTF-8", "ignore").decode("UTF-8", "ignore")
        self.rank = rank.encode("UTF-8", "ignore").decode("UTF-8", "ignore")
        self.level = level
        self.zone = zone.encode("UTF-8", "ignore").decode("UTF-8", "ignore")
        self.note = note.encode("UTF-8", "ignore").decode("UTF-8", "ignore")
        self.officernote = officernote.encode("UTF-8", "ignore").decode("UTF-8", "ignore")
        self.online = online
        self.status = status
        self.clazz = clazz
