from typing import List, Optional
from pydantic import BaseModel, Field

class GeneVariantPair(BaseModel):
    gene: str
    variant: str

class FunctionalVariants(BaseModel):
    data: List[GeneVariantPair]