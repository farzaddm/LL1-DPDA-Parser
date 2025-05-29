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
        self.positions = {}  # Dictionary to store the (x, y) coordinates for each node in the plot.
        self.node_labels = {}
        self._subtree_widths = {}  # Private dictionary to store the calculated width of each subtree, used for horizontal positioning.
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

        unique_key = str(uuid.uuid4())  # unique node key for NetworkX internal
        node_id = node.symbol  # shared ID for grouping nodes of same symbol
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
                        for n in self.graph.nodes:
                            if self.graph.nodes[n]["node_id"] == clicked_id:
                                self.graph.nodes[n]["node_id"] = new_label
                                self.node_labels[n] = new_label

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
