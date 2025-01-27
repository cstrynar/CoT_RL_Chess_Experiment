import chess
import chess.svg
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtSvgWidgets import QSvgWidget 
from PySide6.QtCore import Qt, QPoint, Signal
import sys

class ChessBoard(QWidget):
    # Add a signal to communicate status changes
    status_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.selected_square = None
        self.svg_widget = QSvgWidget(self)
        self.setWindowTitle("Chess Game")  # Initial window title
        self.update_board()
        
    def update_board(self):
        squares = []
        if self.selected_square is not None:
            # Highlight selected square and possible moves
            squares.append((self.selected_square, "#eed85c"))  # Yellow highlight for selected
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    squares.append((move.to_square, "#31b43c"))  # Green highlight for possible moves
        
        # Add red highlight for checkmated king
        if self.board.is_checkmate():
            # Find the king's square of the losing side
            losing_color = self.board.turn  # Current turn is the losing side in checkmate
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece and piece.piece_type == chess.KING and piece.color == losing_color:
                    squares.append((square, "#ff3333"))  # Red highlight for checkmated king
                    break
        
        # Emit status signal
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            self.status_changed.emit(f"Game Over - {winner} wins!")
        elif self.board.is_stalemate():
            self.status_changed.emit("Game Over - Stalemate!")
        elif self.board.is_check():
            self.status_changed.emit("Check!")
        else:
            current_player = "White" if self.board.turn == chess.WHITE else "Black"
            self.status_changed.emit(f"{current_player} to move")
        
        svg_content = chess.svg.board(
            board=self.board,
            squares=dict(squares),  # Convert list of tuples to dictionary
            size=400,
            lastmove=None,  # Remove last move marker
            check=None,     # Remove check marker
            arrows=[],      # Remove any arrows
            coordinates=False  # Remove coordinates
        ).encode('UTF-8')
        
        self.svg_widget.load(svg_content)
        self.svg_widget.resize(400, 400)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            # Right click deselects the piece
            if self.selected_square is not None:
                self.selected_square = None
                self.update_board()
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert click coordinates to chess square
            size = min(self.width(), self.height())
            x = int(event.position().x() * 8 / size)
            y = 7 - int(event.position().y() * 8 / size)
            square = y * 8 + x
            
            if self.selected_square is None:
                # Only allow selection of squares with pieces that can move
                piece = self.board.piece_at(square)
                if piece and any(move.from_square == square for move in self.board.legal_moves):
                    self.selected_square = square
                    self.update_board()
            else:
                # Try to make a move
                move = chess.Move(self.selected_square, square)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.selected_square = None
                    self.update_board()
                else:
                    # If clicking on a different piece of same color, select that piece instead
                    piece = self.board.piece_at(square)
                    if piece and piece.color == self.board.turn and any(move.from_square == square for move in self.board.legal_moves):
                        self.selected_square = square
                        self.update_board()
                    else:
                        # Clicking on invalid square deselects the piece
                        self.selected_square = None
                        self.update_board()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Game")
        self.chess_board = ChessBoard()
        self.setCentralWidget(self.chess_board)
        self.resize(400, 400)
        
        # Connect the status signal to update window title
        self.chess_board.status_changed.connect(self.setWindowTitle)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
