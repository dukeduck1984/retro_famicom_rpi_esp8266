

### The Purpose of this Project
I'd like to retrofit an Famicom (aka. NES) game console with a spared RPI2 and I want to make it
feel as authentic as possible, for example: the power on and off is handled by the original power switch,
and I don't need to worry about RPI being properly shutdown; also I can reset the game or quit the game to 
choose another one by pressing the original reset button, rather than using the combined key press on the gamepad
which is not the way how a real Famicom works.

So what I do is use a spared WeMos D1mini (ESP8266) to handle the original power switch and SSR etc, and the ESP8266
will send signals to GPIOs on RPI to either reset/quit games or shutdown the Linux system.

### Prerequisites
##### Edit ```recalbox.conf```
* You can edit recalbox.conf through the browser by enter the IP address of the RPI,
 this will open the Recalbox manager.
* In recalbox.conf, add/uncomment the following line:
```system.power.switch=PIN356ONOFFRESET```
* You can find the corresponding Python script under folder:
```/recalbox/scripts/```
* Should you wish to change the Python script, enter ```mount -o remount,rw /``` first to make the partition writeable.
* By adding/uncommenting the above line, you can:
    1. Activate Linux shut down command by turn off a single throw switch, 
    which sends a low signal to RPI GPIO3.
    2. Reset a game (meaning return to start screen of the game) which you are playing,
    by short press (less than 1 sec) then release a push button, by which a low signal is sent to RPI GPIO2.
    3. Quit the game (meaning return to the emulator console) so that you can select another game,
    by long press (longer than 1 sec) then release a push button, by which a low signal is sent to RPI GPIO2.

##### Edit ```config.txt```
* You need to connect to the RPI by SSH.
* Enter ```mount -o remount,rw /boot``` before editing, otherwise the partition is read-only, and you won't be
able to save the change.
* You need to add/uncomment the following line in config.txt:
```enable_uart=1```
* By doing so, the RPI GPIO14 (UART0_TXD) is at high level when the RPI is on, and it will go low when the RPI is
properly shut down, which helps determine the power status of the RPI.

### Wiring
* Overview

| WeMos D1mini | RPI2 | Famicom | SSR | LED | 5V DC PS |
| :----------------: |:------:| :-----------------------: | :--------: | :--------------------:| :-----: |
| GPIO5 (D1)         |        |     Power SW +            |            |                       |         |
| GND                |   GND  | Power SW - & Reset BTN -  |  Input -   |   Cathode             |         |
| GPIO4 (D2)         |        |                           |  Input +   |                       |         |
| GPIO16 (D0)        |  GPIO3 |                           |            |                       |         |
| GPIO14 (D5)        | GPIO14 |                           |            |                       |         |
| GPIO12 (D6)        |        |                           |            | Anode (/w a resistor) |         |
|                    |  GPIO2 |      Reset BTN +          |            |                       |         |
|  USB V+            |        |                           |  Load +    |                       |   5V+   |     
|  USB V-            | USB V- |                           |            |                       |   GND   |
|                    | USB V+ |                           |  Load -    |                       |         |

* Fritzing Diagram

![](./pic/wiring.png)

### Refs
* [Make a partition writable](https://github.com/recalbox/recalbox-os/wiki/Make-a-partition-writable-%28EN%29)
* [Edit the config.txt file](https://github.com/recalbox/recalbox-os/wiki/Edit-the-config.txt-file-%28EN%29)
* [recalbox.conf](https://github.com/recalbox/recalbox-os/wiki/recalbox.conf-%28EN%29)
* [Add a start stop button to your recalbox](https://github.com/recalbox/recalbox-os/wiki/Add-a-start-stop-button-to-your-recalbox-%28EN%29)
* [Emulator interactions via GPIO mapping](https://github.com/recalbox/recalbox-os/wiki/Emulator-interactions-via-GPIO-mapping-%28EN%29)
* [Rotary Encoder via GPIO](https://github.com/recalbox/recalbox-os/wiki/Rotary-Encoder-via-GPIO-%28EN%29)
* [RPI2 more power to usb ports](https://github.com/recalbox/recalbox-os/wiki/RPI2-more-power-to-usb-ports-%28EN%29)
* For more info, pls refer to Recalbox Wiki [Mini How To](https://github.com/recalbox/recalbox-os/wiki/Mini-How-To-%28EN%29)

