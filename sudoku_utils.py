

class SudokuUtils(object):
    rows = 'ABCDEFGHI'
    cols = '123456789'

    @classmethod
    def get_rows_as_list(cls):
        for row in cls.rows:
            target = row + '1'
            row_peers = cls.get_row_peers(target)
            yield [target] + row_peers

    @classmethod
    def get_cols_as_list(cls):
        for col in cls.cols:
            target = 'A' + col
            col_peers = cls.get_col_peers(target)
            yield [target] + col_peers

    @classmethod
    def get_boxs_as_list(cls):
        starting = ['A1', 'A4', 'A7', 'D1', 'D4', 'D7', 'G1', 'G4', 'G7']
        for box_target in starting:
            peers = cls.get_box_peers(box_target)
            yield [box_target] + peers

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
