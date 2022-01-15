#!python3
#from msvcrt import getch
import time
import os
#import serial
import math
from datetime import date, datetime

serialport = '/dev/ttyUSB0'
#os.system('stty -F ' + serialport + ' -hupcl')

print("Opening serial port on " + serialport + '...')
#ser = serial.Serial(serialport, 19200, timeout = 1)
#res = ser.readline()[:-1].decode('utf-8')
#while res != '':
#    print(res)
#    res = ser.readline()[:-1].decode('utf-8')

# wait for reboot
#time.sleep(5)

class Deg():
    @property
    def string(self):
        return F"{self.deg}*{self.min}'{self.sec}"
    @string.setter
    def string(self,str):
        str = str if str != '' else F"0*0'0"
        str = str if str.find('*') >= 0 else F"{str}*0'0"
        str = str if str.find('\'') >= 0 else F"{str}'0"
        (deg,min) = str.split("*")
        (min,sec) = min.split("'")
        (self.deg,self.min,self.sec) = (int(deg),int(min),int(sec))

def cmd(cmd):
    print(cmd)
    if True:
        return F" {cmd} -> OK"  
    ser.write(str.encode(F":{cmd}#"))
    res = ser.readline()
    return res[:-1].decode('utf-8')

class Focuser():
    def __init__(self):
        self._speed = 1
    def inward(self):
        cmd("F+")
    def outward(self):
        cmd("F-")
    def stop(self):
        cmd("FQ")
    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self,val):
        self._speed = val
        cmd(F"F{self._speed}")
    def slow(self):
        self.speed = 1
    def fast(self):
        self.speed = 4
    @property
    def position(self):
        return int(cmd("Fp"))
    @property
    def state(self):
        str = cmd("FB")
        return int(str)

class DigitalLevel():
    def start(self):
        return cmd(F"XL1")
    def stop(self):
        return cmd(F"XL0")
    @property
    def values(self):
        (pitch,roll) = cmd(F"XLGC").split(",")
        return (int(pitch),int(roll))
    @property
    def reference(self):
        (pitch,roll) = cmd(F"XLGR").split(",")
        return (int(pitch),int(roll))
    @property
    def values(self):
        return cmd(F"XLGC")

class Mount():
    @property
    def firmware(self):
        return F"{cmd('GVP')} {cmd('GVN')}"
        
    def init(self):
        cmd("I")
    
    @property
    def slewing(self):
        return cmd("D") == '|'

    @property
    def tracking(self):
        return cmd("GIT") == '1'

    @property
    def guiding(self):
        return cmd("GIG") == '1'

    @property
    def info(self):
        #<board>,<RA Stepper Info>,<DEC Stepper Info>,<GPS info>,<AzAlt info>,<Gyro info>
        str = cmd('XGM').split(",")
        return str
    @property
    def driver_config(self):
        #<RA driver>,<RA slewMS>,<RA trackMS>|<DEC driver>,<DEC slewMS>,<DEC guideMS>
        str = cmd('XGMS').split(",")
        return str


    @property
    def latidute(self):
        (deg,min) = cmd(F'Gt').split("*")
        return float(deg) + float(min) / 60 
    @latidute.setter
    def latidute(self, val):
        time = cmd(F'St{int(val)}*{val * 60 % 60}')

    @property
    def longitude(self):
        (deg,min) = cmd(F'Gg').split("*")
        return float(deg) + float(min) / 60 
    @longitude.setter
    def longitude(self, val):
        time = cmd(F'Sg{int(val)}*{val * 60 % 60}')

    @property
    def ha(self):
        str = cmd('XGH')
        return datetime.strptime(str, "%H%M%S")

    @property
    def lst(self):
        str = cmd(F'XGL')
        return datetime.strptime(str, "%H%M%S")
    @lst.setter
    def lst(self, d):
        time = cmd(F'SHL{d.strftime("%H:%M:%S")}')

    @property
    def current_dec(self):
        str = cmd(F'GD')
        return datetime.strptime(str, "+%H*%M'%S")
    @current_dec.setter
    def current_dec(self, d):
        val = d.strftime("+%H*%M'%S")
        time = cmd(F'SD{val}')
    
    # FIXME: handle +/-
    @property
    def target_dec(self):
        str = cmd(F'Gd')
        return datetime.strptime(str, "+%H*%M'%S")
    @current_dec.setter
    def target_dec(self, d):
        val = d.strftime("+%H*%M'%S")
        time = cmd(F'Sd{val}')

    @property
    def target_ra(self):
        str = cmd(F'Gr')
        return datetime.strptime(str, "%H:%M:%S")
    @target_ra.setter
    def target_ra(self, d):
        val = d.strftime("%H:%M:%S")
        time = cmd(F'Sr{val}')

    @property
    def current_ra(self):
        str = cmd(F'GR')
        return datetime.strptime(str, "%H:%M:%S")
    @target_ra.setter
    def current_ra(self, d):
        val = d.strftime("%H:%M:%S")
        time = cmd(F'SR{val}')

    @property
    def current_date(self):
        str = cmd(F'GC')
        return datetime.strptime(str, "%m/%d/%y")
    @current_date.setter
    def current_date(self, d):
        val = d.strftime("%m/%d/%y")
        time = cmd(F'SC{val}')

    @property
    def current_time(self):
        str = cmd(F'GL')
        return datetime.strptime(str, "%H:%M:%S")
    @current_time.setter
    def current_time(self, d):
        val = d.strftime("%H:%M:%S")
        time = cmd(F'GL{val}')

mount = Mount()
focuser = Focuser()
digital_level = DigitalLevel()

def raw_loop():
    while True:
        text = input("> ")
        result = cmd(text)
        print(F"> {result}")

import curses
class Menu():
    def loop(self):
        self.screen = curses.initscr()
        screen = self.screen
        curses.cbreak(); screen.keypad(True); curses.noecho()
        screen.nodelay(1)
        screen.addstr(0, 0, f'Some menu. "q" to exit')
        try:
            while True:
                c = screen.getch()
                if c != -1:
                    screen.addstr(2, 0, f"c: {c}")
                    time.sleep(0.1)
                if c == ord('q'):
                    break
        finally:
            # shut down cleanly
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()

menu = Menu()
menu.loop()