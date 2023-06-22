import datetime
import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class SubBlock:
    original_index: int
    current_index: int
    content: str
    clean_content: str
    start_time: datetime.timedelta
    end_time: datetime.timedelta
    regex_matches = 0
    hints: List[str]

    def __init__(self, block_content: str, original_index_actual: int):
        lines = block_content.strip().split("\n")

        if self.is_sub_block_header(lines[0]):
            lines = [""] + lines
        if not self.is_sub_block_header(lines[1]):
            raise ParsingException(original_index_actual)

        if lines[0].isnumeric():
            self.original_index = int(lines[0])
        else:
            number = ""
            for character in lines[0]:
                if character.isnumeric():
                    number += character
                else:
                    break
            if number:
                self.original_index = int(number)
            else:
                self.original_index = original_index_actual

        if not self.original_index:
            self.original_index = original_index_actual

        times = lines[1].replace(" ", "").split("-->")
        try:
            self.start_time = time_string_to_timedelta(times[0])
            self.end_time = time_string_to_timedelta(times[1])
        except ValueError:
            raise ParsingException(self.original_index)
        except IndexError:
            raise ParsingException(self.original_index)

        if len(lines) > 2:
            self.content = "\n".join(lines[2:]).strip()
        else:
            self.content = ""
        self.content = self.content.replace("</br>", "\n")
        self.clean_content = re.sub("[\\s.,:_-]", "", self.content)
        self.hints = []

    def equal_content(self, block: "SubBlock") -> bool:
        t = re.sub("[\\s.,:_-]", "", self.content)
        o = re.sub("[\\s.,:_-]", "", block.content)
        return t == o

    def __str__(self) -> str:
        string = f"{timedelta_to_time_string(self.start_time)} --> {timedelta_to_time_string(self.end_time)}\n" \
                 f"{self.content.replace('--', '—')}"
        return string

    @classmethod
    def is_sub_block_header(cls, line: str) -> bool:
        if "\n" in line:
            return False

        times = line.replace(" ", "").split("-->")
        try:
            start_time = time_string_to_timedelta(times[0])
            end_time = time_string_to_timedelta(times[1])
        except ValueError:
            return False
        except IndexError:
            return False

        return True


class ParsingException(Exception):
    block_index: int
    subtitle_file: str

    def __init__(self, block_index):
        self.block_index = block_index

    def __str__(self) -> str:
        return f"Parsing error at block {self.block_index} in file {self.subtitle_file}."


def time_string_to_timedelta(time_string: str) -> datetime.timedelta:
    time = time_string.replace(",", ".").replace(" ", "")
    split = time.split(":")

    hours = split[0]
    minutes = split[1]
    seconds = split[2][:6]

    seconds_clean = ""
    found_dot = False
    for ch in seconds:
        if ch.isnumeric():
            seconds_clean += ch
        if ch == ".":
            if not found_dot:
                found_dot = True
                seconds_clean += ch
    seconds = seconds_clean

    return datetime.timedelta(hours=float(hours),
                              minutes=float(minutes),
                              seconds=float(seconds))


def timedelta_to_time_string(timedelta: datetime.timedelta) -> str:
    time_string = str(timedelta)
    if "." in time_string:
        time_string = time_string[: -3].replace(".", ",").zfill(12)
    else:
        time_string = f"{time_string},000".zfill(12)
    return time_string
