class ParseTreeNode:
    def __init__(self, symbol, children=None, node_id=None):
        self.symbol = symbol
        self.children = children or []
        self.node_id = node_id  # برای مرحله ۵



def rename_nodes(root: ParseTreeNode, target_id: str, new_name: str):
    # تمام گره‌هایی که با target_id یا symbol برابرند رو پیدا کن و تغییر بده
    pass
