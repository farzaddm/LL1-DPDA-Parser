import matplotlib.pyplot as plt
import networkx as nx

class ParseTreeNode:
    def __init__(self, symbol, children=None, node_id=None):
        self.symbol = symbol
        self.children = children or []
        self.node_id = node_id

    def add_child(self, child_node):
        self.children.append(child_node)

# ساخت درخت تستی
def make_sample_tree():
    root = ParseTreeNode("E", node_id=100)

    t1 = ParseTreeNode("T", node_id=200)
    plus = ParseTreeNode("+", node_id=300)
    t2 = ParseTreeNode("T", node_id=200)  # همون node_id با t1

    a = ParseTreeNode("a", node_id=400)
    b = ParseTreeNode("b", node_id=500)

    t1.add_child(a)
    t2.add_child(b)

    root.add_child(t1)
    root.add_child(plus)
    root.add_child(t2)

    return root

# تبدیل درخت به گراف
def build_graph_from_tree(node, graph, parent=None, pos=None, depth=0, x=0):
    if pos is None:
        pos = {}
    node_label = f"{node.symbol}\n(id={node.node_id})"
    graph.add_node(node_label, node_id=node.node_id)
    pos[node_label] = (x, -depth)
    if parent:
        graph.add_edge(parent, node_label)
    width = 1
    child_x = x - width / 2
    for child in node.children:
        build_graph_from_tree(child, graph, node_label, pos, depth + 1, child_x)
        child_x += width / len(node.children) if node.children else width
    return pos

# رسم و تعامل
def draw_interactive_tree(root):
    G = nx.DiGraph()
    pos = build_graph_from_tree(root, G)
    fig, ax = plt.subplots(figsize=(10, 6))

    def draw(highlight_ids=None):
        ax.clear()
        node_colors = []
        for node in G.nodes(data=True):
            if highlight_ids and node[1]["node_id"] in highlight_ids:
                node_colors.append("orange")
            else:
                node_colors.append("lightblue")
        nx.draw(G, pos, with_labels=True, node_color=node_colors, ax=ax, node_size=1500, font_size=10)
        fig.canvas.draw()

    def on_click(event):
        if event.inaxes != ax:
            return
        # پیدا کردن نزدیک‌ترین نود به محل کلیک
        for node, (x, y) in pos.items():
            dx = event.xdata - x
            dy = event.ydata - y
            dist = dx*dx + dy*dy
            if dist < 0.1:  # تقریباً نزدیک بود
                clicked_node_id = G.nodes[node]["node_id"]
                same_ids = [d["node_id"] for n, d in G.nodes(data=True) if d["node_id"] == clicked_node_id]
                draw(highlight_ids=same_ids)
                print(f"Clicked node ID: {clicked_node_id}")
                break

    draw()
    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.title("Parse Tree (click a node to highlight matching node_ids)")
    plt.show()

# اجرا
if __name__ == "__main__":
    root = make_sample_tree()
    draw_interactive_tree(root)
