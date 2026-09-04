# Super4C

## Product SKU

-   SKU: DP-0040

## Introduction

Super4C is a cluster-based hardware built on the Raspberry Pi CM5. This hardware supports four channels of CM5 and extends almost all interfaces of the CM5, providing users with powerful device connectivity. Additionally, the hardware integrates an ESP32 processing module, offering remote management capabilities for the entire cluster device. For convenience, this document will refer to this cluster board hardware as the "motherboard" in subsequent sections.

Compatible with Raspberry Pi CM5 Only  

![super4c01](../imgs/super4c/main_01.png)

## Features

-   Standard mini ITX form factor
-   Supports all Raspberry Pi CM5 modules
-   External DC 19V/4.73A power input with redundant interface support and reverse polarity protection
-   Four-channel independent DC/DC conversion to provide power for following two parts:
-   Independent power reset button (simultaneously resets CM5, NVMe, 2.5Gbps, 1Gbps, SD card, CAM0/1, etc.)
-   Hardware power - on delay (approximately 0.5 seconds each) to avoid inrush current from simultaneous power on
-   4-pin fan connector (directly connected to the DC 19V power port)
-   Supports up to four CM5 modules per channel, each with:
-   1x micro HDMI interface
-   1x USB 3.0 interface
-   1x USB 2.0 interface (Type-C connector, no VBUS output)
-   1x 1Gbps Ethernet interface
-   1x 2.5Gbps Ethernet interface (via USB 3.0 expansion)
-   1x microSD card interface
-   1x M.2 M-key PCIe interface
-   1x 4-pin JST-SH PWM fan interface
-   1x RTC battery interface
-   2x MIPI DSI/CSI - 2 interfaces
-   Jumper interface (to disable eMMC, EEPROM, etc.)
-   Integrated ESP32-WROOM-32E-N4 module
-   Supports 2.4GHz Wi - Fi + Bluetooth with integrated antenna
-   Expanded W5500 100Mbps wired network
-   4-pin UART download interface
-   4-pin I2C expansion interface (for expanding OLED screens, etc.)
-   Two integrated INA3221 chips for measuring voltage and current of six channels on the board
-   ESP32 pins can individually control the power switch for each channel and the PMIC_EN signal switch for CM5
-   BOOT/EN button

### Main Power Input

The main power input uses a barrel power connector (inner diameter 2mm, outer diameter 6.6mm) with a voltage range of DC 12V-20V. Two sockets(DC1, DC2) support redundant power input. When two power supplies with different voltages are inserted simultaneously, the hardware will automatically select the power supply with the higher voltage.

![super4c02](../imgs/super4c/main_02.png)

### Main Power Protection

The main power supply passes through protection circuits, voltage and current sampling circuits, reverse polarity protection, and fuse circuits before powering the internal components and outputting to the J15 connector for external main fan power supply.

> Note: When connecting a fan, ensure that the fan's rated voltage matches the main power supply voltage.

### Internal 5V DC/DC and Buttons

The main power supply passes through four-channel DC/DC circuits to convert to 5V power, supplying each CM5 and its peripherals. Each DC/DC channel has an independent power reset button (PWR_OFF1/2/3/4). Pressing the button (SW3/4/5/6) will reset the power of each CM5 and its peripheral channel.

![super4c03](../imgs/super4c/main_03.png)

### Voltage and Current Monitoring

Both the main power sockets and the four internal 5V power rails are equipped with voltage and current sensing capabilities. Through the I2C interface of the ESP32, two INA3221 chips (covering a total of six channels) are controlled to monitor voltage and current.

![super4c04](../imgs/super4c/main_04.png)

### CM5 Modules

A total of four CM5 channels are supported, with each channel featuring identical extended interfaces, which are labeled with the numbers 1, 2, 3, and 4 on the hardware silk screen.

### CM5 Connector

The standard CM5 connector is used, with a total height of 3mm below the board after installation.

### micro HDMI 2.0 Interface

The standard micro HDMI interface is directly connected to the `HDMI0` interface of the CM5 module. The 5V power on the interface is provided by the motherboard through a current - limiting switch.

### USB3.0 Interface

The CM5 module features 2 x `USB 3.0` interfaces. On this motherboard, the USB 3.0 interface is connected to `Port 0`. The interface is equipped with a current - limiting switch, which provides a maximum power supply capability of 0.9A to external devices.

![super4c05](../imgs/super4c/main_05.png)

### USB2.0 Interface

The CM5 module has one USB 2.0 interface, which is connected to the Type-C connector on this motherboard. This interface only connects the D+/D- signals and does not provide external power. It can be used in conjunction with the `nRPIBOOT` signals to program the CM5.

![super4c06](../imgs/super4c/main_06.png)

### 1Gbps Ethernet Interface

Connected to the CM5's native Gigabit Ethernet interface, using a standard `RJ45` connector and `does not support Power over Ethernet (PoE)`.

![super4c07](../imgs/super4c/main_07.png)

### 2.5Gbps Ethernet Interface

Extended from the CM5's USB3.0 Port 1, this interface also supports Gigabit and Fast Ethernet (10/100/1000Mbps) connections.

![super4c08](../imgs/super4c/main_08.png)

### microSD Card Interface

Press-fit interface, only supports `CM5 Lite` version.

### M.2 M-Key Interface

-   Supports various M.2 M-key cards with only PCIe signals on the interface.
-   `ONLY` supports the 2280 form factor.

#### Tested SSDs List

-   The following SSDs have been tested and demostrated good performance when used with M.2 M-key Interface, supporting only PCIe signals:

<!-- -->

     
    1. WD_BLACK SN7100 PCIe Gen 4.0 NVMe SSD 1TB M.2 2280 M-Key 
    2. WD_BLACK SN8100 PCIe Gen 5.0 NVMe SSD  1TB M.2 2280 M-Key 
    3. WD_BLACK SN770 PCIe Gen 4.0 NVMe SSD  2TB M.2 2280 M-Key 
    4. Fanxiang Jing PCIe Gen 4.0 NVMe SSD 512GB M.2 2280 M-Key 
    5. Lexar NQ790 PCIe Gen 4.0x4 NVMe SSD 2TB M.2 2280 M-Key
    6. SAMSUNG 990 PRO PCIe 4.0 NVMe SSD 2TB M.2 2280 M-Key 

> NOTE: Due to the limitations of the Raspberry Pi's PCIex1 interface, the performance of high-speed SSDs may be downgraded.

### Fan Interface

Same interface dimensions and signal definitions as the Raspberry Pi Official CM5 IO Board. (compatible with Active cooler's JST cable. but not compatible with the mounting holes)

![super4c09](../imgs/super4c/main_09.png)

### RTC Battery Interface

Same interface dimensions and signal definitions as the official CM5 IO board.

![super4c10](../imgs/super4c/main_10.png)

### MIPI Interface

Same interface dimensions and signal definitions as the official CM5 IO board, featuring a `22-pin`, `0.5-pitch FPC` (Flexible Printed Circuit) connector.

![super4c11](../imgs/super4c/main_11.png)

### Jumper Headers

The IO voltage is by default configured to +3.3V, with pin definitions matching the silk screen on the board. This pin header also brings out `GPIO8/GPIO9/GPIO10/GPIO11` for expansion use. Additionally, the `PMIC_ENABLE` signal can be controlled via jumpers or ESP32(with different ESP32 IO Pin allocations for different CM5 Channels). The figure below shows the jumper pins and silk - screen markings corresponding to the first - channel CM5.

![super4c12](../imgs/super4c/main_12.png)

### ESP32

The model of the ESP32 integrated on the motherboard is `ESP32-WROOM-32E-N4`. The motherboard comes with a pre-installed basic firmware that can perform simple power control, monitor voltage and current, and display the information in real - time on an OLED screen (SSD1306).

#### ESP32 Pin Allocation

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Pin</strong></th>
<th><strong>ESP32-WROOM-32E</strong></th>
<th><strong>Super4C Net Name</strong></th>
<th><strong>Function / Notes</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>1</td>
<td>GND</td>
<td>GND</td>
<td><strong>Ground</strong></td>
</tr>
<tr class="even">
<td>2</td>
<td>3V3</td>
<td>3V3</td>
<td><strong>3.3 V Power Supply</strong></td>
</tr>
<tr class="odd">
<td>3</td>
<td>EN</td>
<td>EN</td>
<td><strong>HIGH=ON</strong> (ESP32 enabled)<br />
<strong>LOW=OFF</strong> (ESP32 shut-down)<br />
Also wired to <strong>SW2</strong> (pressed = LOW)</td>
</tr>
<tr class="even">
<td>4</td>
<td>SENSOR_VP</td>
<td>NC</td>
<td><em>Unconnected</em></td>
</tr>
<tr class="odd">
<td>5</td>
<td>SENSOR_VN</td>
<td>NC</td>
<td><em>Unconnected</em></td>
</tr>
<tr class="even">
<td>6</td>
<td>IO34</td>
<td>NC</td>
<td><em>Unconnected</em></td>
</tr>
<tr class="odd">
<td>7</td>
<td>IO35</td>
<td>NC</td>
<td><em>Unconnected</em></td>
</tr>
<tr class="even">
<td>8</td>
<td>IO32</td>
<td>XTAL_32K_P</td>
<td>32.768 kHz crystal <strong>input</strong></td>
</tr>
<tr class="odd">
<td>9</td>
<td>IO33</td>
<td>XTAL_32K_N</td>
<td>32.768 kHz crystal <strong>output</strong></td>
</tr>
<tr class="even">
<td>10</td>
<td>IO25</td>
<td>CM5_4_PMIC_ENABLE</td>
<td><strong>Channel-4 Enable</strong><br />
HIGH=ON (default) ‑ LOW=OFF</td>
</tr>
<tr class="odd">
<td>11</td>
<td>IO26</td>
<td>CM5_3_PMIC_ENABLE</td>
<td><strong>Channel-3 Enable</strong><br />
HIGH=ON (default) ‑ LOW=OFF</td>
</tr>
<tr class="even">
<td>12</td>
<td>IO27</td>
<td>CM5_2_PMIC_ENABLE</td>
<td><strong>Channel-2 Enable</strong><br />
HIGH=ON (default) ‑ LOW=OFF</td>
</tr>
<tr class="odd">
<td>13</td>
<td>IO14</td>
<td>CM5_1_PMIC_ENABLE</td>
<td><strong>Channel-1 Enable</strong><br />
HIGH=ON (default) ‑ LOW=OFF</td>
</tr>
<tr class="even">
<td>14</td>
<td>IO12</td>
<td>NC</td>
<td><em>Unconnected</em></td>
</tr>
<tr class="odd">
<td>15</td>
<td>GND</td>
<td>GND</td>
<td><strong>Ground</strong></td>
</tr>
<tr class="even">
<td>16</td>
<td>IO13</td>
<td>BMC_I2C_SDA</td>
<td>I²C <strong>SDA</strong><br />
→ two on-board <strong>INA3221</strong> + <strong>J12</strong> &amp; <strong>J6</strong></td>
</tr>
<tr class="odd">
<td>17-22</td>
<td>—</td>
<td>NC</td>
<td><em>Unconnected</em></td>
</tr>
<tr class="even">
<td>23</td>
<td>IO15</td>
<td>BMC_I2C_SCL</td>
<td>I²C <strong>SCL</strong><br />
→ two on-board <strong>INA3221</strong> + <strong>J12</strong> &amp; <strong>J6</strong></td>
</tr>
<tr class="odd">
<td>24</td>
<td>IO2</td>
<td>BMC_PSU1</td>
<td><strong>PSU-1 ENABLE</strong><br />
<code>HIGH=OFF</code> ‑ <code>LOW=ON</code> (default)</td>
</tr>
<tr class="even">
<td>25</td>
<td>IO0</td>
<td>BOOT</td>
<td>Boot-strap (strapping) pin</td>
</tr>
<tr class="odd">
<td>26</td>
<td>IO4</td>
<td>BMC_PSU2</td>
<td><strong>PSU-2 ENABLE</strong><br />
<code>HIGH=OFF</code> ‑ <code>LOW=ON</code> (default)</td>
</tr>
<tr class="even">
<td>27</td>
<td>IO16</td>
<td>BMC_PSU3</td>
<td><strong>PSU-3 ENABLE</strong><br />
<code>HIGH=OFF</code> ‑ <code>LOW=ON</code> (default)</td>
</tr>
<tr class="odd">
<td>28</td>
<td>IO17</td>
<td>BMC_PSU4</td>
<td><strong>PSU-4 ENABLE</strong><br />
<code>HIGH=OFF</code> ‑ <code>LOW=ON</code> (default)</td>
</tr>
<tr class="even">
<td>29</td>
<td>IO5</td>
<td><code>#SCS_W5500</code></td>
<td>W5500 <strong>SPI-CS</strong> (pin 32)</td>
</tr>
<tr class="odd">
<td>30</td>
<td>IO18</td>
<td>SCLK_W5500</td>
<td>W5500 <strong>SPI-CLK</strong> (pin 33)</td>
</tr>
<tr class="even">
<td>31</td>
<td>IO19</td>
<td>MISO_W5500</td>
<td>W5500 <strong>MISO</strong> (pin 34)</td>
</tr>
<tr class="odd">
<td>32</td>
<td>—</td>
<td>NC</td>
<td><em>Unconnected</em></td>
</tr>
<tr class="even">
<td>33</td>
<td>IO21</td>
<td><code>#INT_W5500</code></td>
<td>W5500 <strong>INT</strong> (pin 36)</td>
</tr>
<tr class="odd">
<td>34</td>
<td>RXD0</td>
<td>BMC_RXD0</td>
<td>UART0 RX → <strong>J47</strong></td>
</tr>
<tr class="even">
<td>35</td>
<td>TXD0</td>
<td>BMC_TXD0</td>
<td>UART0 TX → <strong>J47</strong></td>
</tr>
<tr class="odd">
<td>36</td>
<td>IO22</td>
<td><code>#RST_W5500</code></td>
<td>W5500 <strong>RST</strong> (pin 37)</td>
</tr>
<tr class="even">
<td>37</td>
<td>IO23</td>
<td>MOSI_W5500</td>
<td>W5500 <strong>MOSI</strong> (pin 35)</td>
</tr>
<tr class="odd">
<td>38</td>
<td>GND</td>
<td>GND</td>
<td><strong>Ground</strong></td>
</tr>
</tbody>
</table>

#### ESP32 Buttons

-   **BOOT (SW1):**

-   When the BOOT button is held down while powering on the motherboard (or while powered on, hold both BOOT and EN buttons, release the EN button first, and then release the BOOT button), the ESP32 will enter programming mode. The ESP32 can then be programmed via the UART interface (J47).

-   In the default firmware, after the ESP32 starts up, the BOOT pin is used as an input IO (GPIO0). When the BOOT button is pressed for more than 1 second and then released, the ESP32 will sequentially disable the PMIC_ENABLE signals for the four CM5 modules and the ENABLE signals for the four DC/DC (5V) channels, with an interval of approximately 0.5 seconds.

-   **EN (SW2):**

-   In the default firmware, pressing the EN button will reset all CM5_PMIC_ENABLE and DC/DC (5V) ENABLE signals.

#### ESP32 I2C Address

The I2C signals of the ESP32 are connected to both the J12 and J6 headers, as well as the two onboard INA3221 chips. The headers can be used to expand external I2C devices.

<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Item</strong></th>
<th><strong>Channels / Pins / Address</strong></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>J12 Connector</strong></td>
<td>4-pin 2.54 mm header (GND, 3V3, SDA, SCL)</td>
<td>Header for plugging in an <strong>OLED module</strong> (I²C interface)</td>
</tr>
<tr class="even">
<td><strong>J16 Connector</strong></td>
<td>4-pin 2.54 mm header (GND, 3V3, SDA, SCL)</td>
<td>Header for <strong>additional I²C devices</strong></td>
</tr>
<tr class="odd">
<td><strong>INA3221 #1</strong></td>
<td>3-channel • 20 mΩ shunt • I²C address <code>0x40</code></td>
<td>IN1 → <strong>DC1</strong><br />
IN2 → <strong>DC2</strong><br />
IN3 → <strong>DC/DC 5 V #1</strong></td>
</tr>
<tr class="even">
<td><strong>INA3221 #2</strong></td>
<td>3-channel • 20 mΩ shunt • I²C address <code>0x41</code></td>
<td>IN1 → <strong>DC/DC 5 V #2</strong><br />
IN2 → <strong>DC/DC 5 V #3</strong><br />
IN3 → <strong>DC/DC 5 V #4</strong></td>
</tr>
</tbody>
</table>

The pinout diagram for J12/J6 connectors is as follows:

![super4c13](../imgs/super4c/main_13.png)

#### ESP32 Firmware

The ESP32 comes with default firmware that can:

-   Display the current WiFi mode and corresponding IP information.
-   Control the power of the four DC/DC channels and the PMIC_ENABLE signals of the CM5.
-   Drive OLED display modules (SSD1306).
-   Sample the current of six channels (two DC input ports and four internal 5V power supplies).
-   Display the sampled current information on the OLED screen.
-   Detect the network connectivity of W5500 (in firmware version \_1.1.2: W5500 has not been developed for other functions):
-   If connected, the OLED screen displays: \| W55
-   If disconnected, the OLED screen displays: \| OFF

### Web Controller Usage Instructions

By flashing the accompanying ESP32 firmware (with web controller functionality) onto the motherboard, remote monitoring of the motherboard can be achieved via a web interface.

#### Web Controller Connection Modes

-   AP Mode: Before the ESP32's WiFi connects to a specific network, the motherboard will default to AP mode.

In AP mode, the OLED screen will display "AP mode" with an SSID of `Super4C` and a default password of `12345678` (an SSD1306 OLED module must be installed first, additional purchase required).

![apmode](../imgs/super4c/apmode.jpg)

In AP mode, you can connect a computer or mobile device to the following network:

-   SSID: Super4C
-   Password: 12345678

After successfully connecting, enter `192.168.4.1` in a web browser to access the Web Controller page.

-   Station Mode: After accessing the Web Controller via AP mode, click the `WiFi Setup` button on the page to enter the configuration page.
-   Enter the desired WiFi network (e.g., your home WiFi) in the WiFi SSID field and the password in the WiFi password field.
-   Click `Save & Reboot` to save the configuration and restart the device (this will take about 10 seconds).
-   After rebooting, the OLED screen will display the obtained IP address.

![stationmode](../imgs/super4c/stationmode.jpg)

Within the same local network, use a computer or mobile device to open a web browser and enter the IP address displayed on the OLED screen (e.g., "192.168.1.49") to access the Web Controller page.

-   Reset Connection Mode: In either AP or Station mode, `hold` the `BOOT button` on the motherboard for more than 5 seconds to reset the device to AP mode. This allows users to reconnect and reconfigure the WiFi network.

![reset_connection_mode](../imgs/super4c/reset_connection_mode.png)

#### Web Controller Main Page Instructions

-   Main Display Content and Operation Buttons

-   Displays the current mode and IP address.

-   Displays signal strength.

-   Displays server uptime.

-   Displays the current of six current monitoring channels on the motherboard.

-   Buttons to independently turn on/off the four onboard main power supplies.

-   Buttons to independently turn on/off the PMIC_ENABLE signals of the four CM5 channels.

-   Buttons to turn all four power supplies and CM5 channels on/off simultaneously.

-   Button to toggle all switches.

-   WiFi settings button.

![webpage1](../imgs/super4c/webpage1.png)

#### Web Controller Page Access and WiFi Configuration

-   Using a computer as an example: The Super4C's WiFi defaults to `AP mode`. First, connect your computer's WiFi to the network named `Super4C` with the default password `12345678`. Then, enter the IP address `192.168.4.1` in a web browser and press `Enter`.

![webpage2](../imgs/super4c/webpage2.png)

Click the gray `WiFi Setup` button to enter the WiFi configuration page. Enter the desired wireless network name in the `WiFi SSID` field and the password in the `WiFi password` field. Click the green `Save & Reboot` button to save the configuration to the Super4C motherboard.

![webpage3](../imgs/super4c/webpage3.png)

The motherboard will automatically reboot. Wait for approximately 10 seconds.

![webpage4](../imgs/super4c/webpage4.png)

After rebooting, connect your computer to the same local network as the Super4C. Then, enter the IP address displayed on the OLED screen (e.g., "192.168.1.49") in a web browser and press "Enter". From this point, users can remotely control the power of the Super4C, monitor current, and perform other operations within the local network.

![webpage5](../imgs/super4c/webpage5.png)

#### Web Controller Power Switch Button Operations

-   The page has eight independent power switch buttons, including `PSU #1~4` and `CM5 #1~4`.
-   The PSUs are the 5V power units on the board, with a total of four.
-   Each PSU powers the CM5, NVME, SD, USB, 2.5G network, and other circuits in each channel. Therefore, turning off a PSU will cut power to all the aforementioned circuits in that channel.
-   The `CM5 #1~4` buttons control the `PMIC_ENABLE` signals of each CM5 channel. Turning off a CM5 will only cut power to that channel's CM5, while other circuits such as NVME, SD, USB, and 2.5G network will remain powered.
-   To operate, click the `Switch OFF` or `Switch ON` buttons to perform the power actions.

> When powered on, the corresponding channel status displays "ON" with a colored status light. When powered off, the corresponding channel status displays "OFF" with a gray status light.
>
> Note: DC1/DC2 are external input power channels and cannot be controlled via switches. Do not confuse them.

![webpage6](../imgs/super4c/webpage6.jpg)

-   The `Switch All OFF` button will turn off all eight switches simultaneously. Use with caution.
-   The `Switch All ON` button will turn on all eight switches simultaneously.Use with caution.
-   The `Toggle All` button will toggle all switches.Use with caution.

![webpage7](../imgs/super4c/webpage7.png)

### OLED Screen Display

After connecting an SSD1306 screen:

-   Displays the current WiFi mode and IP address.
-   Displays the current of the six current monitoring channels on the motherboard, in units of Amps (A).

![webpage8](../imgs/super4c/webpage8.jpg) ![webpage9](../imgs/super4c/webpage9.png)

If the W5500 function is not enabled, but an Ethernet cable is connected, the screen will display "W55" when connected and "OFF" when disconnected.

------------------------------------------------------------------------

### Open Source

Some pages of the schematics and the ESP32 default firmware source code can be open - sourced to facilitate secondary development of the board by community enthusiasts. It will be open source once the firmware has been fully test.

### Diagram Block

![Diagram Block](../imgs/super4c/diagramblock.png)

### Flash an image to a Compute Module

To flash the same image to multiple Compute Modules, use the Raspberry Pi Secure Boot Provisioner. To customise an OS image to flash onto those devices, use pi-gen.

The Compute Module has an on-board eMMC device connected to the primary SD card interface. This guide explains how to flash (write) an operating system image to the eMMC storage of a single Compute Module. Lite variants of Compute Modules do not have on-board eMMC. Instead, follow the procedure to flash a storage device for other Raspberry Pi devices at Install an operating system.

#### Prerequisites

To flash the Compute Module eMMC, you need the following: \* Another computer, referred to in this guide as the host device. You can use Linux (we recommend Raspberry Pi OS or Ubuntu), Windows 11, or macOS. \* Super4C motherboard. \* A USB-C cable for Compute Module models flashing image.

#### Set up the IO Board

-   1.Connect the Compute Module to the Super4C board. When connected, the Compute Module should lie flat.
-   2.Fit `nRPI_BOOT` to `GND` Pin (disable eMMC Boot) on the board with jumper.

![super4c14](../imgs/super4c/main_14.png)

-   Connect a cable from USB-C slave port J11 on the board to the host device.

![super4c15](../imgs/super4c/main_15.png)

#### Set up the host device

Next, let’s set up software on the host device. For a host device, we recommend a Raspberry Pi 4 or newer running 64-bit Raspberry Pi OS.

##### For Linux:

To set up software on a Linux host device:

-   1.Run the following command to install rpiboot (or, alternatively, build rpiboot from source):

    sudo apt install rpiboot

-   2.Connect the IO Board to power.
-   3.Then, run rpiboot:

        sudo rpiboot

-   4.After a few seconds, the Compute Module should appear as a mass storage device. Check the /dev/ directory, likely /dev/sda or /dev/sdb, for the device. Alternatively, run lsblk and search for a device with a storage capacity that matches the capacity of your Compute Module.

##### For macOS:

To set up software on a macOS host device:

-   1.First, build rpiboot from source.
-   2.Connect the IO Board to power.
-   3.Then, run the rpiboot executable with the following command:

    rpiboot -d mass-storage-gadget64

\* 4.When the command finishes running, you should see a message stating "The disk you inserted was not readable by this computer." Click Ignore. Your Compute Module should now appear as a mass storage device

##### For Windows:

To set up software on a Windows 11 host device:

-   1.Download the Windows installer or build rpiboot from source. Windows installer Download URL: https://github.com/raspberrypi/usbboot/raw/master/win32/rpiboot_setup.exe Build source : https://github.com/raspberrypi/usbboot
-   2.Double-click on the installer to run it. This installs the drivers and boot tool. Do not close any driver installation windows which appear during the installation process.
-   3.Reboot
-   4.Connect the IO Board to power. Windows should discover the hardware and configure the required drivers.
-   5.On CM4 and later devices, select Raspberry Pi - Mass Storage Gadget - 64-bit from the start menu. After a few seconds, the Compute Module eMMC or NVMe will appear as USB mass storage devices. This also provides a debug console as a serial port gadget.
-   6.On CM3 and older devices, select rpiboot. Double-click on RPiBoot.exe to run it. After a few seconds, the Compute Module eMMC should appear as a USB mass storage device.

### Flash the eMMC

You can use Raspberry Pi Imager to flash an operating system image to a Compute Module. Raspberry Pi Imager Download URL: https://www.raspberrypi.com/documentation/computers/getting-started.html#raspberry-pi-imager Alternatively, use dd to write a raw OS image (such as Raspberry Pi OS) to your Compute Module. Run the following command, replacing /dev/sdX with the path to the mass storage device representation of your Compute Module and raw_os_image.img with the path to your raw OS image:

    sudo dd if=raw_os_image.img of=/dev/sdX bs=4MiB

Once the image has been written, disconnect and reconnect the Compute Module. You should now see two partitions (for Raspberry Pi OS):

    /dev/sdX    <- Device
    /dev/sdX1   <- First partition (FAT)
    /dev/sdX2   <- Second partition (Linux filesystem)

You can mount the /dev/sdX1 and /dev/sdX2 partitions normally. For example: Following figure shows that how to dump the OS from Raspberry Pi’s MicroSD card to the CM5’s eMMC storage:

![super4c16](../imgs/super4c/main_16.png)

## Boot from eMMC

Disconnect `nRPI_BOOT` from `GND` (disable eMMC Boot) on the super4c board jumper.

Disconnect the USB slave port. Power-cycle the super4c board to boot the Compute Module from the new image you just wrote to eMMC.

## More information please visit:

[Raspberry Pi Official Documentations](https://www.raspberrypi.com/documentation/computers/compute-module.html)

## Application Demo

End-to-End Guide: Build & Manage a 4-Node Raspberry Pi CM5 Cluster with Ansible on Raspberry Pi 5

> All previous Chinese instructions condensed, corrected, and translated into a single English document.

------------------------------------------------------------------------

## 0. Hardware & Network Topology

| Node           | Role                     | IP Address      |
|----------------|--------------------------|-----------------|
| Raspberry Pi 5 | **Ansible Control Node** | 192.168.10.1/24 |
| CM5-01         | Compute Module 5         | 192.168.10.11   |
| CM5-02         | Compute Module 5         | 192.168.10.12   |
| CM5-03         | Compute Module 5         | 192.168.10.13   |
| CM5-04         | Compute Module 5         | 192.168.10.14   |

------------------------------------------------------------------------

## 1. Prepare the Control Node (ONLY this machine)

    sudo apt update && sudo apt full-upgrade -y
    sudo apt install -y python3-pip sshpass jq
    pip3 install --user ansible-core==2.16
    echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc && source ~/.bashrc

    mkdir -p ~/cm5-cluster/{inventory,group_vars,playbooks,roles,report}
    cd ~/cm5-cluster

## Inventory & First-Time SSH Setup

-   Create `inventory/hosts.yml`

        all:
          children:
            cm5_cluster:
              hosts:
                CM501: {ansible_host: 192.168.10.11}
                CM502: {ansible_host: 192.168.10.12}
                CM503: {ansible_host: 192.168.10.13}
                CM504: {ansible_host: 192.168.10.14}
              vars:
                ansible_user: pi
                ansible_ssh_pass: raspberry
                ansible_ssh_common_args: '-o StrictHostKeyChecking=no'

    Generate & push SSH key (password login is kept):

### Create playbooks/init-ssh.yml file

    ---
    - hosts: cm5_cluster
      gather_facts: no
      tasks:
        - name: Push public key
          authorized_key:
            user: pi
            key: "{{ lookup('file', '~/.ssh/id_ed25519.pub') }}"

### Run once:

    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ''
    ansible-galaxy collection install ansible.posix   # only if using FQCN
    ansible-playbook -i inventory/hosts.yml playbooks/init-ssh.yml

### Basic System Initialization

-   playbooks/site.yml

    ---
    - name: Initialize all CM5 nodes
      hosts: cm5_cluster
      become: yes
      roles:
        - common

### Create `roles/common/tasks/main.yml`

    ---
    - name: Expand root filesystem
      shell: raspi-config --expand-rootfs
      notify: reboot

    - name: Set unique hostname
      hostname:
        name: "{{ inventory_hostname }}"

    - name: Update system
      apt:
        update_cache: yes
        upgrade: dist

    - name: Install common packages
      apt:
        name:
          - python3-venv
          - python3-dev
          - build-essential
          - git
          - htop
          - vim
        state: present

    handlers:
      - name: reboot
        reboot:

\* Execute:

    ansible-playbook -i inventory/hosts.yml playbooks/site.yml

## Create Python Virtualenv & Install Data-Science Packages

-   create `playbooks/venv.yml`

        ---
        - name: Deploy Python venv with AI/ML packages
          hosts: cm5_cluster
          become: yes
          vars:
            venv_path: "/home/{{ ansible_user }}/venv"
            python_packages:
              - pandas
              - numpy
              - opencv-python
              - matplotlib
              - seaborn
              - xgboost
              - pillow
              - onnxruntime
          tasks:
            - name: Ensure venv directory exists
              file:
                path: "{{ venv_path }}"
                state: directory
                owner: "{{ ansible_user }}"
                group: "{{ ansible_user }}"

            - name: Create virtualenv
              command: python3 -m venv {{ venv_path }}
              args:
                creates: "{{ venv_path }}/bin/activate"

            - name: Upgrade pip
              pip:
                executable: "{{ venv_path }}/bin/pip"
                name: pip
                state: latest

            - name: Install packages
              pip:
                executable: "{{ venv_path }}/bin/pip"
                name: "{{ python_packages }}"

            - name: Auto-activate venv on login
              copy:
                dest: /etc/profile.d/venv.sh
                mode: '0644'
                content: |
                  [ -d "{{ venv_path }}" ] && source {{ venv_path }}/bin/activate

-   Execute:

        ansible-playbook -i inventory/hosts.yml playbooks/venv.yml

## Gather Hostname, IP, Disk Information

-   Create `playbooks/gather-host-info.yml`

        ---
        - name: Collect hostname, IPs, disk usage
          hosts: cm5_cluster
          gather_facts: yes
          vars:
            report_dir: "{{ playbook_dir }}/../report"
          tasks:
            - name: Ensure report directory exists (locally)
              file:
                path: "{{ report_dir }}"
                state: directory
              delegate_to: localhost
              run_once: yes

            - name: Render per-host JSON file
              template:
                src: host-info.json.j2
                dest: "{{ report_dir }}/{{ inventory_hostname }}.json"
              delegate_to: localhost

-   Create playbooks/templates/host-info.json.j2

        {% set root = ansible_mounts | selectattr('mount','equalto','/') | first %}
        {"hostname":"{{ ansible_hostname }}","ipv4":{{ ansible_all_ipv4_addresses | to_json }},"disk_GB":"{{ (root.block_total * root.block_size / 1024**3) | round(2) }}","used_GB":"{{ (root.block_used * root.block_size / 1024**3) | round(2) }}","usage":"{{ (root.block_used / root.block_total * 100) | round(1) }}%"}

-   Run & view:

        sudo apt -y install jq
        ansible-playbook -i inventory/hosts.yml playbooks/gather-host-info.yml
        cat report/*.json | jq -s .

## Batch Shutdown / Reboot

-   Create `playbooks/shutdown.yml`

        ---
        - name: Shutdown all CM5 nodes
          hosts: cm5_cluster
          become: yes
          tasks:
            - name: Power off
              command: shutdown -h now

-   Create `playbooks/reboot.yml`

        ---
        - name: Reboot all CM5 nodes
          hosts: cm5_cluster
          become: yes
          tasks:
            - name: Reboot
              command: reboot 

-   Execute:

        ansible-playbook -i inventory/hosts.yml playbooks/shutdown.yml   # shutdown
        ansible-playbook -i inventory/hosts.yml playbooks/reboot.yml    # reboot  

### Get the CPU temperature

-   Create a file structure like this:

<!-- -->

    cpu_temp/
    ├── hosts.ini          # Inventory file – list of managed hosts
    ├── cpu_temp.yml       # Main Ansible playbook
    └── templates/
        └── temp_report.j2 # Optional Jinja2 template for formatted output

-   Explanations:

| Directory / File           | Purpose & Explanation (English)                                                        |
|----------------------------|----------------------------------------------------------------------------------------|
| `cpu_temp/`                | Root directory that contains all playbook-related files.                               |
| `hosts.ini`                | Inventory file listing the managed hosts (the Raspberry Pi nodes).                     |
| `cpu_temp.yml`             | Main Ansible playbook that defines the tasks to retrieve and process CPU temperatures. |
| `templates/`               | Directory for Jinja2 templates used to create formatted reports or files.              |
| `templates/temp_report.j2` | Optional Jinja2 template for generating a nicely-formatted output report.              |

-   Create `playbooks/cpu_temp.yml`

        # This playbook retrieves the CPU temperature of managed Raspberry Pi hosts.
        # The `vcgencmd measure_temp` command is executed on each host to get the real-time temperature.

        - name: Retrieve CPU temperature from managed Raspberry Pi hosts
          hosts: rpi
          gather_facts: no        # Skip full fact gathering to speed up execution
          become: no              # vcgencmd can be run by the pi user without sudo

          tasks:
            - name: Execute vcgencmd measure_temp to obtain real-time temperature
              ansible.builtin.command: vcgencmd measure_temp
              register: temp_raw  # Save command output in the variable temp_raw

            - name: Parse temperature value (remove prefix and unit)
              ansible.builtin.set_fact:
                cpu_temp: "{{ (temp_raw.stdout | regex_replace('temp=', '') | regex_replace(\"'C\\n\", '')) }}"

            - name: Display temperature for each host in the console
              ansible.builtin.debug:
                msg: "Host {{ inventory_hostname }} CPU temperature: {{ cpu_temp }}°C"

            - name: Append results to a local summary file (optional)
              ansible.builtin.lineinfile:
                path: "./cpu_temp_summary.txt"
                line: "{{ '%Y-%m-%d %H:%M:%S' | strftime }} - {{ inventory_hostname }} - {{ cpu_temp }}°C"
                create: yes
              delegate_to: localhost  # Run this task on the Ansible control node 

-   Explanations:

| Playbook Segment                                 | Purpose & Explanation (English)                                                                                 |
|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `---`                                            | YAML file start marker.                                                                                         |
| `- name: Get Raspberry Pi CPU Temperature`       | Name of the play; it appears in the playbook output.                                                            |
| `hosts: rpi`                                     | Targets only hosts in the `[rpi]` group from the inventory.                                                     |
| `gather_facts: no`                               | Skips the `setup` module to reduce SSH round-trips and speed up execution.                                      |
| `become: no`                                     | Does not escalate privileges; `vcgencmd` does not require root.                                                 |
| `ansible.builtin.command: vcgencmd measure_temp` | Executes the temperature-retrieval command on the remote host.                                                  |
| `register: temp_raw`                             | Captures stdout, stderr, and return code of the command into the variable `temp_raw`.                           |
| `set_fact: cpu_temp: ...`                        | Uses regex to strip prefixes like `temp=` and the trailing `'C`, leaving only the numeric value (e.g., `47.2`). |
| `debug: msg: "Host: ..."`                        | Prints the formatted temperature for each host in real time on the console.                                     |
| `lineinfile: ...`                                | Appends results to `cpu_temp_summary.txt` on the control node for later review or graphing.                     |
| `delegate_to: localhost`                         | Ensures the file-append task runs on the Ansible control node, not on the managed hosts.                        |

-   Execute:

        cd cpu_temp
        ansible-playbook -i hosts.ini cpu_temp.yml

## Quick Reference

| Action             | Command                                              |
|--------------------|------------------------------------------------------|
| Check connectivity | `ansible cm5_cluster -i inventory/hosts.yml -m ping` |
| Ad-hoc shell       | `ansible cm5_cluster -a "uname -a"`                  |
| View JSON report   | `cat ~/cm5-cluster/report/*.json \| jq -s .`         |

Enjoy your fully-automated CM5 cluster!
