# Linux Hardware

## LoRa Radio Interfaces

### SPI

Supported [boards](/docs/meshtasticd/hardware/boards/) can be paired with SPI radio hats, such as the RAK6421.

### USB

Any Linux device with a USB port can use a CH341-based USB radio.

USB support via the **CH341** was added in Meshtastic 2.5.18.

Note that in order for Linux to recognize multiple CH341-USB devices, an EEPROM must be included onboard, burned with a unique serial number. Devices like the Pine64 Pinedio v1 do not include this.

## Hardware Compatibility

<span class="admonitionIcon_wqLL"></span>Warning

-   **UART** HATs and SX1302/SX1303 chip-based HATs are not supported. Only hats that use a SPI radio can work with Meshtastic.
-   The Waveshare SX1262 LoRaWAN Hat for Raspberry Pi is not recommended for deployment. It has known hardware limitations that may affect longer messages. If you must use it, please use the **CLIENT_MUTE** role to avoid rebroadcasting.
-   The Pine64 Pinedio is also not recommended for deployment, as it suffers from similar hardware limitations as the Waveshare SX1262 LoRaWAN Hat.

See: <a href="https://www.youtube.com/watch?v=PND1GlMSrEM" rel="noopener noreferrer" target="_blank">The Meshtastic CRC Problem</a>

-   Tested USB devices include the <a href="https://github.com/markbirss/MESHSTICK" rel="noopener noreferrer" target="_blank">MeshStick</a> and Pinedio CH341 USB adapter.
-   Tested Raspberry Pi LoRa hats include the <a href="https://github.com/chrismyers2000/MeshAdv-Pi-Hat" rel="noopener noreferrer" target="_blank">MeshAdv-Pi v1.1</a>, Adafruit RFM9x, and Elecrow Lora RFM95 IOT.
-   Support for I²C displays, SPI displays, and keyboard input has been confirmed. It is necessary to be aware of potential pin conflicts when stacking hats.

### System Requirements

-   The Meshtastic binary, `meshtasticd`, necessitates root access or a user with permissions to access GPIO, SPI, and other interfaces.
-   A Linux distribution compatible with the Meshtastic installation packages.
