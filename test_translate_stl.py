import pyvista as pv

coil = pv.read("examples/stl_inductor_core/stl/coil.stl")
src = pv.read("examples/stl_inductor_core/stl/src.stl")
sink = pv.read("examples/stl_inductor_core/stl/sink.stl")
core = pv.read("examples/stl_inductor_core/stl/core.stl")

s = 20

coil = coil.scale((s, s, s))
src = src.scale((s, s, s))
sink = sink.scale((s, s, s))
core = core.scale((s, s, s))

(x_min, x_max, y_min, y_max, z_min, z_max) = coil.bounds

print(1e3*(x_max-x_min))
print(1e3*(y_max-y_min))

coil.save('coil.stl')
src.save('src.stl')
sink.save('sink.stl')
core.save('core.stl')
