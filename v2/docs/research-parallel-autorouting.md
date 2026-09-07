# Research: parallel autorouting across machines (7 Sep 2026)

Question from the owner (7 Sep 2026, 22:35 CEST): the B16 route runs for hours to days on one box; how can such runs be parallelised over several servers instead of one?

Short answer: **more servers do not shorten a Freerouting job, because a job is one sequential thread whatever the thread option says; the box we rent has 384 threads and runs every job we give it side by side. The parallelism has to come from splitting the board into independent routing jobs, and that split runs as well on one big box as on ten small ones.** The split is possible with the tool we have (Freerouting 1.9.0's `-inc` option ignores whole net classes), the merge is a KiCad scripting task, and the plan below is what we build. The alternatives (cloud routers, other engines, faster single-thread hardware, design levers) are listed with their trade-offs.

## 1. The problem as measured on B16

| Fact | Value |
|---|---|
| Board | 330 x 200 mm, six layers (In1 ground, In4 the four 5 V pours), four routing layers |
| Connections after the plane fanout | 1452 (682 nets, 3868 pad-to-net references) |
| Freerouting 1.9.0, single thread, passes 1 to 3 | 1 h 42 min, 252 open, 2 hard |
| passes 1 to 5 | 2 h 05 min, 159 open, 0 hard |
| passes 1 to 12 | not finished after 2 h 45 min |
| passes 1 to 100 | not finished after 4 h (no session written) |
| CPU use per router process | about 1.2 cores, whatever `-mt` says |
| Session output | only after the last pass; a time limit that cuts the passes leaves nothing |

The passes are sequential by construction: pass N works on what pass N-1 left, with a growing ripup budget. A long run is a single thread of dependent steps.

## 2. What the tools actually do (sources read 7 Sep 2026)

**Freerouting 1.9.0 (the version that routes our boards).** Its `BatchAutorouterThread` selects `BatchOptRouteMT` for the *optimizer* when the thread count is above one and runs `batch_autorouter.autoroute_passes()` single-threaded; the same file warns that the multi-threaded optimizer produces clearance violations and recommends `-mt 1` (that is the "knot" we removed with `unknot.py`). The README documents `-mt` as "thread pool size for route optimization", `-im` as checkpoints "to resume the interrupted optimization" (again the optimizer, not the router), and `-inc [net class names]` as "auto-router ignores the listed net classes". So: the router passes cannot be parallelised inside 1.9.0, and there is no checkpoint of the router passes; the useful option for us is `-inc`.

**Freerouting 2.4.1.** The settings reference documents `router.max_threads` (default 11) as pass parallelism, and `AutoroutePassRunner.runMultiThread` shows what that means: each thread gets a deep copy of the board and a shuffled subset of the items, the threads run independently, and the best result of the pass is kept. That is speculative parallelism (try several orderings, keep the best), not a division of the work; our diagnostic of the morning confirms it does not speed a pass up. What 2.x does add: a REST API (`POST /jobs/enqueue`, `POST /jobs/{id}/input` with the DSN, `PUT /jobs/{id}/start`, `GET /jobs/{id}/output` returning the in-progress session with HTTP 202 while the job runs), a `--router.job_timeout`, a Docker image for self-hosting, a job persistence flag; no horizontal scaling, no worker pool: one server processes its own jobs. Several servers are several independent processors; a dispatcher on our side would be a hundred lines of shell. The in-progress output is the one feature that addresses "nothing until the last pass"; 2.4.1's own routing was slower than 1.9.0 on B16 in the morning diagnostic (fanout pre-pass on by default, eight threads), so it would need a fair single-thread retest before it replaces 1.9.0.

**tscircuit capacity autorouter** (`@tscircuit/capacity-autorouter`, MIT, TypeScript). A capacity-mesh router that subdivides the board into cells and solves connections through them; the public API is a stepping solver in one process (`solver.step()` until solved); no distributed or multi-worker solving is documented; input and output are SimpleRouteJson, with `dsn-converter` (MIT) translating Specctra DSN to circuit JSON and back. The benchmark repository that preceded it is archived. It is a candidate for an experiment on a small board, not for a 1452-connection six-layer board this week.

**DeepPCB (InstaDeep).** A learned routing engine in the cloud, self-serve and pay as you go, inputs Altium, KiCad (plugin), EasyEDA, Zuken, and Specctra DSN for OrCAD, Allegro and Eagle; public examples are four-layer boards of 39 to 210 nets routed in 2 to 18 minutes; no size limit is stated. Our board is public (CERN-OHL-S), so uploading it is allowed; the unknowns are the price per board and whether the engine takes six layers with the plane rule areas and 0.4 mm receptacle escapes.

**Quilter.** Physics-driven placement and routing in the cloud, KiCad native input, generates hundreds of layout candidates; the stated sweet spot is 100 to 1,000 components and 2,000 to 5,000 pins at under 20 percent pin density, through-hole vias only, no length matching yet; a free tier and a startup programme exist; data is uploaded (a self-hosted option exists for regulated users). B16 (about 3,900 pad references, 682 nets) is inside the stated envelope, but Quilter re-places the board, which our generators and gates do not allow; a routing-only use is not documented.

**Commercial desktop routers** (Altium ActiveRoute, Cadence Allegro, Siemens Xpedition, Zuken CR-8000, Eremex TopoR). All route on one workstation with several cores; none distributes a job over machines; TopoR is excluded by ruling; the rest are licence purchases outside our toolchain.

**Academic parallel routers** (for example CUGR, "routing all nets with rip-up and reroute and multithreading", eight threads on a workstation). The pattern they use is the one that transfers: partition the nets into batches that do not interact, route the batches concurrently, resolve the few conflicts afterwards. That is what section 3 builds.

**Faster single-thread hardware.** The EPYC 9654 of our box boosts to 3.7 GHz; the vast.ai list at 22:36 CEST held Ryzen 9 5900X boxes at 5.0 GHz for 0.06 to 0.17 USD per hour (24 threads, 32 to 64 GB). Same architecture generation within one step, so about 1.2 to 1.3 times per job. Cheap, and a place to put partition jobs when the big box is busy, but not a change of category.

## 3. The scheme that fits our pipeline: net partition with fixed obstacles

The B16 netlist falls into four groups that barely interact geometrically: the local nets of slot 1, slot 2 and slot 3 (each a column of the board with its receptacle pair, PCIe switch, hub, NVMe and card slot, converters and decoupling) and the global nets (Ethernet switch, HDMI switch, USB and I2C fabrics, the rails, the panel and dock connectors, the radios). Freerouting 1.9.0 skips whole net classes with `-inc`, and everything it skips stays on the board as an obstacle (pads, locked escapes, locked joins). So:

1. **Partition the DSN** (`tools/dsn_partition.py`): rewrite the `network` section so that every net sits in a class named `<original class>_<group>` (S1, S2, S3, GLOBAL), each new class carrying the rule block of its original class (width and clearance stay). Group by the net name suffix (`_S1`, `_S1A`, `_S1B`, `_CM1`, ...) and, for unsuffixed nets, by the column of the pads it touches; a net touching more than one column is GLOBAL.
2. **Route GLOBAL first** with `-inc` listing every S class: a few hundred connections, one job, about half an hour; import its session and **lock** its tracks (a locked track exports as `(type fix)` and the next jobs keep it).
3. **Route S1, S2 and S3 concurrently**, each job ignoring the other S classes and GLOBAL; the GLOBAL tracks and the other columns' pads and escapes are obstacles. Each job carries about a third of the connections, so each pass costs a third and the ripup interactions inside a job are the ones of one column. On the measured rate, twenty passes of a third of the board are about 1.5 to 2 hours instead of the 8 to 12 of the whole board.
4. **Merge** (`tools/ses_merge.py`): import each S session into its own copy of the board, then copy the tracks and vias of the S1 nets from copy 1, S2 from copy 2, S3 from copy 3 into the master board that already holds the locked GLOBAL tracks. A `ses` import in KiCad replaces the unlocked tracks of the board, which is why the merge works from copies.
5. **Reconcile**: run DRC on the merged board; a short or crossing between two partitions is a boundary conflict; rip the unlocked tracks of the smaller partition at each conflict (the `unknot.py` mechanism) and close the openings with the stub router and, if needed, one short continuation route of a few passes with all classes enabled (the continuation now keeps the planes and power layers).
6. **Finish** as today (`finish_b16.sh`: clean-up, stub router, refill, gates, deliverable).

Scaling to N servers: steps 3 and 5 are independent jobs; `route_parallel.sh` already runs jobs as separate processes from separate directories, and dispatching a directory to another box is an rsync out, a route, an rsync back. Our box has 384 threads and runs the three slot jobs plus the from-scratch hedges at once, so the multi-server form is a cost option (the 5 GHz boxes at a tenth of the price), not a speed option.

Risks: conflicts at the column boundaries (mitigated by routing GLOBAL first and by the columns' geometry); the DSN class rewrite must preserve the rule blocks exactly or the router routes at the wrong width (the class gate of `check_pcb_b.py` reads the widths back); the merge must copy by net, never by position; and the reconcile step must be gated by the same DRC as the finish.

## 4. What does not help, for the record

- More threads on 1.9.0: optimizer only, and broken there (the knot).
- More boxes for one job: one thread per job.
- Longer time limits without more passes: the passes are the work.
- Continuation from an imported session in chunks: the router restarts at pass 1 with no ripup budget and spends its first passes on exactly the items that needed ripup; five passes from the 252-open board did not finish in 90 minutes, while passes 4 and 5 from scratch took 23 minutes.

## 5. Design levers that shrink the problem (owner decisions)

- The per-slot 3.3 V, 1.0 V, 1.1 V and 1.2 V rails (about 500 pads) are wired because their pads are interleaved with the signal parts across each column; an In4 island per rail needs a placement pass that groups each rail's consumers (owed as the B17 power-copper pass beside A23).
- An eight-layer stack (two more routing layers) would cut the pass count and the congestion; it is a stack ruling and a cost line.
- Nothing else in the generators reduces the connection count without a device change.

## 6. Recommendation

Build the partition pipeline (section 3) now and run it on B16 beside the from-scratch runs that are already going; keep 1.9.0 as the engine; retest 2.4.1 single-threaded with the fanout off on one partition to see whether its in-progress output is worth the switch; put the design levers of section 5 to the owner as one decision each when the partition result is in. The cloud routers are a paid experiment for a later day, on a board that is public anyway.

Sources: Freerouting repository (README at v1.9.0 and master, `docs/command_line_arguments.md`, `docs/settings.md`, `docs/self-hosting.md`, `docs/architecture.md`, `docs/benchmarks.md`, `docs/API/API_v1.md`, the release notes for v2.0.0 to v2.4.1, `interactive/BatchAutorouterThread.java` at v1.9.0, `autoroute/pipeline/AutoroutePassRunner.java` and `BatchAutorouterThread.java` at master); tscircuit `tscircuit-autorouter`, `dsn-converter` and the archived `autorouting` repository; deeppcb.ai; quilter.ai; cuhk-eda/cu-gr; the vast.ai offer list of 7 Sep 2026 22:36 CEST; our own B16 measurements of the day (appendix 32.63).
