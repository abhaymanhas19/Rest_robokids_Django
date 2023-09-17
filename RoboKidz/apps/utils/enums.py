import enum
from enum import Enum


class UserType(Enum):
    STUDENT = "STUDENT"
    MENTOR = "MENTOR"
    INSTITUTE = "INSTITUTE"
    ADMIN = "ADMIN"

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class GenderType(Enum):
    Male = "male"
    Female = "Female"

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)
