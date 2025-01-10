from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, Namespace
import random
import time
from dataclasses import dataclass
from typing import List, Set, Dict
from os import environ
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = environ.get('SECRET_KEY', 'fallback-secret-key-for-development')
socketio = SocketIO(app)

@dataclass
class Player:
    id: str
    name: str  # Add name field
    board: List[List[int]]
    marked_numbers: Set[int]
    score: int = 0
    completed_rows: Set[int] = None  # Track which rows are completed
    
    def __post_init__(self):
        self.completed_rows = set()

class TombalaGame:
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.drawn_numbers: List[int] = []
        self.available_numbers = list(range(1, 91))
        self.is_active = False
        self.draw_interval = 3
        self.last_draw_time = 0
        self.max_numbers = 90  # Total numbers in the game
        self.first_cinko_claimed = False
        self.second_cinko_claimed = False
        self.tombala_claimed = False

    def generate_board(self) -> List[List[int]]:
        # Simple random board generation without any rigging
        numbers = random.sample(range(1, 91), 15)
        return [sorted(numbers[i:i+5]) for i in range(0, 15, 5)]
    
    def draw_number(self) -> int:
        if self.available_numbers:
            number = random.choice(self.available_numbers)
            self.available_numbers.remove(number)
            self.drawn_numbers.append(number)
            print(f"Left number count:{len(self.available_numbers)}, Drawn number: {number}")
            return number
        return None
    
    def check_win(self, player_id: str, marked_rows: int) -> tuple[bool, int]:
        player = self.players.get(player_id)
        if not player:
            return False, 0
        
        points = 0
        if marked_rows == 1 and not self.first_cinko_claimed:
            self.first_cinko_claimed = True
            points = 1
        elif marked_rows == 2 and not self.second_cinko_claimed:
            self.second_cinko_claimed = True
            points = 2
        elif marked_rows == 3 and not self.tombala_claimed:
            self.tombala_claimed = True
            points = 3
            self.is_active = False  # End game when tombala is achieved
        
        if points > 0:
            player.score += points
            return True, points
        return False, 0
    
    def reset_game(self):
        self.first_cinko_claimed = False
        self.second_cinko_claimed = False
        self.tombala_claimed = False
        self.is_active = False
        self.drawn_numbers = []
        self.available_numbers = list(range(1, 91))

    def is_game_complete(self):
        return len(self.drawn_numbers) >= self.max_numbers

game = TombalaGame()

class GameNamespace(Namespace):
    def on_connect(self):
        print(f"Client connected: {request.sid}")
        emit('gameState', {
            'active': game.is_active,
            'canStart': len(game.players) > 3,
            'message': 'Waiting for players...'
        })

    def on_disconnect(self):
        if request.sid in game.players:
            del game.players[request.sid]
            self.broadcast_player_update()

    def on_join(self):
        if game.is_active:
            emit('gameState', {
                'active': game.is_active,
                'canStart': False,
                'message': 'Game already in progress!'
            })
            return
            
        player_id = request.sid
        player_name = f"Player {len(game.players) + 1}"
        board = game.generate_board()  # Remove is_player_one parameter
        game.players[player_id] = Player(player_id, player_name, board, set())
        
        emit('board', {'board': board})
        self.broadcast_player_update()
        self.broadcast_game_state()

    def on_start(self):
        if len(game.players) < 2:
            return
            
        game.is_active = True
        game.last_draw_time = time.time()
        self.broadcast_game_state()
        socketio.start_background_task(self.draw_numbers)

    def on_win(self, data):
        player_id = request.sid
        won, points = game.check_win(player_id, data['rows'])
        if won:
            player = game.players[player_id]
            message = f'Player {player.name} won {points} points!'
            if points == 3:
                message += ' TOMBALA! Game Over!'
            self.broadcast_game_state(message)
            self.broadcast_player_update()
            
            if game.tombala_claimed:
                # Reset game state but keep player scores
                game.reset_game()
                self.broadcast_game_state('Game Over! New game can be started.')

    def broadcast_player_update(self):
        player_list = [{
            'id': p.id,
            'name': p.name,
            'score': p.score,
            'achievements': [
                'Çinko' if game.first_cinko_claimed else '',
                'İkinci Çinko' if game.second_cinko_claimed else '',
                'Tombala' if game.tombala_claimed else ''
            ]
        } for p in game.players.values()]
        emit('playerUpdate', {'players': player_list}, broadcast=True)

    def broadcast_game_state(self, message=None):
        emit('gameState', {
            'active': game.is_active,
            'canStart': len(game.players) >= 2,
            'message': message or ('Game Started!' if game.is_active else 'Waiting for players...')
        }, broadcast=True)

    def draw_numbers(self):
        while game.is_active and not game.is_game_complete():
            socketio.sleep(game.draw_interval)
            with app.app_context():
                number = game.draw_number()
                if number:
                    emit('drawnNumber', {'number': number}, broadcast=True, namespace='/')
                    if game.is_game_complete():
                        game.is_active = False
                        self.broadcast_game_state('Game Over - All numbers drawn!')
                        break
                else:
                    game.is_active = False
                    self.broadcast_game_state('Game Over!')
                    break

@app.route('/')
def index():
    return render_template('index.html')

# Register the namespace
socketio.on_namespace(GameNamespace('/'))

if __name__ == '__main__':
    socketio.run(app, 
                 debug=True, 
                 host='0.0.0.0',
                 allow_unsafe_werkzeug=True)
