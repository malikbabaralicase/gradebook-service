from errors import ValidationError

TOLERANCE = 1e-9


def ensure_weight_fits(existing_weights, new_weight):
    if sum(existing_weights) + new_weight > 100 + TOLERANCE:
        raise ValidationError("Total weight cannot exceed 100")