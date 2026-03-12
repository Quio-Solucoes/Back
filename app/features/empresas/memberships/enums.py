from enum import Enum


class MembershipStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    INVITED = "INVITED"


class MembershipRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    COLABORADOR = "COLABORADOR"
    CONSULTOR = "CONSULTOR"
    GESTOR_COMERCIAL = "GESTOR_COMERCIAL"
