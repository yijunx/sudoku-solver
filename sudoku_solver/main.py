from typing import List, Set, Tuple
from exceptions import SolveError


class Board:
    def __init__(self, content: List[List[int]]) -> None:
        self.content = [x.copy() for x in content]
        self.interation: int = 0

    @property
    def is_done(self) -> bool:
        if any([0 in x for x in self.content]):
            return False
        else:
            return True

    def pprint(self) -> None:
        for row in self.content:
            print(row)


def find_grid(row: int, col: int) -> List[Tuple[int, int]]:
    top_left_row = row // 3 * 3
    top_left_col = col // 3 * 3

    return [
        (x, y)
        for x in [top_left_row + i for i in range(3)]
        for y in [top_left_col + j for j in range(3)]
    ]


def row_removal(
    value: int,
    row: int,
    all_possibilities: List[List[set]],
    exclude_cells: List[Tuple[int, int]] = None,
) -> bool:
    """ """
    # print(f"removing {value} in row {row}")
    has_input = False
    for col, possibilities_of_a_cell in enumerate(all_possibilities[row]):
        if value in possibilities_of_a_cell:
            if exclude_cells:
                if (row, col) not in exclude_cells:
                    has_input = True
                    possibilities_of_a_cell.remove(value)
            else:
                has_input = True
                possibilities_of_a_cell.remove(value)
    return has_input


def col_removal(
    value: int,
    col: int,
    all_possibilities: List[List[set]],
    exclude_cells: List[Tuple[int, int]] = None,
):
    """ """
    has_input = False
    for row, possibilities_of_a_cell in enumerate([x[col] for x in all_possibilities]):
        if value in possibilities_of_a_cell:
            if exclude_cells:
                if (row, col) not in exclude_cells:
                    has_input = True
                    possibilities_of_a_cell.remove(value)
            else:
                has_input = True
                possibilities_of_a_cell.remove(value)
    return has_input


def grid_removal(
    value: int, row: int, col: int, all_possibilities: List[List[set]]
) -> bool:
    # print(f"removing {value} in the grid of {row},{col}")
    has_input = False
    for i, j in find_grid(row=row, col=col):
        if value in all_possibilities[i][j]:
            has_input = True
            all_possibilities[i][j].remove(value)
    return has_input


def simle_removal_one_loc(
    board: Board,
    row: int,
    col: int,
    removed_locations: Set[Tuple[int, int]],
    all_possibilities: List[List[set]],
) -> bool:
    value = board.content[row][col]
    if value == 0:
        return

    if (row, col) in removed_locations:
        return

    # row removal
    has_input_row = row_removal(
        value=value, row=row, all_possibilities=all_possibilities
    )

    # col removal
    has_input_col = col_removal(
        value=value, col=col, all_possibilities=all_possibilities
    )

    # 3*3 removal
    has_input_grid = grid_removal(
        value=value, row=row, col=col, all_possibilities=all_possibilities
    )

    # self removal
    has_self_input = False
    if all_possibilities[row][col]:
        has_self_input = True
        all_possibilities[row][col] = set()
    removed_locations.add((row, col))
    return has_input_row or has_input_grid or has_input_col or has_self_input


def simple_removal(
    board: Board,
    removed_locations: Set[Tuple[int, int]],
    all_possibilities: List[List[set]],
) -> bool:
    """remove the number from possibilities in same row / col / grid"""
    has_input = False
    for i in range(9):
        for j in range(9):
            has_input_one_loc = simle_removal_one_loc(
                board=board,
                row=i,
                col=j,
                removed_locations=removed_locations,
                all_possibilities=all_possibilities,
            )
            has_input = has_input_one_loc or has_input
    return has_input


def grid_fill(
    board: Board,
    removed_locations: Set[Tuple[int, int]],
    all_possibilities: List[List[set]],
) -> bool:
    """in a grid's perspective, fill number if possible,
    also does not possibility removal if possible
    (all possibilities of a number lies same row or col)"""
    has_input_fill = False
    has_input_row = False
    has_input_col = False
    for i in range(3):
        for j in range(3):
            grid_locations = [
                (x, y)
                for x in [3 * i + x for x in range(3)]
                for y in [3 * j + x for x in range(3)]
            ]

            for value in [x + 1 for x in range(9)]:
                # if value in [
                #     board.content[cell[0]][cell[1]] for cell in grid_locations
                # ]:
                #     # we already filled it
                #     continue

                possible_locations_for_a_value: List[Tuple[int, int]] = []
                for row, col in grid_locations:
                    if value in all_possibilities[row][col]:
                        possible_locations_for_a_value.append((row, col))

                if len(possible_locations_for_a_value) == 1:
                    # fill we can fill it!!!!
                    has_input_fill = True
                    if value in [
                        board.content[cell[0]][cell[1]] for cell in grid_locations
                    ]:
                        # we already filled it
                        raise SolveError(f"{value} is already in {grid_locations}")
                    x, y = possible_locations_for_a_value.pop()
                    board.content[x][y] = value
                    print(f"GRID filling {x},{y} with {value}")
                    simle_removal_one_loc(
                        board=board,
                        row=x,
                        col=y,
                        removed_locations=removed_locations,
                        all_possibilities=all_possibilities,
                    )
                elif len(possible_locations_for_a_value) > 0:
                    # check if all possible results of a value in the same row
                    if all(
                        [
                            loc[0] == possible_locations_for_a_value[0][0]
                            for loc in possible_locations_for_a_value
                        ]
                    ):
                        has_input_row = has_input_row or row_removal(
                            value=value,
                            row=possible_locations_for_a_value[0][0],
                            all_possibilities=all_possibilities,
                            exclude_cells=grid_locations,
                        )

                    # check if all possible results of a value in the same col
                    if all(
                        [
                            loc[1] == possible_locations_for_a_value[0][1]
                            for loc in possible_locations_for_a_value
                        ]
                    ):
                        has_input_col = has_input_col or col_removal(
                            value=value,
                            col=possible_locations_for_a_value[0][1],
                            all_possibilities=all_possibilities,
                            exclude_cells=grid_locations,
                        )
    return has_input_col or has_input_row or has_input_fill


def simple_fill(
    board: Board,
    all_possibilities: List[List[set]],
) -> bool:
    has_input = False
    for i in range(9):
        for j in range(9):
            if board.content[i][j] == 0 and len(all_possibilities[i][j]) == 1:
                v = all_possibilities[i][j].pop()
                board.content[i][j] = v
                print(f"SIMPLE filling {i},{j} with {v}")
                has_input = True
            if board.content[i][j] == 0 and len(all_possibilities[i][j]) == 0:
                raise SolveError(f"cell {i},{j} has no value possible")
    return has_input


def print_all_possibilities(all_possibilities: List[List[set]]):
    for row in range(9):
        for col in range(9):
            print(f"LOC[{row}][{col}] is possibly {all_possibilities[row][col]}")


def logical_solve(board: Board, all_possibilities: List[List[set]] = None) -> Board:

    if all_possibilities is None:
        all_possibilities: List[List[set]] = [
            [set([1, 2, 3, 4, 5, 6, 7, 8, 9]) for _ in range(9)] for _ in range(9)
        ]
    removed_locations: Set[Tuple[int, int]] = set()

    def do_an_iteration(
        board: Board,
        all_possibilities: List[List[set]],
        removed_locations: Set[Tuple[int, int]],
    ):
        if board.is_done:
            print("WELL ITS DONE!!!")
            return board

        has_input_simple_removal = simple_removal(
            board=board,
            removed_locations=removed_locations,
            all_possibilities=all_possibilities,
        )

        has_input_grid_fill = grid_fill(
            board=board,
            removed_locations=removed_locations,
            all_possibilities=all_possibilities,
        )

        has_input_simple_fill = simple_fill(
            board=board,
            all_possibilities=all_possibilities,
        )

        # print(has_input_simple_removal, has_input_grid_fill, has_input_simple_fill)
        board_changed = (
            has_input_simple_removal or has_input_grid_fill or has_input_simple_fill
        )

        # print the result
        board.interation += 1
        print(f"interation {board.interation} done")
        print(has_input_simple_removal, has_input_grid_fill, has_input_simple_fill)
        if not board_changed:
            # print_all_possibilities(all_possibilities=all_possibilities)
            print(f"CANNOT FINISH...AFTER ITERATION {board.interation}")
            return board

        return do_an_iteration(
            board=board,
            all_possibilities=all_possibilities,
            removed_locations=removed_locations,
        )

    return do_an_iteration(
        board=board,
        all_possibilities=all_possibilities,
        removed_locations=removed_locations,
    )


def simple_check_assumption_validity(board: Board, row: int, col: int):
    values_in_row = [x for x in board.content[row] if x]
    if len(values_in_row) > len(set(values_in_row)):
        raise SolveError(f"There are duplicates in row {row}")
    values_in_col = [x[col] for x in board.content if x[col]]
    if len(values_in_col) > len(set(values_in_col)):
        raise SolveError(f"There are duplicates in col {row}")
    values_in_grid = [
        board.content[cell[0]][cell[1]] for cell in find_grid(row=row, col=col)
    ]
    values_in_grid = [x for x in values_in_grid if x]
    if len(values_in_grid) > len(set(values_in_grid)):
        raise SolveError(f"There are duplicates in the grid of {row},{col}")


def brutal_solve(board: Board):

    initial_board = Board(content=board.content)

    all_possibilities: List[List[set]] = [
        [set([1, 2, 3, 4, 5, 6, 7, 8, 9]) for _ in range(9)] for _ in range(9)
    ]

    for i in range(9):
        for j in range(9):
            if board.content[i][j] == 0:  # if the cell is not filled
                possibilities = all_possibilities[i][j].copy()  # set(list(range(9)))
                while possibilities:

                    # fill one first
                    value_to_fill = possibilities.pop()
                    board.content[i][j] = value_to_fill
                    print(f"assuming cell {i},{j} is {board.content[i][j]}")
                    try:
                        simple_check_assumption_validity(board, row=i, col=j)
                        bruted_board = logical_solve(board=board)
                        if bruted_board.is_done:
                            return bruted_board
                        else:
                            print("well, no solve error.. not finished also")

                            # board = brutal_solve(
                            #     board=bruted_board
                            # )  # bruted_board = brutal_solve(board=bruted_board)
                    except SolveError:
                        board = Board(content=initial_board.content)
                        all_possibilities[i][j].remove(value_to_fill)
                        print(f"cell {i},{j} cannot be {board.content[i][j]}")
    raise SolveError("unsolvable!!!")


def convert_string_input_to_board(input_strs: List[str]) -> Board:
    """each row is a row"""
    b = Board(content=[])
    for row in input_strs:
        b.content.append([int(x) for x in row])
    return b


if __name__ == "__main__":
    board_content_easy = [
        [0, 0, 0, 6, 7, 0, 5, 4, 2],
        [0, 0, 4, 0, 9, 5, 3, 0, 6],
        [0, 0, 5, 0, 0, 0, 8, 1, 0],
        [0, 1, 2, 8, 0, 0, 0, 0, 4],
        [0, 5, 0, 3, 4, 2, 7, 0, 0],
        [4, 0, 7, 0, 0, 1, 6, 0, 3],
        [0, 4, 0, 0, 1, 0, 0, 3, 8],
        [0, 6, 0, 7, 0, 4, 0, 0, 5],
        [0, 0, 0, 2, 0, 0, 0, 6, 7],
    ]

    easy_board = Board(content=board_content_easy)

    hard_board = convert_string_input_to_board(
        input_strs=[
            "106003000",
            "000000200",
            "003000074",
            "000000000",
            "010045003",
            "400028560",
            "600700002",
            "805000000",
            "090080000",
        ]
    )

    master_board = convert_string_input_to_board(
        input_strs=[
            "005000000",
            "600000900",
            "100970053",
            "063801200",
            "002050000",
            "000000017",
            "080600000",
            "000380090",
            "070005002"
        ]
    )

    grand_master_board = convert_string_input_to_board(
        input_strs=[
            "000020600",
            "001800030",
            "000700245",
            "000640000",
            "903107020",
            "016003000",
            "600400070",
            "100000008",
            "000005000"
        ]
    )

    board = Board(content=grand_master_board.content)
    board.pprint()
    board = logical_solve(board=board)

    print("now i am going to use brutal force..")
    board = brutal_solve(board=board)


    board.pprint()
    # print(is_done(board))

    # print(find_grid(0, 0))

    # print(find_grid(4, 3))
