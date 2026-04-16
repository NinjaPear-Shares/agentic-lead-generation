from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class ProspectAccount(BaseModel):
    source_company: str
    relationship_type: Literal['customer', 'investor', 'partner_platform', 'competitor']
    name: str
    website: str | None = None
    normalized_domain: str | None = None
    description: str | None = None
    specialties: list[str] = Field(default_factory=list)
    x_profile: str | None = None
    provenance: list[str] = Field(default_factory=list)
    score: float = 0.0


class ProspectPerson(BaseModel):
    account_domain: str
    full_name: str | None = None
    role: str | None = None
    work_email: str | None = None
    x_handle: str | None = None
    score: float = 0.0


class CompanyUpdate(BaseModel):
    title: str
    category: str | None = None
    summary: str | None = None
    link: str | None = None
    published_at: str | None = None


class LeadGenResult(BaseModel):
    accounts: list[ProspectAccount]
    people: list[ProspectPerson]
    summary: str
