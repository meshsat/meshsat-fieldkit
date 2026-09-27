#!/usr/bin/env python3
"""The three-slot failover fabric map of board B, read from two netlists (MESHSAT-1357, stream FAB, 26 Sep 2026).

Usage: fabmap.py <candidate.net> <b21.net> <out_dir>

Read-only. For every fabric signal it starts at a named pin (a CM5 receptacle pin, a switch pin, a hub pin, a
supervisor pin), follows series two-pin passives (tracer.py) and reports the far-end pins, the series parts with
their values and the shunt parts, on BOTH netlists. Each row also carries the far-end pin the datasheets call for
(`expect`); the script checks the netlist against it and prints OK or MISMATCH, so a transcription error in this
table or a wiring error in a netlist shows up as a MISMATCH rather than as a quiet row.

Writes <out_dir>/fabmap.json (every row, both netlists) and <out_dir>/fabmap-tables.md (the tables the page quotes).
No fitted constant. The only convention it relies on is the generator's rail naming (a net named GND or starting
with '+' is a rail), which tracer.py states.
"""
import json
import os
import sys

import tracer as T

CM5B = {1: 'U30B', 2: 'U31B', 3: 'U32B'}
CM5A = {1: 'U30A', 2: 'U31A', 3: 'U32A'}
CARD = {1: 'J_M2C1', 2: 'J_M2C2', 3: 'J_M2C3'}
CARD_KEY = {1: 'E', 2: 'B', 3: 'E'}
# M.2 PCIe pin numbers by key, host-perspective names (the KiCad symbols' names; for key B the Quectel RM520N
# hardware design pin table and for key M Raspberry Pi's CM5 IO board J4 wiring agree, see the page)
M2 = {'M': {'PETp0': '49', 'PETn0': '47', 'PERp0': '43', 'PERn0': '41', 'REFCLKp': '55', 'REFCLKn': '53', 'PERST': '50'},
      'B': {'PETp0': '49', 'PETn0': '47', 'PERp0': '43', 'PERn0': '41', 'REFCLKp': '55', 'REFCLKn': '53', 'PERST': '50'},
      'E': {'PETp0': '35', 'PETn0': '37', 'PERp0': '41', 'PERn0': '43', 'REFCLKp': '47', 'REFCLKn': '49', 'PERST': '52'}}


def rows():
    R = []
    for s in (1, 2, 3):
        cm, sw, nv, cd, k = CM5B[s], 'U%d01' % s, 'J_M2N%d' % s, CARD[s], CARD_KEY[s]
        f = s % 3 + 1          # this slot's USB3-1 is the failover host of bank p where f(p) = s, i.e. p = s - 1
        up = {1: 3, 2: 1, 3: 2}[s]
        R += [
            ('pcie-up', s, 'PCIe TX+ (module transmit)', cm, '122', [(sw, '128')]),
            ('pcie-up', s, 'PCIe TX-', cm, '124', [(sw, '127')]),
            ('pcie-up', s, 'PCIe RX+ (module receive)', cm, '116', [(sw, '124')]),
            ('pcie-up', s, 'PCIe RX-', cm, '118', [(sw, '123')]),
            ('pcie-ctl', s, 'PCIe_CLK_P (module 100 MHz out)', cm, '110', [(sw, '74')]),
            ('pcie-ctl', s, 'PCIe_CLK_N', cm, '112', [(sw, '73')]),
            ('pcie-ctl', s, 'PCIe_CLK_nREQ', cm, '102', []),
            ('pcie-ctl', s, 'PCIe_nRST', cm, '109', [(sw, '10')]),
            ('pcie-ctl', s, 'PCIE_nWAKE', cm, '104', [(nv, '54'), (cd, {'E': '55', 'B': '54'}[k])]),
            ('pcie-ctl', s, 'PCIE_PWR_EN', cm, '106', []),
            ('pcie-dn', s, 'port 1 switch TX+ to NVMe', sw, '100', [(nv, M2['M']['PETp0'])]),
            ('pcie-dn', s, 'port 1 switch TX-', sw, '101', [(nv, M2['M']['PETn0'])]),
            ('pcie-dn', s, 'port 1 switch RX+ from NVMe', sw, '97', [(nv, M2['M']['PERp0'])]),
            ('pcie-dn', s, 'port 1 switch RX-', sw, '98', [(nv, M2['M']['PERn0'])]),
            ('pcie-dn', s, 'port 1 PERST#', sw, '5', [(nv, M2['M']['PERST'])]),
            ('pcie-dn', s, 'port 2 switch TX+ to card (key %s)' % k, sw, '106', [(cd, M2[k]['PETp0'])]),
            ('pcie-dn', s, 'port 2 switch TX-', sw, '107', [(cd, M2[k]['PETn0'])]),
            ('pcie-dn', s, 'port 2 switch RX+ from card', sw, '102', [(cd, M2[k]['PERp0'])]),
            ('pcie-dn', s, 'port 2 switch RX-', sw, '103', [(cd, M2[k]['PERn0'])]),
            ('pcie-dn', s, 'port 2 PERST#', sw, '6', [(cd, M2[k]['PERST'])]),
            ('pcie-dn', s, 'port 3 TX+ (unused)', sw, '118', []),
            ('pcie-dn', s, 'port 3 RX+ (unused)', sw, '122', []),
            ('refclk', s, 'REFCLKO_P0 to own REFCLKP', sw, '85', [(sw, '110')]),
            ('refclk', s, 'REFCLKO_N0 to own REFCLKN', sw, '83', [(sw, '111')]),
            ('refclk', s, 'REFCLKO_P1 to NVMe REFCLKp', sw, '81', [(nv, M2['M']['REFCLKp'])]),
            ('refclk', s, 'REFCLKO_N1 to NVMe REFCLKn', sw, '80', [(nv, M2['M']['REFCLKn'])]),
            ('refclk', s, 'REFCLKO_P2 to card REFCLKp', sw, '78', [(cd, M2[k]['REFCLKp'])]),
            ('refclk', s, 'REFCLKO_N2 to card REFCLKn', sw, '77', [(cd, M2[k]['REFCLKn'])]),
            ('refclk', s, 'REFCLKO_P3 (unused)', sw, '76', []),
            ('refclk', s, 'IREF', sw, '86', []),
            ('refclk', s, 'REXT', sw, '116', []),
            ('refclk', s, 'CLKBUF_PD', sw, '60', []),
            ('refclk', s, 'SLOTCLK', sw, '33', []),
            ('strap', s, 'TEST1', sw, '9', []),
            ('strap', s, 'TEST2', sw, '16', []),
            ('strap', s, 'TCK', sw, '89', []),
            ('strap', s, 'TDI', sw, '93', []),
            ('usb-home', s, 'USB3-0 TX+ (home host of bank %d)' % s, cm, '142', [('U%d09' % s, '19')]),
            ('usb-home', s, 'USB3-0 TX-', cm, '140', [('U%d09' % s, '18')]),
            ('usb-home', s, 'USB3-0 RX+', cm, '130', [('U%d09' % s, '17')]),
            ('usb-home', s, 'USB3-0 RX-', cm, '128', [('U%d09' % s, '16')]),
            ('usb-home', s, 'USB3-0 D+ (USB 2.0 half)', cm, '134', [('U%d10' % s, '1')]),
            ('usb-home', s, 'USB3-0 D-', cm, '136', [('U%d10' % s, '2')]),
            ('usb-fail', s, 'USB3-1 TX+ (failover host of bank %d)' % up, cm, '171', [('U%d09' % up, '15')]),
            ('usb-fail', s, 'USB3-1 TX-', cm, '169', [('U%d09' % up, '14')]),
            ('usb-fail', s, 'USB3-1 RX+', cm, '159', [('U%d09' % up, '13')]),
            ('usb-fail', s, 'USB3-1 RX-', cm, '157', [('U%d09' % up, '12')]),
            ('usb-fail', s, 'USB3-1 D+', cm, '163', [('U%d10' % up, '3')]),
            ('usb-fail', s, 'USB3-1 D-', cm, '165', [('U%d10' % up, '4')]),
            ('usb-ctl', s, 'VBUS_EN', cm, '111', []),
            ('usb-ctl', s, 'USB_OTG_ID', cm, '101', []),
        ]
        hd, hp = {1: ('U3', 'A'), 2: ('U3', 'B'), 3: ('U4', 'B')}[s]
        hp_pins = {'A': {'D2P': '34', 'D2N': '33', 'D1P': '36', 'D1N': '35', 'D0P': '38', 'D0N': '37', 'D3P': '32',
                         'D3N': '31', 'SDA': '41', 'SCL': '42', 'HPD': '19', 'CEC': '18'},
                   'B': {'D2P': '25', 'D2N': '24', 'D1P': '27', 'D1N': '26', 'D0P': '29', 'D0N': '28', 'D3P': '23',
                         'D3N': '22', 'SDA': '39', 'SCL': '40', 'HPD': '21', 'CEC': '20'}}[hp]
        for pin, nm, far in (('170', 'HDMI0_TX2_P', 'D2P'), ('172', 'HDMI0_TX2_N', 'D2N'), ('176', 'HDMI0_TX1_P', 'D1P'),
                             ('178', 'HDMI0_TX1_N', 'D1N'), ('182', 'HDMI0_TX0_P', 'D0P'), ('184', 'HDMI0_TX0_N', 'D0N'),
                             ('188', 'HDMI0_CLK_P', 'D3P'), ('190', 'HDMI0_CLK_N', 'D3N'), ('199', 'HDMI0_SDA', 'SDA'),
                             ('200', 'HDMI0_SCL', 'SCL'), ('153', 'HDMI0_HOTPLUG', 'HPD'), ('151', 'HDMI0_CEC', 'CEC')):
            R.append(('hdmi', s, nm, cm, pin, [(hd, hp_pins[far])]))
        ca = CM5A[s]
        base = {1: 0, 2: 11, 3: 23}[s]
        # KSZ9897R TXRXnP/M_A..D pins (DS00002330E pin table, the generator's KSZ map)
        ksz = {1: {'A': ('1', '2'), 'B': ('4', '5'), 'C': ('6', '7'), 'D': ('8', '9')},
               2: {'A': ('12', '13'), 'B': ('15', '16'), 'C': ('17', '18'), 'D': ('20', '21')},
               3: {'A': ('24', '25'), 'B': ('26', '27'), 'C': ('28', '29'), 'D': ('31', '32')}}[s]
        for pair, (pp, pn), lane in (('0', ('12', '10'), 'A'), ('1', ('4', '6'), 'B'), ('2', ('11', '9'), 'C'), ('3', ('3', '5'), 'D')):
            R.append(('eth', s, 'Ethernet_Pair%s_P' % pair, ca, pp, [('U1', ksz[lane][0])]))
            R.append(('eth', s, 'Ethernet_Pair%s_N' % pair, ca, pn, [('U1', ksz[lane][1])]))
        R.append(('hb', s, 'GPIO16 heartbeat', ca, '29', []))
    for b in (1, 2, 3):
        hub, mx, m2 = 'U%d02' % b, 'U%d09' % b, 'U%d10' % b
        R += [
            ('bank', b, 'hub SS receiver + (upstream)', hub, '58', [(mx, '3')]),
            ('bank', b, 'hub SS receiver -', hub, '59', [(mx, '4')]),
            ('bank', b, 'hub SS transmitter + (upstream)', hub, '55', [(mx, '7')]),
            ('bank', b, 'hub SS transmitter -', hub, '56', [(mx, '8')]),
            ('bank', b, 'hub D+ (upstream)', hub, '53', [(m2, '8')]),
            ('bank', b, 'hub D- (upstream)', hub, '54', [(m2, '7')]),
            ('bank', b, 'hub USB_VBUS (upstream detect)', hub, '48', []),
            ('bank', b, 'hub GRSTz', hub, '50', []),
            ('bank', b, 'TMUXHS4212 SEL', mx, '9', [(m2, '9')]),
            ('bank', b, 'TMUXHS4212 OEn', mx, '2', [(m2, '6')]),
        ]
    R += [
        ('bank', 1, 'hub DN1 SS TX+ to LimeSDR', 'U102', '3', [('J_LIME', '9')]),
        ('bank', 1, 'hub DN1 SS TX-', 'U102', '4', [('J_LIME', '8')]),
        ('bank', 1, 'hub DN1 SS RX+ from LimeSDR', 'U102', '6', [('J_LIME', '6')]),
        ('bank', 1, 'hub DN1 SS RX-', 'U102', '7', [('J_LIME', '5')]),
    ]
    for ref, nm, far in (('U3', 'SEL2 (HDMI_SEL1)', ('J_PANEL', '12')), ('U4', 'SEL2 (HDMI_SEL2)', ('J_PANEL', '13')),
                         ('U3', 'EN', None), ('U4', 'D0P common to J_HDMI', ('J_HDMI', '7')),
                         ('U4', 'SDA common', ('J_HDMI', '16')), ('U4', 'SCL common', ('J_HDMI', '15')),
                         ('U4', 'HPD common', ('J_HDMI', '19'))):
        pin = {'SEL2 (HDMI_SEL1)': '17', 'SEL2 (HDMI_SEL2)': '17', 'EN': '2', 'D0P common to J_HDMI': '5',
               'SDA common': '4', 'SCL common': '3', 'HPD common': '14'}[nm]
        R.append(('hdmi-ctl', 0, nm, ref, pin, [far] if far else []))
    for tag, u in (('A', 'U41'), ('B', 'U51'), ('C', 'U61')):
        for pin, nm in (('22', 'PA0 SEL1'), ('23', 'PA1 SEL2'), ('24', 'PA2 SEL3'), ('25', 'PA3 HUBRST1'),
                        ('28', 'PA4 HUBRST2'), ('29', 'PA5 HUBRST3'), ('37', 'PE7 WSEC'), ('38', 'PE8 read BSEL1'),
                        ('39', 'PE9 read BSEL2'), ('40', 'PE10 read BSEL3'), ('41', 'PE11 read WIFI_SEC'),
                        ('30', 'PA6 HB1'), ('31', 'PA7 HB2'), ('32', 'PC4 HB3'), ('81', 'PD0 FDCAN1_RX'),
                        ('82', 'PD1 FDCAN1_TX'), ('51', 'PB12 FDCAN2_RX'), ('52', 'PB13 FDCAN2_TX'),
                        ('92', 'PB6 I2C1_SCL'), ('93', 'PB7 I2C1_SDA')):
            R.append(('ctrl', tag, nm, u, pin, []))
    for u in ('U43', 'U44', 'U53', 'U54', 'U63', 'U64'):
        for pin in ('5', '6', '7', '8'):
            R.append(('can', u, 'TCAN334 pin %s' % pin, u, pin, []))
    return R


def describe(b, ref, pin):
    net = b.pinnet.get((ref, pin))
    fn = b.pf.get((ref, pin), '')
    if net is None:
        return {'net': None, 'fn': fn, 'paths': [], 'shunts': [], 'far': []}
    if T.is_rail(net):
        return {'net': net, 'fn': fn, 'paths': ['(rail %s)' % net], 'shunts': [], 'far': []}
    paths, shunts = b.trace(ref, pin)
    far, ptxt = [], []
    for p in paths:
        if isinstance(p, tuple):
            chain, (r, pp, f) = p
            far.append((r, pp, f))
            via = [v for (n, v) in chain if v]
            ptxt.append('%s %s.%s %s' % ((' + '.join(via) + ' ->') if via else '->', r, pp, f))
    sh = ['%s %s to %s' % (r, v, o) for (n, r, v, o) in shunts if not n.startswith('+') and n != 'GND']
    return {'net': net, 'fn': fn, 'paths': ptxt, 'shunts': sh, 'far': far}


def main():
    cand, b21, out = sys.argv[1], sys.argv[2], sys.argv[3]
    B = {'cand': T.Board(cand), 'b21': T.Board(b21)}
    res = []
    for (kind, slot, label, ref, pin, expect) in rows():
        row = {'kind': kind, 'slot': slot, 'label': label, 'ref': ref, 'pin': pin, 'expect': expect}
        for tag, b in B.items():
            d = describe(b, ref, pin)
            fars = set((r, p) for (r, p, f) in d['far'])
            d['check'] = 'n/a' if not expect else ('OK' if all(tuple(e) in fars for e in expect) else 'MISMATCH')
            row[tag] = d
        res.append(row)
    os.makedirs(out, exist_ok=True)
    meta = {'candidate': cand, 'candidate_sha256': T.netparse.sha256(cand), 'b21': b21, 'b21_sha256': T.netparse.sha256(b21),
            'script_sha256': T.netparse.sha256(__file__), 'tracer_sha256': T.netparse.sha256(T.__file__)}
    json.dump({'meta': meta, 'rows': res}, open(os.path.join(out, 'fabmap.json'), 'w'), indent=1)
    n_c = sum(1 for r in res if r['cand']['check'] == 'MISMATCH')
    n_b = sum(1 for r in res if r['b21']['check'] == 'MISMATCH')
    lines = ['candidate %s mismatches %d; B21 %s mismatches %d' % (meta['candidate_sha256'][:16], n_c, meta['b21_sha256'][:16], n_b)]
    for r in res:
        c, o = r['cand'], r['b21']
        same = 'same' if (c['net'] == o['net'] and c['paths'] == o['paths'] and c['shunts'] == o['shunts']) else 'DIFFERS'
        lines.append('| %s | %s | %s | %s.%s %s | %s | %s | %s | %s | B21 %s: %s %s |' % (
            r['kind'], r['slot'], r['label'], r['ref'], r['pin'], c['fn'], c['net'], '; '.join(c['paths']) or '-',
            '; '.join(c['shunts']) or '-', c['check'], same, o['check'],
            ('' if same == 'same' else (o['net'] or '-') + ' ' + ('; '.join(o['paths']) or '-'))))
    open(os.path.join(out, 'fabmap-tables.md'), 'w').write('\n'.join(lines) + '\n')
    print(lines[0])


if __name__ == '__main__':
    main()
