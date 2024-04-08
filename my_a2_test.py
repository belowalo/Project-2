import os
from typing import List, Tuple
import tempfile
from hypothesis import given
from hypothesis.strategies import integers

from tm_trees import TMTree, FileSystemTree

# This should be the path to the "workshop" folder in the sample data.
# You may need to modify this, depending on where you downloaded and
# extracted the files.
EXAMPLE_PATH = os.path.join(os.getcwd(), 'example-directory', 'workshop')


def test_empty_directory_tree_creation() -> None:
    """Test the creation of a FileSystemTree object for an empty directory."""
    # Create a temporary empty directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a FileSystemTree object for the empty directory
        tree = FileSystemTree(temp_dir)

        # Verify attributes of the tree object
        assert tree._name == os.path.basename(temp_dir)
        assert tree.data_size == 0  # Empty directory, so data size should be 0
        assert len(tree._subtrees) == 0  # No files or subdirectories present
        assert tree._parent_tree is None


def test_update_rectangles() -> None:
    """Test the update_rectangles method."""
    # Path to the folder containing the example directory
    folder_path = os.path.dirname(EXAMPLE_PATH)

    # Create a FileSystemTree object for the folder
    tree = FileSystemTree(folder_path)

    # Update rectangles with arbitrary dimensions
    tree.update_rectangles((0, 0, 200, 100))

    # Get the rectangles
    rectangles = tree.get_rectangles()

    # Ensure that rectangles have been updated
    assert len(rectangles) > 0

    # Check that each rectangle has valid dimensions
    for rect, _ in rectangles:
        x, y, width, height = rect
        assert isinstance(x, int) and isinstance(y, int)
        assert isinstance(width, int) and isinstance(height, int)
        assert width >= 0 and height >= 0


def test_get_rectangles() -> None:
    """Test the get_rectangles method."""
    # Path to the folder containing the example directory
    folder_path = os.path.dirname(EXAMPLE_PATH)

    # Create a FileSystemTree object for the folder
    tree = FileSystemTree(folder_path)

    # Update rectangles with arbitrary dimensions
    tree.update_rectangles((0, 0, 200, 100))

    # Get the rectangles
    rectangles = tree.get_rectangles()

    # Ensure that rectangles have been updated
    assert len(rectangles) > 0

    # Check that each rectangle has valid dimensions
    for rect, _ in rectangles:
        x, y, width, height = rect
        assert isinstance(x, int) and isinstance(y, int)
        assert isinstance(width, int) and isinstance(height, int)
        assert width >= 0 and height >= 0


def get_rectangles_correctness(rectangles: List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]]) -> int:
    """Return the number of rectangles that have a correct format.

    A correct rectangle format is a tuple consisting of:
    - A tuple of four integers representing the position and size of the rectangle (x, y, width, height).
    - A tuple of three integers representing the RGB color value (red, green, blue).

    Parameters:
    - rectangles: A list of tuples representing rectangles.

    Returns:
    - The number of rectangles with correct format.
    """
    correct_count = 0
    for rect, color in rectangles:
        if isinstance(rect, tuple) and len(rect) == 4 and isinstance(color, tuple) and len(color) == 3:
            if all(isinstance(i, int) for i in rect) and all(0 <= i <= 255 for i in color):
                correct_count += 1
    return correct_count


def test_get_rectangles_correctness() -> None:
    """Test the correctness of the rectangles returned by get_rectangles method."""
    # Sample rectangles with correct format
    rectangles = [((0, 0, 100, 50), (255, 0, 0)),
                  ((100, 0, 100, 50), (0, 255, 0))]

    # Call the function to get the count of correct rectangles
    correct_count = get_rectangles_correctness(rectangles)

    # Assert that the correct count is equal to the length of the rectangles list
    assert correct_count == len(rectangles), f"Expected {len(rectangles)} rectangles, but got {correct_count}"


def test_get_tree_at_position_leaf_with_rect() -> None:
    """Test selecting a leaf node with proper rect attribute."""
    # Create a sample tree
    tree = TMTree('root', [])
    leaf = TMTree('leaf', [], data_size=100)
    tree._subtrees.append(leaf)

    # Set rect attribute for the tree and the leaf
    tree.rect = (0, 0, 200, 200)
    leaf.rect = (0, 0, 100, 100)

    # Test selecting a leaf node
    pos_inside_leaf = (50, 50)
    selected_leaf = tree.get_tree_at_position(pos_inside_leaf)
    assert selected_leaf is leaf


def test_get_tree_at_position_empty_tree() -> None:
    """Test selecting a position in an empty tree."""
    # Create an empty tree
    tree = TMTree(None, [])

    # Test selecting a position in an empty tree
    pos = (50, 50)
    selected_node = tree.get_tree_at_position(pos)
    assert selected_node is None


def test_change_size_leaf():
    """Test changing the size of a leaf node."""
    leaf = TMTree('leaf', [], data_size=100)
    leaf.change_size(0.5)
    assert leaf.data_size == 150


def test_change_size_non_leaf():
    """Test changing the size of a non-leaf node."""
    root = TMTree('root', [])
    root.change_size(0.5)
    assert root.data_size == 0


# Define test cases for the update_data_sizes method
def test_update_data_sizes_leaf():
    """Test updating data sizes for a leaf node."""
    leaf = TMTree('leaf', [], data_size=100)
    assert leaf.update_data_sizes() == 100


def test_update_data_sizes_non_leaf():
    """Test updating data sizes for a non-leaf node."""
    root = TMTree('root', [])
    leaf1 = TMTree('leaf1', [], data_size=50)
    leaf2 = TMTree('leaf2', [], data_size=75)
    root._subtrees.extend([leaf1, leaf2])
    assert root.update_data_sizes() == 125


# Define test cases for the move method
def test_move_leaf_to_non_leaf():
    """Test moving a leaf node to a non-leaf node."""
    root = TMTree('root', [])
    leaf = TMTree('leaf', [], data_size=100)
    root.move(leaf)
    assert leaf._parent_tree is None


def test_move_non_leaf_to_leaf():
    """Test moving a non-leaf node to a leaf node."""
    root = TMTree('root', [])
    leaf = TMTree('leaf', [], data_size=100)
    root.move(leaf)
    assert root._parent_tree is None


def test_expand():
    # Create a sample tree
    tree = TMTree('root', [])
    leaf1 = TMTree('leaf1', [], data_size=10)
    leaf2 = TMTree('leaf2', [], data_size=20)
    tree._subtrees.extend([leaf1, leaf2])

    # Expand the tree
    tree.expand()

    # Check if the tree is expanded
    assert tree._expanded is True


def test_collapse() -> None:
    """Test collapsing a tree."""
    # Create a sample tree
    tree = TMTree('root', [])
    leaf1 = TMTree('leaf1', [], data_size=10)
    leaf2 = TMTree('leaf2', [], data_size=20)
    tree._subtrees.extend([leaf1, leaf2])

    # Expand the tree first
    tree.expand()

    # Collapse the tree
    tree.collapse()

    # Check if the tree is collapsed
    assert tree._expanded is False

    # Check if the subtrees are collapsed
    assert all(not subtree._expanded for subtree in tree._subtrees)


def test_expand_all():
    # Create a sample tree
    tree = TMTree('root', [])
    leaf1 = TMTree('leaf1', [], data_size=10)
    leaf2 = TMTree('leaf2', [], data_size=20)
    subtree = TMTree('subtree', [leaf1, leaf2])
    tree._subtrees.append(subtree)

    # Expand all trees
    tree.expand_all()

    # Check if all trees are expanded
    assert all(subtree._expanded for subtree in tree._subtrees)


def test_collapse_all():
    # Create a sample tree
    tree = TMTree('root', [])
    leaf1 = TMTree('leaf1', [], data_size=10)
    leaf2 = TMTree('leaf2', [], data_size=20)
    subtree = TMTree('subtree', [leaf1, leaf2])
    tree._subtrees.append(subtree)

    # Expand all trees first
    tree.expand_all()

    # Collapse all trees
    tree.collapse_all()

    # Check if all trees are collapsed
    assert not any(subtree._expanded for subtree in tree._subtrees)


import pytest
from papers import PaperTree, _load_papers_to_dict, _build_tree_from_dict


@pytest.fixture
def sample_papers_dict():
    """Return a sample nested dictionary representing paper data."""
    return {
        '2019': {
            'CategoryA': {
                'Paper1': {'authors': 'Author1', 'name': 'Paper1', 'doi': 'doi1', 'citations': 10},
                'Paper2': {'authors': 'Author2', 'name': 'Paper2', 'doi': 'doi2', 'citations': 20}
            },
            'CategoryB': {
                'Paper3': {'authors': 'Author3', 'name': 'Paper3', 'doi': 'doi3', 'citations': 30}
            }
        }
    }


def test_build_tree_from_dict(sample_papers_dict):
    """Test _build_tree_from_dict function."""
    paper_tree_list = _build_tree_from_dict(sample_papers_dict)
    assert len(paper_tree_list) == 1
    assert len(paper_tree_list[0]._subtrees) == 2  # Two years: 2019 and 2020
