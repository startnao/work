import cv2
import numpy
import Image

class MyClass(GeneratedClass):
    """ THE line detector in a box without any external library """
    def detectBlueBall(self,  img ):
        self.logger.info("aaa")
        img = cv2.flip(img,5)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = numpy.array([110,50,50], dtype=numpy.uint8)
        upper_blue = numpy.array([130,255,255], dtype=numpy.uint8)
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        res = cv2.bitwise_and(img,img, mask= mask)
        imgray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,127,255,0)
        contours, hierarchy = cv2.findContours(imgray,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            print len(contours)
            x,y,w,h = cv2.boundingRect(cnt)
            if(w < 30):
                return True
    def __init__(self):
        GeneratedClass.__init__(self);

    def onLoad(self):
        self.connectToCamera()
        detected=False
        i=0
        while detected is not True :
            if i>50 :
                detected=True
            i=i+1
            self.log( "pas detecte")
            img= self.getImageFromCamera()
            img = cv2.flip(img,5)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_blue = numpy.array([110,50,50], dtype=numpy.uint8)
            upper_blue = numpy.array([130,255,255], dtype=numpy.uint8)
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            res = cv2.bitwise_and(img,img, mask= mask)
            imgray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(imgray,127,255,0)
            contours, hierarchy = cv2.findContours(imgray,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                print len(contours)
                x,y,w,h = cv2.boundingRect(cnt)
                if(w < 30):
                    detected=True
        self.disconnectFromCamera()
        pass


    def onUnload(self):
        pass


    def connectToCamera( self ):
        try:
            self.avd = ALProxy( "ALVideoDevice" );
            strMyClientName = self.getName();
            nCameraNum = 0;
            nResolution = 1;
            nColorspace = 11;
            nFps = 5;
            self.strMyClientName = self.avd.subscribeCamera( strMyClientName, nCameraNum, nResolution, nColorspace, nFps );
        except BaseException, err:
            self.log( "ERR: connectToCamera: catching error: %s!" % err );

    def disconnectFromCamera( self ):
        self.log("debut disconnect")
        try:
            self.avd.unsubscribe( self.strMyClientName );
        except BaseException, err:
            self.log( "ERR: disconnectFromCamera: catching error: %s!" % err );
        self.log("fin disconnect")
        pass

    def getImageFromCamera( self ):
        """
        return the image from camera or None on error
        """
        self.log( "BBB" );
        try:
            dataImage = self.avd.getImageRemote( self.strMyClientName );
            self.log( "CCC" );
            self.log( "IS NULL : %s" % dataImage != None );
            self.log(dataImage[0])
            self.log(dataImage[1])
            self.log(dataImage[2])
            if( dataImage != None ):
                image = (numpy.reshape(numpy.frombuffer(dataImage[6], dtype='%iuint8' % dataImage[2]), (dataImage[1], dataImage[0], dataImage[2])))
                return image;
        except BaseException, err:
            self.log( "ERR: getImageFromCamera: catching error: %s!" % err );
        return None;



    def onInput_onStart(self):
        #self.onStopped() #activate the output of the box
        pass

    def onInput_onStop(self):
        self.onUnload() #it is recommended to reuse the clean-up as the box is stopped
        self.onStopped() #activate the output of the box