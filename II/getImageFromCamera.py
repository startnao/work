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