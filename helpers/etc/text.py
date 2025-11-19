def text(node):
    return node.get_text(" ", strip=True) if node else None