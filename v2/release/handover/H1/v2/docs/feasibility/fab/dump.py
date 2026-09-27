import sys, tracer as T
b = T.Board(sys.argv[1])
for ref in sys.argv[2:]:
    for pin in sorted(b.pins_of[ref], key=lambda x: int(x) if x.isdigit() else 9999):
        net = b.pinnet[(ref,pin)]
        if net=='GND': continue
        if T.is_rail(net):
            print(ref, pin, b.pf[(ref,pin)], '|', net, '|| (rail)'); continue
        paths, sh = b.fmt(ref,pin)
        sh=[x for x in sh if not x.startswith('+')]
        print(ref, pin, b.pf[(ref,pin)], '|', net, '||', ' ; '.join(paths[:6]), '||', ' ; '.join(sh))
