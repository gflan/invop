import cplex
from sys import argv

retailers = [
    #oil, delivery, spirit, category

    (9, 11, 34, 'A'),
    (13, 47, 411, 'A'),
    (14, 44, 82, 'A'),
    (17, 25, 157, 'B'),
    (18, 10, 5, 'A'),
    (19, 26, 183, 'A'),
    (23, 26, 14, 'B'),
    (21, 54, 215, 'B'),
    (9, 18, 102, 'B'),
    (11, 51, 21, 'A'),
    (17, 20, 54, 'B'),
    (18, 105, 0, 'B'),
    (18, 7, 6, 'B'),
    (17, 16, 96, 'B'),
    (22, 34, 118, 'A'),
    (24, 100, 112, 'B'),
    (36, 50, 535, 'B'),
    (43, 21, 8, 'B'),
    (6, 11, 53, 'B'),
    (15, 19, 28, 'A'),
    (15, 14, 69, 'B'),
    (25, 10, 65, 'B'),
    (39, 11, 27, 'B'),
]

n = len(retailers)

def variables(problem):

    my_obj = [0.0]*n + [1.0]
    my_types = [problem.variables.type.binary]*n + [problem.variables.type.continuous]
    my_names = ["x_1_"+str(i) for i in range(n)] + ["t"]

    problem.variables.add(obj = my_obj, types = my_types, names = my_names)

def constraints(problem):

    def add_range_constraint(row_ind, row_val):
        suma = sum(row_val)
        problem.linear_constraints.add(
                                lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
                                rhs=[0.45*suma],
                                senses=["L"])
        problem.linear_constraints.add(
                                lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val)],
                                rhs=[0.35*suma],
                                senses=["G"])

        # t constraints

        row_ind += [n]
        problem.linear_constraints.add(
                                lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val+[-1.0])],
                                rhs=[0.40*suma],
                                senses=["L"])
        problem.linear_constraints.add(
                                lin_expr=[cplex.SparsePair(ind=row_ind, val=row_val+[1.0])],
                                rhs=[0.40*suma],
                                senses=["G"])


    def add_retailer_att_constraint(row_ind, att):
        row_val = [retailers[i][att] for i in row_ind]
        add_range_constraint(row_ind, row_val)



    # total number of delivery points
    row_ind = [i for i in range(n)]
    add_retailer_att_constraint(row_ind, 1)

    # control of spirit market
    row_ind = [i for i in range(n)]
    add_retailer_att_constraint(row_ind, 2)

    # control of oil market (per region)
    # region 1
    row_ind = [i for i in range(8)]
    add_retailer_att_constraint(row_ind, 0)
    # region 2
    row_ind = [i for i in range(8,18)]
    add_retailer_att_constraint(row_ind, 0)

    # region 3
    row_ind = [i for i in range(18,n)]
    add_retailer_att_constraint(row_ind, 0)

    # number of retailers in A
    row_ind = [i for i in range(n) if retailers[i][3] == 'A']
    row_val = [1.0 for i in row_ind]
    add_range_constraint(row_ind, row_val)

    # number of retailers in B
    row_ind = [i for i in range(n) if retailers[i][3] == 'B']
    row_val = [1.0 for i in row_ind]
    add_range_constraint(row_ind, row_val)

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
