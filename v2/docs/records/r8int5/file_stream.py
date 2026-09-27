"""r8int5: file one stream's drafts folder (the integration kit's copy, which holds the stream's drafts plus the
integrator's *_r8int5 scripts) under v2/docs/records/<stream>/ through records/r8int4/file_records.py's logic. The
absolute scratch directory of the session is replaced by $SP in the filed copy (the notation the README already uses),
and the files so rewritten are listed in the folder row. Usage (worktree root):
  file_stream.py <kit dir> <folder> "<folder row>" "<cited by>" [exclude-substring ...]"""
import json, os, subprocess, sys
kit, folder, row, cited = sys.argv[1:5]
excl = sys.argv[5:]
SPD = '$SP'
stage = os.path.join(SPD, 'r8int5', 'stage', folder)
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
        files.append([out, rel, '`fnd/%s` `drafts/%s/%s`' % (folder, folder, rel) if not rel.endswith('_r8int5.py') and 'r8int5' not in rel else 'the r8int5 integrator (`%s`)' % rel, cited])
if rewritten:
    row += '; the session scratch path is written $SP in ' + ', '.join('`%s`' % r for r in rewritten)
spec = {'folder': folder, 'folder_row': row, 'files': sorted(files, key=lambda x: x[1])}
sp = os.path.join(stage, '..', folder + '.spec.json'); json.dump(spec, open(sp, 'w'), indent=1)
subprocess.run([sys.executable, os.path.join(SPD, 'r8int5', 'kit', 'common', 'file_records.py'), sp], check=True)
