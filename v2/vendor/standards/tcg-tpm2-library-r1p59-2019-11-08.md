# TCG Trusted Platform Module Library, Family "2.0", Level 00 Revision 01.59, 8 November 2019: the clauses ZEROIZE cites

**What this file is.** The clauses `v2/docs/feasibility/ZEROIZE.md` cites for its TPM 2.0 fallback (owner ruling D-03.1,
the Infineon OPTIGA TPM SLB 9673 on board B's U8 site; not fitted), transcribed from the specification as published,
with the source and the hash of each file read. The specification itself is fetched, not redistributed here: this
folder transcribes standards rather than copying them, and TCG's licence grants the rights "to reproduce, distribute,
display, and perform the specification solely for the purpose of developing products based on such documents" (Part 1,
"Licenses and Notices"), which this repository does not need to test. Filed 26 September 2026 (MESHSAT-1357, stream
r8docs; the session's choice under the owner's standing rule of 26 September 2026, over filing the two PDFs or citing
them by URL alone). Quoted in the extent this project needs to say what its fallback's key destruction rests on.

| Part | URL | How it was read | sha256 of the file read |
|---|---|---|---|
| Part 1: Architecture | `https://trustedcomputinggroup.org/wp-content/uploads/TCG_TPM2_r1p59_Part1_Architecture_pub.pdf` | trustedcomputinggroup.org answered this host HTTP 403 on 26 September 2026 (21:15:57Z); the Internet Archive's capture `https://web.archive.org/web/20260904023834id_/<the URL>` returned the same bytes as the ZEROIZE stream's copy (306 pages, 3,790,735 bytes) | `18e393ef8f61d4c5deebb578cc4220b025fdaff2c28a7e3264f16e37796c3d9b` |
| Part 3: Commands | `https://trustedcomputinggroup.org/wp-content/uploads/TCG_TPM2_r1p59_Part3_Commands_pub.pdf` | HTTP 403 on 26 September 2026 (21:15:59Z); the Internet Archive's capture `https://web.archive.org/web/20260428182655id_/<the URL>`, the same bytes as the stream's copy (432 pages, 3,839,615 bytes) | `d2e5e7187574d383b00ff966c33b30a96e3f5165cbfae20a4d094e5794f3b9bb` |

Copyright TCG 2006-2020. Page numbers are the printed ones.

## Part 3, section 24.6, TPM2_Clear, General Description (page 294)

> This command removes all TPM context associated with a specific Owner.
> The clear operation will:
> - flush resident objects (persistent and volatile) in the Storage and Endorsement hierarchies;
> - delete any NV Index with TPMA_NV_PLATFORMCREATE == CLEAR;
> - change the storage primary seed (SPS) to a new value from the TPM's random number generator (RNG),
> - change shProof and ehProof,
>
> [NOTE 1 on how the proof values are derived, not transcribed]
> - SET shEnable and ehEnable;
> - set ownerAuth, endorsementAuth, and lockoutAuth to the Empty Buffer;
> - set ownerPolicy, endorsementPolicy, and lockoutPolicy to the Empty Buffer;
> - set Clock to zero;
> - set resetCount to zero;
> - set restartCount to zero; and
> - set Safe to YES.
> - increment pcrUpdateCounter
>
> [NOTE 2 on policy sessions, not transcribed]
>
> This command requires Platform Authorization or Lockout Authorization. If TPM2_ClearControl() has disabled this
> command, the TPM shall return TPM_RC_DISABLED.

## Part 1, section 13.8, TPM Ownership, "Releasing Ownership" (pages 70 and 71)

> TPM2_Clear() clears the current Owner from the TPM. A persistent TPM control (TPMA_PERMANENT.disableClear) controls
> whether TPM2_Clear() is functional. If disableClear is CLEAR, then TPM2_Clear() may be authorized using either
> Platform Authorization or Lockout Authorization. If the control is SET, then TPM2_Clear() is not functional.
>
> TPM2_Clear() instructs the TPM to:
> - flush any transient or persistent objects associated with the SPS or EPS hierarchies (PPS objects are not
>   affected);
> - release any NV Index locations that do not have their TPMA_NV_PLATFORMCREATE attribute SET;
> - set shEnable and ehEnable to TRUE;
> - set ownerAuth, endorsementAuth, and lockoutAuth to an EmptyAuth;
> - set ownerPolicy, endorsementPolicy, and lockoutPolicy to an Empty Policy;
> - replace the existing SPS with a new value from the RNG; and
> - recompute shProof, and ehProof.

## Part 1, "Storage Primary Seed (SPS)" (page 75)

> The TPM creates the SPS whenever it is powered on and no SPS is present. TPM2_Clear() may be used to change the SPS
> if the TPM owner wants to ensure that no previously generated keys in the Storage hierarchy may be used in the
> future.
>
> Changing the SPS invalidates all objects in the Storage Hierarchy and they cannot be recreated. Changing the SPS
> also invalidates all objects in the Endorsement Hierarchy and only the Primary Objects in the Endorsement Hierarchy
> may be recreated.

## Part 1, section 37.7, NV Other Considerations, "Power Interruption" (page 232)

> A TPM is not required to maintain the integrity of the data in an NV Index if a power loss interrupts the write.
> After the interruption, the TPM should indicate that the Index no longer exists. The interruption of a write to one
> Index is not allowed to affect the integrity of other Indices.

## Part 3, section 28.5, TPM2_EvictControl, General Description (page 335)

> This command allows certain Transient Objects to be made persistent or a persistent object to be evicted.
>
> If objectHandle is a Transient Object, then this call makes a persistent copy of the object and assigns
> persistentHandle to the persistent version of the object. If objectHandle is a persistent object, then the call
> evicts the persistent object. The call does not affect the transient object.

## What this does NOT establish

- **Nothing about the SLB 9673 in particular.** These are the library's normative statements; how Infineon's firmware
  implements them, and how long TPM2_Clear takes on the part, is the part's data sheet and a bench question
  (`v2/vendor/infineon/infineon-slb9673-fw26-datasheet-rev1.4.pdf`, ZEROIZE.md section 6).
- **No physical erasure.** "Change the SPS to a new value" says what the TPM's logic does, not that the old value's
  cells are overwritten beyond recovery (ZEROIZE.md U2, common to all three candidates).
- **Nothing about a power loss during TPM2_Clear itself.** Section 37.7 speaks of an NV Index write; ZEROIZE.md's
  table records TPM2_Clear's own interruption as "not stated".
