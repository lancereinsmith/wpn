"""
WPN (What's Playing Now) Web Scraper

This module provides functionality to scrape song information from the Muzak WPN website.
It retrieves current and historical song data for various music channels/stations.

The WPN class provides methods to:
- Get a directory of available channels
- Retrieve the current song playing on a specific channel
- Get a list of previous songs played on a channel
- Get a complete list of current and previous songs for a channel
- Fetch and process all song data for all available channels

Usage:
    from wpn import WPN

    # Create an instance
    wpn = WPN()

    # Get all available channels
    channels = wpn.channel_list

    # Get current song on a specific channel
    song, artist = wpn.get_current_song("Channel Name")

    # Get all songs (current and previous) for a channel
    songs = wpn.get_all_songs("Channel Name")

    # Get previous songs using negative indices
    recent_song = songs[-1]  # Most recently played song (before current)
    two_songs_ago = songs[-2]  # Second most recently played song

    # Get all song data for all channels
    all_data = wpn.get_all_song_data()
"""

from importlib.metadata import version

__version__ = version("wpn")  # Uses installed package metadata

import json
import os
import re
from typing import Union

import click
import grequests
import requests
from bs4 import BeautifulSoup
from thefuzz import process

BASEADDR = "http://muzakwpn.muzak.com/"


class WPN:
    def __init__(self):
        self.directory = self._get_directory()
        self.song_data = {k: {"url": v} for k, v in self.directory.items()}
        self.channel_list = list(self.directory.keys())
        self.urls = list(self.directory.values())

    def _get_soup(self, html: str) -> BeautifulSoup:
        """Given html, return a BeautifulSoup object.

        Args:
            html (str): HTML document

        Returns:
            BeautifulSoup: Parsable object of the html document.
        """
        return BeautifulSoup(html, "html.parser")

    def _get_directory(self, sort: bool = True) -> dict[str, dict[str, str]]:
        """Create an up-to-date directory of channels and urls from the WPN website.

        Args:
            sort (bool, optional): Whether to sort the directory. Defaults to True.

        Returns:
            dict[str,str]: The directory of channel keys matched with the channel url.
        """
        html = requests.get(BASEADDR).text
        soup = self._get_soup(html)
        crumblinks = soup.find_all(class_="crumblink")
        wpnaddr = re.compile(r"wpn/...\.html")
        self.directory = {
            crumblink.text: os.path.join(
                BASEADDR, wpnaddr.findall(crumblink["onclick"])[0]
            )
            for crumblink in crumblinks[1:]
        }
        if sort:
            self.directory = dict(
                sorted(self.directory.items(), key=lambda item: item[0])
            )
        return self.directory

    def _split_song(self, song: str) -> tuple[str, str]:
        """Given an artist and song as a string, convert it into a tuple.

        Args:
            song (str): A string containing song and artist information.

        Returns:
            tuple[str, str]: A tuple containing (song, artist).
        """
        # Check if song is a Tag object from BeautifulSoup
        if hasattr(song, "text"):
            text = song.text.strip()
        else:
            text = str(song).strip()

        # Split by ", by " to separate song and artist
        parts = text.split(", by ", 1)
        if len(parts) > 1:
            return (parts[0].strip(), parts[1].strip())
        else:
            return (parts[0].strip(), "Unknown Artist")

    def _get_song_list_from_html(self, html: str) -> tuple[str, list[tuple[str, str]]]:
        """Given the html for a channel, generate a song list.

        Args:
            html (str): HTML document for a channel URL

        Returns:
            tuple[str, list[tuple[str, str]]]: A tuple containing the channel name and
                                            a list of tuples containing (song, artist) info.
                                            Index 0 is current song, negative indices refer
                                            to previous songs chronologically (-1 is most recent).
        """
        soup = self._get_soup(html)
        all_channel_data = soup.find(id="titles")
        # get the channel name
        channel_name = all_channel_data.find("p").find("b").text.replace("Now on ", "")
        # get first song (current song)
        current_song = self._split_song(list(all_channel_data.children)[0].contents[-1])
        # list for previous songs that will be reversed
        previous_songs = []

        # try to add additional songs
        try:
            # add second song to previous_songs
            previous_songs.append(self._split_song(list(all_channel_data.children)[2]))
            # add songs 3-10 to previous_songs
            previous_songs.extend(
                self._split_song(song)
                for song in list(all_channel_data.children)[3]
                if len(song.text) > 1
            )
            # reverse previous_songs so that most recent is last (for negative indexing)
            previous_songs.reverse()
            # combine current song with reversed previous songs
            song_list = [current_song] + previous_songs
            return channel_name, song_list
        except IndexError:
            return channel_name, [current_song]

    def _get_all_channels(self, urls: list[str]) -> list[requests.models.Response]:
        """Given a list of URLs, perform simultaneous GET requests on those and return
        the data as a list.

        Args:
            urls (list[str]): A list of URLs.

        Returns:
            list[requests.models.Response]: A list of requests Response objects from the URLs.
        """
        reqs = (grequests.get(url) for url in urls)
        web_data = grequests.map(reqs)
        return web_data

    def get_channel_name(self, channel_input: Union[int, str]) -> str:
        """Filter input to match a valid channel name.  Or, accept an integer to get a
        channel by index.

        Args:
            channel_input (Union[int, str]): User input for the channel.

        Returns:
            str: A valid channel name from the WPN website.
        """
        if channel_input in self.channel_list:
            return channel_input
        elif isinstance(channel_input, int):
            return self.channel_list[channel_input]
        else:
            return process.extractOne(channel_input, self.channel_list)[0]

    def get_all_song_data(self) -> dict:
        """Generate the song data for all songs currently playing.

        Returns:
            dict: A dictionary of all the WPN data.
        """
        # get the webdata
        web_data = self._get_all_channels(self.urls)
        # cycle through the responses, extract the channel name and song list,
        # and add to the song_data
        for channel in web_data:
            channel_name, song_list = self._get_song_list_from_html(channel.text)
            channel_name = self.get_channel_name(channel_name)
            self.song_data[channel_name].update({"song_list": song_list})
        return self.song_data

    def get_current_song(self, channel_input: Union[str, int]) -> tuple[str, str]:
        """Given a channel name or index, get the current song and artist.

        Args:
            channel_input (Union[str, int]): The name of the channel, or index number.

        Returns:
            tuple[str, str]: The current song as a tuple (song, artist).
        """
        channel_name = self.get_channel_name(channel_input)
        song_data = self.get_all_song_data()
        return song_data[channel_name]["song_list"][0]

    def get_previous_songs(
        self, channel_input: Union[str, int]
    ) -> list[tuple[str, str]]:
        """Given a channel name or index, get the previous songs and artists.

        Args:
            channel_input (Union[str, int]): The name of the channel, or index number.

        Returns:
            list[tuple[str, str]]: A list of previous songs as tuples (song, artist).
                                  Ordered from oldest to most recent.
        """
        channel_name = self.get_channel_name(channel_input)
        song_data = self.get_all_song_data()
        # Return all songs except the current one (index 0), in the order they appear
        return song_data[channel_name]["song_list"][1:]

    def get_all_songs(self, channel_input: Union[str, int]) -> list[tuple[str, str]]:
        """Given a channel name or index, get current and previous songs and artists.

        Args:
            channel_input (Union[str, int]): The name of the channel, or index number.

        Returns:
            list[tuple[str, str]]: A list of current and previous songs
            as tuples (song, artist).
        """
        channel_name = self.get_channel_name(channel_input)
        song_data = self.get_all_song_data()
        return song_data[channel_name]["song_list"]

    def identify_channel_by_song(
        self, song_input: str
    ) -> tuple[str, tuple[str, str], float]:
        """Identify which channel is playing a given song using fuzzy matching.

        Args:
            song_input (str): The song name or partial song name to search for.

        Returns:
            tuple[str, tuple[str, str], float]: A tuple containing:
                - The channel name
                - The matched song tuple (song, artist)
                - The confidence score (0-100)
        """
        # Get all current songs across all channels
        song_data = self.get_all_song_data()

        # Create a list of all current songs with their channel names
        current_songs = []
        for channel, data in song_data.items():
            if "song_list" in data and len(data["song_list"]) > 0:
                current_song = data["song_list"][0]  # Get current song
                current_songs.append((channel, current_song))

        # Create a list of song strings for matching
        song_strings = [f"{song[0]} by {song[1]}" for _, song in current_songs]

        # Find the best match
        best_match = process.extractOne(song_input, song_strings)

        if best_match:
            match_index = song_strings.index(best_match[0])
            channel, song_tuple = current_songs[match_index]
            return channel, song_tuple, best_match[1]

        return None, None, 0.0


@click.group()
def cli():
    """Command-line interface for the WPN (What's Playing Now) web scraper."""
    pass


@cli.command(
    "all-data", help="Get all song data for all channels and save to a JSON file."
)
@click.option(
    "--output",
    "-o",
    type=str,
    default="output/output.json",
    help="Path to save the JSON output file",
)
def all_data(output):
    """Get all song data for all channels and save to a JSON file."""
    try:
        wpn = WPN()
        data = wpn.get_all_song_data()

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output), exist_ok=True)

        with open(output, "w", encoding="UTF-8") as f:
            json.dump(data, f, indent=2)

        click.echo(f"Data saved to {output} with {len(data)} channels")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command("list", help="List all available music channels.")
def list_channels():
    """List all available music channels."""
    wpn = WPN()
    channels = wpn.channel_list
    click.echo(f"Available channels ({len(channels)}):")
    for i, channel in enumerate(channels):
        click.echo(f"{i}: {channel}")


@cli.command("songs", help="Get all songs (current and previous) for a channel.")
@click.argument("channel", type=str)
def all_songs(channel):
    """Get all songs (current and previous) for a channel.

    CHANNEL can be the exact channel name, a partial name that will be matched,
    or an index number from the list command.
    """
    wpn = WPN()
    try:
        # Handle integer input
        if channel.isdigit():
            channel = int(channel)

        channel_name = wpn.get_channel_name(channel)
        songs = wpn.get_all_songs(channel)
        click.echo(f"All songs on {channel_name}:")
        click.echo(f"Currently playing: {songs[0][0]} by {songs[0][1]}")
        if len(songs) > 1:
            click.echo("Previously played (most recent first):")
            # Show previous songs in reverse order (most recent first)
            for i, (song, artist) in enumerate(reversed(songs[1:]), 1):
                click.echo(f"{i}. {song} by {artist}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command("current", help="Get the current song playing on a specific channel.")
@click.argument("channel", type=str)
def current_song(channel):
    """Get the current song playing on a specific channel.

    CHANNEL can be the exact channel name, a partial name that will be matched,
    or an index number from the list command.
    """
    wpn = WPN()
    try:
        # Handle integer input
        if channel.isdigit():
            channel = int(channel)

        channel_name = wpn.get_channel_name(channel)
        song, artist = wpn.get_current_song(channel)
        click.echo(f"Channel: {channel_name}")
        click.echo(f"Now playing: {song} by {artist}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command("previous", help="Get a list of previous songs played on a channel.")
@click.argument("channel", type=str)
def previous_songs(channel):
    """Get a list of previous songs played on a channel.

    CHANNEL can be the exact channel name, a partial name that will be matched,
    or an index number from the list command.
    """
    wpn = WPN()
    try:
        # Handle integer input
        if channel.isdigit():
            channel = int(channel)

        channel_name = wpn.get_channel_name(channel)
        songs = wpn.get_previous_songs(channel)
        click.echo(f"Previous songs on {channel_name} (most recent first):")

        # Reverse the order to show most recent first
        songs_to_display = list(reversed(songs))
        for i, (song, artist) in enumerate(songs_to_display, 1):
            click.echo(f"{i}. {song} by {artist}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command("identify", help="Identify which channel is playing a given song.")
@click.argument("song", nargs=-1, type=str)
def identify_channel(song):
    """Identify which channel is playing a given song given the song name and/or artist name.

    SONG can be the exact song name or a partial name that will be matched.
    Multiple words are allowed.
    """
    wpn = WPN()
    try:
        # Join all parts of the song argument into a single string
        song_query = " ".join(song)
        channel, song_info, confidence = wpn.identify_channel_by_song(song_query)
        if channel and song_info:
            click.echo(f"Channel: {channel}")
            click.echo(f"Song: {song_info[0]} by {song_info[1]}")
            click.echo(f"Confidence: {confidence:.1f}%")
        else:
            click.echo("No matching song found across all channels.")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command("tui", help="Launch the interactive Textual TUI application.")
def launch_tui():
    """Launch the interactive Textual TUI application."""
    from wpn.tui import main

    main()


if __name__ == "__main__":
    cli()
