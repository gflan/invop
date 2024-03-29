from sys import argv
import cplex
from ej12_01 import *

def variables_2(problem):
    variables(problem)
    # bool vars
    my_obj = [0.0]*cant_tipos*cant_meses
    my_types = [problem.variables.type.binary]*cant_tipos*cant_meses
    nombres = []

    for m in range(cant_meses):
        nombres += ["x_usa_"+str(m)+"_"+str(t) for t in range(cant_tipos)]

    problem.variables.add(obj = my_obj, types = my_types, names=nombres)

def constraints_2(problem):
    constraints(problem)

    # bool 0 -> ref 0
    ptro_bool_primer_mes = 3*cant_tipos*cant_meses
    for mes in range(cant_meses):
        for tipo in range(cant_tipos):
            row_ind = [mes*cant_tipos + tipo, ptro_bool_primer_mes + mes*cant_tipos + tipo]
            row_val = [1.0, -250.0]
            problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)], rhs=[0.0], senses=["L"])
    # bool 1 -> ref > 20
    for mes in range(cant_meses):
        for tipo in range(cant_tipos):
            row_ind = [mes*cant_tipos + tipo, ptro_bool_primer_mes + mes*cant_tipos + tipo]
            row_val = [1.0, -20.0]
            problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)], rhs=[0.0], senses=["G"])
    # veg 1 o veg 2 -> oil 3

    for mes in range(cant_meses):

        #veg 1 -> oil 3
        row_ind = [ptro_bool_primer_mes + mes*cant_tipos + 0, ptro_bool_primer_mes + mes*cant_tipos + 4]
        row_val = [1.0, -1.0]
        problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)], rhs=[0.0], senses=["L"])

        #veg 2 -> oil 3
        row_ind = [ptro_bool_primer_mes + mes*cant_tipos + 1, ptro_bool_primer_mes + mes*cant_tipos + 4]
        row_val = [1.0, -1.0]
        problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)], rhs=[0.0], senses=["L"])

        # menos de 3 aceites
        row_ind = [ptro_bool_primer_mes + mes*cant_tipos + i for i in range(cant_tipos)]
        row_val = [1.0] * cant_tipos
        problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)], rhs=[3.0], senses=["L"])


def solved_print(problem):

    for mes in range(cant_meses):
        print("mes: {}".format(mes))

        refinado = []
        for tipo in range(cant_tipos):
            refinado += [problem.solution.get_values(mes*cant_tipos + tipo)]
        print("refinado: {}".format(refinado))

        comprado = []
        for tipo in range(cant_tipos):
            comprado += [problem.solution.get_values(cant_meses*cant_tipos + mes*cant_tipos + tipo)]
        print("comprado: {}".format(comprado))

        almacenado = []
        for tipo in range(cant_tipos):
            almacenado += [problem.solution.get_values(2*cant_meses*cant_tipos + mes*cant_tipos + tipo)]
        print("almacenado: {}".format(almacenado))

        usado = []
        for tipo in range(cant_tipos):
            usado += [problem.solution.get_values(3*cant_meses*cant_tipos + mes*cant_tipos + tipo)]
        print("usado: {}".format(usado))



if __name__ == "__main__":

    problem = cplex.Cplex()
    problem.objective.set_sense(problem.objective.sense.maximize)

    # experimentacion

    #f = problem.parameters.preprocessing.presolve.values.off
    #f = problem.parameters.preprocessing.presolve.values.on
    #problem.parameters.preprocessing.presolve.set(f)

    #f = problem.parameters.mip.strategy.nodeselect.values.depth_first
    #f = problem.parameters.mip.strategy.nodeselect.values.best_bound
    #f = problem.parameters.mip.strategy.nodeselect.values.best_estimate
    #f = problem.parameters.mip.strategy.nodeselect.values.best_estimate_alt
    #problem.parameters.mip.strategy.nodeselect.set(f)

    #f = problem.parameters.mip.strategy.branch.values.down
    #f = problem.parameters.mip.strategy.branch.values.up
    #problem.parameters.mip.strategy.branch.set(f)

    #f = problem.parameters.mip.strategy.variableselect.values.min_infeasibility
    #f = problem.parameters.mip.strategy.variableselect.values.max_infeasibility
    #f = problem.parameters.mip.strategy.variableselect.values.pseudo_costs
    #f = problem.parameters.mip.strategy.variableselect.values.strong_branching
    #f = problem.parameters.mip.strategy.variableselect.values.pseudo_reduced_costs
    #problem.parameters.mip.strategy.variableselect.set(f)

    #f = problem.parameters.mip.cuts.covers.values.none
    #f = problem.parameters.mip.cuts.covers.values.aggressive
    #f = problem.parameters.mip.cuts.covers.values.very_aggressive
    #problem.parameters.mip.cuts.covers.set(f)
    #problem.parameters.mip.cuts.cliques.set(f)

    variables_2(problem)
    constraints_2(problem)

    if len(argv) > 1:
        problem.write(str(argv[1])+".lp")

    problem.solve()

    solved_print(problem)
    print("max: {}".format(problem.solution.get_objective_value()))
