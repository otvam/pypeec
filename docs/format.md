# PyPEEC - File Formats

## Workflow

![viewer](images/workflow.png)

## Mesher File Format

The `file_mesher` file format is used by the mesher.
This file contains the definition of the voxel structure.

### Definition from Index Arrays

```yaml
# voxel definition type ("voxel" for index arrays)
"mesh_type": "voxel"

# definition of the voxel structure
"data_voxelize":
    # array with the number of voxels (x, y, and z directions)
    "n": [4, 4, 3]
    
    # array with the voxel dimensions (x, y, and z directions)
    "d": [10.0e-3, 10.0e-3, 10.0e-3]
    
    # array with the coordinates of the voxel structure center (x, y, and z directions)
    "c": [0.0, 0.0, 0.0]
    
    # definition of the voxel indices of the different domains
    #   - dict of arrays with the domain name and the voxel indices
    #   - required information, the dict cannot be empty
    "domain_def":
        "dom_src": [1, 2]
        "dom_cond": [5, 6, 9, 10]
        "dom_sink": [13, 14]
        "dom_mag": [36, 37, 38, 39, 40, 41, 42, 43]
        
# resampling of the voxel structure
#   - array with resampling factors (x, y, and z directions)
#   - the array [1, 1, 1] means that no resampling is performed
#   - the array [2, 2, 2] means that the voxel are divided in two for all directions
"resampling_factor": [2, 2, 1]

# pledge the existence or absence of connections between domains
#   - dict of dicts with the connection name and the connection definition
#   - optional feature, the dict can be empty without having an impact on the results
#   - connection definition
#       - domain_list: list of domains where the connections are checks
#       - connected: boolean specified if the listed domains should be connected or not
"domain_connection":
    "connected": {"domain_list": ["dom_src", "dom_cond", "dom_sink"], "connected": true}
    "insulated_1": {"domain_list": ["dom_src", "dom_mag"], "connected": false}
    "insulated_2": {"domain_list": ["dom_cond", "dom_mag"], "connected": false}
    "insulated_3": {"domain_list": ["dom_sink", "dom_mag"], "connected": false}
```

### Definition from PNG Files

```yaml
# voxel definition type ("png" for PNG files)
"mesh_type": "png"

# definition of the voxel structure
"data_voxelize":
    # array with the voxel dimensions (x, y, and z directions)
    "d": [10.0e-3, 10.0e-3, 10.0e-3]
    
    # array with the coordinates of the voxel structure center (x, y, and z directions)
    "c": [0.0, 0.0, 0.0]
    
    # size of the image in x-direction (number of voxels in the x-direction)
    "nx": 49
    
    # size of the image in y-direction (number of voxels in the y-direction)
    "ny": 49
    
    # definition of the mapping between the image color and the different domains
    #   - dict of arrays with the domain name and the specified color (RGBA format)
    #   - required information, the dict cannot be empty
    "domain_color":
        "dom_src": [255, 0, 0, 255]
        "dom_cond": [0, 0, 0, 255]
        "dom_sink": [0, 255, 0, 255]
        "dom_mag": [0, 0, 255, 255]
    
    # definition of the layer stack (voxels in the z-direction)
    #   - list of dicts with the definition of the layers
    #   - required information, the list cannot be empty
    #   - layer definition
    #       - n_layer: number of voxels in the z-direction for the layer
    #       - filename: name of the PNG file defining the layer
    "layer_stack":
        - {"n_layer": 1, "filename": "png/layer_bottom.png"}
        - {"n_layer": 8, "filename": "png/layer_mid.png"}
        - {"n_layer": 1, "filename": "png/layer_top.png"}
        
# resampling of the voxel structure
#   - array with resampling factors (x, y, and z directions)
#   - the array [1, 1, 1] means that no resampling is performed
#   - the array [2, 2, 2] means that the voxel are divided in two for all directions
"resampling_factor": [2, 2, 1]

# pledge the existence or absence of connections between domains
#   - dict of dicts with the connection name and the connection definition
#   - optional feature, the dict can be empty without having an impact on the results
#   - connection definition
#       - domain_list: list of domains where the connections are checks
#       - connected: boolean specified if the listed domains should be connected or not
"domain_connection":
    "connected": {"domain_list": ["dom_src", "dom_cond", "dom_sink"], "connected": true}
    "insulated_1": {"domain_list": ["dom_src", "dom_mag"], "connected": false}
    "insulated_2": {"domain_list": ["dom_cond", "dom_mag"], "connected": false}
    "insulated_3": {"domain_list": ["dom_sink", "dom_mag"], "connected": false}
```

### Definition from STL Files

```yaml
# voxel definition type ("stl" for STL files)
"mesh_type": "stl"

# definition of the voxel structure
"data_voxelize":
    # define the number of voxels
    #   - sampling: sampling type ("number" for defining the voxel numbers)
    #   - n: array with the number of voxels (x, y, and z directions)
    #   - d: null (not used)
    "sampling": "number"
    "n": [4, 4, 3]
    "d": null

    # define the voxel dimensions
    #   - sampling: sampling type ("dimension" for defining the voxel dimensions)
    #   - d: array with the voxel dimensions (x, y, and z directions)
    #   - n: null (not used)
    "sampling": "dimension"
    "d": [10.0e-3, 10.0e-3, 10.0e-3]
    "n": null

    # array with the coordinates of the voxel structure center (x, y, and z directions)
    "c": [0.0, 0.0, 0.0]
    # alternatively, the coordinates can be set to null and the STL coordinate are kept
    "c": null
    
    # array with the lower corner coordinates of the voxel structure (x, y, and z directions)
    "pts_min": [-20e-3, -20e-3, -20e-3]
    # alternatively, the coordinates can be set to null and the STL lower corner coordinate are kept
    "pts_min": null

    # array with the upper corner coordinates of the voxel structure (x, y, and z directions)
    "pts_max": [+20e-3, +20e-3, +20e-3]
    # alternatively, the coordinates can be set to null and the STL upper corner coordinate are kept
    "pts_max": null
    
    # definition of the STL files of the different domains
    #   - dict of strings with the domain name and the STL files
    #   - required information, the dict cannot be empty
    "domain_stl":
        "dom_src": "stl/dom_src.stl"
        "dom_cond": "stl/dom_cond.stl"
        "dom_sink": "stl/dom_sink.stl"
        "dom_mag": "stl/dom_mag.stl"
    
    # definition of the conflict resolution between domains
    #   - during the voxelization, the same voxel can be assigned to several domains
    #   - the shared voxels are located at the boundaries between domain
    #   - the shared voxels are conflicts and should be assigned to a single domain
    #   - list of dicts with the conflict resolution rules
    #   - optional feature, the list can be empty if no conflict resolution is required
    #   - conflict definition
    #       - domain_resolve: domain name where the shared voxels should be removed
    #       - domain_keep: domain name where the shared voxels should be kept
    "domain_conflict":
        - {"domain_resolve": "dom_cond", "domain_keep": "dom_src"}
        - {"domain_resolve": "dom_cond", "domain_keep": "dom_sink"}
        
# resampling of the voxel structure
#   - array with resampling factors (x, y, and z directions)
#   - the array [1, 1, 1] means that no resampling is performed
#   - the array [2, 2, 2] means that the voxel are divided in two for all directions
"resampling_factor": [2, 2, 1]

# pledge the existence or absence of connections between domains
#   - dict of dicts with the connection name and the connection definition
#   - optional feature, the dict can be empty without having an impact on the results
#   - connection definition
#       - domain_list: list of domains where the connections are checks
#       - connected: boolean specified if the listed domains should be connected or not
"domain_connection":
    "connected": {"domain_list": ["dom_src", "dom_cond", "dom_sink"], "connected": true}
    "insulated_1": {"domain_list": ["dom_src", "dom_mag"], "connected": false}
    "insulated_2": {"domain_list": ["dom_cond", "dom_mag"], "connected": false}
    "insulated_3": {"domain_list": ["dom_sink", "dom_mag"], "connected": false}
```

## Problem File Format

The `file_problem` file format is used by the solver.
This file contains the definition of the magnetic problem to be solved.

```yaml
 # operating frequency for the problem (DC or AC)
"freq": 1.0e+3

# material definition
#   - dict of dicts with the material name and the material definition
#   - required information, the dict cannot be empty
#   - magnetic material definition
#       - domain_list: list of domains with the specified material
#       - material_type: material type ("magnetic" for magnetic materials)
#       - chi_re: material real susceptibility (should be positive)
#       - chi_im: material imaginary susceptibility (should be positive)
#   - electric material definition
#       - domain_list: list of domains with the specified material
#       - material_type: material type ("electric" for electric materials)
#       - rho: material resistivity (should be positive)
"material_def":
    "mat_magnetic": {"domain_list": ["dom_src", "dom_cond", "dom_sink"], "material_type": "electric", "rho": 1.0e-8}
    "mat_electric": {"domain_list": ["dom_mag"], "material_type": "magnetic", "chi_re": 100.0, "chi_im": 10.0}

# source definition
#   - dict of dicts with the source name and the source definition
#   - required information, the dict cannot be empty
#   - sources can only be defined on electric material domains
#   - voltage source definition
#       - domain_list: list of domains with the specified source
#       - source_type: source type ("current" for current source)
#       - I_re: current source value (real part)
#       - I_im: current source value (imaginary part)
#       - Y_re: current internal admittance (real part)
#       - Y_im: current internal admittance (imaginary part)
#   - voltage source definition
#       - domain_list: list of domains with the specified source
#       - source_type: source type ("voltage" for voltage source)
#       - V_re: voltage source value (real part)
#       - V_im: voltage source value (imaginary part)
#       - Z_re: voltage internal impedance (real part)
#       - Z_im: voltage internal impedance (imaginary part)
"source_def":
    "src": {"domain_list": ["dom_src"], "source_type": "current", "I_re": 1.0, "I_im": 0.0, "Y_re": 0.5, "Y_im": 0.0}
    "sink": {"domain_list": ["dom_sink"], "source_type": "voltage", "V_re": 0.0, "V_im": 0.0, "Z_re": 2.0, "Z_im": 0.0}
```

## Point File Format

The `file_point` file format is used by the viewer and plotter.
This file contains the definition of the points used for magnetic field evaluation.

```yaml
# 2D array containing the points used for magnetic field evaluation
#   - the number of points (n_pts) can be zero.
#   - the array has the following size: (n_pts, 3)
[
    [-1.0, +1.0, +1.0],
    [+1.0, -1.0, +1.0],
    [+1.0, +1.0, -1.0],
]
```

## Other File Formats

* The `file_tolerance` format is documented in `examples/run_config.py`.
* The `file_viewer` format is documented in `examples/run_config.py`.
* The `file_plotter` format is documented in `examples/run_config.py`.
* The configuration file format is documented in `PyPEEC/pypeec.yaml`.