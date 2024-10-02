import pytest
from unittest.mock import Mock
from source.data_downloader.get_organisation_hierarchy import OrgHierarchyTree, Node

@pytest.fixture
def sample_org_units():
    return [
        {"id": "root", "name": "Root", "level": 1},
        {"id": "child1", "name": "Child 1", "level": 2, "parent": {"id": "root"}},
        {"id": "child2", "name": "Child 2", "level": 2, "parent": {"id": "root"}},
        {"id": "grandchild1", "name": "Grandchild 1", "level": 3, "parent": {"id": "child1"}},
    ]

@pytest.fixture
def mock_api(sample_org_units):
    mock_api = Mock()
    mock_api.get.return_value.json.return_value = {"organisationUnits": sample_org_units}
    return mock_api

def test_init(mock_api):
    tree = OrgHierarchyTree(mock_api)
    assert len(tree.list_of_org_units) == 4
    assert len(tree.graph) == 4

def test_build_graph(mock_api):
    tree = OrgHierarchyTree(mock_api)
    graph = tree.graph

    assert "root" in graph
    assert "child1" in graph
    assert "child2" in graph
    assert "grandchild1" in graph

    assert graph["root"].parent_id is None
    assert graph["child1"].parent_id == "root"
    assert graph["child2"].parent_id == "root"
    assert graph["grandchild1"].parent_id == "child1"

    assert len(graph["root"].children) == 2
    assert len(graph["child1"].children) == 1
    assert len(graph["child2"].children) == 0
    assert len(graph["grandchild1"].children) == 0

def test_find_all_parents(mock_api):
    tree = OrgHierarchyTree(mock_api)

    assert tree.find_all_parents("root") == []
    assert tree.find_all_parents("child1") == ["root"]
    assert tree.find_all_parents("child2") == ["root"]
    assert tree.find_all_parents("grandchild1") == ["child1", "root"]

    #Ensure that there is a test that a orgs parents are in order

def test_create_parent_json(mock_api):
    tree = OrgHierarchyTree(mock_api)
    parent_json = tree.create_parent_json()

    assert len(parent_json) == 4
    assert parent_json["root"]["parents"] == []
    assert parent_json["child1"]["parents"] == ["root"]
    assert parent_json["child2"]["parents"] == ["root"]
    assert parent_json["grandchild1"]["parents"] == ["child1", "root"]

def test_save_tree_to_json(mock_api, tmp_path):
    tree = OrgHierarchyTree(mock_api)
    json_file = tmp_path / "parent_relationships.json"

    # Monkey patch the open function to use our temporary file
    import builtins
    original_open = builtins.open
    builtins.open = lambda *args, **kwargs: original_open(json_file, *args[1:], **kwargs)

    tree.save_tree_to_json()

    # Restore the original open function
    builtins.open = original_open

    assert json_file.is_file()
    content = json_file.read_text()
    assert "root" in content
    assert "child1" in content
    assert "child2" in content
    assert "grandchild1" in content

def test_node_creation():
    node = Node("Test Node", "test_id", "parent_id")
    assert node.name == "Test Node"
    assert node.id == "test_id"
    assert node.parent_id == "parent_id"
    assert node.children == []