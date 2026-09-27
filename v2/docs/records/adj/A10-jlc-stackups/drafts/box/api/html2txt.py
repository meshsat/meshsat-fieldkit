import sys,re
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style','noscript'): s.skip+=1
        if t in ('br','p','div','tr','li','h1','h2','h3','h4','td','th'): s.out.append('\n')
    def handle_endtag(s,t):
        if t in ('script','style','noscript'): s.skip-=1
    def handle_data(s,d):
        if not s.skip and d.strip(): s.out.append(d.strip()+' ')
p=P(); p.feed(open(sys.argv[1],errors='replace').read())
t=''.join(p.out); t=re.sub(r'[ \t]+\n','\n',t); t=re.sub(r'\n{2,}','\n',t)
open(sys.argv[2],'w').write(t)
