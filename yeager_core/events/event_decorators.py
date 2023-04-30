def event_type(event_type: str):
    def decorator(cls):
        cls.event_type = event_type
        return cls

    return decorator
