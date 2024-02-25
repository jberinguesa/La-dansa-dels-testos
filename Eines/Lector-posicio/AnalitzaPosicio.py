import cv2
import datetime
import math
import numpy as np

DEBUG = True
REDUCCIO_CAMP_REFERENCIES = 12

# Function to open an image file and perform global thresholding
# Input: image_path: path to the image file
# Output: image_thresh: thresholded image
def ObreImatge(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Check if the image was successfully read
    if image is None:
        print('No s\'ha pogut obrir el fitxer', image_path)
        return
    
    if DEBUG:
        # Display the original image
        cv2.imshow('Original image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Perform global thresholding
    retval, img_thresh = cv2.threshold(image, 250, 255, cv2.THRESH_BINARY)

    if DEBUG:
        # Display the thresholded image
        cv2.imshow('Thresholded image', img_thresh)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    GuardaImatge(img_thresh, 'Eines/Lector-posicio/Data/Output/Thresholded')

    return img_thresh 

# Function to extract just the field from the image
# Input: image_path: path to the image file
# Output: image: image without references
def ObteCamp(image):
    # Find contours
    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) 

    # Find the 4 contours delimiting the field
    # Find centers
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            centers.append((cx, cy))
            cv2.circle(image, (cx, cy), 5, (255, 0, 0), -1)

    # Find the left up center 
    distance_to_0 = [math.sqrt(x**2 + y**2) for (x, y) in centers]
    left_up = centers[distance_to_0.index(min(distance_to_0))]

    # Find the right up center
    distance_to_x = [math.sqrt((image.shape[1]-x)**2 + y**2) for (x, y) in centers]
    right_up = centers[distance_to_x.index(min(distance_to_x))]

    # Find the left down center
    distance_to_y = [math.sqrt(x**2 + (image.shape[0]-y)**2) for (x, y) in centers]
    left_down = centers[distance_to_y.index(min(distance_to_y))]

    # Find the right down center
    distance_to_xy = [math.sqrt((image.shape[1]-x)**2 + (image.shape[0]-y)**2) for (x, y) in centers]
    right_down = centers[distance_to_xy.index(min(distance_to_xy))]
  
    if DEBUG:
        #Draw a gray circle on center of every reference
        cv2.circle(image, (right_down), 5, (128, 128, 128), -1)
        cv2.circle(image, (left_down), 5, (128, 128, 128), -1)
        cv2.circle(image, (right_up), 5, (128, 128, 128), -1)
        cv2.circle(image, (left_up), 5, (128, 128, 128), -1)
        cv2.imshow('Image amb References', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Calculate the field size
    ymin = max(left_up[1], right_up[1]) + REDUCCIO_CAMP_REFERENCIES
    ymax = min(left_down[1], right_down[1]) - REDUCCIO_CAMP_REFERENCIES
    xmin = max(left_up[0], left_down[0]) + REDUCCIO_CAMP_REFERENCIES
    xmax = min(right_up[0], right_down[0]) - REDUCCIO_CAMP_REFERENCIES
  
    if DEBUG:
        # Draw a grey line for the field size
        image[ymin, :] = 128
        image[:, xmin] = 128
        image[ymax, :] = 128
        image[:, xmax] = 128    
        # Display the image with borders
        cv2.imshow('Image with borders', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Crop the image to the field size
    image = image[(ymin+1):(ymax-1), (xmin+1):(xmax-1)] # +1 and -1 to avoid the grey lines

    if DEBUG:
        #Display the cropped image
        cv2.imshow('Cropped image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Return field size
    return image

# Function to save an image on file
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
    
def TrobaPosicioFlor(image):
    # Find contours
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    # Find centers
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            centers.append((cx, cy))
            cv2.circle(image, (cx, cy), 5, (255, 0, 0), -1)

    if DEBUG:
        #Draw a gray circle on every center
        for center in centers:
            cv2.circle(image, center, 10, (128, 128, 128), -1)
        cv2.imshow('Image amb References', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # If more than 2 centers are found, print an error message
    if len(centers) > 2:
        print('TrobaPosicioFlor: S\'han trobat més de 2 referències')
        # Save image 
        GuardaImatge(image, 'Eines/Lector-posicio/Data/Output/ErrorReferences')
        return 0,0,0
    
    # Calculate the distance between the two centers
    distance = math.sqrt((centers[0][0]-centers[1][0])**2 + (centers[0][1]-centers[1][1])**2)

    # Get the coordinates of the middle point between the two centers
    middle_point = ((centers[0][0]+centers[1][0])//2, (centers[0][1]+centers[1][1])//2)

    if DEBUG:
        # Draw a gray circle on the middle point
        cv2.circle(image, middle_point, 5, (128, 128, 128), -1)
        cv2.imshow('Image amb posició flor', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    #Get the angle betwwen the line joining the two centers and the y axis
    angle = math.atan((centers[1][0]-centers[0][0])/(centers[1][1]-centers[0][1]))
    return middle_point, distance, angle

def ActivaCamera():
    cap = cv2.VideoCapture('rtsp://admin:TAV1234a@192.168.1.116:554/11')

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("ActivaCamera: Could not open camera.")
        exit()
    return cap

def LlegeixFoto(cap):
    ret, frame = cap.read()
    if not ret:
        print("LlegeixFoto: Failed to capture frame.")
    return frame

    # Release the VideoCapture object and close all OpenCV windows

def prova():

    # Replace 'rtsp://username:password@IP:port/stream' with your RTSP stream URL
    rtsp_url = 'rtsp://admin:TAV1234a@192.168.1.116:554/11'

    # Create a VideoCapture object
    cap = ActivaCamera()

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    # Read and display frames from the camera
    while True:
        frame = LlegeixFoto(cap)
        cv2.imshow('RTSP Camera', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the VideoCapture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

#Main function
def main():
    #cap = ActivaCamera()
    #image = LlegeixFoto(cap)
    prova()
    cap = cv2.VideoCapture('rtsp://admin:TAV1234a@192.168.1.116:554/11')
    ret, frame = cap.read()
    
    cv2.imshow('Frame', frame)
    #image = ObreImatge('Eines/Lector-posicio/Data/IMG_6330.jpg')
    #image = ObreImatge('Eines/Lector-posicio/Data/IMG_6331.jpg')
    image = ObreImatge('Eines/Lector-posicio/Data/IMG_6332.jpg')
    #image = ObreImatge('Eines/Lector-posicio/Data/IMG_6334.jpg')
    #image = ObteCamp(image)
    Posicio, Distancia, Angle = TrobaPosicioFlor(image)
    print('Posició de la flor:', Posicio)
    print('Distancia de la flor (pixels): {:.2f}'.format(Distancia))
    print('Angle de la flor (graus): {:.2f}'.format((Angle*360)/6.28))
    cap.release()
    cv2.destroyAllWindows()  


if __name__ == "__main__":
    main()

    