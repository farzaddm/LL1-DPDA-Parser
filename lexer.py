import re


class Lexer:
    def __init__(self, grammar):
        """
        Initializes the Lexer with a given grammar.
        Args:
            grammar (Grammar): An instance of the Grammar class containing terminal regex definitions.
        """
        self.grammar = grammar
        self.token_regexes = []
        for token_name, pattern in grammar.terminals.items():
            if pattern[-1] == "/" and pattern[0] == "/":
                clean_pattern = pattern[1:-1]
            else:
                clean_pattern = pattern

            compiled_regex = re.compile(clean_pattern)
            self.token_regexes.append((token_name, compiled_regex))

    def tokenize(self, input_string):
        """
        Tokenizes the input string into a list of (token_type, value) pairs.

        Args:
            input_string (str): The raw input string to tokenize.

        Returns:
            list: A list of (token_type, value) tuples.

        Raises:
            ValueError: If an unknown sequence is encountered.
        """
        tokens = []
        inputs = input_string.strip().split()

        for char in inputs:
            match_found = False
            for token_name, pattern in self.token_regexes:
                if pattern.fullmatch(char):
                    tokens.append((token_name, char))
                    match_found = True
                    break
            if not match_found:
                raise ValueError(f"Unrecognized token: {char}")

        return tokens
