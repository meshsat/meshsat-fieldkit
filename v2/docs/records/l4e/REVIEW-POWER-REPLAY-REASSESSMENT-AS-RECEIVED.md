# MeshSat V2 — independent power-replay reassessment

**Date:** 1 October 2026  
**Artifact:** `MESHSAT-POWER-REPLAY-c1321ebc.zip`  
**Replayed revision:** `c1321ebcf43dd47e45da8636f290dcf684869aaf`  
**Decision:** closure of power-architecture review finding **L4-R03**, the missing standalone replay dependencies.

## Verdict

**READY for the specified offline replay. L4-R03 is independently CLOSED.**

The package supplies the missing model files, board-A BOM, vendor inputs and Git objects. I ran its unmodified replay from a fresh work directory with network access blocked. It exited successfully and reproduced the supplied 50,066-byte result exactly. No files from the earlier project exports were needed.

This closes a real handover defect. It establishes reproducibility of the supplied calculations; it does not validate every modelling assumption, demonstrate hardware performance, or complete Layer 4.

I also confirmed one separate **P2 tracing defect** that can generate excessive logs. It is inactive during the normal replay and does not undo this closure.

## Received files and scope

Received:

- The power-replay ZIP and its checksum.
- The checksum for `MESHSAT-LAYER3-REVIEW-c1321ebc.zip`.

**The Layer 3 review ZIP itself was not attached.** Its checksum is not sufficient to review the amendment, acceptance binding, tests or full handover package. L3-R01 through L3-R05 cannot be independently closed by this reassessment.

The power companion targets `c1321ebc`; I have not inspected the later main revision `e3c99df8` or the separate L4-E4 circuit-change drafts through this package.

## Independent verification

| Check | Observed result |
|---|---|
| ZIP SHA-256 | Matches the supplied checksum: `514ce797b09b521ad5a89ccf537ca1bda5385beb1f615400c887f32d51524bea` |
| Archive | 21,322,720 compressed bytes; 117 entries; CRC clean; no traversal paths or symlinks |
| Internal manifest | All 116 listed payloads match |
| File inventory | 99 tracked files and seven held vendor documents; all listed SHA-256 values match |
| Tracked-source provenance | All 99 supplied tracked files have blob hashes matching the supplied `c1321ebc` tree |
| Git pack | `git verify-pack` succeeds |
| Historical file reads | All nine `LOOKUPS.tsv` entries resolve and return the expected contents |
| Environment | Python 3.12.14 with PyYAML, Git 2.51.1, installed PDF extraction tools |
| Replay | Exit 0; output matches byte for byte; reported Python socket events: 0 |
| Output SHA-256 | Actual and expected: `59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d` |
| Original inputs after execution | No manifest-covered source file changed |

Observed replay output:

```text
OFFLINE CHECK: IPv4, IPv6 and child-process socket creation blocked
HEAD is c1321ebcf43dd47e45da8636f290dcf684869aaf
replay exit 0
l4e_replay.out reproduced byte for byte
socket events logged: 0
REPLAY: PASS at c1321ebcf43dd47e45da8636f290dcf684869aaf
```

### Offline method and its boundary

The documented `unshare -rn` method could not initialize here: this execution environment lacks the accessible `/proc/self/uid_map` required by that invocation. That is a limitation of this review environment, not a package failure.

Instead, I applied an additional kernel seccomp filter to the replay process and its descendants. It blocks socket creation and network operations. Before starting the package, checks confirmed that IPv4 and IPv6 sockets were denied and a child Python process inherited the denial. The package scripts and model were not altered. The run used a clean environment with no inherited Git object-store overrides and global/system Git configuration disabled.

The included bounded Git pack is sufficient for this replay. It deliberately omits most historical file blobs and is not a replacement for a complete development repository. That is consistent with the documented purpose.

No full project test suite, KiCad generation, electrical simulation beyond the supplied models, or hardware test was performed.

## New finding: PR-01 — file tracing recursively records its own logging

**Priority:** P2; confirmed defect, high confidence.  
**Location:** `measurement/sitecustomize.py`, lines 8–11, with the same logging pattern at line 15.  
**Affected mode:** tracing with `OPENLOG` enabled.

The `open` audit handler writes its record using `open(_LOG, "a")`. That operation raises another `open` event and re-enters the handler. The broad exception handler eventually swallows the recursion failure rather than preventing re-entry. Python documents the audit event raised by `open()` in its [built-in function reference](https://docs.python.org/3.12/library/functions.html#open).

I reproduced the defect in a bounded subprocess using the supplied hook and one deliberate read of `/dev/null`:

| Measurement | Result |
|---|---:|
| Intended `/dev/null` opens recorded | 1 |
| Logger's own log-file opens recorded | 995 |
| Total log lines | 996 |
| Resulting log size | 84,585 bytes |
| Process exit | 0 |

This is a credible explanation for severe log amplification during dependency measurement. It could have contributed to the previously reported 6.8 GB log, but I do not have that run's original trace to establish the incident's exact cause.

**Why it does not block L4-R03:** `REPLAY.sh` enables `SOCKLOG` and leaves `OPENLOG` unset. The faulty file-tracing branch is therefore inactive in the successful replay. The observed dependency set is sufficient, as demonstrated by the actual offline execution.

**Bounded correction:** make the tracing writer non-reentrant, for example by establishing its logging handle before registering the hook and guarding against recursive logging. Exclude its own log files and bound log growth. If instrumentation fails, report the measurement as incomplete rather than silently presenting it as a complete trace.

**Acceptance check:** one deliberate file open produces one corresponding record and no self-generated open records. Exercise process-launch logging too, since it uses the same writer. Fix this before another large `OPENLOG` measurement; it does not require reopening the requirements baseline or repeating the architecture review.

## Prior-finding disposition

| Earlier finding | Independent disposition now | Boundary / remaining work |
|---|---|---|
| **L4-R03 — replay dependencies missing** | **CLOSED** | The fresh, network-blocked replay passes without another project checkout or object store. |
| L4-R02 — compliant panel and usable solar trace | **PARTIAL** | Section 12 now evaluates a named candidate and its operating curve. The output explicitly retains source compliance as INCONCLUSIVE. |
| L4-R01 — conditional 100 W limit | **PARTIAL; physical bound remains open** | Its calculation reproduces as part of the replay. This adds no new evidence that the assumed specification bounds are guaranteed in operation. |
| L4-R04 — source-specific acceptance wording | **UNVERIFIED here** | This companion does not provide the revised architecture/contract pages needed to establish closure. |
| L3-R01 to L3-R05 — Layer 3 amendment and handover | **UNVERIFIED here** | The new Layer 3 ZIP is absent. Its reported acceptance and test results have not been independently reassessed. |

## What the newly reproduced calculations add

Sections 12 and 13 make useful progress beyond the original power packet:

- The solar calculation now uses a named **SunPower SPR-E-Flex-100 candidate**, with a model of its operating point under the proposed control. It does not promote nominal compatibility into demonstrated compliance; the manufacturer's qualification remains unresolved in the model's source-compliance assessment.
- The three undocumented load contributions are individually identified. They total **8.40 W**, and the output retains the defined **42.8 W** profile.
- Under the candidate's nominal trace and corrected-path assumptions, the replay reports that A2 carries approximately **21.1 W for 48 hours** or **17.5 W for 72 hours**. These are model sensitivities, not approved reductions in service. Even removing all 8.40 W would leave 34.40 W, above either figure.

Consequently, substantiating the uncertain loads alone cannot close the endurance gap in this particular candidate case. That is useful architecture evidence, not a reason to restart Layer 3. Panel/source selection, control design, energy architecture and the objective shortfall remain Layer 4 work.

## Next actions

1. Record **L4-R03 closed by this independent replay**, naming this artifact and its checksum.
2. Fix PR-01 before the next full file-tracing measurement. Keep it separate from the accepted replay result.
3. Continue the authorized Layer 4 engineering work with the conditional assumptions visible.
4. Supply the actual corrected Layer 3 review ZIP for its independent reassessment. A checksum alone cannot establish those closures.

Technical references used to check the review method: [Git tree inspection](https://git-scm.com/docs/git-ls-tree), [Linux unshare](https://man7.org/linux/man-pages/man1/unshare.1.html), and libseccomp's [initialization](https://man7.org/linux/man-pages/man3/seccomp_init.3.html), [rule](https://man7.org/linux/man-pages/man3/seccomp_rule_add.3.html) and [loading](https://man7.org/linux/man-pages/man3/seccomp_load.3.html) documentation. The archive, execution results and fixture measurements are the primary evidence for the conclusions above.
