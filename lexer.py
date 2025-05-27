# lexer.py

import re

class Lexer:
    def __init__(self, grammar):
        """
        Initializes the Lexer with a given grammar.
        Args:
            grammar (Grammar): An instance of the Grammar class containing terminal regex definitions.
        """
        self.grammar = grammar
        self.token_regexes = [
            (token_name, re.compile(pattern.strip("/")))  # Remove the surrounding slashes
            for token_name, pattern in grammar.terminals.items()
        ]

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
        position = 0
        input_string = input_string.strip()

        while position < len(input_string):
            match_found = False

            # Ignore whitespaces
            if input_string[position].isspace():
                position += 1
                continue

            for token_name, pattern in self.token_regexes:
                match = pattern.match(input_string, position)
                if match:
                    tokens.append((token_name, match.group()))
                    position = match.end()
                    match_found = True
                    break

            if not match_found:
                raise ValueError(f"Unexpected character at position {position}: '{input_string[position]}'")

        return tokens
