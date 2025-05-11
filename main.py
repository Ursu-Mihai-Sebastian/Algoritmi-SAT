import random
import time
import tracemalloc
from rezolutie import rezolutie_pl
from DPLL import dpll_solver
from DP import dp_solver

def  genereaza_formula_satisfiabila(n_vars, n_clauze):
    """Generează o problemă 3-SAT satisfiabilă prin crearea inițială a unei atribuiri aleatoare"""
    variables = list(range(1, n_vars + 1))

    # Creează o atribuire satisfiabilă aleatoare
    assignment = {var: random.choice([True, False]) for var in variables}

    clauze = []
    for _ in range(n_clauze):
        # Generăm o clauză satisfăcută de atribuirea inițială
        while True:
            clause = set()
            # Alege 3 variabile distincte
            for var in random.sample(variables, min(3, len(variables))):
                # Inversează semnul cu o anumită probabilitate pentru a evita trivialitatea.
                if random.random() < 0.3:  # 30% sa schimbe semnul
                    clause.add(-var if assignment[var] else var)
                else:
                    clause.add(var if assignment[var] else -var)

            # Are grija ca clauza sa aibe 3 literali si sa nu fie tautologie
            if len(clause) == 3 and not any(-lit in clause for lit in clause):
                clauze.append(clause)
                break
    return clauze


def ruleaza_test(algoritm, clauze, nume="Algoritm"):
    print(f"Rulăm: {nume}")
    tracemalloc.start()
    t_start = time.perf_counter()
    rezultat, interpretare = algoritm(clauze)
    durata = time.perf_counter() - t_start
    mem_curenta, mem_max = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  Rezultat: {'NESATISFIABIL' if rezultat else 'SATISFIABIL'}")
    if interpretare:
        print(f"  Interpretare: {interpretare}")
    print(f"  Timp execuție: {durata:.4f} sec")
    print(f"  Memorie maximă: {mem_max / 1024:.2f} KB")
    print()


if __name__ == "__main__":
    print("=== Generator instanțe 3-SAT satisfiabile ===")
    numar_var = int(input("Introdu numărul de variabile: "))
    numar_clauze = int(input("Introdu numărul de clauze: "))

    formula = genereaza_formula_satisfiabila(numar_var, numar_clauze)

    print("\nFormulă generată:")
    for idx, cl in enumerate(formula):
        print(f"  Clauza {idx+1}: {cl}")

    # --- Algoritmi disponibili ---
    disponibili = {
        "1": ("Rezoluție", rezolutie_pl),
        "2": ("DPLL", dpll_solver),
        "3": ("DP", dp_solver)
    }

    print("\n Alege algoritmii de testat (ex: 1 2 3):")
    for cheie, (nume, _) in disponibili.items():
        print(f"  {cheie}) {nume}")

    selectie = input(" Introdu opțiunile (separate prin spațiu): ").split()
    algoritmi = {disponibili[opt][0]: disponibili[opt][1] for opt in selectie if opt in disponibili}

    print("\n=== Rezultate testare ===")
    for nume, func in algoritmi.items():
        ruleaza_test(func, formula, nume)