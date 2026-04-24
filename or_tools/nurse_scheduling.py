from ortools.sat.python import cp_model

# num_infermieri, giorni, turni
def nurse_scheduling(n, g, t):
    model = cp_model.CpModel()
    
    shifts = {}
    for i in range(n):
        for j in range(g):
            for k in range(t):
                shifts[(i, j, k)] = model.NewBoolVar(f'nurse_{i}_day_{j}_shift_{k}')

    # Un infermiere per turno
    for j in range(g):
        for k in range(t):
            model.AddExactlyOne([shifts[(i, j, k)] for i in range(n)])

    # Un turno al giorno per ciascun infermiere
    for i in range(n):
        for j in range(g):
            model.AddAtMostOne([shifts[(i, j, k)] for k in range(t)])

    # Distribuzione equa dei turni: la somma di tutti i turni di un infermiere deve essere compresa fra min_shifts e max_shifts
    min_shifts_value = (t * g) // n
    min_shifts = model.NewIntVar(min_shifts_value, min_shifts_value, 'min_s')
    max_shifts = model.NewIntVar(min_shifts_value, g*t, 'max_s')
    turni = []
    for i in range(n):
        # calcolo il numero di turni per ciascun infermiere
        num_turni = sum(shifts[(i, j, k)] for j in range(g) for k in range(t))
        turni.append(num_turni)
    
    val_max = model.AddMaxEquality(max_shifts, turni) # imposta max_shifts al massimo fra i turni
    model.minimize(val_max - min_shifts) # minimizza la differenza fra il numero massimo e minimo di turni

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    return status, model
