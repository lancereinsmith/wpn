# WPN - What's Playing Now

A Python library for scraping and retrieving song information from the Muzak WPN (What's Playing Now) website. This tool allows you to get current and historical song data for various music channels/stations.

## Features

- Get a directory of available music channels
- Retrieve the current song playing on a specific channel
- Get a list of previous songs played on a channel
- Get a complete list of current and previous songs for a channel
- Fetch and process all song data for all available channels
- Export song data to JSON format
- Command-line interface for all functionality
- Identify which channel is playing a given song using fuzzy matching

## Installation

### Requirements

- Python 3.12 or higher
- Dependencies are specified in `pyproject.toml`

### Installation Options

#### 1. Install as a Python Package

Using `uv` (recommended):
```bash
uv pip install wpn
```

Or using `pip`:
```bash
pip install wpn
```

#### 2. Install as a Standalone Executable

Using `uv` (recommended):
```bash
uv tool install wpn
```

Or using `pipx`:
```bash
pipx install wpn
```

#### 3. Install from Source (Development)

If you want to contribute to the project or need the latest development version:

1. Clone this repository:
   ```bash
   git clone https://github.com/lancereinsmith/wpn.git
   cd wpn
   ```

2. Install using `uv` (recommended):
   ```bash
   pip install uv
   uv venv
   uv pip install -e .
   ```

3. Alternatively, you can use a standard venv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   pip install -e .
   ```

## Usage

### Python API Usage

```python
from wpn import WPN

# Create an instance
wpn = WPN()

# Get all available channels
channels = wpn.channel_list
print(f"Available channels: {len(channels)}")

# Get current song on a specific channel (by name or index)
song, artist = wpn.get_current_song("Channel Name")  # Using channel name
# Or
song, artist = wpn.get_current_song(5)  # Using channel index
print(f"Now playing: {song} by {artist}")

# Get all songs (current and previous) for a channel
songs = wpn.get_all_songs("Channel Name")  # Using channel name
# Or
songs = wpn.get_all_songs(5)  # Using channel index

# Current song is at index 0
current_song, current_artist = songs[0]
print(f"Now playing: {current_song} by {current_artist}")

# Previous songs can be accessed using negative indices
# Most recent previous song
if len(songs) > 1:
    prev_song, prev_artist = songs[-1]
    print(f"Previously played: {prev_song} by {prev_artist}")
    
    # Second most recent previous song
    if len(songs) > 2:
        older_song, older_artist = songs[-2]
        print(f"Before that: {older_song} by {older_artist}")

# Or iterate through all songs
for i, (song, artist) in enumerate(songs):
    if i == 0:
        print(f"Current: {song} by {artist}")
    else:
        print(f"Previous ({len(songs)-i}): {song} by {artist}")

# Get previous songs only (by name or index)
previous_songs = wpn.get_previous_songs("Channel Name")  # Using channel name
# Or
previous_songs = wpn.get_previous_songs(5)  # Using channel index

# Get all song data for all channels
all_data = wpn.get_all_song_data()
```

### Command-Line Interface

WPN provides a comprehensive command-line interface for accessing all functionality.

After installing the package, the `wpn` command will be available:

```
wpn --help
```

#### List all available channels

```
wpn list
```

#### Get the current song playing on a channel

```
wpn current "Channel Name"
# Or using channel index
wpn current 5
```

#### Get previous songs played on a channel

```
wpn previous "Channel Name"
# Or using channel index
wpn previous 5
```

This will display a list of previously played songs from most recent to least recent.

#### Get all songs (current and previous) for a channel

```
wpn songs "Channel Name"
# Or using channel index
wpn songs 5
```

#### Get all song data for all channels

```
wpn all-data
# Or specify custom output path
wpn all-data --output data.json
```

#### Identify which channel is playing a song

```
wpn identify "Song Name"
# Or with artist name
wpn identify "Song Name by Artist Name"
# Or without quotes
wpn identify Song Name by Artist Name
```

This will search across all channels for the given song and return:
- The channel name where the song is playing
- The full song information (song name and artist)
- A confidence score indicating how well the match was found

#### Interactive Terminal User Interface (TUI)

WPN includes a modern, interactive terminal interface that provides a visual way to browse and filter all channels and their songs.

```
wpn tui
```

The TUI features:
- Real-time display of all channels and their current songs
- Color-coded channel cards for easy visual distinction
- Live filtering by channel name, song title, or artist
- Keyboard shortcuts:
  - `q` to quit
  - `r` to refresh data
  - `f` to focus the filter input
- Scrollable interface for browsing many channels
- Previous songs list for each channel

The interface updates automatically when you type in the filter box, making it easy to find specific channels or songs. Each channel is displayed in its own card with a unique color, showing both the current song and a list of previously played songs.

## API Reference

### WPN Class

#### `