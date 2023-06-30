import inspect
from typing import Type

from fastapi import Form
from pydantic import BaseModel
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
        return cls(**params)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig
    setattr(cls, "as_form", as_form_func)
    return cls
