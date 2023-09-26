from datetime import datetime
from pydantic import create_model
from typing import Dict, Any, Optional

TYPE_MAPPING = {
    "string": str,
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
    "number": float,
    # add more as needed
}


def json_schema_to_pydantic_model(schema: Dict[str, Any]) -> Any:
    name = schema.get("title", "DynamicModel")
    required_fields = schema.get("required", [])

    fields = {}
    for k, v in schema["properties"].items():
        field_type = TYPE_MAPPING.get(v.get("type"))

        # Special handling for date-time format
        if v.get("format") == "date-time":
            field_type = datetime

        default_value = v.get("default")

        # If the field is not required or has a default value, it's optional
        if k not in required_fields:
            field_type = Optional[field_type]

            if default_value is not None:
                fields[k] = (field_type, default_value)
            else:
                fields[k] = (field_type, None)
        else:
            fields[k] = field_type

    return create_model(name, **fields)
