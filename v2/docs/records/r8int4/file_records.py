"""File session records into v2/docs/records/<folder>/ byte for byte and add their rows to records/README.md.
Usage: file_records.py SPEC.json   (run from the worktree root)
SPEC: {"folder": "hc2", "folder_row": "...", "files": [[src_abs, dest_rel_in_folder, source_label, cited_by], ...]}
A file already filed with the same bytes is left alone; a different file at the path refuses."""
import json, sys, os, hashlib, shutil
spec = json.load(open(sys.argv[1]))
R = 'v2/docs/records/README.md'; t = open(R).read().split('\n')
folder = spec['folder']
# the worktree table
hdr = t.index('| folder | whose records |')
end = hdr + 2
while t[end].startswith('| `'): end += 1
rows = t[hdr + 2:end]
if not any(r.startswith('| `%s/` |' % folder) for r in rows):
    new = '| `%s/` | %s |' % (folder, spec['folder_row'])
    pos = hdr + 2
    while pos < end and t[pos].split('`')[1] < folder + '/': pos += 1
    t.insert(pos, new)
# the filed files table
fh = t.index('| file | sha256 | bytes | source worktree and path | cited by |')
added = 0
for src, dest, label, cited in spec['files']:
    rel = '%s/%s' % (folder, dest); out = os.path.join('v2/docs/records', rel)
    data = open(src, 'rb').read(); sha = hashlib.sha256(data).hexdigest()
    if os.path.exists(out):
        assert hashlib.sha256(open(out, 'rb').read()).hexdigest() == sha, "a different file is filed at " + out
    else:
        os.makedirs(os.path.dirname(out), exist_ok=True); shutil.copyfile(src, out)
    if any(l.startswith('| `%s` |' % rel) for l in t): continue
    row = '| `%s` | `%s` | %d | %s | %s |' % (rel, sha, len(data), label, cited)
    end = fh + 2
    while t[end].startswith('| `'): end += 1
    pos = fh + 2
    while pos < end and t[pos].split('`')[1] < rel: pos += 1
    t.insert(pos, row); added += 1
open(R, 'w').write('\n'.join(t))
print("file_records: %s, %d row(s) added" % (folder, added))
