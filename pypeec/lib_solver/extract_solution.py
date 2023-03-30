"""
Different functions for extracting the fields and terminal currents and voltages from the solution vector.

The voxel structure has the following size: (nx, ny, nz).
The problem contains n_vc non-empty electric voxels and n_vm non-empty magnetic voxels.
The problem contains n_fc internal electric faces and n_fm internal magnetic faces.
The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec.lib_utils import timelogger
from pypeec import config

# get a logger
LOGGER = timelogger.get_logger("SOLUTION")

# get config
NP_TYPES = config.NP_TYPES


def _get_sol_var(sol, idx, n_offset):
    """
    Extract a variable from the solution vector.
    """

    # size of the slice
    n_var = len(idx)

    # get the variable
    var = sol[n_offset:n_offset+n_var]

    # update the offset
    n_offset += n_var

    return var, n_offset


def get_sol_extract_field(sol, idx_f, idx_v, n_offset):
    """
    Extract the electric/magnetic variables from the solution vector.
    """

    (I_f, n_offset) = _get_sol_var(sol, idx_f, n_offset)
    (V_v, n_offset) = _get_sol_var(sol, idx_v, n_offset)

    return I_f, V_v, n_offset


def get_sol_extract_source(sol, idx_src_c, idx_src_v, n_offset):
    """
    Extract the electric/magnetic variables from the solution vector.
    """

    (I_src_c, n_offset) = _get_sol_var(sol, idx_src_c, n_offset)
    (I_src_v, n_offset) = _get_sol_var(sol, idx_src_v, n_offset)

    return I_src_c, I_src_v, n_offset


def get_vector_density(n, d, idx_f, A_net, var_f):
    """
    Project a face vector variable into a voxel vector variable.
    Scale the variable with respect to the face area (density).

    At the input, the array has the following size: 3*nx*ny*nx.
    At the output, the array has the following size: (nx*ny*nx, 3).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # extract the voxel data
    (dx, dy, dz) = d

    # get the direction of the faces (x, y, z)
    idx_fx = np.in1d(idx_f, np.arange(0*nv, 1*nv, dtype=NP_TYPES.INT))
    idx_fy = np.in1d(idx_f, np.arange(1*nv, 2*nv, dtype=NP_TYPES.INT))
    idx_fz = np.in1d(idx_f, np.arange(2*nv, 3*nv, dtype=NP_TYPES.INT))

    # project the faces into the voxels
    var_v_x = 0.5*np.abs(A_net[:, idx_fx])*var_f[idx_fx]
    var_v_y = 0.5*np.abs(A_net[:, idx_fy])*var_f[idx_fy]
    var_v_z = 0.5*np.abs(A_net[:, idx_fz])*var_f[idx_fz]

    # convert to density.
    var_v_x = var_v_x/(dy*dz)
    var_v_y = var_v_y/(dx*dz)
    var_v_z = var_v_z/(dx*dy)

    # assemble the variables
    var_v = np.stack((var_v_x, var_v_y, var_v_z), axis=1)

    return var_v


def get_scalar_density(d, A_net, var_f):
    """
    Project a face vector variable into a voxel scalar variable.
    Scale the variable with respect to the voxel volume (density).

    At the input, the array has the following size: 3*nx*ny*nx.
    At the output, the array has the following size: nx*ny*nx.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # convert face to voxel variable
    var_v = 0.5*np.abs(A_net)*var_f

    # convert to density.
    var_v = var_v/(dx*dy*dz)

    return var_v


def get_divergence_density(d, A_net, var_f):
    """
    Compute the divergence of a face vector with respect to the voxels.
    Scale the variable with respect to the voxel volume (density).

    At the input, the array has the following size: 3*nx*ny*nx.
    At the output, the array has the following size: nx*ny*nx.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # compute the divergence
    var_v = A_net*var_f

    # convert to density.
    var_v = var_v/(dx*dy*dz)

    return var_v


def get_losses(freq, I_fc, I_fm, R_c, R_m):
    """
    Get the losses for the electric and magnetic domains.
    """

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # get the factor for getting the loss time-averaged values
    if freq == 0:
        fact = 1.0
    else:
        fact = 0.5

    # get the magnetic losses linked with the electric domains
    P_fc = fact*np.conj(I_fc)*R_c*I_fc
    P_fc = np.real(P_fc)

    # get the magnetic losses linked with the magnetic domains
    P_fm = fact*np.conj(s*I_fm)*R_m*I_fm
    P_fm = np.real(P_fm)

    return P_fc, P_fm


def get_energy(freq, I_fc, I_fm, L_op_c, K_op_c):
    """
    Get the energy for the electric and magnetic domains.
    """

    # get the factor for getting the energy time-averaged values
    if freq == 0:
        fact = 0.5
    else:
        fact = 0.25

    # get the magnetic energy linked with the electric domains
    W_fc = fact*np.conj(I_fc)*L_op_c(I_fc)
    W_fc = np.real(W_fc)

    # get the magnetic energy linked with the magnetic domains
    W_fm = fact*np.conj(I_fc)*K_op_c(I_fm)
    W_fm = np.real(W_fm)

    return W_fc, W_fm


def get_integral(P_fc, P_fm, W_fc, W_fm):
    """
    Sum the loss/energy in order to obtain global quantities.
    """

    # compute the integral quantities
    P_electric = np.sum(P_fc)
    P_magnetic = np.sum(P_fm)
    W_electric = np.sum(W_fc)
    W_magnetic = np.sum(W_fm)
    P_tot = P_electric+P_magnetic
    W_tot = W_electric+W_magnetic

    # assign the integral quantities
    integral = {
        "P_electric": P_electric, "P_magnetic": P_magnetic, "P_tot": P_tot,
        "W_electric": W_electric, "W_magnetic": W_magnetic, "W_tot": W_tot,
    }

    # display
    LOGGER.debug("integral: P_electric = %.3e W" % P_electric)
    LOGGER.debug("integral: P_magnetic = %.3e W" % P_magnetic)
    LOGGER.debug("integral: W_electric = %.3e J" % W_electric)
    LOGGER.debug("integral: W_magnetic = %.3e J" % W_magnetic)
    LOGGER.debug("integral: P_tot = %.3e W" % P_tot)
    LOGGER.debug("integral: W_tot = %.3e J" % W_tot)

    return integral


def get_material(material_idx, idx_vc, idx_vm, A_net_c, A_net_m, P_fc, P_fm):
    """
    Parse the losses for the materials.
    The results are assigned to a dict with the magnetic and electric losses.
    """

    # init material dict
    material = {}

    # compute the losses of the voxels
    P_vc = 0.5*np.abs(A_net_c)*P_fc
    P_vm = 0.5*np.abs(A_net_m)*P_fm

    # parse the material domains
    for tag, dat_tmp in material_idx.items():
        # get the data
        material_type = dat_tmp["material_type"]
        idx = dat_tmp["idx"]

        # get the position of the domains
        idx_vc_tmp = np.in1d(idx_vc, idx)
        idx_vm_tmp = np.in1d(idx_vm, idx)

        # get the domain losses
        P_vc_tmp = NP_TYPES.FLOAT(np.sum(P_vc[idx_vc_tmp]))
        P_vm_tmp = NP_TYPES.FLOAT(np.sum(P_vm[idx_vm_tmp]))
        P_tmp = P_vc_tmp+P_vm_tmp

        # assign the losses
        material[tag] = {"P_electric": P_vc_tmp, "P_magnetic": P_vm_tmp, "P_tot": P_tmp, "material_type": material_type}

        # display
        LOGGER.debug("domain: %s : material_type = %s" % (tag, material_type))
        LOGGER.debug("domain: %s : P_electric = %.3e W" % (tag, P_vc_tmp))
        LOGGER.debug("domain: %s : P_magnetic = %.3e W" % (tag, P_vm_tmp))
        LOGGER.debug("domain: %s : P_tot = %.3e W" % (tag, P_tmp))

    return material


def get_source(freq, source_idx, idx_src_c, idx_src_v, idx_vc, V_vc, I_src_c, I_src_v):
    """
    Parse the terminal voltages and currents for the sources.
    The sources have internal resistances/admittances.
    Therefore, the extracted value can differ from the source value.
    The results are assigned to a dict with the voltage and current values.
    """

    # init source dict
    source = {}

    # get the factor for getting the power time-averaged values
    if freq == 0:
        fact = 1.0
    else:
        fact = 0.5

    # parse the source terminals
    for tag, dat_tmp in source_idx.items():
        # get the data
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]

        # get the position of the sources
        idx_vc_tmp = np.in1d(idx_vc, idx)
        idx_src_c_tmp = np.in1d(idx_src_c, idx)
        idx_src_v_tmp = np.in1d(idx_src_v, idx)

        # extract the terminal variables
        if len(idx) == 0:
            V_tmp = NP_TYPES.COMPLEX(0)
            I_tmp = NP_TYPES.COMPLEX(0)
        else:
            # voltage is the average between all the voxels composing the terminal
            V_tmp = NP_TYPES.COMPLEX(np.mean(V_vc[idx_vc_tmp]))

            # current is the sum between all the voxels composing the terminal
            if source_type == "current":
                I_tmp = NP_TYPES.COMPLEX(np.sum(I_src_c[idx_src_c_tmp]))
            elif source_type == "voltage":
                I_tmp = NP_TYPES.COMPLEX(np.sum(I_src_v[idx_src_v_tmp]))
            else:
                raise ValueError("invalid terminal type")

        # compute the apparent power
        S_tmp = fact*V_tmp*np.conj(I_tmp)

        # assign the current and voltage
        source[tag] = {"V": V_tmp, "I": I_tmp, "S": S_tmp, "source_type": source_type}

        # display
        LOGGER.debug("terminal: %s : source_type = %s" % (tag, source_type))
        LOGGER.debug("terminal: %s : V = %+.3e + %+.3ej V" % (tag, V_tmp.real, V_tmp.imag))
        LOGGER.debug("terminal: %s : I = %+.3e + %+.3ej A" % (tag, I_tmp.real, I_tmp.imag))
        LOGGER.debug("terminal: %s : S = %+.3e + %+.3ej VA" % (tag, S_tmp.real, S_tmp.imag))

    return source
