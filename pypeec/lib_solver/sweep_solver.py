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
from pypeec import log


def _get_tree_tag(sweep_config, tag):
    """
    Find the run configurations for a defined init tag.
    """

    tag_sub = []
    for tag_run, tag_init in sweep_config.items():
        if tag_init == tag:
            tag_sub.append(tag_run)

    return tag_sub


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


def _get_parallel_loop(sweep_pool, fct_compute, arg_list):
    """
    Run a loop (serial or parallel).
    """

    if sweep_pool is None:
        out_list = []
        for arg in arg_list:
            out = fct_compute(*arg)
            out_list.append(out)
    else:
        # get the log global parameters
        (global_timestamp, global_level) = log.get_global()

        # wrap the compute function for setting globals
        def fct_joblib(*args):
            log.set_global(global_timestamp, global_level)
            out = fct_compute(*args)
            return out

        # run the parallel loop
        out_list = joblib.Parallel(n_jobs=sweep_pool, backend="loky")(
            joblib.delayed(fct_joblib)(*arg) for arg in arg_list
        )

    return out_list


def _get_tree_compute(sweep_pool, sweep_tree, sweep_param, fct_compute, tag_init, output, init):
    """
    Compute the sweeps with the dependencies.
    This is done by walking through the graph from the root.
    """

    # find the sweeps to be computed
    tag_sub = sweep_tree[tag_init]

    # find the dependency for the sweeps
    if tag_init is None:
        init_tmp = None
    else:
        init_tmp = init[tag_init]

    # get the input
    data_sub = [sweep_param[tag_tmp] for tag_tmp in tag_sub]
    init_sub = [init_tmp]*len(tag_sub)

    # return if there is nothing to compute
    if not tag_sub:
        return output, init

    # run the serial or parallel loop
    arg_list = zip(tag_sub, data_sub, init_sub)
    out_list = _get_parallel_loop(sweep_pool, fct_compute, arg_list)

    # assemble the results
    for tag_tmp, out_tmp in zip(tag_sub, out_list):
        (output_tmp, sol_tmp) = out_tmp
        output[tag_tmp] = output_tmp
        init[tag_tmp] = sol_tmp

    # recursive call for the dependent sweeps
    for tag_tmp in tag_sub:
        (output, init) = _get_tree_compute(sweep_pool, sweep_tree, sweep_param, fct_compute, tag_tmp, output, init)

    return output, init


def get_run_sweep(sweep_pool, sweep_config, sweep_param, fct_compute):
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
        raise RuntimeError("invalid sweep: cannot solve the sweep dependencies")

    # init the dict for the output data
    output = {}

    # init the dict for the interdependent data
    init = {}

    # compute the sweep in the correct order (starting from the tree root)
    (output, init) = _get_tree_compute(sweep_pool, sweep_tree, sweep_param, fct_compute, None, output, init)

    return output
