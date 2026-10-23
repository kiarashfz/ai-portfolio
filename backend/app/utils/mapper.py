from typing import Type, TypeVar, List, Union
from pydantic import BaseModel

T = TypeVar("T")


def map_to_dto(
    data: Union[List[BaseModel], BaseModel, dict, None], dto_class: Type[T]
) -> Union[List[T], T, None]:
    if isinstance(data, list):
        if len(data) > 0 and isinstance(data[0], BaseModel):
            return [dto_class(**item.model_dump()) for item in data]
        return [dto_class(**item) for item in data]
    elif isinstance(data, BaseModel):
        return dto_class(**data.model_dump())
    elif isinstance(data, dict):
        return dto_class(**data)
    return None
