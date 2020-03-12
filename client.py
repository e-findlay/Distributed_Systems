import Pyro4
import time
import Pyro4.errors
import json

class Client():

    def __init__(self, front_end_server):
        print("Welcome to Just Hungry!")
        self.front_end_server = front_end_server
        self.logged_in = False
        self.username = None
        while True:
            self.processInput()

        
    def processInput(self):
        # Check client is logged in
        while not self.logged_in:
            print("Enter 1 to create an account")
            print("Enter 2 to login")
            user_input = input("Enter your choice:\n")
            # Check user-input is valid
            while user_input not in ['1', '2']:
                user_input = input("Invalid choice! Please try again!:\n")
            if user_input == '1':
                # Register User account
                username = input("Please enter a Username:  ")
                password = input("Please enter a Password:  ")
                self.createUser(username, password)
            elif user_input == '2':
                # Sign in already registered user
                username = input("Please enter your Username:\n")
                password = input("Please enter your Password:\n")
                self.loginUser(username, password)
        # Check user is logged in
        while self.logged_in:
            print("Enter 1 to list orders")
            print("Enter 2 to make an order")
            print("Enter 3 to change an order")
            print("Enter 4 to cancel an order")
            print("Enter 5 to see other online users")
            print("Enter 6 to logout")
            user_input = input("Enter your Choice:\n")
            print(user_input)
            # Check user input is valid
            while user_input not in ['1','2','3', '4','5', '6']:
                user_input = input("Invalid choice! Please try again:\n")
            # Get All Orders sumbitted by the logged in user
            if user_input == '1':
                self.retrieveOrders(self.username)
            # Submit an order
            elif user_input == '2':
                post_code = input("Please enter your post code:\n ")
                post_code = post_code.replace(" ", "")
                items = self.listMenuItems()
                num_items = len(items)
                ordered = False
                order_items = []
                print('0. Submit Order')
                while user_input !='0':
                    user_input = input("Select your food:\n")
                    print(user_input)
                    for i in range(1, num_items+1):
                        if str(i) == user_input:
                            order_items += [items[i-1]]
                            ordered = True
                if ordered:
                    print(order_items)
                    self.submitOrder(self.username, order_items, post_code)
                else:
                    print('You did not order any items!')
            # Change an existing order
            elif user_input == '3':
                retrieved = self.retrieveOrders(self.username)
                if not retrieved:
                     return
                not_integer = True
                while not_integer:
                    try:
                        order_id = int(input('Please enter the number of the order you would like to change\n'))
                        not_integer = False
                    except:
                        print("Order ID must be an integer!")
                post_code = input("Please enter your post code:\n")
                post_code = post_code.replace(" ", "")
                items = self.listMenuItems()
                num_items = len(items)
                ordered = False
                order_items = []
                print('0. Submit Order')
                while user_input not in ['0']:
                    user_input = input("Select your food:\n")
                    for i in range(1, num_items+1):
                        if str(i) == user_input:
                            order_items += [items[i-1]]
                            ordered = True
                if ordered:
                    self.changeOrder(self.username, order_id, order_items, post_code)
                else:
                    print('You did not order any items!')
            # Cancel an existing order
            elif user_input == '4':
                retrieved = self.retrieveOrders(self.username)
                if not retrieved:
                    return
                not_integer = True
                while not_integer:
                    try:
                        order_id = int(input('Please enter the number of the order you would like to cancel\n'))
                        not_integer = False
                    except:
                        print("Order ID must be an integer!")
                self.cancelOrder(self.username, order_id)
            # Get list of all users currently logged in
            elif user_input == '5':
                self.getUsers()
            # logout
            else:
                self.logout(self.username)

        
        
    def submitOrder(self, username, items, post_code):
        try:
            response = self.front_end_server.addOrder(username, items, post_code)
            response = json.loads(response)
            if "Error" in response.keys():
                print("Error: ", response["Error"])
                return
            print("Order Confirmed!")
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")

    def cancelOrder(self, username, order_id):
        try:
            response = self.front_end_server.cancelOrder(username, order_id)
            response = json.loads(response)
            if "Error" in response.keys():
                print("Error: ", response["Error"])
                return
            print("Order {} has been cancelled!".format(order_id))
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")
    
    def changeOrder(self, username, order_id, items, post_code):
        try:
            response = self.front_end_server.changeOrder(username, order_id, items, post_code)
            response = json.loads(response)
            if "Error" in response.keys():
                print("Error: ", response["Error"])
                return
            print("Order {} has been changed!".format(order_id))
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")
    
    def listMenuItems(self):
        try:
            response = self.front_end_server.getMenuItems()
            response = json.loads(response)
            if "Error" in response.keys():
                print(response["Error"])
                return
            # dsiplay menu on console
            for idx, item in enumerate(response["Success"]):
                print("{}. {}".format(idx+1, item))
            return response["Success"]
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")

    def retrieveOrders(self, username):
        try:
            response = self.front_end_server.getOrders(username)
            response = json.loads(response)
            if "Error" in response.keys():
                print("Error: ", response["Error"])
                return False
            orders = response["Success"]
            print("Orders:")
            for order in orders:
                print("ID:{}. Deliver_To:{}, Order:{}".format(order[0], order[1][1], ", ".join(order[1][0])))
            return True
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")
            return False

    def loginUser(self, username, password):
        try:
            response = self.front_end_server.authenticateUser(username, password)
            response = json.loads(response)
            if "Error" in response.keys():
                print("Error: ", response["Error"])
                return
            self.logged_in = True
            self.username = username
            print("Hello {}! You are logged in!".format(username))
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")

                    
    def createUser(self, username, password):
        try:
            response = self.front_end_server.createUser(username, password)
            response = json.loads(response)
            if "Error" in response.keys():
                print("Error: ", response["Error"])
                return
            print("Hello {}! Your account has been created".format(username))
            self.logged_in = True
            self.username = username
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")
                    
    def logout(self, username):
        try:
            response = self.front_end_server.logout(username)
            response = json.loads(response)
            if "Error" in response.keys():
                print("Error: ", response["Error"])
                return
            if response:
                self.logged_in = not response
                self.username = None
                print("You are logged out!")
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")

    def getUsers(self):
        try:
            response = self.front_end_server.getUsers()
            response = json.loads(response)
            if "Error" in response.keys():
                print("Error: ", response["Error"])
                return
            # print logged in users on console
            for user in response["Success"]:
                print("{}".format(user))
        except Pyro4.errors.TimeoutError:
            print("Error: Request Timed Out!")
                    
        
try:
    Pyro4.config.COMMTIMEOUT = 0
    uri = Pyro4.resolve("PYRONAME:Front_End_Server")
    front_end_server = Pyro4.Proxy(uri)
    # set timeout to front end to 5 seconds
    front_end_server._pyroTimeout = 5
    client = Client(front_end_server)
except Pyro4.errors.NamingError:
    print("Error: Could not connect to Front End Server!")

