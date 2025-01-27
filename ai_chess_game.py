from GUI import ChessBoard, QMainWindow, QApplication
from PySide6.QtCore import QTimer
import sys
from ai_player import AIPlayer

class AIChessBoard(ChessBoard):
    def __init__(self):
        super().__init__()
        self.is_player_turn = True
        self.ai_player = AIPlayer()
        self.setWindowTitle("Chess Game vs AI")

    def mousePressEvent(self, event):
        if not self.is_player_turn:
            return  # Ignore clicks during AI turn
        
        # Call the parent class's mousePressEvent
        super().mousePressEvent(event)
        
        # If a move was made (selected_square was reset to None), trigger AI move
        if self.selected_square is None and not self.board.is_game_over():
            self.is_player_turn = False
            QTimer.singleShot(500, self.make_ai_move)

    def make_ai_move(self):
        """Handle AI's turn"""
        if self.board.is_game_over():
            return

        move = self.ai_player.get_move(self.board)
        if move:
            self.board.push(move)
            self.is_player_turn = True
            self.update_board()
        else:
            print("AI failed to make a valid move")

class AIChessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Game vs AI")
        self.chess_board = AIChessBoard()
        self.setCentralWidget(self.chess_board)
        self.resize(400, 400)
        self.chess_board.status_changed.connect(self.setWindowTitle)

def main():
    app = QApplication(sys.argv)
    window = AIChessWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 