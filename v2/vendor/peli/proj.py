import sys
from build123d import import_step, ExportSVG, Vector, LineType
shape = import_step(sys.argv[1]); out = sys.argv[2]
views = {'top_from_+Y': ((0, 1000, 0), (0, 0, -1)), 'bottom_from_-Y': ((0, -1000, 0), (0, 0, 1)), 'front_from_+Z': ((0, 0, 1000), (0, 1, 0)), 'end_from_+X': ((1000, 0, 0), (0, 1, 0)), 'iso': ((700, 900, 800), (0, 1, 0))}
for name, (origin, up) in views.items():
    vis, hid = shape.project_to_viewport(viewport_origin=Vector(*origin), viewport_up=Vector(*up), look_at=Vector(0, 0, 0))
    ex = ExportSVG(scale=1.0, line_weight=0.35)
    ex.add_layer('vis', line_weight=0.5); ex.add_layer('hid', line_weight=0.2, line_type=LineType.ISO_DASH)
    ex.add_shape(vis, layer='vis'); ex.add_shape(hid, layer='hid')
    ex.write('%s-%s.svg' % (out, name)); print('wrote', '%s-%s.svg' % (out, name))
