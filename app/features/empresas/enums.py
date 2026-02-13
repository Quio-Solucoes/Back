from enum import Enum


class EmpresaStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELED = "CANCELED"
