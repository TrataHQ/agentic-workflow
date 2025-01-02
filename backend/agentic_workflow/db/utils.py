import json
import os
from typing import Generic, TypeVar
import logging
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as, TypeAdapter
from pydantic._internal._model_construction import ModelMetaclass
from sqlmodel import JSON
from sqlmodel import JSON, TypeDecorator
from sqlalchemy import CHAR, types, JSON
from sqlalchemy.types import TypeEngine
from sqlalchemy.engine.interfaces import Dialect
from typing import Any, Optional, cast, ClassVar
from enum import Enum
from sqlalchemy import String, TypeDecorator
from typing import Type, TypeVar
from sqlalchemy.sql.operators import OperatorType


T = TypeVar("T")


# Taken from https://github.com/tiangolo/sqlmodel/issues/63#issuecomment-1081555082
def pydantic_column_type(pydantic_type):
    class PydanticJSONType(TypeDecorator, Generic[T]):
        impl = JSON()

        def __init__(
            self,
            json_encoder=json,
        ):
            self.json_encoder = json_encoder
            super(PydanticJSONType, self).__init__()

        def bind_processor(self, dialect):
            impl_processor = self.impl.bind_processor(dialect)
            dumps = self.json_encoder.dumps
            if impl_processor:

                def process(value: T):
                    if value is not None:
                        if isinstance(pydantic_type, ModelMetaclass):
                            # This allows to assign non-InDB models and if they're
                            # compatible, they're directly parsed into the InDB
                            # representation, thus hiding the implementation in the
                            # background. However, the InDB model will still be returned
                            value_to_dump = pydantic_type.model_validate(value)
                        else:
                            value_to_dump = value
                        value = jsonable_encoder(value_to_dump)
                    return impl_processor(value)

            else:

                def process(value):
                    if isinstance(pydantic_type, ModelMetaclass):
                        # This allows to assign non-InDB models and if they're
                        # compatible, they're directly parsed into the InDB
                        # representation, thus hiding the implementation in the
                        # background. However, the InDB model will still be returned
                        value_to_dump = pydantic_type.model_validate(value)
                    else:
                        value_to_dump = value
                    value = dumps(jsonable_encoder(value_to_dump))
                    return value

            return process

        def result_processor(self, dialect, coltype) -> T:
            impl_processor = self.impl.result_processor(dialect, coltype)
            if impl_processor:

                def process(value):
                    value = impl_processor(value)
                    if value is None:
                        return None

                    data = value
                    # Explicitly use the generic directly, not type(T)
                    full_obj = TypeAdapter(pydantic_type).validate_python(data)
                    # full_obj = parse_obj_as(pydantic_type, data)
                    return full_obj

            else:

                def process(value):
                    if value is None:
                        return None

                    # Explicitly use the generic directly, not type(T)
                    full_obj = TypeAdapter(pydantic_type).validate_python(value)
                    # full_obj = parse_obj_as(pydantic_type, value)
                    return full_obj

            return process

        def compare_values(self, x, y):
            if x is None or y is None:
                return x == y
            # Convert both to dict for comparison if they're Pydantic models
            x_dict = x.model_dump() if hasattr(x, "model_dump") else x
            y_dict = y.model_dump() if hasattr(y, "model_dump") else y
            return x_dict == y_dict

    return PydanticJSONType


### HACK: "PydanticJSONType" class is duplicated to get referenced by alembic migration file. Fix it
class PydanticJSONType(types.TypeDecorator):
    impl = types.JSON

    def load_dialect_impl(self, dialect: Dialect) -> "types.TypeEngine[Any]":
        impl = cast(types.JSON, self.impl)
        return super().load_dialect_impl(dialect)


R = TypeVar("R", bound=Enum)


class EnumAsStringType(TypeDecorator, Generic[R]):
    impl: ClassVar[TypeEngine] = String()

    cache_ok = True

    def __init__(self, enum_class: Type[R], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        if isinstance(value, self.enum_class):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return self.enum_class(value)
        return value

    @classmethod
    def coerce_compared_value(cls, op: Optional[OperatorType], value: Any) -> TypeEngine[Any]:
        return cls.impl.coerce_compared_value(op, value)

    def __repr__(self):
        return f"EnumAsStringType({self.enum_class.__name__})"
