import re
TOK = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))')
def parse(text):
    stack = [[]]
    pos = 0
    n = len(text)
    while pos < n:
        m = TOK.match(text, pos)
        if not m:
            if text[pos:].strip() == "": break
            raise ValueError("bad at %d" % pos)
        pos = m.end()
        if m.group(1): stack.append([])
        elif m.group(2):
            t = stack.pop(); stack[-1].append(t)
        elif m.group(3) is not None: stack[-1].append(m.group(3).replace('\\"', '"'))
        elif m.group(4) is not None: stack[-1].append(m.group(4))
    return stack[0][0]
def find(node, tag):
    return [c for c in node if isinstance(c, list) and c and c[0] == tag]
def first(node, tag):
    r = find(node, tag); return r[0] if r else None
def val(node, tag):
    r = first(node, tag); return r[1] if r and len(r) > 1 else None
