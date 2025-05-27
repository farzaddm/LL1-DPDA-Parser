from grammar import Grammar
from parser import parse_input
from visualizer import ParseTreeVisualizer


if __name__ == "__main__":
    # List of test grammar files
    grammarTestPaths = [
        "tests/grammar_test1.txt",
        # "tests/grammar_test2.txt",
        # "tests/grammar_test3.txt",
        # "tests/grammar_test4.txt",
        # "tests/grammar_test5.txt"
    ]

    testNum = 1
    for testAddress in grammarTestPaths:
        print("\n===============================")
        print(f"Test {testNum}: {testAddress}:")
        print("===============================")

        # Initialize Grammar object
        grammar = Grammar()

        # Load grammar from file
        grammar.load_from_file(testAddress)

        # Validate grammar (checks for undefined symbols)
        grammar.validate()

        # Print basic grammar info
        print("\nGrammar Info:")
        print("Start symbol:", grammar.start_symbol)
        print("Non-terminals:", grammar.non_terminals)
        print("Terminals:", grammar.terminals)
        print("Productions:")
        for nt, rules in grammar.productions.items():
            for rule in rules:
                print(f"  {nt} -> {rule}")

        # Compute FIRST sets
        grammar.compute_first_sets()
        print("\nFIRST sets:")
        for nt in grammar.non_terminals:
            print(f"FIRST({nt}) = {grammar.first[nt]}")

        # Compute FOLLOW sets
        grammar.compute_follow_sets()
        print("\nFOLLOW sets:")
        for nt in grammar.non_terminals:
            print(f"FOLLOW({nt}) = {grammar.follow[nt]}")

        # Compute LL(1) parsing table
        ll1_table = grammar.compute_ll1_table()
        print("\nLL(1) Parsing Table:")
        print(ll1_table)

        # Example tokenized input for test (this should ideally match your grammar terminals)
        input_tokens = []
        while True:
            token = input("Enter token (or type 'done' to finish): ")
            if token.lower() == 'done':
                break
            input_tokens.append(token)

        if not input_tokens:
            print("No input tokens provided, skipping parse for this grammar.")
            testNum += 1
            continue

        try:
            # Parse the input and build parse tree
            root = parse_input(input_tokens, grammar, ll1_table, grammar.start_symbol)

            # Visualize the parse tree
            visualizer = ParseTreeVisualizer(root)
            visualizer.show_tree()

        except ValueError as e:
            print(f"Parsing error: {e}")

        testNum += 1
