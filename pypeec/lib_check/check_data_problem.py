"""
Module for checking the solver problem data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_utils import datachecker


def _check_material_def(material_def):
    """
    Check that the material definition is valid.
    """

    # check type
    datachecker.check_dict("material_def", material_def, can_be_empty=False, sub_type=dict)

    # check value
    for dat_tmp in material_def.values():
        # check type
        key_list = ["material_type", "domain_list"]
        datachecker.check_dict("material_def", dat_tmp, key_list=key_list)

        # extract the data
        var_type = dat_tmp["var_type"]
        material_type = dat_tmp["material_type"]
        domain_list = dat_tmp["domain_list"]

        # check data
        datachecker.check_choice("var_type", var_type, ["lumped", "distributed"])
        datachecker.check_choice("material_type", material_type, ["electric", "magnetic"])
        datachecker.check_list("domain_list", domain_list, can_be_empty=False, sub_type=str)

        # get the source value
        if material_type == "electric":
            key_list = ["rho"]
        elif material_type == "magnetic":
            key_list = ["chi_re", "chi_im"]
        else:
            raise ValueError("invalid material type")

        # check type
        datachecker.check_dict("material_def", dat_tmp, key_list=key_list)

        # check data
        for tag in key_list:
            if var_type == "lumped":
                datachecker.check_float(tag, dat_tmp[tag], is_positive=True)
            elif var_type == "distributed":
                datachecker.check_float_array(tag, dat_tmp[tag], is_positive=True, can_be_empty=False)
            else:
                raise ValueError("invalid material type")


def _check_source_def(source_def):
    """
    Check that the source definition is valid.
    """

    # check type
    datachecker.check_dict("source_def", source_def, can_be_empty=False, sub_type=dict)

    # check value
    for dat_tmp in source_def.values():
        # check type
        key_list = ["source_type", "domain_list"]
        datachecker.check_dict("source_def", dat_tmp, key_list=key_list)

        # extract the data
        var_type = dat_tmp["var_type"]
        source_type = dat_tmp["source_type"]
        domain_list = dat_tmp["domain_list"]

        # check data
        datachecker.check_choice("var_type", var_type, ["lumped", "distributed"])
        datachecker.check_choice("source_type", source_type, ["current", "voltage"])
        datachecker.check_list("domain_list", domain_list, can_be_empty=False, sub_type=str)

        # get the source value
        if source_type == "current":
            key_list = ["I_re", "I_im", "Y_re", "Y_im"]
        elif source_type == "voltage":
            key_list = ["V_re", "V_im", "Z_re", "Z_im"]
        else:
            raise ValueError("invalid source type")

        # check type
        datachecker.check_dict("source_type", dat_tmp, key_list=key_list)

        # check data
        for tag in key_list:
            if var_type == "lumped":
                datachecker.check_float(tag, dat_tmp[tag])
            elif var_type == "distributed":
                datachecker.check_float_array(tag, dat_tmp[tag], can_be_empty=False)
            else:
                raise ValueError("invalid material type")


def check_data_problem(data_problem):
    """
    Check the solver problem data:
        - frequency
        - material definition
        - source definition
    """

    # check type
    key_list = ["freq", "material_def", "source_def"]
    datachecker.check_dict("data_problem", data_problem, key_list=key_list)

    # extract field
    freq = data_problem["freq"]
    material_def = data_problem["material_def"]
    source_def = data_problem["source_def"]

    # check data
    datachecker.check_float("freq", freq, is_positive=True)

    # check material and source
    _check_material_def(material_def)
    _check_source_def(source_def)
