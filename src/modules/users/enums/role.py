import enum


class UserRole(str, enum.Enum):
    COMMON = "common"
    ADMIN = "admin"
