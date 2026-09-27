import re,sys
def nets(path):
    s=open(path).read()
    out={}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\n\s*\)\s*(?=\(net |\)\s*\)\s*$)', s, re.S):
        pass
    # simpler robust parse
    i=s.find('(nets')
    body=s[i:]
    for blk in re.split(r'\n\s*\(net ', body)[1:]:
        nm=re.search(r'\(name "([^"]*)"\)',blk).group(1)
        nodes=re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?',blk)
        out[nm]=nodes
    return out
def comps(path):
    s=open(path).read()
    i=s.find('(components'); j=s.find('(libparts')
    c={}
    for blk in re.split(r'\n\s*\(comp ', s[i:j])[1:]:
        ref=re.search(r'\(ref "([^"]+)"\)',blk).group(1)
        val=re.search(r'\(value "([^"]*)"\)',blk)
        fields=dict(re.findall(r'\(field \(name "([^"]+)"\) "([^"]*)"\)',blk))
        c[ref]=(val.group(1) if val else '', fields)
    return c
if __name__=='__main__':
    p=sys.argv[1]; N=nets(p); C=comps(p)
    for nm in sys.argv[2:]:
        k=[x for x in N if x==nm or x.lstrip('/')==nm]
        for kk in k:
            print(kk, ' '.join('%s.%s'%(r,pn) for r,pn,_ in N[kk]))
            for r,pn,_ in N[kk]:
                v,f=C.get(r,('?',{}))
                print('    %s.%s  %s  %s'%(r,pn,v,f.get('LCSC','')))
        if not k: print(nm,'NOT FOUND')
