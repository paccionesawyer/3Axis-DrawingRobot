'''
Homework 3 - ME 134 - Robotics 
Group 5 : Sawyer Paccione, Rebecca Shen, Matt Toven

Description: A class for controlling a 3DOF Arm
'''

import time
import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import math

import sys,tty,termios

from tkinter import Tk, Canvas, Button

import json

class RobotArm():
    def __init__(self):
        '''
        Set channels to the number of servo channels on your kit.
        8 for FeatherWing, 16 for Shield/HAT/Bonnet.
        '''
        self.kit = ServoKit(channels=16)

        self.base  = self.kit.servo[0]
        self.shldr = self.kit.servo[1]
        self.elbow = self.kit.servo[2]

        self.d1 = 25 # mm
        self.a2 = 105 # mm
        self.a3 = 118 # mm

        self.BASE_MAX = 180 # 180
        self.BASE_MIN = 75 # 75
        self.BASE_MATH_MAX = -45 # 
        self.BASE_MATH_MIN = -150 # 

        self.SHLDR_MAX = 70 # 90
        self.SHLDR_MIN = 24 # 24
        self.SHLDR_MATH_MAX = 28 # 30
        self.SHLDR_MATH_MIN = -30 # -36

        self.ELBOW_MAX = 180 #
        self.ELBOW_MIN = 0 #
        self.ELBOW_MATH_MAX = 120 # 
        self.ELBOW_MATH_MIN = -60 #

        self.PAPER_Z = -31

        self.servos = [self.base, self.shldr, self.elbow]

        self.servoAngles = [135,60,60]
        self.moveToAngles()
        self.runMode()

    def rebeccaMath(self, x,y,z):
        print(x,y,z)
        theta1 = math.atan2(y,x)
        r_1 = math.sqrt(x**2 + y**2)
        r_2 = z - self.d1
        print("theta1", theta1)
        phi_2 = math.atan2(r_2, r_1)
        r_3 = math.sqrt(r_1**2 + r_2**2)

        phi_1 = math.acos((self.a3**2-self.a2**2-r_3**2)/(-2*self.a2*r_3))
        theta2 = phi_2-phi_1
        phi_3 = math.acos((r_3**2-self.a2**2-self.a3**2)/(-2*self.a2*self.a3))
        theta3 = math.pi-phi_3

        x1 = math.cos(theta1)*(self.a2*math.cos(theta2)+self.a3*math.cos(theta2+theta3))
        y1 = math.sin(theta1)*(self.a2*math.cos(theta2)+self.a3*math.cos(theta2+theta3))
        z1 = self.a3*math.sin(theta2+theta3)+self.a2*math.sin(theta2)+self.d1

        print([x1,y1,z1])

        theta1Deg = math.degrees(theta1)
        theta2Deg = math.degrees(theta2)
        theta3Deg = math.degrees(theta3)

        print([theta1Deg, theta2Deg, theta3Deg])

        goodDegrees = self.mathDegToNormDeg([theta1Deg, theta2Deg, theta3Deg])
        print(goodDegrees)
        # self.moveToAngles(goodDegrees[0], goodDegrees[1], goodDegrees[2])


    def mathDegToNormDeg(self, thetas):
        goodDeg1 = thetas[0] + 135

        goodDeg2 = 60 - thetas[1]

        goodDeg3 = 60 - thetas[2]

        return [goodDeg1, goodDeg2, goodDeg3]

    def get_x_and_y(self, event):
        self.lasx, self.lasy = event.x, event.y
        print(self.lasx, self.lasy)
        
        
        
    def draw_smth(self, event):
        self.canvas.create_line((self.lasx, self.lasy, event.x, event.y), 
                        fill='red', 
                        width=2)

        prevx = self.lasx 
        prevy = self.lasy
        self.lasx, self.lasy = event.x, event.y

        xdiff = self.lasx - prevx
        ydiff = self.lasy - prevy

        self.moveDist(0,-xdiff/4)
        self.moveDist(1,ydiff/8)

        print(self.lasx, self.lasy)
        # self.rebeccaMath(self.lasx, self.lasy, self.PAPER_Z)
        # print("HTRERERASDFGSFDG")
        self.canvasPoints.append([self.lasx, self.lasy])


    def startDrawCanvas(self):
        halfPoints = self.canvasPoints[::2]
        print(halfPoints)
        
        for point in halfPoints:
            pageX = self.translateAngles(point[0], 0, 320, 0, 70)
            pageY = self.translateAngles(point[0], 0, 480, 0, 105)
            
            # self.rebeccaMath(pageX, pageY, self.PAPER_Z)
            self.app.destroy()


    def lcdScreenMode(self):
        self.app = Tk()
        self.app.geometry("480x320")
        self.canvas = Canvas(self.app, bg='black')
        self.canvas.pack(anchor='nw', fill='both', expand=1)

        self.canvasPoints = []

        print('here')

        self.lasx = 0
        self.lasy = 0

        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw_smth)

        btn1 = Button(self.app, text='Quit', width=10,
                    height=2, bd='2', command=self.app.destroy)
        btn2 = Button(self.app, text='Run', width=10,
                    height=2, bd='2', command=self.startDrawCanvas)
        btn1.place(x=0, y=0)
        btn2.place(x=400,y=0)

        self.app.mainloop()

    def runMode(self):
        response = input("Hello Potential User! How would you like to control the motor? \nType (1) for TouchScreen (2) for Keyboard or (3) for Initial Writings (4) for UserInputTesting (5) for Coordinate Control? ")

        while response not in ['1','2','3','4','5']: 
            print("I don't recognize that answer...")
            response = input("Type (1) for TouchScreen (2) for Keyboard or (3) for Initial Writings (4) for UserInputTesting (5) for Coordinate Control? ")

        if response == "1":
            self.lcdScreenMode()
        elif response == "2":
            self.keyboardControl()
        elif response == "3":
            raise NotImplementedError
        elif response == '4':
            self.userMathInput()
        elif response == '5':
            self.coordinateControl()

    def moveToAngles(self, angle1=135, angle2=60, angle3=60):
        '''
        Moves the servo motors to the specified angles, the default behaviour of this function to stick the arm straight out.
        '''
        self.kit.servo[0].angle = angle1
        self.kit.servo[1].angle = angle2
        self.kit.servo[2].angle = angle3

        self.servoAngles = [angle1, angle2, angle3]

    def touchScreenToPoint(self):
        '''
        Takes input from the XPT2046 Touch Controller and translates it to x,y,
        z coordinates
        '''

        return x, y, z

    def togglePen(self):
        '''
        Toggles the pen from the up and down direction
        '''

        return True

    def drawInitials(self):
        '''
        Draws the pre-determined for the initials of all three group members
        "SP", "RS", "MT"
        '''

        return True 

    def getKeyboardInput(self):
        '''
        Gets a character input from the command line
        '''
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            test = sys.stdin.read(1)
            if test == 'w' or test == 's':
                pass
            else :
                test = test + sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return test

    def printCurrAngles(self):
        '''
        Prints the current angles of the servo motors
        '''
        counter = 0
        for angle in self.servoAngles:
            print("Servo", counter, ": ", angle)
            counter += 1

    def moveDist(self, motorNumber, distance):
        '''
        Move the servo motors the specified distance in degrees
        '''
        newPos = self.servoAngles[motorNumber] + distance
        
        if newPos < 180 and newPos > 0 :
            self.kit.servo[motorNumber].angle = newPos
            self.servoAngles[motorNumber] = newPos
        
        self.printCurrAngles()
            
    def keyboardControl(self):
        '''
        Left and Right Arrow Keys to control BASE Motor
        Up and Down Arrow Keys to control SHOULDER Motor
        W and S to control ELBOW Motor
        '''
        while True:
            k = self.getKeyboardInput()
            print(k)
            if k == '':
                continue
            elif k == '\x1b[A':
                self.moveDist(1,-2)
            elif k == '\x1b[B':
                self.moveDist(1,2)
            elif k == '\x1b[C':
                self.moveDist(0,-2)
            elif k == '\x1b[D':
                self.moveDist(0,2)
            elif k == 'w':
                self.moveDist(2,-2)
            elif k == 's':
                self.moveDist(2,2)
            elif k == 'ooo':
                break
            else:
                print ("not an arrow key!")

    def coordinateControl(self):
        '''
        Control the Robot Arm by providing it coordinates
        '''

        #### TODO : Validate Length MAX

        while True: 
            coordinates = input("Please Enter Coordinates ('x,y,z'): ")
            listofCoords = coordinates.split(',')

            xCoord = int(listofCoords[0]) + 58
            yCoord = int(listofCoords[1])
            zCoord = int(listofCoords[2]) 

            self.rebeccaMath(xCoord, yCoord, zCoord)

    def translateAngles(self, value, fromMin, fromMax, toMin, toMax):
        '''
        Translate a number from one range to another range 
        '''
        # Figure out how 'wide' each range is
        fromSpan = fromMax - fromMin
        toSpan = toMax - toMin

        # Convert the from range into a 0-1 range (float)
        valueScaled = float(value - fromMin) / float(fromSpan)

        # Convert the 0-1 range into a value in the to range.
        return toMin + (valueScaled * toSpan)

    def userMathInput(self):
        '''
        Ask user for input to specify the angle of each motor
        '''

        while True:
            motor = input("What motor would you like to adjust? (Base, Shoulder, Elbow)? ")

            angle = int(input("What MATH angle do you want the " + motor + " motor to be at? "))

            if motor.lower() == "base":
                angle = self.translateAngles(angle, self.BASE_MATH_MIN, self.BASE_MATH_MAX, self.BASE_MIN, self.BASE_MAX)
                self.moveToAngles(angle1=angle)
            if motor.lower() == "shoulder":
                angle = self.translateAngles(angle, self.SHLDR_MATH_MIN, self.SHLDR_MATH_MAX, self.SHLDR_MIN, self.SHLDR_MAX)
                self.moveToAngles(angle2=angle)
            if motor.lower() == "elbow":
                angle = self.translateAngles(angle, self.BASE_MATH_MIN, self.BASE_MATH_MAX, self.BASE_MIN, self.BASE_MAX)
                self.moveToAngles(angle3=angle)
            print(angle)
        

    def pointToAngles(self, x, y, z):
        '''
        Given an x,y,z coordinate, move the motors to angles that work
        '''
        # Collect the list of all angles
        listofAngles = self.solveInverse(x,y,z)
        
        # Convert all angles to Degrees 

        print("All possible angles", listofAngles)

        # Find the best of those angles 
        bestAngles = self.getBestAngles(listofAngles)

        print("Best angle found In Degrees", bestAngles)

        self.moveToAngles(bestAngles[0], bestAngles[1], bestAngles[2])

    def getBestAngles(self, listofAngles):
        '''
        Run an algorithm to determine the best angle set to use
        '''

        goodList = []

        # Check to see which set is in bounds
        for angleSet in listofAngles:
            baseTheta  = self.translateAngles(math.degrees(angleSet[0]), self.BASE_MATH_MIN, self.BASE_MATH_MAX, self.BASE_MIN, self.BASE_MAX)
            shldrTheta = self.translateAngles(math.degrees(angleSet[1]), self.SHLDR_MATH_MIN, self.SHLDR_MATH_MAX, self.SHLDR_MIN, self.SHLDR_MAX)
            elbowTheta = self.translateAngles(math.degrees(angleSet[2]), self.ELBOW_MATH_MIN, self.ELBOW_MATH_MAX, self.ELBOW_MIN, self.ELBOW_MAX)
            if baseTheta < self.BASE_MATH_MIN or baseTheta > self.BASE_MATH_MAX:
                listofAngles.remove(angleSet)
            elif shldrTheta < self.SHLDR_MATH_MIN or shldrTheta > self.SHLDR_MATH_MAX:
                listofAngles.remove(angleSet)
            elif elbowTheta < self.ELBOW_MATH_MIN or elbowTheta > self.ELBOW_MATH_MAX:
                listofAngles.remove(angleSet)
            
            goodList.append([baseTheta,shldrTheta,elbowTheta])

        # Closest to current set of angles

        dist = 1000000
        index = 0
        counter = 0

        if len(goodList) == 0:
            print("NOT POSSIBLE SORRY")
            return None 
        elif len(goodList) == 1:
            return goodList[0]
        else:
            for angleSet in goodList:
                new_dist = math.sqrt((self.servoAngles[0] - angleSet[0])**2+(self.servoAngles[1] - angleSet[1])**2+(self.servoAngles[2] - angleSet[2])**2)

                if new_dist < dist :
                    dist = new_dist
                    index = counter

                counter += 1

        return goodList[index]

    def solveInverse(self, xe, ye, ze):
        '''
        Given an x,y,z coordinate, solve a translation matrix to angles for the 
        three motors
        Returns: 4 Arrays of Angles 
        '''

        d1 = self.d1 
        a2 = self.a2 
        a3 = self.a3

        theta1a = math.atan2((xe*math.sqrt(a2**6*(-d1**2 + xe**2 + ye**2 + 2*d1*ze - ze**2) - a2**2*(d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 + 2*a2**4*(a3**2*(d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2) + (d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2) - 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2*(a2**4 + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 - 2*a2**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2))))*(a2**6*(xe**2 + ye**2) + 2*a2**4*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2) + a2**2*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2*(a2**4 + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 - 2*a2**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)))))/(a2*(xe**2 + ye**2)*math.sqrt(a2**4*(d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2)*(a2**6 - a2**4*(3*a3**2 + d1**2 - 3*xe**2 - 3*ye**2 - 2*d1*ze + ze**2) + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**3 + a2**2*(3*a3**4 - d1**4 + 3*xe**4 + 6*xe**2*ye**2 + 3*ye**4 + 4*d1**3*ze + 2*xe**2*ze**2 + 2*ye**2*ze**2 - ze**4 + 2*d1**2*(xe**2 + ye**2 - 3*ze**2) - 4*d1*ze*(xe**2 + ye**2 - ze**2) - 2*a3**2*(d1**2 + 3*xe**2 + 3*ye**2 - 2*d1*ze + ze**2)))), (ye*math.sqrt(a2**6*(-d1**2 + xe**2 + ye**2 + 2*d1*ze - ze**2) - a2**2*(d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 + 2*a2**4*(a3**2*(d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2) + (d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2) - 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2*(a2**4 + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 - 2*a2**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2))))*(a2**6*(xe**2 + ye**2) + 2*a2**4*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2) + a2**2*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2*(a2**4 + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 - 2*a2**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)))))/(a2*(xe**2 + ye**2)*math.sqrt(a2**4*(d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2)*(a2**6 - a2**4*(3*a3**2 + d1**2 - 3*xe**2 - 3*ye**2 - 2*d1*ze + ze**2) + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**3 + a2**2*(3*a3**4 - d1**4 + 3*xe**4 + 6*xe**2*ye**2 + 3*ye**4 + 4*d1**3*ze + 2*xe**2*ze**2 + 2*ye**2*ze**2 - ze**4 + 2*d1**2*(xe**2 + ye**2 - 3*ze**2) - 4*d1*ze*(xe**2 + ye**2 - ze**2) - 2*a3**2*(d1**2 + 3*xe**2 + 3*ye**2 - 2*d1*ze + ze**2)))))
        theta2a = math.atan2((2*math.sqrt(a2**6*(-d1**2 + xe**2 + ye**2 + 2*d1*ze - ze**2) - a2**2*(d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 + 2*a2**4*(a3**2*(d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2) + (d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2) - 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2*(a2**4 + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 - 2*a2**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)))))/math.sqrt(a2**4*(d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2), -((2*(a2**6*(d1 - ze)**2 + 2*a2**4*(d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2) + a2**2*(d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2*(a2**4 + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 - 2*a2**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)))))/(a2**3*(d1 - ze)*(d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2))))
        theta3a = math.atan2((-a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)/(a2*a3), (math.sqrt(a2**6*(-d1**2 + xe**2 + ye**2 + 2*d1*ze - ze**2) - a2**2*(d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 + 2*a2**4*(a3**2*(d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2) + (d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2) - 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2*(a2**4 + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 - 2*a2**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2))))*((-a2**6)*(d1 - ze)**2 - a2**2*(d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 + 2*a2**4*(d1 - ze)**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2) + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2*(a2**4 + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2 - 2*a2**2*(a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)))))/(a2**2*a3*(d1 - ze)*math.sqrt(a2**4*(d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2)*(a2**4 - 2*a2**2*(a3**2 + d1**2 - xe**2 - ye**2 - 2*d1*ze + ze**2) + (-a3**2 + d1**2 + xe**2 + ye**2 - 2*d1*ze + ze**2)**2)))

        theta1b = math.atan2(-((xe* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 - 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))*((xe**2 + ye**2)*a2**6 + 2*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/ (a2*(xe**2 + ye**2)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*(a2**6 - (3*a3**2 + d1**2 - 3*xe**2 - 3*ye**2 + ze**2 - 2*d1*ze)*a2**4 + (3*a3**4 - 2*(d1**2 - 2*ze*d1 + 3*xe**2 + 3*ye**2 + ze**2)*a3**2 - d1**4 + 3*xe**4 + 3*ye**4 - ze**4 + 6*xe**2*ye**2 + 2*xe**2*ze**2 + 2*ye**2*ze**2 + 4*d1**3*ze - 4*d1*ze*(xe**2 + ye**2 - ze**2) + 2*d1**2*(xe**2 + ye**2 - 3*ze**2))* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**3))), -((ye* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 - 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))*((xe**2 + ye**2)*a2**6 + 2*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/ (a2*(xe**2 + ye**2)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*(a2**6 - (3*a3**2 + d1**2 - 3*xe**2 - 3*ye**2 + ze**2 - 2*d1*ze)*a2**4 + (3*a3**4 - 2*(d1**2 - 2*ze*d1 + 3*xe**2 + 3*ye**2 + ze**2)*a3**2 - d1**4 + 3*xe**4 + 3*ye**4 - ze**4 + 6*xe**2*ye**2 + 2*xe**2*ze**2 + 2*ye**2*ze**2 + 4*d1**3*ze - 4*d1*ze*(xe**2 + ye**2 - ze**2) + 2*d1**2*(xe**2 + ye**2 - 3*ze**2))* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**3))))
        theta2b = math.atan2(-((1/math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2))* (2* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 - 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))), -((2*((d1 - ze)**2*a2**6 + 2*(d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/ (a2**3*(d1 - ze)*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze))))
        theta3b = math.atan2((-a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)/(a2*a3), (math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 - 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))*((d1 - ze)**2*a2**6 - 2*(d1 - ze)**2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 - math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/ (a2**2*a3*(d1 - ze)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*(a2**4 - 2*(a3**2 + d1**2 - xe**2 - ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))

        theta1c = math.atan2((xe*((xe**2 + ye**2)*a2**6 + 2*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 - math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 + 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/(a2*(xe**2 + ye**2)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)* (a2**6 - (3*a3**2 + d1**2 - 3*xe**2 - 3*ye**2 + ze**2 - 2*d1*ze)* a2**4 + (3*a3**4 - 2*(d1**2 - 2*ze*d1 + 3*xe**2 + 3*ye**2 + ze**2)*a3**2 - d1**4 + 3*xe**4 + 3*ye**4 - ze**4 + 6*xe**2*ye**2 + 2*xe**2*ze**2 + 2*ye**2*ze**2 + 4*d1**3*ze - 4*d1*ze*(xe**2 + ye**2 - ze**2) + 2*d1**2*(xe**2 + ye**2 - 3*ze**2))*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**3)), (ye*((xe**2 + ye**2)*a2**6 + 2*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 - math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 + 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/(a2*(xe**2 + ye**2)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)* (a2**6 - (3*a3**2 + d1**2 - 3*xe**2 - 3*ye**2 + ze**2 - 2*d1*ze)* a2**4 + (3*a3**4 - 2*(d1**2 - 2*ze*d1 + 3*xe**2 + 3*ye**2 + ze**2)*a3**2 - d1**4 + 3*xe**4 + 3*ye**4 - ze**4 + 6*xe**2*ye**2 + 2*xe**2*ze**2 + 2*ye**2*ze**2 + 4*d1**3*ze - 4*d1*ze*(xe**2 + ye**2 - ze**2) + 2*d1**2*(xe**2 + ye**2 - 3*ze**2))*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**3)))
        theta2c = math.atan2((1/math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2))* (2* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 + 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))), -((2*((d1 - ze)**2*a2**6 + 2*(d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 - math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/ (a2**3*(d1 - ze)*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze))))
        theta3c = math.atan2((-a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)/(a2*a3), -((((d1 - ze)**2*a2**6 - 2*(d1 - ze)**2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)* a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 + 2* math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/ (a2**2*a3*(d1 - ze)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*(a2**4 - 2*(a3**2 + d1**2 - xe**2 - ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))

        theta1d = math.atan2(-((xe*((xe**2 + ye**2)*a2**6 + 2*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 - math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 + 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/(a2*(xe**2 + ye**2)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)* (a2**6 - (3*a3**2 + d1**2 - 3*xe**2 - 3*ye**2 + ze**2 - 2*d1*ze)* a2**4 + (3*a3**4 - 2*(d1**2 - 2*ze*d1 + 3*xe**2 + 3*ye**2 + ze**2)*a3**2 - d1**4 + 3*xe**4 + 3*ye**4 - ze**4 + 6*xe**2*ye**2 + 2*xe**2*ze**2 + 2*ye**2*ze**2 + 4*d1**3*ze - 4*d1*ze*(xe**2 + ye**2 - ze**2) + 2*d1**2*(xe**2 + ye**2 - 3*ze**2))*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**3))), -((ye*((xe**2 + ye**2)*a2**6 + 2*(xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (xe**2 + ye**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 - math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 + 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/(a2*(xe**2 + ye**2)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)* (a2**6 - (3*a3**2 + d1**2 - 3*xe**2 - 3*ye**2 + ze**2 - 2*d1*ze)* a2**4 + (3*a3**4 - 2*(d1**2 - 2*ze*d1 + 3*xe**2 + 3*ye**2 + ze**2)*a3**2 - d1**4 + 3*xe**4 + 3*ye**4 - ze**4 + 6*xe**2*ye**2 + 2*xe**2*ze**2 + 2*ye**2*ze**2 + 4*d1**3*ze - 4*d1*ze*(xe**2 + ye**2 - ze**2) + 2*d1**2*(xe**2 + ye**2 - 3*ze**2))*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**3))))
        theta2d = math.atan2(-((1/math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2))* (2* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 + 2*math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))), -((2*((d1 - ze)**2*a2**6 + 2*(d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 - math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/ (a2**3*(d1 - ze)*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze))))
        theta3d = math.atan2((-a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)/(a2*a3), (((d1 - ze)**2*a2**6 - 2*(d1 - ze)**2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**4 + (d1 - ze)**2*(-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*a2**2 + math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2*(a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))* math.sqrt((-d1**2 + 2*ze*d1 + xe**2 + ye**2 - ze**2)*a2**6 + 2*((d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* a3**2 + (d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)* a2**4 - (d1**2 - 2*ze*d1 - xe**2 - ye**2 + ze**2)* (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* a2**2 + 2* math.sqrt((-a2**4)*(xe**2 + ye**2)*(d1 - ze)**2*(a2**2 - a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2* (a2**4 - 2*(a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)* a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2))))/ (a2**2*a3*(d1 - ze)* math.sqrt(a2**4*(d1**2 - 2*ze*d1 + xe**2 + ye**2 + ze**2)**2)*(a2**4 - 2*(a3**2 + d1**2 - xe**2 - ye**2 + ze**2 - 2*d1*ze)*a2**2 + (-a3**2 + d1**2 + xe**2 + ye**2 + ze**2 - 2*d1*ze)**2)))

        listofAngles = [[theta1a, theta2a, theta3a], [theta1b, theta2b, theta3b], [theta1c, theta2c, theta3c], [theta1d, theta2d, theta3d]]

        return listofAngles

if __name__ == "__main__":
    steve = RobotArm()

