# HTW-2D

# Main menu

- [] 1: The menu should have a play button that lets the player start the game if they have an account. 
- [] 2: The menu should have a login button that leads to the login page.
- [] 3: The menu should have a signup button that takes the user to the signup page.
- [] 4: The menu should have a leaderboard on the left that displays the score from descending order.
- [] 5: The menu should have a background that plays the animation of the main character getting chased by the wumpus.
- [] 6: In the bottom left of the main menu, there should be a text that says "Logged in: {user}" when logged in or signed up that should be boxed in.
- [] 7: The menu should be centered in the middle of the screen that is enclosed in a box.

# 1. The game
- [] 1.1: If the user is logged in, start the game. Else, tell the player that they do not have an account signed in and lead the player to the login page.
- [] 1.2: The game should be displayed in a rectangle box in the center of the screen.
- [] 1.3: The game should display the cautions such as being a scary game and loud noises and has a button to continue to the next screen
- [] 1.4: The game should then display the controls of the game such as movement, actions, and rules and has a button to continue to the next screen
- []1.5: The game should then display the story of the game and has a button to continue to the next screen.

# 2. Login page

- [] 2.1: There should be an input field "Username" for username in str form.
- [] 2.2: There should be an input field "Password" for password in str form.
- [] 2.3: There should be a button "Login" that confirms the form for username and password. 
- [] 2.4: If user exist, go back to the main menu with the text "logged in: {user}" added to the main menu. If not, alert the user that the username or password doesn't exist.
- [] 2.5: The form should be closed in a box that is in the center of the screen.
- [] 2.6: There should be text "Don't have an account?" above the button "Signup" at the bottom left of the form that takes the user to the signup page.

# 3. Signup page

- [] 3.1: There should be an input field for username in str form.
- [] 3.2: There should be an input field for password in str form.
- [] 3.3: There should be a button "Signup" that checks the credentials if the user exists or not.
- [] 3.4: If the username exists in the database, alert the user that this username already exists and take them back to the signup page. Else, Take them back to the main menu with the text "Logged in: {user}" added to the main menu.
- [] 3.5: The form should be closed in a box that is in the center of the screen.
- [] 3.6: There should be text "You have an account?" above the button "Login" at the bottom left of the form that takes the user to the login page.