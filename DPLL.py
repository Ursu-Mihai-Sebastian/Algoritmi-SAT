def _apply_assignment_to_clauses(clauses, var, val):
    """
    Aplica asignarea (var=val) unei liste de clauze.
    Fiecare clauza este un frozenset de literali.
    Returneaza o noua lista de clauze simplificate sau None daca se ajunge la o contradictie (clauza vida).
    """
    literal_assigned_true = var if val else -var
    literal_assigned_false = -var if val else var

    new_clauses = []
    for c in clauses:
        if literal_assigned_true in c:  # Clauza este satisfacuta
            continue
        if literal_assigned_false in c:  # Literalul este fals, trebuie eliminat din clauza
            simplified_clause = c - {literal_assigned_false}
            if not simplified_clause:  # S-a derivat o clauza vida (contradictie)
                return None
            new_clauses.append(simplified_clause)
        else:  # Clauza nu contine var sau -var
            new_clauses.append(c)
    return new_clauses


def dpll_solver_recursive(clauses, assignment):
    """
    Functia recursiva pentru algoritmul DPLL.
    clauses: lista de frozenset-uri (clauze).
    assignment: dictionar {var: bool} reprezentand asignarile curente.
    Returneaza: (is_unsatisfiable, model)
    """
    # Bucla principala pentru simplificare iterativa (Propagare Unitara si Eliminare Literal Pur)
    while True:
        prev_assignment_len = len(assignment)
        # Folosim o reprezentare sortata a clauzelor pentru a detecta modificari
        prev_clauses_repr = tuple(sorted(tuple(sorted(list(c))) for c in clauses))

        # --- 1. Propagare Unitara (Unit Propagation) ---
        # Bucla interna: continua aplicarea propagarii unitare cat timp se gasesc/proceseaza noi clauze unitare
        while True:
            unit_literal_to_process_next = None

            for c_unit in clauses:
                if len(c_unit) == 1:
                    lit = next(iter(c_unit))
                    var = abs(lit)
                    val_lit = lit > 0
                    if var in assignment:
                        if assignment[var] != val_lit: return (True, None)  # Contradictie cu asignarea existenta
                        # Daca e asignat consistent, aceasta clauza unitara e satisfacuta.
                        # Cautam o clauza unitara care ofera o *noua* asignare.
                    else:  # var nu e in assignment, deci e o noua asignare posibila
                        unit_literal_to_process_next = lit
                        break  # Am gasit un literal unitar de procesat

            if unit_literal_to_process_next:
                var_prop = abs(unit_literal_to_process_next)
                val_prop = unit_literal_to_process_next > 0

                assignment[var_prop] = val_prop  # Realizeaza noua asignare

                # Simplifica clauzele cu aceasta noua asignare
                clauses_after_prop = _apply_assignment_to_clauses(clauses, var_prop, val_prop)
                if clauses_after_prop is None: return (True, None)  # Contradictie
                clauses = clauses_after_prop
                if not clauses: return (False, assignment.copy())  # SATISFIABIL
                # Continua bucla interna de propagare unitara
            else:
                # Nu s-au gasit literali unitari noi care sa duca la o noua asignare
                break  # Iesi din bucla interna de propagare unitara

        # Dupa stabilizarea propagarii unitare:
        if not clauses: return (False, assignment.copy())
        if any(not c for c in clauses): return (True, None)  # S-a gasit o clauza vida

        # --- 2. Eliminare Literal Pur (Pure Literal Elimination) ---
        # Bucla interna: continua gasirea si asignarea literalilor puri
        while True:
            all_lits_current = {lit for cl in clauses for lit in cl}

            if not all_lits_current:  # Daca nu mai sunt literali
                if not clauses: return (False, assignment.copy())  # SATISFIABIL, nicio clauza ramasa
                # Daca exista clauze dar nu literali, clauzele trebuie sa fie vide
                if any(not c for c in clauses): return (True, None)  # NESATISFIABIL
                # Cazul (clauze exista, nu sunt vide, dar nu sunt literali) e imposibil daca formatul e corect.

            pure_literal_assigned_in_pass = False

            unassigned_vars_in_clauses = set()
            for cl_ple in clauses:
                for lit_ple in cl_ple:
                    var_ple = abs(lit_ple)
                    if var_ple not in assignment:
                        unassigned_vars_in_clauses.add(var_ple)

            for var_cand in sorted(list(unassigned_vars_in_clauses)):  # Sortat pentru determinism
                is_pos_present = var_cand in all_lits_current
                is_neg_present = -var_cand in all_lits_current

                val_for_pure_assignment = None
                if is_pos_present and not is_neg_present:
                    val_for_pure_assignment = True
                elif is_neg_present and not is_pos_present:
                    val_for_pure_assignment = False

                if val_for_pure_assignment is not None:
                    assignment[var_cand] = val_for_pure_assignment
                    pure_literal_assigned_in_pass = True

                    clauses_after_ple = _apply_assignment_to_clauses(clauses, var_cand, val_for_pure_assignment)
                    if clauses_after_ple is None: return (True, None)  # Contradictie
                    clauses = clauses_after_ple
                    if not clauses: return (False, assignment.copy())  # SATISFIABIL

                    # Setul de clauze s-a schimbat, reia cautarea literalilor puri in aceasta bucla PLE
                    break  # Iesi din bucla `for var_cand`

            if pure_literal_assigned_in_pass:
                continue  # Mergi la inceputul buclei `while True` pentru PLE
            else:
                # Nu s-au asignat literali puri in aceasta trecere a buclei interna
                break  # Iesi din bucla interna PLE

        # Dupa stabilizarea eliminarii literalilor puri pentru aceasta iteratie externa:
        if not clauses: return (False, assignment.copy())
        if any(not c for c in clauses): return (True, None)

        # Verifica daca pasul combinat de PU si ELP a produs vreo modificare
        current_clauses_repr = tuple(sorted(tuple(sorted(list(c))) for c in clauses))
        if len(assignment) == prev_assignment_len and current_clauses_repr == prev_clauses_repr:
            # S-a atins un punct fix pentru PU si ELP
            break  # Iesi din bucla externa de simplificare, treci la divizare sau cazuri de baza finale

    # --- Sfarsitul buclei externe de simplificare ---

    # Cazuri de baza finale dupa toate simplificarile:
    if not clauses: return (False, assignment.copy())  # Toate clauzele satisfacute
    if any(not c for c in clauses): return (True, None)  # S-a gasit o clauza vida, deci NESATISFIABIL

    # --- 3. Regula de Divizare (Splitting Rule) ---
    # Selecteaza o variabila neasignata pentru divizare
    split_var = -1
    unassigned_vars_for_split = set()
    for cl_split in clauses:  # Cauta in toate clauzele ramase
        for lit_split in cl_split:
            var = abs(lit_split)
            if var not in assignment:
                unassigned_vars_for_split.add(var)

    if not unassigned_vars_for_split:
        # Toate variabilele din clauzele ramase sunt asignate.
        # Deoarece `clauses` nu este vid si nu exista clauze vide,
        # inseamna ca asignarea curenta nu satisface clauzele ramase.
        # Deci, aceasta cale este NESATISFIABILA.
        return (True, None)

    # Euristica simpla: alege variabila neasignata cu cel mai mic numar
    # Posibila implementarea de ereustice avansate pentru a compara diferenta intre optimizari
    split_var = min(unassigned_vars_for_split)

    # Ramura 1: split_var = True
    assignment_true_branch = assignment.copy()
    assignment_true_branch[split_var] = True

    # Este important sa trimitem o copie a listei de clauze, nu referinta directa,
    # deoarece _apply_assignment_to_clauses returneaza o noua lista.
    clauses_for_true_branch = _apply_assignment_to_clauses(list(clauses), split_var, True)

    res_true, model_true = (True, None)  # Presupunem NESATISFIABIL initial
    if clauses_for_true_branch is not None:  # Daca nu e contradictie imediata
        res_true, model_true = dpll_solver_recursive(clauses_for_true_branch, assignment_true_branch)

    if not res_true:  # Daca este SATISFIABIL pe ramura True
        return (False, model_true)  # model_true contine deja asignarea completa pentru aceasta solutie

    # Ramura 2: split_var = False
    assignment_false_branch = assignment.copy()
    assignment_false_branch[split_var] = False

    clauses_for_false_branch = _apply_assignment_to_clauses(list(clauses), split_var, False)

    res_false, model_false = (True, None)  # Presupunem NESATISFIABIL initial
    if clauses_for_false_branch is not None:  # Daca nu e contradictie imediata
        res_false, model_false = dpll_solver_recursive(clauses_for_false_branch, assignment_false_branch)

    if not res_false:  # Daca este SATISFIABIL pe ramura False
        return (False, model_false)

    # Ambele ramuri sunt NESATISFIABILE
    return (True, None)


def dpll_solver(clauses_input):
    """
    Solver SAT bazat pe algoritmul DPLL
    """
    # Cazul trivial: nicio clauza inseamna satisfiabil
    if isinstance(clauses_input, list) and not clauses_input:
        return (False, {})

    # Verificare initiala pentru clauza vida
    if any(not c for c in clauses_input):
        return (True, None)

    # Convertim clauzele intr-o lista de frozenset-uri pentru procesare interna
    # Frozenset permite ca seturile sa fie elemente in alte seturi sau chei in dictionare.
    try:
        clauses = [frozenset(clause) for clause in clauses_input]
    except TypeError:
        # Gestionarea erorii in cazul in care inputul nu este iterabil
        # Acest lucru nu ar trebui sa se intample cu outputul de la `genereaza_formula_satisfiabila`
        print("Eroare: Inputul pentru clauze nu este in formatul asteptat (lista de seturi/iterabile).")
        return (True, None)  # Consideram nesatisfiabil in caz de format incorect

    # Extragem toate variabilele unice din problema originala
    # Acest lucru este important pentru a ne asigura ca modelul final este complet
    # pentru toate variabilele care faceau parte din instanta problemei.
    original_variables = set()
    if clauses_input:
        for clause_set in clauses_input:
            if clause_set:  # Daca setul de clauze (o clauza individuala) nu este vid
                for literal in clause_set:
                    original_variables.add(abs(literal))

    is_unsat, model = dpll_solver_recursive(list(clauses), {})  # Trimitem o copie a listei de clauze

    if not is_unsat:  # Daca este satisfiabil
        final_model = {}
        if model is not None:  # Modelul ar putea fi None daca ceva a esuat intern, desi nu ar trebui
            final_model.update(model)

        # Daca o variabila a fost eliminata prin literal pur sau nu a facut niciodata parte dintr-o divizare,
        for var in original_variables:
            if var not in final_model:
                final_model[var] = True  # Asignare implicita pentru variabilele libere
        return (False, final_model)
    else:  # Nesatisfiabil
        return (True, None)
