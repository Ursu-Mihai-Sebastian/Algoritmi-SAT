def is_subsumed(new_clause, formula):
    """Verifica daca new_clause este logic mai slaba decat alta clauza (continuta de alta clauza)"""
    return any(new_clause.issuperset(c) for c in formula)

def dp_solver(formula):
    """
    Implementarea algoritmului Davis-Putnam clasic (fara literalul pur).
    Am facut optimizari pentru a face algoritmul complet doar cu pasii explcati in sectiunea sa
    de teorie.
    param formula: lista de clauze (seturi de literali)
    return: (True daca formula este nesatisfiabila, None)
    """
    formula = [set(clause) for clause in formula]
    all_clauses = set(frozenset(clause) for clause in formula)
    while True:
        # Eliminare tautologii nu avem in cazul nostru dar pentru corectitudine.
        formula = [clause for clause in formula if not any(-lit in clause for lit in clause)]

        # Verificare clauza vida (NESATISFIABIL)
        if any(len(clause) == 0 for clause in formula):
            return True, None  # NESATISFIABIL

        # Daca formula este goala => SATISFIABIL (nu se mai poate deduce nimic)
        if not formula:
            return False, {}  # SATISFIABIL, dar fara interpretare construita

        # Alegem o variabila pentru rezolutie
        literals = {lit for clause in formula for lit in clause}
        chosen = next(iter(literals))

        pos_clauses = [c for c in formula if chosen in c]
        neg_clauses = [c for c in formula if -chosen in c]
        rest_clauses = [c for c in formula if chosen not in c and -chosen not in c]

        # Aplicati rezolutia pentru toate combinatiile (A v x), (B v ¬x) => (A v B)
        new_clauses = []
        for c1 in pos_clauses:
            for c2 in neg_clauses:
                resolvent = (c1 - {chosen}) | (c2 - {-chosen})
                if not resolvent:  # Clauza vida.
                    return True, None  # UNSAT

                # Verifica sa nu fie tautologie
                if any(-lit in resolvent for lit in resolvent):
                    continue

                # Verificam daca clauza rezolventa a mai fost intalnita anterior in procesul de rezoluție.
                # Daca `frozen_resolvent` nu se afla in `all_clauses`, inseamna ca este o clauza noua si trebuie adaugata.
                frozen_resolvent = frozenset(resolvent)
                if frozen_resolvent not in all_clauses:  # Only add if not seen before
                    all_clauses.add(frozen_resolvent)
                    new_clauses.append(resolvent)


                # Verifica daca clauza este continuta de alta sau egala.
                if not is_subsumed(resolvent, rest_clauses + new_clauses):
                    new_clauses.append(resolvent)

        formula = rest_clauses + new_clauses