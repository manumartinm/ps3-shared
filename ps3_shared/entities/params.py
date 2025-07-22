from pydantic import BaseModel, Field, validator
from typing import Optional

class GetPDFDataArgs(BaseModel):
    filename: Optional[str]