from enum import Enum
from pydantic import BaseModel, Field, model_validator


class CategoryStatus(str, Enum):
    approved = "approved"
    new = "new"
    unclassified = "unclassified"


class BatchIntRequest(BaseModel):
    """What the user or system hands in."""
    since: str = Field(description="The date/datetime from when the Ints should be resolved")

class SingleIntRequest(BaseModel):
    """What the user or system hands in."""
    incident_id: str = Field(description="The Id of the incident being requested to be classified")   

class SingleIntResponse(BaseModel):
    """What comes back."""
    suggested_category: str | None = Field(default=None, description="The suggested category for the incident")
    category_status: CategoryStatus = Field(default=CategoryStatus.unclassified, description="Where the suggested category stands in the taxonomy: approved, or new (first proposed by this incident) or unclassified (no category suggested)")
    problem_id: str | None= Field(default=None, description="The ID of the problem associated with the incident")    
    needs_human: bool = Field(description="Whether human intervention is needed")
    confidence: float = Field(description="Confidence score for the classification", ge=0, le=1) 
    reason: str = Field(description="Reason for the classification")

    @model_validator(mode="after")
    def validate_classification(self):
        has_category = bool(self.suggested_category and self.suggested_category.strip())
        is_unclassified = self.category_status is CategoryStatus.unclassified

        if not has_category and not self.needs_human:
            raise ValueError("suggested_category is required if human intervention is not needed")

        if not self.needs_human and self.category_status is not CategoryStatus.approved:
            raise ValueError("category_status must be approved to skip human review")

        if not is_unclassified and not has_category:
            raise ValueError("suggested_category is required when category_status is not unclassified")

        if is_unclassified and self.suggested_category is not None:
            raise ValueError("suggested_category must be None when category_status is unclassified")

        return self
 
class BatchIntResponse(BaseModel):
    classifications: list[SingleIntResponse] = Field(description="One result per incident processed")
    # plus whatever batch-level summary fields you need
    
 
def solveBatch(request: BatchIntRequest) -> BatchIntResponse:
    raise NotImplementedError("implement against this signature")






