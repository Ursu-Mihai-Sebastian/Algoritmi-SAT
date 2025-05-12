import random
import time
import tracemalloc
from rezolutie import rezolutie_pl
from DPLL import dpll_solver
from DP import dp_solver


#Switchuri Hard codate
SHOW_ALL_CLAUSES = False  # True- va arata toate clauzele din formula generata.
SHOW_TRUTH_VALUES_DPLL = True  # True- va arata o enumeratie de literal-valoare pentru care CNF este satisfiabila.




def  genereaza_formula_satisfiabila(n_vars, n_clauze):
    """Genereaza o problema 3-SAT satisfiabila prin crearea initiala a unei atribuiri aleatoare"""
    variables = list(range(1, n_vars + 1))

    # Creeaza o atribuire satisfiabila aleatoare
    assignment = {var: random.choice([True, False]) for var in variables}

    clauze = []
    for _ in range(n_clauze):
        # Generam o clauza satisfacuta de atribuirea initiala
        while True:
            clause = set()
            # Alege 3 variabile distincte
            for var in random.sample(variables, min(3, len(variables))):
                # Inverseaza semnul cu o anumita probabilitate pentru a evita trivialitatea.
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
    print(f"Rulam: {nume}")
    tracemalloc.start()
    t_start = time.perf_counter()
    rezultat, interpretare = algoritm(clauze)
    durata = time.perf_counter() - t_start
    mem_curenta, mem_max = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  Rezultat: {'NESATISFIABIL' if rezultat else 'SATISFIABIL'}")
    if interpretare and SHOW_TRUTH_VALUES_DPLL:
        print(f"  Interpretare: {interpretare}")
    print(f"  Timp executie: {durata:.4f} sec")
    print(f"  Memorie maxima: {mem_max / 1024:.2f} KB")
    print()


if __name__ == "__main__":
    print("=== Generator instante 3-SAT satisfiabile ===")
    numar_var = int(input("Introdu numarul de variabile: "))
    numar_clauze = int(input("Introdu numarul de clauze: "))
    numar_teste = int(input("Introdu numarul de teste (1-10): "))
    numar_teste = max(1, min(10, numar_teste))  # Are grija ca numarul maxim de teste sa fie 10


    # --- Algoritmi disponibili ---
    disponibili = {
        "1": ("Rezolutie", rezolutie_pl),
        "2": ("DPLL", dpll_solver),
        "3": ("DP", dp_solver)
    }

    print("\n Alege algoritmii de testat (ex: 1 2 3):")
    for cheie, (nume, _) in disponibili.items():
        print(f"  {cheie}) {nume}")

    selectie = input(" Introdu optiunile (separate prin spatiu): ").split()
    algoritmi = {disponibili[opt][0]: disponibili[opt][1] for opt in selectie if opt in disponibili}

    for test in range(1, numar_teste + 1):
        print(f"\n=== Testul {test} ===")
        formula = genereaza_formula_satisfiabila(numar_var, numar_clauze)

        if SHOW_ALL_CLAUSES:
            print("\nFormula generata:")
            for idx, cl in enumerate(formula):
                print(f"  Clauza {idx + 1}: {cl}")
        else:
            print(f"\nFormula generata cu {len(formula)} clauze (afisarea literal:valoare este dezactivata)")

        print("\n=== Rezultate testare ===")
        for nume, func in algoritmi.items():
            ruleaza_test(func, formula, nume)