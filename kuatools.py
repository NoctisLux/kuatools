#!/usr/bin/python3

import requests
import json
import datetime as dt
from time import sleep

class Snapshot:
    """Represents the information on a livestream at a given time"""
    def __init__(self, viewers, game, followers, time=dt.datetime.now()):
        self.time = time
        self.viewers = viewers
        self.game = game
        self.followers = followers
    def getTime(self):
        """returns time as a datetime"""
        return self.time.replace()
    def getViewers(self):
        """returns the viewer count at that time as an integer"""
        return self.viewers
    def getGame(self):
        """returns the game played at that time as a string"""
        return self.game
    def getFollowers(self):
        """returns the follower count at that time as an integer"""
        return self.followers
    def dumpable(self):
        """returns a json-friendly tuple of the Snapshot"""
        return tuple((self.viewers, self.game, self.followers ,str(self.time)[:19]))

class StreamStats:
    """Contains the statistics of a livestream"""
    def __init__(self, streamer, dump=None):
        self.streamer = streamer
        self.snaps = []
        if dump != None:
            for s in dump:
                self.snaps.append(Snapshot(s[0], s[1], s[2], dt.datetime.strptime(s[3], "%Y-%m-%d %H:%M:%S")))
    def dumpable(self):
        """returns a json-friendly list of tuples representing the self.snaps list"""
        dumpableSnaps = []
        for s in self.snaps:
            dumpableSnaps.append(s.dumpable())
        return dumpableSnaps
    def add(self, snap):
        """Adds a Snapshot at the end of the current list"""
        self.snaps.append(snap)

class ChannelStats:
    """Contains the statistics of all recorded livestreams"""
    def __init__(self, streamer, dump=None):
        self.streams = []
        self.streamer = streamer
        if dump != None:
            for stream in dump:
                self.streams.append(StreamStats(self.streamer, stream))
    def dumpable(self):
        """Returns a json-friendly version of the self.streams list."""
        dumpableStreams = []
        for s in self.streams:
            dumpableStreams.append(s.dumpable())
        return dumpableStreams
    def add(self, stream):
        """Adds a StreamStats at the end of the list"""
        self.streams.append(stream)
    def getLast(self):
        """Returns the last StreamStats recorded"""
        return self.streams[-1]

class Screen:
    """wrapper for interaction with the terminal"""
    def write(self, message):
        """Writes the message in the terminal followed by and endline"""
        print(message + "\n")
    def __init__(self, programName):
        self.program = programName
        self.write("\t\t==={}===".format(self.program))
    def end(self):
        self.write("\t\t===End of {}===".format(self.program))
    def writeWarning(self, warning):
        """Writes a more visible message in the terminal for warnings"""
        self.write("\tWarning: {}".format(warning))
    def writeError(self, error):
        """Writes an error message in a more visible formatting"""
        #self.write("\t" + str(dt.datetime.now()) + " Error: " + error)
        self.write("\t[{0}]Error: {1}".format(str(dt.datetime.now())[:19], error))
    def ask(self, prompt):
        """Returns the user's input after displaying the prompted message"""
        return input(prompt)

class Logger:
    """centralized log for the program"""
    def _write(self, message):
        """Should not be used outside of the Logger"""
        logFile = open(self.fileName, "a", encoding ="utf-8")
        logFile.write(message + "\n")
    def __init__(self, fileName, programName, terminal):
        self.fileName = fileName
        self.terminal = terminal
        #check for an existing log file
        try:
            logFile = open(fileName, "r", encoding="utf-8")
            logFile.close()
        except FileNotFoundError:
            #self.terminal.writeWarning("No previous log (file " + fileName + ") has been found (normal on the first execution)")
            self.terminal.writeWarning("No previous log (file {0}) has been found (normal on the first execution)".format(fileName))
            try:
                self._write("\t\t====Log file of {0}===".format(programName))
            except Exception as e:
                self.terminal.writeError(str(e))
        #marks the start of this logging process in the file
        try:
            self._write("\t--started on {0}--".format(str(dt.datetime.now())[:19]))
        except Exception as e:
            self.terminal.writeError(str(e))
    def writeEvent(self, message):
        """Writes an event with the proper formatting in the log"""
        try:
            self._write("[{0}] Event: {1}".format(str(dt.datetime.now())[:19],message))
        except:
            self.terminal.writeError("Failed to log event \'{}\'".format(message))
    def writeError(self, message):
        """Writes an error with the proper formatting in the log"""
        try:
            self._write("[{0}]Error: {1} ".format(str(dt.datetime.now())[:19],message))
        except:
            self.terminal.writeError("Failed to log error \'{}\'".format(message))

class StatsDump:
    """wrapper for the file where the stats of a channel are stored"""
    def __init__(self, streamer):
        self.fileName = "{}_viewers.json".format(streamer)
    def dump(self, dumpable):
        """"Writes the dumpable ChannelStats to the streamer_viewers.json"""
        statsFile = open(self.fileName, "w", encoding="utf-8")
        statsFile.write(json.dumps(dumpable))
        statsFile.close()
    def load(self):
        """Returns the dump for the recreation of ChannelStats"""
        statsFile = open(self.fileName, "r", encoding="utf-8")
        previousDump = json.loads(statsFile.read())
        statsFile.close()
        return previousDump            

class TwitchStream:
    """Create the statstics of a StreamStats"""
    def __init__(self, streamer, globalLog):
        self.globalLog = globalLog
        self.streamer = streamer
    def snap(self):
        """Returns a Snapshot of the current informations of the livestream"""
        apiAnswerStream = requests.get("https://api.twitch.tv/kraken/streams/" + self.streamer).json()['stream']
        apiAnswerChannel = requests.get("https://api.twitch.tv/kraken/channels/" + self.streamer).json()
        if apiAnswerStream != None:
            return Snapshot(apiAnswerStream["viewers"], apiAnswerStream["game"], apiAnswerChannel["followers"])
        return None
class Tracker:
    """Tool tracking and recording the stats of a live channel"""
    def __init__(self, streamer, globalLog, terminal):
        self.streamer = streamer
        self.liveStream = TwitchStream(streamer, globalLog)
        self.channelDump = StatsDump(streamer)
        self.globalLog = globalLog
        self.terminal = terminal
        try:
            self.channelInfo = ChannelStats(streamer, self.channelDump.load())
        except FileNotFoundError:
            self.channelInfo = ChannelStats(streamer)
    def connect(self, retryDelay=10):
        """Tries to make a Snapshot of the livestream to return it. Returns None if failed after 10 attempts."""
        s = None
        attempt = 0
        while (s == None) and (attempt < 11):
            attempt+= 1
            try:
                s = self.liveStream.snap()
                if (s == None):
                    self.terminal.write("(attempt {0} of 10) The tracked stream is offline.".format(str(attempt)))
            except requests.exceptions.ConnectionError:
                self.terminal.write("(attempt {0} of 10) The service is unavailable or you have no connection.".format(str(attempt)))
            if (s == None):
                sleep(retryDelay)
        return s
    def track(self, interval=300):
        """Fires the tracking process of the livestream to get and log a Snapshot of it every <interval> seconds."""
        self.channelInfo.add(StreamStats(self.streamer))
        self.terminal.write("\t--start of {}\'s tracking--".format(self.streamer))
        self.terminal.write("Establishing connection...")
        s = self.connect()
        while s != None:
            self.channelInfo.getLast().add(s)
            self.terminal.write("[{0}] \tviewer count: {1}".format(str(s.getTime())[:19], str(s.getViewers())))
            try:
                self.channelDump.dump(self.channelInfo.dumpable())
            except Exception as e:
                trySave = 'y'
                self.terminal.writeWarning("The latest stats on {} couldn't be saved.".format(self.streamer))
                self.globalLog.writeError(str(e))
            else:
                trySave = 'n'
                self.globalLog.writeEvent("{}'s channel stats have been successfully saved".format(self.streamer))
            sleep(interval)
            s = self.connect()
        self.terminal.write("\t--End of {}\'s tracking--".format(self.streamer))
        trySave = 'y'
        success = False
        while (success == False) and (trySave in ['y', 'Y']):
            try:
                self.channelDump.dump(self.channelInfo.dumpable())
            except Exception as e:
                self.globalLog.writeError(str(e))
                trySave = self.terminal.ask("The information on {} \'s channel couldn't be saved. Try again? (y/N): ".format(self.streamer))
            else:
                success == True
                self.terminal.write("Information on {}\'s channel successfully saved".format(self.streamer))
