import datetime
import cv2
import math
import numpy as np
import pickle   
import time
import os

DEBUG = False
LLEGEIX_CAMERA = False
CAMERA_USED = 'TPTEK' # Used camera. Possible values: 'TPTEK'
REDUCCIO_REFERENCIES = 0 # Pixels to reduce the field limits for avoiding the external references

MIDA_CAMP_X = 2360
MIDA_CAMP_Y = 1310

################################################ Lectura i gravació d'imatges ################################################

# Function to open an image file and perform global thresholding
# Input: image_path: path to the image file
# Output: image_thresh: thresholded image
def ObreImatge(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Check if the image was successfully read
    if image is None:
        print('ObreImatge: No s\'ha pogut obrir el fitxer', image_path)
        return
    
    return image 

# Function to activate the camera
# Output: cap: VideoCapture object
def ActivaCamera():
    if LLEGEIX_CAMERA:
        cap = cv2.VideoCapture('rtsp://admin:TAV1234a@192.168.1.116:554/11')

        # Check if the camera opened successfully
        if not cap.isOpened():
            print("ActivaCamera: Could not open camera.")
            exit()
        return cap
    else:
        return None
    
# Function to read a frame from the camera
# Input: cap: VideoCapture object
# Output: frame: frame read from the camera
def LlegeixFotoCamera(cap):
    if LLEGEIX_CAMERA:
        ret, frame = cap.read()
        #GuardaImatge(frame, 'Software/Lector-posicio/Data/FotoCamp')
        
        if not ret:
            print("LlegeixFoto: Failed to capture frame.")
    else:
        frame = ObreImatge('Software/Lector-posicio/Data/FotoCamp_20240310_212033.jpg')
    
    if DEBUG:
        #Display read image
        cv2.imshow('Imatge de la camera', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
     
    return frame

# Function to save an image on file with a timestamp
# Input: image: image to save
#        filename: name of the file
def GuardaImatge(image, filename):
    # Save image on file, adding timestamp to the filename
    timestamp = datetime.datetime.now().strftime('_%Y%m%d_%H%M%S')
    if  not cv2.imwrite(filename
                + timestamp
                + '.jpg', image):
        print('No s\'ha pogut guardar la imatge', filename)
        return
    

################################################ Millora de l'imatge ################################################ 
# Function to perform global thresholding on an image
# Input: frame: image to threshold
# Output: img_thresh: thresholded image
def ThresholdImatge(frame):
    # If the image is not in grayscale, convert it
    if len(frame.shape) > 2:
        # Convert image to grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform global thresholding
    
    _, img_thresh = cv2.threshold(frame, 250, 255, cv2.THRESH_BINARY)

    if DEBUG:
        # Display the thresholded image
        cv2.imshow('Thresholded image', img_thresh)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return img_thresh  

# Function to correct the distortion of an image
# Input: image: image to correct
#        cameraMatrix: camera matrix
#        dist: distortion coefficients
#        newCameraMatrix: new camera matrix
#        roi: region of interest
#        w: width of the image
#        h: height of the image
# Output: dst: undistorted and cropped image
def CorregeixImatge(image, cameraMatrix, dist):
    h,  w = image.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))
    
    # Undistort the image
    dst = cv2.undistort(image, cameraMatrix, dist, None, newCameraMatrix)
    
    # Undistort with Remapping
    #mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
    #dst = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)
    
    if DEBUG:
        # Display undistorted image
        cv2.imshow('Undistorted image', dst)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # crop the image
    x, y, w, h = roi

    if CAMERA_USED == 'TPTEK':
        dst = dst[y + 20:y+h, x:x+w] # We remove completely text from the camera
    else:
        dst = dst[y:y+h, x:x+w]

    if DEBUG:
        # Display cropped image
        cv2.imshow('Cropped image', dst)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return dst

################################################ Anàlisis inatge ################################################
# Class which defines the field of the flowers
class FlowerField:
    def __init__(self):
        self.left_up = (0,0) # Top left corner of the field in pixels
        self.right_up = (0,0) # Top right corner of the field in pixels
        self.left_down = (0,0) # Bottom left corner of the field in pixels
        self.right_down = (0,0) # Bottom right corner of the field in pixels
        self.image_size = (0,0) # Size of the screen in pixels

    # It finds limits of the field. The field is limited by 4 white references
    # Input: image: path to the undistorted image file
    #        image_thresh: thresholded image
    def ObteCamp(self):
        # Load camera calibration data
        cameraMatrix = pickle.load(open('Software/Calibracio-camera/cameraMatrix.pkl', 'rb'))
        dist = pickle.load(open('Software/Calibracio-camera/dist.pkl', 'rb'))

        cap = ActivaCamera()  
        
        image = LlegeixFotoCamera(cap)   
        imagec = CorregeixImatge(image, cameraMatrix, dist)
        imaget = ThresholdImatge(imagec)
        # Find contours
        contours, _ = cv2.findContours(imaget, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) 
    
        if DEBUG:
            print('Nombre de contorns trobats:', len(contours))
            # Print size of every contour
            contour_trobats = list(contours)
            # Sort by size
            contour_trobats.sort(key=cv2.contourArea, reverse=True)
            print('Àrea dels contorns trobats:')
            for contour in contour_trobats:
                # We print contour size if it is bigger than 0
                if cv2.contourArea(contour) > 0:
                    print(cv2.contourArea(contour))
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Filter contours by area, we keep only the big ones
        contours = [contour for contour in contours if cv2.contourArea(contour) > 100]

        # Find the 4 contours delimiting the field
        # Find centers
        centers = []
        for contour in contours:
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                centers.append((cx, cy))
                cv2.circle(image, (cx, cy), 5, (128, 128, 128), -1)

        # Find the left up center 
        distance_to_0 = [math.sqrt(x**2 + y**2) for (x, y) in centers]
        self.left_up = centers[distance_to_0.index(min(distance_to_0))]

        # Find the right up center
        distance_to_x = [math.sqrt((image.shape[1]-x)**2 + y**2) for (x, y) in centers]
        self.right_up = centers[distance_to_x.index(min(distance_to_x))]

        # Find the left down center
        distance_to_y = [math.sqrt(x**2 + (image.shape[0]-y)**2) for (x, y) in centers]
        self.left_down = centers[distance_to_y.index(min(distance_to_y))]

        # Find the right down center
        distance_to_xy = [math.sqrt((image.shape[1]-x)**2 + (image.shape[0]-y)**2) for (x, y) in centers]
        self.right_down = centers[distance_to_xy.index(min(distance_to_xy))]
  
        if DEBUG:
            #Draw a gray circle on center of every reference
            cv2.circle(imagec, (self.left_down), 5, (128, 128, 128), -1)
            cv2.circle(imagec, (self.right_up), 5, (128, 128, 128), -1)
            cv2.circle(imagec, (self.left_up), 5, (128, 128, 128), -1)
            cv2.circle(imagec, (self.right_down), 5, (128, 128, 128), -1)
            cv2.imshow('Imatge amb Limits del camp', imagec)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Update image size
        self.image_size = imagec.shape
        
        return
    
    def PixelXY2ReallXY(self, px, py):
        # On camera, flower field is limited by 4 lines, left line, right line, up line and down line
        # Every line is defined by its points (left_up, left_down, right_up, right_down)
        # We know the real field size, so real position is proportional to the distance to the lines
        # Get a line equation from the left_up to the right_up
        m_up = (self.right_up[1] - self.left_up[1])/(self.right_up[0] - self.left_up[0])
        n_up = self.left_up[1] - m_up*self.left_up[0]

        # Get a line equation from the left_up to the left_down
        m_left = (self.left_down[1] - self.left_up[1])/(self.left_down[0] - self.left_up[0])
        n_left = self.left_up[1] - m_left*self.left_up[0]

        # Get a line equation from the right_up to the right_down
        m_right = (self.right_down[1] - self.right_up[1])/(self.right_down[0] - self.right_up[0])
        n_right = self.right_up[1] - m_right*self.right_up[0]

        # Get a line equation from the left_down to the right_down
        m_down = (self.right_down[1] - self.left_down[1])/(self.right_down[0] - self.left_down[0])
        n_down = self.left_down[1] - m_down*self.left_down[0]

        # Distance from left line to the point
        d_left = px - ((py - n_left) / m_left)
        # Distance from right line to the point
        d_right = ((py - n_right) / m_right) - px
        # Scale to real world
        x = (d_left * MIDA_CAMP_X) / (d_left + d_right)

        # Distance from up line to the point
        d_up = py - ((m_up * px) + n_up)
        # Distance from down line to the point
        d_down = ((m_down * px) + n_down) - py
        # Scale to real world
        y = (d_up * MIDA_CAMP_Y) / (d_up + d_down)

        return x, y

# Function to help to adjust the limits of the field. It must be executed with DEBUG = True and it continuously shows the image of the field 
# Input: CampFlors: FlowerField object
# Output: None
def AjustaLimitsCamp(CampFlors):

    if not DEBUG:
        print('AjustaLimitsCamp: Només té sentit executar aquesta funció amb DEBUG = True')
        return
       
    while True:
        CampFlors.ObteCamp()
        k = cv2.waitKey(0)
        if k == 27:
            break  

# Function to find the position of one flower in the image
# Just one flower is expected to be found
# Input: image: image to analyze
#        CampFlors: FlowerField object already calibrated (ObteCamp executed)
# Output: middle_point: screen coordinates of the middle point between the two centers
#                       (0,0),0,0 if flower not found
def TrobaPosicioFlor(image, CampFlors):
    # Reduce the field limits for avoiding the external references
    xmin = max(CampFlors.left_up[0], CampFlors.left_down[0]) + REDUCCIO_REFERENCIES
    xmax = min(CampFlors.right_up[0], CampFlors.right_down[0]) - REDUCCIO_REFERENCIES
    ymin = max(CampFlors.left_up[1], CampFlors.right_up[1]) + REDUCCIO_REFERENCIES
    ymax = min(CampFlors.left_down[1], CampFlors.right_down[1]) - REDUCCIO_REFERENCIES

    # Crop the image
    imager = image[ymin:ymax, xmin:xmax]

    # Find contours
    contours, _ = cv2.findContours(imager, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    # Filter contours by area, we keep only the big ones
    contours = [contour for contour in contours if cv2.contourArea(contour) > 100]

    # Find centers
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            centers.append((cx, cy))
    
    if DEBUG:
        #Draw a gray circle on every center
        for center in centers:
            cv2.circle(imager, center, 5, (128, 128, 128), -1)
        cv2.imshow('Imatge amb Contorns trobats', imager)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # If more than 2 centers are found, print an error message
    if len(centers) > 2 or len(centers) < 2:
        print('TrobaPosicioFlor: S\'han trobat més de 2 referències')
        # Save image 
        #GuardaImatge(image, 'Software/Lector-posicio/Data/ErrorReferences')
        return (0,0),0,0
    
    # Calculate the distance between the two centers
    distance = math.sqrt((centers[0][0]-centers[1][0])**2 + (centers[0][1]-centers[1][1])**2)

    # Get the coordinates of the middle point between the two centers
    middle_point = ((centers[0][0]+centers[1][0])//2, (centers[0][1]+centers[1][1])//2)

    if DEBUG:
        # Draw a gray circle on the middle point
        cv2.circle(imager, middle_point, 5, (128, 128, 128), -1)
        cv2.imshow('Imatge amb posicio flor', imager)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    #Get the angle betwwen the line joining the two centers and the y axis
    try:
        angle = math.atan((centers[1][0]-centers[0][0])/(centers[1][1]-centers[0][1]))
    except ZeroDivisionError:
        angle = 0
    
    # We add what we cropped at the begginning for removing the external references
    middle_point = (middle_point[0] + xmin, middle_point[1] + ymin)

    return middle_point, distance, angle

# It draws a circle on the middle point and a line at the inclination of the flower
# Input: image: image to draw on
#        x: x screen coordinate of the middle point
#        y: y screen coordinate of the middle point
#        angle: inclination of the flower
# Output: image: image with the circle and the line drawn
def DibuixaPosicioFlor(image, x, y, angle):
    #Draw a circle on the middle point
    cv2.circle(image, (x, y), 100, (255, 255, 255), 2)

    #Draw a line at the inclination of the flower
    x2 = int(x + 200 * math.sin(angle))
    y2 = int(y + 200 * math.cos(angle))
    cv2.line(image, (x, y), (x2, y2), (255, 255, 255), 2)
    
    if DEBUG:
        cv2.imshow('Imatge amb dibuix posicio flor', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return image

# For following the flower
# It reads the camera, it corrects the image, thresholds it and finds the position of the flower
# It shows the image with a circle on the middle point and a line at the inclination of the flower
# It also shows the x, y and angle of the flower
# If the user presses 's' it saves the original, corrected, thresholded and position images
# If the user presses 'esc' it closes the camera
# Input: Camp: FlowerField object already calibrated (ObteCamp executed)
# Output: None
def SegueixFlor(CampFlors):
    # Load camera calibration data
    cameraMatrix = pickle.load(open('Software/Calibracio-camera/cameraMatrix.pkl', 'rb'))
    dist = pickle.load(open('Software/Calibracio-camera/dist.pkl', 'rb'))

    cap = ActivaCamera()  
    
    while True:
        image = LlegeixFotoCamera(cap)
                
        imagec = CorregeixImatge(image, cameraMatrix, dist)
        imaget = ThresholdImatge(imagec)
        
        Posicio, Distancia, Angle = TrobaPosicioFlor(imaget, CampFlors)

        font = cv2.FONT_HERSHEY_SIMPLEX
        if (Posicio[0] == 0 and Posicio[1] == 0 and Distancia == 0 and Angle == 0):
            # No flower found
            cv2.putText(imagec, 'No s\'ha trobat flor', (50, 60), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Imatge sense posicio', imagec)
        else:
            # Draw the position of the flower
            imager = DibuixaPosicioFlor(imagec, Posicio[0], Posicio[1], Angle)
            PosicioReal = CampFlors.PixelXY2ReallXY(Posicio[0], Posicio[1])
            cv2.putText(imager, 'X: ' + str(int(PosicioReal[0])), (50, 80), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(imager, 'Y: ' + str(int(PosicioReal[1])), (50, 160), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            # Angle in str with just 2 decimals
            Ang = "{:.2f}".format((Angle*360)/6.28)
            cv2.putText(imager, 'Angle: ' + Ang, (50, 240), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Imatge amb posicio', imager)
        
        if DEBUG:
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        k = cv2.waitKey(5)
        if k == 27:
            break
        elif k == ord('s'):
            GuardaImatge(image, 'Software/Lector-posicio/Data/FotoOriginal')
            GuardaImatge(imagec, 'Software/Lector-posicio/Data/FotoCorregida')
            GuardaImatge(imaget, 'Software/Lector-posicio/Data/FotoThreshold') 
            if not (Posicio[0] == 0 and Posicio[1] == 0 and Distancia == 0 and Angle == 0):
                GuardaImatge(imager, 'Software/Lector-posicio/Data/FotoPosicio')
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()  

# For moving a circle on the screen using keyboard and check which is the real calculated position, to see if it matches with the real position
# Input: CampFlors: FlowerField object already calibrated (ObteCamp executed)
# Output: None (screen)
def ComprovaPosicio(CampFlors):
    # Load camera calibration data
    cameraMatrix = pickle.load(open('Software/Calibracio-camera/cameraMatrix.pkl', 'rb'))
    dist = pickle.load(open('Software/Calibracio-camera/dist.pkl', 'rb'))

    cap = ActivaCamera()  
    
    Posicio = (100,1000)
    Angle = 0

    while True:
        image = LlegeixFotoCamera(cap)
                
        imagec = CorregeixImatge(image, cameraMatrix, dist)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        # Draw the position of the flower
        imager = DibuixaPosicioFlor(imagec, Posicio[0], Posicio[1], Angle)
        PosicioReal = CampFlors.PixelXY2ReallXY(Posicio[0], Posicio[1])
        cv2.putText(imager, 'X: ' + str(int(PosicioReal[0])), (50, 80), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(imager, 'Y: ' + str(int(PosicioReal[1])), (50, 160), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
        # Angle in str with just 2 decimals
        Ang = "{:.2f}".format((Angle*360)/6.28)
        cv2.putText(imager, 'Angle: ' + Ang, (50, 240), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('Imatge amb posicio', imager)
        
        if DEBUG:
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        k = cv2.waitKey(5)
        # Move the position of the flower
        # s: right
        # a: left
        # w: up
        # z: down
        # k: right 10 pixels
        # j: left 10 pixels
        # i: up 10 pixels
        # m: down 10 pixels
        if k == 27:
            break
        elif k == ord('s'):
            Posicio = (Posicio[0]+1, Posicio[1])
        elif k == ord('a'):
            Posicio = (Posicio[0]-1, Posicio[1])
        elif k == ord('w'):
            Posicio = (Posicio[0], Posicio[1]-1)
        elif k == ord('z'):
            Posicio = (Posicio[0], Posicio[1]+1)
        elif k == ord('k'):
            Posicio = (Posicio[0]+10, Posicio[1])
        elif k == ord('j'):
            Posicio = (Posicio[0]-10, Posicio[1])
        elif k == ord('i'):
            Posicio = (Posicio[0], Posicio[1]-10)
        elif k == ord('m'):
            Posicio = (Posicio[0], Posicio[1]+10)
                
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()  

################################################ Main function ################################################
def main():
    
    CampFlors = FlowerField()
    #AjustaLimitsCamp(CampFlors)
    CampFlors.ObteCamp()
    #SegueixFlor(CampFlors)
    ComprovaPosicio(CampFlors)
     
   
if __name__ == "__main__":
    main()

    