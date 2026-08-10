import inspect
from typing import Type

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError


def as_form(cls: Type[BaseModel]):
    new_parameters = []

    for field_name, model_field in cls.model_fields.items():
        new_parameters.append(
            inspect.Parameter(
                model_field.alias or field_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=Form(...)
                if model_field.is_required()
                else Form(model_field.default),
                annotation=model_field.annotation,
            )
        )

    def as_form_func(**params):
        try:
            return cls(**params)
        except ValidationError as e:
            # Pydantic errors raised while resolving a Depends() callable are not
            # automatically turned into a 422 response by FastAPI (that only
            # happens for its own body/query/path validation) — re-raise as
            # RequestValidationError so it is. e.errors() is already in the dict
            # shape RequestValidationError expects.
            raise RequestValidationError(e.errors())

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig
    setattr(cls, "as_form", as_form_func)
    return cls
