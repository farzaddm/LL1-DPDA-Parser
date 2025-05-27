from lexer import Lexer
from DPDA import DPDA
from visualizer import ParseTreeVisualizer
from grammar import Grammar

# List of test grammar files
grammarTestPaths = [
    "tests/grammar_test1.txt",
    # "tests/grammar_test2.txt",
    # "tests/grammar_test3.txt",
    # "tests/grammar_test4.txt",
    # "tests/grammar_test5.txt"
]

if __name__ == "__main__":

    testNum = 1
    for testAddress in grammarTestPaths:
        print("\n===============================")
        print(f"Test {testNum}: {testAddress}:")
        print("===============================")

        grammar = Grammar()
        grammar.load_from_file(testAddress)
        grammar.validate()
        
        lexer = Lexer(grammar)
        tokens = [tok[0] for tok in lexer.tokenize(input("enter your string : "))]
        
        print(tokens)

        dpda = DPDA.build_from_parsing_table(grammar)
        
        result, parse_tree_root = dpda.simulate(tokens)
        print("Accepted ✅" if result else "Rejected ❌")

        if result:
            visualizer = ParseTreeVisualizer(parse_tree_root)
            visualizer.show_tree()

        testNum += 1

        # #! Print basic grammar info
        # print("\nGrammar Info:")
        # print("Start symbol:", grammar.start_symbol)  # str: The starting non-terminal
        # print("Non-terminals:", grammar.non_terminals)  # set[str]: All non-terminals
        # print("Terminals:", grammar.terminals)  # dict[str, str]: Terminals and their regex patterns
        # print("Productions:")

        # #! Print all productions (rules)
        # for nt, rules in grammar.productions.items():  # grammar.productions: dict[str, list[list[str]]]
        #     for rule in rules:
        #         print(f"  {nt} -> {rule}")  # Each rule is a list[str] (sequence of symbols)

        # #! Compute FIRST sets (used for LL(1) parsing)
        # grammar.compute_first_sets()  # Modifies grammar.first: dict[str, set[str]]
        # print("\nFIRST sets:")
        # for nt in grammar.non_terminals:
        #     print(f"FIRST({nt}) = {grammar.first[nt]}")  # FIRST[nt] = set of possible first terminals

        # #! Compute FOLLOW sets (used for LL(1) parsing)
        # grammar.compute_follow_sets()  # Modifies grammar.follow: dict[str, set[str]]
        # print("\nFOLLOW sets:")
        # for nt in grammar.non_terminals:
        #     print(f"FOLLOW({nt}) = {grammar.follow[nt]}")  # FOLLOW[nt] = set of terminals that can appear after nt

        # #! Compute LL(1) parsing table
        # # Returns: dict[str, dict[str, list[str]]] (e.g., { "Expr": { "PLUS": ["Term", "PLUS", "Expr"], ... } })
        # ll1_table = grammar.compute_ll1_table()
        # print("\nLL(1) Parsing Table:")
        # print(ll1_table)  # Example: ll1_table["Expr"]["PLUS"] = ["Term", "PLUS", "Expr"]
