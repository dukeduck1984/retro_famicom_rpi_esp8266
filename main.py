"""
This code is intended to start up and safely shut down an RPI with a single-throw switch.
The ST switch is wired to a GPIO of ESP8266 which is pulled up (high).
When switching on, the GPIO goes low, which triggers 'on_press' function - activate the SSR and turn on the LED.
When switching off, the GPIO goes back to high, which triggers 'on_release' function - it sends a pull low signal to
RPI GPIO to execute linux shut down command while monitoring the TxD pin of the RPI, as soon as the TxD goes low,
which means the RPI is shut down safely, the LED will be off.


WIRING:
WeMos D1mini    RPI     FC                          SSR                 LED
GPIO5(D1)               Power Switch Positive
GND             GND     Power Switch Negative       Input Negative      Negative
GPIO4(D2)                                           Input Positive
GPIO16(D0)      GPIO3
GPIO14(D5)      GPIO14
GPIO12(D6)                                                              Positive (with a resistor)
"""


import machine
import utime

from button import Button


POWER_SW_PIN = 5  # WeMos D1 mini (D1), input, wire to the switch of the FC
RPI_SSR_PIN = 4  # (D2), output, wire to the SSR
RPI_SHUTDOWN_PIN = 16  # (D0), output, wire to RPI GPIO3 (Pin #5)
RPI_POWER_LED_PIN = 12  # (D6), output, wire to an Led along with a resistor

# Edit your rpi /boot/config.txt file and add the following line:
# enable_uart=1
RPI_STATUS_CHECK_PIN = 14  # (D5), input, wire to RPI GPIO14 (Pin #8, UART TxD)

power_sw = Button(POWER_SW_PIN)
rpi_ssr = machine.Pin(RPI_SSR_PIN, machine.Pin.OUT, value=0)
rpi_shut_cmd = machine.Pin(RPI_SHUTDOWN_PIN, machine.Pin.OUT, value=1)
rpi_is_on = machine.Pin(RPI_STATUS_CHECK_PIN, machine.Pin.IN, machine.Pin.PULL_UP).value
rpi_led = machine.Pin(RPI_POWER_LED_PIN, machine.Pin.OUT, value=0)


def rpi_start_up():
    print('Powering On')
    rpi_ssr.on()
    rpi_led.on()


def rpi_shut_down():
    rpi_shut_cmd.value(0)
    while True:
        if not rpi_is_on():
            utime.sleep_ms(30)
            if not rpi_is_on():
                print('Powering Off')
                rpi_ssr.off()
                rpi_led.off()
                rpi_shut_cmd.value(1)
                break


power_sw.on_press(rpi_start_up)

power_sw.on_release(rpi_shut_down)
