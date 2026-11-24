from pydantic import BaseModel, Field
from typing import Optional

class PushRequest(BaseModel):
    
    do_reset: Optional[bool] = False

class SearchRequest(BaseModel):
    
    text: str = Field(..., min_length=1)
    limit: Optional[int] = Field(default=10, gt=0)
