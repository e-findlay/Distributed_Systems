import Pyro4
import Pyro4.errors
import json
import urllib
import urllib.request as request
import random
import uuid
from collections import defaultdict

    
        
class Server():

    def __init__(self):
        self.status = 'active'
        self.server_name = 'server' + str(uuid.uuid4())
        self.menu_items = ['Pizza', 'Burger', 'Curry', 'Fish and Chips',
                           'Coke', 'Lemonade', 'Ice Cream', 'Lasagne']
        self.users = {'Admin': 'test'}
        self.current_users = []
        self.orders = {1: [['Pizza', 'Burger'], 'DH1 4AB']}
        self.user_order = defaultdict(list)
        self.user_order['Admin'] += [1]
        self.front_end = None
        self.o_id = 2


    @Pyro4.expose
    def getUsers(self):
        return json.dumps({"Success": self.current_users})

    

    @Pyro4.expose
    def addOrder(self, username, items, post_code):
        try:
            # Check Post code is valid
            data = request.urlopen('http://api.getthedata.com/postcode/{}'.format(post_code))
            data = json.load(data)
            if data['status'] == 'no_match':
                return json.dumps({"Error": "Invalid Post Code Supplied"})
            order_id = self.o_id
            self.o_id += 1
            self.user_order[username] += [order_id]
            self.orders[order_id] = [items, post_code]
            self.updateReplicas()
            return json.dumps({"Success": "Your Order was Successfully Completed"})
        except:
            return json.dumps({"Error": "Your order could not be processed"})


    @Pyro4.expose
    def changeOrder(self, username, order_id, items, post_code):
        try:
            # Check Post code is valid
            data = request.urlopen('http://api.getthedata.com/postcode/{}'.format(post_code))
            data = json.load(data)
            if data['status'] == 'no_match':
                return json.dumps({"Error": "Invalid Post Code Supplied"})
            # check order_id already exists
            if order_id not in self.user_order[username]:
                return json.dumps({"Error": "invalid order ID"})
            self.orders[order_id] = [items, post_code]
            self.user_order[username] += [order_id]
            self.updateReplicas()
            return json.dumps({"Success": "Order {} has been changed".format(order_id)})
        except:
            return json.dumps({"Error": "Order {} could not be changed".format(order_id)})


    @Pyro4.expose        
    def cancelOrder(self, username, order_id):
        try:
            # check order_id already exists
            if order_id not in self.user_order[username]:
                return json.dumps({"Error": "invalid order ID"})
            self.user_order[username].remove(order_id)
            del self.orders[order_id]
            self.updateReplicas()
            return json.dumps({"Success": "Order {} Cancelled".format(order_id)})
        except:
            return json.dumps({"Error": "Order {} could not be cancelled".format(order_id)})


    @Pyro4.expose
    def getOrders(self, username):
        try:
            order_ids = self.user_order[username]
            orders = []
            for o_id in order_ids:
                orders.append([o_id, self.orders[o_id]])
            # check user has orders
            if not orders:
                return json.dumps({"Error": "No orders found!"})
            return json.dumps({"Success": orders})
        except:
            return json.dumps({"Error": "No orders found!"})


    @Pyro4.expose  
    def getMenuItems(self):
        try:
            return json.dumps({"Success": self.menu_items})
        except:
            return json.dumps({"Error": "Could not retrieve menu items!"})


    @Pyro4.expose
    def authenticateUser(self, username, password):
        try:
            if username in self.users.keys():
                if self.users[username] == password:
                    # log user into server
                    self.current_users.append(username)
                    self.updateReplicas()
                    return json.dumps({"Success": "You are logged in!"})
                else:
                    return json.dumps({"Error": "Incorrect Password!"})
            else:
                return json.dumps({"Error": "Incorrect Password!"})
        except:
            return json.dumps({"Error": "Could not complete authentication!"})


    @Pyro4.expose
    def createUser(self, username, password):
        try:
            if username not in self.users.keys():
                self.users[username] = password
                # log user into server
                self.current_users.append(username)
                self.updateReplicas()
                return json.dumps({"Success": "Your account has been registered"})
            else:
                return json.dumps({"Error": "Username already taken"})
        except:
            return json.dumps({"Error": "Could not register your account"})

    @Pyro4.expose
    def logout(self, username):
        try:
            if username in self.current_users:
                # log user out of server
                self.current_users.remove(username)
                self.updateReplicas()
                return json.dumps({"Success": "You have been logged out"})
            else:
                return json.dumps({"Error": "Your are already logged out!"})
        except:
            return json.dumps({"Error": "Could not perform logout!"})


    # get list of all backup replicas from front end and update their data
    def updateReplicas(self):
        replicas = self.front_end.getReplicas(self)
        if replicas:
            for replica in replicas:
                replica.setState(self.users, self.orders, self.current_users, self.user_order, self.o_id)

    # update data of backup replica to data of primary server         
    @Pyro4.expose
    def setState(self, users, orders, current_users, user_order, order_id):
        self.users = users
        self.orders = orders
        self.current_users = current_users
        self.user_order = user_order
        self.o_id = order_id


    # sets status of server to online or offline
    @Pyro4.expose           
    def checkServerStatus(self):
        status_probability = random.uniform(0,1)
        if self.status == 'online':
            if status_probability <= 0.2:
                self.status = 'offline'
        else:
            if status_probability <= 0.8:
                self.status = 'online'
        return self.status
            
            


def main():
    try:
        Pyro4.config.COMMTIMEOUT = 0 
        name_server = Pyro4.locateNS()
        daemon = Pyro4.Daemon()
        server = Server()
        uri = daemon.register(server)
        name_server.register(server.server_name, uri, safe=True)
        fe_uri = Pyro4.resolve('PYRONAME:Front_End_Server')
        Front_End = Pyro4.Proxy(fe_uri)
        Front_End.registerServers(server)
        server.front_end = Front_End
        print("Server {} Online".format(server.server_name))
        daemon.requestLoop()
    except Pyro4.errors.NamingError:
        print("Error: Could not register Server to Front End")


if __name__ == "__main__":
    main()
