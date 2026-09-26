# ZEROIZE feasibility on the fitted secure element (architecture feasibility blocker FB-ZER-1)

MESHSAT-1357. Written 26 September 2026 on base `1f614233` as the execution of item 1 of section 3 of
`v2/docs/reviews/2026-09-26-foundation-progress-review.md` ("For ZEROIZE, establish the exact key/slot lifecycle,
permissions, lock state, provisioning, trigger persistence and interrupted-power behavior. Obtain the necessary
authorized device documentation or demonstrate the operation on a development device. If the selected mechanism is
unsuitable, assess a concrete alternative and its interfaces before finalizing dependent boards.").
Main moved to `458b2873` during the third cycle; that commit carries the round-6 board B circuit, with the supervisors
on PB6 and PB7. Every repository line cited below is at `1f614233` unless it says otherwise, and
`drafts/ZEROIZE-integration.md` section 7 maps the ones that moved.

**Prototype framing.** Nothing here has been built, provisioned or tested. No ATECC608B has been configured, no drive
encrypted, no wipe run. Every result below is a DESK result: read from vendor documents and vendor source code. Desk
results and physical tests are kept in separate categories (review section 1); the physical part of this blocker is
the bench experiment of section 5, which has not run.

Evidence labels: **VERIFIED** = the cited artefact was read and says this; **SUPPORTED** = consistent public Microchip
sources say it for the same device family or configuration, but not for the exact part in the exact state;
**INFERRED** = a conclusion drawn by this study, with its reasoning given; **TBD** = not known, with its effect stated.
Fetched documents are listed with URL, capture date and sha256 in `drafts/datasheets/SOURCES.md` of this worktree.

**Revision note (second cycle, same day).** A checker found two wrong facts in the first cycle, both corrected here:
property P8 claimed the netlist settles who can reach the secure element, while three firmware-bearing supervisors
share its bus (section 2, Z-C3, residual R7); and the wipe's "about 0.51 s worst case" left out the retries its own
step 2 allowed (section 3.4, now computed by `drafts/zeroize/zer_budget.py` with every retry loop counted).

**Revision note (third cycle, same day).** A second check found that the bound at which the timed phase "gives up"
modelled a part that refuses every poll on a free bus, and was claimed for "the bus not answering" too; on a held bus
every HAL operation ends at the HAL's own timeout, which was not declared, and the Pico SDK's blocking calls have none.
Section 3.4 now declares that timeout (10 ms), computes both held-bus cases, and ends the timed phase at a deadline
the panel's HAL enforces whatever the part or the bus does; the retry cap is 6 commands, not 8. The same check
corrected a sentence about the first cycle's pass lines (3.4), and its minor items are taken in sections 3.1, 3.3, 3.4,
3.5 and 8.

## 1. Result in one screen

1. **The ruled mechanism is supported by public Microchip documentation for the ATECC608B** (a desk result: VERIFIED
   that the documents say it; SUPPORTED, not yet shown, for the fitted part in this configuration, which Z-EXP-A shows). A NIST P-256 private key held in a slot whose SlotConfig bit 13 is set can be replaced by a new,
   internally generated random key with the GenKey command (mode 0x04) after the configuration and data zones are
   both locked; locking the data zone does not freeze such a slot, and a slot whose KeyConfig.Lockable bit is clear
   can never be made permanent. Microchip's own ATECC608B Trust&GO and TrustFLEX data sheets name this use in so many
   words: the secondary private keys "can be overwritten with a new internally-generated private key (GenKey command
   mode = 0x04) to enable key deletion, key rotation and remote provisioning" (DS40002250B p. 8; DS40002249B p. 9).
   Microchip's CryptoAuthLib v3.8.0 test suite asserts a locked data zone and then regenerates exactly such a slot and
   uses it for ECDH (`test/api_atcab/atca_tests_ecdh.c:62`, `:87`, `:119`).
2. **The red team's sentence "'Wipe the secure element' is not implementable on a locked ATECC608B"**
   (`v2/docs/RED-TEAM-2026-09-09.md:420`) is right about the whole device and wrong about a key. There is no
   whole-device erase on this part (CryptoAuthLib's Delete command is for ECC204, TA010 and SHA10x only,
   `lib/calib/calib_delete.c:9`; zone locks are one-way, DS20005927A p. 24), but a key in an updatable slot can be
   destroyed, which is exactly the key hierarchy the same red-team item asked for ("a device-bound KEK in something
   erasable", `RED-TEAM-2026-09-09.md:421-422`).
3. **Not in any public document, therefore OPEN:** what GenKey does when power fails part-way through its EEPROM
   write (U1); whether the overwritten bits are physically unrecoverable (U2); the encodings of the ATECC608-only
   configuration bytes (U3); and the SSHDA part's factory configuration including its default address (U4). U1 and
   U4 are closed by the bench experiment of section 5 on the fitted MPN; U3 is avoided by design (section 3.1); U2 is
   a stated residual for the D-09 security review.
4. **Design taken by the session under the owner's standing rule of 26 September 2026:** keep the ATECC608B (no board
   change, D-03 intact); two key-encryption keys (KEK_A in slot 0, KEK_B in slot 1), both needed to unlock any drive,
   both destroyed by ZEROIZE; SlotConfig 0x2084 and KeyConfig 0x0013 on both; every other configuration byte left at
   the ATECC608 image Microchip's test suite runs against. The image and its properties are generated and checked by
   `drafts/zeroize/zer_config.py` (9 planted defects caught, 0 checks failed). The wipe takes about 0.52 s with no
   retry and at most 0.82 s with every retry the design allows, and the modules are told to drop their keys by
   1.504 s whatever the part or the bus does, at a deadline the panel's own bus layer enforces (section 3.4,
   `drafts/zeroize/zer_budget.py`);
   the proposed REQ-035 pass lines are 1.5 s for both KEKs destroyed and verified and 3.0 s for the slot cut, which a
   hardware timer enforces whatever the bus does.
5. **Fallback if the bench fails:** a TPM 2.0 on the same kit I2C bus, Infineon OPTIGA TPM SLB 9673 (I2C, address
   0x2E), whose TPM2_Clear replaces the storage primary seed by normative text of the TCG library specification. It
   changes board B's U8 site only (SOIC-8 to UQFN-32 5 x 5 mm) and the panel firmware's stack; boards A, C, D, E and P
   are untouched. JLCPCB showed no stock of any SLB 9673 variant on 2026-09-26, so the fallback carries a procurement
   risk that the ATECC608B (2,344 in stock) does not.
6. **FB-ZER-1 status: documentary feasibility CLOSED; physical demonstration OPEN** (section 7). It holds board B's
   layout entry for the U8 site only, and the panel firmware; it holds no other board.
7. **The panel controller is not the only part with firmware on the secure element's bus.** The three STM32H743 I/O
   supervisors on board B are wired to the same SDA and SCL (`gen_sch_b.py:824`); the architecture makes them I2C
   targets, but nothing in hardware stops their firmware from holding the bus or commanding the secure element. That
   is bounded by a firmware rule (Z-C3) under the owner's D-13 verified-boot floor and stated as residual R7 for the
   D-09 security review (sections 2, 3.1 and 8).

## 2. What D-03 needs from the part, as checkable properties

Owner ruling D-03 (`pcb_decisions.yaml:207-233`, decision 30; `CONOPS.md:212`; `V2-SPEC.md:34`; `PANEL.md:129`):
drive and eMMC keys are wrapped by a key the secure element holds; the covered toggle held 5 s, the only trigger,
destroys that key, then the running modules drop their RAM keys, then the slots are cut; level-sensitive after a
power loss with a wipe-pending record; re-arm only when the toggle returns; firmware and provisioning, no board
change. The secure element is `U8`, ATECC608B-SSHDA-T, on board B at kit-bus address 0x60, supplied from `+3V3_DEV`
(`gen_sch_b.py:750`); the kit I2C bus is mastered by the panel controller, an RP2040 on board C with SDA on GPIO0
and SCL on GPIO1 (`gen_sch_c.py:108`, `:124-127`), which is also the only reader of the toggle (`gen_sch_c.py:111-123`;
`PANEL.md:129`). The compute modules' own I2C reaches only their bench headers (`gen_sch_b.py:360`, `:571`), so no
module can address the secure element directly.

**Who else is on SDA and SCL (the wiring VERIFIED from the generators).** Two kinds of part share the kit bus with
U8. (a) I2C targets, which do not master it: the expanders, rail monitors, clock, temperature and light sensors and
the charger of `PANEL.md:137-150` (target-only by their function, INFERRED; their data sheets were not re-read for
this), the PoE controller (`gen_sch_b.py:639`; programmed by its "I2C Slave Address", TI SLUSBX9I,
`v2/vendor/ti/tps23861-datasheet.pdf`) and the KSZ9897R switch (`gen_sch_b.py:613`), which "is always a slave" on its
management interface (DS00002330E section 4.6.3 p. 50). The
USB hubs' and HDMI switches' own SDA and SCL pins are not on the kit bus (`gen_sch_b.py:507-513` leaves the hubs' pins 37
and 38 at NC; `gen_sch_b.py:653-655` puts the HDMI switches' on the DDC nets). (b) **Parts with firmware: the panel
RP2040, the intended master (`gen_sch_c.py:124-126`), and the three STM32H743 I/O supervisors on board B**, whose LQFP
pins 35 and 36 (PB1 and PB2, `gen_sch_b.py:261`) are on SDA and SCL in the generator at `1f614233`
(`gen_sch_b.py:824`). Those two pins have no I2C alternate function (`v2/vendor/SOURCES.yaml:310`), but a GPIO can
still bit-bang the bus or hold a line low. The round-6 board B circuit moves the supervisors to PB6 and PB7, the
I2C1 pins (`gen_sch_b.py:1137-1140` at `458b2873`, committed during this cycle; the same lines in worktree `r4b`
before it), which gives them a hardware I2C controller that can
be set to master. The architecture makes the supervisors targets at 0x30, 0x31 and 0x32 on a bus "which the panel
controller masters" (`ARCH-PCB-B-IOHA.md:96`; "one bus with one master", `:147`). That is a property of their
firmware, not of the netlist. Physical access to the bus (test points on SDA and SCL, `gen_sch_a.py:581`,
`gen_sch_b.py:786`, `gen_sch_c.py:310`) is the capture case of residual R1.

| ID | Property the part and its configuration must have | Where it is settled |
|---|---|---|
| P1 | a key only the SE holds unwraps every drive and eMMC key, and it can never be read out | section 3.1, E6 |
| P2 | after every zone is locked the panel can destroy that key with one command and no secret | E1, E2, E3, E4 |
| P3 | no command and no configuration state can make that key permanent after provisioning | E5 |
| P4 | a destruction can be verified without the key leaving the part | E7 |
| P5 | a destruction interrupted by a power loss can be completed at the next boot, and the part is never left refusing | E10, U1, Z-EXP-B |
| P6 | after a destruction the part can be re-provisioned for re-arm, many times | E2, E12 |
| P7 | the destruction is fast enough to bound the wipe time, counting every retry the design allows, and the timed phase ends at a known time whatever the part or the bus does | section 3.4, E13, E18, E20, E21, `zer_budget.py`; on the part: Z-EXP-B step B0 and Z-EXP-C |
| P8 | only the panel controller commands the part | in two parts. **Compute modules: the netlist** (their I2C reaches only the bench headers, `gen_sch_b.py:360`, `:571`). **The three STM32H743 supervisors: firmware rule Z-C3 only** (section 3.1), bounded by the owner's D-13 floor of software-verified boot on the supervisors (`ARCH-PCB-B-IOHA.md:166-172`; `CONOPS.md:404`), because their pins are on the same SDA and SCL as U8 (`gen_sch_b.py:824`, U8 at `:750`). Not settled in hardware; the residual is R7 (section 8) |

## 3. The design: slot map, key lifecycle, enrolment, unlock and wipe

Firmware and provisioning only. No generator line changes.

### 3.0 What can still change on a locked ATECC608B, and why GenKey is the destroying command

After the configuration lock nothing in the configuration zone changes by a direct write (DS20005927A section 2.4.1
p. 24), and after the data lock each slot changes only as its own SlotConfig and KeyConfig allow (E1). The paths that
remain, from the same data sheet:

| Path after both locks | Needs | Fit for destroying a KEK |
|---|---|---|
| Write, WriteConfig Always (0000) | nothing; "Slots set to always should never be used as key storage" (Table 2-8 p. 18) | no: anyone on the bus could also write a known key, and re-arming would put key material on the bus |
| Write, WriteConfig Encrypt (x1xx) | a MAC and encryption with the slot's WriteKey (Table 2-8 p. 18; the key-rotation recipe of section 2.2.3 p. 19) | no: destruction would then depend on a secret the panel must keep |
| DeriveKey roll or create (WriteConfig xx1x, never on a private-key slot) | a nonce, and a MAC if bit 15 is set (Table 2-9 p. 18; section 9.4 pp. 63-64) | possible for a symmetric key ("After the key is rolled, there is no possible way to retrieve the old key's value", p. 29) but not verifiable without a stored reference, and an interrupted roll leaves an unknown value (pp. 29, 64) |
| PrivWrite (private keys, bit 14 set) | encryption with the slot's WriteKey (Table 2-11 p. 19) | no: needs a secret, and an interrupted PrivWrite leaves the key invalid (p. 11) |
| **GenKey mode 0x04 (private keys, bit 13 set)** | nothing, unless ReqAuth is set (p. 70) | **yes: the new key comes from the part's own RNG, no key material crosses the bus to destroy or to re-arm, and the result is verifiable from public data (E7)** |
| Lock, SlotLock mode (Lockable 1) | nothing | the opposite of what is needed: it makes a slot permanent (Table 2-15 p. 25), so the KEK slots are Lockable 0 |
| UpdateExtra (bytes 84 and 85, once each), Counter (increment only) | nothing | not key storage (Table 2-5 p. 15; section 3.2.5 p. 30); the counters are a possible second persistence record, not needed |

A symmetric alternative inside the same part exists (an AES key in a slot written only encrypted, as the ATECC608B
TrustFLEX's slot 5, DS40002249B p. 15, with the unwrap done by the AES command); it needs a write secret for both
destruction and re-provisioning and is not taken.

### 3.1 Slot map

| Slot | Role | SlotConfig | KeyConfig | What each field does (DS20005927A tables) |
|---|---|---|---|---|
| 0 | KEK_A | 0x2084 | 0x0013 | WriteConfig 0010: Write never (Table 2-8), PrivWrite forbidden (Table 2-11, bit 14 clear), GenKey may write a random key after the data zone is locked (Table 2-10, bit 13 set). WriteKey 0 (unused: PrivWrite is forbidden). IsSecret 1, EncryptRead 0 (never readable, Table 2-7; required for GenKey, p. 70). LimitedUse 0, NoMac 0. ReadKey 0100: ECDH allowed with the result returned to the host, not written to slot N+1, no internal or external signatures (Table 2-6 p. 17). KeyConfig: Private 1, PubInfo 1 (the public key can always be recomputed), KeyType 100 (P-256), Lockable 0, ReqRandom 0, ReqAuth 0, AuthKey 0, bit 12 0, X509id 0 (Table 2-12 pp. 20-21) |
| 1 | KEK_B | 0x2084 | 0x0013 | the same as slot 0 |
| 2 to 15 | not used by ZEROIZE | CryptoAuthLib test image | CryptoAuthLib test image | for the bench: unchanged from `test_ecc608_configdata` (`test/api_calib/test_calib_config.c:35-44`); for the product: owned by key fill (REQ-037, deferred), under constraints Z-C1 to Z-C3 below |

KEK_A and KEK_B are CryptoAuthLib's own test slot 2 (SlotConfig 0x2087, KeyConfig 0x0013), the slot its ECDH test
regenerates on a data-locked device, with the two signing permissions removed; removing a permission only narrows
what the key can do. SlotLocked (bytes 88-89) stays 0xFFFF at the configuration lock, so both slots stay writeable by
GenKey (a 0 there makes GenKey fail, p. 70). The I2C address byte stays 0xC0, 7-bit 0x60, as `PANEL.md:143` reserves.

**Why every other byte stays at Microchip's test image (U3 avoided by design).** The ATECC608-only bytes (CountMatch,
UseLock, VolatileKeyPermission, SecureBoot, KdfIvLoc and KdfIvStr, ChipOptions; offsets in CryptoAuthLib
`lib/calib/calib_device.h:104-134`) have their semantics published only in the NDA data sheet; CryptoAuthLib publishes
their bit positions (`calib_device.h:145-249`) but not what each value does. Leaving them at the value Microchip's own
test suite runs with means the ZEROIZE functions (GenKey on a locked device, ECDH with the result in the clear) are
used in a configuration a Microchip test already exercises: the ECDH test does both under ChipOptions 0x400E
(`atca_tests_ecdh.c:62` asserts the data zone locked; `:87` GenKey on slot 2; `:119` clear ECDH on slot 2).

**The fields ZEROIZE uses mean the same on the ATECC608B as in the public ATECC508A data sheet (SUPPORTED).** The
ATECC608B summary says "No configuration bit fields have changed" from the ATECC608A and that the part is compatible
with the ATECC508A except for a listed set (DS40002239A pp. 12-13); that set is the HMAC command, the OTP consumption
mode, the Pause command, the slot 15 limited-use scheme and the SHA command's TempKey use, none of which is GenKey,
ECDH, SlotConfig, KeyConfig or the zone locks. CryptoAuthLib's ATECC608 masks put every SlotConfig and KeyConfig field
at the bit the ATECC508A tables give (`calib_device.h:171-185`, `:253-271`), with one naming difference: KeyConfig bit
12 is "IntrusionDisable" in the ATECC508A (DS20005927A Table 2-12) and `PERSIST_DIS` for the ATECC608
(`calib_device.h:269`); it is 0 on both KEK slots, which disables either feature. One inconsistency in the library is
recorded so nobody trips on it: `calib_device.h:198-200` defines `ATCA_SLOT_CONFIG_GEN_KEY_SHIFT` as 8 and
`PRIV_WRITE` as 9, which contradicts DS20005927A Table 2-10 (bit 13); no code in the library uses those two defines,
and the code that does test for GenKey permission uses WriteConfig code 2, bit 13 (`lib/pkcs11/pkcs11_key.c:175`).
This study follows the data sheet and the code that uses it; Z-EXP-A step A5 settles it on the part.

Constraints on the slots ZEROIZE does not use, whatever key fill puts there:
- **Z-C1:** no slot holds a copy, a wrapped copy or a derivative of any drive secret or of the KEKs' ECDH results.
- **Z-C2:** no slot uses slot 0 or 1 as its WriteKey (when its WriteConfig encrypts writes or authorises a
  DeriveKey), its ReadKey (when EncryptRead is set) or its AuthKey (when ReqAuth is set); a field its slot does not use
  may hold any value, as many do in the kept image (checked by `zer_config.py`); a private-key
  slot cannot serve as a symmetric key anyway (KeyConfig.Private: "can be used only with the Sign, GenKey, ECDH and
  PrivWrite commands", DS20005927A p. 21).
- **Z-C3:** SlotLocked bits 0 and 1 stay 1 at the configuration lock, and nothing on the kit bus other than the panel
  controller masters the bus. The three STM32H743 supervisors are wired to SDA and SCL (`gen_sch_b.py:824` at
  `1f614233`, on PB1 and PB2, which have no I2C alternate function, `v2/vendor/SOURCES.yaml:310`; on PB6 and PB7, the
  I2C1 pins, in the round-6 circuit, `gen_sch_b.py:1137-1140` at `458b2873`). **This is a firmware rule, not a
  hardware property, and it is the whole of P8's basis for the supervisors:** their firmware answers only as I2C
  targets at 0x30 to 0x32 (`ARCH-PCB-B-IOHA.md:96`), never sets its I2C controller to master mode, never drives SCL,
  never drives SDA except to acknowledge or return data as an addressed target, and never addresses 0x60. Its bound
  is the owner's D-13 floor: software-verified boot on the supervisors (`ARCH-PCB-B-IOHA.md:166-172`; `CONOPS.md:404`),
  their images written over the bench SWD pads (`gen_sch_b.py:840`) with BOOT0 held low (`gen_sch_b.py:832`). What a
  supervisor can do if this rule is broken is residual R7 (section 8).

### 3.2 Key and slot lifecycle

| State | How it is entered | Commands (CryptoAuthLib v3.8.0) | What the part holds | Who acts |
|---|---|---|---|---|
| BLANK | factory; LockConfig and LockValue 0x55 (DS20005927A p. 15) | `atcab_read_config_zone` | Microchip's factory configuration (U4) | provisioning firmware on the panel |
| CONFIGURED | the configuration image written and the configuration zone locked with its CRC | `calib_write_config_zone` (`calib_write.c:351`), `calib_lock_config_zone_crc` (`calib_lock.c:139`) | the slot map of 3.1, now unchangeable (p. 24) | provisioning firmware |
| KEYED | KEK_A and KEK_B created inside the part; the data zone locked | `calib_genkey` mode 0x04 (`calib_genkey.c:134-136`), `calib_lock_data_zone` (`calib_lock.c:162`) | two private keys no one has seen; the public keys P_A0 and P_B0 were returned by GenKey (p. 70); the data-zone lock CRC leaves private-key slots out (E11), so creating the KEKs before or after the lock gives the same CRC | provisioning firmware; P_A0 and P_B0 go into the panel's flash |
| ENROLLED (armed) | every NVMe drive and eMMC encrypted under the two KEKs (3.3) | none on the SE: enrolment needs only P_A0 and P_B0 | unchanged | module provisioning, service state |
| WIPE PENDING | the toggle held closed 5 s, or found closed at boot, or a pending record found | journal record written first | unchanged until GenKey runs | panel |
| ZEROIZED | GenKey mode 0x04 on slots 0 and 1, verified | `calib_genkey` twice, `calib_get_pubkey` (`calib_genkey.c:151-153`) twice | two new random keys, public keys P_A1 and P_B1 different from P_A0 and P_B0 | panel |
| RE-ARMED | the toggle returned with a verified ZEROIZED state | none | the new keys | panel |
| RE-ENROLLED | the modules re-imaged and the drives re-created under P_A1 and P_B1 | none on the SE | unchanged | service procedure over the Glenair console (D-12) |

Endurance does not bound this cycle: the EEPROM is rated for 400,000 writes per byte at +85 C (DS40002239A p. 6),
and each wipe and re-provisioning writes each KEK slot a handful of times.

**Consequence recorded (not a new decision):** because D-03 wraps the eMMC keys too, a ZEROIZED kit's modules cannot
boot their operating system from eMMC until they are re-imaged over `rpiboot` in the Service mode (`CONOPS.md:215`)
and re-enrolled. The session's provisioning rule: `/boot` and a recovery image hold no secret and stay unencrypted,
so a re-armed kit boots to a recovery state rather than to nothing.

### 3.3 Enrolment and unlock (INFERRED design, standard constructions)

- **Enrolment of a drive d**, on the module, with no secret from the SE: generate an ephemeral P-256 pair (e_d,
  E_d); compute Z_A = ECDH(e_d, P_A0) and Z_B = ECDH(e_d, P_B0); the LUKS2 passphrase is HKDF-SHA256 over Z_A || Z_B
  with the drive's UUID in the info string; E_d is stored in the LUKS2 header as a token (public); e_d is discarded.
  Exactly one LUKS keyslot; no recovery passphrase, no second keyslot, no key escrow (any of these would survive
  ZEROIZE).
- **Unlock of drive d:** the panel runs ECDH(slot 0, E_d) and ECDH(slot 1, E_d) (75 ms each at the default clock,
  `calib_execution.c:129`; that is the same ATECC608A table as GenKey's 115 ms, so SUPPORTED, not VERIFIED, for the
  ATECC608B, E13; it gates no requirement) and returns Z_A and Z_B; the module runs the same HKDF. Both KEKs are
  needed, so a single KEK that survived a failed destruction (U1) unlocks nothing.
- **Which modules reach the panel directly:** the panel is a USB device on bank 1's hub, whose home host is slot 1
  and whose failover host is slot 2 (`PANEL.md:5`; `ARCH-PCB-B-IOHA.md:311`). A module that does not host bank 1 (slot
  3 always, and slot 1 while bank 1 is failed over to slot 2) must ask through the bank-1 host over Ethernet, from its
  initramfs. **Consequence recorded:** for those modules the unlock dependency of the owner's accepted residual (the
  SE, the panel controller, the kit I2C bus) also includes the bank-1 host module and the KSZ9897R switch; with slots
  1 and 2 both down, slot 3 cannot unlock. This matches `ARCH-PCB-B-IOHA.md:145` and `:330` (common modes) and adds
  nothing to any board. The unlock relay must never answer on the wall Ethernet port (KSZ port 4), which is red-team
  item 4 (`RED-TEAM-2026-09-09.md:426-427`) applied to this service.
- **The ECDH result crosses the kit bus in the clear** (ReadKey bit 3 clear). ATECC608 I/O protection could encrypt it
  (DS40002239A p. 12, "Encrypted output for ECDH"; DS40002250B p. 10 describes the pairing), but its ChipOptions
  encoding is NDA-only (U3) and it protects only against a probe on a live kit that has not been zeroized, which
  already unlocks its own drives. Deferred to the D-09 security review, not needed for D-03.

### 3.4 The wipe sequence and its time budget

At the 5 s commit point (flipping back earlier aborts, `CONOPS.md:212`), the panel controller:

0. arms a hardware timer alarm 3.0 s after the end of the hold whose interrupt handler drives `SLOT_EN1..3` low,
   whatever the rest of the firmware is doing (the RP2040 timer has four alarms, each raising its own interrupt,
   RP2040 datasheet section 4.6 p. 534). The 3.0 s pass line depends on this alarm and on nothing else. "Whatever the
   rest of the firmware is doing" holds under three firmware rules, taken by the session under the owner's standing
   rule of 26 September 2026 (E22): the handler, and everything it calls, runs from RAM, because the SDK's flash
   functions are "unsafe if you have interrupt handlers or an interrupt vector table in flash" (pico-sdk 2.3.1
   `hardware/flash.h:23-25`); its interrupt has the highest priority (`PICO_HIGHEST_IRQ_PRIORITY` 0x00, where the SDK
   gives every interrupt 0x80 by default, `hardware/irq.h:172-178`); and interrupts are masked only for the two
   journal page programs of steps 1 and 4 (each at most 3 ms, tPP), both before step 5, which starts by 1.504 s, and
   no flash erase or program runs between the start of step 5 and the slot cut, so no masked window can reach 3.0 s.
   Backstop if the firmware hangs with interrupts masked: the RP2040 watchdog, which the panel firmware enables. Its
   reset reaches every block the SDK selects, which is every block but the two oscillators
   (`hardware_watchdog/watchdog.c:52-53`; RP2040 datasheet section 4.7.1 p. 544), so `SLOT_EN1..3` return to inputs
   with the pad pull-down and board A's 100k resistors hold them low (`gen_sch_c.py:118-119`; `gen_sch_a.py:407`, "a
   slot with no controller line stays off"). In that failure the slots go off at the watchdog period, a panel firmware
   choice (TBD), not at 3.0 s;
1. appends a PENDING record to its flash journal (one page program, 3 ms maximum, W25Q16JV Rev H PDF p. 63; the
   journal sectors are pre-erased so no 45 to 400 ms sector erase sits in this path, same page);
2. wakes the SE and runs GenKey mode 0x04 on slot 0, then on slot 1 (C0, C1), so both keys are overwritten before
   anything else is spent;
3. verifies each slot with GenKey mode 0x00 (V0, V1; public key recomputed from the stored key, allowed because PubInfo
   is 1, p. 70): the result must equal the key GenKey returned and differ from that slot's recorded public key (P_A0
   for slot 0, P_B0 for slot 1). **Retry policy of steps 2 and 3, the timed phase** (taken by the session under the
   owner's standing rule of 26 September 2026): a command answering with an error, the ECC fault code (a generated key
   can be unacceptable and "the command should be re-run", DS20005927A p. 70), the health-test error (a transient
   failure "may pass when run a second time", DS40002250B p. 7), a CRC error or a bus error is retried; a failed
   verification re-runs that slot's create and verifies again. The timed phase issues **at most 6 GenKey commands in
   all**, the 4 of the nominal sequence plus 2 retries shared by the two slots, and spends no retry before C0 and C1
   have both been issued. The library's own loops are bounded by the panel's build: `rx_retries` = 1 in its
   `ATCAIfaceCfg` (the field of `lib/atca_iface.h:178`; the library default is 20, `lib/atca_cfgs.c:59`),
   `ATCA_POLLING_MAX_TIME_MSEC` = 200 (overridable, `lib/hal/atca_hal.h:185-187`; default 2500). **The bus layer is
   bounded twice** (taken by the session under the owner's standing rule of 26 September 2026). (a) Every bus
   operation of the panel's six-function HAL (`lib/hal/README.md:34-39`) ends within **T_HAL = 10 ms**: it uses the
   Pico SDK's `i2c_write_blocking_until` and `i2c_read_blocking_until`, which return `PICO_ERROR_TIMEOUT` at a given
   time (pico-sdk 2.3.1 `hardware/i2c.h:266-295`, `i2c.c:222-224`), never `i2c_write_blocking`, which takes no
   timeout (`i2c.c:245-247`) and waits for each byte to leave with no limit (`i2c.c:170-176`); after a timeout it runs
   `i2c_init` again, which puts the controller block through reset (`i2c.c:32-34`), because an SCL held low cannot be
   recovered from the master's side (RP2040 datasheet section 4.3.13.2 p. 459). 10 ms is 65 percent above the longest
   legitimate transfer, the 67-byte response read (6.05 ms at 100 kHz); a 5 ms limit would fail every response read
   at 100 kHz. (b) **A deadline D = 1.5 s after the end of the hold**, the KEK pass line: each bus operation's limit
   is the earlier of now + T_HAL and D, and from D the HAL fails every bus operation at once and the platform's
   `atca_delay_ms` and `atca_delay_us` (supplied by the panel, `lib/hal/atca_hal.h:209-216`) return without waiting, so
   a library call in progress unwinds through its own bounded loops, and the wipe issues no further command;
4. appends DONE if both slots verified; otherwise the PENDING record stays (I3) and the wipe is INCOMPLETE, and the
   panel carries on with step 5 all the same;
5. tells the running modules to drop their keys (for example `cryptsetup luksSuspend`, plus `luksErase` on the drives
   it can still reach, as defence in depth that a powered-off module does not need);
6. drops `SLOT_EN1..3` as soon as every running module has confirmed, and at the latest at the alarm of step 0;
7. if the wipe is INCOMPLETE, keeps retrying with the slots already off, untimed, up to 10 GenKey mode 0x04 tries per
   slot in all (the timed phase included), then shows ZEROIZE INCOMPLETE as the wipe-due failure row of the boot
   table in 3.5 does;
8. sounds 3 s and refreshes the e-paper (`PANEL.md`, section 9).

Invariants: **I1**, every wipe request runs GenKey on both slots at least once, and no record anywhere can make the
panel skip it (a record only decides whether to start, never whether the key is already gone); **I2**, P_A0 and P_B0
live where only the panel writes them, never in a slot another bus master could rewrite; **I3**, an unreadable or
torn journal entry reads as PENDING, so a failure there fails toward the wipe; **I4**, the slot cut never waits on
the secure element, the bus or a module (step 0); **I5**, step 5 never waits on the secure element or the bus past
the deadline D (step 3), so the modules are told before their power goes whatever the bus does.

**Time budget** (computed by `drafts/zeroize/zer_budget.py`, which carries the source of every number in its header
and refuses a pass line that does not cover the worst case). The kit bus clock is not declared anywhere (TBD); the
budget assumes 100 kHz, the top of I2C standard mode and the lowest clock CryptoAuthLib itself uses (it wakes the part
at 100 kHz, `calib_basic.c:54-63`, and defaults to 400 kHz off Linux, `lib/atca_cfgs.c:52-56`), so it holds for any
clock of 100 kHz or more; a slower clock is a new input to the script, and the panel firmware runs the bus at 100 kHz
or faster. One GenKey command then costs **127.85 ms nominally**: a wake of 2.17 ms (the wake-delay of 1.5 ms, tWHI in
DS40002239A Table 2-2 p. 7 and `lib/atca_cfgs.c:58`, plus the wake write and the 4-byte wake response,
`lib/calib/calib_basic.c:37-105`); a 9-byte send (DS20005927A Table 6-1 p. 42, Table 9-1 p. 55, Table 9-20 p. 70); 115
ms of execution (the ATECC608-M0 table, `lib/calib/calib_execution.c:124-146`) plus at most one 2.2 ms polling cycle
to see the answer (`calib_execution.c:506-507`, `:571-590`, `lib/hal/atca_hal.h:176-183`; a busy part does not
acknowledge its address, DS20005927A section 6.5 p. 44); a 67-byte response read (Table 9-21 p. 70,
`calib_execution.c:378-475`); an idle write (`calib_basic.c:143-169`); and 1 ms for the panel's own code, an INFERRED
allowance that Z-EXP-C replaces with a measurement. With every library-level retry taken a command costs 135.19 ms.
Three fault cases are computed per command as well. **The part not answering, bus free** (it takes the command and
refuses every poll): the library polls to its 200 ms cap, 234.74 ms. **The bus held for the whole command** (SCL or
SDA held low, by a failed part or by a supervisor breaking Z-C3, R7): nothing is ever sent, but CryptoAuthLib still
runs every loop, because `calib_wakeup_i2c` ignores the result of its wake write and still reads (`calib_basic.c:79`,
`:87-90`) up to `rx_retries` + 1 times (`:45`, `:102`), and `calib_execute_command` repeats wake-and-send up to
`rx_retries` + 1 times while the send reports `ATCA_RX_NO_RESPONSE` (`calib_execution.c:521-563`), then idles
(`:623-627`). With every operation ending at T_HAL that is (R+1)((R+1)(2 T_HAL + 1.5 ms) + T_HAL) + T_HAL + 1 ms = 11
T_HAL + 7 ms = **117 ms** at R = 1 and T_HAL = 10 ms, an upper bound over the HAL's return codes (a HAL reporting
`ATCA_COMM_FAIL`, as the vendor's ESP32 HAL does, `lib/hal/hal_esp32_i2c.c:256-258`, ends the send loop after one
round, `calib_execution.c:552-559`). **The bus held from just after an accepted send**: every one of the 101 polls
then costs T_HAL plus the 2 ms polling delay, 1227 ms per command, which no retry cap bounds well; the deadline D
bounds it.

| Case | What it counts | Time from the end of the hold |
|---|---|---|
| Nominal | C0, C1, V0, V1, no retry, two journal writes | **0.517 s** |
| Worst case in specification | 6 commands (the nominal 4 plus the 2 retries of the policy), each with every library-level retry | **0.817 s** |
| The part not answering (NACK), bus free | 6 commands, each polled to the 200 ms cap | 1.414 s, before D: the retry policy ends it |
| The bus held throughout | 6 commands, every HAL operation ending at T_HAL = 10 ms | 0.708 s, before D: the retry policy ends it |
| The bus held after each send, or any other bus behaviour | 6 commands, every poll ending at T_HAL | 7.368 s and 7.986 s if nothing stopped them; D stops them |
| **Step 5 starts, whatever the part or the bus does** | the deadline D = 1.5 s, the library's unwind (1 ms, INFERRED; Z-EXP-C measures it) and at most one journal write of step 4 (3 ms; DONE is appended only for a verification finished before D) | **1.504 s** |
| The first cycle's policy, for the record | up to 10 creates per slot inside the timed sequence, plus 2 verifications, nominal commands | 2.819 s |

The script checks that the two named fault cases run their whole retry policy before D (so D ends only what the model
does not name), that D never cuts short an in-specification wipe, that the polling cap and T_HAL each keep 25 percent
over the figure they cover (115 ms of execution; the 6.05 ms response read), and that step 5 starts at least 1.0 s
before the cut. Why 6 commands and not the second cycle's 8: with 8, the NACK case takes 1.884 s and would need D near
2 s, leaving the modules about 1 s; keeping the polling cap's 74 percent margin over an execution time that is not yet
measured matters more than two further retries, because a cap below the true execution time would fail every command,
in step 7 as well. It plants ten defects, each required to fail its own check: among them no HAL timeout (the Pico
SDK's blocking calls), a 200 ms HAL timeout (the ESP32 HAL's value, `hal_esp32_i2c.c:249`), a 5 ms one, a polling cap
below the execution time, and the second cycle's model with no deadline.

**Correction of the first cycle.** Its "about 0.51 s worst case" was the nominal line: it counted no retry while its
own step 2 allowed ten tries per slot, which puts that policy's worst case near 2.8 s, above its 1.0 s line; and
with its slot cut 2 s after DONE the slots would have been cut near 4.8 s, above its 3.0 s line, so R3's "at most
3.0 s" did not hold either. **Correction of the second cycle.** Its bound of 1.884 s "the timed phase gives up"
modelled only a part refusing every poll on a free bus, and was claimed for "the bus not answering" too; on a held bus
every HAL operation ends at the HAL's own timeout, which it did not declare. The retry cap of 6, the library bounds,
T_HAL, the deadline D and the step-0 alarm above replace both.

The 115 ms is the ATECC608A's figure. The ATECC608B summary names Verify, SecureBoot, Lock and Read as the commands
whose timing changed from the ATECC608A (DS40002239A section 3.1 p. 12), not GenKey, so the figure is SUPPORTED for
the fitted part, not VERIFIED; the library itself warns that the ATECC608B supports only polling
(`calib_execution.c:37-39`), which this design uses. Z-EXP-B step B0 measures GenKey on the part and the script takes the
measured value. Each command is far inside the 0.7 s minimum watchdog (DS40002239A p. 7), and CryptoAuthLib wakes the
part before and idles it after every command (`calib_execution.c:524-529`, `:623-627`), which restarts the watchdog
(DS20005927A pp. 60-61). Appendix 32.50 item 5's "keys wiped in milliseconds" (`MESHSAT-709-geometry-appendix.md:2789`)
is therefore about half a second, and at most about a second.

**Proposed pass lines for REQ-035's open timing TBD** (`REQUIREMENTS-TRACE.md`, REQ-035, pending merge in worktree
`i1` at `d468613e`, lines 1075-1085; **taken by the session under the owner's standing rule of 26 September 2026**),
set from the worst case, not the nominal: (1) both KEKs destroyed and verified within **1.5 s** of the end of the 5 s
hold (worst case in specification 0.817 s, so 0.68 s of margin for the unpublished ATECC608B execution time; the
script refuses a line less than 25 percent above the worst case); (2) the slots cut within **3.0 s** of it, by the
step-0 alarm, whatever the secure element or the bus does. Step 5 starts by 1.504 s whatever the part or the bus
does, so the modules are told to drop their keys at least 1.49 s before their power goes even when the secure
element fails or the bus is held, which keeps D-03's order (if the HAL's timeouts or the
deadline themselves failed, the alarm still cuts at 3.0 s, and a hang with interrupts masked meets the watchdog of
step 0). A wipe needing more than the 2 retries misses line (1); that is the requirement doing its job: the miss is
recorded, the slots are still cut at 3.0 s and step 7 keeps going. Supply current is not a constraint: 14 mA
maximum during an ECC command at clock divider 0 (DS40002239A p. 10).

### 3.5 Trigger persistence and interrupted power

The toggle is a maintained part, so its level survives a power loss by itself (`gen_sch_c.py:115-116`; the reading at
reset needs no firmware, `gen_sch_c.py:112-114`). The boot logic, run before any `SLOT_EN` write:

| Toggle at boot | Journal | KEK public keys vs P_A0/P_B0 | Action |
|---|---|---|---|
| closed | any | any | run the wipe (3.4 steps 1 to 4 and 7, I1 applies; the slots are already off, so steps 0, 5 and 6 have nothing to do), keep the slots off while the toggle stays closed |
| open | PENDING (or torn, I3) | any | run the wipe to DONE; then, the toggle being open, re-arm (slots may power; the modules find their drives unreadable) |
| open | no PENDING entry | differ from the recorded keys | ZEROIZED and re-armed (or the SE was replaced): slots may power into the recovery state (3.2) until the drives are re-enrolled and the new public keys recorded |
| open | no PENDING entry | equal to the recorded keys | normal boot |
| open | PENDING (or torn, I3): **a wipe is due** | GenKey or GenKey-public still refused after 10 mode 0x04 tries per slot in all (3.4 step 7), or the SE does not answer (a bus held by another part included, R7) | ZEROIZE INCOMPLETE: MASTER WARN, e-paper message, slots stay off; retry at every boot. Fail secure, taken by the session under the owner's standing rule of 26 September 2026: a kit whose wipe cannot be proven never computes |
| open | no PENDING entry: **no wipe is due** | the SE does not answer (a failed SE, or any target holding the kit bus on boards A to D), or refuses GenKey-public on a KEK slot | normal boot without the SE: MASTER WARN, e-paper message, slots may power; no drive or eMMC unlocks until the SE answers (3.3), so the modules come up in the recovery state of 3.2 and the SE is retried. Taken by the session under the owner's standing rule of 26 September 2026: keeping the slots off here would add a new whole-compute common mode (every module unpowered by one failed SE or one stuck bus target) that D-03 never accepted, while powering them gives nothing away, since the drives' unlock already depends on the SE, the panel controller and the kit bus by the owner's accepted residual (`pcb_decisions.yaml:224-225`) |

What the public documents say about power loss inside a command (VERIFIED, DS20005927A): an interrupted PrivWrite
may leave the key invalid (p. 11); an interrupted DeriveKey roll may leave "the key to have an unknown value" (pp. 29,
64); the monotonic counters "never lose counts" and "may increment by a value of more than one" (pp. 30, 62-63); a
command the watchdog would cut is refused before it starts, and "The device will never be left in an unusable state
after an aborted command" (p. 61, about watchdog aborts). **What GenKey does when the power fails during its write is
not documented publicly (U1).** Every outcome GenKey could leave (old key intact, new key, invalid slot, mixed bytes)
is handled by the table above, because the wipe always re-runs GenKey and verifies against P_A0 and P_B0, and GenKey
creates a key in an invalid slot as a matter of course (the slot is invalid before its first GenKey, p. 11). One
outcome would break the design: the part refusing GenKey on that slot for good while the old key stays usable. Two
KEKs make that single failure harmless (the unlock needs both), and Z-EXP-B measures whether it happens at all.

A wipe requested while the kit has no power completes only at the next power-up (D-03's level-sensitive rule). Until
then the KEKs exist; see residual R1.

## 4. Evidence register (desk)

| ID | Claim | Source | Status |
|---|---|---|---|
| E1 | Locking the data zone does not freeze the slots: "Locking the data/OTP zone does not mean that the values in these zones cannot be modified; locking indicates that the slot now behaves according to the policies set by the associated configuration zone's values" | DS20005927A section 2.4.2 p. 24 | VERIFIED |
| E2 | GenKey may write a random key into a slot after the data lock when SlotConfig bit 13 is set; ReqAuth, if set, would require prior authorisation; a zero SlotLocked bit makes it fail | DS20005927A Table 2-10 p. 19; section 9.7 p. 70 | VERIFIED |
| E3 | On the ATECC608B itself, GenKey mode 0x04 overwrites a secondary private key "to enable key deletion, key rotation and remote provisioning" | DS40002250B (ATECC608B-TNGTLS) p. 8; DS40002249B (ATECC608B-TFLXTLS) p. 9 | VERIFIED for those factory configurations; SUPPORTED for a customer configuration with the same bits |
| E4 | Microchip's test suite runs GenKey and then clear ECDH on its slot 2 (0x2087 / 0x0013) with the data zone asserted locked | CryptoAuthLib `d49c7d57`, `test/api_atcab/atca_tests_ecdh.c:62`, `:87`, `:119`; config `test/api_calib/test_calib_config.c:35-44`; slot map `:61-70` | VERIFIED (vendor code read; not run here) |
| E5 | With SlotLocked 1 and Lockable 0 a slot is "Writeable but not lockable"; a zero SlotLocked bit prohibits PrivWrite, Write, GenKey and DeriveKey "regardless" of other bits | DS20005927A section 2.4.3, Table 2-15 p. 25 | VERIFIED |
| E6 | ECC private keys can never be read; KeyConfig.Private limits a slot to Sign, GenKey, ECDH and PrivWrite; ECDH is allowed by ReadKey bit 2 and returns the result in the clear when bit 3 is clear | DS20005927A pp. 21, 29 (section 3.2), Table 2-6 p. 17, section 9.5 p. 65 | VERIFIED |
| E7 | GenKey returns the public key of a created key, and with PubInfo set recomputes the public key from the stored private key | DS20005927A section 9.7 pp. 69-71 | VERIFIED |
| E8 | ATECC608B configuration fields are unchanged from the ATECC608A and compatible with the ATECC508A except the listed functions | DS40002239A sections 3.1 and 3.2 pp. 12-13 | VERIFIED (the statement); SUPPORTED (its application to each field used here) |
| E9 | No whole-device erase exists on this family; zone locks cannot be undone | CryptoAuthLib `lib/calib/calib_delete.c:9`; DS20005927A p. 24 | VERIFIED |
| E10 | Power loss inside PrivWrite and DeriveKey roll, counters' tear behaviour, watchdog aborts | DS20005927A pp. 11, 29, 30, 61, 62-64 | VERIFIED |
| E11 | Private-key slots are excluded from the data-zone lock CRC, so the CRC does not depend on the KEKs | DS20005927A section 9.10 p. 75 | VERIFIED |
| E12 | EEPROM write endurance 400,000 cycles per byte at +85 C; retention 10 years at +55 C | DS40002239A Table 2-1 p. 6 | VERIFIED |
| E13 | ATECC608 execution times at clock divider M0: GenKey 115 ms, ECDH 75 ms, Lock 35 ms; watchdog 0.7 to 1.7 s; tWHI 1.5 ms. The library's table is compiled only without polling (`#ifdef ATCA_NO_POLL`, `calib_execution.c:42`) and the library states that the ATECC608B supports only polling (`:37-39`); the ATECC608B's timing changes from the ATECC608A are Verify, SecureBoot, Lock and Read | CryptoAuthLib `lib/calib/calib_execution.c:124-146`; DS40002239A Table 2-2 p. 7, section 3.1 p. 12 | VERIFIED that the library and the summary say this; the 115 ms is SUPPORTED, not VERIFIED, for the ATECC608B's GenKey; Z-EXP-B step B0 measures it |
| E14 | The default I2C address byte is 0xC0 (7-bit 0x60); the library's default ATECC608 interface uses 0xC0; Microchip's kit guide lists the generic ATECC608A-MAHDA at 7-bit 0x60 | DS20005927A Table 2-5 p. 13; CryptoAuthLib `lib/atca_cfgs.c:42-50`; DS50002921A p. 4 | SUPPORTED for the ATECC608B-SSHDA-T (U4 closes it on the part) |
| E15 | The full ATECC608B and ATECC608A data sheets are under NDA; DS40001977A, the number sometimes cited as the full ATECC608A sheet, is itself a summary | DS40002239A p. 1; `microchip-atecc608a-40001977A.pdf` footer "Datasheet Summary" | VERIFIED; no third-party copy of an NDA document was used |
| E16 | The KSZ9897R's management interface "is always a slave", whether SPI, I2C or MIIM | Microchip DS00002330E section 4.6.3 p. 50 (`v2/vendor/cluster/ksz9897.pdf`, sha256 `02aab4c6a8065c497946191af10bc41f7299d9bbd98c8b3b1db5a51407c21bf0`, as `v2/vendor/SOURCES.yaml:233-238` records it) | VERIFIED |
| E17 | The three STM32H743 supervisors are on the kit bus: pins 35 and 36 (PB1, PB2) on SDA and SCL at `1f614233`; PB6 and PB7 (I2C1) in the round-6 circuit; the architecture makes them I2C targets at 0x30 to 0x32 on a bus the panel masters | `gen_sch_b.py:261`, `:824`; `gen_sch_b.py:1137-1140` at `458b2873` (committed during this cycle; worktree `r4b` before it); `v2/vendor/SOURCES.yaml:310`; `ARCH-PCB-B-IOHA.md:96`, `:147` | VERIFIED from the generators (netlist not regenerated here) |
| E18 | CryptoAuthLib's own loops: the wake retries and the send retries both take `rx_retries` (default 20 in the I2C configuration); the wake ignores the result of its wake write and still reads; the send loop repeats only while the send reports `ATCA_RX_NO_RESPONSE`, and the vendor's ESP32 HAL reports `ATCA_COMM_FAIL` and gives its own transfers a 200 ms limit; polling waits 1 ms, then retries every 2 ms up to a cap of 2500 ms, each value overridable at build time; the timer functions are the platform's; a busy part does not acknowledge its address; the I2C framing of a command and of a response | `lib/calib/calib_basic.c:45`, `:79`, `:87-90`, `:102`; `lib/calib/calib_execution.c:548-559`; `lib/hal/hal_esp32_i2c.c:249`, `:256-258`; `lib/hal/atca_hal.h:209-216`; `lib/calib/calib_execution.c:506-507`, `:521`, `:563`, `:571-590`; `lib/atca_cfgs.c:58-59`; `lib/atca_iface.h:177-178`; `lib/hal/atca_hal.h:176-187`; DS20005927A Table 6-1 p. 42, Table 6-2 p. 43, section 6.5 p. 44, Table 9-1 p. 55, Tables 9-20 and 9-21 p. 70 | VERIFIED (source and data sheet read; not run) |
| E19 | The RP2040 system timer has four alarms, each raising an interrupt on a match | RP2040 datasheet section 4.6.1 p. 534 (build-version 3184e62) | VERIFIED |
| E20 | The Pico SDK's `i2c_write_blocking` takes no timeout and waits for each byte to leave with no limit; `i2c_write_blocking_until` and `i2c_read_blocking_until` return `PICO_ERROR_TIMEOUT` at a given absolute time; `i2c_init` puts the controller block through reset | pico-sdk 2.3.1 (`079c6f39`) `src/rp2_common/hardware_i2c/i2c.c:32-34`, `:170-176`, `:222-224`, `:245-247`, `:249-253`; `include/hardware/i2c.h:266-295`, `:338-349` | VERIFIED (source read; not run) |
| E21 | For an SCL stuck low "there is no effective method to overcome this problem but to reset the bus using the hardware reset signal"; the RESETS register holds each peripheral, I2C0 and I2C1 among them, in reset while its bit is set | RP2040 datasheet section 4.3.13.2 p. 459; section 2.14 Table 202 pp. 175-176 | VERIFIED |
| E22 | The SDK's flash functions are unsafe with interrupt handlers or a vector table in flash unless interrupts are disabled; interrupt priority 0x00 is the highest and the SDK default is 0x80; the SDK's watchdog resets every block but the two oscillators; a watchdog reset feeds the power-on state machine and the reset controller | pico-sdk 2.3.1 `hardware_flash/include/hardware/flash.h:17-25`, `hardware_irq/include/hardware/irq.h:172-178`, `:217-218`, `hardware_watchdog/watchdog.c:52-53`; RP2040 datasheet section 4.7.1 p. 544 | VERIFIED |
| E23 | I2C word address 0x01 puts the part to sleep until the next wake flag; GenKey mode bit 3 places a digest of a slot's public key in TempKey; Sign in internal mode signs a GenKey or GenDig result in TempKey and needs SlotConfig.ReadKey bit 1 on the signing slot | DS20005927A Table 6-2 p. 43; section 9.7 p. 71; section 9.18 pp. 85-86; Table 2-6 p. 17 | VERIFIED (the statements); the impersonation of R7(d) and the attested check built on them are INFERRED |

## 5. What is not public, and the bounded bench experiment that settles it

| ID | Unknown | Effect if left open | Settled by |
|---|---|---|---|
| U1 | GenKey's behaviour when power fails during its write, including whether the part can end refusing GenKey on the slot | P5 unproven; the design's recovery rests on it | Z-EXP-B |
| U2 | whether EEPROM bits overwritten by GenKey are unrecoverable to invasive analysis (DS20005927A p. 33 lists internal memory encryption and an active shield, no erase guarantee) | a lab-grade attacker might recover a destroyed key | not settleable by the project; residual R2, D-09 review |
| U3 | the ATECC608-only ChipOptions and related encodings | only if a design needed them; this one does not (3.1) | avoided by design; Z-EXP-A A4 checks clear ECDH under the kept image |
| U4 | the SSHDA part's factory configuration and default address | the kit-bus address 0x60 (`PANEL.md:143`) | Z-EXP-A A0 |

**Z-EXP-A, function on the fitted MPN (about 2 h, one person).** Equipment: Microchip DM320118 CryptoAuth Trust
Platform (a SAM D21 host speaking Microchip's kit protocol over USB HID, DS50002921A p. 4); MikroElektronika Secure
SOIC click, a SOIC-8 socket on the mikroBUS header (DS50002921A Table 2-1 p. 6); ATECC608B-SSHDA-T samples of the
fitted order code (LCSC C1518769, JLCPCB 2,344 in stock at 0.9955 USD, read 2026-09-26T12:27Z,
`drafts/prices/jlc-ATECC608B-SSHDA-T.json`). The DIP switch is set to the mikroBUS only (SW2_1 ON, SW2_2 OFF,
DS50002921A p. 5), because the on-board TrustCUSTOM device also answers at 0x60 (p. 4). Host: a PC with CryptoAuthLib
v3.8.0 and its kit HID HAL (`lib/hal/hal_all_platforms_kit_hidapi.c`). Steps on each of three parts:

- A0: `atcab_info`; read the whole configuration zone; record it; require LockConfig = LockValue = 0x55 and byte 16 =
  0xC0 (closes U4).
- A1: write the image of `drafts/zeroize/zer_config.py` (`calib_write_config_zone`), read it back byte for byte, lock
  the configuration zone with the CRC of the read-back (`calib_lock_config_zone_crc`).
- A2: GenKey mode 0x04 on slots 0 and 1; record P_A0, P_B0. A3: lock the data zone; require LockValue = 0x00.
- A4: with a host test key pair (q, Q): ECDH(slot 0, Q) and ECDH(slot 1, Q) must equal the host's ECDH(q, P_A0) and
  ECDH(q, P_B0) (proves the slot holds the key whose public key was recorded, and that clear ECDH works under the
  kept ChipOptions).
- A5: GenKey mode 0x04 on slot 0 and slot 1 with the data zone locked: both succeed; P_A1 differs from P_A0 and P_B1
  from P_B0; GenKey mode 0x00 returns P_A1 and P_B1; ECDH(slot 0, Q) now equals ECDH(q, P_A1) and differs from the A4
  result.
- A6: `calib_lock_data_slot(0)` (`calib_lock.c:219`) must be refused, and bytes 88-89 must still read 0xFFFF.
- A7: a clear Write and a PrivWrite to slot 0 must both be refused.
- A8: repeat A5 1,000 times on one part: every call succeeds and all 1,000 public keys are distinct (0.25 percent of
  the rated endurance, E12).

Pass: every step on all three parts. Fail (switch condition S1, section 6): GenKey refused on a locked device, any
public key repeated, A6 or A7 accepted, or A4 or A5 disagreeing with the host computation.

**Z-EXP-B, interrupted power (a few hours to build, about 10 minutes of unattended run per part).** Rig: a Raspberry
Pi Pico (an RP2040, the panel controller's own MCU, so the CryptoAuthLib HAL written for it is the panel's: six
functions, `lib/hal/README.md:34-39`) wired to the Secure SOIC click, the SE's VCC from a load switch the Pico drives,
100 nF at the part as on board B (`C69`, `gen_sch_b.py:750`), and the I2C pull-ups on the switched rail so the part is
not powered through SDA and SCL while off (pin voltage limit VCC + 0.5 V, DS40002239A p. 6). A one-off scope check
sets the off-time so VCC is below 0.2 V before power returns. **Step B0, timing, before the power trials:** at 100
kHz, 1,000 GenKey mode 0x04 and 1,000 mode 0x00 on slot 0 of a provisioned part, recording for each the time from the
command's STOP to the first acknowledged read and the whole call time; the maxima go into `zer_budget.py` in place of
the 115 ms and the per-command total, and the pass lines of 3.4 are re-checked with them (a larger maximum is a budget
input, not a switch condition). Per trial, on a part provisioned by Z-EXP-A: read P_before (GenKey mode 0x00 on slot
0); issue GenKey mode 0x04 on slot 0 and cut VCC at a delay drawn uniformly from 0 to 130 ms after the command's last
byte (the M0 maximum is 115 ms; if step B0 measures more, the window is that maximum plus 15 ms); restore power;
classify GenKey mode 0x00 as OLD, NEW or ERROR; resume with GenKey mode 0x04 until it succeeds (at most 10 tries);
require the resumed public key to differ from P_before and to be returned by mode 0x00; require the configuration zone
byte-identical and slot 1's public key unchanged. 1,000 trials on each of two parts.

Pass: 2,000 of 2,000 trials resume within 10 tries, with no configuration change and no collateral change. With no
failure in 1,000 trials on a part, the per-interruption failure probability is below 0.3 percent at 95 percent
confidence (rule of three, 3/n). The OLD, NEW and ERROR counts are recorded as U1's answer. Fail (switch condition S2):
any trial whose slot stays refused after 10 tries, any configuration or lock byte changed, any collateral change, or
any resumed public key equal to P_before after a success report.

**Z-EXP-C, the panel's own sequence** (part of the panel firmware, MESHSAT-837, on the same rig): cut the Pico's own
supply at a random point of the wipe sequence 1,000 times, with an LED standing in for a slot enable; after every
restart the boot logic of 3.5 must end ZEROIZED with both KEKs changed, and the LED must never light before that. Then
100 uninterrupted wipes, each timed from the end of the hold: both KEKs verified within 1.5 s and the LED off within
3.0 s every time (the proposed REQ-035 lines of 3.4; the measured sequence time also replaces the script's 1 ms
software allowance). Then **the held-bus cases** (R7(a), and a failed part), with a second GPIO of the rig standing in
for a supervisor and a third output, read by a logic analyser, marking the start of step 5; 100 runs of each:
**C-H1**, SDA held low from before the hold; **C-H2**, SCL held low from before the hold, the case the RP2040's
controller cannot recover from by itself (RP2040 datasheet section 4.3.13.2 p. 459) and the one T_HAL exists for;
**C-H3**, SCL held low from the STOP of the first accepted send, so the library is inside its polling loop when the
bus goes and only the deadline D can end the timed phase. In every run: the step-5 marker comes by 1.5 s plus the
measured unwind (which replaces the script's 1 ms T_UNWIND) plus at most one journal write, and before the slot LED
goes off; the slot LED goes off within 3.0 s of the end of the hold (the step-0 alarm); no bus operation lasts longer
than T_HAL plus 1 ms (each one timed on the analyser by a GPIO the HAL toggles around it); the panel shows ZEROIZE
INCOMPLETE; and once the line is released, step 7 or the next boot completes the wipe with both KEKs changed. The
impersonation case of R7(d) is not shown by this rig and goes to the D-09 review.

What the three prove: P2, P3, P4 and P6 on the exact MPN in the exact configuration (A); P5, and P7's execution time
(B); the resume and the slot gating of D-03.3, the two pass lines, the HAL timeout, the timed-phase deadline and the
slot cut with the bus held (C). None of them is a test of the built kit: `TEST-PLAN.md:46` and REQ-035's acceptance
clauses stay the prototype's tests.

**Spend.** None was taken. The owner's D-09 route governs it: "nothing is spent beyond the voucher without a quote and
the owner's approval" (`CONOPS.md:400`, D-09). Prepared list for that route: one DM320118, one
MikroElektronika Secure SOIC click, ten ATECC608B-SSHDA-T, one Raspberry Pi Pico, one load-switch breakout, jumpers;
prices other than the SE's are TBD (not read). The SIDN voucher review (D-09) is the natural reviewer of sections 3
and 5 and of residuals R1 to R7.

## 6. The alternative, assessed before any dependent board is finalised

| | ATECC608B-SSHDA-T (fitted) | Infineon OPTIGA TPM SLB 9673 (TPM 2.0, I2C) | NXP EdgeLock SE050 (C2 or E2, HQ1) |
|---|---|---|---|
| Interface and address | I2C to 1 MHz, 7-bit 0x60 (E14) | I2C to 1 MHz, clock stretching required, 7-bit 0x2E (datasheet Rev 1.4 section 1.3 p. 8) | I2C target, T=1 over I2C APDUs (DS Rev 3.8 p. 6), 7-bit 0x48 (p. 8), clock stretching above 600 kHz (p. 9) |
| Kit-bus fit | reserved at 0x60 (`PANEL.md:143`) | 0x2E free in `PANEL.md:137-145`; the RP2040 master handles stretching (RP2040 datasheet 4.3.9 p. 451) | 0x48 free in `PANEL.md:137-145` |
| Package, supply, temperature | SOIC-8; 2.0 to 5.5 V; -40 to +85 C (SSH) | PG-UQFN-32 5 x 5 mm, 0.5 mm pitch, exposed pad (p. 9); 3.0 to 3.6 V or 1.65 to 1.95 V; -40 to +85 C (XU) or +105 C (AU) (p. 13) | HX2QFN20 3 x 3 mm; -25 to +85 C (1) or -40 to +105 C (2) (pp. 3, 5) |
| How a key is destroyed | GenKey mode 0x04 over an updatable slot (E2, E3) | TPM2_Clear: flushes storage and endorsement objects, deletes non-platform NV indices, "replace the existing SPS with a new value from the RNG"; needs Platform or Lockout authorisation and disableClear clear (TCG Library 1.59 Part 3 section 24.6 p. 294; Part 1 section 13.8 pp. 70-71, "Changing the SPS invalidates all objects in the Storage Hierarchy and they cannot be recreated", Part 1 p. 75); one persistent key by TPM2_EvictControl (Part 3 section 28.5 p. 335) | DeleteSecureObject: "Garbage collection is triggered, the memory will be freed on the next incoming APDU" (AN12413 Rev 2.12 section 4.7.4.5 p. 70); regeneration in place under POLICY_OBJ_ALLOW_GEN (p. 47). Whether freed memory is overwritten is not stated |
| Power loss in the erase | not documented (U1) | NV index: "A TPM is not required to maintain the integrity of the data in an NV Index if a power loss interrupts the write. After the interruption, the TPM should indicate that the Index no longer exists" (Part 1 section 37.7 p. 232); TPM2_Clear itself not stated | not stated |
| Host stack on the RP2040 | CryptoAuthLib, a six-function HAL to write | wolfTPM (tested with the SLB 9673 over I2C, `README.md:10`, `:239`, `:258-260` at `0f639565`; GPLv3 with exception or commercial, `LICENSE`); I2C needs its advanced-IO option (`README.md:233`); no RP2040 HAL, one IO callback to write (`README.md:220`) | NXP Plug & Trust middleware (DS Rev 3.8 p. 1 names it); an RP2040 port TBD |
| Board B change | none | U8 site: SOIC-8 to UQFN-32; VDD pins 1, 14, 22 each with 100 nF (two capacitors more than today); GND pins 2, 9, 23, 32 and the pad; TEST# (pin 20) to a static high; RST# (pin 17) to a spare expander output or its internal pull-up and a test point; I2C_PIRQ# (pin 18) unconnected; NC pins 6, 19, 21, 24 floating (p. 18) | U8 site: SOIC-8 to HX2QFN20 with its ENA pin (deep power-down) tied or driven (p. 9) |
| Other boards | none | none (same bus, same master, same supply `+3V3_DEV`) | none |
| Stock and price, JLCPCB 2026-09-26T12:27Z | C1518769: 2,344 at 0.9955 USD | every SLB 9673 row 0 in stock (C17668983 XU FW26.10 at 6.426 USD, C28980992 AU FW26.13 at 7.4766 USD, others); the SPI SLB 9672 has 2 to 20 in stock but SPI is not on the kit bus | C2659345 SE050C2HQ1: 41 at 3.8812 USD; C5190917 SE050E2HQ1: 644 at 5.4792 USD |

Reading of the table (INFERRED): the TPM's erase is the best specified of the three, in normative TCG text, and it is
the fallback D-03 already names; the SE050's delete is specified as a free, not as an overwrite. None of the three
publishes a physical-erasure guarantee (U2 is common to all). The TPM costs a board-B site change of one small part, a
heavier host stack with a copyleft-or-commercial licence, and today a part JLCPCB cannot supply.

**Switch conditions (taken by the session under the owner's standing rule of 26 September 2026).** The secure element
changes to the SLB 9673 on board B's U8 site if **S1** (Z-EXP-A fails) or **S2** (Z-EXP-B fails) holds. If the SLB 9673
is still unobtainable when a switch is due, the SE050E2HQ1 is assessed in its place with its own bench run (its delete
semantics are weaker on paper). No switch is due today.

## 7. Architecture feasibility blocker FB-ZER-1

**Statement.** ZEROIZE as ruled (D-03) requires that the fitted ATECC608B-SSHDA-T, in the configuration of section
3.1, lets the panel controller destroy the two key-encryption keys after every zone is locked, verifiably, with no
secret, resumably across a power loss, and never ending in a state where a key survives and cannot be destroyed.

| Part | Status | Closing evidence | Holds | Owner and bound |
|---|---|---|---|---|
| Mechanism exists on the part (P2, P3, P4, P6) | **CLOSED at desk level** (E1 to E9, E13) | this document; `drafts/zeroize/zer_config.py` PASS | nothing further at desk level | session; done 2026-09-26 |
| Mechanism works on the fitted MPN in this configuration | **OPEN** | Z-EXP-A pass record (script, log, part lot, config read-back) filed under `v2/docs/feasibility/evidence/` | board B layout entry, U8 site only | session runs it once the parts exist; the spend is the owner's under D-09; bound: section 5 |
| Interrupted power (P5, U1) | **OPEN** | Z-EXP-B pass record, with the OLD/NEW/ERROR counts | board B layout entry, U8 site only; the panel firmware's wipe | as above |
| Panel resume and slot gating (D-03.3) | **OPEN** | Z-EXP-C pass record | panel firmware (MESHSAT-837) | session, with the panel firmware |
| Wipe time bounded, every retry counted (P7) | **CLOSED at desk level as a bound**: 0.517 s nominal, 0.817 s worst case in specification; the part not answering 1.414 s and the bus held throughout 0.708 s, both ended by the retry policy; step 5 (the modules told) starts by 1.504 s whatever the part or the bus does (deadline D with T_HAL = 10 ms); the slot cut is a hardware alarm at 3.0 s. **OPEN on the part** | `drafts/zeroize/zer_budget.py` PASS (10 planted defects, each caught by its own check); Z-EXP-B step B0 and the Z-EXP-C timing and held-bus records | the proposed REQ-035 pass lines (1.5 s, 3.0 s) until B0 and Z-EXP-C confirm them | session |
| Only the panel commands the part (P8) | modules: **CLOSED by the netlist**; the three supervisors: **BOUNDED, not closed**, by firmware rule Z-C3 under the owner's D-13 verified-boot floor; **ACCEPTED AS RESIDUAL R7**, for review | `gen_sch_b.py:360`, `:571` (modules); `gen_sch_b.py:824` and E17 (supervisors); Z-C3 written into the supervisor firmware's requirements and its D-13 verified boot; the Z-EXP-C held-bus cases C-H1 to C-H3 for the fail-secure outcome of R7(a); R7(d) goes to the D-09 review | the supervisor firmware (it must implement Z-C3); no board | session, with the supervisor firmware; the D-09 reviewer for R7 |
| Physical remanence (U2) | **ACCEPTED AS RESIDUAL R2**, for review | D-09 security review note | nothing | D-09 reviewer |
| Address 0x60 (U4) | **OPEN, trivial** | Z-EXP-A A0 | nothing (the address is programmable before the configuration lock, DS20005927A p. 13, so a different factory value costs no board change) | session |

**Where it sits in the requirements registry** (pending merge in worktree `i1` at `d468613e`): it is assumption ASM-005
and session item S-35 (`REQUIREMENTS-TRACE.md:1089-1097`, `:1937`), which gate REQ-035 and REQ-038. ASM-005's
"TBD: confirmed from the full ATECC608B datasheet (under NDA ...) or by a bench test on a provisioned part" becomes:
supported by public Microchip documentation (E1 to E9); the bench confirmation is Z-EXP-A and Z-EXP-B.

**What this blocker does not hold.** Boards A, C, D, E and P: none of them carries a ZEROIZE part or conductor that
depends on the outcome (the toggle, its buffer and pull-ups exist in either case, `gen_sch_c.py:111-123`,
`gen_sch_a.py:573`). Board B's other circuits: the fallback touches only the U8 site. Board B's layout entry is held by
far larger items today (`B-FEASIBILITY.md`, decision 43), so this blocker is not on the critical path if Z-EXP-A and B
run before board B's layout entry.

**H743 condition 1 cross-check.** `v2/vendor/SOURCES.yaml:304-307` leaves open whether a ZEROIZE step needs an
STM32H753-only unit (CRYP, HASH, secure access). This design uses no supervisor function at all: the panel RP2040,
the ATECC608B and the modules' LUKS do the whole job, and Z-C3 only restricts what the supervisors' firmware may do on
the kit bus, which needs no H753-only unit. That reopen condition does not fire.

## 8. Residual risks stated with the design (not re-asked)

- **R1, a wipe requested with the kit unpowered.** The KEKs exist until the next power-up; an adversary who takes the
  kit and never powers it through the panel can move the SE to another I2C host and, with ReqAuth clear, compute the
  ECDH results for the drives' public keys. Binding the KEKs to the panel with ReqAuth would also gate their
  destruction (GenKey after lock needs the authorisation, DS20005927A p. 70), and the panel's QSPI flash (`gen_sch_c.py:129`)
  offers no protected storage for the binding secret, so the binding buys little against capture and costs the
  wipe's unconditional nature. Not taken; the D-09 review sees it.
- **R2, remanence** of overwritten EEPROM bits (U2).
- **R3, module RAM** until the slot cut, at most 3.0 s after the end of the hold, enforced by the step-0 hardware
  alarm whatever the secure element, the bus or a module does (3.4; the first cycle's cut, 2 s after DONE, did not
  bound this), and DRAM decay after it.
- **R4, the unlock chain** for modules not hosting bank 1 (3.3). A normal boot with the SE not answering powers the
  slots into the recovery state (3.5), so a failed SE or a stuck target on the kit bus costs the drives' unlock, which
  the owner accepted with D-03, and not the modules' power.
- **R5, the panel firmware bounds ZEROIZE.** Whoever can replace the panel's firmware can disable the wipe; the
  in-system update path from a module is recorded as W5-F4 in the architecture review. A panel-firmware integrity
  requirement is a question for the D-09 review; D-13 sets a secure-boot floor only for the supervisors and modules.
- **R6, ECDH results in the clear** on the kit bus of a live, non-zeroized kit (3.3).
- **R7, a supervisor driving the kit bus (for the D-09 security-review packet).** The three STM32H743 I/O supervisors
  share SDA and SCL with the secure element (`gen_sch_b.py:824`, U8 at `:750`), so "only the panel controller commands
  the part" (P8) holds for them only through firmware rule Z-C3 under the owner's D-13 floor of software-verified
  boot; a supervisor whose firmware breaks it can hold the bus, so the wipe ends ZEROIZE INCOMPLETE with both KEKs
  intact (the slots are still cut at 3.0 s), or run ECDH on slots 0 and 1 (ReqAuth is clear) and so obtain every
  drive's unlock secret, or answer in the secure element's place so that the panel records a verified wipe that did
  not happen. In detail (the round-6 circuit, committed in `458b2873`, moves them to PB6 and PB7, the I2C1 pins, which
  changes nothing here): a supervisor whose firmware breaks Z-C3 can (a) hold the bus, so the wipe cannot reach U8:
  the slots are still cut at 3.0 s by the step-0 alarm and the panel shows ZEROIZE INCOMPLETE, but both KEKs stay
  intact, which leaves a captured kit where R1 leaves it; (b) run ECDH on slots 0 and 1 itself (ReqAuth is clear) with
  any drive's public key E_d, which sits in the drive's LUKS2 header and crosses the kit bus in every unlock, and so
  obtain every drive's unlock secret; (c) without driving anything, read Z_A and Z_B of every unlock off the bus (R6,
  with the supervisor as the probe); and (d) impersonate the secure element: after the panel's wake it can put U8 back
  to sleep (word address 0x01, after which the part "ignores all subsequent I/O transitions until the next wake flag",
  DS20005927A Table 6-2 p. 43), or corrupt its commands, and answer at 0x60 itself. Nothing authenticates the SE's
  responses, so it can return fresh public keys for C0, C1, V0 and V1 and the panel records a verified DONE with both
  KEKs intact: this defeats P4's verification and the fail-secure boot row of 3.5 ("a wipe that cannot be proven never
  computes"), and the Z-EXP-C held-bus cases cannot show it (INFERRED from the bus protocol; not tried). A secret the
  supervisor obtains by (b) or (c) has a way out, so the limit this section gave in its second cycle ("no direct
  channel to send out") was wrong: its own pins reach the two CAN fabrics among the three supervisors (terminated on
  board B, `gen_sch_b.py:847-854`), the bank host selects and hub resets, the voted-bit read-backs, EMCON_HW and the
  kit bus (`gen_sch_b.py:816-828`), and no drive or network, but the design itself carries its status out: the
  supervisors publish status as I2C targets and the panel relays it to the cluster over its USB device
  (`ARCH-PCB-B-IOHA.md:96`), so a secret written into a status register leaves by the normal data flow; they also
  share the heartbeat lines HB1..3 with the panel (`gen_sch_b.py:823`; the panel's connector `gen_sch_b.py:767`, read
  at `gen_sch_c.py:126`). Mitigations for the reviewer, each a board change and so not taken for prototype 1 (D-03 is
  firmware and provisioning with no board change): a private I2C bus from the panel's second I2C controller (the
  RP2040 has two, RP2040 datasheet chapter 1 p. 8) to U8, which removes (a) to (d) for the supervisors but not a
  physical probe on that bus (R6); or a switch or buffer the panel opens to isolate the supervisors during a wipe and
  an unlock. Their conductor counts and parts are TBD. For (d) alone a configuration-only candidate exists, which the
  session recommends to the D-09 review and does not design here: an authenticated verification, GenKey creating a
  digest of the slot's public key in TempKey (mode bit 3, DS20005927A section 9.7 p. 71) and Sign in its internal mode
  signing that digest with an attestation key held in another slot (section 9.18 pp. 85-86; the signing slot needs
  SlotConfig.ReadKey bit 1, Table 2-6 p. 17), checked by the panel against the attestation key's recorded public key.
  An impersonator cannot sign, and a relay to the real U8 would attest the old key (INFERRED). Its slot, permissions and
  interaction with Z-C1 and Z-C2 need their own check in `zer_config.py` before it is taken. **Taken by the session
  under the owner's standing rule of 26 September 2026:** keep the shared bus for prototype 1, write Z-C3 into the
  supervisor firmware's requirements, prove the fail-secure outcome of (a) with the Z-EXP-C held-bus cases C-H1 to
  C-H3, and put R7 with both mitigations and the attested-verification candidate for (d) in the D-09 packet.

## 9. Recommendation (taken by the session under the owner's standing rule of 26 September 2026)

1. Keep the ATECC608B-SSHDA-T. D-03 stands as ruled, with no board change.
2. Provision it with the slot map of section 3.1 (KEK_A and KEK_B, SlotConfig 0x2084, KeyConfig 0x0013, all other bytes
   Microchip's tested image until key fill defines them under Z-C1 to Z-C3), generated and checked by
   `drafts/zeroize/zer_config.py`.
3. Enrol every drive and eMMC under both KEKs with one LUKS keyslot and no recovery keyslot (3.3); keep `/boot` and a
   recovery image unencrypted and secret-free.
4. Implement the wipe of 3.4 with invariants I1 to I5, the retry cap of 6 GenKey commands in the timed phase, the
   library bounds (`rx_retries` 1, polling cap 200 ms), the bus layer's two bounds (T_HAL = 10 ms on every operation
   through the Pico SDK's `_until` calls, and the deadline D = 1.5 s), the step-0 slot-cut alarm under its three
   firmware rules and the watchdog backstop, and the boot table of 3.5; propose to REQ-035 the pass lines of 1.5 s
   (KEKs destroyed and verified; worst case 0.817 s, nominal 0.517 s) and 3.0 s (slots cut, by the alarm) from the
   end of the hold, as computed by `drafts/zeroize/zer_budget.py`.
5. Run Z-EXP-A and Z-EXP-B on the fitted MPN before board B's layout entry; Z-EXP-C with the panel firmware.
6. Keep the SLB 9673 on board B's U8 site as the fallback under switch conditions S1 and S2, with the SE050E2 behind it
   if the TPM stays unobtainable.
7. Put sections 3, 5 and 8 in the D-09 security-review packet, R7 (a supervisor driving the kit bus) with its two
   board mitigations and the configuration-only attested verification for its impersonation case (d) among them.
8. Write firmware rule Z-C3 into the supervisor firmware's requirements: I2C target at 0x30 to 0x32 only, never a
   master, never address 0x60, under D-13's verified boot.
