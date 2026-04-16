from __future__ import annotations

from app.models import ProspectAccount, ProspectPerson


def score_account(is_competitor_customer: bool, employee_count: int | None, recent_updates: int, role_match: bool) -> float:
    score = 0.0
    if is_competitor_customer:
        score += 40
    if employee_count and 50 <= employee_count <= 2000:
        score += 20
    score += min(recent_updates * 10, 20)
    if role_match:
        score += 20
    return round(score, 2)


def score_person(person: ProspectPerson, account: ProspectAccount) -> float:
    score = 0.0
    if person.role and any(k in person.role.lower() for k in ['revenue', 'sales', 'marketing', 'growth', 'operations']):
        score += 40
    if person.work_email:
        score += 20
    if person.x_handle:
        score += 10
    score += min(account.score / 3, 30)
    return round(score, 2)
