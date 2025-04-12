# python3 src/dataloader.py
# python3 src/problem.py
# python3 src/solver.py

for n in {4..8}
do
    python3 src/dataloader.py -n $n
    python3 test/test_problem.py -n $n
    python3 test/test_solver.py -n $n
    python3 test/test_figure.py -n $n
done