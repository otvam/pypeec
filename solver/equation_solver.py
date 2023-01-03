import scipy.sparse.linalg as sla
import scipy.linalg as lna


class IterCounter():
    def __init__(self):
        self.n_iter = 0

    def get_callback(self, res):
        self.n_iter += 1

    def get_n_iter(self):
        return self.n_iter


def get_solver(sys_op, pcd_op, rhs, solver_options):
    # get the solver options
    tol = solver_options["tol"]
    atol = solver_options["atol"]
    restart = solver_options["restart"]
    maxiter = solver_options["maxiter"]

    # object for counting the solver iterations (callback)
    obj = IterCounter()

    # define callback
    def fct(res_iter):
        obj.get_callback(res_iter)

    # call the solver
    (sol, flag) = sla.gmres(sys_op, rhs, tol=tol, atol=atol, restart=restart, maxiter=maxiter, M=pcd_op, callback=fct)

    # get the number of iterations
    n_iter = obj.get_n_iter()

    # compute the residuum
    res = sys_op(sol) - rhs
    res_abs = lna.norm(res)
    res_rel = lna.norm(res) / lna.norm(rhs)

    # check for convergence
    has_converged = flag==0

    # assign the results
    solver_status = {"n_iter": n_iter, "res_abs": res_abs, "res_rel": res_rel, "has_converged": has_converged}

    return sol, solver_status
