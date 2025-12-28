from enum import Enum


class Genre(str, Enum):
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science-fiction"
    DETECTIVE = "detective"
    ROMANCE = "romance"
    NONFICTION = "nonfiction"


class BookReadingStatus(str, Enum):
    NOT_STARTED = "not_started"
    READING = "reading"
    FINISHED = "finished"