from typing import Any
from pydantic import BaseModel, field_validator


def model_dump(
    model: BaseModel,
    *args,
    **kwargs,
) -> dict[str, Any]:
    return model.model_dump(*args, **kwargs)


def model_validate(
    model,
    obj: Any,
    *args,
    **kwargs,
) -> BaseModel:
    return model.model_validate(obj, *args, **kwargs)


class BaseUserModel(BaseModel):
    def create_update_dict(self) -> dict[str, Any]:
        return model_dump(
            model=self,
            exclude_unset=True,
            exclude={
                "id",
                "is_active",
                "is_superuser",
                "is_verified",
            },
        )

    def create_update_dict_superuser(self) -> dict[str, Any]:
        return model_dump(
            model=self,
            exclude_unset=True,
            exclude={"id"},
        )

    @field_validator(
        "email",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_email(cls, value):
        return value.lower()
