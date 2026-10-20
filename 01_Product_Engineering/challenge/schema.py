from enum import Enum

from pydantic import BaseModel, Field, model_validator


class CategoryStatus(str, Enum):
    approved = "approved"
    pending = "pending"
    new = "new"


class BatchIntRequest(BaseModel):
    """What the user or system hands in."""
    since: str = Field(description="The date/datetime from when the Ints should be resolved")

class SingleIntRequest(BaseModel):
    """What the user or system hands in."""
    incident_id: str = Field(description="The Id of the incident being requested to be classified")   

class SingleIntResponse(BaseModel):
    """What comes back."""
    suggested_category: str | None = Field(default=None, description="The suggested category for the incident")
    category_status: CategoryStatus = Field(default=CategoryStatus.pending, description="Where the suggested category stands in the taxonomy: approved, pending (matches an existing proposal), or new (first proposed by this incident)")
    problem_id: str | None= Field(default=None, description="The ID of the problem associated with the incident")    
    needs_human: bool = Field(description="Whether human intervention is needed")
    confidence: float = Field(description="Confidence score for the classification", ge=0, le=1) 
    reason: str = Field(description="Reason for the classification")

    @model_validator(mode="after")
    def validate_classification(self):
        if self.suggested_category is None and not self.needs_human:
            raise ValueError("Suggested category is required if human intervention is not needed")
        if self.category_status is not CategoryStatus.approved and self.needs_human is False:
            raise ValueError("Suggested category should be approved to skip human review")    
        return self  
 
class BatchIntResponse(BaseModel):
    classifications: list[SingleIntResponse] = Field(description="One result per incident processed")
    # plus whatever batch-level summary fields you need
    
 
def solveBatch(request: BatchIntRequest) -> BatchIntResponse:
    raise NotImplementedError("implement against this signature")

def solveSingle(request: SingleIntRequest) -> SingleIntResponse:
    raise NotImplementedError("implement against this signature")
