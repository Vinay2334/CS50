"""
Tic Tac Toe Player
"""

import copy

X = "X"
O = "O"
EMPTY = None
cur_player = X


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    ans = None

    if x_count > o_count:
        ans = O
    else:
        ans = X

    return ans


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    res = list()
    for i, row in enumerate(board):
        for j, box in enumerate(row):
            if not box:
                res.append((i, j))
    return res


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)
    row, col = action
    player_now = player(board)
    new_board[row][col] = player_now
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Horizontally
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] is not None:
            return board[i][0]

    # Vertically
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] is not None:
            return board[0][i]

    # Diagonally
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    for row in board:
        for box in row:
            if not box:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == 'X':
        return 1
    elif win == 'O':
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None

    def optimal(board, current_player):
        if terminal(board):
            return utility(board), None

        if current_player == X:
            best_score = -float('inf')
            best_action = None
            for move in actions(board):
                new_board = result(board, move)
                score, _ = optimal(new_board, O)
                if score == 1:
                    return 1, move
                if score > best_score:
                    best_score = score
                    best_action = move
            return best_score, best_action

        else:  # O is minimizing
            best_score = float('inf')
            best_action = None
            for move in actions(board):
                new_board = result(board, move)
                score, _ = optimal(new_board, X)
                if score == -1:
                    return -1, move
                if score < best_score:
                    best_score = score
                    best_action = move
            return best_score, best_action

    _, optimal_move = optimal(board, player(board))
    return optimal_move
