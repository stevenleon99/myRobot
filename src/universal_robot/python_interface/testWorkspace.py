import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class workSpace():
    def __init__(self, widthToArm = 0, lengthToArm = 0, heightToArm = 0):
        '''origin created from robotic arm'''
        self.widthToArm = widthToArm
        self.lengthToArm = lengthToArm
        self.heightToArm = heightToArm
        '''workspace dimension'''
        self.w = 200
        self.l = 300
        self.h = 300
        '''sample rate'''
        self.sampleRate = 10
        self.angleSampleRate_1 = 1
        self.angleSampleRate_2 = 1
        '''sample angle (deg)'''
        self.angle = 30
        '''sample depth (mm)'''
        self.depth = 30
        '''coordinate'''
        self.coordinate = []
        self.trajectory = []
        '''Target Pose'''
        self.targetPosition = []
        self.targetOrientation = []

    def __str__(self):
        string = f"w: {self.w} \n " \
                 f"l: {self.l} \n " \
                 f"h: {self.h} \n " \
                 f"angle: {self.angle} \n" \
                 f"sampleRate: {self.sampleRate} \n " \
                 f"angleSampleRate_vertical: {self.angleSampleRate_1} \n " \
                 f"angleSampleRate_horizontal: {self.angleSampleRate_2}"

        return string

    def createWorkSpace(self, w, l, h, angle, sampleRate, angleSampleRate_1, angleSampleRate_2):
        self.w = w
        self.l = l
        self.h = h
        self.sampleRate = sampleRate
        self.angle = angle
        self.angleSampleRate_1 = angleSampleRate_1
        self.angleSampleRate_2 = angleSampleRate_2
        self._createSphere()
        self._createTrajectory()

    def _createSphere(self):

        ## H      L
        ## |    /
        ## |  /
        ## |/_______W

        wrate = self.w/self.sampleRate
        lrate = self.l/self.sampleRate
        hrate = self.h / self.sampleRate
        for i in range(self.sampleRate+1):
            for j in range(self.sampleRate+1):
                for k in range(self.sampleRate+1):
                    self.coordinate.append([self.widthToArm+i*wrate,
                                            self.lengthToArm+j*lrate,
                                            self.heightToArm+k*hrate])
    def _createSurfacePoint(self):
        '''
        create the trajectories for each sphere
        '''
        numberSphere = len(self.coordinate)
        '''
            \  |
             \ |
              \|  angleSample_vertical
        '''
        ang_verti_rate = self.angle / self.angleSampleRate_1
        ang_hori_rate = 360 / self.angleSampleRate_2
        for k in range(numberSphere):
            self.trajectory.append([])
            for i in range(self.angleSampleRate_1): # vertical angle
                for j in range(self.angleSampleRate_2): # horizontal angle
                    l = - math.sin(math.radians(self.angle - i * ang_verti_rate)) * self.depth * math.cos(math.radians(270 - j * ang_hori_rate)) + self.coordinate[k][1]
                    w = math.sin(math.radians(self.angle - i * ang_verti_rate)) * self.depth * math.sin(math.radians(270 - j * ang_hori_rate)) + self.coordinate[k][0]
                    h = math.cos(math.radians(self.angle - i * ang_verti_rate)) * self.depth + self.coordinate[k][2]
                    self.trajectory[k].append([w, l, h])
            self.trajectory[k].append([self.coordinate[k][0], self.coordinate[k][1], self.coordinate[k][2]+self.depth]) # add the top vertical

    def _createTrajectory(self):
        self._createSurfacePoint()

    def plotspace(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        x = np.array([i[0] for i in self.coordinate])
        y = np.array([i[1] for i in self.coordinate])
        z = np.array([i[2] for i in self.coordinate])
        ax.scatter(x, y, z)

        spaceStart_xyz = []
        spaceEnd_xyz = []
        initial = [[self.widthToArm, self.lengthToArm, self.heightToArm]]
        add = [self.w, self.l, self.h]
        iter = 0
        while 1:
            if iter >= len(initial):
                break
            start = initial[iter]
            for i in range(3):
                if start[i]+add[i] <= initial[0][i]+add[i]:
                    temp = start.copy()
                    temp[i] = start[i]+add[i]
                    initial.append(temp)
                    spaceStart_xyz.append(start)
                    spaceEnd_xyz.append(temp)
            iter += 1
        print(f"number of line {len(spaceStart_xyz)}")
        self._plottrajector(spaceStart_xyz, spaceEnd_xyz, 'blue', ax)

        trajStart, trajEnd = self._createTrajectoryLine()
        self._plottrajector(trajStart,trajEnd,'green',ax)

        ax.set_aspect('equal')
        plt.show()


    def _createTrajectoryLine(self):
        trajectoryStart = []
        trajectoryEnd = []
        for i in range(len(self.coordinate)):
            for j in range(len(self.trajectory[0])):
                trajectoryStart.append(self.coordinate[i])
                trajectoryEnd.append(self.trajectory[i][j])
        return trajectoryStart, trajectoryEnd

    def _plottrajector(self, start, end, color, ax):
        for i in range(len(start)):
            ax.plot([start[i][0], end[i][0]], [start[i][1], end[i][1]],
                    zs=[start[i][2], end[i][2]],
                    c=color)

    def createTargetPoint(self):
        self.targetPosition = self.trajectory
        return self.targetPosition

    def createTargetOrientation(self, interval=8):
        '''
        only one direction is fixed, so there are infinite solutions with fixed direction rotation
        the rotation interval is needed (default: 8)
            pilz_robot ready orientation Z-Y-X (-90, 0, -90)

        :return: the possible orientation for each trajectory
        '''



if __name__ == '__main__':
    ws = workSpace(widthToArm=300, lengthToArm=0, heightToArm=0)
    ws.createWorkSpace(300, 200, 200, 45, 1, 3, 3)
    temp = ws.createTargetPoint()
    temp = np.array(temp)
    print(temp.shape)
    ws.plotspace()




