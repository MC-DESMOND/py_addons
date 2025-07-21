class EventDispatcher:
    def __init__(self):
        self._listeners = {}

    def on(self, event_name):
        """
        Decorator to register a callback function for a given event.
        Example: @dispatcher.on("my_event")
        """
        def decorator(callback):
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(callback)
            return callback # Return the original function so it can still be called
        return decorator

    def off(self, event_name, callback):
        """
        Unregisters a callback function from an event.
        """
        if event_name in self._listeners and callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)
        else:
            ...

    def dispatch(self, event_name, *args, **kwargs):
        """
        Triggers an event, calling all registered callbacks for that event.
        Additional arguments are passed directly to the callbacks.
        """
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                    callback(*args, **kwargs)
        else:
            ...

# --- Example Usage ---

base = EventDispatcher()
