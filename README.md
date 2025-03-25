# Social Messaging

#### Video Demo: https://youtu.be/ZVxuM-9vcgI 

#### Description:
Social Messaging is a web-based messaging platform that allows users to connect with friends and exchange messages in a secure environment. Built using Flask and SQLite, this application provides a comprehensive social networking experience with features such as user registration, friend management, and a messaging system.

It is my CS50x 2025 final project. It was built upon the CS50x 2025 'Finance' problem set code.

## Project Overview

This project was developed as my final submission for Harvardx's CS50 course. The goal was to create a functional web application that demonstrates my proficiency in web development, database management, and user authentication. Social Messaging accomplishes this by providing a platform where users can:

1. Register and log in
2. Search for and connect with friends
3. Send and receive messages
4. Manage their inbox and friend connections, including deleting messages and removing friends

The application uses a Flask backend with a SQLite database to store user information, friend connections, and messages. The frontend is built using HTML, CSS, and JavaScript with Bootstrap for responsive design.

## File Structure and Functionality

### `app.py`
The main application file that contains all the Flask routes and application logic. This file handles:
- User authentication (registration, login, logout)
- Friend management (sending, accepting, and rejecting friend requests)
- Messaging functionality (sending, reading, and deleting messages)
- Rendering templates and processing form submissions

Key routes include:
- `/register` and `/login` for user authentication (levraging the code from 'Finance')
- `/search` for finding potential friends
- `/friends` for viewing current connections
- `/requests` for managing friend requests
- `/inbox` for viewing messages
- `/send` and `/send_message` for composing and sending messages
- `/trash` for viewing deleted messages

### `helpers.py`
This file is a modified version of the fiance helper.py, it contains utility functions that support the main application:
- `apology()`: Renders error messages to users (using my custom image and error box)
- `login_required()`: A decorator function that restricts access to certain routes for authenticated users only

### `messaging.db`
A SQLite database that stores all application data with the following tables:
- `users`: Stores user information (username, password hash, full name, country), it includes over 100 sample users
- `friends`: Tracks friend connections and their status (pending, accepted)
- `messages`: Stores all messages with sender, receiver, content, and status information

It is important to note, that I did not end up using all the columns from my original design, such as 'is_read', I plan to levrage them as I continute to enhance this app.

### `templates/`
Contains all HTML templates for rendering the web pages (Layout.html took inspiration from the Finance layout with some modifications):
- `layout.html`: The base template that defines the overall structure of the site
- `register.html` and `login.html`: Forms for user authentication
- `index.html`: The dashboard serving as 'home page' showing user statistics such as how many incoming messages are in their inbox, how many friends they have and how many pedning friend requests require the user's attention
- `search.html`: Interface for finding friends and displaying the search results inline in a table format, each result include an action button to 'Invite' a friend to connect
- `friends.html`: Displays the user's current friends with the ability to send a message or remove a friend connection
- `requests.html`: Shows pending friend requests as well as the status of sent requests (with color code for the 3 main status, red for Rejected, Orange fpr Pending and Green for Accepted)
- `inbox.html`: Displays incoming and outgoing messages with related actions. Incoming messages include the actions to Read, Reply and Delete (which sends messages to the trash); Sent messages include the option to Read messages and delete them (also sends them to the 'Trash')
- `send.html` and `reply.html`: Forms for composing messages. Send is when sending a message from the Friedns page and reply is when replying to a message from Inbox page.
- `trash.html`: Shows deleted messages with the ability to "Purge" mesages, this action will delete the message from the database and I used a simple JS 'OnClick' script to display a warning to the user.
- `apology.html`: Error page template that will display custom error text and a local image (a meme of Captain Picard from Star Trek ;)

### `static/`
Contains static files such as:
- `styles.css`: Custom CSS styling
- `sm_logo.png`: The 'Social Messaging' application logo
- `favicon.ico`: The site favicon
- `local_apology_image.png`: The image that will be displayed in error screen

### `requirements.txt`
Lists all Python dependencies required to run the application:
- `cs50`: CS50 library for database operations
- `Flask`: The web framework
- `Flask-Session`: For session management
- `pytz`: For timezone handling
- `requests`: For HTTP requests

## Design Choices

### User Authentication
I implemented a secure authentication system using Werkzeug's password hashing functions. This ensures that user passwords are never stored in plain text in the database. The registration process collects essential information like full name and country to create a more personalized experience.

### Friend Connection System
I designed the friend system to mimic real-world social connections:
1. Users can search for potential friends by name
2. Friend requests must be sent and accepted before a connection is established
3. Users can view pending requests, sent requests, and manage their friend list

This two-way confirmation process ensures that connections are mutual and consensual, enhancing the social aspect of the platform.

### Messaging System
The messaging functionality was designed with simplicity and privacy in mind:
1. Messages can only be sent between connected friends
2. Users can view both incoming and outgoing messages in their inbox
3. Messages can be deleted (moved to trash) or permanently purged
4. The interface uses popovers to display message content, keeping the inbox clean and organized

### User Interface
I chose a dark-themed interface with multiple Bootstrap elements (buttons, tables, cards, input forms, etc.) for several reasons:
1. It provides a modern, visually appealing look
2. The responsive design works well on various screen sizes
3. The consistent navigation bar makes the application intuitive to use
4. Color coding helps differentiate between incoming and outgoing messages
5. The popper element for reading messages in-place was a very cool element I decided to adopt after reviewing the Bootstrap docs. It was exteremly helpful as it prevents the user from navigating away from the screen there were on

## Challenges and Solutions

One of the main challenges was designing an efficient database schema that could handle the relationships between users, friends, and messages. I decided to use separate tables with foreign key relationships to maintain data integrity while allowing for flexible queries.

Another challenge was implementing the friend request system with different states (pending, accepted). I solved this by adding a status field to the friends table and creating appropriate routes to handle the various actions a user might take.

For the messaging system, I wanted to allow users to "delete" messages without permanently removing them from the database. My solution was to implement a status field for messages that could be updated to "deleted" when a user removes a message, with a separate trash view to display these messages.

## Future Improvements

While the current version of Social Messaging provides a solid foundation, there are several enhancements I would like to implement in the future:

1. Real-time messaging using WebSockets
2. Profile customization options (ability to upload profile picture, bio and change password)
3. Group messaging capabilities
4. Message read receipts
5. Media sharing (images, files)

## Conclusion

Social Messaging demonstrates the application of web development principles learned throughout CS50. By combining a Flask backend with a SQLite database and a Bootstrap frontend (HTTP, CSS and JavaScript), I've created a functional social platform that allows users to connect and communicate securely. 

