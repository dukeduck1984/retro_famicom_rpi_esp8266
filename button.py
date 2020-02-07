# USAGE EXAMPLE
#
# # define the buttons by their gpios
# power_btn = Button(25)
# vol_up_btn = Button(26)
#
# # define functions for the buttons to execute
# def power_func():
#     if power_off:
#         do_power_on()
#     else:
#         do_power_off()
#
# def vol_up_func():
#     vol += 1
#
#
# # by holding the power button, power_func() will only run once
# power_btn.on_hold_once(power_func)
#
# # by pressing the vol_up button, volume will increase by 1
# vol_up_btn.on_press(vol_up_func)
# # by holding the vol up button, volume will be increasing continuously
# vol_up_btn.on_hold(vol_up_func)
#

import machine


class Button:
    def __init__(self, pin, pull_up=True, checks=2, check_period=5, hold_time=1500, debug=False):
        """
        :param pin: int; GPIO number
        :param checks: int; the times of deboucing
        :param check_period: int; the frequency (microseconds) of debouncing
        :param pull_up: boolean; whether the pin is pulled up or not
        :param hold_time: int; how long (microseconds) before the press action becomes holding
        """
        self.pin_pull = machine.Pin.PULL_UP if pull_up else machine.Pin.PULL_DOWN
        self.pin = machine.Pin(pin, machine.Pin.IN, self.pin_pull)
        self.pin_default_value = 1 if pull_up else 0
        self.pin_active_value = 0 if pull_up else 1
        self.pin_status = [self.pin_default_value] * (checks + 1)
        self.irq_enabled = True
        self.irq_trigger = machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING
        self.checks = checks
        self.check_period = check_period
        self.check_counter = 0
        self.hold_time = hold_time
        self.debug = debug
        self.pin_pressed_status = [self.pin_default_value] + [self.pin_active_value] * self.checks
        self.pin_held_status = [self.pin_active_value] * (self.checks + 1)
        self.pin_released_status = [self.pin_active_value] + [self.pin_default_value] * self.checks
        self.is_pressed = False
        self.is_released = False
        self.is_held = False
        self.press_func = None
        self.release_func = None
        self.hold_func = None
        self.hold_task_interval = 100
        self.timer = machine.Timer(-1)
        # self.pin.irq(handler=self._activated, trigger=pin_trigger)
        self.pin.irq(handler=self._activated, trigger=self.irq_trigger)

    def _activated(self, pin):
        """
        Callback function for interruption
        """
        if self.irq_enabled:
            self.irq_enabled = False
            self.timer.init(mode=machine.Timer.PERIODIC,
                            period=self.check_period,
                            callback=lambda t: self._debouncing())

    def _debouncing(self):
        pin_value = self.pin.value()
        if self.check_counter < self.checks:
            self.pin_status.pop(0)
            self.pin_status.append(pin_value)
            self.check_counter += 1
        else:
            self.timer.deinit()
            self.check_counter = 0
            self.irq_enabled = True
            # [1, 0, 0]
            if self.pin_status == self.pin_pressed_status:
                self.is_pressed = True
                # Execute pressing task
                self._do_pressing_task()
                self.timer.init(mode=machine.Timer.ONE_SHOT,
                                period=self.hold_time,
                                callback=lambda t: self._check_holding())
            # [0, 0, 0]
            if self.pin_status == self.pin_held_status:
                self.is_pressed = True
                self._do_holding_task()

            # [0, 1, 1]
            if self.pin_status == self.pin_released_status and self.is_pressed:
                self.is_released = True
                # Execute releasing task
                self._do_releasing_task()
                self.timer.deinit()
                self.timer.init(mode=machine.Timer.ONE_SHOT,
                                period=10,
                                callback=lambda t: self._reset())

    def _reset(self):
        self.pin_status = [self.pin_default_value] * (self.checks + 1)
        self.is_pressed = False
        self.is_released = False
        self.is_held = False

    def _check_holding(self):
        if self.pin.value() == self.pin_active_value and self.is_pressed:
            self.is_held = True
            # Execute holding task
            self._do_holding_task()

    def _do_pressing_task(self):
        if self.debug:
            print('The button was pressed.')
        if self.press_func:
            try:
                self.press_func()
            except Exception as e:
                print(e)

    def _do_releasing_task(self):
        if self.debug:
            print('The button was released.')
        if self.release_func:
            try:
                self.release_func()
            except Exception as e:
                print(e)

    def _do_holding_task(self):
        if self.debug:
            print('The button is being held.')
        if self.hold_func:
            this = self

            def cb(t):
                if this.is_held:
                    try:
                        this.hold_func()
                    except Exception as e:
                        print(e)
            self.timer.deinit()
            mode = machine.Timer.PERIODIC if self.hold_task_interval else machine.Timer.ONE_SHOT
            period = self.hold_task_interval if self.hold_task_interval else 100
            self.timer.init(mode=mode,
                            period=period,
                            callback=cb)

    def on_press(self, func=None):
        self.press_func = func

    def on_release(self, func=None):
        self.release_func = func

    def on_hold(self, func=None, interval=100):
        self.hold_func = func
        self.hold_task_interval = interval

    def on_hold_once(self, func=None):
        self.on_hold(func, interval=0)

    def on_hold_repeat(self, func=None):
        self.on_hold(func)

    def clear_press(self):
        self.press_func = None

    def clear_release(self):
        self.release_func = None

    def clear_hold(self):
        self.hold_func = None

    def clear_all(self):
        self.clear_press()
        self.clear_hold()
        self.clear_release()
