import matplotlib.pyplot as plt
import networkx as nx

class ParseTreeNode:
    def __init__(self, symbol, children=None, node_id=None):
        self.symbol = symbol
        self.children = children or []
        self.node_id = node_id

    def add_child(self, child_node):
        self.children.append(child_node)

class ParseTreeVisualizer:
    def __init__(self, root: ParseTreeNode):
        self.root = root
        self.graph = nx.DiGraph()
        self.positions = {}
        self._build_graph(self.root)

    def _build_graph(self, node, parent=None, depth=0, x=0, width=1):
        label = f"{node.symbol}\n(id={node.node_id})"
        self.graph.add_node(label, node_id=node.node_id)
        self.positions[label] = (x, -depth)
        if parent:
            self.graph.add_edge(parent, label)

        child_x = x - width / 2
        for child in node.children:
            self._build_graph(child, parent=label, depth=depth + 1, x=child_x, width=width / max(len(node.children), 1))
            child_x += width / max(len(node.children), 1)

    def show_tree(self):
        fig, ax = plt.subplots(figsize=(10, 6))

        def _draw(highlight_ids=None):
            ax.clear()
            node_colors = [
                "orange" if self.graph.nodes[n]["node_id"] in (highlight_ids or []) else "lightblue"
                for n in self.graph.nodes
            ]
            nx.draw(
                self.graph, self.positions,
                with_labels=True,
                node_color=node_colors,
                ax=ax,
                node_size=1500,
                font_size=10
            )
            fig.canvas.draw()

        def _on_click(event):
            if event.inaxes != ax:
                return
            for node, (x, y) in self.positions.items():
                dx = event.xdata - x
                dy = event.ydata - y
                if dx * dx + dy * dy < 0.1:  # threshold for "near click"
                    clicked_id = self.graph.nodes[node]["node_id"]
                    matching_ids = [d["node_id"] for n, d in self.graph.nodes(data=True) if d["node_id"] == clicked_id]
                    _draw(highlight_ids=matching_ids)
                    print(f"Clicked node ID: {clicked_id}")
                    break

        _draw()
        fig.canvas.mpl_connect("button_press_event", _on_click)
        plt.title("Parse Tree - Click to Highlight Same Node IDs")
        plt.show()

    def export_pdf(self, filename="parse_tree.pdf"):
        plt.figure(figsize=(10, 6))
        nx.draw(
            self.graph,
            self.positions,
            with_labels=True,
            node_color="lightblue",
            node_size=1500,
            font_size=10
        )
        plt.title("Parse Tree")
        plt.savefig(filename)
        print(f"Parse tree saved as: {filename}")
