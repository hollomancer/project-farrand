from datetime import date, datetime
from dataclasses import dataclass
from typing import Set, List, Optional
from src.agents.delegate_agent import DialogueTurn

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    feedback: Optional[str]

class ConstraintValidator:
    def __init__(self, anachronism_terms: Set[str]):
        self.anachronism_terms = anachronism_terms
        self.date_boundary = date(1787, 9, 17)

    def validate(self, turn: DialogueTurn) -> ValidationResult:
        errors = []

        # Check for anachronistic terms
        for term in self.anachronism_terms:
            if term.lower() in turn.text.lower():
                errors.append(f"Anachronistic term detected: '{term}'")

        # Check date references
        # This is a simplified check. A real implementation would need NLP to extract dates.
        # For now, we'll assume no explicit future dates are mentioned in a simple format.
        # date_refs = self._extract_dates(turn.text)
        # for ref in date_refs:
        #     if ref > self.date_boundary:
        #         errors.append(f"Future date reference: {ref}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            feedback=self._generate_feedback(errors) if errors else None
        )

    def _generate_feedback(self, errors: List[str]) -> str:
        return "Validation failed: " + "; ".join(errors)
