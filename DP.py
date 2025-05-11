def dp_solver(formula):
    """
    Implementarea algoritmului Davis-Putnam clasic.
    :param formula: listă de clauze (seturi de literali)
    :return: (True dacă formula este nesatisfiabilă, None)
    """
    formula = [set(clause) for clause in formula]

    while True:
        # Eliminare tautologii nu avem in cazul nostru dar pentru corectitudine.
        formula = [clause for clause in formula if not any(-lit in clause for lit in clause)]

        # Verificare clauză vidă (NESATISFIABIL)
        if any(len(clause) == 0 for clause in formula):
            return True, None  # NESATISFIABIL

        # Dacă formula este goală => SATISFIABIL (nu se mai poate deduce nimic)
        if not formula:
            return False, {}  # SATISFIABIL, dar fără interpretare construită

        # Alegem o variabilă pentru rezoluție
        literals = {lit for clause in formula for lit in clause}
        chosen = next(iter(literals))

        pos_clauses = [c for c in formula if chosen in c]
        neg_clauses = [c for c in formula if -chosen in c]
        rest_clauses = [c for c in formula if chosen not in c and -chosen not in c]

        # Aplicați rezoluția pentru toate combinațiile (A v x), (B v ¬x) => (A v B)
        new_clauses = []
        for c1 in pos_clauses:
            for c2 in neg_clauses:
                resolvent = (c1 - {chosen}) | (c2 - {-chosen})
                # Verifică să nu fie tautologie
                if not any(-lit in resolvent for lit in resolvent):
                    new_clauses.append(resolvent)

        formula = rest_clauses + new_clauses