"""
Module for running the sweeps with interdependencies.
Interdependency means that the result of a sweep can be used as the input for another one.

Build a tree representing the interdependencies between the sweeps.
Check that the interdependencies are not impossible (no cyclical dependencies).
Run the sweeps in the correct order and return the results.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import joblib
import numpy as np
import scipy.sparse.csgraph as csg
from pypeec.error import RunError
from pypeec import config

# get config
SWEEP_POOL = config.SWEEP_POOL


def _get_tree_create(config):
    """
    Represent the sweep interdependencies with a tree.
    The root of the tree is the starting point for the computing the sweeps.
    """

    # get the sweep names and dependencies
    tag_run = np.array(list(config.keys()), dtype=object)
    tag_init = np.array(list(config.values()), dtype=object)

    # dict for storing the tree
    tree = {}

    # the root node is linking the sweep without dependencies
    tree[None] = tag_run[tag_init == None]

    # add the dependencies between the sweeps
    for tag_tmp in tag_run:
        tree[tag_tmp] = tag_run[tag_init == tag_tmp]

    return tree


def _get_tree_check(tree):
    """
    Check that the dependencies between the sweeps are solvable.
    This is done by checking that the dependency tree has no cycles.
    """

    # get the name of the nodes
    node = np.array(list(tree.keys()), dtype=object)

    # matrix describing the tree
    mat = []
    for tag_tmp in node:
        mat_tmp = np.in1d(node, tree[tag_tmp])
        mat.append(mat_tmp.astype(int))

    # construct the tree
    tree = csg.csgraph_from_dense(mat)

    # span a tree from the root node
    tree_span = csg.breadth_first_tree(tree, 0)

    # check the difference between the tree and the tree
    diff = tree != tree_span

    # if the tree and the tree are not identical, the tree has cycles
    if diff.nnz != 0:
        raise RunError("invalid sweep: cannot solve the sweep dependencies")


def _get_tree_compute(output, init, tree, param, fct_compute, tag_init):
    """
    Compute the sweeps with the dependencies.
    This is done by walking through the graph from the root.
    """

    # find the sweeps to be computed
    tag_sub = tree[tag_init]

    # find the correct dependency for the sweeps
    if tag_init is None:
        init_tmp = None
    else:
        init_tmp = init[tag_init]

    # get the input
    param_sub = [param[tag_tmp] for tag_tmp in tag_sub]

    # run the serial or parallel loop
    if SWEEP_POOL is None:
        for tag_tmp, param_tmp in zip(tag_sub, param_sub):
            (output_tmp, sol_tmp) = fct_compute(tag_tmp, param_tmp, init_tmp)
            output[tag_tmp] = output_tmp
            init[tag_tmp] = sol_tmp
    else:
        # run the parallel jobs
        pool_res = joblib.Parallel(n_jobs=SWEEP_POOL, backend="loky")(
            joblib.delayed(fct_compute)(
                tag_tmp, param_tmp, init_tmp
            )
            for tag_tmp, param_tmp in zip(tag_sub, param_sub)
        )

        # assemble the results
        for tag_tmp, pool_res_tmp in zip(tag_sub, pool_res):
            (output_tmp, sol_tmp) = pool_res_tmp
            output[tag_tmp] = output_tmp
            init[tag_tmp] = sol_tmp

    # recursive call for the dependent sweeps
    for tag_tmp in tag_sub:
        (output, init) = _get_tree_compute(output, init, tree, param, fct_compute, tag_tmp)

    return output, init


def get_run_sweep(config, param, fct_compute):
    """
    Build a tree representing the interdependencies between the sweeps.
    Check that the interdependencies are not impossible (no cyclical dependencies).
    Run the sweeps in the correct order and return the results.
    """

    # create a representing the interdependencies between the sweeps
    tree = _get_tree_create(config)

    # ensure that the interdependencies are solvable
    _get_tree_check(tree)

    # init the dict for the output data
    output = {}

    # init the dict for the interdependent data
    init = {}

    # compute the sweep in the correct order (starting from the tree root)
    (output, init) = _get_tree_compute(output, init, tree, param, fct_compute, None)

    return output
