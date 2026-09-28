## Board A

- `e3aedb25` (as first written): netlist 7b08510106687b3d; intent 83ba5e43a6fbcccb; 30 row(s)
- `ef144760` (the H2 line): netlist da05dc02bc1e612f; intent 92dd3b1cda9046b8; 34 row(s)
- `760d7f41` (set 6): netlist 0a2b59087bcc2678; intent 3422910a15c4d145; 34 row(s)

From `e3aedb25` to `ef144760` (the H2 line): 4 new, 0 gone, 1 moved, 29 the same.
  - NEW   PRECHG | 14.4 (16.8) | 0.00 / 1.68 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 3 / 2 / 2
  - NEW   VMON | 14.4 (16.8) | 0.69 / 1.00 | 0.69, typical (PI-001) | 0.18 | 0.07 | 1.08 | 2 / 2 / 1
  - NEW   +3V3_EMCON_EF | 3.30 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   +3V3_EMCON | 3.30 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - MOVED VIN_RAW
      typ / peak A: 12.31 / 12.31 -> 14.10 / 14.10
      governing A: 12.31, typical (PI-001) -> 14.10, typical (PI-001)
      outer mm: 11.92 -> 15.29
      two outer faces, each mm: 3.68 -> 4.43
      inner mm: 97.66 (over 40 mm) -> 125.22 (over 40 mm)
      barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill: 17 / 14 / 12 -> 20 / 16 / 14

From `ef144760` to `760d7f41` (set 6): 0 new, 0 gone, 0 moved, 34 the same.

## Board B

- `e3aedb25` (as first written): netlist 669d02d07aeaae4b; intent cf461c0b75ce368b; 41 row(s)
- `ef144760` (the H2 line): netlist 8b78c59754a6a0c7; intent 162fcb9b95f680a7; 58 row(s)
- `760d7f41` (set 6): netlist 028997a6c5e8810f; intent 96ee391b3e3f638d; 58 row(s)

From `e3aedb25` to `ef144760` (the H2 line): 17 new, 0 gone, 0 moved, 41 the same.
  - NEW   VBUS_FLASH1 | 5.00 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   SIM1_VCC | 3.00 | 0.01 / 0.05 | 0.01, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   SIM2_VCC | 3.00 | 0.01 / 0.05 | 0.01, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   SIMC2_VCC | 3.00 | 0.01 / 0.05 | 0.01, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   VBUS_FLASH2 | 5.00 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   VBUS_FLASH3 | 5.00 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   VBAT_RTC | 3.00 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   POE_P | 54.00 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1
  - NEW   MDI_A_P | 54.00 | 0.15 / 0.30 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1
  - NEW   MDI_A_N | 54.00 | 0.15 / 0.30 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1
  - NEW   MDI_B_P (return of +54V_POE) | 0.15 | 0.15 / 0.30 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1
  - NEW   MDI_B_N (return of +54V_POE) | 0.15 | 0.15 / 0.30 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1
  - NEW   POE_DRAIN (return of +54V_POE) | 0.15 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1
  - NEW   POE_SEN (return of +54V_POE) | 0.15 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1
  - NEW   GNSS_VDD_RF | 3.30 | 0.02 / 0.03 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1
  - NEW   GNSS_BIAS | 3.30 | 0.02 / 0.03 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1
  - NEW   GNSS_ANT | 3.30 | 0.02 / 0.03 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1

From `ef144760` to `760d7f41` (set 6): 0 new, 0 gone, 0 moved, 58 the same.

## Board C

- `e3aedb25` (as first written): netlist 2834f0d8c4071d56; intent 5c8d991e3805016a; 2 row(s)
- `ef144760` (the H2 line): netlist 11eabc2dddca5161; intent 854436c729322993; 2 row(s)
- `760d7f41` (set 6): netlist 3fddbb3edcd4248a; intent 270ebb4ccf1d0e8e; 5 row(s)

From `e3aedb25` to `ef144760` (the H2 line): 0 new, 0 gone, 0 moved, 2 the same.

From `ef144760` to `760d7f41` (set 6): 3 new, 0 gone, 1 moved, 1 the same.
  - NEW   EPD_VCC | 3.30 | 0.03 / 0.52 | 0.03, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1
  - NEW   LED_RAIL_SW | 5.00 | 0.16 / 0.46 | 0.16, typical (PI-001) | 0.02 | 0.01 | 0.14 | 1 / 1 / 1
  - NEW   LED_RAIL | 5.00 | 0.14 / 0.44 | 0.14, typical (PI-001) | 0.02 | 0.01 | 0.12 | 1 / 1 / 1
  - MOVED +3V3
      typ / peak A: 0.12 / 0.20 -> 0.15 / 0.72
      governing A: 0.12, typical (PI-001) -> 0.15, typical (PI-001)
      inner mm: 0.10 -> 0.13

## Board D

- `e3aedb25` (as first written): netlist f13d8b70099ab03e; intent 59591c54eb29ab64; 5 row(s)
- `ef144760` (the H2 line): netlist 76700a687eb6187f; intent 443fd745879d3022; 6 row(s)
- `760d7f41` (set 6): netlist 7a2c0ac2190b141a; intent 8d9f3b2256521b0d; 6 row(s)

From `e3aedb25` to `ef144760` (the H2 line): 1 new, 0 gone, 0 moved, 5 the same.
  - NEW   +5V_TX | 5.0 (5.2) | 0.37 / 1.15 | 0.37, typical (PI-001) | 0.08 | 0.03 | 0.46 | 2 / 2 / 2

From `ef144760` to `760d7f41` (set 6): 0 new, 0 gone, 0 moved, 6 the same.

## Board E

- `e3aedb25` (as first written): netlist d910e49c5f5f50b2; intent 9ae33eb17d04670e; 14 row(s)
- `ef144760` (the H2 line): netlist d6137f50059e5cbc; intent 5913e38b20333d35; 15 row(s)
- `760d7f41` (set 6): netlist 56adc9746d61c4e0; intent dad1163afd720b5e; 15 row(s)

From `e3aedb25` to `ef144760` (the H2 line): 1 new, 0 gone, 2 moved, 12 the same.
  - NEW   SGP_VDD | 3.30 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - MOVED VIN_RAW
      typ / peak A: 6.15 / 6.15 -> 14.10 / 14.10
      governing A: 6.15, typical (PI-001) -> 14.10, typical (PI-001)
      outer mm: 3.67 -> 15.29
      two outer faces, each mm: 1.41 -> 4.43
      inner mm: 27.42 -> 125.22 (over 40 mm)
      barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill: 9 / 7 / 6 -> 20 / 16 / 14
  - MOVED TRK_OUT
      typ / peak A: 6.16 / 6.16 -> 10.33 / 10.33
      governing A: 6.16, typical (PI-001) -> 10.33, typical (PI-001)
      outer mm: 3.68 -> 8.65
      two outer faces, each mm: 1.42 -> 2.89
      inner mm: 27.50 -> 70.84 (over 40 mm)
      barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill: 9 / 7 / 6 -> 14 / 12 / 10

From `ef144760` to `760d7f41` (set 6): 0 new, 0 gone, 0 moved, 15 the same.

## Board E5

- `e3aedb25` (as first written): board_file 686b29a734c55b9a; chain 935e524eed0ee4d1; 2 row(s)
- `ef144760` (the H2 line): board_file 686b29a734c55b9a; chain a09ca0293afd1f7c; 2 row(s)
- `760d7f41` (set 6): board_file 686b29a734c55b9a; chain a09ca0293afd1f7c; 2 row(s)

From `e3aedb25` to `ef144760` (the H2 line): 0 new, 0 gone, 0 moved, 2 the same.

From `ef144760` to `760d7f41` (set 6): 0 new, 0 gone, 0 moved, 2 the same.

## Board P

- `e3aedb25` (as first written): netlist 4342c4cbe1b43dc4; intent 59d679f0859fc203; 5 row(s)
- `ef144760` (the H2 line): netlist 085f833362fbbda8; intent 6ff1b8129a5c5aff; 5 row(s)
- `760d7f41` (set 6): netlist 760ac6f74d62d194; intent 12f92bd3ce7a8264; 10 row(s)

From `e3aedb25` to `ef144760` (the H2 line): 0 new, 0 gone, 0 moved, 5 the same.

From `ef144760` to `760d7f41` (set 6): 5 new, 0 gone, 0 moved, 5 the same.
  - NEW   BAT_F | 14.4 (16.8) | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   VCC_F | 14.4 (16.8) | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   SEC_VDD | 14.4 (16.8) | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1
  - NEW   SW | 14.4 (16.8) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s, series of SCP_OUT | 11.95 | 3.36 | 195.80 (over 40 mm) | 25 / 21 / 18
  - NEW   SCP_HTR | 14.4 (16.8) | 3.50 / 3.50 | 3.50, typical (PI-001) | 0.84 | 0.32 | 10.11 | 5 / 4 / 4

