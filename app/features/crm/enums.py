from enum import Enum


class LeadStatus(str, Enum):
    NEW = "NEW"
    IN_REVIEW = "IN_REVIEW"
    CONTRACT_SENT = "CONTRACT_SENT"
    CONTRACT_SIGNED = "CONTRACT_SIGNED"
    CONTRACT_REJECTED = "CONTRACT_REJECTED"
    CLOSED_LOST = "CLOSED_LOST"


class ContractStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    SIGNED = "SIGNED"
    CANCELED = "CANCELED"
