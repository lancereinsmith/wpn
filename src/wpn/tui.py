"""
WPN (What's Playing Now) Textual TUI

This module provides a Textual-based Terminal User Interface for the WPN web scraper.
It offers an interactive way to access all WPN functionality.
"""

from rich.style import Style
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Static,
)

from wpn import WPN


class FilterInput(Input):
    """Custom input widget for filtering channels."""

    class FilterChanged(Message):
        """Message sent when the filter text changes."""

        def __init__(self, filter_text: str) -> None:
            self.filter_text = filter_text
            super().__init__()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes and emit filter message."""
        self.post_message(self.FilterChanged(event.value))


class Instructions(Static):
    """Widget to display instructions."""

    def __init__(self):
        instructions = Text()
        instructions.append("Press ", style="bold")
        instructions.append("q", style="bold yellow")
        instructions.append(" to quit, ", style="bold")
        instructions.append("r", style="bold yellow")
        instructions.append(" to refresh, ", style="bold")
        instructions.append("f", style="bold yellow")
        instructions.append(" to focus filter", style="bold")
        super().__init__(instructions)


class ChannelCard(Widget):
    """A card widget displaying channel information."""

    def __init__(self, channel_name: str, song_list: list[tuple[str, str]], color: str):
        super().__init__()
        self.channel_name = channel_name
        self.song_list = song_list
        self.color = color

    def compose(self) -> ComposeResult:
        """Create child widgets for the card."""
        # Channel name with larger font and bold
        channel_text = Text(self.channel_name, style=Style(color=self.color, bold=True))
        channel_text.stylize("bold", 0, len(self.channel_name))
        yield Static(channel_text, classes="channel-name")

        if self.song_list:
            current_song, current_artist = self.song_list[0]
            yield Static(
                Text(
                    f"Now Playing: {current_song} by {current_artist}",
                    style=Style(color=self.color),
                ),
                classes="current-song",
            )
            if len(self.song_list) > 1:
                # Previous songs header with bold
                header_text = Text("Previous Songs:", style=Style(bold=True))
                header_text.stylize("bold", 0, len("Previous Songs:"))
                yield Static(header_text, classes="previous-songs-header")

                for song, artist in self.song_list[1:]:
                    yield Static(
                        Text(f"• {song} by {artist}", style=Style(color=self.color)),
                        classes="previous-song",
                    )


class WPNTUI(App):
    """The main WPN TUI application."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("f", "focus_filter", "Focus Filter", show=True),
    ]

    # Define colors for channel cards
    COLORS = [
        "bright_blue",
        "bright_green",
        "bright_magenta",
        "bright_yellow",
        "bright_cyan",
        "bright_red",
        "bright_white",
    ]

    def __init__(self):
        super().__init__()
        self.wpn = WPN()
        self.song_data = reactive({})
        self.filter_text = reactive("")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Vertical(
                Instructions(),
                Horizontal(
                    Label("Filter:", classes="filter-label"),
                    FilterInput(
                        placeholder="Filter by channel, artist, or song...",
                        id="filter_input",
                    ),
                    Button("Refresh", id="refresh_btn"),
                    id="controls",
                ),
                ScrollableContainer(id="cards_container"),
                id="main_content",
            ),
            id="app_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the app when it starts."""
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh all channel data."""
        self.song_data = self.wpn.get_all_song_data()
        self.update_cards()

    def update_cards(self) -> None:
        """Update the channel cards with current data."""
        container = self.query_one("#cards_container", ScrollableContainer)
        container.remove_children()

        filter_text = str(self.filter_text).lower()

        for i, (channel_name, data) in enumerate(self.song_data.items()):
            if "song_list" not in data:
                continue

            # Check if this channel should be shown based on filter
            should_show = False
            if not filter_text:
                should_show = True
            else:
                # Check channel name
                if filter_text in channel_name.lower():
                    should_show = True
                else:
                    # Check all songs and artists
                    for song, artist in data["song_list"]:
                        if filter_text in song.lower() or filter_text in artist.lower():
                            should_show = True
                            break

            if should_show:
                color = self.COLORS[i % len(self.COLORS)]
                card = ChannelCard(channel_name, data["song_list"], color)
                container.mount(card)

    def on_filter_input_filter_changed(self, event: FilterInput.FilterChanged) -> None:
        """Handle filter text changes."""
        self.filter_text = event.filter_text
        self.update_cards()

    def action_refresh(self) -> None:
        """Refresh the current data."""
        self.refresh_data()

    def action_focus_filter(self) -> None:
        """Focus the filter input."""
        self.query_one("#filter_input", FilterInput).focus()


def main():
    """Run the WPN TUI application."""
    app = WPNTUI()
    app.run()


if __name__ == "__main__":
    main()
