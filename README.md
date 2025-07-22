# Python Add-ons and Utilities

This directory contains a collection of Python modules designed for various utility and framework purposes.

## Files:

### `event.py`
Provides an `EventDispatcher` class for implementing event-driven programming patterns. It allows for registering and unregistering callback functions to specific events, and dispatching events to trigger all associated callbacks.

### `little_os.py`
Defines the `LITTLEOS` class, a minimal operating system framework. It includes functionalities for file system operations (create, delete, list directories, read/write files), and a persistent command-line shell (CMD) interface to run system commands, capture their output, and manage processes.

### `file_dict.py`
Contains `JSONDict` and `BSONDict` classes, which are dictionary-like objects designed for persistent data storage. They automatically save their content to a specified JSON or BSON file, respectively, upon modification, ensuring data integrity.

### `RUI.py`
Implements `CyperxCommandLineRichUI`, a class utilizing the `rich` library to create a rich command-line interface. It supports styled text output, gradient coloring, notification messages, and user input prompts, enhancing the visual and interactive experience of console applications.
