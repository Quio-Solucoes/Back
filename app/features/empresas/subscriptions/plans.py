from dataclasses import dataclass


@dataclass(frozen=True)
class PlanLimit:
    max_admins: int
    max_members: int


PLAN_LIMITS = {
    "START": PlanLimit(max_admins=1, max_members=5),
    "GROW": PlanLimit(max_admins=3, max_members=20),
    "SCALE": PlanLimit(max_admins=10, max_members=100),
}


def get_plan_limit(plan_id: str | None) -> PlanLimit:
    if not plan_id:
        return PLAN_LIMITS["START"]
    return PLAN_LIMITS.get(plan_id.upper(), PLAN_LIMITS["START"])
