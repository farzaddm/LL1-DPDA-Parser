import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import uuid
import math
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
            symbol (str): The symbol associated with this node (e.g., a grammar rule, a token).
            children (list, optional): A list of child ParseTreeNode objects. Defaults to an empty list.
            node_id (str, optional): A unique identifier for this node. If None, a unique ID will be assigned automatically when building the graph.
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
    It calculates node positions to create a clear, hierarchical layout and supports
    interactive highlighting and PDF export.
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
        # Sum of the widths of the sub-trees
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

        unique_id = str(uuid.uuid4())  # Generate a unique ID for the NetworkX node to avoid conflicts.
        label = f"{node.symbol}\n(id={node.node_id})"  # Create a display label for the node, including its symbol and ID.
        self.graph.add_node(unique_id, node_id=node.node_id, label=label)  # Add the node to the NetworkX graph.
        self.positions[unique_id] = (
            x_center,
            -depth,
        )  # Store its calculated (x, y) position. Y-coordinates are negative for top-down drawing.
        self.node_labels[unique_id] = label  # Store its display label.

        if parent:
            self.graph.add_edge(parent, unique_id)  # Add a directed edge from the parent to the current node.

        # Place children in order from x_start with the width assigned to each child
        current_x = x_start
        for child in node.children:
            child_width = self._subtree_widths[child]
            # Recursively call _build_graph for each child, adjusting their x_start and increasing depth.
            self._build_graph(child, parent=unique_id, depth=depth + 1, x_start=current_x)
            current_x += child_width
            
    def _get_scaling_parameters(self):
        """
        Computes dynamic scaling for figure size, node size, and font size based on graph size.
        Returns:
            tuple: (figsize, node_size, font_size)
        """
        num_nodes = self.graph.number_of_nodes()
        max_depth = max(-y for _, y in self.positions.values())

        # عرض و ارتفاع شکل براساس اندازه درخت
        width = max(12, min(0.5 * num_nodes, 100))
        height = max(7, min(1.5 * max_depth, 60))

        # اندازه نود و فونت به شکل معکوس با تعداد نود تنظیم می‌شود
        node_size = max(500, 2500 - (num_nodes * 20))
        font_size = max(5, 14 - (num_nodes // 10))

        return (width, height), node_size, font_size


    def show_tree(self):
        """
        Displays the parse tree with adaptive scaling for large graphs.
        """
        figsize, node_size, font_size = self._get_scaling_parameters()
        fig, ax = plt.subplots(figsize=figsize)

        def _draw(highlight_ids=None):
            ax.clear()
            node_colors = [
                "orange" if self.graph.nodes[n]["node_id"] in (highlight_ids or []) else "lightblue"
                for n in self.graph.nodes
            ]
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
            for node, (x, y) in self.positions.items():
                dx = event.xdata - x
                dy = event.ydata - y
                if dx * dx + dy * dy < 0.1:
                    clicked_id = self.graph.nodes[node]["node_id"]
                    _draw(highlight_ids=[clicked_id])
                    print(f"Clicked node ID: {clicked_id}")
                    break

        _draw()
        fig.canvas.mpl_connect("button_press_event", _on_click)
        plt.title("Parse Tree - Click to Highlight Same Node IDs")
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



