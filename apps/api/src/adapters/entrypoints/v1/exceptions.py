from pydantic import ValidationError


class NoFiltersError(ValidationError):
    def __init__(self, model_class, filters_input):
        super().__init__(
            [
                {
                    "type": "value_error",
                    "loc": ("filters",),
                    "msg": "At least one filter must be provided",
                    "input": filters_input,
                }
            ],
            model_class,
        )
