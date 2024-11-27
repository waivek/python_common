
import rich
from rich.panel import Panel

console = rich.get_console()
console._highlight = False

# panel example

console.print(Panel("Hello, World!", border_style="bright_blue", title="[black on bright_blue bold] PANEL ", title_align="right", subtitle="[black on bright_blue bold] END ", subtitle_align="right"))
