import cplex
from sys import argv

def solved_print(problem):
    nombres = problem.variables.get_names()
    for nombre in nombres:
        print("{}: {}".format(nombre, problem.solution.get_values(nombre)))

if __name__ == "__main__":

    problem = cplex.Cplex("ej12_06.lp")

    if len(argv) > 1:
        problem.write(str(argv[1])+".lp")

    problem.solve()

    solved_print(problem)
    print("max: {}".format(problem.solution.get_objective_value()))
