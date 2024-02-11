import cv2
import datetime
import math

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
    retval, img_thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)

    if DEBUG:
        # Display the thresholded image
        cv2.imshow('Thresholded image', img_thresh)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

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

def TrobaPosicioFlor(image):
    # Find contours
    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) 

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
            cv2.circle(image, center, 5, (128, 128, 128), -1)
        cv2.imshow('Image amb References', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # If more than 2 centers are found, print an error message
    if len(centers) > 2:
        print('TrobaPosicioFlor: S\'han trobat més de 2 referències')
                # Save image on file, adding timestamp to the filename
        timestamp = datetime.datetime.now().strftime('_%Y%m%d_%H%M%S')
        cv2.imwrite('Data/Output/ErrorReferences'+timestamp+'.jpg', image)
        return

#Main function
def main():
    image = ObreImatge('Eines/LEctor-posicio/Data/TestImage.jpg')
    image = ObteCamp(image)
    TrobaPosicioFlor(image)



if __name__ == "__main__":
    main()

    