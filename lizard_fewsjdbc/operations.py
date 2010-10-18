"""
Some utility operations on data structures
"""
import datetime


class AnchestorRegistration(object):
    def __init__(self):
        # self.anchestors consist of id's and a dict of id's that one
        # cannot have as a parent
        self.anchestors = {}

    def register(self, row_id):
        if row_id not in self.anchestors:
            self.anchestors[row_id] = {row_id: None}

    def anchestor_of(self, row_id, row_anchestor):
        """
        Check if row_id is an anchestor of row_anchestor
        """
        self.register(row_id)
        return row_anchestor in self.anchestors[row_id]

    def register_parent(self, row_id, row_parent):
        """
        Register row_id under row_parent.
        """
        self.register(row_parent)
        self.register(row_id)
        self.anchestors[row_id].update(self.anchestors[row_parent])


class CycleError(Exception):
    pass


def tree_from_list(rows,
                   id_field='id',
                   parent_field='parent_id',
                   children_field='children',
                   root_parent=None):
    """Makes a hierarchical tree structure, list of dicts with list of dicts, etc

    [{'name': 'name', 'children': [{'name': 'child', 'children': None}, ],
    {'name': 'name2', 'children': None,
    ]

    rows is a list with dicts. Each dict has keys 'name', 'parent'
    the nodes with parent is None are at root level.
    """

    result = {}
    anchestors = AnchestorRegistration()

    if root_parent not in result:
        result[root_parent] = {children_field: []}

    for row in rows:
        row_id = row[id_field]
        row_parent = row[parent_field]

        if row_id not in result:
            result[row_id] = {children_field: []}

        result[row[id_field]].update(row)

        if row_parent not in result:
            result[row_parent] = {children_field: []}

        # Prevent cycles: check if row_id is now already an anchestor
        # of (future) parent.
        if not anchestors.anchestor_of(row_parent, row_id):
            result[row_parent][children_field].append(result[row_id])

            # Register current row_id under row_parent.
            anchestors.register_parent(row_id, row_parent)
        else:
            raise CycleError('cycle detected while building tree from list')

    return result[root_parent][children_field]


def named_list(rows, names):
    """
    Converts list of lists to list of dicts, with given name.

    Assumes that len(names) = len(single row)
    """
    result = []
    for row in rows:
        row_dict = dict([(names[i], value) for i, value in enumerate(row)])
        result.append(row_dict)
    return result


def unique_list(rows):
    """
    Makes a new list with unique items from input list. Order is preserved.
    """
    result = []
    seen = {}
    for row in rows:
        row_str = str(row)
        if row_str not in seen:
            result.append(row)
            seen[row_str] = None
    return result
