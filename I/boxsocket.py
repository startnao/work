import socket
import base64

class MyClass(GeneratedClass):

    # ------------------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        GeneratedClass.__init__(self)
        self.listenSocket=None
        self.connectedSocket=None
        self.doingUnload=False

        self.avd = None
        self.strMyClientName = None
        pass


    # ------------------------------------------------------------------------------------------------------------------------------
    def onLoad(self):
        self.connectToCamera()
        pass


    # ------------------------------------------------------------------------------------------------------------------------------
    # Handles a single connection by receiving a message and decomposing it into fields,
    # which are then sent to an box output.
    #
    # Format incoming command string: "uid#command#param1#param2#...#paramN$",
    # where
    #     $ is the end of command line token,
    #
    # Format of the outgoing command array:
    #     String[uid,command,param1,param2,...,paramN]
    #
    def handleConnection(self):

        total_data=""

        try:
            while True:
                data = self.connectedSocket.recv(1)
                if not data:
                    self.logger.info("Socket "+str(self.connectedSocket)+" closed by peer.")
                    self.onDisconnect()
                    break

                if data=='$':
                    self.logger.info('Execute:'+total_data)

                    # Convert the command string to an array of strings. We use an array instead of separate output
                    # signals to avoid race conditions on the 10 different signals (and it makes handling of the command
                    # string more easy)
                    self.command( total_data.strip(' \t\n\r').split('#') )

                    total_data=""

                else:
                    if len(total_data)<255:  # data buffer limitation
                        total_data += data

        except Exception as ex:
            self.onDisconnect()
            self.logger.info("Exception while listening on socket "+str(self.connectedSocket)+", close connection! ")
            self.logger.info(ex)

        try:
            self.connectedSocket.close();
        except:
            pass

        self.connectedSocket=None
        pass


    # ------------------------------------------------------------------------------------------------------------------------------
    # Starts the TCP/IP listener on the configured port and delegates the connection to a
    # handler. no multiple connections supported so far to avoid complicating things with
    # multi-threading and synchronised management data.
    #
    def onInput_onStart(self):

        while True:

            # Open port for listening
            try:
                self.logger.info("Listening on port "+str(self.getParameter("port"))+" allowing 1 concurrent connection.")

                self.listenSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.listenSocket.bind(("",self.getParameter("port")))
                self.listenSocket.listen(1)
                self.connectedSocket,address=self.listenSocket.accept()  # -> waiting for incoming connection

            except Exception as ex:
                # Very probaly an UNLOAD triggered by stopping the behaviour
                if self.doingUnload==False:
                    self.onUnload()  # |_ don't call it twice
                break

            # Handle incoming connection
            self.onConnect()
            self.logger.info('Connected to '+str(address)+"/"+str(self.connectedSocket))

            # Send back a welcome message. The ~ prefix indicates a small talk message (i.e. can be ignored)
            self.connectedSocket.sendall("~Hello, NAO4Scratch speaking! Waiting for your commands!\n\r")

            self.handleConnection()

        # |_ while True
        pass


    # ------------------------------------------------------------------------------------------------------------------------------
    # Stop the socket server box.  Closes all sockets and set the onStop output.
    #
    def onUnload(self):
        self.logger.info('Unloading: closing all sockets')

        self.doingUnload=True

        try:
            self.connectedSocket.shutdown(socket.SHUT_RDWR)
            self.connectedSocket.close()
        except:
            pass

        try:
            self.listenSocket.shutdown(socket.SHUT_RDWR)
            self.listenSocket.close()
        except:
            pass

        self.connectedSocket=None
        self.listenSocket=None

        self.disconnectFromCamera()
        self.avd = None
        self.strMyClientName = None

        self.onStopped()
        pass


    # ------------------------------------------------------------------------------------------------------------------------------
    # External signal forcing to stop the box.
    #
    def onInput_onStop(self):
        self.onUnload()
        #~ it is recommended to call onUnload of this box in a onStop method,
        # as the code written in onUnload is used to stop the box as well
        pass


    # ------------------------------------------------------------------------------------------------------------------------------
    # External signal when the blocking command has been finished. We need to notify the
    # client by sending back the UID of the command.
    #
    # Format:  "UID#end$"
    #
    def onInput_onCommandFinished(self,cmd):
        try:
            if cmd[1] == 'camera':
                self.connectedSocket.sendall(self.getImageFromCamera()+"#image$")

            self.connectedSocket.sendall(cmd[0]+"#end$")

        except Exception as ex:
            self.logger.warn("Unable to send back command complete notification")
            self.logger.warn(ex)

        pass


    def connectToCamera(self):
        self.log("STARTNAO: connecting to camera...")

        try:
            self.avd = ALProxy("ALVideoDevice")

            self.strMyClientName = self.avd.subscribeCamera(
                # Name              # CameraNum     # Resolution    # Colorspace        # FPS
                self.getName(),     0,              1,              11,                 5
            )

            self.log("STARTNAO: connected to camera")
        except BaseException, err:
            self.log("STARTNAO: error connecting to camera: %s" % err)


    def disconnectFromCamera(self):
        self.log("STARTNAO: disconnecting from camera...")

        try:
            self.avd.unsubscribe( self.strMyClientName )
        except BaseException, err:
            self.log("STARTNAO: error disconnecting from camera: %s" % err)

        self.log("STARTNAO: disconnected from camera")


    def getImageFromCamera(self):
        self.log("STARTNAO: getting camera image...")

        try:
            dataImage = self.avd.getImageRemote(self.strMyClientName)
            return base64.b64encode(dataImage[6])
        except BaseException, err:
            self.log("STARTNAO: error getting camera image: %s" % err)

        return None
