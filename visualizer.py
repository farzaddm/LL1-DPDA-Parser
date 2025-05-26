import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import uuid  # برای تولید شناسه یکتا
import os

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
        self.node_labels = {}
        self._subtree_widths = {}
        self._calculate_subtree_widths(self.root)
        self._build_graph(self.root)

    def _calculate_subtree_widths(self, node):
        # برگ اگر بچه نداشت عرض 1 داره
        if not node.children:
            self._subtree_widths[node] = 1
            return 1
        # جمع عرض زیرشاخه‌ها
        width = 0
        for child in node.children:
            width += self._calculate_subtree_widths(child)
        self._subtree_widths[node] = width
        return width

    def _build_graph(self, node, parent=None, depth=0, x_start=0):
        # موقعیت X بر اساس مرکز زیر درخت قرار میگیره
        width = self._subtree_widths[node]
        x_center = x_start + width / 2

        unique_id = str(uuid.uuid4())
        label = f"{node.symbol}\n(id={node.node_id})"
        self.graph.add_node(unique_id, node_id=node.node_id, label=label)
        self.positions[unique_id] = (x_center, -depth)
        self.node_labels[unique_id] = label

        if parent:
            self.graph.add_edge(parent, unique_id)

        # جایگذاری فرزندان به ترتیب از x_start با عرض اختصاص داده شده به هر فرزند
        current_x = x_start
        for child in node.children:
            child_width = self._subtree_widths[child]
            self._build_graph(child, parent=unique_id, depth=depth + 1, x_start=current_x)
            current_x += child_width

    def show_tree(self):
        fig, ax = plt.subplots(figsize=(12, 7))

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
                if dx * dx + dy * dy < 0.1:
                    clicked_id = self.graph.nodes[node]["node_id"]
                    _draw(highlight_ids=[clicked_id])
                    print(f"Clicked node ID: {clicked_id}")
                    break

        _draw()
        fig.canvas.mpl_connect("button_press_event", _on_click)
        plt.title("Parse Tree - Click to Highlight Same Node IDs")
        plt.show()

    def export_pdf(self, file_name = "parse_tree"):
        # ایجاد نام یکتا بر اساس زمان فعلی
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename = f"{file_name}_{timestamp}.pdf"

        # ساخت مسیر خروجی
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        # ترسیم و ذخیره
        plt.figure(figsize=(12, 7))
        nx.draw(
            self.graph,
            self.positions,
            labels=self.node_labels,
            with_labels=True,
            node_color="lightblue",
            node_size=1500,
            font_size=10
        )
        plt.title("Parse Tree")
        plt.savefig(filepath)
        print(f"Parse tree saved as: {filepath}")
