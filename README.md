# HTW 2D

# Main menu

* [ ] 1: The menu should have a play button that lets the player start the game if they have an account. 
* [ ] 2: The menu should have a login button under that leads to the login page.
* [ ] 3: The menu should have a signup button under that takes the user to the signup page.
* [ ] 4: The menu should have a leaderboard on the left that displays the "user:difficulty:time" from either descending/ascending order for time and sorted by a single difficulty.
* [ ] 5: The menu should have a background around the menu that plays the animation of the main character getting chased by the wumpus.
* [ ] 6: In the bottom left of the main menu, there should be a text that says "Logged in: {user}" when logged in or signed up that should be boxed in.
* [ ] 7: The menu should be centered in the middle of the screen that is enclosed in a box.
* [ ] 8: The menu should have a difficulty button between the login and play button that modifies the behaviour of the enemies and the main character, ranged from Easy, Normal, and Hard.

# 1. The game
* [ ] 1.1: If the user is logged in, start the game. Else, tell the player that they do not have an account signed in and lead the player to the login page.
* [ ] 1.2: The game should be displayed in a rectangle box in the center of the screen.
* [ ] 1.3: The game should display the cautions such as being a scary game and loud noises and has a button to continue to the next screen
* [ ] 1.4: The game should then display the controls of the game such as movement, actions, and rules and has a button to continue to the next screen
* [ ] 1.5: The game should then display the story of the game and has a button to continue to the next screen.
* [ ] 1.6: The game should generate the cave in the shape of a dodecahedron.
* [ ] 1.7: The game should put the main character in a random area that does not occupy the same spot as the wumpus.
* [ ] 1.8: The game should put the wumpus in a random area that does not occupy the same spot as the main character.
* [ ] 1.9: The game should put 'n' amount of bottomless pits in random areas that does not occupy both the main character and the wumpus.
* [ ] 1.10: The game should put 'n' amount of superbats in random areas that does not occupy the main character, wumpus, and bottomless pits.
* [ ] 1.10: The game should limit the main character's vision to 3 viewable paths that shows the user where can they go.
* [ ] 1.11: The game should give the user options on what he can do such as "Move" and "Shoot" and give cues on whether the wumpus, bottomless pit or superbat is nearby.
* [ ] 1.12: When the game is started, set the game's status to True and start the timer.

# 1.7 The main character
* [ ] 1.7.1: The main character should have 'n' arrows.
* [ ] 1.7.2: The main character should choose how many rooms for the arrow to shoot through.
* [ ] 1.7.3: If the chosen points are connected with each other, shoot in that path. Else, shoot in a random path with the given amount of rooms.
* [ ] 1.7.4: The main character should get rid of 1 arrow when used.
* [ ] 1.7.5: The main character should be able to move in one of the 3 spaces
* [ ] 1.7.6: If that space is valid, move to that spot. Else, tell the user that this space is not valid.
* [ ] 1.7.7: If that space has a superbat, move the player to a random spot of the cave. Else, check the next condition
* [ ] 1.7.8: If that space has a bottomless pit, set the game's status to False, telling the user that they falled into the pit, discarding the timer.
* [ ] 1.7.9: If the main character has no arrows, set the game's status to False, telling 

# 1.8 The wumpus
* [ ] 1.8.1: The wumpus should be asleep as default when started.
* [ ] 1.8.2: The wumpus should be able to wake up if an arrow is shot and missed as a boolean.
* [ ] 1.8.3: If the wumpus is awake, start moving to the main character using an algorithm as a delay using an algorithm. Else, stay asleep in the same spot.
* [ ] 1.8.4: If the wumpus was shot/fall into the pit, set the game's status to False, telling the user that they killed the wumpus/wumpus fell into the pit from a superbat, ending the timer and send it to the leaderboard if the player killed it.
* [ ] 1.8.4: If the wumpus was shot/fall into the pit, set the game's status to False, telling the user that they killed the wumpus/wumpus fell into the pit from a superbat, ending the timer an

# 1.9 Bottomless pit
* [ ] 1.9.1: The bottomless pit should be stationary

# 1.10 Super bats
* [ ] 1.10.1: The Super bats should remain stationary.

# 8 Difficulty
* [ ] 8.1: If the difficulty is set to easy, change the main character's arrow count to 5, he can see what is in the 3 paths, the movement from the wumpus is slow, less bottomless pits and superbats.
* [ ] 8.2: If the difficulty is set to medium, it is the standard default settings, 3 arrows, main character's vision is lacking, wumpus moving at a default rate with a chance of movingm, normal amount of bottomless pits and superbats.
* [ ] 8.3: If the difficulty is set to hard, the main character has 1 arrow, no visual cues, wumpus is on the move in a faster rate with a guarantee chance of moving, more superbats and bottomless p

# 2. Login page

* [ ] 2.1: There should be an input field "Username" for username in str form.
* [ ] 2.2: There should be an input field "Password" for password in str form.
* [ ] 2.3: There should be a button "Login" that confirms the form for username and password. 
* [ ] 2.4: If user exist, go back to the main menu with the text "logged in: {user}" added to the main menu. If not, alert the user that the username or password doesn't exist.
* [ ] 2.5: The form should be closed in a box that is in the center of the screen.
* [ ] 2.6: There should be text "Don't have an account?" above the button "Signup" at the bottom left of the form that takes the user to the signup page.

# 3. Signup page
* [ ] 3.1: There should be an input field for username in str form.
* [ ] 3.2: There should be an input field for password in str form.
* [ ] 3.3: There should be a button "Signup" that checks the credentials if the user exists or not.
* [ ] 3.4: If the username exists in the database, alert the user that this username already exists and take them back to the signup page. Else, Take them back to the main menu with the text "Logged in: {user}" added to the main menu.
* [ ] 3.5: The form should be closed in a box that is in the center of the screen.
* [ ] 3.6: There should be text "You have an account?" above the button "Login" at the bottom left of the form that takes the user to the login page.