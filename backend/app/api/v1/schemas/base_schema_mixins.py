from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import get_origin, get_args, Union

from pydantic import field_validator, field_serializer

from core.settings import settings

TIME_ZONE = ZoneInfo(settings.TIMEZONE)


def is_datetime_field(annotation) -> bool:
    if annotation is datetime:
        return True

    origin = get_origin(annotation)
    if origin in (Union, getattr(__import__("types"), "UnionType", Union)):
        return datetime in get_args(annotation)
    return False


class InputDateTimeTZMixin:
    @field_validator("*", mode="before")
    @classmethod
    def convert_input_datetime(cls, v, info):
        if hasattr(cls, '__annotations__') and info.field_name in cls.__annotations__:
            field_annotation = cls.__annotations__[info.field_name]
        elif hasattr(cls, 'model_fields') and info.field_name in cls.model_fields:
            field_info = cls.model_fields[info.field_name]
            field_annotation = getattr(field_info, 'annotation', None)
        else:
            return v

        if field_annotation and is_datetime_field(field_annotation):
            if v is None:
                return v

            dt: datetime
            if isinstance(v, str):
                try:
                    dt = datetime.fromisoformat(v)
                except ValueError:
                    return v
            elif isinstance(v, datetime):
                dt = v
            else:
                return v

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=TIME_ZONE)

            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return v

class OutputDateTimeTZMixin:
    @field_serializer("*")
    def convert_output_datetime(self, v, info):
        if hasattr(self.__class__, '__annotations__') and info.field_name in self.__class__.__annotations__:
            field_annotation = self.__class__.__annotations__[info.field_name]
        elif hasattr(self, 'model_fields') and info.field_name in self.model_fields:
            field_info = self.model_fields[info.field_name]
            field_annotation = getattr(field_info, 'annotation', None)
        else:
            return v

        if field_annotation and is_datetime_field(field_annotation) and isinstance(v, datetime):
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            return v.astimezone(TIME_ZONE).replace(tzinfo=None)
        return v
