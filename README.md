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

## API Reference

### WPN Class

#### `__init__()`
Initialize the WPN scraper with an up-to-date directory of channels.

#### `get_directory(sort=True)`
Create an up-to-date directory of channels and URLs from the WPN website.

#### `get_channel_name(channel_input)`
Filter input to match a valid channel name or accept an integer to get a channel by index.

#### `get_current_song(channel_input)`
Get the current song playing on a specified channel, returned as a tuple of (song, artist).
The `channel_input` can be either a string (channel name) or an integer (channel index).

#### `get_previous_songs(channel_input)`
Get a list of previous songs played on a channel as a list of (song, artist) tuples, ordered from oldest to most recent.
The `channel_input` can be either a string (channel name) or an integer (channel index).

#### `get_all_songs(channel_input)`
Get a list of current and previous songs for a channel as a list of (song, artist) tuples. The list is structured so that:
- Index 0 contains the current song
- Negative indices can be used to access previous songs chronologically
- songs[-1] is the most recently played previous song
- songs[-2] is the second most recently played previous song, and so on

The `channel_input` can be either a string (channel name) or an integer (channel index).

#### `get_all_song_data()`
Generate the song data for all songs currently playing on all channels.

#### `identify_channel_by_song(song_input)`
Identify which channel is playing a given song using fuzzy matching. Returns a tuple containing:
- The channel name
- The matched song tuple (song, artist)
- The confidence score (0-100)

The `song_input` can be a partial song name or include artist information. The matching is done using fuzzy string matching, so it will work even with slight differences in the text.

## Project Structure

```wpn/
├── src/
│   └── wpn/
│       ├── __init__.py
│       └── wpn.py
├── tests/
│   └── test_wpn.py
├── pyproject.toml
└── README.md
```

## Testing

Run tests using pytest:

```
python -m pytest
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

