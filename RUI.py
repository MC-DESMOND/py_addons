from rich.console import Console
from rich.text import Text
from rich.color import Color
from rich.style import Style

default_Color = "#505050"

class CyperxCommandLineRichUI:
    """
    CyperxCommandLineRichUI provides a rich command-line interface for styled and gradient text output using the `rich` library.
    Attributes:
        text (Text): The current text buffer.
        console (Console): The rich console for output.
        his_style (Style): Default style for the "who" prompt.
        def_style (Style): Default style for general text.
        who (str): The prompt string (e.g., ">>").
        spacer (str): Spacer string between prompt and text.
        def_gradient (tuple[str, str]): Default gradient colors.
        len (int): Tracks the length of the text buffer for carriage return handling.
    Properties:
        him: Appends the prompt and spacer to the text buffer.
        his_notify: Appends a notification-style prompt to the text buffer.
        POP: Returns a copy of the current text buffer and clears it.
        LOGGING: Appends a "LOGGING" notification to the text buffer.
        INFO: Appends an "INFO" notification to the text buffer.
        WARNING: Appends a "WARNING" notification to the text buffer.
        ERROR: Appends an "ERROR" notification to the text buffer.
        LOG: Appends a "LOG" notification to the text buffer.
    Methods:
        __init__(who=">>", his_style=..., def_style=..., def_gradient=("...","...")):
            Initializes the UI with prompt, styles, and gradient colors.
        his_gradient(*colors, style=None):
            Appends the prompt with a gradient style using the given colors.
        clear():
            Clears the text buffer.
        cat_gradient(text="", *colors, style=None):
            Appends text with a gradient color effect.
        notify(title="NOTE", title_style=..., cover_style=None):
            Appends a notification with a styled title to the text buffer.
        input(text="", style=None):
            Prompts for user input with styled text.
        cat(text="", style=None):
            Appends text to the buffer with the given style.
        print(*args, style=None, sep=" ", end="\n"):
            Prints the current text buffer to the console, with optional styling and formatting.
    Notes:
        - Uses the `rich` library for text styling and console output.
        - Designed for interactive command-line applications needing rich text formatting.
        - Supports gradient coloring, styled notifications, and input prompts.
    """
    def __init__(self,who = ">>", his_style:Style = Style(color=default_Color,bold=True), def_style=Style(color=default_Color),def_gradient:tuple[str,str] = ("#ff0000","#0000ff")):
        self.text = Text()
        self.console = Console()
        self.his_style = his_style
        self.def_style = def_style
        self.who = who  
        self.spacer = "  "  
        self.def_gradient = def_gradient
        self.len = 0
    
    # === CyperxCommandLineRichUI Methods and Properties ===
    @property
    def him(self):
        """Appends the prompt and spacer to the text buffer."""
        self.text.append(self.who, style=self.his_style)
        self.text.append(self.spacer, style=self.def_style)
        return self

    def his_gradient(self, *colors, style: Style = None):
        """Appends the prompt with a gradient style using the given colors."""
        if not colors or len(colors) < 2:
            colors = self.def_gradient
        self.cat_gradient(self.who, *colors, style=style or self.his_style)
        self.text.append(self.spacer, style=self.def_style)
        return self

    @property
    def his_notify(self):
        """Appends a notification-style prompt to the text buffer."""
        self.text.append("[", style=self.def_style)
        self.text.append(self.who, style=self.his_style)
        self.text.append("]", style=self.def_style)
        self.text.append(self.spacer, style=self.def_style)
        return self

    def clear(self):
        """Clears the text buffer."""
        self.text = Text()
        return self

    @property
    def POP(self):
        """Returns a copy of the current text buffer and clears it."""
        text = self.text.copy()
        self.clear()
        return text

    def cat_gradient(self, text="", *colors, style: Style = None):
        """Appends text with a gradient color effect."""
        gradient = Text()
        style = style or self.def_style
        if len(colors) < 2:
            raise ValueError("You need at least two colors for a gradient.")

        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        rgb_colors = [hex_to_rgb(c) for c in colors]
        total_steps = len(text)
        segments = len(rgb_colors) - 1
        steps_per_segment = total_steps / segments

        for i, char in enumerate(text):
            seg = min(int(i // steps_per_segment), segments - 1)
            ratio = (i % steps_per_segment) / steps_per_segment
            start_rgb = rgb_colors[seg]
            end_rgb = rgb_colors[seg + 1]
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            color = f"rgb({r},{g},{b})"
            gradient.append(char, style=Style().combine([style, Style(color=color)]))

        self.text.append_text(gradient)
        return self

    def notify(self, title: Text | str = "NOTE", title_style: Style = Style(color="blue", bold=True), cover_style: Style = None):
        """Appends a notification with a styled title to the text buffer."""
        cover_style = cover_style or self.def_style
        cover_style = Style().combine([self.def_style, cover_style])
        title_style = Style().combine([self.def_style, title_style])

        self.text.append("[", style=cover_style)
        self.text.append(title if type(title) == Text else title.upper(), style=title_style)
        self.text.append("]", style=cover_style)
        self.text.append(self.spacer, style=self.def_style)
        return self

    def input(self, text: Text | str = "", style: Style = None):
        """Prompts for user input with styled text."""
        style = style or self.def_style
        text_ = Text(text)
        text_.stylize(style)
        return self.console.input(text_)

    def cat(self, text: Text | str = "", style: Style = None):
        """Appends text to the buffer with the given style."""
        self.text.append(text, style=style or self.def_style)
        return self

    def print(self, *args, style: Style = None, sep=" ", end="\n"):
        """Prints the current text buffer to the console, with optional styling and formatting."""
        self.text.append(sep.join(args), style=style or self.def_style)
        if end == "\r":
            if self.text.__len__() > self.len:
                self.len = self.text.__len__()
            self.text.append(f"{" ".rjust(self.len - self.text.__len__())}")
        self.console.print(self.text, end=end)
        self.clear()
        return self

    NOTIFY = notify

    @property
    def LOGGING(self):
        """Appends a 'LOGGING' notification to the text buffer."""
        self.notify("LOGGING", Style(color="#0000FF", bold=True), Style(color="#ffffff", bold=True))
        return self

    @property
    def INFO(self):
        """Appends an 'INFO' notification to the text buffer."""
        self.notify("INFO", Style(color="#00ff00", bold=True), Style(color="#ffffff", bold=True))
        return self

    @property
    def WARNING(self):
        """Appends a 'WARNING' notification to the text buffer."""
        self.notify("INFO", Style(color="#ffff00", bold=True), Style(color="#ffffff", bold=True))
        return self

    @property
    def ERROR(self):
        """Appends an 'ERROR' notification to the text buffer."""
        self.notify("INFO", Style(color="#ff0000", bold=True), Style(color="#ffffff", bold=True))
        return self

    @property
    def LOG(self):
        """Appends a 'LOG' notification to the text buffer."""
        self.notify("INFO", Style(color="#00ff00", bold=True), Style(color="#ffffff", bold=True))
        return self