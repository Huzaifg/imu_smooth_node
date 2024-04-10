import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import numpy as np

class ImuSmoothingNode(Node):
    def __init__(self):
        super().__init__('imu_smoothing_node')
        self.hz_from_actual_imu = 500
        self.hz_to_publish = 100

        self.buffer_size = int(round(self.hz_from_actual_imu / self.hz_to_publish))
        self.imu_sub = self.create_subscription(Imu, '/ARTcar/imu', self.imu_callback, self.buffer_size)
        self.imu_pub = self.create_publisher(Imu, '/ARTcar/imu_smoothed', self.buffer_size)
        self.imu_buffer = []
        self.timer = self.create_timer(1/self.hz_to_publish, self.publish_smoothed_imu)  # Timer for set hz

    def imu_callback(self, msg):
        self.imu_buffer.append(msg)
        if len(self.imu_buffer) > self.buffer_size:
            self.imu_buffer.pop(0)

    def publish_smoothed_imu(self):
        if len(self.imu_buffer) < self.buffer_size:
            return

        smoothed_imu = Imu()
        smoothed_imu.header = self.imu_buffer[-1].header
        smoothed_imu.linear_acceleration.x = np.mean([imu.linear_acceleration.x for imu in self.imu_buffer])
        smoothed_imu.linear_acceleration.y = np.mean([imu.linear_acceleration.y for imu in self.imu_buffer])
        smoothed_imu.linear_acceleration.z = np.mean([imu.linear_acceleration.z for imu in self.imu_buffer])
        self.imu_pub.publish(smoothed_imu)

def main(args=None):
    rclpy.init(args=args)
    node = ImuSmoothingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()