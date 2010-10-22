"""
Post-processing utility operations on data structures coming from
JdbcEi (lists of lists).
"""


class AnchestorRegistration(object):
    """
    Keeps track of anchestors. Used by tree_from_list. Simple
    implementation, does not handle corner cases.
    """

    def __init__(self):
        # self.anchestors consists of ids and a dict of ids that one
        # cannot have as a parent
        self.anchestors = {}

    def register(self, row_id):
        if row_id not in self.anchestors:
            self.anchestors[row_id] = {row_id: None}

    def anchestor_of(self, row_id, row_anchestor_id):
        """
        Check if row_anchestor is an anchestor of row
        """
        self.register(row_id)
        return row_anchestor_id in self.anchestors[row_id]

    def register_parent(self, row_id, row_parent_id):
        """
        Register row_id under row_parent.
        """
        self.register(row_parent_id)
        self.register(row_id)
        self.anchestors[row_id].update(self.anchestors[row_parent_id])


class CycleError(Exception):
    pass


def tree_from_list(rows,
                   id_field='id',
                   parent_field='parent_id',
                   children_field='children',
                   root_parent=None):
    """Makes a hierarchical tree structure from list of lists. The
    resulting tree structure is a recursive list of dicts (with lists
    of dicts in it).

    rows is a list with dicts.

    >>> rows = [{'id': 'name', 'parent_id': None},
                {'id': 'child', 'parent_id': 'name'},
                {'id': 'name2', 'parent_id': None}]
    >>> tree_from_list(rows)
    [{'id': 'name', 'parent_id': None, 'children': [
        {'id': 'child', 'parent_id': 'name', 'children': []}, ],
    {'id': 'name2', 'parent_id': None, 'children': [],
    ]
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
