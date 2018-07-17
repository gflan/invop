import cplex
from sys import argv
from ej12_15 import *

hydro_A = {
    "level": 900.0,
    "costo_hora": 90.0,
    "reduccion_hora": .31,
    "start_cost": 1500.0
}
hydro_B = {
    "level": 1400.0,
    "costo_hora": 150.0,
    "reduccion_hora": .47,
    "start_cost": 1200.0
}


def variables_new(problem):
    # las mismas variables de antes
    variables(problem)

    # hidro-gens usados

    my_obj = []
    my_names = []
    my_types = [ problem.variables.type.binary ] * cant_periodos * 2

    for p in range(cant_periodos):
        my_obj += [ hydro_A["costo_hora"] * periodos[p]["total_hs"], hydro_B["costo_hora"] * periodos[p]["total_hs"] ]
        my_names += [ "x_u_"+str(p)+"_A", "x_u_"+str(p)+"_B" ]

    problem.variables.add(obj = my_obj, types = my_types, names = my_names)

    # hidro-gens arrancados

    my_obj = []
    my_names = []
    my_types = [ problem.variables.type.binary ] * cant_periodos * 2

    for p in range(cant_periodos):
        my_obj += [ hydro_A["start_cost"], hydro_B["start_cost"]]
        my_names += [ "x_s_"+str(p)+"_A", "x_s_"+str(p)+"_B" ]

    problem.variables.add(obj = my_obj, types = my_types, names = my_names)

    # output a la reserva por generador

    my_obj = []
    my_ub = []
    my_names = []

    for p in range(cant_periodos):
        for g in range(cant_generadores):
            # el costo se paga por mw totales, independientemente del uso
            my_obj += [ 0.0 ]
            my_ub += [ generadores[g]["max_mw"] ]
            my_names += [ "x_r_"+str(p)+"_"+str(g) ]

    problem.variables.add(obj = my_obj, ub = my_ub, names = my_names)

    # altura de la reserva por periodo

    my_obj = [ 0.0 ] * cant_periodos
    my_ub = [ 20.0 ] * cant_periodos
    my_lb = [ 15.0 ] * cant_periodos
    my_names = [ "x_h_"+str(p) for p in range(cant_periodos) ]

    problem.variables.add(obj = my_obj, ub = my_ub, lb = my_lb, names = my_names)


def constraints_new(problem):

    # las restricciones de requisitos de mw cambian, pero el comportamiento
    # de las vars sigue siendo el mismo

    var_constraints(problem)

    # si se usa UN HIDRO, se encendió
        # primer periodo
    for hidro in ['A','B']:
        row_ind = [ "x_u_0_"+hidro, "x_s_0_"+hidro]
        row_val = [1.0, -1.0]

        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
            rhs=[0.0],
            senses=["L"]
        )

        # resto de los periodos
    for p in range(1, cant_periodos):
        for hidro in ['A','B']:
            row_ind = [
                "x_u_"+str(p)+"_"+hidro,
                "x_u_"+str(p-1)+"_"+hidro,
                "x_s_"+str(p)+"_"+hidro
            ]
            row_val = [1.0, -1.0, -1.0]
            problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
                rhs=[0.0],
                senses=["L"]
            )

    # altura de cada periodo
        # al finalizar primer periodo
    row_ind = [
        "x_h_0",
        "x_u_0_A",
        "x_u_0_B"
    ] + [ "x_r_0_"+str(g) for g in range(cant_generadores) ]

    row_val = [
        1.0,
        hydro_A["reduccion_hora"]*periodos[0]["total_hs"],
        hydro_B["reduccion_hora"]*periodos[0]["total_hs"],
    ] + [-1/3000.0] * cant_generadores

    problem.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
        rhs=[16.0],
        senses=["E"]
    )

        # intermedios
    for p in range(1, cant_periodos):
        row_ind = [
            "x_h_"+str(p),
            "x_h_"+str(p-1),
            "x_u_"+str(p)+"_A",
            "x_u_"+str(p)+"_B"
        ] + [ "x_r_"+str(p)+"_"+str(g) for g in range(cant_generadores) ]

        row_val = [
            1.0,
            -1.0,
            hydro_A["reduccion_hora"]*periodos[p]["total_hs"],
            hydro_B["reduccion_hora"]*periodos[p]["total_hs"],
        ] + [-1/3000.0] * cant_generadores

        problem.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
            rhs=[0.0],
            senses=["E"]
        )

        # asegurar ult periodo altura 16
    problem.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=["x_h_"+str(cant_periodos-1)], val=[1.0])],
        rhs=[16.0],
        senses=["E"]
    )

    # requisitos de potencia

    for p in range(cant_periodos):
        row_ind =   [ "x_mw_"+str(p)+"_"+str(g) for g in range (cant_generadores) ] \
                    + [ "x_r_"+str(p)+"_"+str(g) for g in range (cant_generadores) ] \
                    + [ "x_u_"+str(p)+"_A", "x_u_"+str(p)+"_B" ]

        row_val =   [1.0] * cant_generadores + [-1.0] * cant_generadores \
                    + [ hydro_A["level"], hydro_B["level"] ]

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
            # el mw_req menos la suma de los mws de los hidros
            rhs=[ periodos[p]["mw_req"] * 1.15 - hydro_A["level"] - hydro_B["level"] ],
            senses=["G"]
        )

def solved_print(problem):

    nombres = problem.variables.get_names()
    for nombre in nombres:
        print("{}: {}".format(nombre, problem.solution.get_values(nombre)))

    print("min: {}".format(problem.solution.get_objective_value()))

if __name__ == "__main__":

    problem = cplex.Cplex()
    problem.objective.set_sense(problem.objective.sense.minimize)

    variables_new(problem)
    constraints_new(problem)

    if len(argv) > 1:
        problem.write(str(argv[1])+".lp")

    problem.solve()

    solved_print(problem)
