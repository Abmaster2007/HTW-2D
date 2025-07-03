/**
 * Gameplay script for the Wumpus Hunt game.
 * This script handles the game logic, rendering, and user interactions.
 * It initializes the game, manages the hunter's movements, handles shooting,
 * and updates the game state based on interactions with the Wumpus, bats, and pits.
 * It also manages the game loop and end conditions.
 */

const hunterSprites = {
    up: new Image(),
    down: new Image(),
    left: new Image(),
    right: new Image(),
    vignette: new Image()
};
hunterSprites.up.src = '/static/img/hunter_up.png';
hunterSprites.down.src = '/static/img/hunter_down.png';
hunterSprites.left.src = '/static/img/hunter_left.png';
hunterSprites.right.src = '/static/img/hunter_right.png';
hunterSprites.vignette.src = '/static/img/vignette.png';

const wumpusImg = new Image();
wumpusImg.src = '/static/img/wumpus.png';

const batImg = new Image();
batImg.src = '/static/img/superbat.png';

const pitImg = new Image();
pitImg.src = '/static/img/pit.png';


// Pause menu audio immediately when this script loads
const bgAudio = document.getElementById('backgroundAudio');
if (bgAudio) {
    bgAudio.pause();
    bgAudio.currentTime = 0;
}
// Play gameplay audio
const gameplayAudio = document.getElementById('gameplayAudio');
if (gameplayAudio) {
    gameplayAudio.currentTime = 0;
    gameplayAudio.play();
}

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const tileSize = 100;

let startTime = null;
let endTime = null;
let gameEnded = false;
let maze = [];
let hunter = {};
let wumpus = {};
let bullets = [];
let lastDirection = 'up';

let hunterAmmo = gameConfig.hunterAmmo;
let visionRadius = gameConfig.visionRadius;
let wumpusSpeed = gameConfig.wumpusSpeed;
let wumpusAggressive = gameConfig.wumpusAggressive;
let difficulty = gameConfig.difficulty;
let multiplier = gameConfig.multiplier;


let wumpusInterval = null;
let gameLoopStarted = false;

let bats = [];
let pits = [];

function drawMaze() {
    for (let y = 0; y < maze.length; y++) {
        for (let x = 0; x < maze[y].length; x++) {
            const distance = Math.sqrt((hunter.x - x) ** 2 + (hunter.y - y) ** 2);
            ctx.fillStyle = distance <= visionRadius ? (maze[y][x] === 1 ? 'white' : 'black') : 'black';
            ctx.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
        }
    }
}

function drawHunter() {
    
    let img = hunterSprites[lastDirection] || hunterSprites.down;
    ctx.drawImage(
        img,
        hunter.x * tileSize, hunter.y * tileSize,
        tileSize, tileSize
    );
    
}

function drawWumpus() {
    if (!wumpus || !wumpus.alive) return;
    const distance = Math.sqrt((hunter.x - wumpus.x) ** 2 + (hunter.y - wumpus.y) ** 2);
    if (distance <= visionRadius) {
        ctx.drawImage(
            wumpusImg,
            wumpus.x * tileSize, wumpus.y * tileSize,
            tileSize, tileSize
        );
    }
}

function drawBullets() {
    ctx.fillStyle = 'red';
    bullets.forEach((bullet, index) => {
        if (bullet.direction === 'up') bullet.y -= 5;
        else if (bullet.direction === 'down') bullet.y += 5;
        else if (bullet.direction === 'left') bullet.x -= 5;
        else if (bullet.direction === 'right') bullet.x += 5;

        const mazeX = Math.floor(bullet.x / tileSize);
        const mazeY = Math.floor(bullet.y / tileSize);

        if (
            (maze[mazeY] && maze[mazeY][mazeX] === 0) ||
            (mazeX === wumpus.x && mazeY === wumpus.y)
        ) {
            if (mazeX === wumpus.x && mazeY === wumpus.y) {
                console.log('Wumpus defeated!');
            }
            bullets.splice(index, 1);
        } else {
            ctx.beginPath();
            ctx.arc(bullet.x, bullet.y, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.closePath();
        }
    });
}

// Draw Super Bats
function drawBats() {
    bats.forEach(bat => {
        const distance = Math.sqrt((hunter.x - bat.x) ** 2 + (hunter.y - bat.y) ** 2);
        if (distance <= visionRadius) {
            ctx.drawImage(
                batImg,
                bat.x * tileSize, bat.y * tileSize,
                tileSize, tileSize
            );
        }
    });
}

// Draw Bottomless Pits
function drawPits() {
    pits.forEach(pit => {
        const distance = Math.sqrt((hunter.x - pit.x) ** 2 + (hunter.y - pit.y) ** 2);
        if (distance <= visionRadius) {
            ctx.drawImage(
                pitImg,
                pit.x * tileSize, pit.y * tileSize,
                tileSize, tileSize
            );
        }
    });
}

function drawVignette() {
    const vignette = hunterSprites.vignette;
    // The size of the vignette should cover the vision area
    const vignetteSize = tileSize * visionRadius * 3;
    // Center of the hunter in pixels
    const hunterCenterX = hunter.x * tileSize + tileSize / 2;
    const hunterCenterY = hunter.y * tileSize + tileSize / 2;
    // Top-left corner for the vignette so it's centered on the hunter
    const vignetteX = hunterCenterX - vignetteSize / 2;
    const vignetteY = hunterCenterY - vignetteSize / 2;

    ctx.drawImage(
        vignette,
        vignetteX,
        vignetteY,
        vignetteSize,
        vignetteSize
    );
}

function gameLoop() {
    if (gameEnded) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    console.log("Game loop running");
    drawMaze();
    drawPits();
    drawBats();
    drawHunter();
    drawWumpus();
    drawBullets();
    drawVignette();
    requestAnimationFrame(gameLoop);
}

function updateGameState(data) {
    maze = data.maze || maze;
    hunter = data.hunter || hunter;
    wumpus = data.wumpus || wumpus;
    bats = data.bats || bats;
    pits = data.pits || pits;
    drawHunter();
    drawWumpus();
    drawVignette();
    document.getElementById('ammoValue').textContent = hunter.ammo;
    checkEndState();
}

function moveHunter(direction) {
    fetch('/move_hunter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction: direction })
    })
    .then(response => response.json())
    .then(data => {
        updateGameState(data);
    })
    .catch(error => console.error('Error moving hunter:', error));
}

function shootHunter() {
    if (hunter.ammo <= 0) {
        console.log('No ammo left!');
        return;
    }
    bullets.push({
        x: hunter.x * tileSize + tileSize / 2,
        y: hunter.y * tileSize + tileSize / 2,
        direction: lastDirection,
    });

    fetch('/shoot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction: lastDirection })
    })
    .then(response => response.json())
    .then(data => {
        updateGameState(data);
    })
    .catch(error => console.error('Error handling shoot:', error));
}

function checkEndState() {
    if (!wumpus.alive) {
        showEndScreen(true);
    } else if (hunter.dead) {
        if (hunter.fell) {
            showEndScreen(false, "You fell into a bottomless pit!");
        } else {
            showEndScreen(false);
        }
    }
}

function handleKeyDown(event) {
    if (gameEnded) return;
    const key = event.key.toLowerCase();
    let direction = null;
    if (key === 'w') {
        direction = 'up';
        lastDirection = 'up';
    } else if (key === 'a') {
        direction = 'left';
        lastDirection = 'left';
    } else if (key === 's') {
        direction = 'down';
        lastDirection = 'down';
    } else if (key === 'd') {
        direction = 'right';
        lastDirection = 'right';
    } else if (key === ' ') {
        shootHunter();
        return;
    }
    if (direction) {
        moveHunter(direction);
    }
}

function showInstructions() {
    document.getElementById('precautionScreen').style.display = 'none';
    document.getElementById('instructionsScreen').style.display = 'block';
    document.getElementById('instructionsNext').focus();
}

function showStory() {
    document.getElementById('instructionsScreen').style.display = 'none';
    document.getElementById('storyScreen').style.display = 'block';
    document.getElementById('storyNext').focus();
}

function startGame() {
    const gameArea = document.getElementById('gameArea');
    
    if (gameArea.requestFullscreen) {
        gameArea.requestFullscreen();
    } else if (gameArea.mozRequestFullScreen) { // Firefox
        gameArea.mozRequestFullScreen();
    } else if (gameArea.webkitRequestFullscreen) { // Chrome, Safari and Opera
        gameArea.webkitRequestFullscreen();
    } else if (gameArea.msRequestFullscreen) { // IE/Edge
        gameArea.msRequestFullscreen();
    }

    document.getElementById('storyScreen').style.display = 'none';
    document.getElementById('gameArea').style.display = 'block';
    document.getElementById('htmlElement').style.backgroundColor = 'black';
    document.getElementById('pageTitle').style.display = 'none';
    startGameTimer();

    // Fetch initialized game state from the backend
    fetch('/initialize')
        .then(response => response.json())
        .then((data) => {
            maze = data.maze;
            hunter = data.hunter;
            wumpus = data.wumpus;
            bats = data.bats;
            pits = data.pits;
            document.getElementById('ammoValue').textContent = hunter.ammo;
            visionRadius = data.vision_radius;
            wumpusSpeed = data.wumpus_speed;
            wumpusAggressive = data.wumpus_aggressive;
            multiplier = data.multiplier;
            canvas.width = maze[0].length * tileSize;
            canvas.height = maze.length * tileSize;
            drawMaze();
            drawHunter();
            drawWumpus();
            drawBats();
            drawPits();
            if (!gameLoopStarted) {
                document.addEventListener('keydown', handleKeyDown);
                gameLoopStarted = true;
                gameLoop();
            }
            if (wumpusInterval) clearInterval(wumpusInterval);
            wumpusInterval = setInterval(() => {
                fetch('/move_wumpus', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    updateGameState(data);
                })
                .catch(error => console.error('Error moving Wumpus:', error));
            }, wumpusSpeed);
        })
        .catch(error => console.error('Error fetching game state:', error));
}

function startGameTimer() {
    startTime = Date.now();
}

function endGameTimer() {
    endTime = Date.now();
    return ((endTime - startTime) / 1000).toFixed(2);
}

function showEndScreen(win, customMessage) {
    gameEnded = true;
    if (wumpusInterval) clearInterval(wumpusInterval);
    document.removeEventListener('keydown', handleKeyDown);
    document.getElementById('gameArea').style.display = 'none';
    const endScreen = document.createElement('div');
    endScreen.id = 'endScreen';
    endScreen.style.textAlign = 'center';
    endScreen.style.marginTop = '50px';
    const timeTaken = endGameTimer();
    endScreen.innerHTML = `
        <h1>${win ? "You Won!" : "Game Over"}</h1>
        ${customMessage ? `<p>${customMessage}</p>` : ""}
        <p>Time: <span id="finalTime">${timeTaken}</span> seconds</p>
        <button onclick="tryAgain()">Try Again</button>
        <button onclick="goToMenu()">Back to Difficulty Selector</button>
    `;
    document.body.appendChild(endScreen);

    document.getElementById('gameplayAudio').pause();

    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else if (document.mozFullScreenElement) { // Firefox
        document.mozCancelFullScreen();
    } else if (document.webkitFullscreenElement) { // Chrome, Safari and Opera
        document.webkitExitFullscreen();
    } else if (document.msFullscreenElement) { // IE/Edge
        document.msExitFullscreen();
    }

    if (win) {
        document.getElementById('winnerAudio').currentTime = 0;
        document.getElementById('winnerAudio').play();
        fetch('/submit_score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ time: timeTaken, difficulty: difficulty })
        });
    } else {
        document.getElementById('gameOverAudio').currentTime = 0;
        document.getElementById('gameOverAudio').play();
    }
}

function tryAgain() {
    window.location.reload();
}

function goToMenu() {
    window.location.href = '/';
}

console.log("Difficulty settings:",
    "Ammo:", hunterAmmo,
    "Vision:", visionRadius,
    "Wumpus Speed:", wumpusSpeed,
    "Aggressive:", wumpusAggressive,
    "Multiplier:", multiplier,
    "Difficulty:", difficulty
);