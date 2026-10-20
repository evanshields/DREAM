"""Thin authenticated Mono HTTP surface. Trust and business rules live in service."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr


class RevisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: StrictInt = Field(ge=1)
    expected_deal_sha256: StrictStr = Field(min_length=1)


class EditRequest(RevisionRequest):
    field_id: StrictStr = Field(min_length=1)
    entered_value: StrictStr | StrictInt | StrictFloat | StrictBool | None
    unit: StrictStr
    reason: StrictStr = Field(min_length=1)
    idempotency_key: StrictStr = Field(min_length=1)


class CalculateRequest(RevisionRequest):
    idempotency_key: StrictStr = Field(min_length=1)


class GateRequest(RevisionRequest):
    gate: Literal["comps", "go_no_go"]
    decision: Literal["confirm", "go", "no_go"]
    reason: StrictStr = Field(min_length=1)
    idempotency_key: StrictStr = Field(min_length=1)
    comps_sha256: StrictStr | None = None
    result_id: StrictStr | None = None


class EmptyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


def create_router(service, actor_dependency):
    router = APIRouter(tags=["mono"])

    @router.get("/{deal_id}/mono")
    def view(deal_id: str, actor=Depends(actor_dependency)):
        return service.view(deal_id, actor)

    @router.post("/{deal_id}/mono/edits")
    def edit(deal_id: str, body: EditRequest, actor=Depends(actor_dependency)):
        return service.edit(deal_id, body.model_dump(), actor)

    @router.post("/{deal_id}/mono/calculations")
    def calculate(deal_id: str, body: CalculateRequest, actor=Depends(actor_dependency)):
        return service.calculate(deal_id, body.model_dump(), actor)

    @router.get("/{deal_id}/mono/jobs/{job_id}")
    def job(deal_id: str, job_id: str, actor=Depends(actor_dependency)):
        return service.job(deal_id, job_id, actor)

    @router.post("/{deal_id}/mono/jobs/{job_id}/cancel")
    def cancel(deal_id: str, job_id: str, body: EmptyRequest | None = None, actor=Depends(actor_dependency)):
        return service.cancel(deal_id, job_id, actor)

    @router.post("/{deal_id}/mono/gates")
    def gate(deal_id: str, body: GateRequest, actor=Depends(actor_dependency)):
        return service.gate(deal_id, body.model_dump(exclude_none=True), actor)

    return router
