"""
Assignment 2: Trees for Treemap

=== CSC148 Winter 2024 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2024 Bogdan Simion, David Liu, Diane Horton,
                   Haocheng Hu, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this asignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: Optional[str]
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._expanded = True

        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        self.data_size = data_size
        self._sum_size()

        for tree in self._subtrees:
            tree._parent_tree = self

    def _sum_size(self) -> int:
        """Return the total data_size of this tree
        """
        if self.is_empty():
            self.data_size = 0
        elif not self._subtrees:
            pass
        else:
            total = 0
            for tree in self._subtrees:
                total += tree._sum_size()
            self.data_size = total

        return self.data_size

    def get_parent(self) -> Optional[TMTree]:
        """Returns the parent of this tree.
        """
        return self._parent_tree

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        if self.is_empty() or self.data_size == 0:
            return

        if self._subtrees and self._expanded:
            self.rect = rect
            x, y, width, height = rect

            # Divide the rectangles horizontally or vertically based on the aspect ratio
            if width > height:
                total_data_size = sum(subtree.data_size for subtree in self._subtrees)
                nx = x

                for subtree in self._subtrees:
                    new_width = math.floor(width * (subtree.data_size / total_data_size))
                    if subtree == self._subtrees[-1] and (nx + new_width - x) != width:
                        new_width = (width + x) - nx
                    subtree.rect = (nx, y, new_width, height)
                    nx += new_width
            else:
                total_data_size = sum(subtree.data_size for subtree in self._subtrees)
                ny = y

                for subtree in self._subtrees:
                    new_height = math.floor(height * (subtree.data_size / total_data_size))
                    if subtree == self._subtrees[-1] and (ny + new_height - y) != height:
                        new_height = (height + y) - ny
                    subtree.rect = (x, ny, width, new_height)
                    ny += new_height

            # Update rectangles recursively for each subtree
            for tree in self._subtrees:
                tree.update_rectangles(tree.rect)

        elif not self._subtrees or not self._expanded:
            self.rect = rect

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
    Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        rectangles = []

        def traverse(tree: TMTree) -> None:
            if tree._expanded and not tree.is_empty():
                if tree._subtrees:
                    for subtree in tree._subtrees:
                        traverse(subtree)
                else:
                    rectangles.append((tree.rect, tree._colour))

        traverse(self)
        return rectangles

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        if self.rect is None:
            return None

        x, y = pos
        lx, ly, ux, uy = self.rect

        if lx <= x <= lx + ux and ly <= y <= ly + uy:
            if self._subtrees == [] or not self._expanded:
                return self
            else:
                matches = [tree.get_tree_at_position(pos) for tree in self._subtrees]
                matches = [match for match in matches if match is not None]

                if matches:
                    closest = min(matches, key=lambda match: (match.rect[0], match.rect[1]))
                    return closest
                else:
                    return None
        else:
            return None

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        return self._sum_size()

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        if not self._subtrees and destination._subtrees:
            self._parent_tree._subtrees.remove(self)
            self._parent_tree.update_data_sizes()

            destination._subtrees.append(self)
            destination.update_data_sizes()

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """
        if self._subtrees or self.is_empty():
            return

        absolute_factor = abs(factor)
        change = math.ceil(self.data_size * absolute_factor)
        change_direction = 1 if factor >= 0 else -1
        change = change_direction * change

        self.data_size += change

    def expand(self) -> None:
        """Expand this tree, so that it's subtrees are shown.
        If this tree is expanded, or a leaf, do nothing.
        """
        if not self._expanded or not self._subtrees:
            self._expanded = True
            self.update_rectangles(self.rect)

    def expand_all(self) -> None:
        """Expand this tree, and all trees within it.
        If this tree is exanded, or a leaf, do nothing.
        """
        # Create a stack for iterative traversal
        stack = [self]

        # Iterate through the stack
        while stack:
            current = stack.pop()

            # If the current tree is not expanded and has subtrees, expand it
            if not current._expanded and current._subtrees:
                current._expanded = True
                current.update_rectangles(current.rect)

                # Add all subtrees of the current tree to the stack
                stack.extend(current._subtrees)

    def collapse(self) -> None:
        """Collapse the selected group of trees."""
        if self._subtrees:  # Check if the tree has any subtrees
            self.collapse_subtrees()

    def collapse_subtrees(self) -> None:
        """Collapse all subtrees of this tree.
        """
        self._expanded = False
        for subtree in self._subtrees:
            subtree.collapse_subtrees()

    def collapse_all(self) -> None:
        """Collapse every tree contained in the root of this tree.
        """
        root = self
        while root._parent_tree is not None:
            root = root._parent_tree
        root.collapse_subtrees()

    def get_path_string(self) -> str:
        """
        Return a string representing the path containing this tree
        and its ancestors, using the separator for this OS between each
        tree's name.
        """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() + \
                self.get_separator() + self._name

    def _build_path_string(self) -> str:
        """
        Recursively build the path string of the tree and its ancestors.
        """
        if self._parent_tree is None:
            return self._name

        parent_path = self._parent_tree._build_path_string()
        return f"{parent_path}{self.get_separator()}{self._name}"

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        temp_subtrees = [FileSystemTree(os.path.join(path, x)) for x in os.listdir(path)] if os.path.isdir(path) else []
        super().__init__(os.path.basename(path), temp_subtrees, os.path.getsize(path))

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    # x = FileSystemTree(test_path)
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
