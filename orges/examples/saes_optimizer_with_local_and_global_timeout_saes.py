# -*- coding: utf-8 -*-
import inspect

from orges.invoker.pluggable import TimeoutInvocationPlugin
from orges.invoker.pluggable import PrintInvocationPlugin
from orges.main import optimize
from orges.optimizer.saes import SAESOptimizer
import orges.param as param
from orges.test.demo.algorithm.host.saes import f as saes


@param.int("mu", interval=(5, 10), display_name="μ")
@param.int("lambd", interval=(5, 10), display_name="λ")
@param.float("tau0", interval=(0, 1), step=0.5, display_name="τ0")
@param.float("tau1", interval=(0, 1), step=0.5, display_name="τ1")
def f(mu, lambd, tau0, tau1):
    args = dict()

    args["d"] = 2
    args["epsilon"] = 0.0001
    args["mu"] = mu
    args["lambd"] = lambd
    args["tau0"] = tau0
    args["tau1"] = tau1

    return saes(args)

F_PACKAGE = inspect.getmodulename(inspect.getabsfile(f))

if __name__ == '__main__':
    # Local timeout after 1 second
    plugins = [TimeoutInvocationPlugin(1), PrintInvocationPlugin()]

    # Global timeout after 5 seconds
    print optimize(f_package=F_PACKAGE, optimizer=SAESOptimizer(), timeout=5, plugins=plugins)
