from ortools.sat.python import cp_model

def n_queens(N):
    model = cp_model.CpModel()

    queens = [model.NewIntVar(0, N-1, f'q_{i}') for i in range(N)]

    # Each queen must be in a different row
    model.AddAllDifferent(queens)

    # No two queens can be on the same diagonal
    model.AddAllDifferent([queens[i] - i for i in range(N)]) # queen[0] - 0 != queen[1] - 1 != ... != queen[N-1] - (N-1)
    model.AddAllDifferent([queens[i] + i for i in range(N)]) # queen[0] + 0 != queen[1] + 1 != ... != queen[N-1] + (N-1)
    # this is because if queen[i] - i == queen[j] - j, then queen[i] - queen[j] == i - j
    # it means that the difference between the row indices is equal to the difference between the column indices
    # this is the condition for two queens to be on the same diagonal

    solver = cp_model.CpSolver()
    solver.Solve(model)
