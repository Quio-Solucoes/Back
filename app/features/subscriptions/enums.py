from enum import Enum


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"


class BillingCycle(str, Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
