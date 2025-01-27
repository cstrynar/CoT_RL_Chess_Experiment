import chess
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import time

class AIPlayer:
    def __init__(self):
        """Initialize the AI player with Hugging Face model"""
        model_name = "mistralai/Mistral-7B-Instruct-v0.2"
        
        # Check CUDA availability
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available. Please check your GPU setup.")
        
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"Loading model {model_name} and tokenizer...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use float16 for efficiency
            device_map="auto",          # Automatically handle GPU placement
            load_in_4bit=True,          # Enable 4-bit quantization for better memory efficiency
        )
        
        # Verify model is on GPU
        print(f"Model device: {self.model.device}")
        print(f"GPU Memory allocated: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        
        self.max_retries = 5
        self.temperatures = [0.7, 0.8, 0.9, 1.0, 1.1]

    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Generate and return a chess move for the given board state
        Returns None if move generation fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                # Get current board state
                fen = board.fen()
                legal_moves = [str(move) for move in board.legal_moves]
                
                # Prepare prompt using Mistral's chat format
                prompt = f"""<s>[INST] You are playing a chess game as Black. Here is the current board state in FEN notation:
{fen}

Available legal moves in algebraic notation:
{', '.join(legal_moves)}

Analyze the position and make a move for Black. You should try to make the best move possible. 

Include your move in algebraic notation (e.g., 'e2e4' or 'g1f3'). Note that moves include both the starting and ending square, in contrast to some other notations.[/INST]"""

                # Generate response
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1000,
                    temperature=self.temperatures[min(attempt, len(self.temperatures)-1)],
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    do_sample=True,
                    top_p=0.95
                )
                
                # Extract response
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = response[len(prompt):].strip()
                print(f"Attempt {attempt + 1}: AI response: {response}")
                
                # Try to find a valid move in the response
                words = response.split()
                for word in words:
                    # Clean the word of any punctuation
                    word = word.strip('.,!?()"\'')
                    
                    # Try to parse as UCI move
                    try:
                        move = chess.Move.from_uci(word)
                        if move in board.legal_moves:
                            print(f"Found valid move: {word}")
                            return move
                    except ValueError:
                        # If UCI parsing fails, try to parse as SAN
                        try:
                            move = board.parse_san(word)
                            if move in board.legal_moves:
                                print(f"Found valid move: {word}")
                                return move
                        except ValueError:
                            continue
                
                print(f"No valid move found in response")
                if attempt < self.max_retries - 1:
                    print(f"Retrying... ({attempt + 2}/{self.max_retries})")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error during attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying... ({attempt + 2}/{self.max_retries})")
                    time.sleep(1)
        
        # If all retries failed, make a random move
        print("LLM failed to generate valid move after all retries. Making random move...")
        legal_moves = list(board.legal_moves)
        if legal_moves:
            import random
            random_move = random.choice(legal_moves)
            print(f"Random move chosen: {random_move}")
            return random_move
        
        return None  # Only if there are no legal moves at all 