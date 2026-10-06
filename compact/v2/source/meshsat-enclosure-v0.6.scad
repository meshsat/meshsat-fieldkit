// =====================================================================
// MeshSat stacked enclosure v0.6 - LilyGO T-Beam Supreme over RockBLOCK 9704-SMA
// Units: mm.  Generator: OpenSCAD 2021.01.
//
// v0.6 = response to the 5 Oct 2026 engineering audit of v0.5 (F01-F15).
// Board geometry is registered to the manufacturers' STEP files
// (reference-cad/meshes/*.stl are tessellations of those STEPs) and every
// printed part is clash-checked against them by validation/clash_check.py.
//
// Layout: 9704 (component side down) on edge rails in the lower bay, printed
// separator, Supreme + 18650 in the upper bay, OLED window in the lid.
//
// PART = "assembly"      : printed parts + real board meshes (preview only)
//        "exploded"      : exploded view with ruler + 2 EUR coin
//        "body" "lid" "separator" "membrane" "plungers" "retainer"
//        "molle" "belt"  : printable parts, exported in PRINT orientation
//        "coupon_rimlid" : body top band (grounded) + full lid: gasket/insert/screw coupon
//        "coupon_board"  : upper-bay band with ledges/buttons/window datum (grounded):
//                          drop the separator + real Supreme in, close with the lid
//        "coupon_rails"  : 9704 rail pair + floor strip: real-PCB slot fit coupon
//        "a_*"           : same parts in ASSEMBLED position (for clash checks)
// =====================================================================

PART = "assembly";
$fn = 40;
REF = "../reference-cad/meshes/";       // STEP tessellations (assembly / exploded views)

// ---------------- shell ----------------
wall    = 5.0;
floor_t = 3.0;
lid_t   = 5.5;
cr_out  = 9.0;      // vertical-edge radius
r_bot   = 3.0;      // bottom-edge 45 deg chamfer (bed-facing: chamfer, not fillet - F09)
r_top   = 2.5;      // lid top-edge 45 deg chamfer (lid prints face down; F01: <= lid_t/2)
case_rgb = "#FF6A13";

// ---------------- T-Beam Supreme (LilyGO 3d_file-1105.stp) ----------------
// STEP frame: PCB underside z=0, PCB 1.0 thick, footprint x +/-16.44, y -50..50,
// SMA end at y=-50. Placed rotated 180 deg about Z (SMA end toward the antenna wall).
sup_w   = 32.88;    sup_l = 100.0;    pcb_t = 1.0;
top_max = 10.81;    // tallest top-side part above PCB underside (STEP)
usb_out = 0.95;     // USB-end protrusion beyond PCB edge (STEP: USB-C to y=50.95)
// Battery: holder is not in the STEP. LilyGO's own Supreme shell (same frame) puts the
// holder bottom 18.7 below the PCB underside and its inner roof 0.9 above top_max.
hold_drop = 18.7;   // PCB underside -> holder bottom (LilyGO shell)          [VERIFY]
hold_r    = 10.7;   // holder radius: loose saddles (+2.5 clearance), not a datum [VERIFY]
foam_c    = 1.0;    // compressed thickness of 1.5 mm closed-cell foam under the holder
pad_c     = 1.0;    // compressed thickness of 1.5 mm foam/TPU pads on lid bosses
// PCB retention only where BOTH faces are bare in the STEP: 1.3 mm edge strip,
// board-y 5.7..39.7 from the SMA end, both long edges (validation/heightmap).
edge_strip = 1.3;
seat_by    = [8, 24, 37];      // lower seats (board-y from SMA end)
boss_by    = [8, 37];          // lid hold-downs, directly over seats
sma_clear  = 22.0;  usb_clear = 14.0;
// OLED window: centre matches LilyGO's own shell window within 0.2 mm
oled_cy = 22.75;  win_x = 17.0;  win_y = 31.5;
pane_x = 24.0; pane_y = 38.0; pane_t = 2.0;   // 2.0 mm polycarbonate, exact
pane_clr = 0.3;     // XY clearance per side
bond_t   = 0.2;     // adhesive bond line under the pane
// Side buttons (STEP actuator faces): board-y, depth below PCB underside, protrusion
btn_by    = [50.72, 59.02, 74.65];   // RST, POWER, BOOT
btn_drop  = 1.75;
btn_prot  = 0.38;   // actuator face beyond PCB edge
sup_sma_dx = 9.75;  sup_usb_dx = 7.45;   // offsets from board centreline (case frame)

// ---------------- RockBLOCK 9704-SMA (Ground Control STEP 2A) ----------------
// PCB 47.8 x 52.0 x 1.5, component side DOWN: module +5.9 on top; supercaps,
// SMA, header pins, USB-C below (to -10.3 / SMA -11.1). Edges bare within 1.45 mm.
rb_w = 47.8;  rb_l = 52.0;  rb_pcb = 1.5;  rb_h = 5.9;
rb_lift   = 12.5;   // PCB underside above floor (lowest part 1.4 mm off floor)
rb_slot   = 1.80;   // FDM slot height (GC moulded mount: 1.70 +/-0.05). Tune with coupon_rails.
rb_engage = 1.2;    // lip engagement on each PCB edge
rb_sidec  = 0.3;    // side clearance
rb_sma_dx = 8.45;  rb_sma_z = -6.35;  rb_sma_out = 7.2;

// ---------------- derived cavity ----------------
in_w   = 52.5;
in_l   = sma_clear + sup_l + usb_clear;            // 136.0
ledge_z = rb_lift + rb_h + 0.8;                    // separator underside
sep_t  = 3.0;
sup_z0 = ledge_z + sep_t;                          // separator top
pcb_z  = sup_z0 + foam_c + hold_drop;              // Supreme PCB underside
in_h   = pcb_z + top_max + 1.5;                    // 1.5 mm over the tallest part
body_h = floor_t + in_h;
out_w = in_w + 2*wall;  out_l = in_l + 2*wall;
cx     = in_w/2;                                   // board centreline (both boards)
sup_x0 = cx - sup_w/2;
sup_ytop = in_l - sma_clear;                       // Supreme PCB SMA-end edge
function by(b) = sup_ytop - b;                     // board-y -> cavity y
rb_x0 = cx - rb_w/2;
rb_y1 = in_l - sma_clear;   rb_y0 = rb_y1 - rb_l;

// ---------------- screws / seal ----------------
pil_r = 7.0;  insert_d = 4.0;  insert_h = 7.0;     // M3 heat-set, <=5.7 long: pocket 7.0
screw_d = 3.4; head_d = 6.0; head_h = 3.2;        // lid: M3x8 -> 5.7 below mating face
cord_d  = 2.0;                                     // F07: 2.0 mm silicone cord
g_in = 1.15; g_out = 3.85; groove_d = 1.5;         // 2.7 x 1.5 -> 77.6 % fill, 25 % squeeze
mid_ys  = [22, in_l - 40];
pillars = concat([[1,1],[in_w-1,1],[1,in_l-1],[in_w-1,in_l-1]],
                 [for(y=mid_ys) [-1,y]], [for(y=mid_ys) [in_w+1,y]]);
function is_corner(p) = (p[1] < 5 || p[1] > in_l-5);

// ---------------- ports ----------------
sma_hole = 6.6;
lora_bh  = [39, pcb_z + 3.5];          // x,z on the top wall
iri_bh   = [14, 9];
usbc_hole = 16.2;   usb_bh = [18, 10.5];  // [VERIFY] against the chosen panel USB-C (nut up to 20 mm OD)
vent_d    = 12.3;   vent_by = 35;  vent_z = 9;   // vent on the RIGHT side wall, lower bay
// SOS (12 mm IP67 momentary), guarded; switch body must stay below the Supreme
// SMA-end overhang (STEP: z >= PCB underside + 1 out to board-y -4.2)
sos_hole = 12.2;  sos_depth = 20;  sos_x = 17;  sos_z = pcb_z - 6.5;
shroud_id = 21;  shroud_od = 27;  shroud_h = 8;  drain_w = 3;  drain_h = 1.5;

// ---------------- carry plates ----------------
rear_ins_h = 7.0;
plate_t = 3.0;
strap_w = 26.5;  strap_gap = 3.6;  molle_pitch = 38.1;  skin_t = 2.4;  rail_t = 2.5;
belt_w = 40;  belt_gap = 5.6;
tab_l = 14;  lanyard_slot = [16,6];
rear_pts = [[wall+1,wall+1],[out_w-wall-1,wall+1],[wall+1,out_l-wall-1],[out_w-wall-1,out_l-wall-1]];

// ---------------- side buttons: membrane + guided plungers ----------------
btn_y     = [for(b=btn_by) by(b)];          // cavity y
btn_z     = pcb_z - btn_drop;               // cavity z
btn_face  = sup_x0 - btn_prot;              // actuator face, cavity x
pl_gap    = 0.3;                            // plunger-to-actuator gap at rest (no preload)
pl_travel = 0.65;                           // hard stop: max plunger travel
strip_y0  = min(btn_y) - 8;  strip_len = max(btn_y) - min(btn_y) + 16;
flange_t = 1.5;  pocket_d = 1.2;            // 0.3 mm (20 %) flange compression, wall is the stop
fl_h  = 14;      ret_t = 3.0;  ret_h = 24;  // retainer covers flange + screw rows
cap_d = 5.4;     cap_out = 0.8;             // cap protrudes 0.8 mm
pl_head_d = 5.0; pl_head_t = 1.0; pl_d = 3.0;
ret_screw_dy = [3, strip_len/2, strip_len-3];   // 6x M2x6: rows at +/-9.5 mm

assert(r_top <= lid_t/2, "lid round-over would breach the mating plane");
assert(groove_d < lid_t - r_top, "groove too deep for lid");
assert(sos_z + sos_hole/2 + 0.3 < pcb_z + 1, "SOS switch would hit the Supreme SMA-end overhang");

// =====================================================================
module rbox(w,l,h,r){ linear_extrude(h) offset(r) offset(delta=-r) square([w,l]); }
// slab with rounded vertical edges (rv) and 45 deg chamfers on the bottom (rb) / top (rt)
// edges; clipped to 0..h so no edge treatment can cross a mating plane (F01)
module rshell(w,l,h,rv,rb,rt){
  intersection(){
    hull() for(x=[rv,w-rv], y=[rv,l-rv]) translate([x,y,0]) rotate_extrude($fn=56)
      polygon([[0,0],[rv-rb,0],[rv,rb],[rv,h-rt],[rv-rt,h],[0,h]]);
    translate([-1,-1,0]) cube([w+2,l+2,h]);
  }
}
module at_in(){ translate([wall,wall,floor_t]) children(); }
module cavity2d(){
  difference(){ offset(r=1.5) offset(delta=-1.5) square([in_w,in_l]);
                for(p=pillars) translate(p) circle(pil_r); }
}

// ---------------- BODY ----------------
module body_shell(){
  difference(){
    rshell(out_w,out_l,body_h,cr_out,r_bot,0);
    at_in() cube([in_w,in_l,in_h+1]);
    for(b=[lora_bh,iri_bh]) translate([wall+b[0],out_l-wall-1,floor_t+b[1]]) rotate([-90,0,0]) cylinder(d=sma_hole,h=wall+2);
    translate([wall+sos_x,out_l-wall-1,floor_t+sos_z]) rotate([-90,0,0]) cylinder(d=sos_hole,h=wall+2);
    translate([wall+usb_bh[0],-1,floor_t+usb_bh[1]]) rotate([-90,0,0]) cylinder(d=usbc_hole,h=wall+2);
    translate([out_w-wall-1,wall+vent_by,floor_t+vent_z]) rotate([0,90,0]) cylinder(d=vent_d,h=wall+2);
  }
  // SOS guard: self-supporting (45 deg gusset below, teardrop bore), drains at the sides/top
  translate([wall+sos_x,out_l-0.01,floor_t+sos_z]) difference(){
    hull(){ rotate([-90,0,0]) cylinder(d=shroud_od,h=shroud_h,$fn=64);
            translate([0,0,-shroud_od/2-shroud_h]) rotate([-90,0,0]) cylinder(d=shroud_od*0.6,h=0.01,$fn=64); }
    translate([0,-1,0]) rotate([-90,0,0]) linear_extrude(shroud_h+2)
      hull(){ circle(d=shroud_id,$fn=64); translate([0,-shroud_id/2*1.414]) circle(d=0.1); }   // apex +z (rotated frame)
    for(a=[0,180,-90]) rotate([0,a,0]) translate([shroud_id/2-1,-0.01,-drain_w/2]) cube([5,drain_h+0.01,drain_w]);   // +x, -x, +z
  }
  at_in(){
    intersection(){
      cube([in_w,in_l,in_h]);
      union() for(p=pillars) translate([p[0],p[1],0])
        if(is_corner(p)) cylinder(r=pil_r,h=in_h);
        else translate([0,0,in_h-14]) union(){ cylinder(r=pil_r,h=14); translate([0,0,-6]) cylinder(r1=1,r2=pil_r,h=6); }
    }
    // separator ledges (45 deg chamfer below)
    for(s=[0,1]) translate([s==0?0:in_w,0,0]) mirror([s,0,0])
      hull(){ translate([0,0,ledge_z-0.01]) cube([1.5,in_l,0.01]); translate([0,0,ledge_z-1.5]) cube([0.01,in_l,0.01]); }
    rb_rails();
    // 9704 stop at the SMA end
    translate([rb_x0+rb_w-16,rb_y1+0.3,0]) cube([10,2,rb_lift+rb_pcb+1.0]);
  }
}
// F03: real lips (rb_engage over each PCB edge), lead-in, lock screws at the insertion end
rail_y0 = rb_y0 - 4;
module rb_rails(){
  for(s=[0,1]) {
    x_out = s==0 ? rb_x0-3 : rb_x0+rb_w-rb_engage;
    difference(){
      translate([x_out, rail_y0, 0]) cube([3+rb_engage, rb_y1-rail_y0, rb_lift-0.1+rb_slot+1.5]);
      // slot: full engagement depth + side clearance
      translate([s==0 ? rb_x0-rb_sidec : rb_x0+rb_w-rb_engage-0.1, rail_y0-1, rb_lift-0.1])
        cube([rb_engage+rb_sidec+0.1, rb_y1-rail_y0+2, rb_slot]);
      // lead-in flare over the first 3 mm
      xs = s==0 ? rb_x0-rb_sidec : rb_x0+rb_w-rb_engage-0.1;
      hull(){ translate([xs, rail_y0-1, rb_lift-0.7]) cube([rb_engage+rb_sidec+0.1, 1.01, rb_slot+1.2]);
              translate([xs, rail_y0+3, rb_lift-0.1]) cube([rb_engage+rb_sidec+0.1, 0.01, rb_slot]); }
      // lock-screw hole (M3x16 self-tapping from the top; shank blocks the board end)
      translate([s==0 ? rb_x0-0.3 : rb_x0+rb_w+0.3, rb_y0-1.6, -0.1]) cylinder(d=2.6,h=30);
    }
  }
}
module body(){
  difference(){
    body_shell();
    // inserts cut AFTER every union (F04)
    for(p=pillars) translate([wall+p[0],wall+p[1],body_h-insert_h]) cylinder(d=insert_d,h=insert_h+1);
    for(p=rear_pts) translate([p[0],p[1],-0.01]) cylinder(d=insert_d,h=rear_ins_h+0.01);
    // button caps, membrane pocket, retainer screw pilots (left wall)
    for(y=btn_y) translate([-1,wall+y,floor_t+btn_z]) rotate([0,90,0]) cylinder(d=6.0,h=wall+2);
    translate([wall-pocket_d,wall+strip_y0-0.2,floor_t+btn_z-fl_h/2-0.2]) cube([pocket_d+0.01,strip_len+0.4,fl_h+0.4]);
    for(dy=ret_screw_dy, dz=[-9.5,9.5]) translate([wall-3.3,wall+strip_y0+dy,floor_t+btn_z+dz]) rotate([0,90,0]) cylinder(d=1.6,h=3.31);
  }
}

// ---------------- SEPARATOR + SUPREME CRADLE ----------------
module separator(){
  linear_extrude(sep_t) difference(){
    offset(delta=-0.3) square([in_w,in_l]);
    for(p=pillars) translate(p) circle(pil_r+0.4);
    translate([cx+sup_usb_dx-6, 2]) square([12,usb_clear-3]);                  // USB pigtail
    translate([usb_bh[0]-12, -1]) square([24, 7]);                              // panel USB-C nut clearance
    translate([sup_x0+sup_w+0.8, rb_y0-9]) square([in_w-sup_x0-sup_w-2.5,8]);   // 9704 harness
  }
  // stiffening ribs on the TOP face (F09: flat underside on the bed)
  for(x=[sup_x0+3, sup_x0+sup_w-5]) translate([x,usb_clear,sep_t-0.01]) cube([2,in_l-usb_clear-sma_clear,1.21]);
  translate([0,0,sep_t]) supreme_cradle();
}
module supreme_cradle(){
  hz = foam_c;                                  // holder bottom above separator top
  seat_h = foam_c + hold_drop;                  // PCB underside above separator top
  // loose saddles: lateral guidance only; PCB lips are the datum
  for(b=[20,48,76]) translate([0,by(b)-1.5,0]) difference(){
    translate([cx-hold_r-4,0,0]) cube([2*hold_r+8,3,hold_r*0.8+hz]);
    translate([cx,-1,hz+hold_r]) rotate([-90,0,0]) cylinder(r=hold_r+2.5,h=5,$fn=96);
  }
  // PCB seats on the bare 1.3 mm edge strips + outer lips boxing the edges (0.2 clearance)
  for(b=seat_by, s=[0,1]){
    y=by(b);
    xin = s==0 ? sup_x0 : sup_x0+sup_w-edge_strip;
    translate([xin, y-2, 0]) cube([edge_strip, 4, seat_h]);
    xl = s==0 ? sup_x0-1.8 : sup_x0+sup_w+0.2;
    translate([xl, y-2, 0]) cube([1.6, 4, seat_h+pcb_t+0.6]);
    translate([s==0 ? xl : sup_x0+sup_w-edge_strip, y-2, 0]) cube([1.6+edge_strip+0.2, 4, seat_h-0.01]);  // web
  }
  // SMA-end stops: face the PCB edge only (below the STEP overhang at z >= PCB+1)
  for(s=[-1,1]) translate([s<0 ? cx-18 : cx+14.7, sup_ytop+0.2, 0]) cube([3.3, 1.8, seat_h+0.9]);
  // USB-end stops: face the underside block/USB-C ends (board-y 100.95 + 0.2)
  for(s=[-1,1]) translate([s<0 ? cx-18 : cx+14, by(sup_l+usb_out+0.2)-1.8, 0]) cube([4, 1.8, seat_h-0.5]);
}

// ---------------- LID ----------------
module lid(){
  wx=wall+cx; wy=wall+by(oled_cy);
  difference(){
    rshell(out_w,out_l,lid_t,cr_out,0,r_top);
    translate([wall,wall,-0.01]) linear_extrude(groove_d+0.01)
      difference(){ offset(r=g_out) cavity2d(); offset(r=g_in) cavity2d(); }
    for(p=pillars){ translate([wall+p[0],wall+p[1],-1]) cylinder(d=screw_d,h=lid_t+2);
      translate([wall+p[0],wall+p[1],lid_t-head_h]) cylinder(d=head_d,h=head_h+1); }
    translate([wx-win_x/2,wy-win_y/2,-1]) cube([win_x,win_y,lid_t+2]);
    px=pane_x+2*pane_clr; py=pane_y+2*pane_clr;
    translate([wx-px/2,wy-py/2,-0.01]) cube([px,py,pane_t+bond_t+0.01]);
    translate([wx,wy,lid_t-1.2]) linear_extrude(1.21,scale=[(win_x+2.4)/win_x,(win_y+2.4)/win_y]) square([win_x,win_y],center=true);
  }
  // hold-downs directly over the seats, bearing on the bare edge strips (F02)
  bh = in_h - (pcb_z + pcb_t) - pad_c;
  for(b=boss_by, s=[0,1]){
    x = s==0 ? sup_x0-3 : sup_x0+sup_w-edge_strip;
    translate([wall+x, wall+by(b)-2, -bh]) cube([3+edge_strip, 4, bh+0.01]);
  }
}

// ---------------- buttons: TPU membrane, rigid plungers, retainer (F08) ----------------
// Local frame: x along the wall normal (0 = inner wall face, - = outward), y along strip.
module membrane(){                   // print flat: flange down, caps up
  difference(){
    union(){
      cube([strip_len, fl_h, flange_t]);
      for(y=btn_y) translate([y-strip_y0, fl_h/2, flange_t-0.01]) cylinder(d=cap_d, h=wall-pocket_d+cap_out+0.01);
    }
    for(y=btn_y) translate([y-strip_y0, fl_h/2, -0.01]) difference(){ cylinder(d=8.5,h=0.75); translate([0,0,-0.1]) cylinder(d=cap_d+0.2,h=1); }
  }
}
pl_len = btn_face - pl_gap;           // head face (x=0) to tip
module plunger(){                     // print standing, head down
  cylinder(d=pl_head_d, h=pl_head_t); cylinder(d=pl_d, h=pl_len);
}
module plungers(){ for(i=[0:2]) translate([i*8,0,0]) plunger(); }
module retainer(){                    // print flat
  difference(){
    cube([strip_len, ret_h, ret_t]);
    for(y=btn_y){ translate([y-strip_y0, ret_h/2, -0.01]) cylinder(d=pl_head_d+0.6, h=pl_head_t+pl_travel+0.01);
                  translate([y-strip_y0, ret_h/2, -1]) cylinder(d=pl_d+0.3, h=ret_t+2); }
    for(dy=ret_screw_dy, dz=[-9.5,9.5]) translate([dy, ret_h/2+dz, -1]) cylinder(d=2.3, h=ret_t+2);
  }
}
// assembled placements (left wall)
// local (u along strip, v up, w thickness) -> body; flange shown compressed into its pocket
module a_membrane(){ multmatrix([[0,0,-1,wall-pocket_d+flange_t],[1,0,0,wall+strip_y0],[0,1,0,floor_t+btn_z-fl_h/2],[0,0,0,1]]) membrane(); }
module a_retainer(){ multmatrix([[0,0,1,wall],[1,0,0,wall+strip_y0],[0,1,0,floor_t+btn_z-ret_h/2],[0,0,0,1]]) retainer(); }
module a_plungers(){ for(y=btn_y) translate([wall, wall+y, floor_t+btn_z]) rotate([0,90,0]) plunger(); }

// ---------------- CARRY PLATES (modelled outer face z=0; exported body-face down) ----------------
module plate_base(w_extra=0){
  difference(){
    translate([-w_extra/2,0,0]) rbox(out_w+w_extra,out_l+tab_l,plate_t,cr_out);
    for(p=rear_pts){ translate([p[0],p[1],-1]) cylinder(d=3.4,h=plate_t+2); translate([p[0],p[1],-0.01]) cylinder(d1=6.6,d2=3.4,h=1.7); }
    translate([out_w/2-lanyard_slot[0]/2, out_l+tab_l/2-lanyard_slot[1]/2, -1]) cube([lanyard_slot[0],lanyard_slot[1],plate_t+2]);
  }
}
molle_w = molle_pitch + strap_w + 2*rail_t;      // 69.6
module molle_plate(){
  h = plate_t + strap_gap + skin_t;  y0 = 12; y1 = out_l - 12;  c = out_w/2;
  difference(){
    union(){ translate([0,0,h-plate_t]) plate_base(molle_w-out_w); translate([c-molle_w/2, y0, 0]) cube([molle_w, y1-y0, h]); }
    for(sx=[-1,1]) translate([c+sx*molle_pitch/2-strap_w/2, y0-1, skin_t]) cube([strap_w, y1-y0+2, strap_gap]);
  }
}
module belt_plate(){
  h = plate_t + belt_gap + skin_t;  yc = out_l*0.55;
  difference(){
    union(){ translate([0,0,h-plate_t]) plate_base(0); translate([0, yc-belt_w/2-3, 0]) rbox(out_w, belt_w+6, h, 1.5); }
    translate([-1, yc-belt_w/2, skin_t]) cube([out_w+2, belt_w, belt_gap]);
  }
}

// ---------------- reference boards (STEP tessellations) ----------------
module supreme_ref(){ translate([cx, sup_ytop-50, pcb_z]) rotate([0,0,180]) import(str(REF,"supreme_step.stl")); }
module rb9704_ref(){  translate([rb_x0-67.3, rb_y1-116.4, rb_lift]) rotate([0,0,90]) import(str(REF,"rb9704_step.stl")); }
module battery_env(){  // not in STEP: holder envelope per LilyGO shell
  translate([cx, by(100-12-77)-77, sup_z0+foam_c+hold_r]) rotate([-90,0,0]) cylinder(r=hold_r,h=77);
}

// ---------------- ghosts: cables, bought parts, antennas ----------------
module cable(pts,d=2.2){ for(i=[0:len(pts)-2]) hull(){ translate(pts[i]) sphere(d=d,$fn=12); translate(pts[i+1]) sphere(d=d,$fn=12);} }
module bought_parts(){
  sx=cx+sup_sma_dx;
  color("black") cable([[sx,sup_ytop+12,pcb_z+3.5],[sx,sup_ytop+15,pcb_z+3.5],[lora_bh[0],in_l-9,lora_bh[1]],[lora_bh[0],in_l-8,lora_bh[1]]]);
  rx=rb_x0+rb_sma_dx;
  color("black") cable([[rx,rb_y1+rb_sma_out+2,rb_lift+rb_sma_z],[rx+1,rb_y1+rb_sma_out+6,rb_lift+rb_sma_z+2],[iri_bh[0],in_l-9,iri_bh[1]],[iri_bh[0],in_l-8,iri_bh[1]]]);
  ux=cx+sup_usb_dx;
  color("dimgray") cable([[ux,usb_clear-3,pcb_z-1.5],[ux,usb_clear-7,sup_z0+2],[ux,6,ledge_z-3],[usb_bh[0]+6,8,usb_bh[1]+4],[usb_bh[0],10,usb_bh[1]]],d=3.5);
  hx=sup_x0+sup_w+3;
  color("orange") cable([[sup_x0+sup_w-1,by(25),pcb_z+2],[hx,by(25),pcb_z],[hx+1,rb_y0-5,sup_z0+2],[hx+1,rb_y0-5,rb_lift-6],[rb_x0+34,rb_y0+0.5,rb_lift-9.5],[rb_x0+34,rb_y0+3,rb_lift-9.5]],d=3);
  color("gold") for(b=[lora_bh,iri_bh]){ translate([b[0],in_l-9,b[1]]) rotate([-90,0,0]) cylinder(d=6.3,h=9+wall+8);
    translate([b[0],in_l-4,b[1]]) rotate([-90,0,0]) cylinder(d=9,h=2.5,$fn=6); }
  color("dimgray") translate([usb_bh[0],-wall-6,usb_bh[1]]) rotate([-90,0,0]) cylinder(d=15.5,h=wall+6+16);
  color("red") translate([sos_x,in_l+wall+0.5,sos_z]) rotate([-90,0,0]) cylinder(d=14,h=2);
  color("silver") translate([sos_x,in_l-sos_depth,sos_z]) rotate([-90,0,0]) cylinder(d=12,h=sos_depth+wall+0.5);
  color("white") translate([in_w-3,vent_by,vent_z]) rotate([0,90,0]) cylinder(d=12,h=wall+3+6);
  color("gray") for(s=[0,1]) translate([s==0 ? rb_x0+0.5 : rb_x0+rb_w-0.5, rb_y0-1.6, 0]) cylinder(d=3,h=rb_lift+rb_slot+1.4+2.5);  // lock screws
}
iri_d = 19;  iri_len = 49;  lora_d = 10; lora_len = 110;
module antennas(){
  color("black") translate([iri_bh[0],in_l+wall+8,iri_bh[1]]) rotate([-90,0,0]) cylinder(d=iri_d,h=iri_len);
  color("dimgray") translate([lora_bh[0],in_l+wall+8,lora_bh[1]]) rotate([-90,0,0]) { cylinder(d=8,h=15); translate([0,0,15]) cylinder(d=lora_d,h=lora_len-15); }
}

// ---------------- coupons ----------------
module coupon_rimlid(){
  band = 12;
  translate([0,0,-(body_h-band)]) intersection(){ body(); translate([-5,-5,body_h-band]) cube([out_w+10,out_l+20,band+1]); }
  translate([out_w+12,out_l,lid_t]) rotate([180,0,0]) lid();
}
module coupon_board(){
  z0 = floor_t + ledge_z - 2;
  translate([0,0,-z0]) intersection(){ body(); translate([-5,-5,z0]) cube([out_w+10,out_l+20,body_h]); }
}
module coupon_rails(){          // 14 mm slice of floor + both rails + side walls
  L=14; y0=wall+rb_y0+18;
  translate([0,-y0,0]) intersection(){ body(); translate([-1, y0, -1]) cube([out_w+2, L, floor_t+rb_lift+rb_slot+2.5]); }
}

// ---------------- exploded view ----------------
ex_dz = [ -45, 0, 75, 110, 150, 230 ];
ex_side = "front";
module ruler(len, step=10, label=50){
  color("white") cube([len,20,1]);
  for(i=[0:5:len]) color("black") translate([i-0.4, 0, 1]) cube([0.8, (i%label==0)?11:((i%step==0)?7:4), 0.3]);
  for(i=[0:label:len]) color("black") translate([i, 12.5, 1]) linear_extrude(0.3) text(str(i), size=6, halign="center");
  color("black") translate([len+4, 6, 1]) linear_extrude(0.3) text("mm", size=7);
}
module euro2(){
  color("silver") difference(){ cylinder(d=25.75,h=2.2,$fn=96); translate([0,0,-1]) cylinder(d=18.75,h=5,$fn=96); }
  color("goldenrod") cylinder(d=18.75,h=2.2,$fn=96);
  color("black") translate([0,0,2.2]) linear_extrude(0.3) text("2 EUR", size=3.6, halign="center", valign="center");
}
module exploded(){
  color(case_rgb) translate([0,0,ex_dz[0]-9]) molle_plate();
  color(case_rgb) body();
  translate([0,0,ex_dz[2]]) at_in() color("darkred") rb9704_ref();
  color(case_rgb) translate([0,0,ex_dz[3]]) at_in() translate([0,0,ledge_z]) separator();
  translate([0,0,ex_dz[4]]) at_in(){ color("darkgreen") supreme_ref(); color("royalblue",0.6) battery_env(); }
  color(case_rgb) translate([0,0,ex_dz[5]]) lid();
  color("lightblue",0.6) translate([wall+cx-pane_x/2, wall+by(oled_cy)-pane_y/2, ex_dz[5]-12]) cube([pane_x,pane_y,pane_t]);
  // side-button stack pulled straight out of the left wall, in assembly order:
  // TPU membrane (outside) -> 3 plungers -> retainer (inside). One set of 3 buttons.
  color(case_rgb) translate([-110,0,45]) a_membrane();
  color(case_rgb) translate([-85,0,45]) a_plungers();
  color(case_rgb) translate([-62,0,45]) a_retainer();
  translate([0,40,0]) at_in() antennas();
  if(ex_side=="front"){
    translate([-50,-20,ex_dz[0]-9]) rotate([0,0,90]) translate([0,-20,0]) ruler(200);
    translate([0,-85,ex_dz[0]-9]) ruler(100);  translate([-30,-65,ex_dz[0]-9]) euro2();
  } else {
    translate([out_w+50,out_l+60,ex_dz[0]-9]) rotate([0,0,-90]) translate([0,-20,0]) ruler(200);
    translate([out_w,out_l+110,ex_dz[0]-9]) rotate([0,0,180]) translate([0,-20,0]) ruler(100);
    translate([out_w+30,out_l+85,ex_dz[0]-9]) euro2();
  }
}

// =====================================================================
if      (PART=="body")      body();
else if (PART=="lid")       translate([0,out_l,lid_t]) rotate([180,0,0]) lid();
else if (PART=="separator") separator();
else if (PART=="membrane")  membrane();
else if (PART=="plungers")  plungers();
else if (PART=="retainer")  retainer();
else if (PART=="molle")     translate([0,out_l+tab_l,plate_t+strap_gap+skin_t]) rotate([180,0,0]) molle_plate();
else if (PART=="belt")      translate([0,out_l+tab_l,plate_t+belt_gap+skin_t]) rotate([180,0,0]) belt_plate();
else if (PART=="coupon_rimlid") coupon_rimlid();
else if (PART=="coupon_board")  coupon_board();
else if (PART=="coupon_rails")  coupon_rails();
else if (PART=="exploded")  exploded();
else if (PART=="button_detail") {   // side-button stack, exploded along the wall normal, with the wall section
  color(case_rgb) intersection(){ body(); translate([-1,wall+strip_y0-6,floor_t+btn_z-16]) cube([wall+14,strip_len+12,32]); }
  color(case_rgb) translate([-25,0,0]) a_membrane();
  color("#C04A00") translate([22,0,0]) a_plungers();
  color(case_rgb) translate([48,0,0]) a_retainer();
}
else if (PART=="a_body")    body();
else if (PART=="a_lid")     translate([0,0,body_h]) lid();
else if (PART=="a_separator") at_in() translate([0,0,ledge_z]) separator();
else if (PART=="a_membrane")  a_membrane();
else if (PART=="a_plungers")  a_plungers();
else if (PART=="a_retainer")  a_retainer();
else if (PART=="a_parts")     at_in() bought_parts();
else if (PART=="none") {}
// ---- self-checks: each must export EMPTY except chk_rail_lip (must be > 0) ----
else if (PART=="chk_groove")    intersection(){ lid(); translate([wall,wall,0.001]) linear_extrude(groove_d-0.002) difference(){ offset(r=g_out-0.01) cavity2d(); offset(r=g_in+0.01) cavity2d(); } }
else if (PART=="chk_rearbores") intersection(){ body(); for(p=rear_pts) translate([p[0],p[1],0.01]) cylinder(d=insert_d-0.02,h=rear_ins_h-0.02); }
else if (PART=="chk_topbores")  intersection(){ body(); for(p=pillars) translate([wall+p[0],wall+p[1],body_h-insert_h+0.01]) cylinder(d=insert_d-0.02,h=insert_h-0.02); }
else if (PART=="chk_lid_body")  intersection(){ body(); translate([0,0,body_h]) lid(); }
else if (PART=="chk_rail_lip")  intersection(){ body(); at_in() for(x=[rb_x0+0.05, rb_x0+rb_w-rb_engage+0.05]) for(z=[rb_lift-0.1-1.0, rb_lift-0.1+rb_slot+0.05]) translate([x, rb_y0+2, z]) cube([rb_engage-0.1, rb_l-4, 0.9]); }
else if (PART=="reg") echo(str("REGJSON {\"sup_T\":[",wall+cx,",",wall+sup_ytop-50,",",floor_t+pcb_z,"],\"rb_T\":[",wall+rb_x0-67.3,",",wall+rb_y1-116.4,",",floor_t+rb_lift,"],\"hold_r\":",hold_r,",\"hold_l\":77,\"hold_c\":[",wall+cx,",",wall+by(88)+38.5,",",floor_t+sup_z0+foam_c+hold_r,"]}"));
else {
  color(case_rgb) body();
  color(case_rgb) at_in() translate([0,0,ledge_z]) separator();
  color(case_rgb,0.5) translate([0,0,body_h]) lid();
  color(case_rgb) a_membrane(); color(case_rgb) a_plungers(); color(case_rgb) a_retainer();
  at_in(){ color("darkgreen") supreme_ref(); color("darkred") rb9704_ref(); color("royalblue",0.5) battery_env(); bought_parts(); antennas(); }
  echo(str("ENVELOPE body+lid: ", out_w, " x ", out_l, " x ", body_h+lid_t, " mm; with SOS guard length ", out_l+shroud_h));
  echo(str("REG pcb_z=",pcb_z," in_h=",in_h," ledge_z=",ledge_z," sup_z0=",sup_z0));
}
