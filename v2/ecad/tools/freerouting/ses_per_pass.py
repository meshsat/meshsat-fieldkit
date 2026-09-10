#!/usr/bin/env python3
"""Patch Freerouting 1.9.0 to write its Specctra session after EVERY pass (10 September 2026, MESHSAT-862, red team M2).

1.9.0 writes the session only when the whole job ends. Everything in `routeflow.py` that hedges that fact exists because of it:
the NO_SESSION state, the timeout-doubling remedy, `route_parallel.sh`'s speculative attempts with nested pass counts, and the
rule that a multi-hour run must be preceded by a thirty-minute three-pass probe. The pass loop already has a per-pass hook
(`save_intermediate_stages`, which writes a GUI binary board file), and `SpecctraSesFileWriter.write` is static and takes the
routing board, so the session can be written there too.

With `-Dfreerouting.ses_per_pass=<file>` the router writes the session to <file> after every pass, atomically (a `.part` file
then a rename), so a caller that runs out of time still holds the best board reached. Without the property nothing changes.

Usage: ses_per_pass.py <freerouting source tree>     (idempotent; prints what it did)"""
import sys, os

MARK = "freerouting.ses_per_pass"
BLOCK = '''
      // MeshSat (MESHSAT-862, 10 September 2026): the session after every pass, so a run that is cut still leaves its best board.
      String mesh_ses = System.getProperty("freerouting.ses_per_pass");
      if (mesh_ses != null && !mesh_ses.isEmpty()) {
        try {
          java.io.File mesh_tmp = new java.io.File(mesh_ses + ".part");
          try (java.io.OutputStream mesh_os = new java.io.FileOutputStream(mesh_tmp)) {
            app.freerouting.designforms.specctra.SpecctraSesFileWriter.write(
                this.routing_board, mesh_os, System.getProperty("freerouting.design_name", "board.dsn"));
          }
          java.nio.file.Files.move(mesh_tmp.toPath(), new java.io.File(mesh_ses).toPath(),
              java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE);
          FRLogger.info("MeshSat: session written after pass " + curr_pass_no + " to " + mesh_ses);
        } catch (Exception mesh_e) {
          FRLogger.warn("MeshSat: could not write the per-pass session: " + mesh_e);
        }
      }
'''
ANCHOR = """      if (save_intermediate_stages) {
        this.thread.hdlg.get_panel().board_frame.save_intermediate_stage_file();
      }
"""


def main(tree):
    f = os.path.join(tree, "src/main/java/app/freerouting/autoroute/BatchAutorouter.java")
    s = open(f).read()
    if MARK in s: print("ses_per_pass: already patched"); return 0
    if s.count(ANCHOR) != 1: print("ses_per_pass: the per-pass hook is not where 1.9.0 has it; refusing to guess"); return 2
    open(f, "w").write(s.replace(ANCHOR, ANCHOR + BLOCK, 1))
    print("ses_per_pass: patched %s" % f)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
