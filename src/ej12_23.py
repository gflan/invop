import cplex
import cplex.callbacks as CPX_CB
from numpy import sqrt
from sys import argv, exit

nodos = [
    {"x": .0,   "y": .0,    "collect": .0},
    {"x": -3.0, "y": 3.0,   "collect": 5.0},
    {"x": 1.0,  "y": 11.0,  "collect": 4.0},
    {"x": 4.0,  "y": 7.0,   "collect": 3.0},
    {"x": -5.0, "y": 9.0,   "collect": 6.0},
    {"x": -5.0, "y": -2.0,  "collect": 7.0},
    {"x": -4.0, "y": 7.0,   "collect": 3.0},
    {"x": 6.0,  "y": .0,    "collect": 4.0},
    {"x": 3.0,  "y": -6.0,  "collect": 6.0},
    {"x": -1.0, "y": -3.0,  "collect": 5.0},
    {"x": .0,   "y": -6.0,  "collect": 4.0},
    {"x": 6.0,  "y": 4.0,   "collect": 7.0},
    {"x": 2.0,  "y": 5.0,   "collect": 3.0},
    {"x": -2.0, "y": 8.0,   "collect": 4.0},
    {"x": 6.0,  "y": 10.0,  "collect": 5.0},
    {"x": 1.0,  "y": 8.0,   "collect": 6.0},
    {"x": -3.0, "y": 1.0,   "collect": 8.0},
    {"x": -6.0, "y": 5.0,   "collect": 5.0},
    {"x": 2.0,  "y": 9.0,   "collect": 7.0},
    {"x": -6.0, "y": -5.0,  "collect": 6.0},
    {"x": 5.0,  "y": -4.0,  "collect": 6.0}
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

    # si se entra a algún nodo en un camino, se sale de este
    for path in [1, 2]:
        for j in range(cant_nodos):
            row_ind =   ["x_"+str(path)+"_"+str(i)+"_"+str(j) for i in range(cant_nodos)] + \
                        ["x_"+str(path)+"_"+str(j)+"_"+str(i) for i in range(cant_nodos) \
                        if i != j]
            row_val = [1.0] * cant_nodos + [-1.0] * (cant_nodos-1)
            problem.linear_constraints.add(
                lin_expr= [cplex.SparsePair(ind=row_ind, val=row_val)],
                rhs= [0.0],
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

    def conseguir_siguiente(camino, i):

        siguiente = [j for j in range(cant_nodos) if \
            problem.solution.get_values("x_"+str(path)+"_"+str(i)+"_"+str(j)) > 0
        ]

        if len(siguiente) != 1:
            nombres = problem.variables.get_names()
            for nombre in nombres:
                print("{}: {}".format(nombre, problem.solution.get_values(nombre)))

            exit("[!] error en el nodo {} en el camino {}".format(i, camino))

        else:
            return siguiente[0]

    for path in [1,2]:
        print("----Camino: {}".format(path))
        print("nodo actual: {}".format(0))

        actual = conseguir_siguiente(path, 0)
        while (actual != 0):
            print("nodo actual: {}".format(actual))
            actual = conseguir_siguiente(path, actual)

        print("nodo actual: {}".format(0))

    print("min: {}".format(problem.solution.get_objective_value()))


class IncumbentSubtourCallback(CPX_CB.IncumbentCallback):

    # llamada cada vez que hay una nueva candidata a sol. óptima
    def __call__(self):

        # si hay subtour rechazamos la solución actual
        if self.hay_subtour():
            self.times_trimmed += 1
            self.reject()

    def hay_subtour(self):

        # por camino
        for path in [1, 2]:

            # anotamos todos los nodos que forman parte de algun "camino"
            visitados = {}
            for i in range(cant_nodos):
                for j in range(cant_nodos):
                    if self.get_values("x_"+str(path)+"_"+str(i)+"_"+str(j)) > 0:
                        visitados[i] = j
                        break

            nombres = problem.variables.get_names()

            # iteramos el camino que sale del nodo 0

            actual = 0
            actual = visitados.pop(actual)
            while actual != 0:
                actual = visitados.pop(actual)

            if len(visitados) > 0:
                return True

        return False

class LazySubtourCallback(CPX_CB.LazyConstraintCallback):

    # por cada solución factible
    def __call__(self):

        for path in [1, 2]:

            # anotamos todos los nodos que forman parte de algun "camino"
            visitados = {}
            for i in range(cant_nodos):
                for j in range(cant_nodos):
                    if self.get_values("x_"+str(path)+"_"+str(i)+"_"+str(j)) > 0:
                        visitados[i] = j
                        break

            nombres = problem.variables.get_names()

            # iteramos el camino que sale del nodo 0

            actual = 0
            actual = visitados.pop(actual)
            while actual != 0:
                actual = visitados.pop(actual)

            while len(visitados) > 0:
                # armamos los subtours para restringirlos

                self.times_added += 1

                inicial = list(visitados.keys())[0]
                actual = visitados.pop(inicial)
                ciclo = [actual]

                while actual != inicial:
                    actual = visitados.pop(actual)
                    ciclo += [actual]

                # en ciclo ahora tenemos los numeros de cada nodo
                # restringimos globalmente el subtour encontrado

                row_ind = ["x_"+str(path)+"_"+str(i)+"_"+str(j) for i in ciclo for j in ciclo]
                row_val = [1.0] * len(ciclo) * len(ciclo)

                self.add(
                    constraint = cplex.SparsePair(ind=row_ind, val=row_val),
                    rhs = len(ciclo) - 1.0,
                    sense = "L",
                    use = 1
                )

if __name__ == "__main__":

    problem = cplex.Cplex()
    problem.objective.set_sense(problem.objective.sense.minimize)

    problem.parameters.preprocessing.reduce.set(1)

    #solo testing
    #subtour_incumbent_cb = problem.register_callback(IncumbentSubtourCallback)
    #subtour_incumbent_cb.times_trimmed = 0

    subtour_lazy_constraint_cb = problem.register_callback(LazySubtourCallback)
    subtour_lazy_constraint_cb.times_added = 0

    variables(problem)
    constraints(problem)

    if len(argv) > 1:
        problem.write(str(argv[1])+".lp")

    problem.solve()

    solved_print(problem)

    print("")
    #print("incumbents rechazados por subtour desde el nodo inicial:")
    #print("{}".format(subtour_incumbent_cb.times_trimmed))
    print("cantidad de lazy constraints de subtour agregadas:")
    print("{}".format(subtour_lazy_constraint_cb.times_added))
