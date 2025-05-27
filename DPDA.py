from grammar import Grammar
from lexer import Lexer
from visualizer import ParseTreeNode


class DPDA:
    def __init__(self, start_symbol, terminals, non_terminals, parsing_table, transitions):
        self.start_symbol = start_symbol
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.parsing_table = parsing_table
        self.transitions = transitions

        # For formal DPDA definition (not optional!)
        self.states = {"q", "q_accept"}
        self.input_alphabet = set(terminals) | {"$"}
        self.stack_alphabet = set(terminals) | set(non_terminals) | {"$"}
        self.initial_stack_symbol = "$"
        self.final_states = {"q_accept"}

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
        # Build transitions based on parsing table
        for non_terminal, row in parsing_table.items():
            for lookahead, production in row.items():
                key = ("q", lookahead, non_terminal)
                if production == ["eps"]:
                    # Pop the non-terminal, no push
                    transitions[key] = ("q", [])
                else:
                    # Pop the non-terminal, push the production (in reverse)
                    transitions[key] = ("q", list(reversed(production)))

        # Transitions for matching terminal tokens
        for terminal in grammar.terminals.keys():
            key = ("q", terminal, terminal)
            transitions[key] = ("q", [])

        # Accept condition: if input is $ and stack is $ (we can define it here as needed)
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
        Simulates the DPDA to parse a tokenized input based on the LL(1) parsing table.

        Args:
            tokens (list[str]): List of token types, e.g., ['LEFT_PAR', 'IDENTIFIER', 'PLUS', ...]

        Returns:
            bool: True if the input is accepted, False otherwise.
        """
        stack = ["$", self.start_symbol]  # Initialize stack with start symbol and end marker
        tokens.append("$")  # Add end marker to input
        position = 0  # Current input position

        while stack:
            top = stack.pop()  # Top of the stack
            current_token = tokens[position]  # Current input token

            if top == "eps":
                # Epsilon — do nothing
                continue

            elif top in self.terminals or top == "$":
                # Terminal — must match the current input
                if top == current_token:
                    position += 1
                else:
                    # Mismatch — reject
                    return False

            elif top in self.non_terminals:
                # Non-terminal — lookup parsing table
                if current_token in self.parsing_table[top]:
                    production = self.parsing_table[top][current_token]
                    # Push production symbols in reverse order
                    for symbol in reversed(production):
                        stack.append(symbol)
                else:
                    # No valid production — reject
                    return False
            else:
                # Unknown symbol — reject
                return False

        # Accept if all input tokens consumed
        return position == len(tokens)
 #! ====================================================================================
    def simulate(self, tokens):
        stack = ["$", self.start_symbol]
        tokens.append("$")
        position = 0

        root = ParseTreeNode(self.start_symbol)
        tree_stack = [root]  # Stack to keep track of current parent nodes

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
                    # Only create terminal node when we match
                    terminal_node = ParseTreeNode(current_token)
                    tree_stack[-1].add_child(terminal_node)
                    position += 1
                else:
                    return False, None

            elif top in self.non_terminals:
                if current_token in self.parsing_table[top]:
                    production = self.parsing_table[top][current_token]
                    parent_node = tree_stack.pop()  # Get the current parent node

                    if production == ["eps"]:
                        parent_node.add_child(ParseTreeNode("eps"))
                    else:
                        # 1. ابتدا فرزندان را به ترتیب صحیح به درخت اضافه می‌کنیم (چپ به راست)
                        child_nodes = []
                        for symbol in production:
                            child_node = ParseTreeNode(symbol)
                            parent_node.add_child(child_node)
                            child_nodes.append(child_node)
                        
                        # 2. سپس سمبول‌ها را به صورت معکوس به استک اضافه می‌کنیم (راست به چپ)
                        for symbol, child_node in zip(reversed(production), reversed(child_nodes)):
                            stack.append(symbol)
                            if symbol in self.non_terminals:
                                tree_stack.append(child_node)
                else:
                    return False, None
            else:
                return False, None

        return False, None


if __name__ == "__main__":
    grammar = Grammar()
    grammar.load_from_file("tests/grammar_test1.txt")

    lexer = Lexer(grammar)
    tokens = [tok[0] for tok in lexer.tokenize("( ( a + b ) * r ) + ( a * g )")]

    dpda = DPDA.build_from_parsing_table(grammar)

    print(tokens)
    # print(dpda.transitions)
    # for (state, input_symbol, stack_top), (new_state, new_stack) in dpda.transitions.items():
    #     print(f"({state}, {input_symbol}, {stack_top}) -> ({new_state}, {new_stack})")

    result = dpda.simulate(tokens)
    print("Accepted ✅" if result else "Rejected ❌")
