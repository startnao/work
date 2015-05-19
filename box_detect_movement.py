#
# Cette box est une box plus complète basée sur la box de base de récupération d'une image
# (box_get_image.py) qui en plus analyse l'image avec OpenCV
#

import cv
import cv2
import numpy

class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)
        self.avd = None
        self.strMyClientName = None

    def onLoad(self):
        self.connectToCamera()
        self.analyze()
        self.disconnectFromCamera()

    def onUnload(self):
        self.avd = None
        self.strMyClientName = None

    def onInput_onStart(self):
        #self.onStopped() #activate the output of the box
        pass

    def onInput_onStop(self):
        self.onUnload() #it is recommended to reuse the clean-up as the box is stopped
        self.onStopped() #activate the output of the box


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
            image = (numpy.reshape(numpy.frombuffer(dataImage[6], dtype='%iuint8' % dataImage[2]), (dataImage[1], dataImage[0], dataImage[2])))
            return image
        except BaseException, err:
            self.log("STARTNAO: error getting camera image: %s" % err)

        self.log("STARTNAO: camera image got")

        return None

    def getCvImageFromCamera(self):
        rawImage = self.getImageFromCamera()
        rawImage.flags['WRITEABLE'] = True

        return cv.fromarray(rawImage)

    def analyze(self):
        self.log("STARTNAO: analyzing image...")

        frame = self.getImageFromCamera()

        self.log("STARTNAO: analyzed image is null: %s" % frame is None)

        if frame is not None:
            self.detectMovement(frame)

        self.log("STARTNAO: image analyzed")

        return None



    def detectMovement(self, frame):
        nWidth = frame.shape[1]
        nHeight = frame.shape[0]

        maxSize = nWidth * nHeight

        greyFrame = cv.CreateImage([ nWidth, nHeight ], cv.IPL_DEPTH_8U, 1)
        movingAverage = cv.CreateImage([ nWidth, nHeight ], cv.IPL_DEPTH_32F, 3)



        ####### Boucle
        colorRawImage = self.getImageFromCamera()
        colorRawImage = colorRawImage
        colorRawImage.flags['WRITEABLE'] = True

        colorCvImage = cv.fromarray(colorRawImage);


        # Smooth to get rid of false positives
        cv.Smooth(colorCvImage, colorCvImage, cv.CV_GAUSSIAN, 3, 0)

        bitmap = cv.CreateImageHeader((colorCvImage.shape[1], colorCvImage.shape[0]), cv.IPL_DEPTH_8U, 3)
        cv.SetData(bitmap, colorCvImage.tostring(), colorCvImage.dtype.itemsize * 3 * colorCvImage.shape[1])

        difference = cv.CloneImage(bitmap)
        temp = cv.CloneImage(bitmap)
        cv.ConvertScale(bitmap, movingAverage, 1.0, 0.0)

        # Convert the scale of the moving average.
        cv.ConvertScale(movingAverage, temp, 1.0, 0.0)

        # Minus the current frame from the moving average.
        cv.AbsDiff(movingAverage, temp, difference)

        # Convert the image to grayscale.
        cv.CvtColor(difference, greyFrame, cv.CV_RGB2GRAY)

        # Convert the image to black and white.
        cv.Threshold(greyFrame, greyFrame, 70, 255, cv.CV_THRESH_BINARY)

        # Dilate and erode to get people blobs
        cv.Dilate(greyFrame, greyFrame, None, 18)
        cv.Erode(greyFrame, greyFrame, None, 10)

        storage = cv.CreateMemStorage(0)
        contour = cv.FindContours(greyFrame, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)

        while contour:
            boundRect = cv.BoundingRect(list(contour))
            contour = contour.h_next()
            area = boundRect[3] * boundRect[2]
            percentage = (area / maxSize) * 100

            self.log("STARTNAO: Percentage: %s" % percentage)