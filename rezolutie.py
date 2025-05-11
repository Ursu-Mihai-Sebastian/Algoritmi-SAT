def rezolutie_pl(clauze):
    """
    Algoritmul rezoluției pentru (CNF).
    Returnează True dacă formula este nesatisfiabilă, False altfel.
    """
    # Convertim clauzele în frozenset pentru a putea fi stocate într-un set
    clauze = [frozenset(clauza) for clauza in clauze]
    noi_clauze = set()

    # Setul inițial de clauze pentru căutare eficientă
    baza_clauze = set(clauze)

    while True:
        # Generăm toate perechile de clauze distincte
        perechi = [(ci, cj) for i, ci in enumerate(clauze) for cj in clauze[i+1:]]

        for (ci, cj) in perechi:
            rezultate = rezolva(ci, cj)

            # Dacă rezultatul conține clauza vidă => formula este nesatisfiabilă
            if frozenset() in rezultate:
                return True, None  # NESATISFIABIL

            # Adăugăm clauzele noi în mulțimea intermediară
            noi_clauze.update(rezultate)

        # Dacă nu s-a generat nimic nou => nu se poate demonstra nesatisfiabilitatea
        if noi_clauze.issubset(baza_clauze):
            return False, None  # SATISFIABIL (sau necunoscut prin rezoluție)

        # Actualizăm cu clauzele noi și reluăm procesul
        baza_clauze.update(noi_clauze)
        clauze = list(baza_clauze)


def rezolva(clauza1, clauza2):
    """
    Aplică regula de rezoluție între două clauze.
    Returnează clauze rezolvate (seturi fără tautologii).
    """
    rezultate = set()
    for literal in clauza1:
        if -literal in clauza2:
            clauza_noua = (clauza1 - {literal}) | (clauza2 - {-literal})
            # Eliminăm clauzele tautologice (ex: x și ¬x, pentru Generatorul meu nu este cazul dar poate daca vreti sa extindeti la alte implementari)
            if any(-lit in clauza_noua for lit in clauza_noua):
                continue
            rezultate.add(frozenset(clauza_noua))
    return rezultate