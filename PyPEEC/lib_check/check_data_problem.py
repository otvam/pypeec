"""
Module for checking the solver problem data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from PyPEEC.lib_check import check_data_base


def _check_material_def(material_def):
    """
    Check that the material definition is valid.
    """

    # check type
    check_data_base.check_dict(
        "material_def", material_def,
        key_list=None, can_be_empty=False, sub_type=dict,
    )

    # check value
    for material_def_tmp in material_def.values():
        # check type
        key_list = ["material_type", "domain_list"]
        check_data_base.check_dict(
            "material_def", material_def_tmp,
            key_list=key_list, can_be_empty=False, sub_type=None,
        )

        # extract the data
        material_type = material_def_tmp["material_type"]
        domain_list = material_def_tmp["domain_list"]

        # check data
        check_data_base.check_choice("material_type", material_type, ["electric", "magnetic"])
        check_data_base.check_list("domain_list", domain_list, can_be_empty=False, sub_type=str)

        # get the source value
        if material_type == "electric":
            key_list = ["rho"]
        elif material_type == "magnetic":
            key_list = ["chi_re", "chi_im"]
        else:
            raise ValueError("invalid material type")

        # check type
        check_data_base.check_dict(
            "material_def", material_def_tmp,
            key_list=key_list, can_be_empty=False, sub_type=None,
        )

        # check data
        for key_list_tmp in key_list:
            check_data_base.check_float(key_list_tmp, material_def_tmp[key_list_tmp], is_positive=False, can_be_zero=True)


def _check_source_def(source_def):
    """
    Check that the source definition is valid.
    """

    # check type
    check_data_base.check_dict(
        "source_def", source_def,
        key_list=None, can_be_empty=False, sub_type=dict,
    )

    # check value
    for tag, source_def_tmp in source_def.items():
        # check type
        key_list = ["source_type", "domain_list"]
        check_data_base.check_dict(
            "source_def", source_def_tmp,
            key_list=key_list, can_be_empty=False, sub_type=None,
        )

        # extract the data
        source_type = source_def_tmp["source_type"]
        domain_list = source_def_tmp["domain_list"]

        # check data
        check_data_base.check_choice("source_type", source_type, ["current", "voltage"])
        check_data_base.check_list("domain_list", domain_list, can_be_empty=False, sub_type=str)

        # get the source value
        if source_type == "current":
            key_list = ["I_re", "I_im", "Y_re", "Y_im"]
        elif source_type == "voltage":
            key_list = ["V_re", "V_im", "Z_re", "Z_im"]
        else:
            raise ValueError("invalid source type")

        # check type
        check_data_base.check_dict(
            "source_type", source_def_tmp,
            key_list=key_list, can_be_empty=False, sub_type=None,
        )

        # check data
        for key_list_tmp in key_list:
            check_data_base.check_float(key_list_tmp, source_def_tmp[key_list_tmp], is_positive=False, can_be_zero=True)


def check_data_problem(data_problem):
    """
    Check the solver problem data:
        - frequency
        - material definition
        - source definition
    """

    # check type
    key_list = [
        "freq",
        "material_def",
        "source_def",
    ]
    check_data_base.check_dict(
        "data_problem", data_problem,
        key_list=key_list, can_be_empty=False, sub_type=None,
    )

    # extract field
    freq = data_problem["freq"]
    material_def = data_problem["material_def"]
    source_def = data_problem["source_def"]

    # check data
    check_data_base.check_float("freq", freq, is_positive=True, can_be_zero=True)

    # check material and source
    _check_material_def(material_def)
    _check_source_def(source_def)
