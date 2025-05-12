def rezolutie_pl(clauze):
    """
    Algoritmul rezolutiei pentru (CNF).
    Returneaza True daca formula este nesatisfiabila, False altfel.
    """
    # Convertim clauzele in frozenset pentru a putea fi stocate intr-un set
    clauze = [frozenset(clauza) for clauza in clauze]
    noi_clauze = set()

    # Setul initial de clauze pentru cautare eficienta
    baza_clauze = set(clauze)

    while True:
        # Generam toate perechile de clauze distincte
        perechi = [(ci, cj) for i, ci in enumerate(clauze) for cj in clauze[i+1:]]

        for (ci, cj) in perechi:
            rezultate = rezolva(ci, cj)

            # Daca rezultatul contine clauza vida => formula este nesatisfiabila
            if frozenset() in rezultate:
                return True, None  # NESATISFIABIL

            # Adaugam clauzele noi in multimea intermediara
            noi_clauze.update(rezultate)

        # Daca nu s-a generat nimic nou => nu se poate demonstra nesatisfiabilitatea
        if noi_clauze.issubset(baza_clauze):
            return False, None  # SATISFIABIL

        # Actualizam cu clauzele noi si reluam procesul
        baza_clauze.update(noi_clauze)
        clauze = list(baza_clauze)


def rezolva(clauza1, clauza2):
    """
    Aplica regula de rezolutie intre doua clauze.
    Returneaza clauze rezolvate (seturi fara tautologii).
    """
    rezultate = set()
    for literal in clauza1:
        if -literal in clauza2:
            clauza_noua = (clauza1 - {literal}) | (clauza2 - {-literal})
            # Eliminam clauzele tautologice (ex: x si ¬x), pentru Generatorul curent nu este cazul)
            if any(-lit in clauza_noua for lit in clauza_noua):
                continue
            rezultate.add(frozenset(clauza_noua))
    return rezultate