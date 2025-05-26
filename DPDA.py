class DPDA:
    """
    Represents a Deterministic Pushdown Automaton (DPDA).

    A DPDA is a type of automaton that uses a stack in addition to its states
    to recognize a context-free language. It is "deterministic" because for
    any given state, input symbol, and stack top symbol, there is at most
    one possible transition.
    """

    def __init__(self, states, input_alphabet, stack_alphabet, transitions, start_state, start_stack_symbol, accept_states):
        """
        Initializes a DPDA.

        Args:
            states (set): A finite set of states.
            input_alphabet (set): A finite set of input symbols (the alphabet).
            stack_alphabet (set): A finite set of stack symbols.
            transitions (dict): A dictionary representing the transition function.
                                Keys are (current_state, input_symbol, stack_top_symbol) tuples,
                                and values are (next_state, symbols_to_push_onto_stack) tuples.
                                An input_symbol of None represents an epsilon transition.
                                An empty tuple for symbols_to_push_onto_stack means pop the top symbol
                                without pushing anything new.
            start_state (str): The initial state of the DPDA.
            start_stack_symbol (str): The initial symbol on the stack.
            accept_states (set): A set of states that are considered accepting states.
        """
        self.states = states
        self.input_alphabet = input_alphabet
        self.stack_alphabet = stack_alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.start_stack_symbol = start_stack_symbol
        self.accept_states = accept_states

    def simulate(self, input_string):
        """
        Simulates the DPDA's operation on a given input string.

        The simulation proceeds step by step, attempting to apply transitions
        based on the current state, the current input symbol, and the top
        of the stack. Epsilon transitions (transitions on an empty input symbol)
        are prioritized if no regular input transition is available.

        Args:
            input_string (str): The string to be processed by the DPDA.

        Returns:
            bool: True if the input string is accepted by the DPDA, False otherwise.
                An input string is accepted if the DPDA ends in an accept state
                and has consumed the entire input string.
        """
        stack = [self.start_stack_symbol]  # Initialize the stack with the start symbol
        current_state = self.start_state  # Set the initial state
        position = 0  # Keep track of the current position in the input string

        while True:
            # Determine the current input symbol (or None if at the end of the string)
            current_input = input_string[position] if position < len(input_string) else None
            # Get the top symbol of the stack (or None if the stack is empty)
            stack_top = stack[-1] if stack else None

            # Form the key for a regular transition (current_state, current_input, stack_top)
            transition_key = (current_state, current_input, stack_top)
            # Form the key for an epsilon transition (current_state, None, stack_top)
            epsilon_key = (current_state, None, stack_top)

            if transition_key in self.transitions:
                # If a regular transition exists for the current configuration
                next_state, push_symbols = self.transitions[transition_key]
                current_state = next_state  # Update the current state
                stack.pop()  # Pop the top symbol from the stack
                stack.extend(reversed(push_symbols))  # Push new symbols onto the stack (reversed to maintain order)
                position += 1  # Move to the next input symbol
            elif epsilon_key in self.transitions:
                # If an epsilon transition exists (and no regular transition was found)
                next_state, push_symbols = self.transitions[epsilon_key]
                current_state = next_state  # Update the current state
                stack.pop()  # Pop the top symbol from the stack
                stack.extend(reversed(push_symbols))  # Push new symbols onto the stack
                # Note: position does not increment for epsilon transitions as no input is consumed
            else:
                # If no valid transition is found, the simulation halts
                break

        # An input string is accepted if the DPDA is in an accept state AND
        # it has processed all input symbols (position - 1 == len(input_string)
        # accounts for the fact that position is incremented *after* consuming the last symbol).
        return current_state in self.accept_states and position - 1 == len(input_string)


if __name__ == "__main__":
    # test_dpda = DPDA( # a^n b^n
    #     states={"q0", "q1", "q2"},
    #     input_alphabet={"a", "b"},
    #     stack_alphabet={"Z", "A"},
    #     transitions={
    #         ("q0", "a", "Z"): ("q0", ["A", "Z"]),
    #         ("q0", "a", "A"): ("q0", ["A", "A"]),
    #         ("q0", "b", "A"): ("q1", []),
    #         ("q1", "b", "A"): ("q1", []),
    #         ("q1", None, "Z"): ("q2", ["Z"]),  # ε-move برای پذیرش
    #     },
    #     start_state="q0",
    #     start_stack_symbol="Z",
    #     accept_states={"q2"},
    # )

    # print(test_dpda.simulate("ab"))  # True
    # print(test_dpda.simulate("aabb"))  # True
    # print(test_dpda.simulate("aaabbb"))  # True
    # print(test_dpda.simulate("aab"))  # False
    # print(test_dpda.simulate("abb"))  # False
    # ----------------------------------------------------
    # dpda_ac_equal = DPDA( # a^n b^m c^n
    # states={"q0", "q1", "q2"},
    # input_alphabet={"a", "b", "c"},
    # stack_alphabet={"Z", "A"},
    # transitions={
    #     ("q0", "a", "Z"): ("q0", ["A", "Z"]),
    #     ("q0", "a", "A"): ("q0", ["A", "A"]),
    #     ("q0", "b", "A"): ("q0", ["A"]),  # b → پشته تغییر نمی‌کنه
    #     ("q0", "b", "Z"): ("q0", ["Z"]),
    #     ("q0", "c", "A"): ("q1", []),
    #     ("q1", "c", "A"): ("q1", []),
    #     ("q1", None, "Z"): ("q2", ["Z"]),
    # },
    # start_state="q0",
    # start_stack_symbol="Z",
    # accept_states={"q2"}
    # )

    # print(dpda_ac_equal.simulate("ac")) # True
    # print(dpda_ac_equal.simulate("aaacc")) # False
    # print(dpda_ac_equal.simulate("b")) # False
    # print(dpda_ac_equal.simulate("abbbbc")) # True
    # print(dpda_ac_equal.simulate("aabcbc")) # False
    # print(dpda_ac_equal.simulate("aaabccc")) # True
    # print(dpda_ac_equal.simulate("")) # False
    # ----------------------------------------------------
    pass
