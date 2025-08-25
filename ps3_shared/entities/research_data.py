from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, field_validator, model_validator
import re

T = TypeVar("T")


class FieldExplanation(BaseModel):
    explanation: Optional[str] = Field(
        description="A detailed explanation for the 'value' of this field, "
        "including the reason for its presence, its source or origin, "
        "and the method or process by which it was determined."
    )
    pages: Optional[List[int]] = Field(
        description="The pages where the value of this field is located in the document."
    )


class FieldWithExplanation(BaseModel, Generic[T]):
    value: Optional[T]
    explanation: Optional[str] = Field(
        description="A detailed explanation for the 'value' of this field, "
        "including the reason for its presence, its source or origin, "
        "and the method or process by which it was determined."
    )


class ResearchArticle(BaseModel):
    articulo: FieldWithExplanation[str]
    doi: FieldWithExplanation[str]
    disease: FieldWithExplanation[str]
    gene: FieldWithExplanation[str]
    variant_name: FieldWithExplanation[str]
    type: FieldWithExplanation[str]
    modelSystem: FieldWithExplanation[str]
    experimentalMethod: FieldWithExplanation[str]
    outcomeEvaluated: FieldWithExplanation[str]
    positiveControls: FieldWithExplanation[int]
    negativeControls: FieldWithExplanation[int]
    pathogenicVariants: FieldWithExplanation[int]
    pathogenicAbnormalVariants: FieldWithExplanation[int]
    totalVariants: FieldWithExplanation[int]
    replicates: FieldWithExplanation[int]
    statisticalAnalysis: FieldWithExplanation[str]
    validationProcess: FieldWithExplanation[str]
    reproducible: FieldWithExplanation[bool]
    robustnessData: FieldWithExplanation[str]
    functionalImpact: FieldWithExplanation[str]

    # pyrefly: ignore  # bad-argument-type
    @field_validator(
        "articulo",
        "disease",
        "gene",
        "variant_name",
        "type",
        "modelSystem",
        "experimentalMethod",
        "outcomeEvaluated",
        "statisticalAnalysis",
        "validationProcess",
        "robustnessData",
        "functionalImpact",
        mode="after",
    )
    @classmethod
    def not_empty(cls, v: FieldWithExplanation[str], info) -> FieldWithExplanation[str]:
        if v.value is not None and isinstance(v.value, str) and not v.value.strip():
            raise ValueError(f"{info.field_name}.value must not be an empty string")
        return v

    # pyrefly: ignore  # bad-argument-type
    @field_validator("type", mode="after")
    @classmethod
    def normalize_experiment_id(
        cls, v: FieldWithExplanation[str], _info
    ) -> FieldWithExplanation[str]:
        """Extrae y normaliza un ID ontológico al formato PREFIX:NNNNNNN.

        Soporta variantes como:
        - OBI:0000854
        - OBI_0000854
        - obi0000854
        - ECO-0001091
        - Texto libre que contenga alguno de los patrones anteriores
        """
        if v.value is not None:
            text = str(v.value)
            # Prefijo (2-10 letras) + separador opcional + al menos 7 caracteres numéricos o '_'
            # Se permite '_' intercalado entre los dígitos, p.ej. OBI:000_0854 o ECO_0001091_2
            m = re.search(r"(?i)\b([a-z]{2,10})[ _:-]?([0-9_]{7,})\b", text)
            if m:
                prefix = m.group(1).upper()
                digits = m.group(2).replace("_", "")  # normalizar quitando '_'
                v.value = f"{prefix}:{digits}"
        return v

    # pyrefly: ignore  # bad-argument-type
    @field_validator(
        "positiveControls",
        "negativeControls",
        "pathogenicVariants",
        "pathogenicAbnormalVariants",
        "totalVariants",
        "replicates",
        mode="after",
    )
    @classmethod
    def non_negative(
        cls, v: FieldWithExplanation[int], info
    ) -> FieldWithExplanation[int]:
        if v.value is not None and isinstance(v.value, int) and v.value < 0:
            raise ValueError(f"{info.field_name}.value must be a non-negative integer")
        return v

    # pyrefly: ignore  # bad-argument-type
    @field_validator("doi", mode="after")
    @classmethod
    def valid_doi_format(
        cls, v: FieldWithExplanation[str], info
    ) -> FieldWithExplanation[str]:
        if v.value is not None:
            doi_pattern = r"10\.\d{4,9}/[-._;()/:A-Z0-9]+"
            if not re.search(doi_pattern, str(v.value), re.IGNORECASE):
                raise ValueError(
                    f"{info.field_name}.value format seems invalid as a DOI"
                )
            # Convert to URL if valid
            if not str(v.value).lower().startswith("http"):
                v.value = f"https://doi.org/{v.value}"
        return v

    @model_validator(mode="after")
    def check_cross_fields(self) -> "ResearchArticle":
        def val(field_name: str) -> Optional[int]:
            field = getattr(self, field_name)
            return field.value if field and field.value is not None else None

        reproducible = val("reproducible")
        replicates = val("replicates")
        pathogenic_abnormal = val("pathogenicAbnormalVariants")
        pathogenic = val("pathogenicVariants")
        total = val("totalVariants")

        if reproducible is True and (replicates is None or replicates <= 1):
            raise ValueError("Reproducible studies must have more than 1 replicate")

        if (
            pathogenic_abnormal is not None
            and pathogenic is not None
            and pathogenic_abnormal > pathogenic
        ):
            raise ValueError(
                "Pathogenic abnormal variants cannot exceed total pathogenic variants"
            )

        if total is not None and pathogenic is not None and total < pathogenic:
            raise ValueError(
                "Total variants must be greater than or equal to pathogenic variants"
            )

        return self


class ResearchData(BaseModel):
    data: List[ResearchArticle]
