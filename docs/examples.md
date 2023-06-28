# PyPEEC - Included Examples

## Running the Example Problems

The following files should be used to **run the examples**:
* For running the examples from a **Jupyter notebook**, use `examples/notebook.ipynb`.
* For running the examples from **Python**:
  * `examples/examples_config.py` is used to select the example
  * `examples/run_mesher.py` runs the mesher
  * `examples/run_viewer.py` runs the viewer
  * `examples/run_solver.py` runs the solver
  * `examples/run_plotter.py` runs the plotter
* For running the examples from the **Shell**:
  * `examples/examples_config.sh` is used to select the example
  * `examples/run_mesher.sh` runs the mesher
  * `examples/run_viewer.sh` runs the viewer
  * `examples/run_solver.sh` runs the solver
  * `examples/run_plotter.sh` runs the plotter

## Example Problems (STL Mesher)

### examples_stl/inductor_air

* **3D air-core inductor**
* Defined with **STL files**

![examples_stl_inductor_air](examples/examples_stl_inductor_air.png)

### examples_stl/inductor_core

* **3D inductor with a magnetic E-core**
* Defined with **STL files**

![examples_stl_inductor_core](examples/examples_stl_inductor_core.png)


### examples_stl/transformer

* **Planar transformer with two windings**
* Defined with **STL files**

![examples_stl_transformer](examples/examples_stl_transformer.png)

## Example Problems (Shape Mesher)

### examples_shape/busbar

* **Coplanar L-shaped busbar**
* Defined with **2D shapes**

![examples_shape_busbar](examples/examples_shape_busbar.png)

### examples_shape/coplanar

* **PCB with coplanar traces** (defined with 2D shapes)
* Defined with **2D shapes**

![examples_shape_coplanar](examples/examples_shape_coplanar.png)

### examples_shape/trace

* **PCB with two traces**
* Defined with **2D shapes**

![examples_shape_trace](examples/examples_shape_trace.png)

### examples_shape/wire

* **Straight round wire**
* Defined with **2D shapes**

![examples_shape_wire](examples/examples_shape_wire.png)

## Example Problems (PNG Mesher)

### examples_png/inductor_spiral

* **Planar spiral inductor**
* Defined with **PNG files**

![examples_png_inductor_spiral](examples/examples_png_inductor_spiral.png)

### examples_png/inductor_gap

* **Gapped inductor with a magnetic E-core**
* Defined with **PNG files**

![examples_png_inductor_gap](examples/examples_png_inductor_gap.png)

### examples_png/shield

* **Conductor loop with a magnetic shield**
* Defined with **PNG files**

![examples_png_shield](examples/examples_png_shield.png)

### examples_png/gerber

* **PCB inductor defined with GERBER files**
* The **PNG files** are generated from **GERBER files**

![examples_png_gerber](examples/examples_png_gerber.png)

## Example Problems (Voxel Mesher)

### examples_voxel/slab

* **Simple slab conductor in free space**
* Defined with **voxel indices**

![examples_voxel_slab](examples/examples_voxel_slab.png)

### examples_voxel/core

* **Simple slab conductor surrounded by a magnetic core**
* Defined with **voxel indices**

![examples_voxel_core](examples/examples_voxel_core.png)

### examples_voxel/transformer

* **Simple transformer with a short-circuited winding**
* Defined with **voxel indices**

![examples_voxel_transformer](examples/examples_voxel_transformer.png)

### examples_voxel/logo

* **Simple geometry used for the PyPEEC logo**
* Defined with **voxel indices**

![examples_voxel_logo](examples/examples_voxel_logo.png)