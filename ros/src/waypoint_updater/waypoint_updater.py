#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from tf.transformations import euler_from_quaternion

import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 30 # Number of waypoints we will publish. You can change this number


class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        self.sub_all_waypoints = rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below


        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)


        # TODO: Add other member variables you need below
        self.pose = None
        self.position = None
        self.heading_in_rad = None
        self.waypoints = None
        self.count = 0


        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            self.count += 1
            final_waypoints_exist = self.set_final_waypoints()

            if final_waypoints_exist:
                self.final_waypoints_pub.publish(self.final_waypoints)
            # print "hello!"
            rate.sleep()


        rospy.spin()

    def pose_cb(self, msg):
        # TODO: Implement
        self.pose = msg.pose
        # position
        self.position = self.pose.position
        # heading
        _x = self.pose.orientation.x
        _y = self.pose.orientation.y
        _z = self.pose.orientation.z
        _w = self.pose.orientation.w
        self.heading_in_rad = euler_from_quaternion([_x,_y,_z,_w])[2] # roll, pitch, yaw


    def waypoints_cb(self, waypoints):
        # TODO: Implement
        print " [*] GET WAYPOINTS ... "

        if self.waypoints == None:
            self.waypoints = []
            for _waypoint in waypoints.waypoints:
                _w = Waypoint()
                _w = _waypoint
                self.waypoints.append(_w)

    def get_closest_waypoint(self):
        closest_dist = 999999.
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(len(self.waypoints)):
            dist = dl(self.position, self.waypoints[i].pose.pose.position)
            if dist < closest_dist:
                closest_dist = dist
                closest_waypoint = i
        return closest_waypoint

    def set_final_waypoints(self):
        final_waypoints_exist = False
        if (self.waypoints is not None) and (self.position is not None):
            final_waypoints_exist = True
            closest_waypoint = self.get_closest_waypoint()

            _lookahead_wps = LOOKAHEAD_WPS
            if closest_waypoint + _lookahead_wps > len(self.waypoints):
                _lookahead_wps = len(self.waypoints) - closest_waypoint

            # set final waypoints
            self.final_waypoints = Lane()
            self.final_waypoints.waypoints = []
            for i in range(_lookahead_wps):
                self.final_waypoints.waypoints.append(self.waypoints[closest_waypoint + i])
        return final_waypoints_exist

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        pass

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
