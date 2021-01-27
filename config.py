from micropython import const

POWER_SW_PIN = const(5)  # WeMos D1 mini (D1), input, wire to the switch of the FC
RPI_SSR_PIN = const(4)  # (D2), output, wire to the SSR
RPI_SHUTDOWN_PIN = const(14)  # (D5), output, wire to RPI GPIO3 (Pin #5)
RPI_POWER_LED_PIN = const(12)  # (D6), output, wire to an Led along with a resistor

# Edit your rpi /boot/config.txt file and add the following line:
# enable_uart=1
RPI_STATUS_CHECK_PIN = const(15)  # (D8), input, wire to RPI GPIO4 (Pin #7)