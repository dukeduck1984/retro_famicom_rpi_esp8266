"""
This code is intended to start up and safely shut down an RPI with a single-throw switch.
The ST switch is wired to a GPIO of ESP8266 which is pulled up (high).
When switching on, the GPIO goes low, which triggers 'on_press' function - activate the SSR and turn on the LED.
When switching off, the GPIO goes back to high, which triggers 'on_release' function - it sends a pull low signal to
RPI GPIO to execute linux shut down command while monitoring the TxD pin of the RPI, as soon as the TxD goes low,
which means the RPI is shut down safely, the LED will be off.
"""


import machine
import utime

from button import Button
from config import *


power_sw = Button(POWER_SW_PIN)
rpi_ssr = machine.Pin(RPI_SSR_PIN, machine.Pin.OUT, value=0)
rpi_shutdown_cmd = machine.Pin(RPI_SHUTDOWN_PIN, machine.Pin.OUT, value=1)
rpi_is_on = machine.Pin(RPI_STATUS_CHECK_PIN, machine.Pin.IN, None).value
rpi_led = machine.Pin(RPI_POWER_LED_PIN, machine.Pin.OUT, value=0)


def rpi_start_up():
    print('Powering On')
    rpi_ssr.on()
    rpi_led.on()


def rpi_shut_down():
    rpi_shutdown_cmd.value(0)
    while True:
        if not rpi_is_on():
            utime.sleep_ms(500)
            if not rpi_is_on():
                print('Powering Off')
                rpi_led.off()
                utime.sleep_ms(10000)
                rpi_ssr.off()
                rpi_shutdown_cmd.value(1)
                break


power_sw.on_press(rpi_start_up)

power_sw.on_release(rpi_shut_down)
