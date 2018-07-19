import cplex
from sys import argv

periodos = [
    {"total_hs": 6.0, "mw_req": 15000.0},
    {"total_hs": 3.0, "mw_req": 30000.0},
    {"total_hs": 6.0, "mw_req": 25000.0},
    {"total_hs": 3.0, "mw_req": 40000.0},
    {"total_hs": 6.0, "mw_req": 27000.0}
]

tipos = [
    {"min_mw": 850.0, "max_mw": 2000.0, "costo_min_hora": 1000.0, "costo_extra_hora": 2.0, "costo": 2000.0},
    {"min_mw": 1250.0, "max_mw": 1750.0, "costo_min_hora": 2600.0, "costo_extra_hora": 1.30, "costo": 1000.0},
    {"min_mw": 1500.0, "max_mw": 4000.0, "costo_min_hora": 3000.0, "costo_extra_hora": 3.0, "costo": 500.0}
]

cantidades = [12, 10, 5]

generadores = [tipos[0]] * cantidades[0] + [tipos[1]] * cantidades[1] + [tipos[2]] * cantidades[2]

cant_periodos = len(periodos)
cant_generadores = len(generadores)

def variables(problem):

    my_obj = []
    my_ub = []
    my_names = []

    # mw generados
    for p in range(cant_periodos):
        for g in range(cant_generadores):
            # costo extra por hora * cant horas
            my_obj += [ generadores[g]["costo_extra_hora"] * periodos[p]["total_hs"] ]
            my_ub += [ generadores[g]["max_mw"] ]
            my_names += [ "x_mw_"+str(p)+"_"+str(g) ]

    problem.variables.add(obj = my_obj, ub = my_ub, names = my_names)

    # generadores encendidos
    my_obj = [ g["costo"] for g in generadores ] * cant_periodos
    my_types = [ problem.variables.type.binary ] * cant_periodos * cant_generadores
    my_names = []

    for p in range(cant_periodos):
        for g in range(cant_generadores):
            my_names += [ "x_s_"+str(p)+"_"+str(g) ]

    problem.variables.add(obj = my_obj, types = my_types, names = my_names)

    # generadores usados

    my_obj = []
    my_names = []
    my_types = [ problem.variables.type.binary ] * cant_periodos * cant_generadores

    for p in range(cant_periodos):
        for g in range(cant_generadores):
            # costo de encenderlo al mínimo y descontamos los costos "extras" por hora que están por debajo del mínimo de mw
            my_obj += [ generadores[g]["costo_min_hora"] * periodos[p]["total_hs"] - generadores[g]["min_mw"] * periodos[p]["total_hs"] * generadores[g]["costo_extra_hora"] ]
            my_names += [ "x_u_"+str(p)+"_"+str(g) ]

    problem.variables.add(obj = my_obj, types = my_types, names = my_names)

# "las variables se comportan como queremos"
def var_constraints(problem):

    # si se usa, se encendió
    for g in range(cant_generadores):
        row_ind = [ "x_u_0_"+str(g), "x_s_0_"+str(g)]
        row_val = [1.0, -1.0]
        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
            rhs=[0.0],
            senses=["L"]
        )

    for p in range(1, cant_periodos):
        for g in range(cant_generadores):
            row_ind = [ "x_u_"+str(p)+"_"+str(g), "x_u_"+str(p-1)+"_"+str(g), "x_s_"+str(p)+"_"+str(g) ]
            row_val = [1.0, -1.0, -1.0]
            problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
                rhs=[0.0],
                senses=["L"]
            )

    # mw = 0 -> u = 0
    for p in range(cant_periodos):
        for g in range(cant_generadores):
            row_ind = [ "x_mw_"+str(p)+"_"+str(g), "x_u_"+str(p)+"_"+str(g) ]
            row_val = [-1.0, generadores[g]["min_mw"]]
            problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
                rhs=[0.0],
                senses=["L"]
            )

    # u = 0 -> mw = 0
    for p in range(cant_periodos):
        for g in range(cant_generadores):
            row_ind = [ "x_mw_"+str(p)+"_"+str(g), "x_u_"+str(p)+"_"+str(g) ]
            row_val = [1.0, -1.0*cplex.infinity]
            problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
                rhs=[0.0],
                senses=["L"]
            )

# "cumplimos las restricciones"
def req_constraints(problem):

    # cumplimos requisitos por periodo
    for p in range(cant_periodos):
        row_ind = [ "x_mw_"+str(p)+"_"+str(g) for g in range (cant_generadores) ]
        row_val = [1.0] * cant_generadores
        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
            rhs=[ periodos[p]["mw_req"] ],
            senses=["G"]
        )

    # todos al mango se bancan el incremento de 15%
    for p in range(cant_periodos):
        row_ind = [ "x_u_"+str(p)+"_"+str(g) for g in range (cant_generadores) ]
        row_val = [ g["max_mw"] for g in generadores ]
        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
            rhs=[ periodos[p]["mw_req"] * 1.15 ],
            senses=["G"]
        )

def constraints(problem):

    var_constraints(problem)
    req_constraints(problem)


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
