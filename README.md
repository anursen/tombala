# Modern Tombala Game

A real-time multiplayer Tombala (Turkish Bingo) game built with Python Flask and Socket.IO.

## Features

- Real-time multiplayer gameplay
- Interactive game board
- Live number drawing
- Multiple winning conditions (Çinko, İkinci Çinko, Tombala)
- Visual number tracking
- Player score tracking

## Requirements

```
Flask==2.0.1
Flask-SocketIO==5.1.1
python-socketio==5.4.0
eventlet==0.33.0
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tombala.git
cd tombala
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

1. Start the server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Game Rules

- Each player receives a unique board with 15 numbers
- Numbers are drawn randomly
- Players can win by completing:
  - One row (Çinko): 1 point
  - Two rows (İkinci Çinko): 2 points
  - Full board (Tombala): 3 points

## License

MIT License
