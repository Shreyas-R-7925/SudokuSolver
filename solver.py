class Solution:
    def isValid(self, i, j, board, c):
        # Row and column check
        for k in range(9):
            if board[i][k] == c:
                return False
            if board[k][j] == c:
                return False

        # 3x3 sub-box check
        for ki in range(i - i % 3, i - i % 3 + 3):
            for kj in range(j - j % 3, j - j % 3 + 3):
                if board[ki][kj] == c:
                    return False

        return True

    def solve(self, i, j, board):
        if i == 9:  # Completed traversing the whole board
            return True
        if j == 9:  # Go to next row
            return self.solve(i + 1, 0, board)
        
        if board[i][j] != '.':
            return self.solve(i, j + 1, board)

        for c in '123456789':
            if not self.isValid(i, j, board, c):
                continue

            board[i][j] = c
            if self.solve(i, j + 1, board):
                return True

            board[i][j] = '.'

        return False

    def solveSudoku(self, board):
        self.solve(0, 0, board)
