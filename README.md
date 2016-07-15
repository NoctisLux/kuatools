# Kuatools

todo:
* add authentification to classes dealing with the API (before August)
* record the progression of followers during a stream
* add exception handling for lack of connection (ConnectionError)
* add an ending message to Screen when the program ends
* format error messages to contain the type of exception
* format time in messages with datetime attributes
* add unit tests

## General

### Introduction
KUATools, or Knowledge Usage and Acquisition Tools, is a Python 3 module implementing simple classes used for the acquisition and subsequent analysis of relevant data from Twitch livestreams. It is intended as the base of programs assisting Twitch streamers in the appreciation of their performances, specifically between the beginning and the and of their stream.
### Dependencies
This module uses the following modules:
* requests (package python3-requests on Debian, or pip install requests)
### Planned features
* a class dedicated to the extraction of valuable information from ChannelStats
* a class dedicated to the representation of this data, including charts
* multithreading support for concurrent tracking of more than one stream, or live analysis
* a functional GUI

## Current status
This is work in progress.
### Known issues
* a disconnection from the internet will cause the Tracker to crash.

### Content
####Class Snapshot
Represents the information on a livestream at a given time
* __init__(self, viewers, game, time=datetime.now())
* getTime(self) returns time as a datetime
* getViewers(self) returns the viewer count at that time as an integer
* getGame(self) returns the game played at that time as a string
* dumpable(self) returns a json-friendly tuple of the Snapshot

####Class StreamStats
Contains the statistics of a livestream
* __init__(self, streamer, dump=None)
* dumpable(self) returns a json-friendly list of tuples representing the self.snaps list
* add(self, snap) adds a Snapshot at the end of the current list

####Class ChannelStats
* __init__(self, streamer, dump=None)
* dumpable(self) returns a json-friendly version of the self.streams list
* add(self, stream) adds a StreamStats at the end of the list
* getLast(self) returns the last StreamStats recorded

####Class Screen
Wrapper for interaction with the terminal
* write(self, message) writes the message in the terminal followed by an endline
* __init__(self, programName)
* writeWarning(self, warning) writes a more visible message in the terminal for warnings
* writeError(self, error) writes an error message in a more visible formatting
* ask(self, prompt) returns the user's input after displaying the prompted message

####Class Logger
Centralized log for the program
* _write(self, message) Should not be used outside of the Logger
* __init__(self, fileName, programName, terminal)
* writeEvent(self, message) writes an event with the proper formatting in the log
* writeError(self, message) writes an error with the proper formatting in the log

####Class StatsDump
Wrapper for the file where the stats of a channel are stored
* __init__(self, streamer)
* dump(self, dumpable) writes the dumpable ChannelStats to the streamer_viewers.json
* load(self) Returns the dump for the recreation of ChannelStats

####Class TwitchStream
Creates the statistics of a StreamStats
* __init__(self, streamer)
* snap(self) returns a Snapshot of the current information of the livestream

####Class Tracker
Tool tracking and recording the stats of a live channel
* __init__(self, streamer, globalLog, terminal)
* connect(self, retryDelay=10) tries to make a Snapshot of the livestream to return it. Returns None if failed after 10 attempts
* track(self, interval=300) fires the tracking process of the livestream to get and log a Snapshot of it every <interval> seconds

============================================

# Kuatracker

todo:
* stuff
* more stuff

## General

### Introduction
Kuatracker is the main application of kuatools.
### Instructions
Open kuatracker.py and change the streamer variable to your name between quotes before closing it. You can then execute kuatracker.py once your stream is live. The rest of the process is automated.
### Planned features
/
## Current status
Essentially a working prototype. Please report any issue encountered along with the kuatracker.log file generated.
### Features
It kinda works, that's a great feature right?