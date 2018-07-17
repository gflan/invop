import cplex
from sys import argv

periodos = [
	{total_hs: 6, mw_req: 15000},
	{total_hs: 3, mw_req: 30000},
	{total_hs: 6, mw_req: 25000},
	{total_hs: 3, mw_req: 40000},
	{total_hs: 6, mw_req: 27000}
]

tipos = [
	{cant: 12, min_mw: 850, max_mw: 2000, costo_min_hora: 1000, costo_extra_hora: 2, costo: 2000}, 
	{cant: 10, min_mw: 1250, max_mw: 1750, costo_min_hora: 2600, costo_extra_hora: 1.30, costo: 1000}, 
	{cant: 5, min_mw: 1500, max_mw: 4000, costo_min_hora: 3000, costo_extra_hora: 3, costo: 500}
]

def constraints(problem): 

	cant_periodos = len(periodos)
	cant_tipos = 3

	my_obj = []
	my_ub = []
	my_names = []
	my_lb = []

	# mw generados
	for p in range(cant_periodos):
		for t in range(cant_tipos):
			# costo extra por hora * cant horas
			my_obj += [ tipos[t][costo_extra_hora] * periodos[p][total_hs] ]
			my_ub += [ tipos[t][max_mw] ]
			my_lb += [ tipos[t][min_mw] ]
			my_names += [ "x_mw_"+str(p)+"_"+str(t) ]

    problem.variables.add(obj = my_obj, ub = my_ub, lb = my_lb, names = my_names)

	# generadores encendidos
	my_obj = [ tipos[t][costo] for t in cant(tipos) ] * cant_periodos
	my_types = [ problem.variables.type.binary ] * cant_tipos * cant_tipos
	my_names = []

	for p in range(cant_periodos):
		for t in range(cant_tipos):
			my_names += [ "x_s_"+str(p)+"_"+str(t) ]

    problem.variables.add(obj = my_obj, type = my_types, names = my_names)

	# generadores usados 

	

    problem.variables.add(obj = my_obj, ub = my_ub, names = nombres)
