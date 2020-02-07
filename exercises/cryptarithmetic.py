from z3 import Solver, Int, Distinct, sat

ca_solver = Solver()

F, O, U, R, T, W = Int('F'), Int('O'), Int('U'), Int('R'), Int('T'), Int('W')
ca_solver.add(1 <= F, F <= 9)
ca_solver.add(0 <= O, O <= 9)
ca_solver.add(0 <= U, U <= 9)
ca_solver.add(0 <= R, R <= 9)
ca_solver.add(1 <= T, T <= 9)
ca_solver.add(0 <= W, W <= 9)

d = Distinct(F, O, U, R, T, W)
ca_solver.add(d)
ca_solver.add(2*O % 10 == R)
ca_solver.add(2*(W*10 + O) % 100 == U*10 + R)
ca_solver.add(2*(T*100 + W*10 + O) == F*1000 + O*100 + U*10 + R)


assert ca_solver.check() == sat, "Uh oh...the solver did not find a solution. Check your constraints."
print("  T W O  :    {} {} {}".format(ca_solver.model()[T], ca_solver.model()[W], ca_solver.model()[O]))
print("+ T W O  :  + {} {} {}".format(ca_solver.model()[T], ca_solver.model()[W], ca_solver.model()[O]))
print("-------  :  -------")
print("F O U R  :  {} {} {} {}".format(ca_solver.model()[F], ca_solver.model()[O], ca_solver.model()[U], ca_solver.model()[R]))

