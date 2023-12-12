#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#moveit_fk_demo.py
 
import rospy, sys
import moveit_commander
import math
from testWorkspace import *
import moveit_msgs.msg
import geometry_msgs.msg
import sys
import copy
from scipy.spatial.transform import Rotation as R

class MoveItFkDemo:
    def __init__(self):
        self._prevPose = {"position":[0,0,0], "orientation": [0,0,0,1]}
        self._prevJoints = [0,0,0,0,0,0]
        # 初始化move_group的API,出现roscpp是因为底层是通过C++进行实现的
        moveit_commander.roscpp_initialize(sys.argv)
 
        # 初始化ROS节点，节点名为'moveit_fk_demo'
        rospy.init_node('moveit_fk_demo', anonymous=True)       
 
        # 初始化需要使用move group控制的机械臂中的arm group
        self.arm = moveit_commander.MoveGroupCommander('manipulator')
        # 设置机械臂运动的允许误差值，单位弧度
        self.arm.set_goal_joint_tolerance(0.001)
 
        # 设置允许的最大速度和加速度，范围0~1
        self.arm.set_max_acceleration_scaling_factor(0.5)
        self.arm.set_max_velocity_scaling_factor(0.5)
        
        # 控制机械臂先回到初始化位置，home是setup assistant中设置的
        self.arm.set_named_target('home')
        self.arm.go()  #让机械臂先规划，再运动，阻塞指令，直到机械臂到达home后再向下执行
        rospy.sleep(1)
        
    def close(self):
        # 关闭并退出moveit
        moveit_commander.roscpp_shutdown()
        moveit_commander.os._exit(0)

    def demo(self):
        self.rotate_demo()
        rospy.sleep(1)
        self.moveByPose_demo()
        rospy.sleep(1)

    def rotate_demo(self):
        joint1 = [2, -91, 107, -12, 93, -180]
        joint2 = [2, -81, 93, 33, 92, -178]
        for i in range(len(joint1)):
            joint1[i] = self.angle2rad(joint1[i])
            joint2[i] = self.angle2rad(joint2[i])
        self.arm_move(joint1)

        print("=============ready positon pose")
        self.get_current_pose()
        print("position: ", self._prevPose["position"])
        print("orientation: ", self._prevPose["orientation"])

        self.arm_move(joint2)
        self.arm.clear_pose_targets()

        
    def moveByPose_demo(self):
        self.moveByPose([0.3, 0, 0.2], self.euler_to_quaternion(self.angle2rad(-90), 
                                                                     self.angle2rad(0), 
                                                                     self.angle2rad(-90)))
        self.moveByPose([0.3, 0, 0.2], self.euler_to_quaternion(self.angle2rad(-105), 
                                                                     self.angle2rad(0), 
                                                                     self.angle2rad(-90)))

    def moveByPose(self, position, orientation = [-0.5, 0.5, -0.5, 0.5]):
        posegoal = geometry_msgs.msg.Pose()
        posegoal.position.x = position[0]
        posegoal.position.y = position[1]
        posegoal.position.z = position[2]
        posegoal.orientation.x = orientation[0]
        posegoal.orientation.y = orientation[1]
        posegoal.orientation.z = orientation[2]
        posegoal.orientation.w = orientation[3]
        self.arm.set_pose_target(posegoal)
        # `go()` returns a boolean indicating whether the planning and execution was successful.
        success = self.arm.go(wait=True)
        # Calling `stop()` ensures that there is no residual movement
        self.arm.stop()
        # It is always good to clear your targets after planning with poses.
        # Note: there is no equivalent function for clear_joint_value_targets().
        self.arm.clear_pose_targets()

        print("=============ready positon pose")
        self.get_current_pose()
        print("position: ", self._prevPose["position"])
        print("orientation: ", self._prevPose["orientation"])

    def angle2rad(self, angle):
        return math.radians(angle)

    def arm_move(self, joint):
        self.arm.set_joint_value_target(joint)
        self.arm.go()   #规划+执行
        self.arm.stop()
        self.arm.clear_pose_targets()
        rospy.sleep(1)

    def get_current_pose(self):
        pose = self.arm.get_current_pose()
        self._prevPose["position"][0] = pose.pose.position.x
        self._prevPose["position"][1] = pose.pose.position.y
        self._prevPose["position"][2] = pose.pose.position.z

        self._prevPose["orientation"][0] = pose.pose.orientation.x
        self._prevPose["orientation"][1] = pose.pose.orientation.y
        self._prevPose["orientation"][2] = pose.pose.orientation.z
        self._prevPose["orientation"][3] = pose.pose.orientation.w


    def get_current_joints(self):
        joints = self.arm.get_current_joint_values()
        for i in range(len(joints)):
            self._prevJoints[i] = joints[i]

    #Euler Z-Y-X system#
    def euler_to_quaternion(self, roll, pitch, yaw):

        qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
        qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
        qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)

        return [qx, qy, qz, qw]

    def quaternion_to_euler(self, x, y, z, w):

        import math
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        X = math.degrees(math.atan2(t0, t1))

        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        Y = math.degrees(math.asin(t2))

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        Z = math.degrees(math.atan2(t3, t4))

        return X, Y, Z

 
if __name__ == "__main__":
    ws = workSpace(widthToArm=300, lengthToArm=0, heightToArm=0)
    ws.createWorkSpace(300, 400, 1000, 45, 1, 3, 3)
    temp = ws.createTargetPoint()
    print("=============init test work space")
    print(ws)
    md = MoveItFkDemo()
    for coord in ws.coordinate:

        try:
            md.moveByPose([i/1000 for i in coord])
        except rospy.ROSInterruptException:
            pass
    
    md.close()

