import sys, re, json
src = sys.argv[1]
txt = open(src, encoding="utf-8").read()
# entries start with "### desc\n$ cmd...\n--- result\n..."; split on lines that start with "### " followed by a line starting "$ "
parts = re.split(r"(?m)^### (.*)\n\$ ", txt)
ents = []
# parts[0] is preamble; then desc, body pairs
for i in range(1, len(parts), 2):
    desc = parts[i]; body = parts[i+1]
    k = body.find("\n--- result\n")
    cmd = body[:k] if k >= 0 else body
    res = body[k+12:] if k >= 0 else ""
    ents.append(dict(n=len(ents), desc=desc, cmd=cmd, res=res))
json.dump(ents, open(sys.argv[2], "w"))
print(len(ents))
