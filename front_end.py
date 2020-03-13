import Pyro4
import Pyro4.errors
import time
import json
import uuid


class FrontEnd():
    
    def __init__(self):
        self.servers = []
        self.primary_index = None
        self.primary = None

    # keep a record of all backend servers
    @Pyro4.expose
    def registerServers(self, server):
        server._pyroTimeout = 5
        self.servers += [server]
        print("Server added")
        if not self.primary_index:
            self.primary_index = 0
            self.primary = self.servers[self.primary_index]
    
    def setPrimary(self):
        num_servers = len(self.servers)
        # check primary server is still online
        status = self.primary.checkServerStatus()
        if status == 'online':
            return True
        # if primary server is offline find another online server and replace it as the primary server
        for idx, server in enumerate(self.servers):
            if idx != self.primary_index:
                status = server.checkServerStatus()
                print(status)
                if status == 'online':
                    self.primary_index = idx
                    self.primary = server
                    return True
        # if no server online return False
        print("All Servers Offline")    
        return False

    # send list of all backup replicas to primary server and send response back to client   
    @Pyro4.expose
    def getReplicas(self, server):
        replicas = []
        for idx, server in enumerate(self.servers):
            if idx != self.primary_index:
                replicas.append(server)
        return replicas
            
            

    # transfer addOrder request to primary server and send response back to client
    @Pyro4.expose
    def addOrder(self, username, items, post_code):
        if self.setPrimary():
            try:
                response = self.primary.addOrder(username, items, post_code)
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.addOrder(username, items, post_code)

    # transfer authenticateUser request to primary server and send response back to client
    @Pyro4.expose
    def authenticateUser(self, username, password):
        if self.setPrimary():
            try:
                response = self.primary.authenticateUser(username, password)
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.authenticateUser(username, password)

    # transfer createUser request to primary server and send response back to client
    @Pyro4.expose
    def createUser(self, username, password):
        if self.setPrimary():
            try:
                response = self.primary.createUser(username, password)
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.createUser(username, password)

    # transfer cancelOrder request to primary server and send response back to client   
    @Pyro4.expose
    def cancelOrder(self, username, order_id):
        if self.setPrimary():
            try:
                response = self.primary.cancelOrder(username, order_id)
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.cancelOrder(username, order_id)
    # transfer changeOrder request to primary server and send response back to client
    @Pyro4.expose
    def changeOrder(self, username, order_id, items, post_code):
        if self.setPrimary():
            try:
                response = self.primary.changeOrder(username, order_id, items, post_code)
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.changeOrder(username, order_id, post_code)

    # transfer getUsers request to primary server and send response back to client
    @Pyro4.expose
    def getUsers(self):
        if self.setPrimary():
            try:
                response = self.primary.getUsers()
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.getUsers()

    # transfer getOrders request to primary server and send response back to client
    @Pyro4.expose
    def getOrders(self, username):
        if self.setPrimary():
            try:
                response = self.primary.getOrders(username)
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.getOrders(username)

    # transfer getMenuItems request to primary server and send response back to client
    @Pyro4.expose
    def getMenuItems(self):
        if self.setPrimary():
            try:
                response = self.primary.getMenuItems()
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.getMenuItems()

    # transfer logout request to primary server and send response back to client
    @Pyro4.expose
    def logout(self, username):
        if self.setPrimary():
            try:
                response = self.primary.logout(username)
                return response
            except Pyro4.errors.TimeoutError:
                print("Error: Request Yimed Out!")
                return json.dumps({"Error": "Request Timed Out!"})
        else:
            print("Retrying connection...")
            return self.logout(username)

def main():
    try:
        Pyro4.config.COMMTIMEOUT = 0
        front_end = FrontEnd()
        name_server = Pyro4.locateNS()
        daemon = Pyro4.Daemon()
        uri = daemon.register(front_end)
        name_server.register("Front_End_Server", uri)
        print("Front End Server Online")
        daemon.requestLoop()
    except Pyro4.errors.NamingError:
        print("Error: Could not connect to Name Server")

if __name__ == "__main__":
    main()
