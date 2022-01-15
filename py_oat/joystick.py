
#!/usr/bin/env python3
import curses
import time
import sys
import re

class Joystick():
    def __init__(self, horizontal, vertical, keypress_delay):
        self._status = ""
        self.horizontal = horizontal
        self.vertical = vertical
        self.keypress_delay = 1

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self,line):
        self._status = line
        screen = self.screen
        self.clearline(3)
        screen.addstr(3, 0, line)
 
    def clearline(self, line):
        screen = self.screen
        screen.move(line, 0)
        screen.clrtoeol()

    def keypress(self):
        self.keypress_timeout = time.time()
        self.keypress_shown = True
        self.status = F"{self.vertical}: {self.y} | {self.horizontal}: {self.x}"
        return True
    
    def right(self):
        self.x += 1
        self.y = 0
        self.keypress()
    
    def left(self):
        self.x -= 1
        self.y = 0
        self.keypress()

    def up(self):
        self.x = 0
        self.y += 1
        self.keypress() 

    def down(self):
        self.x = 0
        self.y -= 1
        self.keypress() 
    
    def prepare(self):
        screen = self.screen
        # turn off input echoing
        curses.noecho()
        # respond to keys immediately (don't wait for enter)
        curses.cbreak()
        # map arrow keys to special values
        screen.keypad(True)
        screen.nodelay(1)
        screen.addstr(0, 0, f'Up/Down => {self.vertical}, Right/Left => {self.horizontal}. "q" to exit')

    def update(self):
        pass
        
    def loop(self):
        self.screen = curses.initscr()
        screen = self.screen
        self.x = 0
        self.y = 0
        self.prepare()

        self.keypress_timeout = time.time()
        status_timeout = time.time()
        self.keypress_shown = False
        status_shown = False
        try:
            while True:
                char = screen.getch()
                if char == ord('q'):
                    break
                elif char == curses.KEY_RIGHT:
                    self.right()
                elif char == curses.KEY_LEFT:
                    self.left()
                elif char == curses.KEY_UP:
                    self.up()
                elif char == curses.KEY_DOWN:
                    self.down()
                if (time.time() - self.keypress_timeout) > self.keypress_delay and self.keypress_shown:
                    self.keypress_shown = False
                    self.update()
                    status_shown = True
                    status_timeout = time.time()
                if time.time() - status_timeout > 3 and status_shown:
                    status_shown = False
                    self.status = ""
        finally:
            # shut down cleanly
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()

class AutoPAControl(Joystick):
    def __init__(self):
        super().__init__( "Azimuth", "Altitude")

    def altaz(self):
        #print("updating")
        time.sleep(1)
        self.status += "updated."

    def update(self):
        if self.x != 0:
            self.status = f"Adjusting azimuth by {self.x} arcminutes..."
            self.altaz()
        if self.y != 0:
            self.status = f"Adjusting altitude by {self.y} arcminutes..."
            self.altaz()
        self.x = 0
        self.y = 0


class FocusControl(Joystick):
    def __init__(self):
        super().__init__("Speed", "In/out", 1)

    def focus(self):
        #print("updating")
        time.sleep(1)
        self.status += "updated."

    def update(self):
        if self.x != 0:
            self.status = f"Adjusting speed to {self.x}..."
            self.focus()
        if self.y != 0:
            self.status = f"Adjusting focus to {self.y}..."
            self.focus()
        self.x = 0
        self.y = 0

#joystick = Focus()
#joystick.loop()
