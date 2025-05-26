from visualizer import ParseTreeNode, ParseTreeVisualizer

def build_complex_tree():
    # ریشه
    root = ParseTreeNode("E", node_id=1)

    # سطح اول
    t1 = ParseTreeNode("T", node_id=2)
    plus = ParseTreeNode("+", node_id=3)
    t2 = ParseTreeNode("T", node_id=2)

    # سطح دوم - T1
    f1 = ParseTreeNode("F", node_id=4)
    t_prime1 = ParseTreeNode("T'", node_id=5)

    # سطح دوم - T2
    f2 = ParseTreeNode("F", node_id=4)
    t_prime2 = ParseTreeNode("T'", node_id=5)

    # IDENTIFIER nodes (مشترک برای تست)
    id1 = ParseTreeNode("IDENTIFIER", node_id=100)
    id2 = ParseTreeNode("IDENTIFIER", node_id=100)
    id3 = ParseTreeNode("IDENTIFIER", node_id=100)
    id4 = ParseTreeNode("IDENTIFIER", node_id=100)
    id5 = ParseTreeNode("IDENTIFIER", node_id=100)

    # اضافه کردن چند literal و par
    literal1 = ParseTreeNode("LITERAL", node_id=101)
    literal2 = ParseTreeNode("LITERAL", node_id=101)

    left_par = ParseTreeNode("(", node_id=6)
    right_par = ParseTreeNode(")", node_id=7)

    # اضافه کردن گره های بیشتر برای شبیه‌سازی عبارات پیچیده
    e_sub = ParseTreeNode("E", node_id=1)
    t_sub = ParseTreeNode("T", node_id=2)
    f_sub = ParseTreeNode("F", node_id=4)
    id_sub = ParseTreeNode("IDENTIFIER", node_id=100)

    # ساخت شاخه های داخلی
    f1.add_child(id1)
    t_prime1.add_child(ParseTreeNode("eps", node_id=0))
    t1.add_child(f1)
    t1.add_child(t_prime1)

    f2.add_child(id2)
    t_prime2.add_child(ParseTreeNode("*", node_id=8))
    t_prime2.add_child(ParseTreeNode("F", children=[id3], node_id=4))
    t2.add_child(f2)
    t2.add_child(t_prime2)

    # شاخه وسطی
    e_sub.add_child(t_sub)
    t_sub.add_child(f_sub)
    f_sub.add_child(id_sub)

    # بخشی با پرانتز
    par_expr = ParseTreeNode("F", node_id=4)
    par_expr.add_child(left_par)
    par_expr.add_child(e_sub)
    par_expr.add_child(right_par)

    # ساخت شاخه اصلی
    root.add_child(t1)
    root.add_child(plus)
    root.add_child(t2)
    root.add_child(ParseTreeNode("+", node_id=3))
    root.add_child(par_expr)

    # افزودن نودهای بیشتر برای رسیدن به حداقل 25
    root.add_child(literal1)
    root.add_child(literal2)
    root.add_child(id4)
    root.add_child(id5)

    return root


if __name__ == "__main__":
    tree_root = build_complex_tree()
    visualizer = ParseTreeVisualizer(tree_root)
    visualizer.show_tree()
    visualizer.export_pdf()
