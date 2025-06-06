"""
WPN (What's Playing Now) Textual TUI

This module provides a Textual-based Terminal User Interface for the WPN web scraper.
It offers an interactive way to access all WPN functionality.
"""

from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Select,
    Static,
)

from wpn import WPN


class WPNTUI(App):
    """The main WPN TUI application."""

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("s", "search", "Search Song", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.wpn = WPN()
        self.current_channel: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Vertical(
                Horizontal(
                    Select(
                        [(channel, channel) for channel in self.wpn.channel_list],
                        id="channel_select",
                        prompt="Select Channel",
                    ),
                    Button("Refresh", id="refresh_btn"),
                    id="controls",
                ),
                Static("", id="current_song"),
                DataTable(id="previous_songs"),
                id="main_content",
            ),
            id="app_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the app when it starts."""
        # Set up the data table
        table = self.query_one("#previous_songs", DataTable)
        table.add_columns("Song", "Artist")
        table.cursor_type = "row"

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle channel selection."""
        self.current_channel = event.value
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh the current channel's data."""
        if not self.current_channel:
            return

        # Get current song
        current_song, current_artist = self.wpn.get_current_song(self.current_channel)
        current_song_widget = self.query_one("#current_song", Static)
        current_song_widget.update(f"Now Playing: {current_song} by {current_artist}")

        # Get previous songs
        table = self.query_one("#previous_songs", DataTable)
        table.clear()
        previous_songs = self.wpn.get_previous_songs(self.current_channel)
        for song, artist in reversed(previous_songs):  # Most recent first
            table.add_row(song, artist)

    def action_refresh(self) -> None:
        """Refresh the current data."""
        self.refresh_data()

    def action_search(self) -> None:
        """Search for a song across all channels."""
        # TODO: Implement song search dialog
        pass


def main():
    """Run the WPN TUI application."""
    app = WPNTUI()
    app.run()


if __name__ == "__main__":
    main()
