import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleStopNode(Node):
    def __init__(self):
        super().__init__('obstacle_stop_node')

        # Lidar verisi /scan'den geliyor
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Hız komutlarını /cmd_vel'e yayınlayacağız
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Parametreler
        self.safe_distance = 0.5   # m: Engel varsa bu mesafenin altı tehlikeli
        self.forward_speed = 0.2   # m/s: Yol boşken ileri hız

        self.obstacle_detected = False

        # Her 0.1 saniyede bir hız komutu üret
        self.timer = self.create_timer(0.1, self.timer_callback)

        self.get_logger().info('ObstacleStopNode started.')

    def scan_callback(self, msg: LaserScan):
        """
        /scan verisini al, robotun önündeki (−30° ... +30°)
        açı aralığındaki minimum mesafeyi hesapla.
        """
        min_distance = float('inf')
        angle = msg.angle_min

        for r in msg.ranges:

            # Geçersiz değerleri atla
            if math.isinf(r) or math.isnan(r):
                angle += msg.angle_increment
                continue

            # Ön sektör: -30° ile +30° arası
            if -math.radians(30) <= angle <= math.radians(30):
                if r < min_distance:
                    min_distance = r

            angle += msg.angle_increment

        # Engel var mı kontrol et
        if min_distance < self.safe_distance:
            if not self.obstacle_detected:
                self.get_logger().info(
                    f'Obstacle detected! distance={min_distance:.2f} m'
                )
            self.obstacle_detected = True
        else:
            if self.obstacle_detected:
                self.get_logger().info('Path is clear again.')
            self.obstacle_detected = False

    def timer_callback(self):
        """
        Engel yoksa ileri, engel varsa tamamen dur.
        """
        twist = Twist()

        if self.obstacle_detected:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
            twist.linear.x = self.forward_speed
            twist.angular.z = 0.0

        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleStopNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
