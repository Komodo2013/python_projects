import plyer

import todoist
import canvas
import google.gtasks as tasks, google.gcalendar as gcal
import gui

gui = gui.PyCalendarApp()

print("finished init")

if __name__ == "__main__":
    gui.run()
