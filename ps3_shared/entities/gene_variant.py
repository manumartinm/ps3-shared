from typing import List
from pydantic import BaseModel, field_validator


class GeneVariantPair(BaseModel):
    gene: str
    variant: str


class FunctionalVariants(BaseModel):
    data: List[GeneVariantPair]

    @field_validator("data")
    @classmethod
    def filter_unique_variants(
        cls, variants: List[GeneVariantPair]
    ) -> List[GeneVariantPair]:
        """Mantiene solo variantes válidas (p. o r.) y únicas por (gene, variant)."""
        if not variants:
            return variants

        allowed_prefixes = ("p.", "r.", "c.")
        seen = set()
        unique_variants: List[GeneVariantPair] = []

        for item in variants:
            gene_norm = (item.gene or "").strip()
            variant_norm = (item.variant or "").strip()

            # Filtrar por prefijos permitidos (case-insensitive)
            if not variant_norm.lower().startswith(allowed_prefixes):
                continue

            key = (gene_norm.lower(), variant_norm)
            if key in seen:
                continue

            seen.add(key)

            # Normalizar espacios en el objeto devuelto
            if gene_norm != item.gene or variant_norm != item.variant:
                unique_variants.append(
                    GeneVariantPair(gene=gene_norm, variant=variant_norm)
                )
            else:
                unique_variants.append(item)

        return unique_variants
