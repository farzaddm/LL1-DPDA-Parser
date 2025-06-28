from lexer import Lexer
from dpda import DPDA
from visualizer import ParseTreeVisualizer
from grammar import Grammar

tests = [
    "tests/grammar_test1.txt",
    # "tests/grammar_test2.txt",
]

inputs = [
    "tests/input_test1.txt",
    # "tests/input_test2.txt",
]

if __name__ == "__main__":
    grammar = Grammar()
    grammar.load_from_file(tests[0])
    grammar.validate()

    lexer = Lexer(grammar)
    with open(inputs[0], "r") as f:
        code = f.read()

    tokens = [tok[0] for tok in lexer.tokenize(code)]
    dpda = DPDA.build_from_parsing_table(grammar)

    result, parse_tree_root = dpda.simulate(tokens)
    print("Accepted" if result else "Rejected")

    if result:
        visualizer = ParseTreeVisualizer(parse_tree_root)
        visualizer.show_tree()
        visualizer.export_pdf()
