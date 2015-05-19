import cv2
import numpy
import time

def detectLine( img, bVerbose = False ):
    """
    detect a line in an image
    Return [rOffset, rOrientation]
    - rOffset: rough position of the line on screen [-1, +1] (-1: on the extrem left, 1: on the extrem right, 0: centered)
    - rOrientation: its orientation [-pi/2,pi/2]
    or [None,None], if no line detected
    """
    nWidth = img.shape[1];
    nHeight = img.shape[0];

    # filter to detect vertical line
    kernel = -numpy.ones((1,3), dtype=numpy.float);
    kernel[0,1] = 2;

    img = cv2.filter2D(img, -1, kernel);

    # thresholding to remove low differential
    retval, img = cv2.threshold( img, 45, 255, cv2.THRESH_TOZERO );

    aMaxL = numpy.argmax(img, axis=1 );
    aMaxLWithoutZeros = aMaxL[aMaxL>0];

    if( bVerbose ):
        print( "Line Length: %s" % len(aMaxLWithoutZeros) );

    if( len( aMaxLWithoutZeros ) < 4 ):
        print( "WRN: abcdk.image.detectLine: detected line is very short: %s" % aMaxLWithoutZeros );
        return [None, None];

    aNonZeroIdx = numpy.where(aMaxL != 0)[0]; # here we retravelling thru the list, it's not optimal (TODO: optimise!)
    nFirstNonZero = aNonZeroIdx[0];
    nLastNonZero = aNonZeroIdx[-1];
    nHeightSampling = nLastNonZero - nFirstNonZero;

    if( bVerbose ):
        print( "nFirstNonZero: %s" % nFirstNonZero );
        print( "nLastNonZero: %s" % nLastNonZero );
        print( "nHeightSampling: %s" % nHeightSampling );
        print( "nHeight: %s" % nHeight );
        print( "nWidth: %s" % nWidth );

    # here instead of take the average of left and right border, we just keep left, sorry for the approximation
    aLine = aMaxLWithoutZeros;

    # averaging
    nSamplingSize = max( min(len(aLine) / 40, 8), 1 );
    if( bVerbose ):
        print( "nSamplingSize: %s" % nSamplingSize );
    rTop = numpy.average(aLine[:nSamplingSize]); # first points
    rMed =  numpy.average(aLine[len(aLine)/2:len(aLine)/2+nSamplingSize]);
    rBase = numpy.average(aLine[-nSamplingSize:]); # last points

    # this computation is very approximative: we just take the top and bottom position and we compute an average direction (we should make a linear regression or...)
    rOrientation = ((rTop-rBase))/nHeightSampling; # WRN: here it could be wrong as the aLine has zero removed, so perhaps the top and bottom are not really at top or bottom !

    if( bVerbose ):
        print( "rOrientation rough: %s" % rOrientation );
        print( "rBase: %f, rMed: %f, rTop: %f, rOrientation: %f" % (rBase, rMed, rTop, rOrientation) );

    return( [(rMed/nWidth)*2-1, rOrientation] );
# detectLine - end



class MyClass(GeneratedClass):
    """ THE line detector in a box without any external library """
    def __init__(self):
        GeneratedClass.__init__(self);

    def onLoad(self):
        self.bMustStop = False;
        self.bIsRunning = False;

    def onUnload(self):
        self.onInput_onStop(); # stop current loop execution

    def connectToCamera( self ):
        try:
            self.avd = ALProxy( "ALVideoDevice" );
            strMyClientName = self.getName();
            nCameraNum = 1;
            nResolution = 1;
            nColorspace = 0;
            nFps = 5;
            self.strMyClientName = self.avd.subscribeCamera( strMyClientName, nCameraNum, nResolution, nColorspace, nFps );
        except BaseException, err:
            self.log( "ERR: connectToCamera: catching error: %s!" % err );

    def disconnectFromCamera( self ):
        try:
            self.avd.unsubscribe( self.strMyClientName );
        except BaseException, err:
            self.log( "ERR: disconnectFromCamera: catching error: %s!" % err );

    def getImageFromCamera( self ):
        """
        return the image from camera or None on error
        """
        try:
            dataImage = self.avd.getImageRemote( self.strMyClientName );

            if( dataImage != None ):
                image = (numpy.reshape(numpy.frombuffer(dataImage[6], dtype='%iuint8' % dataImage[2]), (dataImage[1], dataImage[0], dataImage[2])))
                return image;

        except BaseException, err:
            self.log( "ERR: getImageFromCamera: catching error: %s!" % err );
        return None;


    def onInput_onStart(self):

        self.log( self.boxName + ": start - begin" );

        if( self.bIsRunning ):
            self.log( self.boxName + ": already started => nothing" );
            return;

        self.bIsRunning = True;
        self.bMustStop = False;

        # camera connection
        self.connectToCamera();

        rPeriod = self.getParameter( 'rPeriod' );
        while( not self.bMustStop ):
            timeBegin = time.time();
            img = self.getImageFromCamera();
            timeImg = time.time();
            if( img == None ):
                self.log( "ERR: error while getting image from camera: img is none" );
                #abcdk.debug.raiseCameraFailure();
            else:
                rBase, rOrientation = detectLine( img, bVerbose=self.getParameter( "bDebug" ) );
                print( "detectLine takes: %5.3fs" % (time.time() - timeBegin ) );
                if( rBase == None ):
                    self.output_none();
                else:
                    self.output_detected( [rBase, rOrientation] );
            timeDetect = time.time();
            self.log( "end of loop, time total: %5.3fs, time get image: %5.3fs, time detect: %5.3fs" % ((time.time()-timeBegin),(timeImg-timeBegin),(time.time()-timeImg) ) );

            time.sleep( rPeriod );
        # end while
        self.bIsRunning = False;
        self.disconnectFromCamera();
        self.onStopped();
        self.log( self.boxName + ": start - end" );

    def onInput_onStop(self):
        self.bMustStop = True; # stop current loop execution

# Template_White - end
pass