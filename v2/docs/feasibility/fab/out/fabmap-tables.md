candidate af8a9186f981210c mismatches 0; B21 0e72edb5d755316f mismatches 28
| pcie-up | 1 | PCIe TX+ (module transmit) | U30B.122 PCIe_TX_P | PCIE1_TX_P | -> U101.128 PERP0 | - | OK | B21 same: OK  |
| pcie-up | 1 | PCIe TX- | U30B.124 PCIe_TX_N | PCIE1_TX_N | -> U101.127 PERN0 | - | OK | B21 same: OK  |
| pcie-up | 1 | PCIe RX+ (module receive) | U30B.116 PCIe_RX_P | PCIE1_RX_P | C151(220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)) -> U101.124 PETP0 | - | OK | B21 same: OK  |
| pcie-up | 1 | PCIe RX- | U30B.118 PCIe_RX_N | PCIE1_RX_N | C152(220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)) -> U101.123 PETN0 | - | OK | B21 same: OK  |
| pcie-ctl | 1 | PCIe_CLK_P (module 100 MHz out) | U30B.110 PCIe_CLK_P | PCIE1_CLK_P | -> U101.74 REFCLKI_P | - | OK | B21 same: OK  |
| pcie-ctl | 1 | PCIe_CLK_N | U30B.112 PCIe_CLK_N | PCIE1_CLK_N | -> U101.73 REFCLKI_N | - | OK | B21 same: OK  |
| pcie-ctl | 1 | PCIe_CLK_nREQ | U30B.102 PCIe_CLK_nREQ | PCIE1_CLKREQ_n | - | R129 1k to GND | n/a | B21 same: n/a  |
| pcie-ctl | 1 | PCIe_nRST | U30B.109 PCIe_nRST | PCIE1_nRST | -> U101.10 PERST_L | - | OK | B21 same: OK  |
| pcie-ctl | 1 | PCIE_nWAKE | U30B.104 PCIE_nWAKE | PCIE1_nWAKE | -> J_M2C1.55 ~{PEWAKE0}; -> J_M2N1.54 ~{PEWAKE} | R132 10k to +3V3_S1B | OK | B21 same: OK  |
| pcie-ctl | 1 | PCIE_PWR_EN | U30B.106 PCIE_PWR_EN | PCIE_PWR_EN1 | R164(10k) -> Q111.3 D; R164(10k) -> U103.3 S1A_EN | R106 100k to GND | n/a | B21 DIFFERS: n/a PCIE_PWR_EN1 -> U103.3 PCIE_PWR_EN1 |
| pcie-dn | 1 | port 1 switch TX+ to NVMe | U101.100 PETP1 | NVME1_RX_SW_P | C153(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2N1.49 PETp0/SATA-A+ | - | OK | B21 DIFFERS: MISMATCH NVME1_RX_P -> J_M2N1.43 PERp0/SATA-B- |
| pcie-dn | 1 | port 1 switch TX- | U101.101 PETN1 | NVME1_RX_SW_N | C154(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2N1.47 PETn0/SATA-A- | - | OK | B21 DIFFERS: MISMATCH NVME1_RX_N -> J_M2N1.41 PERn0/SATA-B+ |
| pcie-dn | 1 | port 1 switch RX+ from NVMe | U101.97 PERP1 | NVME1_TX_P | -> J_M2N1.43 PERp0/SATA-B- | - | OK | B21 DIFFERS: MISMATCH NVME1_TX_P -> J_M2N1.49 PETp0/SATA-A+ |
| pcie-dn | 1 | port 1 switch RX- | U101.98 PERN1 | NVME1_TX_N | -> J_M2N1.41 PERn0/SATA-B+ | - | OK | B21 DIFFERS: MISMATCH NVME1_TX_N -> J_M2N1.47 PETn0/SATA-A- |
| pcie-dn | 1 | port 1 PERST# | U101.5 DWNRST_L1 | PCIE1_RST1_n | -> J_M2N1.50 ~{PERST} | - | OK | B21 same: OK  |
| pcie-dn | 1 | port 2 switch TX+ to card (key E) | U101.106 PETP2 | CARD1_RX_SW_P | C155(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2C1.35 PETp0 | - | OK | B21 DIFFERS: MISMATCH CARD1_RX_P -> J_M2C1.41 PERp0 |
| pcie-dn | 1 | port 2 switch TX- | U101.107 PETN2 | CARD1_RX_SW_N | C156(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2C1.37 PETn0 | - | OK | B21 DIFFERS: MISMATCH CARD1_RX_N -> J_M2C1.43 PERn0 |
| pcie-dn | 1 | port 2 switch RX+ from card | U101.102 PERP2 | CARD1_TX_P | -> J_M2C1.41 PERp0 | - | OK | B21 DIFFERS: MISMATCH CARD1_TX_P -> J_M2C1.35 PETp0 |
| pcie-dn | 1 | port 2 switch RX- | U101.103 PERN2 | CARD1_TX_N | -> J_M2C1.43 PERn0 | - | OK | B21 DIFFERS: MISMATCH CARD1_TX_N -> J_M2C1.37 PETn0 |
| pcie-dn | 1 | port 2 PERST# | U101.6 DWNRST_L2 | PCIE1_RST2_n | -> J_M2C1.52 ~{PERST0} | - | OK | B21 same: OK  |
| pcie-dn | 1 | port 3 TX+ (unused) | U101.118 PETP3 | unconnected-(U101-PETP3-Pad118) | - | - | n/a | B21 same: n/a  |
| pcie-dn | 1 | port 3 RX+ (unused) | U101.122 PERP3 | unconnected-(U101-PERP3-Pad122) | - | - | n/a | B21 same: n/a  |
| refclk | 1 | REFCLKO_P0 to own REFCLKP | U101.85 REFCLKO_P0 | PCIE1_RCLK0_SRC_P | R175(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) + C195(100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)) -> U101.110 REFCLKP | R177 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK PCIE1_RCLK0_P -> U101.110 REFCLKP |
| refclk | 1 | REFCLKO_N0 to own REFCLKN | U101.83 REFCLKO_N0 | PCIE1_RCLK0_SRC_N | R176(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) + C196(100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)) -> U101.111 REFCLKN | R178 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK PCIE1_RCLK0_N -> U101.111 REFCLKN |
| refclk | 1 | REFCLKO_P1 to NVMe REFCLKp | U101.81 REFCLKO_P1 | NVME1_CLK_SRC_P | R179(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2N1.55 REFCLKp | R181 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK NVME1_CLK_P -> J_M2N1.55 REFCLKp |
| refclk | 1 | REFCLKO_N1 to NVMe REFCLKn | U101.80 REFCLKO_N1 | NVME1_CLK_SRC_N | R180(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2N1.53 REFCLKn | R182 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK NVME1_CLK_N -> J_M2N1.53 REFCLKn |
| refclk | 1 | REFCLKO_P2 to card REFCLKp | U101.78 REFCLKO_P2 | CARD1_CLK_SRC_P | R183(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2C1.47 REFCLKp0 | R185 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK CARD1_CLK_P -> J_M2C1.47 REFCLKp0 |
| refclk | 1 | REFCLKO_N2 to card REFCLKn | U101.77 REFCLKO_N2 | CARD1_CLK_SRC_N | R184(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2C1.49 REFCLKn0 | R186 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK CARD1_CLK_N -> J_M2C1.49 REFCLKn0 |
| refclk | 1 | REFCLKO_P3 (unused) | U101.76 REFCLKO_P3 | unconnected-(U101-REFCLKO_P3-Pad76) | - | - | n/a | B21 same: n/a  |
| refclk | 1 | IREF | U101.86 IREF | S1_IREF | - | R117 475 1% (IREF) to GND | n/a | B21 same: n/a  |
| refclk | 1 | REXT | U101.116 REXT | S1_REXT | - | R118 1.43k 1% (REXT) to GND | n/a | B21 same: n/a  |
| refclk | 1 | CLKBUF_PD | U101.60 CLKBUF_PD | unconnected-(U101-CLKBUF_PD-Pad60) | - | - | n/a | B21 same: n/a  |
| refclk | 1 | SLOTCLK | U101.33 SLOTCLK | S1_SLOTCLK | - | R119 5.1k to +3V3_S1B | n/a | B21 same: n/a  |
| strap | 1 | TEST1 | U101.9 TEST1 | S1_TEST1 | - | R123 5.1k to +3V3_S1B | n/a | B21 same: n/a  |
| strap | 1 | TEST2 | U101.16 TEST2 | S1_TESTL | -> U101.17 TEST3; -> U101.18 VC1_EN; -> U101.22 TEST4; -> U101.25 TEST5; -> U101.51 TEST6 | R124 330 to GND | n/a | B21 same: n/a  |
| strap | 1 | TCK | U101.89 TCK | S1_JTAGL | -> U101.92 TMS; -> U101.93 TDI; -> U101.94 TRST_L | R128 330 to GND | n/a | B21 same: n/a  |
| strap | 1 | TDI | U101.93 TDI | S1_JTAGL | -> U101.89 TCK; -> U101.92 TMS; -> U101.94 TRST_L | R128 330 to GND | n/a | B21 same: n/a  |
| usb-home | 1 | USB3-0 TX+ (home host of bank 1) | U30B.142 USB3-0-TX_P | HOST1_0TX_P | -> U109.19 B0p | - | OK | B21 same: OK  |
| usb-home | 1 | USB3-0 TX- | U30B.140 USB3-0-TX_N | HOST1_0TX_N | -> U109.18 B0n | - | OK | B21 same: OK  |
| usb-home | 1 | USB3-0 RX+ | U30B.130 USB3-0-RX_P | HOST1_0RX_P | -> U109.17 B1p | - | OK | B21 same: OK  |
| usb-home | 1 | USB3-0 RX- | U30B.128 USB3-0-RX_N | HOST1_0RX_N | -> U109.16 B1n | - | OK | B21 same: OK  |
| usb-home | 1 | USB3-0 D+ (USB 2.0 half) | U30B.134 USB3-0-DP | HOST1_0D_P | -> U110.1 1Dp | - | OK | B21 same: OK  |
| usb-home | 1 | USB3-0 D- | U30B.136 USB3-0-DM | HOST1_0D_N | -> U110.2 1Dn | - | OK | B21 same: OK  |
| usb-fail | 1 | USB3-1 TX+ (failover host of bank 3) | U30B.171 USB3-1-TX_P | HOST1_1TX_P | -> U309.15 C0p | - | OK | B21 same: OK  |
| usb-fail | 1 | USB3-1 TX- | U30B.169 USB3-1-TX_N | HOST1_1TX_N | -> U309.14 C0n | - | OK | B21 same: OK  |
| usb-fail | 1 | USB3-1 RX+ | U30B.159 USB3-1-RX_P | HOST1_1RX_P | -> U309.13 C1p | - | OK | B21 same: OK  |
| usb-fail | 1 | USB3-1 RX- | U30B.157 USB3-1-RX_N | HOST1_1RX_N | -> U309.12 C1n | - | OK | B21 same: OK  |
| usb-fail | 1 | USB3-1 D+ | U30B.163 USB3-1-DP | HOST1_1D_P | -> U310.3 2Dp | - | OK | B21 same: OK  |
| usb-fail | 1 | USB3-1 D- | U30B.165 USB3-1-DM | HOST1_1D_N | -> U310.4 2Dn | - | OK | B21 same: OK  |
| usb-ctl | 1 | VBUS_EN | U30B.111 VBUS_EN | unconnected-(U30B-VBUS_EN-Pad111) | - | - | n/a | B21 same: n/a  |
| usb-ctl | 1 | USB_OTG_ID | U30B.101 USB_OTG_ID | unconnected-(U30B-USB_OTG_ID-Pad101) | - | - | n/a | B21 same: n/a  |
| hdmi | 1 | HDMI0_TX2_P | U30B.170 HDMI0_TX2_P | HDMI1_D2_P | -> U3.34 D2P_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_TX2_N | U30B.172 HDMI0_TX2_N | HDMI1_D2_N | -> U3.33 D2N_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_TX1_P | U30B.176 HDMI0_TX1_P | HDMI1_D1_P | -> U3.36 D1P_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_TX1_N | U30B.178 HDMI0_TX1_N | HDMI1_D1_N | -> U3.35 D1N_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_TX0_P | U30B.182 HDMI0_TX0_P | HDMI1_D0_P | -> U3.38 D0P_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_TX0_N | U30B.184 HDMI0_TX0_N | HDMI1_D0_N | -> U3.37 D0N_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_CLK_P | U30B.188 HDMI0_CLK_P | HDMI1_CK_P | -> U3.32 D3P_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_CLK_N | U30B.190 HDMI0_CLK_N | HDMI1_CK_N | -> U3.31 D3N_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_SDA | U30B.199 HDMI0_SDA | HDMI1_SDA | -> U3.41 SDA_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_SCL | U30B.200 HDMI0_SCL | HDMI1_SCL | -> U3.42 SCL_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_HOTPLUG | U30B.153 HDMI0_HOTPLUG | HDMI1_HPD | -> U3.19 HPD_A | - | OK | B21 same: OK  |
| hdmi | 1 | HDMI0_CEC | U30B.151 HDMI0_CEC | HDMI1_CEC | -> U3.18 CEC_A | - | OK | B21 same: OK  |
| eth | 1 | Ethernet_Pair0_P | U30A.12 Ethernet_Pair0_P | ETH1_P0_P | C175(100n) -> U1.1 TXRX1P_A | - | OK | B21 same: OK  |
| eth | 1 | Ethernet_Pair0_N | U30A.10 Ethernet_Pair0_N | ETH1_P0_N | C176(100n) -> U1.2 TXRX1M_A | - | OK | B21 same: OK  |
| eth | 1 | Ethernet_Pair1_P | U30A.4 Ethernet_Pair1_P | ETH1_P1_P | C177(100n) -> U1.4 TXRX1P_B | - | OK | B21 same: OK  |
| eth | 1 | Ethernet_Pair1_N | U30A.6 Ethernet_Pair1_N | ETH1_P1_N | C178(100n) -> U1.5 TXRX1M_B | - | OK | B21 same: OK  |
| eth | 1 | Ethernet_Pair2_P | U30A.11 Ethernet_Pair2_P | ETH1_P2_P | C179(100n) -> U1.6 TXRX1P_C | - | OK | B21 same: OK  |
| eth | 1 | Ethernet_Pair2_N | U30A.9 Ethernet_Pair2_N | ETH1_P2_N | C180(100n) -> U1.7 TXRX1M_C | - | OK | B21 same: OK  |
| eth | 1 | Ethernet_Pair3_P | U30A.3 Ethernet_Pair3_P | ETH1_P3_P | C181(100n) -> U1.8 TXRX1P_D | - | OK | B21 same: OK  |
| eth | 1 | Ethernet_Pair3_N | U30A.5 Ethernet_Pair3_N | ETH1_P3_N | C182(100n) -> U1.9 TXRX1M_D | - | OK | B21 same: OK  |
| hb | 1 | GPIO16 heartbeat | U30A.29 GPIO16 | HB_CM1 | -> Q105.2 S | R157 10k to +3V3_CM1 | n/a | B21 same: n/a  |
| pcie-up | 2 | PCIe TX+ (module transmit) | U31B.122 PCIe_TX_P | PCIE2_TX_P | -> U201.128 PERP0 | - | OK | B21 same: OK  |
| pcie-up | 2 | PCIe TX- | U31B.124 PCIe_TX_N | PCIE2_TX_N | -> U201.127 PERN0 | - | OK | B21 same: OK  |
| pcie-up | 2 | PCIe RX+ (module receive) | U31B.116 PCIe_RX_P | PCIE2_RX_P | C251(220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)) -> U201.124 PETP0 | - | OK | B21 same: OK  |
| pcie-up | 2 | PCIe RX- | U31B.118 PCIe_RX_N | PCIE2_RX_N | C252(220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)) -> U201.123 PETN0 | - | OK | B21 same: OK  |
| pcie-ctl | 2 | PCIe_CLK_P (module 100 MHz out) | U31B.110 PCIe_CLK_P | PCIE2_CLK_P | -> U201.74 REFCLKI_P | - | OK | B21 same: OK  |
| pcie-ctl | 2 | PCIe_CLK_N | U31B.112 PCIe_CLK_N | PCIE2_CLK_N | -> U201.73 REFCLKI_N | - | OK | B21 same: OK  |
| pcie-ctl | 2 | PCIe_CLK_nREQ | U31B.102 PCIe_CLK_nREQ | PCIE2_CLKREQ_n | - | R229 1k to GND | n/a | B21 same: n/a  |
| pcie-ctl | 2 | PCIe_nRST | U31B.109 PCIe_nRST | PCIE2_nRST | -> U201.10 PERST_L | - | OK | B21 same: OK  |
| pcie-ctl | 2 | PCIE_nWAKE | U31B.104 PCIE_nWAKE | PCIE2_nWAKE | -> J_M2C2.54 ~{PEWAKE}; -> J_M2N2.54 ~{PEWAKE} | R232 10k to +3V3_S2B | OK | B21 same: OK  |
| pcie-ctl | 2 | PCIE_PWR_EN | U31B.106 PCIE_PWR_EN | PCIE_PWR_EN2 | -> U203.3 PCIE_PWR_EN2 | R206 100k to GND | n/a | B21 same: n/a  |
| pcie-dn | 2 | port 1 switch TX+ to NVMe | U201.100 PETP1 | NVME2_RX_SW_P | C253(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2N2.49 PETp0/SATA-A+ | - | OK | B21 DIFFERS: MISMATCH NVME2_RX_P -> J_M2N2.43 PERp0/SATA-B- |
| pcie-dn | 2 | port 1 switch TX- | U201.101 PETN1 | NVME2_RX_SW_N | C254(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2N2.47 PETn0/SATA-A- | - | OK | B21 DIFFERS: MISMATCH NVME2_RX_N -> J_M2N2.41 PERn0/SATA-B+ |
| pcie-dn | 2 | port 1 switch RX+ from NVMe | U201.97 PERP1 | NVME2_TX_P | -> J_M2N2.43 PERp0/SATA-B- | - | OK | B21 DIFFERS: MISMATCH NVME2_TX_P -> J_M2N2.49 PETp0/SATA-A+ |
| pcie-dn | 2 | port 1 switch RX- | U201.98 PERN1 | NVME2_TX_N | -> J_M2N2.41 PERn0/SATA-B+ | - | OK | B21 DIFFERS: MISMATCH NVME2_TX_N -> J_M2N2.47 PETn0/SATA-A- |
| pcie-dn | 2 | port 1 PERST# | U201.5 DWNRST_L1 | PCIE2_RST1_n | -> J_M2N2.50 ~{PERST} | - | OK | B21 same: OK  |
| pcie-dn | 2 | port 2 switch TX+ to card (key B) | U201.106 PETP2 | CARD2_RX_SW_P | C255(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2C2.49 PETp0/SATA-A+ | - | OK | B21 DIFFERS: MISMATCH CARD2_RX_P -> J_M2C2.43 PERp0/SATA-B- |
| pcie-dn | 2 | port 2 switch TX- | U201.107 PETN2 | CARD2_RX_SW_N | C256(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2C2.47 PETn0/SATA-A- | - | OK | B21 DIFFERS: MISMATCH CARD2_RX_N -> J_M2C2.41 PERn0/SATA-B+ |
| pcie-dn | 2 | port 2 switch RX+ from card | U201.102 PERP2 | CARD2_TX_P | -> J_M2C2.43 PERp0/SATA-B- | - | OK | B21 DIFFERS: MISMATCH CARD2_TX_P -> J_M2C2.49 PETp0/SATA-A+ |
| pcie-dn | 2 | port 2 switch RX- | U201.103 PERN2 | CARD2_TX_N | -> J_M2C2.41 PERn0/SATA-B+ | - | OK | B21 DIFFERS: MISMATCH CARD2_TX_N -> J_M2C2.47 PETn0/SATA-A- |
| pcie-dn | 2 | port 2 PERST# | U201.6 DWNRST_L2 | PCIE2_RST2_n | -> J_M2C2.50 ~{PERST} | - | OK | B21 same: OK  |
| pcie-dn | 2 | port 3 TX+ (unused) | U201.118 PETP3 | unconnected-(U201-PETP3-Pad118) | - | - | n/a | B21 same: n/a  |
| pcie-dn | 2 | port 3 RX+ (unused) | U201.122 PERP3 | unconnected-(U201-PERP3-Pad122) | - | - | n/a | B21 same: n/a  |
| refclk | 2 | REFCLKO_P0 to own REFCLKP | U201.85 REFCLKO_P0 | PCIE2_RCLK0_SRC_P | R275(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) + C295(100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)) -> U201.110 REFCLKP | R277 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK PCIE2_RCLK0_P -> U201.110 REFCLKP |
| refclk | 2 | REFCLKO_N0 to own REFCLKN | U201.83 REFCLKO_N0 | PCIE2_RCLK0_SRC_N | R276(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) + C296(100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)) -> U201.111 REFCLKN | R278 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK PCIE2_RCLK0_N -> U201.111 REFCLKN |
| refclk | 2 | REFCLKO_P1 to NVMe REFCLKp | U201.81 REFCLKO_P1 | NVME2_CLK_SRC_P | R279(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2N2.55 REFCLKp | R281 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK NVME2_CLK_P -> J_M2N2.55 REFCLKp |
| refclk | 2 | REFCLKO_N1 to NVMe REFCLKn | U201.80 REFCLKO_N1 | NVME2_CLK_SRC_N | R280(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2N2.53 REFCLKn | R282 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK NVME2_CLK_N -> J_M2N2.53 REFCLKn |
| refclk | 2 | REFCLKO_P2 to card REFCLKp | U201.78 REFCLKO_P2 | CARD2_CLK_SRC_P | R283(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2C2.55 REFCLKp | R285 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK CARD2_CLK_P -> J_M2C2.55 REFCLKp |
| refclk | 2 | REFCLKO_N2 to card REFCLKn | U201.77 REFCLKO_N2 | CARD2_CLK_SRC_N | R284(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2C2.53 REFCLKn | R286 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK CARD2_CLK_N -> J_M2C2.53 REFCLKn |
| refclk | 2 | REFCLKO_P3 (unused) | U201.76 REFCLKO_P3 | unconnected-(U201-REFCLKO_P3-Pad76) | - | - | n/a | B21 same: n/a  |
| refclk | 2 | IREF | U201.86 IREF | S2_IREF | - | R217 475 1% (IREF) to GND | n/a | B21 same: n/a  |
| refclk | 2 | REXT | U201.116 REXT | S2_REXT | - | R218 1.43k 1% (REXT) to GND | n/a | B21 same: n/a  |
| refclk | 2 | CLKBUF_PD | U201.60 CLKBUF_PD | unconnected-(U201-CLKBUF_PD-Pad60) | - | - | n/a | B21 same: n/a  |
| refclk | 2 | SLOTCLK | U201.33 SLOTCLK | S2_SLOTCLK | - | R219 5.1k to +3V3_S2B | n/a | B21 same: n/a  |
| strap | 2 | TEST1 | U201.9 TEST1 | S2_TEST1 | - | R223 5.1k to +3V3_S2B | n/a | B21 same: n/a  |
| strap | 2 | TEST2 | U201.16 TEST2 | S2_TESTL | -> U201.17 TEST3; -> U201.18 VC1_EN; -> U201.22 TEST4; -> U201.25 TEST5; -> U201.51 TEST6 | R224 330 to GND | n/a | B21 same: n/a  |
| strap | 2 | TCK | U201.89 TCK | S2_JTAGL | -> U201.92 TMS; -> U201.93 TDI; -> U201.94 TRST_L | R228 330 to GND | n/a | B21 same: n/a  |
| strap | 2 | TDI | U201.93 TDI | S2_JTAGL | -> U201.89 TCK; -> U201.92 TMS; -> U201.94 TRST_L | R228 330 to GND | n/a | B21 same: n/a  |
| usb-home | 2 | USB3-0 TX+ (home host of bank 2) | U31B.142 USB3-0-TX_P | HOST2_0TX_P | -> U209.19 B0p | - | OK | B21 same: OK  |
| usb-home | 2 | USB3-0 TX- | U31B.140 USB3-0-TX_N | HOST2_0TX_N | -> U209.18 B0n | - | OK | B21 same: OK  |
| usb-home | 2 | USB3-0 RX+ | U31B.130 USB3-0-RX_P | HOST2_0RX_P | -> U209.17 B1p | - | OK | B21 same: OK  |
| usb-home | 2 | USB3-0 RX- | U31B.128 USB3-0-RX_N | HOST2_0RX_N | -> U209.16 B1n | - | OK | B21 same: OK  |
| usb-home | 2 | USB3-0 D+ (USB 2.0 half) | U31B.134 USB3-0-DP | HOST2_0D_P | -> U210.1 1Dp | - | OK | B21 same: OK  |
| usb-home | 2 | USB3-0 D- | U31B.136 USB3-0-DM | HOST2_0D_N | -> U210.2 1Dn | - | OK | B21 same: OK  |
| usb-fail | 2 | USB3-1 TX+ (failover host of bank 1) | U31B.171 USB3-1-TX_P | HOST2_1TX_P | -> U109.15 C0p | - | OK | B21 same: OK  |
| usb-fail | 2 | USB3-1 TX- | U31B.169 USB3-1-TX_N | HOST2_1TX_N | -> U109.14 C0n | - | OK | B21 same: OK  |
| usb-fail | 2 | USB3-1 RX+ | U31B.159 USB3-1-RX_P | HOST2_1RX_P | -> U109.13 C1p | - | OK | B21 same: OK  |
| usb-fail | 2 | USB3-1 RX- | U31B.157 USB3-1-RX_N | HOST2_1RX_N | -> U109.12 C1n | - | OK | B21 same: OK  |
| usb-fail | 2 | USB3-1 D+ | U31B.163 USB3-1-DP | HOST2_1D_P | -> U110.3 2Dp | - | OK | B21 same: OK  |
| usb-fail | 2 | USB3-1 D- | U31B.165 USB3-1-DM | HOST2_1D_N | -> U110.4 2Dn | - | OK | B21 same: OK  |
| usb-ctl | 2 | VBUS_EN | U31B.111 VBUS_EN | unconnected-(U31B-VBUS_EN-Pad111) | - | - | n/a | B21 same: n/a  |
| usb-ctl | 2 | USB_OTG_ID | U31B.101 USB_OTG_ID | unconnected-(U31B-USB_OTG_ID-Pad101) | - | - | n/a | B21 same: n/a  |
| hdmi | 2 | HDMI0_TX2_P | U31B.170 HDMI0_TX2_P | HDMI2_D2_P | -> U3.25 D2P_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_TX2_N | U31B.172 HDMI0_TX2_N | HDMI2_D2_N | -> U3.24 D2N_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_TX1_P | U31B.176 HDMI0_TX1_P | HDMI2_D1_P | -> U3.27 D1P_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_TX1_N | U31B.178 HDMI0_TX1_N | HDMI2_D1_N | -> U3.26 D1N_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_TX0_P | U31B.182 HDMI0_TX0_P | HDMI2_D0_P | -> U3.29 D0P_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_TX0_N | U31B.184 HDMI0_TX0_N | HDMI2_D0_N | -> U3.28 D0N_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_CLK_P | U31B.188 HDMI0_CLK_P | HDMI2_CK_P | -> U3.23 D3P_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_CLK_N | U31B.190 HDMI0_CLK_N | HDMI2_CK_N | -> U3.22 D3N_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_SDA | U31B.199 HDMI0_SDA | HDMI2_SDA | -> U3.39 SDA_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_SCL | U31B.200 HDMI0_SCL | HDMI2_SCL | -> U3.40 SCL_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_HOTPLUG | U31B.153 HDMI0_HOTPLUG | HDMI2_HPD | -> U3.21 HPD_B | - | OK | B21 same: OK  |
| hdmi | 2 | HDMI0_CEC | U31B.151 HDMI0_CEC | HDMI2_CEC | -> U3.20 CEC_B | - | OK | B21 same: OK  |
| eth | 2 | Ethernet_Pair0_P | U31A.12 Ethernet_Pair0_P | ETH2_P0_P | C275(100n) -> U1.12 TXRX2P_A | - | OK | B21 same: OK  |
| eth | 2 | Ethernet_Pair0_N | U31A.10 Ethernet_Pair0_N | ETH2_P0_N | C276(100n) -> U1.13 TXRX2M_A | - | OK | B21 same: OK  |
| eth | 2 | Ethernet_Pair1_P | U31A.4 Ethernet_Pair1_P | ETH2_P1_P | C277(100n) -> U1.15 TXRX2P_B | - | OK | B21 same: OK  |
| eth | 2 | Ethernet_Pair1_N | U31A.6 Ethernet_Pair1_N | ETH2_P1_N | C278(100n) -> U1.16 TXRX2M_B | - | OK | B21 same: OK  |
| eth | 2 | Ethernet_Pair2_P | U31A.11 Ethernet_Pair2_P | ETH2_P2_P | C279(100n) -> U1.17 TXRX2P_C | - | OK | B21 same: OK  |
| eth | 2 | Ethernet_Pair2_N | U31A.9 Ethernet_Pair2_N | ETH2_P2_N | C280(100n) -> U1.18 TXRX2M_C | - | OK | B21 same: OK  |
| eth | 2 | Ethernet_Pair3_P | U31A.3 Ethernet_Pair3_P | ETH2_P3_P | C281(100n) -> U1.20 TXRX2P_D | - | OK | B21 same: OK  |
| eth | 2 | Ethernet_Pair3_N | U31A.5 Ethernet_Pair3_N | ETH2_P3_N | C282(100n) -> U1.21 TXRX2M_D | - | OK | B21 same: OK  |
| hb | 2 | GPIO16 heartbeat | U31A.29 GPIO16 | HB_CM2 | -> Q205.2 S | R257 10k to +3V3_CM2 | n/a | B21 same: n/a  |
| pcie-up | 3 | PCIe TX+ (module transmit) | U32B.122 PCIe_TX_P | PCIE3_TX_P | -> U301.128 PERP0 | - | OK | B21 same: OK  |
| pcie-up | 3 | PCIe TX- | U32B.124 PCIe_TX_N | PCIE3_TX_N | -> U301.127 PERN0 | - | OK | B21 same: OK  |
| pcie-up | 3 | PCIe RX+ (module receive) | U32B.116 PCIe_RX_P | PCIE3_RX_P | C351(220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)) -> U301.124 PETP0 | - | OK | B21 same: OK  |
| pcie-up | 3 | PCIe RX- | U32B.118 PCIe_RX_N | PCIE3_RX_N | C352(220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)) -> U301.123 PETN0 | - | OK | B21 same: OK  |
| pcie-ctl | 3 | PCIe_CLK_P (module 100 MHz out) | U32B.110 PCIe_CLK_P | PCIE3_CLK_P | -> U301.74 REFCLKI_P | - | OK | B21 same: OK  |
| pcie-ctl | 3 | PCIe_CLK_N | U32B.112 PCIe_CLK_N | PCIE3_CLK_N | -> U301.73 REFCLKI_N | - | OK | B21 same: OK  |
| pcie-ctl | 3 | PCIe_CLK_nREQ | U32B.102 PCIe_CLK_nREQ | PCIE3_CLKREQ_n | - | R329 1k to GND | n/a | B21 same: n/a  |
| pcie-ctl | 3 | PCIe_nRST | U32B.109 PCIe_nRST | PCIE3_nRST | -> U301.10 PERST_L | - | OK | B21 same: OK  |
| pcie-ctl | 3 | PCIE_nWAKE | U32B.104 PCIE_nWAKE | PCIE3_nWAKE | -> J_M2C3.55 ~{PEWAKE0}; -> J_M2N3.54 ~{PEWAKE} | R332 10k to +3V3_S3B | OK | B21 same: OK  |
| pcie-ctl | 3 | PCIE_PWR_EN | U32B.106 PCIE_PWR_EN | PCIE_PWR_EN3 | R364(10k) -> Q311.3 D; R364(10k) -> U303.3 S3A_EN | R306 100k to GND | n/a | B21 DIFFERS: n/a PCIE_PWR_EN3 -> U303.3 PCIE_PWR_EN3 |
| pcie-dn | 3 | port 1 switch TX+ to NVMe | U301.100 PETP1 | NVME3_RX_SW_P | C353(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2N3.49 PETp0/SATA-A+ | - | OK | B21 DIFFERS: MISMATCH NVME3_RX_P -> J_M2N3.43 PERp0/SATA-B- |
| pcie-dn | 3 | port 1 switch TX- | U301.101 PETN1 | NVME3_RX_SW_N | C354(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2N3.47 PETn0/SATA-A- | - | OK | B21 DIFFERS: MISMATCH NVME3_RX_N -> J_M2N3.41 PERn0/SATA-B+ |
| pcie-dn | 3 | port 1 switch RX+ from NVMe | U301.97 PERP1 | NVME3_TX_P | -> J_M2N3.43 PERp0/SATA-B- | - | OK | B21 DIFFERS: MISMATCH NVME3_TX_P -> J_M2N3.49 PETp0/SATA-A+ |
| pcie-dn | 3 | port 1 switch RX- | U301.98 PERN1 | NVME3_TX_N | -> J_M2N3.41 PERn0/SATA-B+ | - | OK | B21 DIFFERS: MISMATCH NVME3_TX_N -> J_M2N3.47 PETn0/SATA-A- |
| pcie-dn | 3 | port 1 PERST# | U301.5 DWNRST_L1 | PCIE3_RST1_n | -> J_M2N3.50 ~{PERST} | - | OK | B21 same: OK  |
| pcie-dn | 3 | port 2 switch TX+ to card (key E) | U301.106 PETP2 | CARD3_RX_SW_P | C355(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2C3.35 PETp0 | - | OK | B21 DIFFERS: MISMATCH CARD3_RX_P -> J_M2C3.41 PERp0 |
| pcie-dn | 3 | port 2 switch TX- | U301.107 PETN2 | CARD3_RX_SW_N | C356(220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)) -> J_M2C3.37 PETn0 | - | OK | B21 DIFFERS: MISMATCH CARD3_RX_N -> J_M2C3.43 PERn0 |
| pcie-dn | 3 | port 2 switch RX+ from card | U301.102 PERP2 | CARD3_TX_P | -> J_M2C3.41 PERp0 | - | OK | B21 DIFFERS: MISMATCH CARD3_TX_P -> J_M2C3.35 PETp0 |
| pcie-dn | 3 | port 2 switch RX- | U301.103 PERN2 | CARD3_TX_N | -> J_M2C3.43 PERn0 | - | OK | B21 DIFFERS: MISMATCH CARD3_TX_N -> J_M2C3.37 PETn0 |
| pcie-dn | 3 | port 2 PERST# | U301.6 DWNRST_L2 | PCIE3_RST2_n | -> J_M2C3.52 ~{PERST0} | - | OK | B21 same: OK  |
| pcie-dn | 3 | port 3 TX+ (unused) | U301.118 PETP3 | unconnected-(U301-PETP3-Pad118) | - | - | n/a | B21 same: n/a  |
| pcie-dn | 3 | port 3 RX+ (unused) | U301.122 PERP3 | unconnected-(U301-PERP3-Pad122) | - | - | n/a | B21 same: n/a  |
| refclk | 3 | REFCLKO_P0 to own REFCLKP | U301.85 REFCLKO_P0 | PCIE3_RCLK0_SRC_P | R375(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) + C395(100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)) -> U301.110 REFCLKP | R377 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK PCIE3_RCLK0_P -> U301.110 REFCLKP |
| refclk | 3 | REFCLKO_N0 to own REFCLKN | U301.83 REFCLKO_N0 | PCIE3_RCLK0_SRC_N | R376(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) + C396(100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)) -> U301.111 REFCLKN | R378 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK PCIE3_RCLK0_N -> U301.111 REFCLKN |
| refclk | 3 | REFCLKO_P1 to NVMe REFCLKp | U301.81 REFCLKO_P1 | NVME3_CLK_SRC_P | R379(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2N3.55 REFCLKp | R381 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK NVME3_CLK_P -> J_M2N3.55 REFCLKp |
| refclk | 3 | REFCLKO_N1 to NVMe REFCLKn | U301.80 REFCLKO_N1 | NVME3_CLK_SRC_N | R380(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2N3.53 REFCLKn | R382 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK NVME3_CLK_N -> J_M2N3.53 REFCLKn |
| refclk | 3 | REFCLKO_P2 to card REFCLKp | U301.78 REFCLKO_P2 | CARD3_CLK_SRC_P | R383(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2C3.47 REFCLKp0 | R385 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK CARD3_CLK_P -> J_M2C3.47 REFCLKp0 |
| refclk | 3 | REFCLKO_N2 to card REFCLKn | U301.77 REFCLKO_N2 | CARD3_CLK_SRC_N | R384(33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)) -> J_M2C3.49 REFCLKn0 | R386 49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03) to GND | OK | B21 DIFFERS: OK CARD3_CLK_N -> J_M2C3.49 REFCLKn0 |
| refclk | 3 | REFCLKO_P3 (unused) | U301.76 REFCLKO_P3 | unconnected-(U301-REFCLKO_P3-Pad76) | - | - | n/a | B21 same: n/a  |
| refclk | 3 | IREF | U301.86 IREF | S3_IREF | - | R317 475 1% (IREF) to GND | n/a | B21 same: n/a  |
| refclk | 3 | REXT | U301.116 REXT | S3_REXT | - | R318 1.43k 1% (REXT) to GND | n/a | B21 same: n/a  |
| refclk | 3 | CLKBUF_PD | U301.60 CLKBUF_PD | unconnected-(U301-CLKBUF_PD-Pad60) | - | - | n/a | B21 same: n/a  |
| refclk | 3 | SLOTCLK | U301.33 SLOTCLK | S3_SLOTCLK | - | R319 5.1k to +3V3_S3B | n/a | B21 same: n/a  |
| strap | 3 | TEST1 | U301.9 TEST1 | S3_TEST1 | - | R323 5.1k to +3V3_S3B | n/a | B21 same: n/a  |
| strap | 3 | TEST2 | U301.16 TEST2 | S3_TESTL | -> U301.17 TEST3; -> U301.18 VC1_EN; -> U301.22 TEST4; -> U301.25 TEST5; -> U301.51 TEST6 | R324 330 to GND | n/a | B21 same: n/a  |
| strap | 3 | TCK | U301.89 TCK | S3_JTAGL | -> U301.92 TMS; -> U301.93 TDI; -> U301.94 TRST_L | R328 330 to GND | n/a | B21 same: n/a  |
| strap | 3 | TDI | U301.93 TDI | S3_JTAGL | -> U301.89 TCK; -> U301.92 TMS; -> U301.94 TRST_L | R328 330 to GND | n/a | B21 same: n/a  |
| usb-home | 3 | USB3-0 TX+ (home host of bank 3) | U32B.142 USB3-0-TX_P | HOST3_0TX_P | -> U309.19 B0p | - | OK | B21 same: OK  |
| usb-home | 3 | USB3-0 TX- | U32B.140 USB3-0-TX_N | HOST3_0TX_N | -> U309.18 B0n | - | OK | B21 same: OK  |
| usb-home | 3 | USB3-0 RX+ | U32B.130 USB3-0-RX_P | HOST3_0RX_P | -> U309.17 B1p | - | OK | B21 same: OK  |
| usb-home | 3 | USB3-0 RX- | U32B.128 USB3-0-RX_N | HOST3_0RX_N | -> U309.16 B1n | - | OK | B21 same: OK  |
| usb-home | 3 | USB3-0 D+ (USB 2.0 half) | U32B.134 USB3-0-DP | HOST3_0D_P | -> U310.1 1Dp | - | OK | B21 same: OK  |
| usb-home | 3 | USB3-0 D- | U32B.136 USB3-0-DM | HOST3_0D_N | -> U310.2 1Dn | - | OK | B21 same: OK  |
| usb-fail | 3 | USB3-1 TX+ (failover host of bank 2) | U32B.171 USB3-1-TX_P | HOST3_1TX_P | -> U209.15 C0p | - | OK | B21 same: OK  |
| usb-fail | 3 | USB3-1 TX- | U32B.169 USB3-1-TX_N | HOST3_1TX_N | -> U209.14 C0n | - | OK | B21 same: OK  |
| usb-fail | 3 | USB3-1 RX+ | U32B.159 USB3-1-RX_P | HOST3_1RX_P | -> U209.13 C1p | - | OK | B21 same: OK  |
| usb-fail | 3 | USB3-1 RX- | U32B.157 USB3-1-RX_N | HOST3_1RX_N | -> U209.12 C1n | - | OK | B21 same: OK  |
| usb-fail | 3 | USB3-1 D+ | U32B.163 USB3-1-DP | HOST3_1D_P | -> U210.3 2Dp | - | OK | B21 same: OK  |
| usb-fail | 3 | USB3-1 D- | U32B.165 USB3-1-DM | HOST3_1D_N | -> U210.4 2Dn | - | OK | B21 same: OK  |
| usb-ctl | 3 | VBUS_EN | U32B.111 VBUS_EN | unconnected-(U32B-VBUS_EN-Pad111) | - | - | n/a | B21 same: n/a  |
| usb-ctl | 3 | USB_OTG_ID | U32B.101 USB_OTG_ID | unconnected-(U32B-USB_OTG_ID-Pad101) | - | - | n/a | B21 same: n/a  |
| hdmi | 3 | HDMI0_TX2_P | U32B.170 HDMI0_TX2_P | HDMI3_D2_P | -> U4.25 D2P_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_TX2_N | U32B.172 HDMI0_TX2_N | HDMI3_D2_N | -> U4.24 D2N_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_TX1_P | U32B.176 HDMI0_TX1_P | HDMI3_D1_P | -> U4.27 D1P_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_TX1_N | U32B.178 HDMI0_TX1_N | HDMI3_D1_N | -> U4.26 D1N_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_TX0_P | U32B.182 HDMI0_TX0_P | HDMI3_D0_P | -> U4.29 D0P_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_TX0_N | U32B.184 HDMI0_TX0_N | HDMI3_D0_N | -> U4.28 D0N_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_CLK_P | U32B.188 HDMI0_CLK_P | HDMI3_CK_P | -> U4.23 D3P_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_CLK_N | U32B.190 HDMI0_CLK_N | HDMI3_CK_N | -> U4.22 D3N_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_SDA | U32B.199 HDMI0_SDA | HDMI3_SDA | -> U4.39 SDA_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_SCL | U32B.200 HDMI0_SCL | HDMI3_SCL | -> U4.40 SCL_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_HOTPLUG | U32B.153 HDMI0_HOTPLUG | HDMI3_HPD | -> U4.21 HPD_B | - | OK | B21 same: OK  |
| hdmi | 3 | HDMI0_CEC | U32B.151 HDMI0_CEC | HDMI3_CEC | -> U4.20 CEC_B | - | OK | B21 same: OK  |
| eth | 3 | Ethernet_Pair0_P | U32A.12 Ethernet_Pair0_P | ETH3_P0_P | C375(100n) -> U1.24 TXRX3P_A | - | OK | B21 same: OK  |
| eth | 3 | Ethernet_Pair0_N | U32A.10 Ethernet_Pair0_N | ETH3_P0_N | C376(100n) -> U1.25 TXRX3M_A | - | OK | B21 same: OK  |
| eth | 3 | Ethernet_Pair1_P | U32A.4 Ethernet_Pair1_P | ETH3_P1_P | C377(100n) -> U1.26 TXRX3P_B | - | OK | B21 same: OK  |
| eth | 3 | Ethernet_Pair1_N | U32A.6 Ethernet_Pair1_N | ETH3_P1_N | C378(100n) -> U1.27 TXRX3M_B | - | OK | B21 same: OK  |
| eth | 3 | Ethernet_Pair2_P | U32A.11 Ethernet_Pair2_P | ETH3_P2_P | C379(100n) -> U1.28 TXRX3P_C | - | OK | B21 same: OK  |
| eth | 3 | Ethernet_Pair2_N | U32A.9 Ethernet_Pair2_N | ETH3_P2_N | C380(100n) -> U1.29 TXRX3M_C | - | OK | B21 same: OK  |
| eth | 3 | Ethernet_Pair3_P | U32A.3 Ethernet_Pair3_P | ETH3_P3_P | C381(100n) -> U1.31 TXRX3P_D | - | OK | B21 same: OK  |
| eth | 3 | Ethernet_Pair3_N | U32A.5 Ethernet_Pair3_N | ETH3_P3_N | C382(100n) -> U1.32 TXRX3M_D | - | OK | B21 same: OK  |
| hb | 3 | GPIO16 heartbeat | U32A.29 GPIO16 | HB_CM3 | -> Q305.2 S | R357 10k to +3V3_CM3 | n/a | B21 same: n/a  |
| bank | 1 | hub SS receiver + (upstream) | U102.58 USB_SSRXP_UP | BANK1_UPTX_P | -> U109.3 A0p | - | OK | B21 same: OK  |
| bank | 1 | hub SS receiver - | U102.59 USB_SSRXM_UP | BANK1_UPTX_N | -> U109.4 A0n | - | OK | B21 same: OK  |
| bank | 1 | hub SS transmitter + (upstream) | U102.55 USB_SSTXP_UP | BANK1_UPRX_P | C159(100n) -> U109.7 A1p | - | OK | B21 same: OK  |
| bank | 1 | hub SS transmitter - | U102.56 USB_SSTXM_UP | BANK1_UPRX_N | C160(100n) -> U109.8 A1n | - | OK | B21 same: OK  |
| bank | 1 | hub D+ (upstream) | U102.53 USB_DP_UP | BANK1_UPD_P | -> U110.8 Dp | - | OK | B21 same: OK  |
| bank | 1 | hub D- (upstream) | U102.54 USB_DM_UP | BANK1_UPD_N | -> U110.7 Dn | - | OK | B21 same: OK  |
| bank | 1 | hub USB_VBUS (upstream detect) | U102.48 USB_VBUS | HUB1_VBUS | - | R143 90.9k 1% to +5V_DEV; R144 10k 1% to GND | n/a | B21 same: n/a  |
| bank | 1 | hub GRSTz | U102.50 GRSTz | HUB1_RST_n | -> Q3.3 D | C163 1u to GND; R141 10k to +3V3_DEV | n/a | B21 same: n/a  |
| bank | 1 | TMUXHS4212 SEL | U109.9 SEL | BSEL1 | R474(10k) -> U80.2 BSEL1_D; -> TP504.1 1; -> U110.9 S; -> U41.38 PE8; -> U51.38 PE8; -> U61.38 PE8; -> U76.6 BSEL1; -> U80.1 BSEL1 | R160 100k to GND; C481 10n to GND | OK | B21 DIFFERS: OK BSEL1 R474(10k) -> U80.2 BSEL1_D; -> U110.9 S; -> U41.38 PE8; -> U51.38 PE8; -> U61.38 PE8; -> U76.6 BSEL1; -> U80.1 BSEL1 |
| bank | 1 | TMUXHS4212 OEn | U109.2 OEn | BOE1_n | -> TP507.1 1; -> U110.6 OEn; -> U80.3 BOE1_n | R161 100k to GND | OK | B21 DIFFERS: OK BOE1_n -> U110.6 OEn; -> U80.3 BOE1_n |
| bank | 2 | hub SS receiver + (upstream) | U202.58 USB_SSRXP_UP | BANK2_UPTX_P | -> U209.3 A0p | - | OK | B21 same: OK  |
| bank | 2 | hub SS receiver - | U202.59 USB_SSRXM_UP | BANK2_UPTX_N | -> U209.4 A0n | - | OK | B21 same: OK  |
| bank | 2 | hub SS transmitter + (upstream) | U202.55 USB_SSTXP_UP | BANK2_UPRX_P | C259(100n) -> U209.7 A1p | - | OK | B21 same: OK  |
| bank | 2 | hub SS transmitter - | U202.56 USB_SSTXM_UP | BANK2_UPRX_N | C260(100n) -> U209.8 A1n | - | OK | B21 same: OK  |
| bank | 2 | hub D+ (upstream) | U202.53 USB_DP_UP | BANK2_UPD_P | -> U210.8 Dp | - | OK | B21 same: OK  |
| bank | 2 | hub D- (upstream) | U202.54 USB_DM_UP | BANK2_UPD_N | -> U210.7 Dn | - | OK | B21 same: OK  |
| bank | 2 | hub USB_VBUS (upstream detect) | U202.48 USB_VBUS | HUB2_VBUS | - | R243 90.9k 1% to +5V_DEV; R244 10k 1% to GND | n/a | B21 same: n/a  |
| bank | 2 | hub GRSTz | U202.50 GRSTz | HUB2_RST_n | -> Q4.3 D | C263 1u to GND; R241 10k to +3V3_DEV | n/a | B21 same: n/a  |
| bank | 2 | TMUXHS4212 SEL | U209.9 SEL | BSEL2 | R475(10k) -> U80.5 BSEL2_D; -> TP505.1 1; -> U210.9 S; -> U41.39 PE9; -> U51.39 PE9; -> U61.39 PE9; -> U76.11 BSEL2; -> U80.4 BSEL2 | R260 100k to GND; C482 10n to GND | OK | B21 DIFFERS: OK BSEL2 R475(10k) -> U80.5 BSEL2_D; -> U210.9 S; -> U41.39 PE9; -> U51.39 PE9; -> U61.39 PE9; -> U76.11 BSEL2; -> U80.4 BSEL2 |
| bank | 2 | TMUXHS4212 OEn | U209.2 OEn | BOE2_n | -> TP508.1 1; -> U210.6 OEn; -> U80.6 BOE2_n | R261 100k to GND | OK | B21 DIFFERS: OK BOE2_n -> U210.6 OEn; -> U80.6 BOE2_n |
| bank | 3 | hub SS receiver + (upstream) | U302.58 USB_SSRXP_UP | BANK3_UPTX_P | -> U309.3 A0p | - | OK | B21 same: OK  |
| bank | 3 | hub SS receiver - | U302.59 USB_SSRXM_UP | BANK3_UPTX_N | -> U309.4 A0n | - | OK | B21 same: OK  |
| bank | 3 | hub SS transmitter + (upstream) | U302.55 USB_SSTXP_UP | BANK3_UPRX_P | C359(100n) -> U309.7 A1p | - | OK | B21 same: OK  |
| bank | 3 | hub SS transmitter - | U302.56 USB_SSTXM_UP | BANK3_UPRX_N | C360(100n) -> U309.8 A1n | - | OK | B21 same: OK  |
| bank | 3 | hub D+ (upstream) | U302.53 USB_DP_UP | BANK3_UPD_P | -> U310.8 Dp | - | OK | B21 same: OK  |
| bank | 3 | hub D- (upstream) | U302.54 USB_DM_UP | BANK3_UPD_N | -> U310.7 Dn | - | OK | B21 same: OK  |
| bank | 3 | hub USB_VBUS (upstream detect) | U302.48 USB_VBUS | HUB3_VBUS | - | R343 90.9k 1% to +5V_DEV; R344 10k 1% to GND | n/a | B21 same: n/a  |
| bank | 3 | hub GRSTz | U302.50 GRSTz | HUB3_RST_n | -> Q5.3 D | C363 1u to GND; R341 10k to +3V3_DEV | n/a | B21 same: n/a  |
| bank | 3 | TMUXHS4212 SEL | U309.9 SEL | BSEL3 | R476(10k) -> U80.9 BSEL3_D; -> TP506.1 1; -> U310.9 S; -> U41.40 PE10; -> U51.40 PE10; -> U61.40 PE10; -> U77.6 BSEL3; -> U80.10 BSEL3 | R360 100k to GND; C483 10n to GND | OK | B21 DIFFERS: OK BSEL3 R476(10k) -> U80.9 BSEL3_D; -> U310.9 S; -> U41.40 PE10; -> U51.40 PE10; -> U61.40 PE10; -> U77.6 BSEL3; -> U80.10 BSEL3 |
| bank | 3 | TMUXHS4212 OEn | U309.2 OEn | BOE3_n | -> TP509.1 1; -> U310.6 OEn; -> U80.8 BOE3_n | R361 100k to GND | OK | B21 DIFFERS: OK BOE3_n -> U310.6 OEn; -> U80.8 BOE3_n |
| bank | 1 | hub DN1 SS TX+ to LimeSDR | U102.3 USB_SSTXP_DN1 | HUB1_D1TX_P | C161(100n) -> J_LIME.9 SSTX+ | - | OK | B21 DIFFERS: MISMATCH HUB1_D1TX_P C161(100n) -> J_LIME.6 SSRX+ |
| bank | 1 | hub DN1 SS TX- | U102.4 USB_SSTXM_DN1 | HUB1_D1TX_N | C162(100n) -> J_LIME.8 SSTX- | - | OK | B21 DIFFERS: MISMATCH HUB1_D1TX_N C162(100n) -> J_LIME.5 SSRX- |
| bank | 1 | hub DN1 SS RX+ from LimeSDR | U102.6 USB_SSRXP_DN1 | LIME_SSRX_P | -> J_LIME.6 SSRX+ | - | OK | B21 DIFFERS: MISMATCH LIME_SSTX_P -> J_LIME.9 SSTX+ |
| bank | 1 | hub DN1 SS RX- | U102.7 USB_SSRXM_DN1 | LIME_SSRX_N | -> J_LIME.5 SSRX- | - | OK | B21 DIFFERS: MISMATCH LIME_SSTX_N -> J_LIME.8 SSTX- |
| hdmi-ctl | 0 | SEL2 (HDMI_SEL1) | U3.17 SEL2 | HDMI_SEL1 | -> J_PANEL.12 Pin_12; -> TP18.1 1 | R15 100k to GND | OK | B21 same: OK  |
| hdmi-ctl | 0 | SEL2 (HDMI_SEL2) | U4.17 SEL2 | HDMI_SEL2 | -> J_PANEL.13 Pin_13; -> TP19.1 1 | R16 100k to GND | OK | B21 same: OK  |
| hdmi-ctl | 0 | EN | U3.2 EN | HDMI_SW_EN | -> U3.16 SEL1; -> U4.16 SEL1; -> U4.2 EN | R14 10k to +3V3_DEV | n/a | B21 same: n/a  |
| hdmi-ctl | 0 | D0P common to J_HDMI | U4.5 D0P | HDMIO_D0_P | -> J_HDMI.7 D0+ | - | OK | B21 same: OK  |
| hdmi-ctl | 0 | SDA common | U4.4 SDA | HDMIO_SDA | -> J_HDMI.16 SDA | R18 2.2k to +5V_HDMI | OK | B21 same: OK  |
| hdmi-ctl | 0 | SCL common | U4.3 SCL | HDMIO_SCL | -> J_HDMI.15 SCL | R17 2.2k to +5V_HDMI | OK | B21 same: OK  |
| hdmi-ctl | 0 | HPD common | U4.14 HPD | HDMIO_HPD | R19(15k) -> J_HDMI.19 HPD | R20 22k to GND | OK | B21 same: OK  |
| ctrl | A | PA0 SEL1 | U41.22 PA0 | SEL1_A | -> TP514.1 1; -> U70.1 SEL1_A; -> U70.9 SEL1_A | R480 100k to GND | n/a | B21 DIFFERS: n/a SEL1_A -> U70.1 SEL1_A; -> U70.9 SEL1_A |
| ctrl | A | PA1 SEL2 | U41.23 PA1 | SEL2_A | -> TP517.1 1; -> U70.13 SEL2_A; -> U71.5 SEL2_A | R483 100k to GND | n/a | B21 DIFFERS: n/a SEL2_A -> U70.13 SEL2_A; -> U71.5 SEL2_A |
| ctrl | A | PA2 SEL3 | U41.24 PA2 | SEL3_A | -> TP520.1 1; -> U71.10 SEL3_A; -> U72.2 SEL3_A | R486 100k to GND | n/a | B21 DIFFERS: n/a SEL3_A -> U71.10 SEL3_A; -> U72.2 SEL3_A |
| ctrl | A | PA3 HUBRST1 | U41.25 PA3 | HUBRST1_A | -> TP523.1 1; -> U72.12 HUBRST1_A; -> U72.4 HUBRST1_A | R489 100k to GND | n/a | B21 DIFFERS: n/a HUBRST1_A -> U72.12 HUBRST1_A; -> U72.4 HUBRST1_A |
| ctrl | A | PA4 HUBRST2 | U41.28 PA4 | HUBRST2_A | -> TP526.1 1; -> U73.1 HUBRST2_A; -> U73.9 HUBRST2_A | R492 100k to GND | n/a | B21 DIFFERS: n/a HUBRST2_A -> U73.1 HUBRST2_A; -> U73.9 HUBRST2_A |
| ctrl | A | PA5 HUBRST3 | U41.29 PA5 | HUBRST3_A | -> TP529.1 1; -> U73.13 HUBRST3_A; -> U74.5 HUBRST3_A | R495 100k to GND | n/a | B21 DIFFERS: n/a HUBRST3_A -> U73.13 HUBRST3_A; -> U74.5 HUBRST3_A |
| ctrl | A | PE7 WSEC | U41.37 PE7 | WSEC_A | -> TP532.1 1; -> U74.10 WSEC_A; -> U75.2 WSEC_A | R498 100k to GND | n/a | B21 DIFFERS: n/a WSEC_A -> U74.10 WSEC_A; -> U75.2 WSEC_A |
| ctrl | A | PE8 read BSEL1 | U41.38 PE8 | BSEL1 | R474(10k) -> U80.2 BSEL1_D; -> TP504.1 1; -> U109.9 SEL; -> U110.9 S; -> U51.38 PE8; -> U61.38 PE8; -> U76.6 BSEL1; -> U80.1 BSEL1 | R160 100k to GND; C481 10n to GND | n/a | B21 DIFFERS: n/a BSEL1 R474(10k) -> U80.2 BSEL1_D; -> U109.9 SEL; -> U110.9 S; -> U51.38 PE8; -> U61.38 PE8; -> U76.6 BSEL1; -> U80.1 BSEL1 |
| ctrl | A | PE9 read BSEL2 | U41.39 PE9 | BSEL2 | R475(10k) -> U80.5 BSEL2_D; -> TP505.1 1; -> U209.9 SEL; -> U210.9 S; -> U51.39 PE9; -> U61.39 PE9; -> U76.11 BSEL2; -> U80.4 BSEL2 | R260 100k to GND; C482 10n to GND | n/a | B21 DIFFERS: n/a BSEL2 R475(10k) -> U80.5 BSEL2_D; -> U209.9 SEL; -> U210.9 S; -> U51.39 PE9; -> U61.39 PE9; -> U76.11 BSEL2; -> U80.4 BSEL2 |
| ctrl | A | PE10 read BSEL3 | U41.40 PE10 | BSEL3 | R476(10k) -> U80.9 BSEL3_D; -> TP506.1 1; -> U309.9 SEL; -> U310.9 S; -> U51.40 PE10; -> U61.40 PE10; -> U77.6 BSEL3; -> U80.10 BSEL3 | R360 100k to GND; C483 10n to GND | n/a | B21 DIFFERS: n/a BSEL3 R476(10k) -> U80.9 BSEL3_D; -> U309.9 SEL; -> U310.9 S; -> U51.40 PE10; -> U61.40 PE10; -> U77.6 BSEL3; -> U80.10 BSEL3 |
| ctrl | A | PE11 read WIFI_SEC | U41.41 PE11 | WIFI_SEC | -> Q10.1 G; -> TP510.1 1; -> U51.41 PE11; -> U61.41 PE11; -> U79.6 WIFI_SEC; -> U82.4 WIFI_SEC; -> U83.4 WIFI_SEC | - | n/a | B21 DIFFERS: n/a WIFI_SEC -> Q10.1 G; -> U51.41 PE11; -> U61.41 PE11; -> U79.6 WIFI_SEC; -> U82.4 WIFI_SEC; -> U83.4 WIFI_SEC |
| ctrl | A | PA6 HB1 | U41.30 PA6 | HB1 | -> J_PANEL.18 Pin_18; -> Q105.3 D; -> U51.30 PA6; -> U61.30 PA6 | R158 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | A | PA7 HB2 | U41.31 PA7 | HB2 | -> J_PANEL.19 Pin_19; -> Q205.3 D; -> U51.31 PA7; -> U61.31 PA7 | R258 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | A | PC4 HB3 | U41.32 PC4 | HB3 | -> J_PANEL.20 Pin_20; -> Q305.3 D; -> U51.32 PC4; -> U61.32 PC4 | R358 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | A | PD0 FDCAN1_RX | U41.81 PD0 | IOCA_CAN1_RX | -> U43.4 IOCA_CAN1_RX | - | n/a | B21 same: n/a  |
| ctrl | A | PD1 FDCAN1_TX | U41.82 PD1 | IOCA_CAN1_TX | -> U43.1 IOCA_CAN1_TX | - | n/a | B21 same: n/a  |
| ctrl | A | PB12 FDCAN2_RX | U41.51 PB12 | IOCA_CAN2_RX | -> U44.4 IOCA_CAN2_RX | - | n/a | B21 same: n/a  |
| ctrl | A | PB13 FDCAN2_TX | U41.52 PB13 | IOCA_CAN2_TX | -> U44.1 IOCA_CAN2_TX | - | n/a | B21 same: n/a  |
| ctrl | A | PB6 I2C1_SCL | U41.92 PB6 | SCL | -> J_AB1.12 Pin_12; -> J_PANEL.5 Pin_5; -> TP11.1 1; -> U1.101 SCL_MDC; -> U10.1 SCL; -> U5.3 SCL; -> U51.92 PB6; -> U6.22 SCL; -> U61.92 PB6; -> U7.22 SCL; -> U8.6 SCL; -> U9.8 SCL | R55 2.2k to +3V3_DEV | n/a | B21 DIFFERS: n/a unconnected-(U41-PB6-Pad92) - |
| ctrl | A | PB7 I2C1_SDA | U41.93 PB7 | SDA | -> J_AB1.11 Pin_11; -> J_PANEL.4 Pin_4; -> TP10.1 1; -> U1.98 SDI_SDA; -> U10.6 SDA; -> U5.4 SDAI; -> U5.5 SDAO; -> U51.93 PB7; -> U6.23 SDA; -> U61.93 PB7; -> U7.23 SDA; -> U8.5 SDA; -> U9.7 SDA | R54 2.2k to +3V3_DEV | n/a | B21 DIFFERS: n/a unconnected-(U41-PB7-Pad93) - |
| ctrl | B | PA0 SEL1 | U51.22 PA0 | SEL1_B | -> TP515.1 1; -> U70.2 SEL1_B; -> U70.4 SEL1_B | R481 100k to GND | n/a | B21 DIFFERS: n/a SEL1_B -> U70.2 SEL1_B; -> U70.4 SEL1_B |
| ctrl | B | PA1 SEL2 | U51.23 PA1 | SEL2_B | -> TP518.1 1; -> U70.12 SEL2_B; -> U71.1 SEL2_B | R484 100k to GND | n/a | B21 DIFFERS: n/a SEL2_B -> U70.12 SEL2_B; -> U71.1 SEL2_B |
| ctrl | B | PA2 SEL3 | U51.24 PA2 | SEL3_B | -> TP521.1 1; -> U71.13 SEL3_B; -> U71.9 SEL3_B | R487 100k to GND | n/a | B21 DIFFERS: n/a SEL3_B -> U71.13 SEL3_B; -> U71.9 SEL3_B |
| ctrl | B | PA3 HUBRST1 | U51.25 PA3 | HUBRST1_B | -> TP524.1 1; -> U72.10 HUBRST1_B; -> U72.5 HUBRST1_B | R490 100k to GND | n/a | B21 DIFFERS: n/a HUBRST1_B -> U72.10 HUBRST1_B; -> U72.5 HUBRST1_B |
| ctrl | B | PA4 HUBRST2 | U51.28 PA4 | HUBRST2_B | -> TP527.1 1; -> U73.2 HUBRST2_B; -> U73.4 HUBRST2_B | R493 100k to GND | n/a | B21 DIFFERS: n/a HUBRST2_B -> U73.2 HUBRST2_B; -> U73.4 HUBRST2_B |
| ctrl | B | PA5 HUBRST3 | U51.29 PA5 | HUBRST3_B | -> TP530.1 1; -> U73.12 HUBRST3_B; -> U74.1 HUBRST3_B | R496 100k to GND | n/a | B21 DIFFERS: n/a HUBRST3_B -> U73.12 HUBRST3_B; -> U74.1 HUBRST3_B |
| ctrl | B | PE7 WSEC | U51.37 PE7 | WSEC_B | -> TP533.1 1; -> U74.13 WSEC_B; -> U74.9 WSEC_B | R499 100k to GND | n/a | B21 DIFFERS: n/a WSEC_B -> U74.13 WSEC_B; -> U74.9 WSEC_B |
| ctrl | B | PE8 read BSEL1 | U51.38 PE8 | BSEL1 | R474(10k) -> U80.2 BSEL1_D; -> TP504.1 1; -> U109.9 SEL; -> U110.9 S; -> U41.38 PE8; -> U61.38 PE8; -> U76.6 BSEL1; -> U80.1 BSEL1 | R160 100k to GND; C481 10n to GND | n/a | B21 DIFFERS: n/a BSEL1 R474(10k) -> U80.2 BSEL1_D; -> U109.9 SEL; -> U110.9 S; -> U41.38 PE8; -> U61.38 PE8; -> U76.6 BSEL1; -> U80.1 BSEL1 |
| ctrl | B | PE9 read BSEL2 | U51.39 PE9 | BSEL2 | R475(10k) -> U80.5 BSEL2_D; -> TP505.1 1; -> U209.9 SEL; -> U210.9 S; -> U41.39 PE9; -> U61.39 PE9; -> U76.11 BSEL2; -> U80.4 BSEL2 | R260 100k to GND; C482 10n to GND | n/a | B21 DIFFERS: n/a BSEL2 R475(10k) -> U80.5 BSEL2_D; -> U209.9 SEL; -> U210.9 S; -> U41.39 PE9; -> U61.39 PE9; -> U76.11 BSEL2; -> U80.4 BSEL2 |
| ctrl | B | PE10 read BSEL3 | U51.40 PE10 | BSEL3 | R476(10k) -> U80.9 BSEL3_D; -> TP506.1 1; -> U309.9 SEL; -> U310.9 S; -> U41.40 PE10; -> U61.40 PE10; -> U77.6 BSEL3; -> U80.10 BSEL3 | R360 100k to GND; C483 10n to GND | n/a | B21 DIFFERS: n/a BSEL3 R476(10k) -> U80.9 BSEL3_D; -> U309.9 SEL; -> U310.9 S; -> U41.40 PE10; -> U61.40 PE10; -> U77.6 BSEL3; -> U80.10 BSEL3 |
| ctrl | B | PE11 read WIFI_SEC | U51.41 PE11 | WIFI_SEC | -> Q10.1 G; -> TP510.1 1; -> U41.41 PE11; -> U61.41 PE11; -> U79.6 WIFI_SEC; -> U82.4 WIFI_SEC; -> U83.4 WIFI_SEC | - | n/a | B21 DIFFERS: n/a WIFI_SEC -> Q10.1 G; -> U41.41 PE11; -> U61.41 PE11; -> U79.6 WIFI_SEC; -> U82.4 WIFI_SEC; -> U83.4 WIFI_SEC |
| ctrl | B | PA6 HB1 | U51.30 PA6 | HB1 | -> J_PANEL.18 Pin_18; -> Q105.3 D; -> U41.30 PA6; -> U61.30 PA6 | R158 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | B | PA7 HB2 | U51.31 PA7 | HB2 | -> J_PANEL.19 Pin_19; -> Q205.3 D; -> U41.31 PA7; -> U61.31 PA7 | R258 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | B | PC4 HB3 | U51.32 PC4 | HB3 | -> J_PANEL.20 Pin_20; -> Q305.3 D; -> U41.32 PC4; -> U61.32 PC4 | R358 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | B | PD0 FDCAN1_RX | U51.81 PD0 | IOCB_CAN1_RX | -> U53.4 IOCB_CAN1_RX | - | n/a | B21 same: n/a  |
| ctrl | B | PD1 FDCAN1_TX | U51.82 PD1 | IOCB_CAN1_TX | -> U53.1 IOCB_CAN1_TX | - | n/a | B21 same: n/a  |
| ctrl | B | PB12 FDCAN2_RX | U51.51 PB12 | IOCB_CAN2_RX | -> U54.4 IOCB_CAN2_RX | - | n/a | B21 same: n/a  |
| ctrl | B | PB13 FDCAN2_TX | U51.52 PB13 | IOCB_CAN2_TX | -> U54.1 IOCB_CAN2_TX | - | n/a | B21 same: n/a  |
| ctrl | B | PB6 I2C1_SCL | U51.92 PB6 | SCL | -> J_AB1.12 Pin_12; -> J_PANEL.5 Pin_5; -> TP11.1 1; -> U1.101 SCL_MDC; -> U10.1 SCL; -> U41.92 PB6; -> U5.3 SCL; -> U6.22 SCL; -> U61.92 PB6; -> U7.22 SCL; -> U8.6 SCL; -> U9.8 SCL | R55 2.2k to +3V3_DEV | n/a | B21 DIFFERS: n/a unconnected-(U51-PB6-Pad92) - |
| ctrl | B | PB7 I2C1_SDA | U51.93 PB7 | SDA | -> J_AB1.11 Pin_11; -> J_PANEL.4 Pin_4; -> TP10.1 1; -> U1.98 SDI_SDA; -> U10.6 SDA; -> U41.93 PB7; -> U5.4 SDAI; -> U5.5 SDAO; -> U6.23 SDA; -> U61.93 PB7; -> U7.23 SDA; -> U8.5 SDA; -> U9.7 SDA | R54 2.2k to +3V3_DEV | n/a | B21 DIFFERS: n/a unconnected-(U51-PB7-Pad93) - |
| ctrl | C | PA0 SEL1 | U61.22 PA0 | SEL1_C | -> TP516.1 1; -> U70.10 SEL1_C; -> U70.5 SEL1_C | R482 100k to GND | n/a | B21 DIFFERS: n/a SEL1_C -> U70.10 SEL1_C; -> U70.5 SEL1_C |
| ctrl | C | PA1 SEL2 | U61.23 PA1 | SEL2_C | -> TP519.1 1; -> U71.2 SEL2_C; -> U71.4 SEL2_C | R485 100k to GND | n/a | B21 DIFFERS: n/a SEL2_C -> U71.2 SEL2_C; -> U71.4 SEL2_C |
| ctrl | C | PA2 SEL3 | U61.24 PA2 | SEL3_C | -> TP522.1 1; -> U71.12 SEL3_C; -> U72.1 SEL3_C | R488 100k to GND | n/a | B21 DIFFERS: n/a SEL3_C -> U71.12 SEL3_C; -> U72.1 SEL3_C |
| ctrl | C | PA3 HUBRST1 | U61.25 PA3 | HUBRST1_C | -> TP525.1 1; -> U72.13 HUBRST1_C; -> U72.9 HUBRST1_C | R491 100k to GND | n/a | B21 DIFFERS: n/a HUBRST1_C -> U72.13 HUBRST1_C; -> U72.9 HUBRST1_C |
| ctrl | C | PA4 HUBRST2 | U61.28 PA4 | HUBRST2_C | -> TP528.1 1; -> U73.10 HUBRST2_C; -> U73.5 HUBRST2_C | R494 100k to GND | n/a | B21 DIFFERS: n/a HUBRST2_C -> U73.10 HUBRST2_C; -> U73.5 HUBRST2_C |
| ctrl | C | PA5 HUBRST3 | U61.29 PA5 | HUBRST3_C | -> TP531.1 1; -> U74.2 HUBRST3_C; -> U74.4 HUBRST3_C | R497 100k to GND | n/a | B21 DIFFERS: n/a HUBRST3_C -> U74.2 HUBRST3_C; -> U74.4 HUBRST3_C |
| ctrl | C | PE7 WSEC | U61.37 PE7 | WSEC_C | -> TP534.1 1; -> U74.12 WSEC_C; -> U75.1 WSEC_C | R500 100k to GND | n/a | B21 DIFFERS: n/a WSEC_C -> U74.12 WSEC_C; -> U75.1 WSEC_C |
| ctrl | C | PE8 read BSEL1 | U61.38 PE8 | BSEL1 | R474(10k) -> U80.2 BSEL1_D; -> TP504.1 1; -> U109.9 SEL; -> U110.9 S; -> U41.38 PE8; -> U51.38 PE8; -> U76.6 BSEL1; -> U80.1 BSEL1 | R160 100k to GND; C481 10n to GND | n/a | B21 DIFFERS: n/a BSEL1 R474(10k) -> U80.2 BSEL1_D; -> U109.9 SEL; -> U110.9 S; -> U41.38 PE8; -> U51.38 PE8; -> U76.6 BSEL1; -> U80.1 BSEL1 |
| ctrl | C | PE9 read BSEL2 | U61.39 PE9 | BSEL2 | R475(10k) -> U80.5 BSEL2_D; -> TP505.1 1; -> U209.9 SEL; -> U210.9 S; -> U41.39 PE9; -> U51.39 PE9; -> U76.11 BSEL2; -> U80.4 BSEL2 | R260 100k to GND; C482 10n to GND | n/a | B21 DIFFERS: n/a BSEL2 R475(10k) -> U80.5 BSEL2_D; -> U209.9 SEL; -> U210.9 S; -> U41.39 PE9; -> U51.39 PE9; -> U76.11 BSEL2; -> U80.4 BSEL2 |
| ctrl | C | PE10 read BSEL3 | U61.40 PE10 | BSEL3 | R476(10k) -> U80.9 BSEL3_D; -> TP506.1 1; -> U309.9 SEL; -> U310.9 S; -> U41.40 PE10; -> U51.40 PE10; -> U77.6 BSEL3; -> U80.10 BSEL3 | R360 100k to GND; C483 10n to GND | n/a | B21 DIFFERS: n/a BSEL3 R476(10k) -> U80.9 BSEL3_D; -> U309.9 SEL; -> U310.9 S; -> U41.40 PE10; -> U51.40 PE10; -> U77.6 BSEL3; -> U80.10 BSEL3 |
| ctrl | C | PE11 read WIFI_SEC | U61.41 PE11 | WIFI_SEC | -> Q10.1 G; -> TP510.1 1; -> U41.41 PE11; -> U51.41 PE11; -> U79.6 WIFI_SEC; -> U82.4 WIFI_SEC; -> U83.4 WIFI_SEC | - | n/a | B21 DIFFERS: n/a WIFI_SEC -> Q10.1 G; -> U41.41 PE11; -> U51.41 PE11; -> U79.6 WIFI_SEC; -> U82.4 WIFI_SEC; -> U83.4 WIFI_SEC |
| ctrl | C | PA6 HB1 | U61.30 PA6 | HB1 | -> J_PANEL.18 Pin_18; -> Q105.3 D; -> U41.30 PA6; -> U51.30 PA6 | R158 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | C | PA7 HB2 | U61.31 PA7 | HB2 | -> J_PANEL.19 Pin_19; -> Q205.3 D; -> U41.31 PA7; -> U51.31 PA7 | R258 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | C | PC4 HB3 | U61.32 PC4 | HB3 | -> J_PANEL.20 Pin_20; -> Q305.3 D; -> U41.32 PC4; -> U51.32 PC4 | R358 10k to +3V3_DEV | n/a | B21 same: n/a  |
| ctrl | C | PD0 FDCAN1_RX | U61.81 PD0 | IOCC_CAN1_RX | -> U63.4 IOCC_CAN1_RX | - | n/a | B21 same: n/a  |
| ctrl | C | PD1 FDCAN1_TX | U61.82 PD1 | IOCC_CAN1_TX | -> U63.1 IOCC_CAN1_TX | - | n/a | B21 same: n/a  |
| ctrl | C | PB12 FDCAN2_RX | U61.51 PB12 | IOCC_CAN2_RX | -> U64.4 IOCC_CAN2_RX | - | n/a | B21 same: n/a  |
| ctrl | C | PB13 FDCAN2_TX | U61.52 PB13 | IOCC_CAN2_TX | -> U64.1 IOCC_CAN2_TX | - | n/a | B21 same: n/a  |
| ctrl | C | PB6 I2C1_SCL | U61.92 PB6 | SCL | -> J_AB1.12 Pin_12; -> J_PANEL.5 Pin_5; -> TP11.1 1; -> U1.101 SCL_MDC; -> U10.1 SCL; -> U41.92 PB6; -> U5.3 SCL; -> U51.92 PB6; -> U6.22 SCL; -> U7.22 SCL; -> U8.6 SCL; -> U9.8 SCL | R55 2.2k to +3V3_DEV | n/a | B21 DIFFERS: n/a unconnected-(U61-PB6-Pad92) - |
| ctrl | C | PB7 I2C1_SDA | U61.93 PB7 | SDA | -> J_AB1.11 Pin_11; -> J_PANEL.4 Pin_4; -> TP10.1 1; -> U1.98 SDI_SDA; -> U10.6 SDA; -> U41.93 PB7; -> U5.4 SDAI; -> U5.5 SDAO; -> U51.93 PB7; -> U6.23 SDA; -> U7.23 SDA; -> U8.5 SDA; -> U9.7 SDA | R54 2.2k to +3V3_DEV | n/a | B21 DIFFERS: n/a unconnected-(U61-PB7-Pad93) - |
| can | U43 | TCAN334 pin 5 | U43.5 NC | unconnected-(U43-NC-Pad5) | - | - | n/a | B21 same: n/a  |
| can | U43 | TCAN334 pin 6 | U43.6 CANL_A1 | CANL_A1 | R471(60R4 1%) + R470(60R4 1%) + R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> TP535.1 1; R471(60R4 1%) + R470(60R4 1%) + R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U53.7 CANH_A; R471(60R4 1%) + R470(60R4 1%) + R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U63.7 CANH_A; R471(60R4 1%) + R470(60R4 1%) -> U43.7 CANH_A1; R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> TP536.1 1; R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U53.6 CANL_A; R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U63.6 CANL_A | C460 4.7n to GND; C506 4.7n to GND | n/a | B21 DIFFERS: n/a CANL_A R471(60R4 1%) + R470(60R4 1%) + R504(60R4 1%) + R505(60R4 1%) -> U53.6 CANL_A; R471(60R4 1%) + R470(60R4 1%) + R504(60R4 1%) + R505(60R4 1%) -> U63.6 CANL_A; R471(60R4 1%) + R470(60R4 1%) -> U43.7 CANH_A; R471(60R4 1%) + R470(60R4 1%) -> U53.7 CANH_A; R471(60R4 1%) + R470(60R4 1%) -> U63.7 CANH_A |
| can | U43 | TCAN334 pin 7 | U43.7 CANH_A1 | CANH_A1 | R470(60R4 1%) + R471(60R4 1%) + R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> TP536.1 1; R470(60R4 1%) + R471(60R4 1%) + R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U53.6 CANL_A; R470(60R4 1%) + R471(60R4 1%) + R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U63.6 CANL_A; R470(60R4 1%) + R471(60R4 1%) -> U43.6 CANL_A1; R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> TP535.1 1; R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U53.7 CANH_A; R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U63.7 CANH_A | C460 4.7n to GND; C506 4.7n to GND | n/a | B21 DIFFERS: n/a CANH_A R470(60R4 1%) + R471(60R4 1%) + R505(60R4 1%) + R504(60R4 1%) -> U53.7 CANH_A; R470(60R4 1%) + R471(60R4 1%) + R505(60R4 1%) + R504(60R4 1%) -> U63.7 CANH_A; R470(60R4 1%) + R471(60R4 1%) -> U43.6 CANL_A; R470(60R4 1%) + R471(60R4 1%) -> U53.6 CANL_A; R470(60R4 1%) + R471(60R4 1%) -> U63.6 CANL_A |
| can | U43 | TCAN334 pin 8 | U43.8 GND | GND | (rail GND) | - | n/a | B21 same: n/a  |
| can | U44 | TCAN334 pin 5 | U44.5 NC | unconnected-(U44-NC-Pad5) | - | - | n/a | B21 same: n/a  |
| can | U44 | TCAN334 pin 6 | U44.6 CANL_B1 | CANL_B1 | R473(60R4 1%) + R472(60R4 1%) + R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> TP537.1 1; R473(60R4 1%) + R472(60R4 1%) + R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U54.7 CANH_B; R473(60R4 1%) + R472(60R4 1%) + R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U64.7 CANH_B; R473(60R4 1%) + R472(60R4 1%) -> U44.7 CANH_B1; R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> TP538.1 1; R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U54.6 CANL_B; R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U64.6 CANL_B | C461 4.7n to GND; C507 4.7n to GND | n/a | B21 DIFFERS: n/a CANL_B R473(60R4 1%) + R472(60R4 1%) + R506(60R4 1%) + R507(60R4 1%) -> U54.6 CANL_B; R473(60R4 1%) + R472(60R4 1%) + R506(60R4 1%) + R507(60R4 1%) -> U64.6 CANL_B; R473(60R4 1%) + R472(60R4 1%) -> U44.7 CANH_B; R473(60R4 1%) + R472(60R4 1%) -> U54.7 CANH_B; R473(60R4 1%) + R472(60R4 1%) -> U64.7 CANH_B |
| can | U44 | TCAN334 pin 7 | U44.7 CANH_B1 | CANH_B1 | R472(60R4 1%) + R473(60R4 1%) + R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> TP538.1 1; R472(60R4 1%) + R473(60R4 1%) + R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U54.6 CANL_B; R472(60R4 1%) + R473(60R4 1%) + R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U64.6 CANL_B; R472(60R4 1%) + R473(60R4 1%) -> U44.6 CANL_B1; R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> TP537.1 1; R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U54.7 CANH_B; R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U64.7 CANH_B | C461 4.7n to GND; C507 4.7n to GND | n/a | B21 DIFFERS: n/a CANH_B R472(60R4 1%) + R473(60R4 1%) + R507(60R4 1%) + R506(60R4 1%) -> U54.7 CANH_B; R472(60R4 1%) + R473(60R4 1%) + R507(60R4 1%) + R506(60R4 1%) -> U64.7 CANH_B; R472(60R4 1%) + R473(60R4 1%) -> U44.6 CANL_B; R472(60R4 1%) + R473(60R4 1%) -> U54.6 CANL_B; R472(60R4 1%) + R473(60R4 1%) -> U64.6 CANL_B |
| can | U44 | TCAN334 pin 8 | U44.8 GND | GND | (rail GND) | - | n/a | B21 same: n/a  |
| can | U53 | TCAN334 pin 5 | U53.5 NC | unconnected-(U53-NC-Pad5) | - | - | n/a | B21 same: n/a  |
| can | U53 | TCAN334 pin 6 | U53.6 CANL_A | CANL_A | R505(60R4 1%) + R504(60R4 1%) + R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U43.7 CANH_A1; R505(60R4 1%) + R504(60R4 1%) -> TP535.1 1; R505(60R4 1%) + R504(60R4 1%) -> U53.7 CANH_A; R505(60R4 1%) + R504(60R4 1%) -> U63.7 CANH_A; R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U43.6 CANL_A1; -> TP536.1 1; -> U63.6 CANL_A | C506 4.7n to GND; C460 4.7n to GND | n/a | B21 DIFFERS: n/a CANL_A R471(60R4 1%) + R470(60R4 1%) + R504(60R4 1%) + R505(60R4 1%) -> U43.6 CANL_A; R471(60R4 1%) + R470(60R4 1%) + R504(60R4 1%) + R505(60R4 1%) -> U63.6 CANL_A; R471(60R4 1%) + R470(60R4 1%) -> U43.7 CANH_A; R471(60R4 1%) + R470(60R4 1%) -> U53.7 CANH_A; R471(60R4 1%) + R470(60R4 1%) -> U63.7 CANH_A |
| can | U53 | TCAN334 pin 7 | U53.7 CANH_A | CANH_A | R504(60R4 1%) + R505(60R4 1%) + R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U43.6 CANL_A1; R504(60R4 1%) + R505(60R4 1%) -> TP536.1 1; R504(60R4 1%) + R505(60R4 1%) -> U53.6 CANL_A; R504(60R4 1%) + R505(60R4 1%) -> U63.6 CANL_A; R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U43.7 CANH_A1; -> TP535.1 1; -> U63.7 CANH_A | C506 4.7n to GND; C460 4.7n to GND | n/a | B21 DIFFERS: n/a CANH_A R470(60R4 1%) + R471(60R4 1%) + R505(60R4 1%) + R504(60R4 1%) -> U43.7 CANH_A; R470(60R4 1%) + R471(60R4 1%) + R505(60R4 1%) + R504(60R4 1%) -> U63.7 CANH_A; R470(60R4 1%) + R471(60R4 1%) -> U43.6 CANL_A; R470(60R4 1%) + R471(60R4 1%) -> U53.6 CANL_A; R470(60R4 1%) + R471(60R4 1%) -> U63.6 CANL_A |
| can | U53 | TCAN334 pin 8 | U53.8 GND | GND | (rail GND) | - | n/a | B21 same: n/a  |
| can | U54 | TCAN334 pin 5 | U54.5 NC | unconnected-(U54-NC-Pad5) | - | - | n/a | B21 same: n/a  |
| can | U54 | TCAN334 pin 6 | U54.6 CANL_B | CANL_B | R507(60R4 1%) + R506(60R4 1%) + R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U44.7 CANH_B1; R507(60R4 1%) + R506(60R4 1%) -> TP537.1 1; R507(60R4 1%) + R506(60R4 1%) -> U54.7 CANH_B; R507(60R4 1%) + R506(60R4 1%) -> U64.7 CANH_B; R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U44.6 CANL_B1; -> TP538.1 1; -> U64.6 CANL_B | C507 4.7n to GND; C461 4.7n to GND | n/a | B21 DIFFERS: n/a CANL_B R473(60R4 1%) + R472(60R4 1%) + R506(60R4 1%) + R507(60R4 1%) -> U44.6 CANL_B; R473(60R4 1%) + R472(60R4 1%) + R506(60R4 1%) + R507(60R4 1%) -> U64.6 CANL_B; R473(60R4 1%) + R472(60R4 1%) -> U44.7 CANH_B; R473(60R4 1%) + R472(60R4 1%) -> U54.7 CANH_B; R473(60R4 1%) + R472(60R4 1%) -> U64.7 CANH_B |
| can | U54 | TCAN334 pin 7 | U54.7 CANH_B | CANH_B | R506(60R4 1%) + R507(60R4 1%) + R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U44.6 CANL_B1; R506(60R4 1%) + R507(60R4 1%) -> TP538.1 1; R506(60R4 1%) + R507(60R4 1%) -> U54.6 CANL_B; R506(60R4 1%) + R507(60R4 1%) -> U64.6 CANL_B; R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U44.7 CANH_B1; -> TP537.1 1; -> U64.7 CANH_B | C507 4.7n to GND; C461 4.7n to GND | n/a | B21 DIFFERS: n/a CANH_B R472(60R4 1%) + R473(60R4 1%) + R507(60R4 1%) + R506(60R4 1%) -> U44.7 CANH_B; R472(60R4 1%) + R473(60R4 1%) + R507(60R4 1%) + R506(60R4 1%) -> U64.7 CANH_B; R472(60R4 1%) + R473(60R4 1%) -> U44.6 CANL_B; R472(60R4 1%) + R473(60R4 1%) -> U54.6 CANL_B; R472(60R4 1%) + R473(60R4 1%) -> U64.6 CANL_B |
| can | U54 | TCAN334 pin 8 | U54.8 GND | GND | (rail GND) | - | n/a | B21 same: n/a  |
| can | U63 | TCAN334 pin 5 | U63.5 NC | unconnected-(U63-NC-Pad5) | - | - | n/a | B21 same: n/a  |
| can | U63 | TCAN334 pin 6 | U63.6 CANL_A | CANL_A | R505(60R4 1%) + R504(60R4 1%) + R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U43.7 CANH_A1; R505(60R4 1%) + R504(60R4 1%) -> TP535.1 1; R505(60R4 1%) + R504(60R4 1%) -> U53.7 CANH_A; R505(60R4 1%) + R504(60R4 1%) -> U63.7 CANH_A; R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U43.6 CANL_A1; -> TP536.1 1; -> U53.6 CANL_A | C506 4.7n to GND; C460 4.7n to GND | n/a | B21 DIFFERS: n/a CANL_A R471(60R4 1%) + R470(60R4 1%) + R504(60R4 1%) + R505(60R4 1%) -> U43.6 CANL_A; R471(60R4 1%) + R470(60R4 1%) + R504(60R4 1%) + R505(60R4 1%) -> U53.6 CANL_A; R471(60R4 1%) + R470(60R4 1%) -> U43.7 CANH_A; R471(60R4 1%) + R470(60R4 1%) -> U53.7 CANH_A; R471(60R4 1%) + R470(60R4 1%) -> U63.7 CANH_A |
| can | U63 | TCAN334 pin 7 | U63.7 CANH_A | CANH_A | R504(60R4 1%) + R505(60R4 1%) + R509(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U43.6 CANL_A1; R504(60R4 1%) + R505(60R4 1%) -> TP536.1 1; R504(60R4 1%) + R505(60R4 1%) -> U53.6 CANL_A; R504(60R4 1%) + R505(60R4 1%) -> U63.6 CANL_A; R508(0R (break link: remove to cut fabric A between controller A and B/C, IOHA A7)) -> U43.7 CANH_A1; -> TP535.1 1; -> U53.7 CANH_A | C506 4.7n to GND; C460 4.7n to GND | n/a | B21 DIFFERS: n/a CANH_A R470(60R4 1%) + R471(60R4 1%) + R505(60R4 1%) + R504(60R4 1%) -> U43.7 CANH_A; R470(60R4 1%) + R471(60R4 1%) + R505(60R4 1%) + R504(60R4 1%) -> U53.7 CANH_A; R470(60R4 1%) + R471(60R4 1%) -> U43.6 CANL_A; R470(60R4 1%) + R471(60R4 1%) -> U53.6 CANL_A; R470(60R4 1%) + R471(60R4 1%) -> U63.6 CANL_A |
| can | U63 | TCAN334 pin 8 | U63.8 GND | GND | (rail GND) | - | n/a | B21 same: n/a  |
| can | U64 | TCAN334 pin 5 | U64.5 NC | unconnected-(U64-NC-Pad5) | - | - | n/a | B21 same: n/a  |
| can | U64 | TCAN334 pin 6 | U64.6 CANL_B | CANL_B | R507(60R4 1%) + R506(60R4 1%) + R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U44.7 CANH_B1; R507(60R4 1%) + R506(60R4 1%) -> TP537.1 1; R507(60R4 1%) + R506(60R4 1%) -> U54.7 CANH_B; R507(60R4 1%) + R506(60R4 1%) -> U64.7 CANH_B; R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U44.6 CANL_B1; -> TP538.1 1; -> U54.6 CANL_B | C507 4.7n to GND; C461 4.7n to GND | n/a | B21 DIFFERS: n/a CANL_B R473(60R4 1%) + R472(60R4 1%) + R506(60R4 1%) + R507(60R4 1%) -> U44.6 CANL_B; R473(60R4 1%) + R472(60R4 1%) + R506(60R4 1%) + R507(60R4 1%) -> U54.6 CANL_B; R473(60R4 1%) + R472(60R4 1%) -> U44.7 CANH_B; R473(60R4 1%) + R472(60R4 1%) -> U54.7 CANH_B; R473(60R4 1%) + R472(60R4 1%) -> U64.7 CANH_B |
| can | U64 | TCAN334 pin 7 | U64.7 CANH_B | CANH_B | R506(60R4 1%) + R507(60R4 1%) + R512(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U44.6 CANL_B1; R506(60R4 1%) + R507(60R4 1%) -> TP538.1 1; R506(60R4 1%) + R507(60R4 1%) -> U54.6 CANL_B; R506(60R4 1%) + R507(60R4 1%) -> U64.6 CANL_B; R511(0R (break link: remove to cut fabric B between controller A and B/C, IOHA A7)) -> U44.7 CANH_B1; -> TP537.1 1; -> U54.7 CANH_B | C507 4.7n to GND; C461 4.7n to GND | n/a | B21 DIFFERS: n/a CANH_B R472(60R4 1%) + R473(60R4 1%) + R507(60R4 1%) + R506(60R4 1%) -> U44.7 CANH_B; R472(60R4 1%) + R473(60R4 1%) + R507(60R4 1%) + R506(60R4 1%) -> U54.7 CANH_B; R472(60R4 1%) + R473(60R4 1%) -> U44.6 CANL_B; R472(60R4 1%) + R473(60R4 1%) -> U54.6 CANL_B; R472(60R4 1%) + R473(60R4 1%) -> U64.6 CANL_B |
| can | U64 | TCAN334 pin 8 | U64.8 GND | GND | (rail GND) | - | n/a | B21 same: n/a  |
