from pydantic import BaseModel, Field


class UpdatePlanRequest(BaseModel):
    plan_id: str = Field(min_length=3, max_length=100)


class SubscriptionResponse(BaseModel):
    id: str
    empresa_id: str
    plan_id: str | None
    status: str
    billing_cycle: str
    current_price: float

    @classmethod
    def from_model(cls, model) -> "SubscriptionResponse":
        return cls(
            id=model.id,
            empresa_id=model.empresa_id,
            plan_id=model.plan_id,
            status=model.status.value,
            billing_cycle=model.billing_cycle.value,
            current_price=float(model.current_price),
        )
