def _apply_assignment_to_clauses(clauses, var, val):
    """
    Aplică asignarea (var=val) unei liste de clauze.
    Fiecare clauză este un frozenset de literali.
    Returnează o nouă listă de clauze simplificate sau None dacă se ajunge la o contradicție (clauză vidă).
    """
    literal_assigned_true = var if val else -var
    literal_assigned_false = -var if val else var

    new_clauses = []
    for c in clauses:
        if literal_assigned_true in c:  # Clauza este satisfăcută
            continue
        if literal_assigned_false in c:  # Literalul este fals, trebuie eliminat din clauză
            simplified_clause = c - {literal_assigned_false}
            if not simplified_clause:  # S-a derivat o clauză vidă (contradicție)
                return None
            new_clauses.append(simplified_clause)
        else:  # Clauza nu conține var sau -var
            new_clauses.append(c)
    return new_clauses


def dpll_solver_recursive(clauses, assignment):
    """
    Funcția recursivă pentru algoritmul DPLL.
    clauses: listă de frozenset-uri (clauze).
    assignment: dicționar {var: bool} reprezentând asignările curente.
    Returnează: (is_unsatisfiable, model)
    """
    # Bucla principală pentru simplificare iterativă (Propagare Unitară și Eliminare Literal Pur)
    while True:
        prev_assignment_len = len(assignment)
        # Folosim o reprezentare sortată a clauzelor pentru a detecta modificări
        prev_clauses_repr = tuple(sorted(tuple(sorted(list(c))) for c in clauses))

        # --- 1. Propagare Unitară (Unit Propagation) ---
        # Buclă internă: continuă aplicarea propagării unitare cât timp se găsesc/procesează noi clauze unitare
        while True:
            unit_literal_to_process_next = None

            for c_unit in clauses:
                if len(c_unit) == 1:
                    lit = next(iter(c_unit))
                    var = abs(lit)
                    val_lit = lit > 0
                    if var in assignment:
                        if assignment[var] != val_lit: return (True, None)  # Contradicție cu asignarea existentă
                        # Dacă e asignat consistent, această clauză unitară e satisfăcută.
                        # Căutăm o clauză unitară care oferă o *nouă* asignare.
                    else:  # var nu e în assignment, deci e o nouă asignare posibilă
                        unit_literal_to_process_next = lit
                        break  # Am găsit un literal unitar de procesat

            if unit_literal_to_process_next:
                var_prop = abs(unit_literal_to_process_next)
                val_prop = unit_literal_to_process_next > 0

                assignment[var_prop] = val_prop  # Realizează noua asignare

                # Simplifică clauzele cu această nouă asignare
                clauses_after_prop = _apply_assignment_to_clauses(clauses, var_prop, val_prop)
                if clauses_after_prop is None: return (True, None)  # Contradicție
                clauses = clauses_after_prop
                if not clauses: return (False, assignment.copy())  # SATISFIABIL
                # Continuă bucla internă de propagare unitară
            else:
                # Nu s-au găsit literali unitari noi care să ducă la o nouă asignare
                break  # Ieși din bucla internă de propagare unitară

        # După stabilizarea propagării unitare:
        if not clauses: return (False, assignment.copy())
        if any(not c for c in clauses): return (True, None)  # S-a găsit o clauză vidă

        # --- 2. Eliminare Literal Pur (Pure Literal Elimination) ---
        # Buclă internă: continuă găsirea și asignarea literalilor puri
        while True:
            all_lits_current = {lit for cl in clauses for lit in cl}

            if not all_lits_current:  # Dacă nu mai sunt literali
                if not clauses: return (False, assignment.copy())  # SATISFIABIL, nicio clauză rămasă
                # Dacă există clauze dar nu literali, clauzele trebuie să fie vide
                if any(not c for c in clauses): return (True, None)  # NESATISFIABIL
                # Cazul (clauze există, nu sunt vide, dar nu sunt literali) e imposibil dacă formatul e corect.

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
                    if clauses_after_ple is None: return (True, None)  # Contradicție
                    clauses = clauses_after_ple
                    if not clauses: return (False, assignment.copy())  # SATISFIABIL

                    # Setul de clauze s-a schimbat, reia căutarea literalilor puri în această buclă PLE
                    break  # Ieși din bucla `for var_cand`

            if pure_literal_assigned_in_pass:
                continue  # Mergi la începutul buclei `while True` pentru PLE
            else:
                # Nu s-au asignat literali puri în această trecere a buclei interne PLE
                break  # Ieși din bucla internă PLE

        # După stabilizarea eliminării literalilor puri pentru această iterație externă:
        if not clauses: return (False, assignment.copy())
        if any(not c for c in clauses): return (True, None)

        # Verifică dacă pasul combinat de PU și ELP a produs vreo modificare
        current_clauses_repr = tuple(sorted(tuple(sorted(list(c))) for c in clauses))
        if len(assignment) == prev_assignment_len and current_clauses_repr == prev_clauses_repr:
            # S-a atins un punct fix pentru PU și ELP
            break  # Ieși din bucla externă de simplificare, treci la divizare sau cazuri de bază finale

    # --- Sfârșitul buclei externe de simplificare ---

    # Cazuri de bază finale după toate simplificările:
    if not clauses: return (False, assignment.copy())  # Toate clauzele satisfăcute
    if any(not c for c in clauses): return (True, None)  # S-a găsit o clauză vidă, deci NESATISFIABIL

    # --- 3. Regula de Divizare (Splitting Rule) ---
    # Selectează o variabilă neasignată pentru divizare
    split_var = -1
    unassigned_vars_for_split = set()
    for cl_split in clauses:  # Caută în toate clauzele rămase
        for lit_split in cl_split:
            var = abs(lit_split)
            if var not in assignment:
                unassigned_vars_for_split.add(var)

    if not unassigned_vars_for_split:
        # Toate variabilele din clauzele rămase sunt asignate.
        # Deoarece `clauses` nu este vid și nu există clauze vide,
        # înseamnă că asignarea curentă nu satisface clauzele rămase.
        # Deci, această cale este NESATISFIABILĂ.
        return (True, None)

    # Euristică simplă: alege variabila neasignată cu cel mai mic număr
    split_var = min(unassigned_vars_for_split)

    # Ramura 1: split_var = True
    assignment_true_branch = assignment.copy()
    assignment_true_branch[split_var] = True

    # Este important să trimitem o copie a listei de clauze, nu referința directă,
    # deoarece _apply_assignment_to_clauses returnează o nouă listă.
    clauses_for_true_branch = _apply_assignment_to_clauses(list(clauses), split_var, True)

    res_true, model_true = (True, None)  # Presupunem NESATISFIABIL inițial
    if clauses_for_true_branch is not None:  # Dacă nu e contradicție imediată
        res_true, model_true = dpll_solver_recursive(clauses_for_true_branch, assignment_true_branch)

    if not res_true:  # Dacă este SATISFIABIL pe ramura True
        return (False, model_true)  # model_true conține deja asignarea completă pentru această soluție

    # Ramura 2: split_var = False
    assignment_false_branch = assignment.copy()
    assignment_false_branch[split_var] = False

    clauses_for_false_branch = _apply_assignment_to_clauses(list(clauses), split_var, False)

    res_false, model_false = (True, None)  # Presupunem NESATISFIABIL inițial
    if clauses_for_false_branch is not None:  # Dacă nu e contradicție imediată
        res_false, model_false = dpll_solver_recursive(clauses_for_false_branch, assignment_false_branch)

    if not res_false:  # Dacă este SATISFIABIL pe ramura False
        return (False, model_false)

    # Ambele ramuri sunt NESATISFIABILE
    return (True, None)


def dpll_solver(clauses_input):
    """
    Solver SAT bazat pe algoritmul DPLL
    """
    # Cazul trivial: nicio clauză înseamnă satisfiabil
    if isinstance(clauses_input, list) and not clauses_input:
        return (False, {})

    # Verificare inițială pentru clauză vidă
    if any(not c for c in clauses_input):
        return (True, None)

    # Convertim clauzele într-o listă de frozenset-uri pentru procesare internă
    # Frozenset permite ca seturile să fie elemente în alte seturi sau chei în dicționare, dacă e necesar.
    try:
        clauses = [frozenset(clause) for clause in clauses_input]
    except TypeError:
        # Gestionarea erorii în cazul în care inputul nu este iterabil sau conține elemente ne-hashable
        # Acest lucru nu ar trebui să se întâmple cu outputul de la `genereaza_formula_satisfiabila`
        print("Eroare: Inputul pentru clauze nu este în formatul așteptat (listă de seturi/iterabile).")
        return (True, None)  # Considerăm nesatisfiabil în caz de format incorect

    # Extragem toate variabilele unice din problema originală
    # Acest lucru este important pentru a ne asigura că modelul final este complet
    # pentru toate variabilele care făceau parte din instanța problemei.
    original_variables = set()
    if clauses_input:
        for clause_set in clauses_input:
            if clause_set:  # Dacă setul de clauze (o clauză individuală) nu este vid
                for literal in clause_set:
                    original_variables.add(abs(literal))

    is_unsat, model = dpll_solver_recursive(list(clauses), {})  # Trimitem o copie a listei de clauze

    if not is_unsat:  # Dacă este satisfiabil
        final_model = {}
        if model is not None:  # Modelul ar putea fi None dacă ceva a eșuat intern, deși nu ar trebui
            final_model.update(model)

        # Asigură-te că toate variabilele originale sunt în model.
        # Dacă o variabilă a fost eliminată prin literal pur sau nu a făcut niciodată parte dintr-o divizare,
        # s-ar putea să lipsească. O asignare implicită (ex: True) este standard pentru variabile "don't care".
        for var in original_variables:
            if var not in final_model:
                final_model[var] = True  # Asignare implicită pentru variabilele neconstrânse
        return (False, final_model)
    else:  # Nesatisfiabil
        return (True, None)
