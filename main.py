from visualizer import ParseTreeNode, ParseTreeVisualizer

def build_complex_tree():
    # ریشه
    root = ParseTreeNode("E", node_id=1)

    # سطح اول
    t1 = ParseTreeNode("T", node_id=2)
    plus = ParseTreeNode("+", node_id=3)
    t2 = ParseTreeNode("T", node_id=2)  # node_id مشترک با t1

    # سطح دوم
    f1 = ParseTreeNode("F", node_id=4)
    star = ParseTreeNode("*", node_id=5)
    f2 = ParseTreeNode("F", node_id=4)  # همون node_id با f1

    id1 = ParseTreeNode("IDENTIFIER", node_id=100)
    id2 = ParseTreeNode("IDENTIFIER", node_id=100)  # هم‌نام id1
    id3 = ParseTreeNode("IDENTIFIER", node_id=100)  # هم‌نام id1

    # ساخت درخت
    f1.add_child(id1)
    f2.add_child(id2)
    t1.add_child(f1)
    t2.add_child(f2)
    root.add_child(t1)
    root.add_child(plus)
    root.add_child(t2)

    # اضافه کردن یک زیرشاخه دیگر برای آزمایش بیشتر
    star.add_child(id3)
    t2.add_child(star)

    return root

if __name__ == "__main__":
    tree_root = build_complex_tree()
    visualizer = ParseTreeVisualizer(tree_root)
    visualizer.show_tree()
    # visualizer.export_pdf("complex_tree.pdf")
