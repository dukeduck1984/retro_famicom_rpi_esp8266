import RPi.GPIO as GPIO
import time
import os
import thread
import datetime
import socket
import sys
import argparse
import subprocess
from datetime import datetime
from configgen import recalboxFiles
# this last one retrieves emulators bin names


parser = argparse.ArgumentParser(description='power manager')
parser.add_argument("-m", help="mode onoff or push", type=str, required=True)
args = parser.parse_args()
mode = args.m

IPADDR = "127.0.0.1"
PORTNUM = 55355
# IP and port for retroarch network commands

POWERPLUS = 3
RESETPLUS = 2
POWEREN = 4
LED = 14

GPIO.setwarnings(False)         # no warnings
GPIO.setmode(GPIO.BCM)          # set up BCM GPIO numbering

GPIO.setup(RESETPLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO on pin 3 is the GPIO 2 in BCM mode
# to Reset+

GPIO.setup(POWERPLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO on pin 5 is the GPIO 3 in BCM mode
# to Power+

GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, True)
# GPIO on pin 8 is the GPIO 14 in BCM mode
# to LED+


# Define a threaded callback function for ONOFF mode
def onoff_mode(channel):
    if channel == POWERPLUS:
        speed = 0.15
        shutdownstring = "shutdown -h now"
        offreset(speed, shutdownstring)
        print('shutdown')

    elif channel == RESETPLUS:
        timer = 0
        flag = True
        while flag:
            if GPIO.input(channel) is False:
                timer += 1
                print('Button pressed')
            elif GPIO.input(channel) is True:
                print('Button released')
                print(timer)

                # timer adds 1 each 0.1 seconds if timer = 10, button is pressed for 1s
                if (timer > 10):
                    nwcommand = "QUIT"
                    retroarch(nwcommand)
                    print('game exit')
                    killthatshit()
                elif (timer > 1):
                    proces = subprocess.Popen(
                        ['/bin/sh', '-c', 'ps -ef | grep [e]mulatorlauncher'],
                        stdout=subprocess.PIPE
                    )  # Searc$
                    result = proces.stdout.read()
                    if result:
                        nwcommand = "RESET"
                        retroarch(nwcommand)
                        print('game reset')
                    else:
                        speed = 0.05
                        shutdownstring = "shutdown -r now"
                        offreset(speed, shutdownstring)
                        print('reboot')

                timer = 0
                flag = False
                time.sleep(0.1)


# Define a threaded callback function for PUSH mode
def push_mode(channel):
    if channel == POWERPLUS:
        speed = 0.15
        shutdownstring = "shutdown -h now"
        nwcommand = "QUIT"

    elif channel == RESETPLUS:
        speed = 0.05
        shutdownstring = "shutdown -r now"
        # Changed from 'RESET' to 'QUIT' by Kaiyuan
        # nwcommand="RESET"
        nwcommand = "QUIT"

        timer = 0
        flag = True
        while flag:
            if GPIO.input(channel) is False:
                timer += 1
                print('Button pressed')
            elif GPIO.input(channel) is True:

                print('Button released')
                print(timer)

                # timer adds 1 each 0.1 seconds if timer = 10, button is pressed for 1s
                if (timer > 10):
                    offreset(speed, shutdownstring)
                    print('shutdown')
                elif (timer > 1):
                    retroarch(nwcommand)
                    print('retroarch')
                    if channel == POWERPLUS:
                        killthatshit()

                timer = 0
                flag = False
            time.sleep(0.1)


# trying to kill all listed emus
def killthatshit():
    for name in recalboxFiles.recalboxBins:
        bin = recalboxFiles.recalboxBins[name]
        print(bin)
        proc = os.path.basename(bin)
        print(proc)
        os.system("killall -9 "+proc)


# clean stop of ES then shutdown -h or -r
def offreset(speed, shutdownstring):
    thread.start_new_thread(blink, (speed, ))
    flag = True
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    os.system("/etc/init.d/S31emulationstation stop")
    while flag:
        flag = False
        for pid in pids:
            try:
                print(pid)
                commandpath = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
                if "emulationstation" in commandpath:
                    flag = True
            except IOError:
                continue
    os.system(shutdownstring)


# threaded blinking function for LED
def blink(speed):
    while True:
        GPIO.output(LED, False)
        time.sleep(speed)
        GPIO.output(LED, True)
        time.sleep(speed)


# sending network command to retroarch (only exit and reset atm)
def retroarch(nwcommand):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print('Failed to create socket')
        sys.exit()
    s.sendto(nwcommand, (IPADDR, PORTNUM))


if mode == "onoff":
    # Allow Nespi+ to detect the end of the shutdown for proper power-off
    GPIO.setup(POWEREN, GPIO.OUT)
    GPIO.output(POWEREN, True)
    GPIO.add_event_detect(POWERPLUS, GPIO.FALLING, callback=onoff_mode, bouncetime=2)
    GPIO.add_event_detect(RESETPLUS, GPIO.BOTH, callback=onoff_mode, bouncetime=2)
elif mode == "push":
    GPIO.add_event_detect(POWERPLUS, GPIO.BOTH, callback=push_mode, bouncetime=2)
    GPIO.add_event_detect(RESETPLUS, GPIO.BOTH, callback=push_mode, bouncetime=2)

while True:
    time.sleep(0.2)
