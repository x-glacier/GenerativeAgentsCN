"""generative_agents.memory.spatial"""

import random

from modules import utils


class Spatial:
    def __init__(self, tree, address=None):
        self.tree = tree
        self.address = address or {}
        if "sleeping" not in self.address and "睡觉" not in self.address and "living_area" in self.address:
            # self.address["sleeping"] = self.address["living_area"] + ["bed"]
            self.address["睡觉"] = self.address["living_area"] + ["床"]

    def __str__(self):
        return utils.dump_dict(self.tree)

    def add_leaf(self, address):
        def _add_leaf(left_address, tree):
            if len(left_address) == 2:
                leaves = tree.setdefault(left_address[0], [])
                if left_address[1] not in leaves:
                    leaves.append(left_address[1])
            elif len(left_address) > 2:
                _add_leaf(left_address[1:], tree.setdefault(left_address[0], {}))

        _add_leaf(address, self.tree)

    def find_address(self, hint, as_list=True):
        address = []
        for key, path in self.address.items():
            if key in hint:
                address = path
                break
        if as_list:
            return address
        return ":".join(address)

    def get_leaves(self, address):
        def _get_tree(address, tree):
            if not address:
                if isinstance(tree, dict):
                    return list(tree.keys())
                return tree
            if address[0] not in tree:
                return []
            return _get_tree(address[1:], tree[address[0]])

        return _get_tree(address, self.tree)

    def random_address(self):
        address, tree = [], self.tree
        while isinstance(tree, dict):
            roots = [r for r in tree if len(tree[r]) > 0]
            address.append(random.choice(roots))
            tree = tree[address[-1]]
        address.append(random.choice(tree))
        return address
