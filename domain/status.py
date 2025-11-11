from enum import Enum


class Status(Enum):
    PENDING = "pending"
    DONE = "done"
    SKIPPED = "skipped"

    def __str__(self):
        return self.value
