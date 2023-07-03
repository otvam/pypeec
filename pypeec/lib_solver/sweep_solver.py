"""
Module for running the sweeps with interdependencies.
Interdependency means that the result of a sweep can be used as the input for another one.

Build a tree representing the interdependencies between the sweeps.
Check that the interdependencies are not impossible (no cyclical dependencies).
Run the sweeps in the correct order and return the results.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import joblib
from pypeec import config
from pypeec.error import RunError

# get config
SWEEP_POOL = config.SWEEP_POOL


def _get_tree_tag(sweep_config, tag):
    """
    Find the run configurations for a defined init tag.
    """

    sweep_list = []
    for tag_run, tag_init in sweep_config.items():
        if tag_init == tag:
            sweep_list.append(tag_run)

    return sweep_list


def _get_tree_create(sweep_config):
    """
    Represent the sweep interdependencies with a tree.
    The root of the tree is the starting point for the computing the sweeps.
    """

    # dict for storing the tree
    sweep_tree = {}

    # add the dependencies between the sweeps
    for tag_tmp in sweep_config.keys():
        sweep_tree[tag_tmp] = _get_tree_tag(sweep_config, tag_tmp)

    # the root node is linking the sweep without dependencies
    sweep_tree[None] = _get_tree_tag(sweep_config, None)

    return sweep_tree


def _get_tree_check(sweep_tree, tag_init, init_list):
    """
    Check that the dependencies between the sweeps are solvable.
    Run through the tree from the root and gather the nodes.
    """

    # find the sweeps to be computed
    tag_sub = sweep_tree[tag_init]

    # add the design to the computed design
    init_list += tag_sub

    # recursive call for the dependent sweeps
    for tag_tmp in tag_sub:
        init_list = _get_tree_check(sweep_tree, tag_tmp, init_list)

    return init_list


def _get_tree_compute(sweep_tree, sweep_param, fct_compute, tag_init, output, init):
    """
    Compute the sweeps with the dependencies.
    This is done by walking through the graph from the root.
    """

    # find the sweeps to be computed
    tag_sub = sweep_tree[tag_init]

    # find the correct dependency for the sweeps
    if tag_init is None:
        init_tmp = None
    else:
        init_tmp = init[tag_init]

    # get the input
    sweep_param_sub = [sweep_param[tag_tmp] for tag_tmp in tag_sub]

    # run the serial or parallel loop
    if SWEEP_POOL is None:
        for tag_tmp, sweep_param_tmp in zip(tag_sub, sweep_param_sub):
            (output_tmp, sol_tmp) = fct_compute(tag_tmp, sweep_param_tmp, init_tmp)
            output[tag_tmp] = output_tmp
            init[tag_tmp] = sol_tmp
    else:
        # run the parallel jobs
        pool_res = joblib.Parallel(n_jobs=SWEEP_POOL, backend="loky")(
            joblib.delayed(fct_compute)(
                tag_tmp, sweep_param_tmp, init_tmp
            )
            for tag_tmp, sweep_param_tmp in zip(tag_sub, sweep_param_sub)
        )

        # assemble the results
        for tag_tmp, pool_res_tmp in zip(tag_sub, pool_res):
            (output_tmp, sol_tmp) = pool_res_tmp
            output[tag_tmp] = output_tmp
            init[tag_tmp] = sol_tmp

    # recursive call for the dependent sweeps
    for tag_tmp in tag_sub:
        (output, init) = _get_tree_compute(sweep_tree, sweep_param, fct_compute, tag_tmp, output, init)

    return output, init


def get_run_sweep(sweep_config, sweep_param, fct_compute):
    """
    Build a tree representing the interdependencies between the sweeps.
    Check that the interdependencies are not impossible (no cyclical dependencies).
    Run the sweeps in the correct order and return the results.
    """

    # create a representing the interdependencies between the sweeps
    sweep_tree = _get_tree_create(sweep_config)

    # ensure that the interdependencies are solvable
    init_list = _get_tree_check(sweep_tree, None, [])
    if len(init_list) != len(sweep_config):
        raise RunError("invalid sweep: cannot solve the sweep dependencies")

    # init the dict for the output data
    output = {}

    # init the dict for the interdependent data
    init = {}

    # compute the sweep in the correct order (starting from the tree root)
    (output, init) = _get_tree_compute(sweep_tree, sweep_param, fct_compute, None, output, init)

    return output
