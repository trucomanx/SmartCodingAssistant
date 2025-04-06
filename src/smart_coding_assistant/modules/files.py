#!/usr/bin/python3

import os

def directory_structure(path):
    """
    Given a path, returns a nested dictionary representing the directory structure.

    Args:
        path (str): Path to the root directory.

    Returns:
        dict: Nested dictionary representing the file/folder structure.
    """
    def build_tree(current_path):
        tree = {}
        with os.scandir(current_path) as it:
            for entry in it:
                if entry.is_dir(follow_symlinks=False):
                    tree[entry.name] = build_tree(entry.path)
                else:
                    tree[entry.name] = None
        return tree

    base_name = os.path.basename(os.path.abspath(path))
    return {base_name: build_tree(path)}

if __name__ == "__main__":
    import json

    estrutura = directory_structure("../../")
    print(json.dumps(estrutura, indent=4))  # Para visualizar melhor

