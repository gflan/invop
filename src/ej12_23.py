import cplex
from numpy import sqrt
from sys import argve

nodos = [
    {"x": .0,   "y": .0,    "collect": .0},
    {"x": -3.0, "y": 3.0,   "collect": .0},
    {"x": 1.0,  "y": 11.0,  "collect": .0},
    {"x": 4.0,  "y": 7.0,   "collect": .0},
    {"x": -5.0, "y": 9.0,   "collect": .0},
    {"x": -5.0, "y": -2.0,  "collect": .0},
    {"x": -4.0, "y": 7.0,   "collect": .0},
    {"x": 6.0,  "y": .0,    "collect": .0},
    {"x": 3.0,  "y": -6.0,  "collect": .0},
    {"x": -1.0, "y": -3.0,  "collect": .0},
    {"x": .0,   "y": -6.0,  "collect": .0},
    {"x": 6.0,  "y": 4.0,   "collect": .0},
    {"x": 2.0,  "y": 5.0,   "collect": .0},
    {"x": -2.0, "y": 8.0,   "collect": .0},
    {"x": 6.0,  "y": 10.0,  "collect": .0},
    {"x": 1.0,  "y": 8.0,   "collect": .0},
    {"x": -3.0, "y": 1.0,   "collect": .0},
    {"x": -6.0, "y": 5.0,   "collect": .0},
    {"x": 2.0,  "y": 9.0,   "collect": .0},
    {"x": -6.0, "y": -5.0,  "collect": .0},
    {"x": 5.0,  "y": -4.0,  "collect": .0}
]

cant_nodos = len(nodos)
cant_obligatorios = 10

def dist(a,b):
    return sqrt( (a["x"]-b["x"])**2 + (a["y"]-b["y"])**2 )

def variables(problem):

    # ir de i a j en ambos caminos

    my_types = [ problem.variables.type.binary ] * cant_nodos * cant_nodos * 2
    my_names = []
    my_obj = []

    for path in [1,2]:
        for i in range(cant_nodos):
            my_names += [ "x_"+str(path)+"_"+str(i)+"_"+str(j) for j in range(cant_nodos) ]
            my_obj += [ dist(nodos[i], nodos[j]) for j in range(cant_nodos) ]

    problem.variables.add(obj = my_obj, types = my_types, names = my_names)


def constraints(problem):

    # ambos caminos pasan una vez por los obligatorios
    for path in [1, 2]:
        for j in range(cant_obligatorios):
            row_ind = ["x_"+str(path)+"_"+str(i)+"_"+str(j) for i in range(cant_nodos)]
            row_val = [1.0] * cant_nodos
            problem.linear_constraints.add(
                lin_expr= [cplex.SparsePair(ind=row_ind, val=row_val)],
                rhs= [1.0],
                senses= ["E"]
            )


    # entre los dos caminos se pasa una vez por cada nodo no obligatorio
    for j in range(cant_obligatorios, cant_nodos):
        row_ind =   ["x_1_"+str(i)+"_"+str(j) for i in range(cant_nodos)] + \
                    ["x_2_"+str(i)+"_"+str(j) for i in range(cant_nodos)]

        row_val = [1.0] * cant_nodos * 2
        problem.linear_constraints.add(
            lin_expr= [cplex.SparsePair(ind=row_ind, val=row_val)],
            rhs= [1.0],
            senses= ["E"]
        )

    # no sucede i -> i
    for path in [1, 2]:
        row_ind = ["x_"+str(path)+"_"+str(i)+"_"+str(i) for i in range(cant_nodos)]
        row_val = [1.0] * cant_nodos
        problem.linear_constraints.add(
            lin_expr= [cplex.SparsePair(ind=row_ind, val=row_val)],
            rhs= [0.0],
            senses= ["E"]
        )

    # no se excede las capacidades de recolección
    for path in [1, 2]:

        row_ind = []
        row_val = []

        for i in range(cant_nodos):
            row_ind += ["x_"+str(path)+"_"+str(i)+"_"+str(j) for j in range(cant_nodos)]
            row_val += [ nj["collect"] for nj in nodos ]

        problem.linear_constraints.add(
            lin_expr= [cplex.SparsePair(ind=row_ind, val=row_val)],
            rhs= [80.0],
            senses= ["L"]
        )

def solved_print(problem):

    nombres = problem.variables.get_names()
    for nombre in nombres:
        print("{}: {}".format(nombre, problem.solution.get_values(nombre)))

    print("min: {}".format(problem.solution.get_objective_value()))

if __name__ == "__main__":

    problem = cplex.Cplex()
    problem.objective.set_sense(problem.objective.sense.minimize)

    variables(problem)
    constraints(problem)

    if len(argv) > 1:
        problem.write(str(argv[1])+".lp")

    problem.solve()

    solved_print(problem)
