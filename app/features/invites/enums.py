from enum import Enum


class FranchiseInviteStatus(str, Enum):
    PENDING = "PENDING"
    REGISTERED = "REGISTERED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class UserInviteStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"
