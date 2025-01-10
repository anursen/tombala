class TombalaGame {
    constructor() {
        this.socket = io();
        this.boardNumbers = [];
        this.markedNumbers = new Set();
        this.gameActive = false;
        this.connected = false;
        
        this.initializeEventListeners();
        this.initializeSocketIO();
        this.initializeNumberBucket();
    }

    initializeSocketIO() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            document.getElementById('joinGameBtn').disabled = false;
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            document.getElementById('joinGameBtn').disabled = true;
            document.getElementById('startGameBtn').disabled = true;
        });

        this.socket.on('board', (data) => {
            this.renderBoard(data.board);
        });

        this.socket.on('drawnNumber', (data) => {
            this.handleDrawnNumber(data.number);
        });

        this.socket.on('gameState', (data) => {
            this.updateGameState(data);
        });

        this.socket.on('playerUpdate', (data) => {
            this.updatePlayers(data.players);
        });
    }

    initializeEventListeners() {
        document.getElementById('joinGameBtn').addEventListener('click', () => this.joinGame());
        document.getElementById('startGameBtn').addEventListener('click', () => this.startGame());
    }

    renderBoard(board) {
        this.boardNumbers = board;
        const tableHtml = board.map(row => `
            <tr>${row.map(num => `
                <td class="board-number">${num || ''}</td>
            `).join('')}</tr>
        `).join('');
        document.getElementById('playerBoard').innerHTML = tableHtml;
    }

    handleDrawnNumber(number) {
        const currentNumber = document.querySelector('.current-number');
        currentNumber.textContent = number;

        // Mark numbers on board
        document.querySelectorAll('.board-number').forEach(cell => {
            if (cell.textContent == number) {
                cell.classList.add('marked');
                this.markedNumbers.add(Number(number));
                this.checkWinConditions();
            }
        });

        // Mark number in bucket
        const bucketNumber = document.querySelector(`.bucket-number[data-number="${number}"]`);
        if (bucketNumber) {
            bucketNumber.classList.add('drawn');
        }
    }

    updateGameState(state) {
        this.gameActive = state.active;
        const startBtn = document.getElementById('startGameBtn');
        startBtn.disabled = !state.canStart;
        
        // Show who can start the game
        if (state.canStart) {
            startBtn.classList.add('ready');
            startBtn.title = 'Click to start the game';
        } else {
            startBtn.classList.remove('ready');
            startBtn.title = 'Waiting for more players';
        }
        
        const statusElement = document.querySelector('.game-status');
        statusElement.textContent = state.message || 'Waiting for players...';
    }

    updatePlayers(players) {
        const playersHtml = players.map(player => `
            <div class="player-card ${player.achievements.includes('Tombala') ? 'winner' : ''}">
                <div class="player-info">
                    <div class="player-name">${player.name}</div>
                    <div class="player-score">Total Score: ${player.score}</div>
                </div>
                <div class="player-achievements">
                    ${player.achievements.filter(a => a).map(achievement => 
                        player.score > 0 ? `<span class="achievement">${achievement}</span>` : ''
                    ).join('')}
                </div>
            </div>
        `).join('');
        document.getElementById('playersList').innerHTML = playersHtml;
    }

    checkWinConditions() {
        const rows = [0, 0, 0];
        this.boardNumbers.forEach((row, i) => {
            if (row.every(num => this.markedNumbers.has(num))) {
                rows[i] = 1;
            }
        });

        const completedRows = rows.reduce((a, b) => a + b, 0);
        if (completedRows > 0) {
            this.socket.emit('win', { rows: completedRows });
        }
    }

    joinGame() {
        this.socket.emit('join');
    }

    startGame() {
        this.socket.emit('start');
    }

    initializeNumberBucket() {
        const bucket = document.getElementById('numberBucket');
        let html = '';
        for (let i = 0; i < 9; i++) {
            html += '<div class="bucket-row">';
            for (let j = 1; j <= 10; j++) {
                const number = i * 10 + j;
                if (number <= 90) {
                    html += `<div class="bucket-number" data-number="${number}">${number}</div>`;
                }
            }
            html += '</div>';
        }
        bucket.innerHTML = html;
    }
}

const game = new TombalaGame();
