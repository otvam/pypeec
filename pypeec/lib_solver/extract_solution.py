"""
Different functions for extracting the fields and terminal currents and voltages from the solution vector.

Extract the different fields.
Extract the losses and energy.
Extract the integral quantities.
Extract the source terminal currents and voltages.
Compute the magnetic field for the point cloud.

Warning
-------
    - The magnetic field computation is done with lumped variables.
    - Therefore, the computation is only accurate far away from the voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np
import numpy.linalg as lna
import scipy.constants as cst

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _get_biot_savart(pts, pts_net, J_src, vol):
    """
    Compute the magnetic field at a specified point.
    The field is created by many currents.
    """

    # get the distance between the points and the voxels
    vec = pts-pts_net

    # get the norm of the distance
    nrm = lna.norm(vec, axis=1, keepdims=True)

    # compute the Biot-Savart contributions
    H_all = (vol/(4*np.pi))*(np.cross(J_src, vec, axis=1)/(nrm**3))

    # sum the contributions
    H_pts = np.sum(H_all, axis=0)

    return H_pts


def _get_magnetic_charge(pts, pts_src, Q_src, vol):
    """
    Compute the magnetic field at a specified point.
    The field is created by many magnetic charge.
    """

    # get the distance between the points and the voxels
    vec = pts_src-pts

    # get the norm of the distance
    nrm = lna.norm(vec, axis=1, keepdims=True)

    # transform the charge into a vector
    Q_src = np.tile(Q_src, (3, 1)).transpose()

    # compute the Biot-Savart contributions
    H_all = (vol/(4*np.pi*cst.mu_0))*((Q_src*vec)/(nrm**3))

    # sum the contributions
    H_pts = np.sum(H_all, axis=0)

    return H_pts


def get_magnetic_field(d, J_vc, Q_vm, pts_net_c, pts_net_m, pts_cloud):
    """
    Compute the magnetic field for the provided points.
    The Biot-Savart law is used for the electric material contribution.
    The magnetic charge is used for the magnetic material contribution.
    """

    # extract the voxel volume
    vol = np.prod(d)

    # for each provided point, compute the magnetic field
    H_pts = np.zeros((len(pts_cloud), 3), dtype=np.complex_)
    for i, pts_tmp in enumerate(pts_cloud):
        H_c = _get_biot_savart(pts_tmp, pts_net_c, J_vc, vol)
        H_m = _get_magnetic_charge(pts_tmp, pts_net_m, Q_vm, vol)
        H_pts[i, :] = H_c+H_m

    return H_pts


def get_sol_extract(sol, sol_idx):
    """
    Extract the different variables from the solution vector.
    """

    I_fc = sol[sol_idx["I_fc"]]
    V_vc = sol[sol_idx["V_vc"]]
    I_fm = sol[sol_idx["I_fm"]]
    V_vm = sol[sol_idx["V_vm"]]
    I_src = sol[sol_idx["I_src"]]

    return I_fc, V_vc, I_fm, V_vm, I_src


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
    idx_fx = np.in1d(idx_f, np.arange(0*nv, 1*nv, dtype=np.int_))
    idx_fy = np.in1d(idx_f, np.arange(1*nv, 2*nv, dtype=np.int_))
    idx_fz = np.in1d(idx_f, np.arange(2*nv, 3*nv, dtype=np.int_))

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


def get_integral(P_fc, P_fm, W_fc, W_fm, S_total):
    """
    Sum the loss/energy in order to obtain global quantities.
    """

    # compute the integral quantities
    P_electric = np.sum(P_fc)
    P_magnetic = np.sum(P_fm)
    W_electric = np.sum(W_fc)
    W_magnetic = np.sum(W_fm)
    P_total = P_electric+P_magnetic
    W_total = W_electric+W_magnetic

    # assign the integral quantities
    integral = {
        "P_electric": P_electric, "P_magnetic": P_magnetic,
        "W_electric": W_electric, "W_magnetic": W_magnetic,
        "P_total": P_total, "W_total": W_total, "S_total": S_total,
    }

    # display
    LOGGER.debug("integral")
    with LOGGER.BlockIndent():
        LOGGER.debug("S_total_real = %.2e VA" % S_total.real)
        LOGGER.debug("S_total_imag = %.2ej VA" % S_total.imag)
        LOGGER.debug("P_electric = %.2e W" % P_electric)
        LOGGER.debug("P_magnetic = %.2e W" % P_magnetic)
        LOGGER.debug("W_electric = %.2e J" % W_electric)
        LOGGER.debug("W_magnetic = %.2e J" % W_magnetic)
        LOGGER.debug("P_total = %.2e W" % P_total)
        LOGGER.debug("W_total = %.2e J" % W_total)

    return integral


def get_material(material_pos, A_net_c, A_net_m, P_fc, P_fm):
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
    for tag, material_pos_tmp in material_pos.items():
        # extract the data
        idx_vc = material_pos_tmp["idx_vc"]
        idx_vm = material_pos_tmp["idx_vm"]

        # get the domain losses
        P_vc_tmp = np.sum(P_vc[idx_vc])
        P_vm_tmp = np.sum(P_vm[idx_vm])
        P_tmp = P_vc_tmp+P_vm_tmp

        # assign the losses
        material[tag] = {"P_electric": P_vc_tmp, "P_magnetic": P_vm_tmp, "P_total": P_tmp}

        # display
        LOGGER.debug("domain: %s" % tag)
        with LOGGER.BlockIndent():
            LOGGER.debug("P_electric = %.2e W" % P_vc_tmp)
            LOGGER.debug("P_magnetic = %.2e W" % P_vm_tmp)
            LOGGER.debug("P_total = %.2e W" % P_tmp)

    return material


def get_source(freq, source_all, I_src, V_vc):
    """
    Parse the terminal voltages and currents for the sources.
    The sources have internal resistances/admittances.
    Therefore, the extracted value can differ from the prescribed value.
    The results are assigned to a dict with the voltage, current, and power values.
    """

    # init source dict
    source = {}

    # total complex power
    S_total = 0.0

    # get the factor for getting the power time-averaged values
    if freq == 0:
        fact = 1.0
    else:
        fact = 0.5

    # parse the source terminals
    for tag, source_all_tmp in source_all.items():
        # extract the data
        idx = source_all_tmp["idx"]
        idx_vc = source_all_tmp["idx_vc"]
        idx_src = source_all_tmp["idx_src"]
        source_type = source_all_tmp["source_type"]
        var_type = source_all_tmp["var_type"]
        value = source_all_tmp["value"]
        element = source_all_tmp["element"]

        # get the distributed source
        if len(idx) == 0:
            V_tmp = np.complex_(0)
            I_tmp = np.complex_(0)
            value = np.complex_(0)
            element = np.complex_(0)
        else:
            V_tmp = np.complex_(V_vc[idx_vc])
            I_tmp = np.complex_(I_src[idx_src])

        # get the drop across the source impedance
        if source_type == "current":
            drop_tmp = np.sum(V_tmp*element)
            src_tmp = np.sum(value)
        elif source_type == "voltage":
            drop_tmp = np.mean(I_tmp*element)
            src_tmp = np.mean(value)
        else:
            raise ValueError("invalid source type")

        # compute the lumped quantities
        S_tmp = np.sum(fact*V_tmp*np.conj(I_tmp))
        V_tmp = np.mean(V_tmp)
        I_tmp = np.sum(I_tmp)

        # assign the current and voltage
        source[tag] = {
            "V": V_tmp, "I": I_tmp, "S": S_tmp,
            "source_type": source_type, "var_type": var_type,
            "src": src_tmp, "drop": drop_tmp,
        }

        # add the power
        S_total += S_tmp

        # display
        LOGGER.debug("terminal: %s" % tag)
        with LOGGER.BlockIndent():
            # source type
            LOGGER.debug("type = %s / %s" % (source_type, var_type))

            # source value
            if source_type == "current":
                LOGGER.debug("I_src = %+.2e + %+.2ej V" % (src_tmp.real, src_tmp.imag))
                LOGGER.debug("I_drop = %+.2e + %+.2ej V" % (drop_tmp.real, drop_tmp.imag))
            elif source_type == "voltage":
                LOGGER.debug("V_src = %+.2e + %+.2ej V" % (src_tmp.real, src_tmp.imag))
                LOGGER.debug("V_drop = %+.2e + %+.2ej V" % (drop_tmp.real, drop_tmp.imag))
            else:
                raise ValueError("invalid source type")

            # terminal value
            LOGGER.debug("V = %+.2e + %+.2ej V" % (V_tmp.real, V_tmp.imag))
            LOGGER.debug("I = %+.2e + %+.2ej A" % (I_tmp.real, I_tmp.imag))
            LOGGER.debug("S = %+.2e + %+.2ej VA" % (S_tmp.real, S_tmp.imag))

    return source, S_total
