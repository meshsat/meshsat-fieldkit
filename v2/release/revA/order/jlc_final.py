#!/usr/bin/env python3
"""Build the final JLCPCB upload set per board: BOM with the chosen LCSC codes, CPL with rotation offsets.
Inputs: <board>/pcb-*-bom.csv, <board>/pcb-*-cpl.csv, jlc-rotations.csv, the LCSC map below (from ORDER-LOG.md).
Outputs: <board>/final/*-bom-final.csv, <board>/final/*-cpl-jlc.csv. Originals untouched."""
import csv, re, sys, os, glob

LCSC = {
 'PCB-E1-DOCK-E1': {'C1':'C13585','C2':'C14663','C3':'C12891','D1':'C438109','D2':'C43491','D3':'C2760888',
   'J_AUX':'C265283','J_DCIN':'C265357','LED1':'C12624','Q1':'C347462','R1':'C25803','R2':'C4190','R3':'C23138','R4':'C25803','U2':'C63268'},
 'PCB-D-APRS-D5': {'C1':'C1653','C2':'C1653','C11':'C53987','C22':'C53987','C21':'C15849','D1':'C12624','D2':'C2286',
   'FB1':'C1002','FB2':'C1002','L1':'','R2':'C23162','R12':'C23345','R13':'C23345','R30':'C2933194','R31':'C25803',
   'R32':'C304711','R33':'C2933128','R34':'C4184','R35':'C25803','R38':'C25803','R39':'C25803','R36':'C25804','R40':'C25804',
   'R37':'C21190','U5':'C94046','U6':'C7519','Y1':'C115962','J_HARN1':'C18202144','J_PWR1':'C265357','J_SWD1':'C22438104',
   'Q1':'C8664','Q2':'C8664','Q3':'C8545','Q4':'C8666','U1':'C165129','U3':'C51118','U4':'C51118',
   **{f'C{i}':'C19666' for i in (4,5,6,7,10,13,14,31)}, **{f'C{i}':'C14663' for i in (8,9,12,15,16,17,18,25,32,20,30)},
   **{f'C{i}':'C2918511' for i in (23,24,26,27,28,29)}, **{f'R{i}':'C22843' for i in (1,4,10,11,18,19)},
   **{f'R{i}':'C22775' for i in (3,8,9,15,17,41)}, **{f'R{i}':'C23186' for i in (5,14,16)}},
 'PCB-C-DISPLAY-C4': {'C1':'C15850','C2':'C15850','D17':'C915628','Q1':'C15127','Q2':'C8545','Q3':'C8545','Q4':'C8545',
   'R9':'C4190','R10':'C23182','R29':'C21190','R31':'C23179','R33':'C23179','U1':'C2864778','U2':'C2864778',
   'BZ1':'C96093','D2':'C282137','D12':'C282137','D10':'','D11':'','J_EPD':'C32713274','J_PANEL':'C18202145',
   'J_PIJ2':'C265283','J_X1202SW':'C265283',
   **{f'C{i}':'C14663' for i in (3,4,11,12,13)}, **{f'C{i}':'C57112' for i in (5,6,7,8,9,10)},
   **{f'FB{i}':'C1002' for i in (1,2,3,4)}, **{f'R{i}':'C25804' for i in (1,2,3,4,5,7,8)},
   **{f'R{i}':'C25803' for i in (6,12,30,39)}, **{f'R{i}':'C22775' for i in (11,34,35,36,37,38)},
   **{f'R{i}':'C23025' for i in (13,14,15,23,28,32)}, **{f'R{i}':'C22828' for i in (16,17,18,19,20,21,22,24,25,26,27)},
   **{f'U{i}':'C7519' for i in (5,6,7,8)}, **{f'D{i}':'C99771' for i in (1,3,4)},
   **{f'D{i}':'C2927624' for i in (5,6,7,8,9,13,14,15,16)}},
 'PCB-B-COMPUTE-B10': {'C1':'C312983','C2':'C312983','C3':'C1653','C4':'C1653','D1':'C19077558','J_USB_UP1':'C165948',
   'J_USB_UP2':'C165948','LED1':'C12624','LED2':'C2287','R1':'C21190','R8':'C21190','R2':'C13167','R7':'C23162',
   'R14':'C2934287','R16':'C2934287','R26':'C22775','U4':'C353882','U7':'C353882','U20':'C2864778','F2':'C20812',
   'F4':'C20812','F5':'C20812','F3':'C20998','F6':'C12559','J_5V_IN1':'C265283','J_5V_IN2':'C265283','J_TD2':'C265283',
   'J_AB1':'C19193808','J_DCF77':'C144395','J_GPIO1':'C19193815','J_PANEL':'C18202145','J_RB9603':'C505021',
   'J_RB9704':'C18202144','J_RTL1':'C3197637','J_ZB1':'C3197637','J_TBEAM1':'C131334','J_TCALL1':'C131334',
   'J_XIAO1':'C131334','Q1':'C8545','U1':'C9359','Y1':'C5160137',
   **{f'C{i}':'C14663' for i in (5,7,9,12,14,16,18,21,24,26,33,34)}, **{f'C{i}':'C15849' for i in (6,8,11,29,30,31,32)},
   **{f'C{i}':'C15850' for i in (10,13,15,17,19,22,25)}, **{f'C{i}':'C1588' for i in (20,23,27,28)},
   **{f'R{i}':'C25804' for i in (3,4,5,6,13,15,17,20,25,28,29)}, **{f'R{i}':'C23186' for i in (9,10,11,12)},
   **{f'R{i}':'C912751' for i in (18,21,22,24)}, **{f'R{i}':'C25803' for i in (27,30,31,32,33,34,35)},
   **{f'U{i}':'C7519' for i in (2,3,6,9,12,17)}, **{f'U{i}':'C87469' for i in (5,8,11,14,16,19)},
   **{f'U{i}':'C527679' for i in (10,13,15,18)}},
 'PCB-A-POWER-A16': {'C13':'C312983','C16':'C1653','C17':'C1653','D2':'C19077558','LED2':'C2287','R18':'C21190','R25':'C21190',
   'R19':'C13167','R24':'C23162','U5':'C6186','U19':'C2864778','U6':'C9359','Y1':'C5160137','J_AB1':'C19193808',
   'J_GPS1':'C3197637','J_WIFI1':'C3197637','J_LEDS1':'C144400','J_MEZZ1':'C18202144','J_MEZZ_PWR1':'C265357',
   'J_PACK':'C98733','J_X1202BAT':'C98733','J_X1202DC':'C265283','F1':'','F2':'',
   **{f'C{i}':'C15850' for i in (7,14,15,25,27,29,31)}, **{f'C{i}':'C14663' for i in (18,20,22,24,26,28,30,32,34,35,36,37)},
   **{f'C{i}':'C15849' for i in (19,21,23)}, **{f'R{i}':'C25804' for i in (12,20,21,22,23,26,28,30,32,34)},
   **{f'R{i}':'C2934287' for i in (27,29,31,33)}, **{f'R{i}':'C23138' for i in (35,36,37,38)},
   **{f'R{i}':'C25803' for i in (39,40,41,42,43)}, **{f'U{i}':'C353882' for i in (7,10,13,16)},
   **{f'U{i}':'C87469' for i in (8,11,14,17)}, **{f'U{i}':'C7519' for i in (9,12,15,18)}},
}

def load_rot():
    rules=[]
    for line in open('jlc-rotations.csv'):
        line=line.strip()
        if not line or line.startswith('#'): continue
        pat,off=line.rsplit(',',1); rules.append((re.compile(pat),float(off)))
    return rules

def main():
    rules=load_rot()
    for board,codes in LCSC.items():
        bom=glob.glob(f'{board}/pcb-*-bom.csv')[0]; cpl=glob.glob(f'{board}/pcb-*-cpl.csv')[0]
        os.makedirs(f'{board}/final',exist_ok=True)
        rows=list(csv.reader(open(bom)))
        hdr,rows=rows[0],rows[1:]
        fp_of={}; out=[hdr]; missing=[]
        for r in rows:
            refs=[x.strip() for x in r[1].split(',') if x.strip()]
            got=set()
            for ref in refs:
                fp_of[ref]=r[2]
                if ref in codes: got.add(codes[ref])
                else: missing.append(ref)
            code = got.pop() if len(got)==1 else ('' if not got else '|'.join(sorted(got)))
            out.append([r[0],r[1],r[2],code])
        name=os.path.basename(bom).replace('-bom.csv','')
        with open(f'{board}/final/{name}-bom-final.csv','w',newline='') as f: csv.writer(f).writerows(out)
        crow=list(csv.reader(open(cpl))); chdr,crow=crow[0],crow[1:]
        cout=[chdr]; changed=[]
        for r in crow:
            ref=r[0]; fp=fp_of.get(ref,''); rot=float(r[4]); off=0
            for pat,o in rules:
                if pat.search(fp): off=o; break
            if off:
                rot=(rot+off)%360; changed.append(f'{ref}({fp.split("_")[0]}:{r[4].rstrip("0").rstrip(".")}->{rot:g})')
            cout.append([r[0],r[1],r[2],r[3],f'{rot:.6f}'])
        with open(f'{board}/final/{name}-cpl-jlc.csv','w',newline='') as f: csv.writer(f).writerows(cout)
        blank=[o[1] for o in out[1:] if o[3]=='']; multi=[o[1] for o in out[1:] if '|' in o[3]]
        print(f'{board}: {len(out)-1} BOM lines, blank={blank}, conflict={multi}, unmapped refs={missing}')
        print(f'   CPL {len(cout)-1} rows, rotated {len(changed)}: {", ".join(changed)}')
main()
