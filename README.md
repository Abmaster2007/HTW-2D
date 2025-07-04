# Hunt the Wumpus 2D

A modern web-based reimagining of the classic "Hunt the Wumpus" game. This 2D version features a procedurally generated maze, multiple hazards, difficulty settings, and user account support with a global leaderboard.

---

## 🎮 Features

### 🧭 Main Menu
- **Play** – Start the game (requires login)
- **Login / Signup** – Manage user authentication
- **Leaderboard** – View top scores by user, difficulty, and time
- **Difficulty Selection** – Choose between Easy, Normal, and Hard
- **Logout** – Securely end your session
- **User Status** – Displays “Logged in: {user}” in the UI
- **Responsive UI** – Centered, boxed layout for clean presentation

### 🕹️ Gameplay
- **Authentication Required** – Only logged-in users can play
- **Central Game Display** – Game is rendered in a centered rectangle
- **Onboarding Flow** – Includes caution, controls, and story screens
- **Randomized Setup** – Hunter and Wumpus spawn in non-overlapping locations
- **Hazards** – Randomly placed bottomless pits and stationary superbats
- **Limited Vision** – Hunter sees only 3 adjacent paths
- **Player Actions** – Choose to move or shoot, with hazard proximity cues
- **Timer** – Starts when the game begins, used for leaderboard scoring

### 🧍 Main Character (Hunter)
- **Arrows** – Starts with a variable number based on difficulty
- **Movement** – Can move to valid adjacent rooms
- **Encounters** – Superbat teleports, pitfall ends game
- **Resource Management** – Arrows are consumed when shooting

### 🐉 Wumpus
- **Behavior** – Starts asleep; wakes if an arrow is missed
- **AI Movement** – Pursues the hunter using pathfinding when awake
- **Defeat Conditions** – Can be killed by an arrow or fall into a pit

### ⚠️ Hazards
- **Bottomless Pits** – Stationary; falling in ends the game
- **Superbats** – Stationary; teleport the hunter to a random location

### 🎚️ Difficulty Settings
- **Easy** – 5 arrows, full vision, slow Wumpus, fewer hazards
- **Normal** – 3 arrows, limited vision, standard Wumpus behavior
- **Hard** – 1 arrow, no visual cues, fast Wumpus, more hazards

### 🔐 Authentication
- **Login** – Username and password required
- **Signup** – Create a new account with unique credentials
- **Validation** – Clear feedback for invalid or duplicate entries
- **UI Design** – Forms are boxed and styled for clarity

---

## ✅ Requirements Checklist

- [x] Main menu with play, login, signup, leaderboard, difficulty, logout, and user status
- [x] Game access restricted to authenticated users
- [x] Centralized, boxed game display
- [x] Onboarding screens: caution, controls, and story
- [x] Randomized placement of hunter and Wumpus
- [x] Stationary bottomless pits and superbats
- [x] Limited vision for hunter
- [x] Move and shoot actions with hazard cues
- [x] Game timer for leaderboard scoring
- [x] Arrow inventory and consumption logic
- [x] Validated movement with feedback
- [x] Superbat and pit interactions
- [x] Wumpus AI: sleep, wake, pursue, and defeat logic
- [x] Difficulty settings affect gameplay variables
- [x] Login and signup with validation and feedback
- [x] Styled and responsive UI for all forms and menus

---

## 🚀 Installation & Running

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/htw-2d.git
   cd htw-2d
