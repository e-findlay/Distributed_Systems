# Distributed_Systems

## Start Instructions
1. Open a terminal and enter `python -m Pyro4.naming` to start the Name Server.
2. Open a terminal and enter `python -m front_end` to start the front end server.
3. Open a terminal and enter `python -m server` to start a backend server.
4. Repeat step 3 for the number of replicas you require.
5. Open a terminal and enter `python -m client` to start the client application.

## Features
The client offers the flowing features:

Account Creation: - user can create an account with a username and password

Login: - user can login to an existing account with a correct username and password

Get Orders: - user can view all orders they have submitted to the system

Submit Order: - users can submit an order to the system

Change Order: - user can change the post code or items of an order they have submitted

Cancel Order: - user can cancel an order they have submitted. This order will no longer be returned by Get Orders

Get Users: - user can view all other users currently using the system

Logout: - user can logout of the system
