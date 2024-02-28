import cv2

def LlegeixImatgesCalibracio():

    cap = cv2.VideoCapture('rtsp://admin:TAV1234a@192.168.1.116:554/11')

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("LlegeixFotoCamera: Could not open camera.")
        exit()

    num = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("LlegeixFotoCamera: Failed to capture frame.")
        
        k = cv2.waitKey(5)
        
        if k == 27:
            break
        elif k == ord('s'):
            num += 1
            nomfitxer = 'cali' + str(num) + '.png'
            if not cv2.imwrite('Eines/Calibracio-camera/Imatges/' + nomfitxer, frame):
                print('Error al gravar la imatge.')
            else:
                print('Imatge gravada com a ' + nomfitxer)
        
        cv2.imshow('Imatge de la càmera', frame)
    cap.release()
    cv2.destroyAllWindows()

def main():
    LlegeixImatgesCalibracio()

if __name__ == "__main__":
    main()
   