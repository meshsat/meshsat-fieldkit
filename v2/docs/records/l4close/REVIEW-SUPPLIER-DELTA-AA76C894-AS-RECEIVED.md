# MeshSat supplier delta review — 4 October 2026

## Decision

**READY for supplier engineering review and quotation, with this review attached. Power-design closure and fabrication release remain BLOCKED.** The delta is more usable than the earlier handover: its entry page separates the tested revision, later branch work, rejected proposals, known defects and unperformed physical tests.

This review found **two additional P1 defects**: a reproducible loss of persistent slot lockout in the panel firmware, and an electrically inconsistent excitation/sensing method in the proposed battery-FET thermal test. Both have bounded corrections. Neither requires restarting the overall power investigation or reopening Layers 1–3.

This is a focused review of the delivered delta, not approval of every circuit, calculation or layer. No hardware was tested. Later branch fixes mentioned in the covering note were not supplied and are not accepted or rejected here.

## Artifact and verification boundary

| Item | Reviewed identity or result |
|---|---|
| Delta | `MESHSAT-SUPPLIER-DELTA-aa76c894-over-d834e6a7.zip` |
| Packaged revision, as declared | `aa76c89448ec943e3a37357ebc11ce3322fa4020` |
| ZIP size | 5,586,732 bytes |
| ZIP SHA-256 | `1bda2d7015704348724d009200691f967779a51514f798e91a9d2016df55fe16` |
| Baseline | `MESHSAT-SUPPLIER-HANDOVER-RELEASE-CANDIDATE-d834e6a7.zip` |
| Baseline SHA-256 | `29ed399ae8f7cb29801b9f6080725cc44cf06957430b8642440faf032e76cb7d` |
| Archive checks | CRC valid; no unsafe extraction paths or symbolic links; all 187 manifest entries match |
| Change inventory | All 184 declared changed files present: 96 added, 88 modified |
| Patch consistency | Git blob hashes of all 184 delivered changed files match the patch's new-file identifiers |
| Python syntax | 64 changed Python files parsed successfully |
| Firmware behavior | Isolated host fault-injection probe compiled against three unmodified delivered source files; two positive controls pass and two fault cases violate lockout persistence |

These checks establish internal consistency of the supplied artifacts. They do not authenticate the declared commit against a live repository or independently establish its full history.

The README reports a suite result of **2,937 passed, 0 failed, 15 skipped; 232/232 modules** at the packaged revision. The raw suite logs, the candidate evidence manifest and the later integration result are not included here, so those counts remain **reported evidence**, not independently reproduced results. The baseline plus delta is also not a complete firmware build tree or a standalone full numerical replay. I did not run the full firmware suite, repeat the project's three-pass release suite, or rerun the complete power and thermal solvers. A new large archive is not needed to act on the findings below.

## New findings

| ID | Priority / type | Confidence | Affected deliverable | What it prevents |
|---|---|---|---|---|
| DELTA-01 | P1 — confirmed software defect | High; executable counterexamples | Layer 12 panel firmware; Layer 5 FW-C05/FW-C02 persistence obligation | Claiming the delivered fault lockout survives the specified controller resets under the exercised flash-error cases |
| DELTA-02 | P1 — confirmed proposed-procedure defect | High; circuit topology | TP-E11-29 / E11-29 battery-FET thermal evidence | Executing the stated per-device heating and junction-sensing method as written |

These are review-local identifiers; map them once into the existing project register rather than creating duplicate workstreams.

### DELTA-01 — A failed flash write or interrupted rollover can remove a slot's lockout

**Evidence:**

- `v2/firmware/panel/src/slotstore.c`, lines 24–50: loading stops at the first all-`FF` record.
- The same file, lines 53–81: a failed program still advances the next-record offset. When full, the only store is erased before a replacement record is written.
- `v2/firmware/panel/src/panel_core.c`, lines 234–257: a non-power-on reset restores `SLOT_FAULT_OFF` only when the loaded record contains `SLOTREC_OFF`. An absent or older record instead produces `SLOT_OFF`.
- The same file, lines 261–270: a failed save is retried on a subsequent tick. Lines 592–597 allow a wanted slot in `SLOT_OFF` to restart under the normal sequencing policy.
- `v2/firmware/panel/src/hal_rp2040.c`, lines 340–367: the real adapter reports program/readback failure and erases the slot-store region as a whole.

**Failure A — successful retry hidden behind an empty gap.** A valid earlier record contains the spent retry but not the final lockout. The next program fails without changing flash. Saving the lockout again succeeds at the following record. On a controller reset, loading stops at the empty gap and never reads that successfully saved lockout. The slot returns to `SLOT_OFF`, eligible for an ordinary restart, instead of remaining `SLOT_FAULT_OFF`.

**Failure B — the last committed lockout is erased during rollover.** The store is full of valid lockout records. Erase succeeds, but programming the first replacement fails. A subsequent non-power-on controller reset finds no record and loses even the previously committed lockout.

The isolated probe uses a 4,096-byte flash abstraction, the original record code and CRC, and the original `panel_init()` with `power_on_reset=false`. Normal save/reset and successful rollover/reset pass. Both fault cases fail. This is a software counterexample, not a measured flash failure rate or a physical RP2040 test. The demonstrated result is loss of the lockout state; the normal restart path is traced in source rather than exercised as a complete hardware boot.

The existing `t_slot_store_torn_keeps_previous()` exercises a torn record and successful rollover, but does not cover the successful retry behind an entirely unwritten gap or failure after rollover erase.

**Bounded correction:** make retry/recovery and rollover preserve recoverable committed lockout state. Specify the conservative behavior when persistence cannot be trusted. Keep the wipe journal independent and preserve the contract's deliberate power-on/operator reset behavior. Merely retrying the failed write at a later offset does not fix the current loader.

**Acceptance:** regression tests reproduce both failures on the old code and pass on the correction; inject reset/failure at erase/program boundaries and after a successful retry; previously committed lockouts survive non-power-on resets; normal rollover, intended re-arming and the absence of a spurious pending wipe still pass. Assign this to the firmware owner at the next available slot. It does not block unrelated power-path or component work.

### DELTA-02 — The thermal coupon cannot independently excite and sense the three parallel body diodes

**Evidence:**

- `v2/docs/test-procedures/TP-E11-29.md`, lines 94–97 and 221–226, requires each FET to be heated through its body diode alone while the other two carry only their sense currents; each junction is inferred from its own calibrated forward voltage.
- Lines 128–143 and 189–199 put Q39, Q40 and Q42 on a common drain pour and a common source pour. Their gates remain tied to source during the test. No individual electrical isolation is defined.
- `v2/docs/records/l4e11/apply_gen_sch_a_charger.py`, line 109, confirms all three devices have the same drain and source nets in the draft.
- Nexperia's [BUK6Y10-30P datasheet, Rev. 5, 17 April 2020](https://assets.nexperia.com/documents/data-sheet/BUK6Y10-30P.pdf), page 2 pinning/symbol and page 6 source-drain diode characteristics, confirms the device topology. The conclusion below is this review's inference from that topology and the supplied wiring, not a manufacturer assessment of MeshSat.

**Why it fails:** with both terminals common, the three body diodes are electrically in parallel. Connecting three sources to those same nets does not independently set each diode's current. Four-wire taps remove lead-voltage error; they do not isolate a diode or establish its individual sense current. The proposed method consequently cannot assume known per-FET heating power or independently convert each measured voltage into junction temperature using the stated fixed-current calibration.

The procedure is already explicitly **not executable** while S29-R1's acceptance limit is corrected. This finding adds a fixture/method prerequisite; it does not allege that the test has run or that the current-sharing calculation itself proves a thermal failure. Updating only the K/W limit leaves this problem in place.

**Bounded correction:** the existing T2/procedure owner should provide an actual excitation/sensing fixture schematic or select a valid alternative method of determining individual junction temperatures. If isolating a device changes copper connectivity or thermal paths, justify transfer from the coupon to the final board instead of assuming equivalence.

**Acceptance:** show the current paths during calibration, heating and sensing; establish each required heating power and individual temperature measurement with uncertainty; reconcile the self/mutual thermal measurements and coupon-transfer rule. Keep the procedure non-executable until the method and corrected limits are reviewed and the supplier agrees to the setup. Route the correction into the existing focused review, not a new general architecture review.

## Prior findings and disclosed unfinished work

| Item | Disposition in this review |
|---|---|
| Earlier supplier-entry/addendum corrections | The delta front-loads the distinctions those reviews requested. No new reopening of those document findings is justified here. |
| FAN_OK and the 70% cooler cap | Rejected/withdrawn directions remain identifiable. Neither is accepted here as a fix. |
| F01/all-transmit and I-03/device rail | Explicitly OPEN. The later dated case correction is distinguished from the packaged revision. No claim of closure is made here. |
| Solar protection, B-R2, DD-3, DD-5, E11-37 and copper choice | Explicitly unresolved or conditional. This review does not change their engineering verdicts. |
| S29-R1 to S29-R8 | Known residues are named at entry; R5 is stated corrected. The remaining residues are not counted again as new findings. Later corrections still need their own evidence. |
| Negative collaborator reviews and coordinator checks | Both are retained and distinguished. A coordinator check has not been presented as an independent positive verdict. |
| Physical qualification | Still unperformed. Neither the software suite nor this review supplies it. |

The practical next handover is the existing baseline, this delta and this review. It can support an engineering quotation now; the supplier must be told which procedures remain drafts and which release decisions are blocked. No purchase, message to a supplier, test execution or fabrication is authorized by this report.

## Bounded continuation prompt for Claude Code

```text
Continue the approved plan with the existing three-worker limit. Incorporate the attached supplier-delta review without restarting the planning or power-review cycle.

1. File the report as received and map DELTA-01 and DELTA-02 once into the active register. First check whether newer committed work already addresses either; cite the actual correction and focused evidence if so. Otherwise keep them open.

2. At the next available slot, give DELTA-01 to the panel-firmware owner. Reproduce the attached empty-gap and rollover counterexamples, correct persistence/recovery, and add tests for non-power-on reset, rollover interruption, intended operator/POR re-arming and wipe-journal separation. Verify the actual fault-state behavior, not just successful file writes or CRC checks.

3. Fold DELTA-02 into the existing T2 / TP-E11-29 correction and its focused check. The common-source/common-drain coupon cannot independently heat and sense each body diode as currently specified. Produce a coherent fixture or alternative measurement method, including per-device observability and thermal transfer. Keep TP-E11-29 non-executable until both the method and corrected acceptance limits are agreed. Do not solve it merely by changing the K/W number or handing an impossible setup to the supplier.

4. Preserve healthy work and the current task dependencies, including T5b before the applicable ground-load verification. Keep the already reported F01, device-rail, solar, protection and thermal items in their existing workstreams. These two findings do not reopen Layers 1–3 or block unrelated deliverables.

5. Run focused checks on the changed implementation and procedure, then the existing integration gate when that change set is ready. Preserve the exact review verdicts and distinguish code evidence, engineering assumptions and physical qualification. Do not rerun a broad review or regenerate a large supplier archive solely to register these findings.

The supplier handover can carry this review immediately; power-design closure and fabrication remain blocked. At the next milestone, report the two findings' commit and check results, the remaining engineering critical path, and the next concrete layer deliverable. Continue autonomously; do not wait for another owner confirmation for these already authorized desk corrections. External contact, purchases and physical work retain their existing authorization boundaries.
```

## Appendix — isolated firmware reproduction

Save the C source below as `slotstore_probe.c` in a scratch directory. Compile it against the supplied source files without modifying them. From the repository/overlay root, adjusting the probe path:

```sh
gcc -std=c11 -O0 -Wall -Wextra -Werror -ffunction-sections -fdata-sections \
  -I v2/firmware/panel/include \
  /path/to/slotstore_probe.c \
  v2/firmware/panel/src/slotstore.c \
  v2/firmware/panel/src/zeroize.c \
  v2/firmware/panel/src/panel_core.c \
  -Wl,--gc-sections -o /path/to/slotstore_probe
/path/to/slotstore_probe
```

Observed output against the delivered source:

```text
CONTROL_NORMAL: invariant=PASS
CONTROL_ROLLOVER: invariant=PASS
EMPTY_GAP: failed=-1 retry=0 load=0 expected=0x03 actual=0x01 reset_state=0 expected_state=4 invariant=FAIL
ROLLOVER: failed=-1 load=1 expected_preserved=0x03 actual=0x00 reset_state=0 expected_state=4 invariant=FAIL
exit_code=1
```

The nonzero exit is expected on the reviewed code. This narrow diagnostic demonstrates the two reported cases; it is not a replacement for production regression tests or hardware qualification.

```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "panel.h"

static uint8_t flash_bytes[4096];
static int fail_next_program;

static int read_store(void *ctx, uint32_t off, uint8_t *buf, unsigned len)
{
    (void)ctx;
    if (off + len > sizeof flash_bytes)
        return -1;
    memcpy(buf, flash_bytes + off, len);
    return 0;
}

static int program_store(void *ctx, uint32_t off, const uint8_t *buf, unsigned len)
{
    (void)ctx;
    if (fail_next_program) {
        fail_next_program = 0;
        return -1;
    }
    if (off + len > sizeof flash_bytes)
        return -1;
    for (unsigned i = 0; i < len; ++i)
        flash_bytes[off + i] &= buf[i];
    return 0;
}

static int erase_store(void *ctx)
{
    (void)ctx;
    memset(flash_bytes, 0xff, sizeof flash_bytes);
    return 0;
}

static int read_empty_wipe(void *ctx, uint32_t off, uint8_t *buf, unsigned len)
{
    (void)ctx;
    (void)off;
    memset(buf, 0xff, len);
    return 0;
}

static panel_ops_t ops = {
    .slots = { .read = read_store, .program = program_store, .erase = erase_store, .size = sizeof flash_bytes },
    .zer = { .flash_read = read_empty_wipe, .flash_size = 8192 }
};

static void init_store(panel_t *p)
{
    memset(p, 0, sizeof *p);
    p->ops = &ops;
    memset(flash_bytes, 0xff, sizeof flash_bytes);
    fail_next_program = 0;
}

static int after_controller_reset(void)
{
    panel_t q;
    const bool held[3] = { false, true, true };
    bool drive[3];
    panel_init(&q, &ops, 0, false, held, false, drive);
    return q.slot[0].state;
}

int main(void)
{
    panel_t p;
    uint8_t prior[3] = { SLOTREC_CYCLED, 0, 0 };
    uint8_t blocked[3] = { SLOTREC_CYCLED | SLOTREC_OFF, 0, 0 };
    uint8_t update[3] = { SLOTREC_CYCLED | SLOTREC_OFF, SLOTREC_CYCLED, 0 };
    uint8_t actual[3];
    int errors = 0;

    init_store(&p);
    panel_slot_store_save(&p, prior);
    int control_saved = panel_slot_store_save(&p, blocked);
    int control_loaded = panel_slot_store_load(&p, actual);
    int control_state = after_controller_reset();
    int control_ok = control_saved == 0 && control_loaded == 0 && actual[0] == blocked[0] && control_state == SLOT_FAULT_OFF;
    printf("CONTROL_NORMAL: invariant=%s\n", control_ok ? "PASS" : "FAIL");
    errors += !control_ok;

    init_store(&p);
    for (unsigned i = 0; i < sizeof flash_bytes / 16; ++i)
        panel_slot_store_save(&p, blocked);
    control_saved = panel_slot_store_save(&p, update);
    control_loaded = panel_slot_store_load(&p, actual);
    control_state = after_controller_reset();
    control_ok = control_saved == 0 && control_loaded == 0 && actual[0] == blocked[0] && control_state == SLOT_FAULT_OFF;
    printf("CONTROL_ROLLOVER: invariant=%s\n", control_ok ? "PASS" : "FAIL");
    errors += !control_ok;

    init_store(&p);
    panel_slot_store_save(&p, prior);
    fail_next_program = 1;
    int failed = panel_slot_store_save(&p, blocked);
    int retried = panel_slot_store_save(&p, blocked);
    int loaded = panel_slot_store_load(&p, actual);
    int reset_state = after_controller_reset();
    int bad = failed != 0 && retried == 0 && loaded == 0 && actual[0] != blocked[0] && reset_state != SLOT_FAULT_OFF;
    printf("EMPTY_GAP: failed=%d retry=%d load=%d expected=0x%02x actual=0x%02x reset_state=%d expected_state=%d invariant=%s\n",
           failed, retried, loaded, blocked[0], actual[0], reset_state, SLOT_FAULT_OFF, bad ? "FAIL" : "PASS");
    errors += bad;

    init_store(&p);
    for (unsigned i = 0; i < sizeof flash_bytes / 16; ++i)
        panel_slot_store_save(&p, blocked);
    fail_next_program = 1;
    failed = panel_slot_store_save(&p, update);
    loaded = panel_slot_store_load(&p, actual);
    reset_state = after_controller_reset();
    bad = failed != 0 && actual[0] != blocked[0] && reset_state != SLOT_FAULT_OFF;
    printf("ROLLOVER: failed=%d load=%d expected_preserved=0x%02x actual=0x%02x reset_state=%d expected_state=%d invariant=%s\n",
           failed, loaded, blocked[0], actual[0], reset_state, SLOT_FAULT_OFF, bad ? "FAIL" : "PASS");
    errors += bad;
    return errors ? 1 : 0;
}
```
