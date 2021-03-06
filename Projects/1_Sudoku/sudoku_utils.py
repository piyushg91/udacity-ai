from typing import Dict, Set, Tuple


rows = 'ABCDEFGHI'
cols = '123456789'
reversed_cols = list(reversed(cols))

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]



class SudokuUtils(object):
    rows = 'ABCDEFGHI'
    cols = '123456789'
    all_rows = [cross(r, cols) for r in rows]
    all_cols = [cross(rows, c) for c in cols]
    all_boxes = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
    left_diagonal = {row + cols[i]for i, row in enumerate(rows)}
    right_diagonal = {row + reversed_cols[i] for i, row in enumerate(rows)}

    @classmethod
    def get_all_units(cls):
        units = {
            'row': cls.all_rows,
            'col': cls.all_cols,
            'boxes': cls.all_boxes,
            'diags': [list(cls.left_diagonal), list(cls.right_diagonal)]
        }
        return units

    @classmethod
    def get_all_units_without_diags(cls):
        units = {
            'row': cls.all_rows,
            'col': cls.all_cols,
            'boxes': cls.all_boxes,
        }
        return units

    @classmethod
    def get_col_peers(cls, target_box: str):
        target_row, target_col = target_box[0], target_box[1]
        peers = [row + target_col for row in cls.rows if row != target_row]
        return peers

    @classmethod
    def get_row_peers(cls, target_box: str):
        target_row, target_col = target_box[0], target_box[1]
        peers = [target_row + col for col in cls.cols if col != target_col]
        return peers

    @classmethod
    def get_box_peers(cls, target_box: str):
        row, col = target_box[0], target_box[1]
        row_index = cls.rows.find(row)
        col_index = cls.cols.find(col)

        start_row = int(int(row_index)/3) * 3
        end_row = start_row + 3 # non inclusive

        start_col = int(int(col_index)/3) * 3
        end_col = start_col + 3

        peers = []
        for row in range(start_row, end_row):
            actual_row = cls.rows[row]
            for col in range(start_col, end_col):
                actual_col = cls.cols[col]
                peer = actual_row + actual_col
                if peer == target_box:
                    continue
                peers.append(peer)
        return peers

    @classmethod
    def get_all_box_indicies(cls):
        return [row + col for row in cls.rows for col in cls.cols]

    @classmethod
    def get_peers_map(cls) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
        global_peers, peers_without_diags = {}, {}
        for box in cls.get_all_box_indicies():
            row = set(cls.get_row_peers(box))
            col = set(cls.get_col_peers(box))
            box_peers = set(cls.get_box_peers(box))
            all_peers = row.union(col).union(box_peers)
            peers_without_diags[box] = all_peers

            if box in cls.left_diagonal:
                all_peers = all_peers.union(cls.left_diagonal)
            if box in cls.right_diagonal:
                all_peers = all_peers.union(cls.right_diagonal)
            global_peers[box] = all_peers
        return global_peers, peers_without_diags

