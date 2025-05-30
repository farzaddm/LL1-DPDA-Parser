import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import uuid
import os


class ParseTreeNode:
    """
    Represents a single node in the parse tree.
    Each node stores its symbol, a list of its children, and a unique ID.
    """

    def __init__(self, symbol, children=None, node_id=None):
        """
        Initializes a ParseTreeNode.

        Args:
            symbol (str): The symbol associated with this node.
            children (list, optional): A list of child ParseTreeNode objects. Defaults to an empty list.
            node_id (str, optional): A unique identifier for this node.
        """
        self.symbol = symbol
        self.children = children or []
        self.node_id = node_id

    def add_child(self, child_node):
        """
        Adds a child node to the current node.

        Args:
            child_node (ParseTreeNode): The ParseTreeNode to add as a child.
        """
        self.children.append(child_node)


class ParseTreeVisualizer:
    """
    Handles the visualization and display of a parse tree using matplotlib and networkx.
    Includes support for exporting the tree to a PDF file.
    """

    def __init__(self, root: ParseTreeNode):
        """
        Initializes the ParseTreeVisualizer.

        Args:
            root (ParseTreeNode): The root ParseTreeNode of the tree to visualize.
        """
        self.root = root
        self.graph = nx.DiGraph()
        self.positions = {}
        self.node_labels = {}
        self._subtree_widths = {}
        self._calculate_subtree_widths(self.root)
        self._build_graph(self.root)

    def _calculate_subtree_widths(self, node):
        """
        Recursively calculates the width of each subtree.

        The width of a leaf node is 1. The width of an internal node is the sum of the
        widths of its children's subtrees. This helps in horizontally spacing nodes.

        Args:
            node (ParseTreeNode): The current ParseTreeNode.

        Returns:
            int: The calculated width of the subtree rooted at this node.
        """

        if not node.children:
            self._subtree_widths[node] = 1
            return 1

        width = 0
        for child in node.children:
            width += self._calculate_subtree_widths(child)
        self._subtree_widths[node] = width
        return width

    def _build_graph(self, node, parent=None, depth=0, x_start=0):
        """
        Recursively builds the NetworkX graph and calculates node positions for visualization.

        Nodes are positioned such that children are spread out beneath their parent,
        centered relative to their subtree's total width.

        Args:
            node (ParseTreeNode): The current ParseTreeNode to process.
            parent (str, optional): The unique ID of the parent node in the NetworkX graph. None for the root node.
            depth (int, optional): The current depth of the node in the tree, used for vertical positioning (y-coordinate). Defaults to 0.
            x_start (float, optional): The starting x-coordinate for placing the subtree rooted at this node. Defaults to 0.
        """
        # The X position is based on the center of the tree.
        width = self._subtree_widths[node]
        x_center = x_start + width / 2

        unique_key = str(uuid.uuid4())
        node_id = node.symbol
        label = node.symbol

        self.graph.add_node(unique_key, node_id=node_id, label=label)
        self.positions[unique_key] = (x_center, -depth)
        self.node_labels[unique_key] = label

        if parent:
            self.graph.add_edge(parent, unique_key)

        current_x = x_start
        for child in node.children:
            child_width = self._subtree_widths[child]
            self._build_graph(child, parent=unique_key, depth=depth + 1, x_start=current_x)
            current_x += child_width

    def _get_scaling_parameters(self):
        """
        Computes dynamic scaling for figure size, node size, and font size based on graph size.
        Returns:
            tuple: (figsize, node_size, font_size)
        """
        num_nodes = self.graph.number_of_nodes()
        max_depth = max(-y for _, y in self.positions.values())
        width = max(12, min(0.5 * num_nodes, 100))
        height = max(7, min(1.5 * max_depth, 60))
        node_size = max(500, 2500 - (num_nodes * 20))
        font_size = max(5, 14 - (num_nodes // 10))

        return (width, height), node_size, font_size

    def _rename_in_scope(self, node, target_symbol, new_label, clicked_node_key):
        """
        Performs scope-aware renaming of nodes in the parse tree.

        When a node with the target_symbol is clicked, this function traverses the tree
        and renames only the nodes with the same symbol that are in the same scope
        (or nested within that scope) using a stack-based mechanism to track scope boundaries.
        Scopes are opened with LEFT_PAR or LEFT_BRACE and closed with RIGHT_PAR or RIGHT_BRACE.

        Args:
            node (ParseTreeNode): The root of the parse tree.
            target_symbol (str): The symbol to rename (e.g. "ID").
            new_label (str): The new name to assign to the nodes.
            clicked_node_key (str): The unique graph key for the clicked node.
        """
        scope_stack = []
        rename_active = False
        clicked_scope_depth = None

        openers = {"LEFT_PAR": "RIGHT_PAR", "LEFT_BRACE": "RIGHT_BRACE"}
        closers = {"RIGHT_PAR": "LEFT_PAR", "RIGHT_BRACE": "LEFT_BRACE"}
        parse_to_graph = {}

        for graph_node in self.graph.nodes:
            label = self.graph.nodes[graph_node]["label"]
            parse_to_graph.setdefault(label, []).append(graph_node)

        def dfs(current_node, current_key):
            nonlocal rename_active, clicked_scope_depth

            symbol = current_node.symbol

            if symbol in openers:
                scope_stack.append(symbol)
            elif symbol in closers:
                if scope_stack and openers[scope_stack[-1]] == symbol:
                    scope_stack.pop()

            if current_key == clicked_node_key and not rename_active:
                rename_active = True
                clicked_scope_depth = len(scope_stack)

            if rename_active and symbol == target_symbol:
                self.graph.nodes[current_key]["node_id"] = new_label
                self.node_labels[current_key] = new_label

            if rename_active and clicked_scope_depth is not None and len(scope_stack) < clicked_scope_depth:
                rename_active = False

            for child in current_node.children:
                if parse_to_graph.get(child.symbol):
                    next_key = parse_to_graph[child.symbol].pop(0)
                    dfs(child, next_key)

        for graph_node in self.graph.nodes:
            if self.graph.nodes[graph_node]["label"] == node.symbol:
                dfs(node, graph_node)
                break

    def show_tree(self):
        figsize, node_size, font_size = self._get_scaling_parameters()
        fig, ax = plt.subplots(figsize=figsize)

        def _draw(highlight_ids=None):
            ax.clear()
            node_colors = []
            for n in self.graph.nodes:
                if self.graph.nodes[n]["node_id"] in (highlight_ids or []):
                    node_colors.append("orange")
                else:
                    node_colors.append("lightblue")

            nx.draw(
                self.graph,
                self.positions,
                with_labels=True,
                labels=self.node_labels,
                node_color=node_colors,
                ax=ax,
                node_size=node_size,
                font_size=font_size,
            )
            fig.canvas.draw()

        def _on_click(event):
            if event.inaxes != ax:
                return
            for node_key, (x, y) in self.positions.items():
                dx = event.xdata - x
                dy = event.ydata - y
                if dx * dx + dy * dy < 0.1:
                    clicked_id = self.graph.nodes[node_key]["node_id"]
                    print(f"Clicked node group: {clicked_id}")

                    new_label = input(f"Rename all '{clicked_id}' nodes to: ")

                    if new_label:
                        self._rename_in_scope(self.root, clicked_id, new_label, node_key)
                        _draw(highlight_ids=[new_label])
                    break

        _draw()
        fig.canvas.mpl_connect("button_press_event", _on_click)
        plt.title("Parse Tree")
        plt.tight_layout()
        plt.show()

    def export_pdf(self, file_name="parse_tree"):
        """
        Exports the current parse tree to a PDF file with adaptive layout.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{file_name}_{timestamp}.pdf"

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        figsize, node_size, font_size = self._get_scaling_parameters()

        plt.figure(figsize=figsize)
        nx.draw(
            self.graph,
            self.positions,
            labels=self.node_labels,
            with_labels=True,
            node_color="lightblue",
            node_size=node_size,
            font_size=font_size,
        )
        plt.title("Parse Tree")
        plt.tight_layout()
        plt.savefig(filepath)
        print(f"Parse tree saved as: {filepath}")
