import subprocess, sys, re
def pages(pdf):
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    return [subprocess.run(['pdftotext', '-layout', '-f', str(i), '-l', str(i), pdf, '-'], capture_output=True, text=True).stdout for i in range(1, n + 1)]
cache = {}
for line in sys.stdin:
    pdf, phrase = line.rstrip('\n').split('|', 1)
    if pdf not in cache:
        cache[pdf] = pages(pdf)
    hits = [i + 1 for i, t in enumerate(cache[pdf]) if phrase in t]
    print('%s | %s | pages %s' % (pdf.split('/')[-1], phrase, hits[:6]))
