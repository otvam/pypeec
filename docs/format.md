# PyPEEC - File Formats

## Workflow

![viewer](images/workflow.png)

## Mesher File Format

The `file_mesher` file format is used by the mesher.

## Problem File Format

The `file_problem` file format is used by the solver.
Definition of the magnetic problem to be solved.

```yaml
 # operating frequency for the problem (DC or AC)
"freq": 1.0e+3

# material definition
#   - dict with the material name and the material definition
#   - magnetic materials
#       - domain_list: list of domains with the specified material
#       - material_type: material type ("magnetic" for magnetic materials)
#       - chi_re: material real susceptibility (should be positive)
#       - chi_im: material imaginary susceptibility (should be positive)
#   - electric materials
#       - domain_list: list of domains with the specified material
#       - material_type: material type ("electric" for electric materials)
#       - rho: material resistivity (should be positive)
"material_def":
    "material_magnetic": {"domain_list": ["domain_1", "domain_2", "domain_3"], "material_type": "electric", "rho": 1.0e-8}
    "material_electric": {"domain_list": ["domain_4"], "material_type": "magnetic", "chi_re": 100.0, "chi_im": 10.0}

# source definition
#   - dict with the source name and the source definition
#   - sources can only be defined on electric material domains
#   - voltage sources
#       - domain_list: list of domains with the specified source
#       - source_type: source type ("current" for current source)
#       - I_re: current source value (real part)
#       - I_im: current source value (imaginary part)
#       - Y_re: current internal admittance (real part)
#       - Y_im: current internal admittance (imaginary part)
#   - voltage sources
#       - domain_list: list of domains with the specified source
#       - source_type: source type ("voltage" for voltage source)
#       - V_re: voltage source value (real part)
#       - V_im: voltage source value (imaginary part)
#       - Z_re: voltage internal impedance (real part)
#       - Z_im: voltage internal impedance (imaginary part)
"source_def":
    "src": {"domain_list": ["domain_1"], "source_type": "current", "I_re": 1.0, "I_im": 0.0, "Y_re": 0.5, "Y_im": 0.0}
    "sink": {"domain_list": ["domain_3"], "source_type": "voltage", "V_re": 0.0, "V_im": 0.0, "Z_re": 2.0, "Z_im": 0.0}
```

## Point File Format

The `file_point` file format is used by the viewer and plotter.
Definition of the points used for magnetic field evaluation.

```yaml
# 2D array containing the points used for magnetic field evaluation.
# The number of points (n_pts) can be zero.
# The array has the following size: (n_pts, 3).

[
    [-1.0, 1.0, 1.0],
    [1.0, -1.0, 1.0],
    [1.0, 1.0, -1.0],
]
```

## Other Files

* The `file_tolerance` format is documented in `examples/run_config.py`.
* The `file_viewer` format is documented in `examples/run_config.py`.
* The `file_plotter` format is documented in `examples/run_config.py`.
* The configuration file format is documented in `PyPEEC/pypeec.yaml`.
