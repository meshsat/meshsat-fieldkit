"""r8int6: file one stream's drafts folder (the integration kit's copy: the stream's drafts plus the integrator's *_r8int6
scripts) under v2/docs/records/<stream>/ through records/r8int4/file_records.py's logic (records/r8int5/file_stream.py's
method). The absolute scratch directory of the session is replaced by $SP in the filed copy, and the files so rewritten
are named in the folder row. Usage (worktree root):
  file_stream_r8int6.py <kit dir> <folder> "<folder row>" "<cited by>" [exclude-substring ...]"""
import json, os, subprocess, sys
kit, folder, row, cited = sys.argv[1:5]
excl = sys.argv[5:]
SPD = '$SP'
stage = os.path.join(SPD, 'r8int6', 'stage', folder)
files, rewritten = [], []
for dp, dn, fn in os.walk(kit):
    dn[:] = [d for d in dn if d != '__pycache__']
    for f in sorted(fn):
        src = os.path.join(dp, f); rel = os.path.relpath(src, kit)
        if any(x in rel for x in excl): continue
        data = open(src, 'rb').read()
        if SPD.encode() in data:
            data = data.replace(SPD.encode(), b'$SP'); rewritten.append(rel)
        out = os.path.join(stage, rel); os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'wb').write(data)
        mine = folder == 'r8int6' or rel.endswith('_r8int6.py') or rel.endswith('_r8int6.sh') or 'r8int6' in rel
        files.append([out, rel, 'the r8int6 integrator (`%s`)' % rel if mine else '`fnd/%s` `drafts/%s/%s`' % (folder, folder, rel), cited])
if rewritten:
    row += '; the session scratch path is written $SP in ' + ', '.join('`%s`' % r for r in sorted(rewritten))
spec = {'folder': folder, 'folder_row': row, 'files': sorted(files, key=lambda x: x[1])}
sp = os.path.join(stage, '..', folder + '.spec.json'); json.dump(spec, open(sp, 'w'), indent=1)
subprocess.run([sys.executable, 'v2/docs/records/r8int4/file_records.py', sp], check=True)
