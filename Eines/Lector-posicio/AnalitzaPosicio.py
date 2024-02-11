import cv2

def GetImageSize(image_path):

    # Read the image using OpenCV
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Check if the image was successfully read
    if image is None:
        print('No s\'ha pogut obrir el fitxer', image_path)
        return 

    # Perform adaptive thresholding
    #img_thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 7)
    # Perform global thresholding
    retval, img_thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)

    # Get the position of the first white pixel
    ymin = None
    for i in range(img_thresh.shape[0]):
        for j in range(img_thresh.shape[1]):
            if img_thresh[i, j] == 255:
                ymin = j
                break
        if ymin is not None:
            break

    # Display the image
    cv2.imshow('Image', img_thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    

#Main function
def main():
    GetImageSize('Data/TestImage.jpg')


if __name__ == "__main__":
    main()

    