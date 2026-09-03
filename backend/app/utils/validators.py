def validate_learning_hours(hours: float) -> None:
    if hours is None or hours <= 0:
        raise ValueError("learning_hours must be greater than 0")


def validate_completion_percentage(pct: float) -> None:
    if pct is None or pct < 0 or pct > 100:
        raise ValueError("completion_percentage must be between 0 and 100")
