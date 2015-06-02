#
# Cette box est une box plus complète basée sur la box de base de récupération d'une image
# (box_get_image.py) qui en plus analyse l'image avec OpenCV
#

import cv
#import cv2
import numpy

class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)
        self.avd = None
        self.strMyClientName = None

    def onLoad(self):
        self.connectToCamera()
        self.analyze()

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
        self.log("maxsize : %d" % maxSize)
        first = True
        gagne=False
        i = 0
        counting = False
        mouvement_count = 0

        #cree des images vides
        greyFrame = cv.CreateImage([ nWidth, nHeight ], cv.IPL_DEPTH_8U, 1)
        movingAverage = cv.CreateImage([ nWidth, nHeight ], cv.IPL_DEPTH_8U, 3)


        ####### Boucle
        while i < 200 :
            self.log("boucle numéro : %d" % i)
            #on récupère une autre image vide de la caméra
            colorRawImage = self.getImageFromCamera()
            colorRawImage.flags['WRITEABLE'] = True


            #on transforme l'image en opencv
            colorCvImage = cv.fromarray(colorRawImage)

            # Smooth to get rid of false positives : on floute l'image
            cv.Smooth(colorCvImage, colorCvImage, cv.CV_GAUSSIAN, 3, 0)

            #on réer une image vide au début pour y mettre les données voulues
            bitmap = cv.CreateImageHeader((colorRawImage.shape[1], colorRawImage.shape[0]), cv.IPL_DEPTH_8U, 3)
            cv.SetData(bitmap, colorCvImage.tostring(), colorRawImage.dtype.itemsize * 3 * colorRawImage.shape[1])

            if first:
                difference = cv.CloneImage(bitmap)
                temp = cv.CloneImage(bitmap) #image actuelle de la caméra
                cv.ConvertScale(bitmap, movingAverage, 1.0, 0.0)
                first = False
            #else:
                #cv.RunningAvg(bitmap, movingAverage, 0.020, None)

            # Convert the scale of the moving average.
            cv.ConvertScale(movingAverage, temp, 1.0, 0.0)

            # Minus the current frame from the moving average.
            #cv.AbsDiff(temp, movingAverage, difference)
            cv.AbsDiff(bitmap, temp, difference)

            # Convert the image to grayscale.: convertit l'image en nuances de gris et stocke dans greyFrame
            cv.CvtColor(difference, greyFrame, cv.CV_RGB2GRAY)

            # Convert the image to black and white. : convertit l'image en noir et blanc
            cv.Threshold(greyFrame, greyFrame, 70, 255, cv.CV_THRESH_BINARY)

            # Dilate and erode to get people blobs
            cv.Dilate(greyFrame, greyFrame, None, 18)
            cv.Erode(greyFrame, greyFrame, None, 10)

            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(greyFrame, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)

            points = []
            max_pourcentage = 0

            while contour:
                boundRect = cv.BoundingRect(list(contour))
                contour = contour.h_next()

                pt1=(boundRect[0], boundRect[1])
                pt2=(boundRect[0] + boundRect[2], boundRect[1] + boundRect[3])

                area = boundRect[3] * boundRect[2]
                percentage = (area/float(maxSize)) * 100

                self.log("STARTNAO: Percentage: %f" % percentage)

                if percentage > max_pourcentage:
                    max_pourcentage = percentage

                points.append(pt1)
                points.append(pt2)
                cv.Rectangle(bitmap, pt1, pt2, cv.CV_RGB(255,0,0), 1)

            self.logger.warning("maxPourcentage :  %f"%max_pourcentage)
            if not counting and max_pourcentage > 70 :
                mouvement_count = 0
                counting = True
                self.logger.warning("STARTING")
            elif counting and max_pourcentage > 60 :
                mouvement_count+=1
                self.logger.warning("INCREMENTING %f"%max_pourcentage)
            elif max_pourcentage < 40 :
                mouvement_count = 0
                counting = False
                self.logger.warning("ENDING")

            if mouvement_count > 50 :
                self.logger.warning("GAGNE !!!!!!!!!!!")
                gagne = True
                break

            max_pourcentage =0
            i+=1
        if gagne :
            self.disconnectFromCamera()
            self.success()
        else:
            self.disconnectFromCamera()
            self.failure()