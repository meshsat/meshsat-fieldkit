#!/usr/bin/env python3
"""ZEROIZE wipe time budget on the kit I2C bus: nominal, worst case with every retry the design allows, the fault
cases the retry policy is designed for (the part not answering, the bus held), and the deadline at which the timed
phase ends whatever the part or the bus does; checked against the proposed REQ-035 pass lines.

DRAFT for v2/docs/feasibility/ZEROIZE.md section 3.4 (MESHSAT-1357). Prototype design, nothing built, nothing measured.
Run: python3 zer_budget.py   (prints the budget and exits 0 when every check holds; the self-test plants defects and
requires each to be caught by the check that names it)

Why this exists. First cycle: "about 0.51 s worst case" counted no retry while its own step 2 allowed ten GenKey tries
per slot. Second cycle: the bound at which the timed phase "gives up" modelled a part that takes every send and then
refuses every poll, and was called good for "the bus not answering"; on a held bus every HAL operation ends at the
HAL's own timeout, which was not declared, and a bus held after an accepted send makes each poll cost a HAL timeout.
Now the HAL timeout is a declared input, both held-bus cases are computed, and a deadline in the panel's HAL ends the
timed phase whatever the part or the bus does.

Provenance of every number (nothing here is a convenient value; each INFERRED item says so):
  F_I2C       100 kHz, the top of I2C standard mode. The kit bus clock is not declared anywhere in the tree (PANEL.md
              section 7 gives addresses only). CryptoAuthLib drops to 100 kHz for the wake itself
              (lib/calib/calib_basic.c:54-63) and its non-Linux default is 400 kHz (lib/atca_cfgs.c:52-56), so 100 kHz
              is the lowest clock the library uses, and the design requires the panel to run the bus at 100 kHz or
              faster. Every transfer time below is then an upper bound; a slower clock is a new input here.
  BYTE        9 bit times per byte (8 data + ACK) and 2 bit times per transaction for START and STOP: DS20005927A
              Figure 6-4 and Table 6-1, p. 42.
  WAKE        CryptoAuthLib v3.8.0 calib_wakeup_i2c (lib/calib/calib_basic.c:37-105): a 2-byte write to address 0
              (drives SDA low for tWLO), a wait of wake_delay = 1500 us (lib/atca_cfgs.c:58; tWHI minimum 1500 us,
              DS40002239A Table 2-2 p. 7), then a 4-byte read of the wake response (address + 4 bytes).
  SEND        address + word address 0x03 + the command group (DS20005927A Table 6-1 p. 42). A GenKey group in mode
              0x04 or 0x00 is 7 bytes: count, opcode, param1, param2 (2), CRC (2) (Table 9-1 p. 55; Table 9-20 p. 70,
              no OtherData in these modes).
  POLL        CryptoAuthLib polls (the ATECC608B supports only polling, lib/calib/calib_execution.c:37-39): it waits
              ATCA_POLLING_INIT_TIME_MSEC = 1 ms, then tries a receive every ATCA_POLLING_FREQUENCY_TIME_MSEC = 2 ms,
              at most ATCA_POLLING_MAX_TIME_MSEC / 2 + 1 times (lib/calib/calib_execution.c:506-507, :571-590;
              defaults lib/hal/atca_hal.h:176-187, each under #ifndef so the panel build may override it). A busy
              part does not ACK its address (DS20005927A section 6.5, p. 44), so a refused poll costs the reset write
              of calib_execute_receive (address + 0x00, 2 bytes) on a free bus, and one HAL operation on a held one.
  RECEIVE     calib_execute_receive (lib/calib/calib_execution.c:378-475): word address 0x00 (2 bytes), read the
              count (address + 1), read the rest (address + count - 1). GenKey returns 64 bytes of public key, so the
              group is 67 bytes (Table 9-21 p. 70; Table 9-1 p. 55), and the longest single transfer of a command is
              that 67-byte read.
  IDLE        calib_idle writes word address 0x02 (lib/calib/calib_basic.c:143-169; DS20005927A Table 6-2 p. 43).
              calib_execute_command wakes before and idles after every command (calib_execution.c:524-529, :623-627).
  T_EXEC      GenKey 115 ms maximum at clock divider 0 (ChipMode 0x00 in the image): CryptoAuthLib's ATECC608-M0
              table (lib/calib/calib_execution.c:124-146). That table is the ATECC608A's; the ATECC608B summary lists
              the commands whose timing changed from the ATECC608A as Verify, SecureBoot, Lock and Read
              (DS40002239A section 3.1 p. 12), not GenKey. SUPPORTED, not VERIFIED, for the ATECC608B; Z-EXP-B
              step B0 measures it on the fitted part and this script takes the measured value.
  JOURNAL     one W25Q16JV page program, tPP maximum 3 ms (Revision H, PDF page 63, printed page 62), twice in the
              timed phase (PENDING before the first command, DONE after the last).
  SOFTWARE    1 ms per command for the panel's own code between bus operations: an INFERRED allowance, not a
              measurement; Z-EXP-C replaces it with the measured sequence time.
  T_HAL       10 ms, the most one HAL bus operation (the panel's hal_i2c_send or hal_i2c_receive) may take: a DESIGN
              input. The Pico SDK's blocking calls have no timeout (i2c_write_blocking passes none, pico-sdk 2.3.1
              src/rp2_common/hardware_i2c/i2c.c:245-247, and its wait for a byte to leave the shift register then ends
              only when the byte has left, :170-176; the header lists no timeout return, include/hardware/i2c.h:338-349),
              and for SCL held low "there is no effective method to overcome this problem but to reset the bus using
              the hardware reset signal" (RP2040 datasheet section 4.3.13.2 p. 459). The panel's HAL therefore uses
              i2c_write_blocking_until and i2c_read_blocking_until (i2c.h:266-295; PICO_ERROR_TIMEOUT, i2c.c:222-224)
              with a limit of the earlier of now + T_HAL and the deadline below, and runs i2c_init again after a
              timeout (it puts the controller block through reset, i2c.c:32-34). T_HAL must exceed the longest
              legitimate transfer, the 67-byte read (6.05 ms at 100 kHz), by MIN_MARGIN, or every response read at
              100 kHz would time out.
  HELD BUS    what CryptoAuthLib does when no bus operation succeeds: calib_wakeup_i2c ignores the result of its wake
              write (calib_basic.c:79) and still reads (:87-90), up to rx_retries + 1 times (:45, :102);
              calib_execute_command repeats wake-and-send up to rx_retries + 1 times while the send reports
              ATCA_RX_NO_RESPONSE (calib_execution.c:521-563), then idles (:623-627). Per command, every operation at
              T_HAL: (R+1)*((R+1)*(2*T_HAL + wake_delay) + T_HAL) + T_HAL + software. A HAL that reports ATCA_COMM_FAIL
              instead, as the vendor's ESP32 HAL does (lib/hal/hal_esp32_i2c.c:256-258), ends the send loop after one
              round (calib_execution.c:552-559), so this is the upper bound over HAL return codes.
  DEADLINE    D_TIMED = 1.5 s after the end of the hold, the KEK pass line: a DESIGN input. From the deadline the
              panel's HAL fails every bus operation at once and its atca_delay_ms and atca_delay_us (the timer functions
              the platform provides, lib/hal/atca_hal.h:209-216) return without waiting, so a library call in progress
              unwinds through its own bounded loops and the wipe issues no further command. T_UNWIND = 1 ms for that
              unwind is INFERRED (a few hundred calls that each return at once, on a 125 MHz core); Z-EXP-C measures it.
              Step 4 appends DONE only for a verification that finished before D, so at most one journal write
              (T_JOURNAL) follows D; step 5 then starts by D + T_UNWIND + T_JOURNAL whatever the part or the bus does.
  DESIGN      choices this document makes (taken by the session under the owner's standing rule of 26 Sep 2026):
              RX_RETRIES = 1 in the panel's ATCAIfaceCfg (the field of lib/atca_iface.h:178; the library default is
              20, lib/atca_cfgs.c:59); ATCA_POLLING_MAX_TIME_MSEC = 200 (default 2500), 74 percent above T_EXEC (checked
              below); at most 6 GenKey commands in the timed phase (the 4 of the nominal sequence plus 2 retries,
              shared); T_HAL = 10 ms; D_TIMED = 1.5 s; the slot cut is a hardware timer alarm 3.0 s after the end of
              the hold, independent of the bus; step 5 (the modules told to drop their keys) gets at least
              MODULE_WINDOW_MIN_S = 1.0 s before the cut.
"""
import math
import sys

F_I2C = 100_000                       # Hz; the lowest clock the design allows (see F_I2C above)
BIT_US = 1e6 / F_I2C
BYTE_US = 9 * BIT_US
FRAME_US = 2 * BIT_US                 # START + STOP

WAKE_DELAY_MS = 1.5                   # atca_cfgs.c:58; tWHI min, DS40002239A Table 2-2 p. 7
GENKEY_GROUP = 7                      # count + opcode + p1 + p2(2) + crc(2), Table 9-1 / 9-20
GENKEY_RESPONSE = 67                  # count + 64 + crc(2), Table 9-21 / 9-1
POLL_INIT_MS = 1                      # atca_hal.h:177-179
POLL_FREQ_MS = 2                      # atca_hal.h:181-183
T_EXEC_GENKEY_MS = 115                # calib_execution.c:124-146 (608-M0); SUPPORTED for the 608B, measured by Z-EXP-B B0
T_JOURNAL_MS = 3                      # W25Q16JV tPP max
T_SOFTWARE_MS = 1                     # INFERRED allowance per command
T_UNWIND_MS = 1                       # INFERRED: the library unwinding after the deadline

# design choices (section 3.4)
RX_RETRIES = 1
POLL_MAX_MS = 200
T_HAL_MS = 10                         # the most one HAL bus operation may take
D_TIMED_S = 1.5                       # the timed phase's deadline, from the end of the hold
N_TIMED = 6                           # GenKey commands allowed in the timed phase (nominal 4 + 2 retries)
N_NOMINAL = 4                         # C0, C1, V0, V1
TRIES_PER_SLOT_TOTAL = 10             # mode-0x04 tries per slot, timed phase and untimed continuation together
PASS_KEKS_S = 1.5                     # proposed REQ-035 line: both KEKs destroyed and verified
PASS_CUT_S = 3.0                      # proposed REQ-035 line: slots cut (hardware alarm)
MODULE_WINDOW_MIN_S = 1.0             # step 5 starts at least this long before the cut
MIN_MARGIN = 0.25                     # margin every timing choice must keep over the figure it covers


def xfer_ms(nbytes):
    return (nbytes * BYTE_US + FRAME_US) / 1000.0


LONGEST_TRANSFER_MS = xfer_ms(1 + GENKEY_RESPONSE - 1)       # the 67-byte response read


def per_command(t_exec_ms=T_EXEC_GENKEY_MS, rx_retries=RX_RETRIES, poll_max_ms=POLL_MAX_MS, t_hal_ms=T_HAL_MS):
    """Wall-clock time of ONE GenKey command in ms, for each case the budget names."""
    r1 = rx_retries + 1
    polls = poll_max_ms // POLL_FREQ_MS + 1
    t_wake = xfer_ms(2) + WAKE_DELAY_MS + xfer_ms(1 + 4)
    t_send = xfer_ms(2 + GENKEY_GROUP)
    t_poll_free = POLL_FREQ_MS + xfer_ms(2)
    t_recv = xfer_ms(2) + xfer_ms(1 + 1) + xfer_ms(1 + GENKEY_RESPONSE - 1)
    t_idle = xfer_ms(2)
    tail = t_recv + t_idle + T_SOFTWARE_MS
    # in spec: the part answers by t_exec, the answer is seen at the next poll
    t_wait = max(POLL_INIT_MS, t_exec_ms) + t_poll_free
    nominal = t_wake + t_send + t_wait + tail
    # every library-level retry taken on a free bus: (R+1) wake calls of (R+1) attempts each, (R+1) sends
    front_max = r1 * (r1 * t_wake + t_send)
    worst = front_max + t_wait + tail
    # the part takes the command and never answers, bus free: the library polls to its cap and reads nothing
    nack = front_max + POLL_INIT_MS + polls * t_poll_free + t_idle + T_SOFTWARE_MS
    # the bus held for the whole command: every HAL operation ends at t_hal, nothing is ever sent
    held = r1 * (r1 * (2 * t_hal_ms + WAKE_DELAY_MS) + t_hal_ms) + t_hal_ms + T_SOFTWARE_MS
    # the bus held from just after an accepted send: every poll and the idle end at t_hal
    held_after_send = t_wake + t_send + POLL_INIT_MS + polls * (t_hal_ms + POLL_FREQ_MS) + t_hal_ms + T_SOFTWARE_MS
    # any bus behaviour at all: every operation of the fronts at t_hal, the send accepted last, every poll at t_hal
    any_bus = r1 * (r1 * (2 * t_hal_ms + WAKE_DELAY_MS) + t_hal_ms) + POLL_INIT_MS + polls * (t_hal_ms + POLL_FREQ_MS) \
        + t_hal_ms + T_SOFTWARE_MS
    return {"nominal": nominal, "worst": worst, "nack": nack, "held": held,
            "held_after_send": held_after_send, "any_bus": any_bus}


def sequence(t_exec_ms=T_EXEC_GENKEY_MS, rx_retries=RX_RETRIES, poll_max_ms=POLL_MAX_MS, n_timed=N_TIMED,
             t_hal_ms=T_HAL_MS, deadline_s=D_TIMED_S):
    """t_hal_ms=math.inf models a HAL without a timeout; deadline_s=None models no deadline. The deadline is
    enforced by the HAL's own timed operations, so it cannot hold without a HAL timeout."""
    c = per_command(t_exec_ms, rx_retries, poll_max_ms, t_hal_ms)
    journal = 2 * T_JOURNAL_MS

    def phase(per_cmd_ms, n):
        return (n * per_cmd_ms + journal) / 1000.0

    untruncated = phase(c["any_bus"], n_timed)
    enforced = deadline_s is not None and math.isfinite(t_hal_ms)
    end = min(untruncated, deadline_s + (T_UNWIND_MS + T_JOURNAL_MS) / 1000.0) if enforced else untruncated
    return {
        "per_command_ms": c,
        "nominal_s": phase(c["nominal"], N_NOMINAL),
        "worst_in_spec_s": phase(c["worst"], n_timed),
        "nack_s": phase(c["nack"], n_timed),
        "held_s": phase(c["held"], n_timed),
        "held_after_send_s": phase(c["held_after_send"], n_timed),
        "untruncated_s": untruncated,
        "deadline_s": deadline_s if enforced else None,
        "timed_phase_end_s": end,
        "t_hal_ms": t_hal_ms,
        "poll_max_ms": poll_max_ms,
        "t_exec_ms": t_exec_ms,
        "n_timed": n_timed,
        # the first cycle's policy, for the record: up to 10 creates per slot in the timed sequence plus 2 verifies
        "previous_policy_worst_s": phase(c["nominal"], 2 * TRIES_PER_SLOT_TOTAL + 2),
    }


def check(r, pass_keks=PASS_KEKS_S, pass_cut=PASS_CUT_S):
    """Return a list of (key, message) for every check that fails."""
    fails = []

    def need(key, cond, what):
        if not cond:
            fails.append((key, what))

    need("nominal_count", r["n_timed"] >= N_NOMINAL, "the timed phase must allow at least the nominal four commands")
    need("retries_counted", r["worst_in_spec_s"] > r["nominal_s"],
         "the worst case must include retries (it equals the nominal)")
    need("kek_line", pass_keks >= r["worst_in_spec_s"] * (1 + MIN_MARGIN),
         "KEK pass line %.2f s is not %.0f percent above the in-spec worst case %.3f s"
         % (pass_keks, 100 * MIN_MARGIN, r["worst_in_spec_s"]))
    need("poll_cap", r["poll_max_ms"] >= r["t_exec_ms"] * (1 + MIN_MARGIN),
         "polling cap %d ms is not %.0f percent above the execution time %d ms, so a command the part completes "
         "in specification could be abandoned" % (r["poll_max_ms"], 100 * MIN_MARGIN, r["t_exec_ms"]))
    need("hal_floor", r["t_hal_ms"] >= LONGEST_TRANSFER_MS * (1 + MIN_MARGIN),
         "HAL timeout %.1f ms is not %.0f percent above the longest legitimate transfer %.2f ms, so a response read "
         "at 100 kHz could time out" % (r["t_hal_ms"], 100 * MIN_MARGIN, LONGEST_TRANSFER_MS))
    need("hal_timeout", math.isfinite(r["t_hal_ms"]),
         "the HAL has no timeout: on a bus held low (SCL) a blocking transfer never returns")
    need("deadline", r["deadline_s"] is not None, "the timed phase has no enforced deadline")
    if r["deadline_s"] is not None:
        need("deadline_covers_spec", r["deadline_s"] >= r["worst_in_spec_s"] * (1 + MIN_MARGIN),
             "the deadline %.2f s would cut short an in-spec wipe (worst case %.3f s)"
             % (r["deadline_s"], r["worst_in_spec_s"]))
        # the fault cases the retry policy is designed for run their whole policy before the deadline, so the policy,
        # not the deadline, is what ends them; the deadline only ends what the model does not name
        for key, name in (("nack_s", "the part not answering (NACK), bus free"),
                          ("held_s", "the bus held for every command")):
            need("fault_fits_" + key, r[key] <= r["deadline_s"],
                 "%s takes %.3f s, past the %.2f s deadline" % (name, r[key], r["deadline_s"]))
    need("order", r["timed_phase_end_s"] + MODULE_WINDOW_MIN_S <= pass_cut,
         "step 5 can start as late as %.3f s, which leaves the modules less than %.1f s before the %.1f s cut "
         "(D-03's order: told before their power goes)" % (r["timed_phase_end_s"], MODULE_WINDOW_MIN_S, pass_cut))
    need("cut_after_keks", pass_cut > pass_keks, "the slot cut must come after the KEK line")
    return fails


def self_test():
    """Plant each defect the reviews caught, or could catch, and require the check that names it to fire."""
    planted = [
        ("no retry counted at any level (the first cycle's defect)",
         sequence(n_timed=N_NOMINAL, rx_retries=0), {}, "retries_counted"),
        ("KEK pass line at the first cycle's 1.0 s", sequence(), {"pass_keks": 1.0}, "kek_line"),
        ("library default polling cap of 2500 ms", sequence(poll_max_ms=2500), {}, "fault_fits_nack_s"),
        ("library default of 20 bus retries", sequence(rx_retries=20), {}, "kek_line"),
        ("timed phase with ten tries per slot", sequence(n_timed=2 * TRIES_PER_SLOT_TOTAL + 2), {}, "kek_line"),
        ("polling cap below the execution time (100 ms against 115 ms)", sequence(poll_max_ms=100), {}, "poll_cap"),
        ("no HAL timeout (the Pico SDK's blocking calls)", sequence(t_hal_ms=math.inf), {}, "hal_timeout"),
        ("a large HAL timeout (200 ms, the vendor ESP32 HAL's value)", sequence(t_hal_ms=200), {}, "fault_fits_held_s"),
        ("a HAL timeout below the longest transfer (5 ms against 6.05 ms)", sequence(t_hal_ms=5), {}, "hal_floor"),
        ("no timed-phase deadline (the second cycle's model)", sequence(deadline_s=None), {}, "order"),
    ]
    missed = []
    for name, r, kw, key in planted:
        fired = {k for k, _ in check(r, **kw)}
        if key not in fired:
            missed.append("%s (expected %s, fired %s)" % (name, key, sorted(fired) or "nothing"))
    return len(planted), missed


def main():
    r = sequence()
    c = r["per_command_ms"]
    print("one GenKey command at %d kHz (ms): nominal %.2f, worst in spec %.2f, NACK to the %d ms polling cap %.2f,"
          % (F_I2C // 1000, c["nominal"], c["worst"], POLL_MAX_MS, c["nack"]))
    print("  bus held throughout %.2f, bus held after the send %.2f, any bus behaviour %.2f (HAL timeout %d ms)"
          % (c["held"], c["held_after_send"], c["any_bus"], T_HAL_MS))
    print("longest single transfer: %.2f ms" % LONGEST_TRANSFER_MS)
    print("nominal sequence (C0 C1 V0 V1, no retry):                  %.3f s" % r["nominal_s"])
    print("worst case in spec (%d commands, every retry taken):         %.3f s" % (N_TIMED, r["worst_in_spec_s"]))
    print("the part not answering (NACK), bus free, %d commands:        %.3f s" % (N_TIMED, r["nack_s"]))
    print("the bus held for every command, %d commands:                 %.3f s" % (N_TIMED, r["held_s"]))
    print("the bus held after each send, %d commands (untruncated):     %.3f s" % (N_TIMED, r["held_after_send_s"]))
    print("any bus behaviour, %d commands (untruncated):                %.3f s" % (N_TIMED, r["untruncated_s"]))
    print("step 5 starts, whatever the part or the bus does, by:       %.3f s (deadline %.1f s + unwind + DONE write)"
          % (r["timed_phase_end_s"], D_TIMED_S))
    print("previous policy (10 creates per slot in the sequence):      %.3f s  (for the record)"
          % r["previous_policy_worst_s"])
    print("pass lines: KEKs destroyed and verified <= %.1f s; slots cut <= %.1f s (hardware alarm); modules told "
          "at least %.1f s before the cut" % (PASS_KEKS_S, PASS_CUT_S, MODULE_WINDOW_MIN_S))
    fails = check(r)
    n, missed = self_test()
    for _, f in fails:
        print("FAIL:", f)
    for m in missed:
        print("SELF-TEST MISSED:", m)
    if fails or missed:
        return 1
    print("PASS: %d planted defects caught, each by its own check; 0 checks failed" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
