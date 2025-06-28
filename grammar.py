from collections import OrderedDict

class Grammar:
    def __init__(self):
        self.start_symbol = None
        self.non_terminals = set()
        self.terminals = OrderedDict()  #Changed to OrderedDict to preserve order
        self.terminal_order = []       #Additional list to track order explicitly
        self.productions = {}

    def validate(self):
        undefined = set()
        for nt, prods in self.productions.items():  # Iterate over productions correctly
            for prod in prods:  # Each prod is a list of symbols (e.g., ['ID', 'EQUALS', 'Expression'])
                for sym in prod:  # Check each symbol in the production
                    if (sym not in self.terminals and 
                        sym not in self.non_terminals and 
                        sym != 'eps'):
                        undefined.add(sym)
        if undefined:
            raise ValueError(f"Undefined symbols: {undefined}")
        
    def compute_first_sets(self):
        self.first = {nt: set() for nt in self.non_terminals}
        self.first.update({t: {t} for t in self.terminals})
        self.first['eps'] = {'eps'}

        def recursive_first(symbol):
            # Base case: terminals or epsilon
            if symbol in self.terminals or symbol == 'eps':
                return {symbol}
            
            # If already computed (non-empty), return cached result
            if self.first[symbol]:
                return self.first[symbol].copy()
            
            first_set = set()
            for prod in self.productions.get(symbol, []):
                if prod == ['eps']:
                    first_set.add('eps')
                else:
                    all_contain_epsilon = True
                    for sym in prod:
                        sym_first = recursive_first(sym)
                        first_set.update(sym_first - {'eps'})
                        if 'eps' not in sym_first:
                            all_contain_epsilon = False
                            break
                    if all_contain_epsilon:
                        first_set.add('eps')
            
            self.first[symbol] = first_set
            return first_set

        # Compute FIRST for all non-terminals
        for nt in self.non_terminals:
            recursive_first(nt)

        # Compute FIRST for all non-terminals
        for nt in self.non_terminals:
            self.first[nt] = recursive_first(nt)

    def compute_follow_sets(self):
        self.follow = {nt: set() for nt in self.non_terminals}
        self.follow[self.start_symbol].add('$')
        
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
                            if 'eps' in self.first.get(symbol, set()):
                                trailer.update(self.first[symbol] - {'eps'})
                            else:
                                trailer = self.first.get(symbol, set() - {'eps'}).copy()
                            
                            if len(self.follow[symbol]) > before:
                                changed = True
                        elif symbol in self.terminals:
                            # Terminals reset the trailer
                            trailer = {symbol}
                        # else: skip eps

    def load_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        mode = None
        i = 0
        
        while i < len(lines):
            line = lines[i]
            if line.startswith("START"):
                self.start_symbol = line.split("=")[1].strip()
            elif line.startswith("NON_TERMINALS"):
                nts = line.split("=")[1].strip()
                while i + 1 < len(lines) and not lines[i+1].startswith(("TERMINALS", "#", "Grammar Productions")):
                    i += 1
                    nts += " " + lines[i].strip()
                self.non_terminals = {nt.strip() for nt in nts.replace('\n', ' ').split(',')}
            elif line.startswith("TERMINALS"):
                #Just parse (not ordering)
                ts = line.split("=")[1].strip()
                while i + 1 < len(lines) and not lines[i+1].startswith(("NON_TERMINALS", "#", "Grammar Productions")):
                    i += 1
                    ts += " " + lines[i].strip()
            elif "Grammar Productions" in line:
                mode = "productions"
            elif "Lexical Definitions" in line:
                mode = "lexical"
                #(tracking order)
                self.terminals = OrderedDict()  #reset to capture lexical order
            elif "->" in line and mode == "lexical":
                lhs, rhs = map(str.strip, line.split("->"))
                rhs = rhs.strip()
                if rhs.startswith('/') and rhs.endswith('/'):
                    rhs = rhs[1:-1]
                #add to terminals in the order they appear in lexical definitions
                if lhs not in self.terminals:
                    self.terminals[lhs] = f"/{rhs}/"
            elif "->" in line and mode == "productions":
                lhs, rhs = map(str.strip, line.split("->"))
                while i + 1 < len(lines) and "->" not in lines[i + 1]:
                    next_line = lines[i + 1].strip()
                    if next_line.startswith("|"):
                        rhs += " " + next_line.strip()
                        i += 1
                    else:
                        break
                productions = []
                for alt in rhs.split('|'):
                    cleaned = ' '.join(alt.strip().split())
                    if cleaned:
                        productions.append(cleaned.split())
                self.productions.setdefault(lhs, []).extend(productions)
            i += 1
            
    def compute_ll1_table(self):
        """Compute the LL(1) parsing table and return it as a dictionary of dictionaries"""
        if not hasattr(self, 'first'):
            self.compute_first_sets()
        if not hasattr(self, 'follow'):
            self.compute_follow_sets()
        
        # Initialize table: {non_terminal: {terminal: production}}
        ll1_table = {nt: {} for nt in self.non_terminals}
        
        for nt in self.non_terminals:
            for prod in self.productions.get(nt, []):
                first_of_prod = self.compute_first_of_sequence(prod)
                
                # Rule 1: For each terminal in FIRST(prod), add prod
                for t in first_of_prod - {'eps'}:
                    if t in self.terminals:
                        if t in ll1_table[nt]:
                            raise ValueError(f"Grammar is not LL(1): conflict at {nt} -> {t}")
                        ll1_table[nt][t] = prod
                
                # Rule 2: If epsilon is in FIRST(prod), add for FOLLOW(nt)
                if 'eps' in first_of_prod:
                    for t in self.follow[nt]:
                        if t in self.terminals:
                            if t in ll1_table[nt]:
                                raise ValueError(f"Grammar is not LL(1): conflict at {nt} -> {t}")
                            ll1_table[nt][t] = prod
                        elif t == '$':
                            if '$' in ll1_table[nt]:
                                raise ValueError(f"Grammar is not LL(1): conflict at {nt} -> $")
                            ll1_table[nt]['$'] = prod
        
        return ll1_table

    def compute_first_of_sequence(self, sequence):
        """Helper: Compute FIRST set for a sequence of symbols"""
        if not sequence or sequence == ['eps']:
            return {'eps'}
        
        first = set()
        all_have_epsilon = True
        
        for symbol in sequence:
            if symbol in self.terminals:
                first.add(symbol)
                all_have_epsilon = False
                break
            elif symbol in self.non_terminals:
                first.update(self.first[symbol] - {'eps'})
                if 'eps' not in self.first[symbol]:
                    all_have_epsilon = False
                    break
        
        if all_have_epsilon:
            first.add('eps')
        
        return first