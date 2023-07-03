"""
Module for checking the solver problem data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def _check_field(val_dict, var_type, key_list):
    """
    Check a value dict.
    """

    # check type
    datachecker.check_dict("val", val_dict, key_list=key_list)

    # check data
    for tag, val in val_dict.items():
        if var_type == "lumped":
            datachecker.check_float(tag, val)
        elif var_type == "distributed":
            datachecker.check_float_array(tag, val)
        else:
            raise ValueError("invalid material type")


def _check_material_def(material_def):
    """
    Check that the material definition is valid.
    """

    # check type
    datachecker.check_dict("material_def", material_def, can_be_empty=False)

    # check value
    for material_def_tmp in material_def.values():
        # check type
        key_list = ["material_type", "var_type", "domain_list"]
        datachecker.check_dict("material_def", material_def_tmp, key_list=key_list)

        # extract the data
        var_type = material_def_tmp["var_type"]
        material_type = material_def_tmp["material_type"]
        domain_list = material_def_tmp["domain_list"]

        # check data
        datachecker.check_choice("var_type", var_type, ["lumped", "distributed"])
        datachecker.check_choice("material_type", material_type, ["electric", "magnetic"])
        datachecker.check_list("domain_list", domain_list, can_be_empty=False, sub_type=str)


def _check_source_def(source_def):
    """
    Check that the source definition is valid.
    """

    # check type
    datachecker.check_dict("source_def", source_def, can_be_empty=False)

    # check value
    for source_def_tmp in source_def.values():
        # check type
        key_list = ["source_type", "var_type", "domain_list"]
        datachecker.check_dict("source_def", source_def_tmp, key_list=key_list)

        # extract the data
        var_type = source_def_tmp["var_type"]
        source_type = source_def_tmp["source_type"]
        domain_list = source_def_tmp["domain_list"]

        # check data
        datachecker.check_choice("var_type", var_type, ["lumped", "distributed"])
        datachecker.check_choice("source_type", source_type, ["current", "voltage"])
        datachecker.check_list("domain_list", domain_list, can_be_empty=False, sub_type=str)


def _check_sweep_param(sweep_param, material_def, source_def):
    """
    Check that the excitation definition (materials and sources) is valid.
    """

    # check type
    key_list = ["freq", "material_val", "source_val"]
    datachecker.check_dict("sweep_param", sweep_param, key_list=key_list)

    # extract field
    freq = sweep_param["freq"]
    material_val = sweep_param["material_val"]
    source_val = sweep_param["source_val"]

    # check data
    datachecker.check_float("freq", freq, is_positive=True, can_be_zero=True)

    # check type
    datachecker.check_dict("material_val", material_val, can_be_empty=False)
    datachecker.check_dict("source_val", source_val, can_be_empty=False)

    # check value
    for tag, material_val_tmp in material_val.items():
        # extract the data
        datachecker.check_choice("tag", tag, material_def)
        var_type = material_def[tag]["var_type"]
        material_type = material_def[tag]["material_type"]

        # get the source value
        if material_type == "electric":
            key_list = ["rho_re", "rho_im"]
        elif material_type == "magnetic":
            key_list = ["chi_re", "chi_im"]
        else:
            raise ValueError("invalid material type")

        # check type
        _check_field(material_val_tmp, var_type, key_list)

    # check value
    for tag, source_val_tmp in source_val.items():
        # extract the data
        datachecker.check_choice("tag", tag, source_def)
        var_type = source_def[tag]["var_type"]
        source_type = source_def[tag]["source_type"]

        # get the source value
        # get the source value
        if source_type == "current":
            key_list = ["I_re", "I_im", "Y_re", "Y_im"]
        elif source_type == "voltage":
            key_list = ["V_re", "V_im", "Z_re", "Z_im"]
        else:
            raise ValueError("invalid source type")

        # check type
        _check_field(source_val_tmp, var_type, key_list)


def check_data_problem(data_problem):
    """
    Check the solver problem data:
        - frequency
        - material definition
        - source definition
    """

    # check type
    key_list = ["material_def", "source_def", "sweep_config", "sweep_param"]
    datachecker.check_dict("data_problem", data_problem, key_list=key_list)

    # extract field
    material_def = data_problem["material_def"]
    source_def = data_problem["source_def"]
    sweep_config = data_problem["sweep_config"]
    sweep_param = data_problem["sweep_param"]

    # check material and source
    _check_material_def(material_def)
    _check_source_def(source_def)

    # check excitation values
    datachecker.check_dict("sweep_param", sweep_param, can_be_empty=False)
    for sweep_param_tmp in sweep_param.values():
        _check_sweep_param(sweep_param_tmp, material_def, source_def)

    # get sweep names
    sweep_list = sweep_param.keys()

    # check the sweep configuration
    datachecker.check_dict("sweep_config", sweep_config, can_be_empty=False)
    for tag_run, tag_init in sweep_config.items():
        datachecker.check_choice("tag_run", tag_run, sweep_list, can_be_none=False)
        datachecker.check_choice("tag_init", tag_init, sweep_list, can_be_none=True)
