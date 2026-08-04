import inspect
from typing import Type

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
from pydantic.fields import ModelField


def as_form(cls: Type[BaseModel]):
    new_parameters = []

    for field_name, model_field in cls.__fields__.items():
        model_field: ModelField

        new_parameters.append(
            inspect.Parameter(
                model_field.alias,
                inspect.Parameter.POSITIONAL_ONLY,
                default=Form(...)
                if model_field.required
                else Form(model_field.default),
                annotation=model_field.outer_type_,
            )
        )

    def as_form_func(**params):
        try:
            return cls(**params)
        except ValidationError as e:
            # Pydantic errors raised while resolving a Depends() callable are not
            # automatically turned into a 422 response by FastAPI (that only
            # happens for its own body/query/path validation) — re-raise as
            # RequestValidationError so it is. Pass raw_errors (not e.errors(),
            # which is already flattened) since RequestValidationError flattens
            # them itself when FastAPI's handler calls .errors() on it.
            raise RequestValidationError(e.raw_errors)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig
    setattr(cls, "as_form", as_form_func)
    return cls
