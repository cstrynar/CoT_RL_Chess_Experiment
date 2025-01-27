# visualize a chess board.

import chess
import chess.svg
from IPython.display import SVG, display

# Create a new chess board in starting position
board = chess.Board()

def extract_svg_content(svg_string):
    # Extract content between <svg> and </svg> tags
    start = svg_string.find('<pre>')
    end = svg_string.find('</pre>')
    return svg_string[start + 5:end]

# Display initial position
print("Initial position:")
svg_output = chess.svg.board(board=board)
print(extract_svg_content(svg_output))

# Make a few moves
# 1. e4 e5 2. Nf3 Nc6
moves = ['e2e4', 'e7e5', 'g1f3', 'b8c6']
for move in moves:
    board.push_san(move)

# Display position after moves
print("\nPosition after 1. e4 e5 2. Nf3 Nc6:")
svg_output = chess.svg.board(board=board)
print(extract_svg_content(svg_output))

# Main game loop
while not board.is_game_over():
    # Get next move from user
    try:
        move = input("\nEnter next move (e.g. e2e4) or 'q' to quit: ")
        
        if move.lower() == 'q':
            break
            
        # Try to make the move
        board.push_san(move)
        
        # Display updated board
        print("\nPosition after move", move + ":")
        svg_output = chess.svg.board(board=board)
        print(extract_svg_content(svg_output))
        
    except ValueError:
        print("Invalid move! Please try again using algebraic notation (e.g. e2e4)")
    except Exception as e:
        print(f"Error: {e}")
        print("Please try again")

# Game over - display result
if board.is_game_over():
    print("\nGame Over!")
    if board.is_checkmate():
        print("Checkmate!")
    elif board.is_stalemate():
        print("Stalemate!")
    elif board.is_insufficient_material():
        print("Draw - Insufficient material!")
    elif board.is_fifty_moves():
        print("Draw - Fifty move rule!")
    elif board.is_repetition():
        print("Draw - Threefold repetition!")
