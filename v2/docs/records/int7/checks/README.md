# Fresh checks of the streams, taken during the set 6 integration (MESHSAT-1357, 28 September 2026)

Each file is a checker's result as it returned it (four dashes in the tray's result are written as a comma or a hyphen, the repository's no-dash rule; the name of git's co-author trailer in one result is written in words, because the repository's commit check refuses the literal string in any diff), an AI review by an agent session that wrote none of what it checked;
none is a qualified engineering review. The streams themselves are NOT in this integration: each is on its own local
branch and is integrated after the promotion, with its check filed again beside its own records. Prototype design:
nothing built, ordered or measured. The heading of each file carries the branch and commit checked; the times in the
headings were typed by the integrating session and are approximate, the branch and commit are exact.

| File | Stream, branch and commit | Verdict |
|---|---|---|
| `w5tray-check-2.md` | the QMX lid tray r2, `fnd/w5tray` `0ad773ab` | mergeable, no blocking item, 7 minor |
| `d8dec31-check-1.md` | decision 31's protection review of boards A, D and E and the repair of H3-02, `fnd/d8dec31` `f8e61f05` | mergeable for its declaration, tool, registry and hold halves; one blocking item before S-88 can close (a declared entry moved into `internal_ports` shrinks the coverage in silence); 10 minor |
| `p3bind-check-2.md` | the constraint binding check, `fnd/p3bind` `3bfaa317` | mergeable, no blocking item, 8 minor |
| `d6rel-check-1.md` | the repair of REL-001 (H3-01), `fnd/d6rel` `efd6899a` | mergeable, no blocking item, 10 minor; the author answered the minor items on the same branch afterwards (`3d7c98d2`, not re-checked yet) |
| `w5si-check-2-drafts.md` | SI-001's edge rates, the drafts, `fnd/w5si` `7f7721c4` | NOT mergeable: the makers' thirteen IBIS models are tracked on that branch, and two drafts write wrong text on the set 6 line; the follow-up is on `fnd/w5si2`, which carries no model file |
