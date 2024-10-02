import json
import os

class OrgHierarchyTree:
    def __init__(self, api):
        # Build the query string for DHIS2 analytics API to retrieve the required data
        query_string = 'organisationUnits.json?fields=id,name,level,parent[id]&paging=false'

        # Fetch the data from DHIS2 API using the constructed query string
        response = api.get(query_string)

        # Store the list of organization units
        self.list_of_org_units = response.json()["organisationUnits"]

        # Build the graph representation of the organization hierarchy
        self.graph = self.build_graph()

        self.save_tree_to_json()

    def save_tree_to_json(self):
        """Save the organization hierarchy tree to a JSON file."""
        # Create the parent relationships JSON
        parent_json = self.create_parent_json()

        # Save the JSON to a file
        with open(rf'{os.getcwd().replace('\test','')}\Data\org_unit_hierarchy.json', 'w') as f:
            json.dump(parent_json, f, indent=4)

    def create_parent_json(self):
        """
        Create a JSON object where each element has its ID, name, and a list of all its parents.

        Returns:
            dict: A dictionary containing the parent information for each node.
        """
        parent_json = {}
        for node_id, node_data in self.graph.items():
            parent_json[node_id] = {
                'name': node_data.name,
                'id': node_id,
                'parents': self.find_all_parents(node_id)
            }
        return parent_json

    def find_all_parents(self, node_id):
        """
        Recursively find all parents of a given node.

        Args:
            node_id (str): The ID of the node.

        Returns:
            list: A list of parent IDs.
        """
        parents = []
        if node_id in self.graph:
            parent = self.graph[node_id].parent_id
            if parent:
                parents.extend(self.find_all_parents(parent))
                parents.append(parent)
        return parents

    def build_graph(self):
        """
        Build a graph representation of the organization hierarchy.

        Returns:
            dict: A dictionary representing the graph, where keys are node IDs and values are Node objects.
        """
        node_dict = {}

        # Create Node objects for each organization unit
        for node_data in self.list_of_org_units:
            node_id = node_data['id']
            parent_id = node_data["parent"]["id"] if node_data["level"] != 1 else None
            node = Node(node_data['name'], node_id, parent_id)
            node_dict[node_id] = node

        # Establish parent-child relationships
        for node_data in self.list_of_org_units:
            node_id = node_data['id']
            parent_id = node_data['parent']['id'] if 'parent' in node_data else None
            if parent_id is not None:
                node_dict[parent_id].children.append(node_dict[node_id])

        return node_dict

class Node:
    def __init__(self, name, id, parent_id):
        self.name = name
        self.id = id
        self.children = []
        self.parent_id = parent_id