from datetime import datetime
from typing import Dict, Any, Optional, Type
from pydantic import create_model, BaseModel

TYPE_MAPPING = {
    "string": (str, ...),
    "integer": (int, ...),
    "boolean": (bool, ...),
    "array": (list, ...),
    "object": (dict, ...),
    "number": (float, ...),
}


def json_schema_to_pydantic_model(schema: Dict[str, Any]) -> Type[BaseModel]:
    name = schema.get("title", "DynamicModel")
    required_fields = schema.get("required", [])

    fields = {}
    for k, v in schema["properties"].items():
        field_type, default_value = TYPE_MAPPING.get(v.get("type"), (Any, ...))

        # Special handling for date-time format
        if v.get("format") == "date-time":
            field_type = datetime

        # If the field is not required or has a default value, it's optional
        if k not in required_fields and "default" in v:
            default_value = v["default"]
            field_type = Optional[field_type]

        fields[k] = (field_type, default_value)

    return create_model(name, **fields)
