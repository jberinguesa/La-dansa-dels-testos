import cv2
import datetime

DEBUG = True

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



# Function to calculate the field size, based on the position of the first and last white pixel
# Input: image_path: path to the image file
# Output: (xmin, ymin, xmax, ymax): coordinates of the field
def CalculaMidaCamp(image):

    # Get the position of the first y white pixel
    ymin = None
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):   
            if image[y, x] == 255:
                ymin = y
                break
        if ymin is not None:
            break
    
    # Draw a grey line to indicate the position of the first y white pixel
    image[ymin, :] = 128
    
    # Get the position of the first x white pixel
    xmin = None
    for x in range(image.shape[1]):
        for y in range(image.shape[0]):
            if image[y, x] == 255:
                xmin = x
                break
        if xmin is not None:
            break
    
    # Draw a grey line to indicate the position of the first x white pixel
    image[:, xmin] = 128

    # Get the position of the last y white pixel
    ymax = None
    for y in range(image.shape[0]-1, -1, -1):
        for x in range(image.shape[1]):
            if image[y, x] == 255:
                ymax = y
                break
        if ymax is not None:
            break

    # Draw a grey line to indicate the position of the last y white pixel
    image[ymax, :] = 128

    # Get the position of the last x white pixel
    xmax = None
    for x in range(image.shape[1]-1, -1, -1):
        for y in range(image.shape[0]):
            if image[y, x] == 255:
                xmax = x
                break
        if xmax is not None:
            break

    # Draw a grey line to indicate the position of the last x white pixel
    image[:, xmax] = 128    
    
    if DEBUG:
        # Display the image with borders
        cv2.imshow('Image with borders', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Return field size
    return (xmin, ymin, xmax, ymax)

def TrobaPosicioFlor(image, field_size):
    # Crop the image to the field size
    image = image[field_size[1]:field_size[3], field_size[0]:field_size[2]]
    # Find contours
    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) 

    if DEBUG:
        #Display the cropped image
        cv2.imshow('Image cropped', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

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
    image = ObreImatge('Data/TestImage.jpg')
    MidesCamp = CalculaMidaCamp(image)
    TrobaPosicioFlor(image, MidesCamp)



if __name__ == "__main__":
    main()

    