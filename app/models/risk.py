from pydantic import BaseModel, Field


class PathNode(BaseModel):
    label: str
    id: str
    name: str | None = None


class PathRelationship(BaseModel):
    type: str


class RiskPath(BaseModel):
    score: float
    nodes: list[PathNode]
    relationships: list[PathRelationship]


class CompanyRiskResponse(BaseModel):
    company_id: str
    total_score: float
    path_count: int
    truncated: bool = False
    paths: list[RiskPath] = Field(default_factory=list)
