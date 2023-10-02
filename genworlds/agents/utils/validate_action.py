import json
from datetime import datetime
from jsonschema import ValidationError, validate
from genworlds.agents.memories.simulation_memory import OneLineEventSummarizer


def validate_action(
    agent_id: str,
    action_schema: str,
    pre_filled_event: dict,
    available_action_schemas: dict,
):
    one_line_summarizer = OneLineEventSummarizer()  # missing key
    try:
        class_name, event_type = action_schema.split(":")
        trigger_event = {
            "event_type": event_type,
            "sender_id": agent_id,
            "created_at": datetime.now().isoformat(),
        }
        trigger_event.update(pre_filled_event)
        summary = one_line_summarizer.summarize(json.dumps(trigger_event))
        trigger_event["summary"] = summary

        event_schema = available_action_schemas[class_name][event_type]

        validate(trigger_event, event_schema)

        if class_name == "Self":
            is_my_action = True
        else:
            is_my_action = False
        return is_my_action, trigger_event
    except IndexError as e:
        return (
            f"Unknown command '{action_schema}'. "
            f"Please refer to the 'COMMANDS' list for available "
            f"commands and only respond in the specified JSON format."
        )
    except ValidationError as e:
        return (
            f"Validation Error in args: {str(e)}, pre_filled_event: {pre_filled_event}"
        )
    except Exception as e:
        return (
            f"Error: {str(e)}, {type(e).__name__}, pre_filled_event: {pre_filled_event}"
        )
