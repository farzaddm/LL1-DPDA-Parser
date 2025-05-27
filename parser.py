from visualizer import ParseTreeNode


def parse_input(input_tokens, grammar, table, start_symbol):
    """
    Parses the input tokens using LL(1) parsing table, builds the parse tree and returns its root node.

    Args:
        input_tokens (list): List of input tokens (strings) to parse.
        grammar (Grammar): An instance of the Grammar class.
        table (dict): The LL(1) parsing table.
        start_symbol (str): The start symbol of the grammar.

    Returns:
        ParseTreeNode: Root node of the constructed parse tree.
    """

    # Add the end marker to input tokens
    input_tokens.append("$")

    # Initialize the parsing stack with end marker and start symbol
    stack = ["$", start_symbol]

    # Root node for the parse tree
    root = ParseTreeNode(symbol=start_symbol, node_id=start_symbol)
    node_stack = [root]  # Stack to track tree nodes corresponding to parser stack symbols

    # Input pointer
    index = 0

    while stack:
        top = stack.pop()
        current_node = node_stack.pop()
        current_token = input_tokens[index]

        if top == "$" and current_token == "$":
            # Parsing successfully finished
            print("Parsing complete!")
            break

        elif top in grammar.terminals or top == "$":
            # Terminal or end marker
            if top == current_token:
                # Match found — move to next input token
                index += 1
            else:
                raise ValueError(f"Syntax error: expected {top}, found {current_token}")

        elif top in grammar.non_terminals:
            # Non-terminal
            key = (top, current_token)
            if key not in table:
                raise ValueError(f"No rule for {top} with input {current_token}")

            production = table[key]

            if production == ["ε"]:
                # Epsilon production — add epsilon as child
                epsilon_node = ParseTreeNode(symbol="ε", node_id="epsilon")
                current_node.add_child(epsilon_node)
                continue

            # Push production symbols to the stack in reverse order
            for symbol in reversed(production):
                stack.append(symbol)

            # Create and push corresponding child nodes to the node stack
            for symbol in production:
                child_node = ParseTreeNode(symbol=symbol, node_id=symbol)
                current_node.add_child(child_node)
                node_stack.append(child_node)

        else:
            raise ValueError(f"Unknown symbol on stack: {top}")

    if stack or index != len(input_tokens) - 1:
        raise ValueError("Parsing did not finish cleanly — possible unmatched symbols.")

    return root
