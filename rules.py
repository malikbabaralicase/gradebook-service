from errors import ValidationError

MAX_TOTAL_WEIGHT = 100
TOLERANCE = 1e-9


def ensure_weight_fits(
    existing_weights: list[float],
    new_weight: float,
) -> None:
    """Ensure the total assessment weight does not exceed 100."""
    if sum(existing_weights) + new_weight > MAX_TOTAL_WEIGHT + TOLERANCE:
        raise ValidationError("Total weight cannot exceed 100")