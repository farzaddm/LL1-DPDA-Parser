class Grammar:
    def __init__(self):
        self.start_symbol = None
        self.non_terminals = set()
        self.terminals = {}
        self.productions = {}

    def validate(self):
        undefined = set()
        for lhs, prods in self.productions.items():
            for prod in prods:
                for sym in prod:
                    if sym not in self.terminals and sym not in self.non_terminals and sym != "eps":
                        undefined.add(sym)
        if undefined:
            raise ValueError(f"Undefined symbols: {undefined}")

    def compute_first_sets(self):
        # Initialize FIRST sets
        self.first = {nt: set() for nt in self.non_terminals}
        self.first.update({t: {t} for t in self.terminals})
        self.first["eps"] = {"eps"}

        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for prod in self.productions.get(nt, []):
                    # Handle epsilon production
                    if prod == ["eps"]:
                        before = len(self.first[nt])
                        self.first[nt].add("eps")
                        if len(self.first[nt]) > before:
                            changed = True
                        continue

                    # Process each symbol in production
                    all_contain_epsilon = True
                    before = len(self.first[nt])

                    for symbol in prod:
                        # Add FIRST(symbol) - {eps}
                        self.first[nt].update(self.first.get(symbol, set()) - {"eps"})

                        # Check if symbol can derive epsilon
                        if "eps" not in self.first.get(symbol, set()):
                            all_contain_epsilon = False
                            break

                    # If all symbols can derive epsilon, add epsilon
                    if all_contain_epsilon:
                        self.first[nt].add("eps")

                    if len(self.first[nt]) > before:
                        changed = True

    def compute_follow_sets(self):
        self.follow = {nt: set() for nt in self.non_terminals}
        self.follow[self.start_symbol].add("$")

        changed = True
        while changed:
            changed = False
            for nt, prods in self.productions.items():
                for prod in prods:
                    # Initialize trailer with FOLLOW of LHS
                    trailer = self.follow[nt].copy()

                    # Process right to left
                    for symbol in reversed(prod):
                        if symbol in self.non_terminals:
                            # Add current trailer to FOLLOW[symbol]
                            before = len(self.follow[symbol])
                            self.follow[symbol].update(trailer)

                            # Prepare trailer for next symbol
                            if "eps" in self.first.get(symbol, set()):
                                trailer.update(self.first[symbol] - {"eps"})
                            else:
                                trailer = self.first.get(symbol, set() - {"eps"}).copy()

                            if len(self.follow[symbol]) > before:
                                changed = True
                        elif symbol in self.terminals:
                            # Terminals reset the trailer
                            trailer = {symbol}
                        # else: skip eps

    def load_from_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        mode = None
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("START"):
                self.start_symbol = line.split("=")[1].strip()
            elif line.startswith("NON_TERMINALS"):
                # Handle multi-line non-terminal definitions
                nts = line.split("=")[1].strip()
                while i + 1 < len(lines) and not lines[i + 1].startswith(("TERMINALS", "#", "Grammar Productions")):
                    i += 1
                    nts += " " + lines[i].strip()
                self.non_terminals = {nt.strip() for nt in nts.replace("\n", " ").split(",")}
            elif line.startswith("TERMINALS"):
                # Handle multi-line terminal definitions
                ts = line.split("=")[1].strip()
                while i + 1 < len(lines) and not lines[i + 1].startswith(("NON_TERMINALS", "#", "Grammar Productions")):
                    i += 1
                    ts += " " + lines[i].strip()
                self.terminals = {t.strip(): None for t in ts.replace("\n", " ").split(",")}
            elif "Grammar Productions" in line or "Productions" in line:
                mode = "productions"
            elif "Lexical Definitions" in line or "Definitions" in line:
                mode = "terminals"
            elif "->" in line:
                lhs, rhs = map(str.strip, line.split("->"))

                # Handle multi-line productions
                while i + 1 < len(lines) and "->" not in lines[i + 1]:
                    next_line = lines[i + 1].strip()
                    if next_line.startswith("|") or next_line.startswith((" ", "\t")):
                        rhs += " " + next_line.strip()
                        i += 1
                    else:
                        break

                if mode == "productions":
                    # Normalize spacing and split properly
                    productions = []
                    for alt in rhs.split("|"):
                        # Clean each alternative production
                        cleaned = " ".join(alt.strip().split())  # Normalize spaces
                        if cleaned:  # Skip empty productions
                            productions.append(cleaned.split())
                    self.productions.setdefault(lhs, []).extend(productions)
                elif mode == "terminals":
                    rhs = rhs.strip().strip("/")
                    self.terminals[lhs] = f"/{rhs}/" if rhs else "//"
            i += 1

    def compute_ll1_table(self):
        """Compute the LL(1) parsing table and return it as a dictionary of dictionaries"""
        if not hasattr(self, "first"):
            self.compute_first_sets()
        if not hasattr(self, "follow"):
            self.compute_follow_sets()

        # Initialize table: {non_terminal: {terminal: production}}
        ll1_table = {nt: {} for nt in self.non_terminals}

        for nt in self.non_terminals:
            for prod in self.productions.get(nt, []):
                first_of_prod = self.compute_first_of_sequence(prod)

                # Rule 1: For each terminal in FIRST(prod), add prod
                for t in first_of_prod - {"eps"}:
                    if t in self.terminals:
                        if t in ll1_table[nt]:
                            raise ValueError(f"Grammar is not LL(1): conflict at {nt} -> {t}")
                        ll1_table[nt][t] = prod

                # Rule 2: If epsilon is in FIRST(prod), add for FOLLOW(nt)
                if "eps" in first_of_prod:
                    for t in self.follow[nt]:
                        if t in self.terminals:
                            if t in ll1_table[nt]:
                                raise ValueError(f"Grammar is not LL(1): conflict at {nt} -> {t}")
                            ll1_table[nt][t] = prod
                        elif t == "$":
                            if "$" in ll1_table[nt]:
                                raise ValueError(f"Grammar is not LL(1): conflict at {nt} -> $")
                            ll1_table[nt]["$"] = prod

        return ll1_table

    def compute_first_of_sequence(self, sequence):
        """Helper: Compute FIRST set for a sequence of symbols"""
        if not sequence or sequence == ["eps"]:
            return {"eps"}

        first = set()
        all_have_epsilon = True

        for symbol in sequence:
            if symbol in self.terminals:
                first.add(symbol)
                all_have_epsilon = False
                break
            elif symbol in self.non_terminals:
                first.update(self.first[symbol] - {"eps"})
                if "eps" not in self.first[symbol]:
                    all_have_epsilon = False
                    break

        if all_have_epsilon:
            first.add("eps")

        return first
