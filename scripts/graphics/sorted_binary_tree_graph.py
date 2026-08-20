import networkx as nx
import matplotlib.pyplot as plt


ARRAY = list(range(1, 25))


class TreeNode:
    value: int
    left: None | TreeNode
    right: None | TreeNode

    def __init__(self, value: int, left: None | TreeNode = None, right: None | TreeNode = None) -> None:
        self.value = value
        self.left = left
        self.right = right


def main():
    assert (tree := sortedListToTree(ARRAY))
    g = nx.Graph()

    g.add_nodes_from(ARRAY)
    g.add_edges_from(get_edges(tree))
    pos = {n: get_position(n, tree) for n in ARRAY}

    # Draw the tree
    fig, ax = plt.subplots()
    nx.draw(g, pos, ax, with_labels=True, node_size=1_000, font_size=15)
    fig.savefig('binarySearchTree.png', dpi=600)


def sortedListToTree(array: list[int]) -> None | TreeNode:
    match array:
        case []:
            return None
        case [value, ]:
            return TreeNode(value)
        case list():
            halfpoint = len(array) // 2
            lower_half, value, upper_half = array[:halfpoint], array[halfpoint], array[halfpoint+1:]
            return TreeNode(
                value,
                sortedListToTree(lower_half),
                sortedListToTree(upper_half),
            )


def get_position(n: int, tree: TreeNode) -> tuple[float, float]:

    def dfs(
        n: int,
        node: None | TreeNode,
        offset: tuple[float, float] = (0, 0),
        stepsize: float = 1
    ) -> None | tuple[float, float]:
        if not node:
            return None
        if n == node.value:
            return offset
        x_offset, y_offset = offset

        if node.left:
            if (pos := dfs(n, node.left, (x_offset - stepsize, y_offset - 1), stepsize / 2)):
                return pos
        if node.right:
            if (pos := dfs(n, node.right, (x_offset + stepsize, y_offset - 1), stepsize / 2)):
                return pos

        return None

    assert (pos := dfs(n, tree)) is not None
    return pos


def get_edges(tree: TreeNode) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []

    def dfs(node: TreeNode) -> None:
        if node.left:
            edges.append((node.value, node.left.value))
            dfs(node.left)
        if node.right:
            edges.append((node.value, node.right.value))
            dfs(node.right)

    dfs(tree)
    return edges


if __name__ == '__main__':
    main()
    plt.show()
