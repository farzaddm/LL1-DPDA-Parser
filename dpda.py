from visualizer import ParseTreeNode

class DPDA:
    def __init__(self, start_symbol, terminals, non_terminals, parsing_table, transitions):
        self.start_symbol = start_symbol
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.parsing_table = parsing_table

        # DPDA definition
        self.states = {"q", "q_accept"}
        self.input_alphabet = set(terminals) | {"$"}
        self.stack_alphabet = set(terminals) | set(non_terminals) | {"$"}
        self.initial_stack_symbol = "$"
        self.final_states = {"q_accept"}
        self.transitions = transitions

    @classmethod
    def build_from_parsing_table(cls, grammar):
        """
        Builds a DPDA from a Grammar's parsing table.

        Args:
            grammar (Grammar): Grammar instance with parsing_table attribute.

        Returns:
            DPDA: a configured DPDA instance.
        """
        parsing_table = grammar.compute_ll1_table()
        transitions = {}
        for pop_from_stack, row in parsing_table.items():
            for input_char, production in row.items():
                key = ("q", input_char, pop_from_stack)
                if production != ["eps"]:
                    transitions[key] = ("q", list(reversed(production)))

        for terminal in grammar.terminals.keys():
            key = ("q", terminal, terminal)
            transitions[key] = ("q", [])

        transitions[("q", "$", "$")] = ("q_accept", [])

        return cls(
            start_symbol=grammar.start_symbol,
            terminals=grammar.terminals.keys(),
            non_terminals=grammar.non_terminals,
            parsing_table=parsing_table,
            transitions=transitions,
        )

    def simulate(self, tokens):
        """
        It parse the tokens(input) with the parsing tree

        Args:
            tokens (list[str]): List of token types, e.g., ['LEFT_PAR', 'IDENTIFIER', 'PLUS', ...]

        Returns:
            bool: True if the input is accepted, False otherwise.
            root: The root of parsing tree
        """
        stack = ["$", self.start_symbol]
        tokens.append("$")
        position = 0

        root = ParseTreeNode(self.start_symbol)
        tree_stack = [root]

        while stack:
            top = stack.pop()

            if top == "$":
                if position == len(tokens) - 1:
                    return True, root
                else:
                    return False, None

            if position >= len(tokens):
                return False, None

            current_token = tokens[position]

            if top in self.terminals:
                if top == current_token:
                    position += 1
                    if tree_stack:
                        tree_stack.pop()
                else:
                    return False, None

            elif top in self.non_terminals:
                if current_token in self.parsing_table[top]:
                    production = self.parsing_table[top][current_token]
                    parent_node = tree_stack.pop()

                    if production == ["eps"]:
                        parent_node.add_child(ParseTreeNode("eps"))
                    else:
                        child_nodes = [ParseTreeNode(symbol) for symbol in production]
                        for child in child_nodes:
                            parent_node.add_child(child)

                        for symbol in reversed(production):
                            stack.append(symbol)

                        for symbol, child in reversed(list(zip(production, child_nodes))):
                            tree_stack.append(child)
                else:
                    return False, None
            else:
                return False, None

        return False, None