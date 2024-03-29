"""Defines the Member class and its components and formatting"""
import logging

LOG = logging.getLogger(__name__)


class Member:
    """Member class to hold properties parsed from World of Warcraft Guild Info"""
    def __init__(self, index, timestamp, name, rank, level, zone, note, officernote, online, status, clazz):
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

    def __lt__(self, other) -> bool:
        if type(other) is Member:
            return self.name < other.name
        else:
            return self.name < other

    def __gt__(self, other) -> bool:
        if type(other) is Member:
            return self.name > other.name
        else:
            return self.name > other

    def __eq__(self, other) -> bool:
        return type(other) is Member and self.name == other.name

    def __hash__(self) -> int:
        return hash(('name', self.name))

    def __str__(self) -> str:
        online = "Offline"
        if self.online:
            online = "Online"
        status = ""
        if self.status != "Available":
            status = "(" + self.status + ")"
        note = "[" + self.note + "|" + self.officernote + "]"
        return self.rank + " " + self.name + ", level " + str(self.level) + " " + self.clazz + ", " + online + status + " in " + self.zone + ", " + note

    def __simple__(self) -> str:
        return self.name + " " + str(self.level) + " " + self.clazz
