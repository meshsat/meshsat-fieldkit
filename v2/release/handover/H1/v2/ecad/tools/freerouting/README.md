# The Freerouting build this project routes with

Freerouting 1.9.0 (GPL, https://github.com/freerouting/freerouting) with one patch of ours, `ses_per_pass.py`.

## Why the patch exists

1.9.0 writes its Specctra session **only when the whole job ends**. A time limit that cuts the passes therefore leaves nothing
at all, and a large part of `routeflow.py` exists to hedge that one behaviour: the `NO_SESSION` state, the timeout-doubling
remedy, `route_parallel.sh`'s speculative parallel attempts with nested pass counts, and the rule (P1 of 9 September 2026) that
a multi-hour route must be preceded by a thirty-minute three-pass probe. Both engineering red teams of 10 September named it.

The pass loop in `BatchAutorouter.autoroute_passes` already has a per-pass hook (`save_intermediate_stages`, which writes a GUI
binary board file and is unreachable headless), and `SpecctraSesFileWriter.write` is static and takes the routing board. So the
session can be written there too.

## The patch

`-Dfreerouting.ses_per_pass=<file>` writes the session to `<file>` after every pass, to `<file>.part` first and then an atomic
rename, so a reader never sees half a file. `-Dfreerouting.design_name=<name.dsn>` names the session inside it. Without the
property nothing changes, and the stock jar ignores an unknown `-D`, so `route_one.sh` passes it either way.

## Proof it changes nothing else

Same D board DSN, same options (`-mp 5 -mt 1 -oit 100 -dct 0`), stock jar against ours, 10 September 2026:

| | stock 1.9.0 | ours |
|---|---|---|
| auto-routing | 1 min 23.13 s | 1 min 24.08 s |
| sessions written | 1, at the end | 6: one per pass plus the final one |
| final session | 139,311 bytes | 139,311 bytes, **byte identical** (`cmp` clean) |

So `route_one.sh` takes our jar when it is on the host and the stock one otherwise. A note on `-oit`: it is a THRESHOLD in
percent, not a pass count. `-oit 100` stops the optimizer after one pass, which is what this pipeline uses; `-oit 0` means
"optimise until the improvement is below zero" and never ends. An hour was spent on that.

## Building it

    git clone --depth 1 --branch v1.9.0 https://github.com/freerouting/freerouting.git fr-src
    python3 ses_per_pass.py fr-src            # idempotent; refuses if the hook is not where 1.9.0 has it
    cd fr-src && JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 ./gradlew --no-daemon assemble
    cp build/libs/freerouting-executable.jar ~/bin/freerouting-1.9.0-mesh.jar

Needs a JDK 17 (`apt-get install openjdk-17-jdk-headless`); the box runs a JRE 25 otherwise.

## Measured, 10 September 2026

On a D board DSN, 20 passes: **seven sessions written in the first ninety seconds**, each one importable
(`pcbnew.ImportSpecctraSES` returned True on a mid-run session: 2,372 tracks, 374 vias). The routing itself is untouched: the
patch only adds a write at the end of a pass.

Jar shas (first 16): stock `9084a4888937a7f3`, ours `2c8263a78bc5196f`.
