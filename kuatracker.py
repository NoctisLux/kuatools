#!/usr/bin/python3

import kuatools as kt

program = "kuatracker 1.0"

terminal = kt.Screen(program)
log = kt.Logger("kuatools.log", program, terminal)
try:
    kuaTracker = kt.Tracker("swalmy21", log, terminal)
    kuaTracker.track()
except Exception as e:
    log.writeError(str(e))
terminal.write("\t\t===End of " + program + "===")
