# Creation date: 2020-04-20
# Last modified: 2020-04-20
# Creator: Robert Guzman
# Description:
#Software for reading a GCODE file and displaying it on the screen

#Import libraries
import pygame
import pandas as pd
import untangle

# Define constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FIELD_WIDTH = 600 #In mm
FIELD_HEIGHT = 800 #In mm
X_SPRITE_SIZE = 54
Y_SPRITE_SIZE = 44
FPS = 30 #Frames per second
GCODE_SCALE = 7 #We scale the GCODE to fit the field, just x and y, no speed
SVG_SCALE = 1 #We scale the SVG to fit the field
REPRODUCTION_SPEED = 10 #To speed up the reproduction

scale = SCREEN_WIDTH / FIELD_WIDTH
file = "GCODETest.gcode"
svg_file = "Test4.svg"
export_file = "DotTest.txt"

from pygame.locals import (
    RLEACCEL,
)
############################ INSTRUCTIONS ##########################################
#GCODE and SVG files are read and stored in a list with two different type of elements:
# - F3400 Speed in mm/min
# - X100 Y200 Absolute coordinates in mm
#This list my be animated on the screen or create a file with the format
#100,200 Relative coordinates in mm
####################################################################################


################################# GCODE ############################################
#Read a GCODE file
def read_gcode_file(file_path):
    try:
        with open(file_path, 'r') as file:
            gcode_data = file.read()
    except FileNotFoundError:
        print("read_gcode_file: GCODE file not found.")

    #Filter just G0 and G1 commands
    gcode_data = gcode_data.split("\n")
    gcode_data = [line for line in gcode_data if line.startswith("G0") or line.startswith("G1")]

    #From gcode_data, it returns a list of tuples with the coordinates of the points
    points = []
    for line in gcode_data:
        line = line.split(';')[0]  # Discard everything after ';'
        if 'F' in line: #We keep F value
            f_index = line.index('F')
            f_value = line[f_index:].split(" ")[0]
            points.append(f_value)
        if ('X' in line) or ('Y' in line): #We keep X and Y values
            f_value = ''
            if 'X' in line:
                f_index = line.index('X')
                x = line.split('X')[1].split(' ')[0]
                f_value = 'X' + str(x) + ' '

            if 'Y' in line:
                f_index = line.index('Y')
                y = line.split('Y')[1].split(' ')[0]
                f_value = f_value + 'Y' + str(y)
            points.append(f_value)
    return points

################################# SVG ############################################
def read_svg_file(file_path):
    try:
        svg_data = untangle.parse(file_path)
    except FileNotFoundError:
        print("read_svg_file: SVG file not found.")

    # Get all the paths
    lines = []
    for line in svg_data.svg.g.path:
        lines.append(line['d'])
    
    # Extract the characters between 'm' and 'l' for the starting point
    if ('m' in lines[0]) and ('l' in lines[0]):
        m_index = lines[0].index('m')
        l_index = lines[0].index('l')
        start_point = lines[0][(m_index + 1):l_index]
    else:
        print("read_svg_file: No path found on file. It must be first object")
        return
 
    # Extract the characters between 'l' and 'l'
    dots_data = lines[0][l_index:]
    dots_data = dots_data.split("l")
    # Transform from 74,75 to X74 Y75
    for dot in dots_data:
        dot = 'X' + dot
        dot = dot.replace(',', ' Y')

    #From relative coordinates to absolute coordinates and store in Xxxxx Yyyyy format
    x = float(start_point.split(',')[0]) * SVG_SCALE
    y = (float(svg_data.svg._attributes['height']) - float(start_point.split(',')[1])) * SVG_SCALE
    dots_data[0] = 'X' + str(x) + ' Y' + str(y)
    for i in range(1, len(dots_data)):
        x = x + float(dots_data[i].split(',')[0]) * SVG_SCALE
        y = y - float(dots_data[i].split(',')[1]) * SVG_SCALE
        dots_data[i] = 'X' + str(x) + ' Y' + str(y) 
    
    return dots_data

def points_analytics(list_points):
    if not list_points:
        print ("points_analytics: No points to analyze.")
        return

    list_F = []
    list_X = []
    list_Y = []

    # Separation F and XY
    for record in list_points:
        if record.startswith("F"):
            list_F.append(int(record[1:]))
        if record.startswith("X"):
            list_X.append(float(record.split('X')[1].split(' ')[0]))
            list_Y.append(float(record.split('Y')[1].split(' ')[0]))
             
    if list_F: print("Fmax:" + str(max(list_F)))
    if list_F: print("Fmin:" + str(min(list_F)))
    if list_X: print("Xmax:" + str(max(list_X)))
    if list_X: print("Xmin:" + str(min(list_X)))
    if list_Y: print("Ymax:" + str(max(list_Y)))
    if list_Y: print("Ymin:" + str(min(list_Y)))


################################# ANIMATION ############################################

#It draws a screen with xmax and ymax dimensions and it draws a cercle following the GCODE commands
def animate_gcode(gcode_data):
    if not gcode_data:
        print("animate_gcode: No points to draw.")
        return
    # Define a Robot object, our sprite
    class Robot(pygame.sprite.Sprite):
        def __init__(self):
            super(Robot, self).__init__()
            self.surf = pygame.image.load("data/RobotTAV.png").convert()
            self.surf = pygame.transform.scale(self.surf, (X_SPRITE_SIZE, Y_SPRITE_SIZE)) #Scale the image
            self.surf.set_colorkey((255, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()

    # Initialize the pygame library
    pygame.init()

    # Set up the drawing window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Temps de flors 2025")
    
    # Instantiate Robot
    robot1 = Robot()

    # Text initialization
    font = pygame.font.Font('freesansbold.ttf', 25)
    
    # Run until the user asks to quit
    running = True
    n = 0
    x = xin = xfin = 0
    y = yin = yfin = 0
    a = 1
    b = 0
    t = 0
    dx = 0
    nt = 1
    no_vertical = True
    F = 1000 #Default speeed mm/min
    get_instructions = True
    clock = pygame.time.Clock()

    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if get_instructions: #Get the next instruction            
            if gcode_data[n].startswith("F"):   #Speed instruction
                F = int(gcode_data[n][1:].split(" ")[0])
                if n < len(gcode_data):
                    n += 1
            else:   #Movement instruction
                if 'X' in gcode_data[n]:
                    xfin = float(gcode_data[n].split('X')[1].split(' ')[0])
                if 'Y' in gcode_data[n]:
                    yfin = float(gcode_data[n].split('Y')[1].split(' ')[0])
                t = 1   
                if x != xfin:
                    a = (yfin - y) / (xfin - x) #Parameter of the line to go to the next point
                    no_vertical = True
                else:
                    no_vertical = False
                b = y - a * x
                length = ((xfin - x)**2 + (yfin - y)**2)**0.5 #Length of the line to go to the next point
                time = (length / (F/60))/REPRODUCTION_SPEED #Time to go to the next point
                nt = time * FPS #Number of frames to go to the next point
                dx = (xfin - x) / nt #X increment each frame
                xin = x
                yin = y
                get_instructions = False
        
        #Calculate position to draw
        x = xin + t * dx
        if no_vertical:
            y = a * x + b
        else:
            y = yin + t * (yfin - yin) / nt
        t += 1
        if t > nt:    #Have we drawn the whole line?
            get_instructions = True 
            if n < (len(gcode_data)-1):
                n += 1
            else:
                running = False   

        text1 = font.render('F: ' + str(F), True, (0, 0, 0), (255, 255, 255))
        text2 = font.render('X: ' + str(round(xfin, 2)), True, (0, 0, 0), (255, 255, 255))
        text3 = font.render('Y: ' + str(round(yfin, 2)), True, (0, 0, 0), (255, 255, 255))
    
        # Update the display
        screen.fill((0, 0, 0))  # Fill the background black
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(0, 0, FIELD_WIDTH * scale, FIELD_HEIGHT * scale)) #Draw the field in white
        pixel_x = int(round((x * scale)-X_SPRITE_SIZE/2))
        pixel_y = int(round((FIELD_HEIGHT-y) * scale - Y_SPRITE_SIZE/2))
        screen.blit(robot1.surf, (pixel_x, pixel_y))
        screen.blit(text1, (10,10))
        screen.blit(text2, (10,35))
        screen.blit(text3, (10,60))
        pygame.display.flip()
        clock.tick(FPS)
             
    # Done! Time to quit.
    pygame.quit()

def export_gcode(gcode_data):
    if not gcode_data:
        print("export_gcode: No points to export.")
        return
    
    data_file = []

    first_coordinates_found = False
    for line in gcode_data:
        if line.startswith("F"):
            F = int(line[1:].split(" ")[0])
        if line.startswith("X"):
            if not first_coordinates_found:
                x = float(line.split('X')[1].split(' ')[0])
                y = float(line.split('Y')[1].split(' ')[0])
                first_coordinates_found = True
            else:
                dx = float(line.split('X')[1].split(' ')[0]) - x
                dy = float(line.split('Y')[1].split(' ')[0]) - y
                x = float(line.split('X')[1].split(' ')[0])
                y = float(line.split('Y')[1].split(' ')[0])
                data_file.append(str(dx) + "," + str(dy))

    #Create a file with the same name and add _export
    try:
        with open(export_file, 'w') as file:
            for line in data_file:
                file.write(line + "\n")
    except FileNotFoundError:
        print("export_gcode: Error creating file.")

#Main function
def main():
    dots_gcode = read_gcode_file("gcode/"+file)
    dots_svg = read_svg_file("svg/" + svg_file)
    points_analytics(dots_svg)
    animate_gcode(dots_svg)
    export_gcode(dots_svg)


if __name__ == "__main__":
    main()

