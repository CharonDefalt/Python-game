def print_board(board):
    print("\n\n")  # Added extra spacing before the board
    print("   0   1   2")
    for i, row in enumerate(board):
        print(f"{i} {' | '.join(row)}")
        if i < 2:
            print("   " + "-" * 9)


def check_winner(board):
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != " ":
            return row[0]

    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != " ":
            return board[0][col]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != " ":
        return board[0][2]

    return None


def is_board_full(board):
    for row in board:
        if " " in row:
            return False
    return True


def play_game():
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"

    while True:
        print_board(board)
        # Added extra spacing before the player turn announcement
        print("\n\n")
        print(f"Player {current_player}'s turn.\n")

        try:
            row = int(input("Enter row (0-2): "))
            col = int(input("Enter column (0-2): "))
            print("\n") # Spacing after input

            if row < 0 or row > 2 or col < 0 or col > 2:
                print("Invalid input. Row and column must be between 0 and 2.")
                continue

            if board[row][col] != " ":
                print("This spot is already taken. Try again.")
                continue

            board[row][col] = current_player
            winner = check_winner(board)

            if winner:
                print_board(board)
                print(f"Player {winner} wins!")
                break

            if is_board_full(board):
                print_board(board)
                print("It's a draw!")
                break

            current_player = "O" if current_player == "X" else "X"

        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    play_game()

