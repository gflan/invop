import cplex
from sys import argv

precio = [
    [110,120,130,110,115],
    [130,130,110,90,115],
    [110,140,130,100,95],
    [120,110,120,120,125],
    [100,120,150,110,105],
    [90,100,140,80,135]
]

dureza = [
    8.8,
    6.1,
    2.0,
    4.2,
    5.0
]

cant_tipos = 5
cant_meses = 6
##########################


def objetivo(problem):

    my_obj = []
    my_ub = []
    nombres = []

    #refinado
    for mes in range(cant_meses):
        my_obj += [150.0]*cant_tipos
        my_ub += [200.0]*2 + [250.0]*3
        nombres += ["x_ref_"+str(mes)+"_"+str(tipo) for tipo in range(cant_tipos)]

    #comprado
    for mes in range(cant_meses):
        my_obj += [-1.0*precio[mes][tipo] for tipo in range(cant_tipos)]
        my_ub += [cplex.infinity]*cant_tipos
        nombres += ["x_cmp_"+str(mes)+"_"+str(tipo) for tipo in range(cant_tipos)]


    #almacenado
    for mes in range(cant_meses):
        my_obj += [-5.0]*cant_tipos
        my_ub += [1000.0]*cant_tipos
        nombres += ["x_alm_"+str(mes)+"_"+str(tipo) for tipo in range(cant_tipos)]

    problem.variables.add(obj = my_obj, ub = my_ub, names = nombres)

def constraints(problem):

    #dureza maxima
    for mes in range(cant_meses):
        row_ind = [mes*cant_tipos + tipo for tipo in range(cant_tipos)]
        row_val = [d-6.0 for d in dureza]
        problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)], rhs=[0.0], senses=["L"])

    #dureza minima
    for mes in range(cant_meses):
        row_ind = [mes*cant_tipos + tipo for tipo in range(cant_tipos)]
        row_val = [d-3.0 for d in dureza]
        problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)], rhs=[0.0], senses=["G"])

    ptr_almacenado_ult_mes = 3*cant_tipos*cant_meses-cant_tipos

    # 500 de storage el ultimo mes
    for tipo in range(cant_tipos):
        problem.linear_constraints.add(lin_expr=[cplex.SparsePair([ptr_almacenado_ult_mes+tipo], [1.0])], rhs=[500.0], senses=["E"])

    # se almacena lo que no se refina
    # 500 de storage el primer mes

    ptr_comprado_primer_mes = cant_meses*cant_tipos
    ptr_almacenado_primer_mes = 2*cant_tipos*cant_meses
    ptr_refinado_primer_mes = 0

    row_ind = []
    row_val = []

    for tipo in range(cant_tipos):
        row_ind = [
            ptr_almacenado_primer_mes + tipo,
            ptr_refinado_primer_mes + tipo,
            ptr_comprado_primer_mes + tipo
        ]
        row_val = [1.0, 1.0, -1.0]
        problem.linear_constraints.add(lin_expr=[cplex.SparsePair(row_ind, row_val)], rhs=[500.0], senses=["E"])

    # resto de los dias
    for mes in range(1, cant_meses):
        row_ind = []
        row_val = []
        for tipo in range(cant_tipos):
            row_ind = [
                ptr_almacenado_primer_mes + mes * cant_tipos + tipo,
                ptr_almacenado_primer_mes + (mes-1) * cant_tipos + tipo,
                ptr_refinado_primer_mes + mes * cant_tipos + tipo,
                ptr_comprado_primer_mes + mes * cant_tipos + tipo
            ]
            row_val = [1.0, -1.0, 1.0, -1.0]
            problem.linear_constraints.add(lin_expr=[cplex.SparsePair(row_ind, row_val)], rhs=[0.0], senses=["E"])

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


if __name__ == "__main__":

    problem = cplex.Cplex()
    problem.objective.set_sense(problem.objective.sense.maximize)

    objetivo(problem)
    constraints(problem)

    if len(argv) > 1:
        problem.write(str(argv[1])+".lp")

    problem.solve()

    solved_print(problem)
    print("max: {}".format(problem.solution.get_objective_value()))
