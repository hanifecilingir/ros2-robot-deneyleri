import rclpy
from rclpy.node import Node
import serial
import threading

from sensor_msgs.msg import Imu, NavSatFix
from std_msgs.msg import String
from geometry_msgs.msg import Twist

class ArduinoBridge(Node):

    def __init__(self):
        super().__init__('arduino_bridge')

        # 🔧 DAHA GÜVENLİ PORT (by-id yerine)
        port = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0"
 
        # Arduino ile seri haberleşme
        self.ser = serial.Serial(port, 9600, timeout=1)
        self.get_logger().info(f"ArduinoBridge started, listening on {port} ...")

        # ---- Publishers ----
        self.imu_pub = self.create_publisher(Imu, 'imu/data_raw', 10)
        self.gps_pub = self.create_publisher(NavSatFix, 'gps/fix', 10)
        self.motor_pub = self.create_publisher(String, 'motor/state', 10)

        #---- /cmd_vel (Lidar → Engel Algoritması → Motor Komutu) ----
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10)


        # ---- Subscriber (ROS2 → Arduino) ----
        self.cmd_sub = self.create_subscription(
            String,
            'motor/cmd',
            self.send_motor_command,
            10
        )

        # ---- Seri port okuma thread ----
        self.read_thread = threading.Thread(
            target=self.read_serial_loop,
            daemon=True
        )
        self.read_thread.start()

    # ------------------------------------------------------------------
    # ROS2 → Arduino (motor komutu gönderme)
    # ------------------------------------------------------------------
    def send_motor_command(self, msg):
        cmd = msg.data.strip()
        self.get_logger().info(f"Sending to Arduino: {cmd}")
        self.ser.write((cmd + "\n").encode())

    # ===============================================================
    #  /cmd_vel → Arduino (OTOMATİK ENGEL KONTROL)
    # ===============================================================
    def cmd_vel_callback(self, msg: Twist):

            
        lin = msg.linear.x
        ang = msg.angular.z

        # İleri – dur – geri
        if lin > 0.05:
            cmd = "FORWARD,200"
        elif lin < -0.05:
            cmd = "REVERSE,200"
        else:
            cmd = "STOP"

        # --- DÖNÜŞ KOMUTU YALNIZCA HAREKET VARSA GEÇERLİ ---
        if cmd != "STOP":
            if ang > 0.2:
                cmd = "TURN_LEFT,100"
            elif ang < -0.2:
                cmd = "TURN_RIGHT,100"

        self.get_logger().info(f"/cmd_vel -> {cmd}")
        self.ser.write((cmd + "\n").encode())

    # ------------------------------------------------------------------
    # Arduino → ROS2 (seri veri okuma)
    # ------------------------------------------------------------------
    def read_serial_loop(self):
        while rclpy.ok():
            try:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                # 🔍 DEBUG (istersen aç)
                # self.get_logger().info(f"Serial: {line}")

                # ---------- IMU ----------
                if line.startswith("IMU,"):
                    parts = line.split(',')
                    if len(parts) == 7:
                        ax, ay, az, gx, gy, gz = map(float, parts[1:])
                        msg = Imu()
                        msg.linear_acceleration.x = ax
                        msg.linear_acceleration.y = ay
                        msg.linear_acceleration.z = az
                        msg.angular_velocity.x = gx
                        msg.angular_velocity.y = gy
                        msg.angular_velocity.z = gz
                        self.imu_pub.publish(msg)

                # ---------- GPS ----------
                elif line.startswith("GPS,"):
                    parts = line.split(',')
                    if len(parts) == 4:
                        lat, lon, alt = map(float, parts[1:])
                        msg = NavSatFix()
                        msg.latitude = lat
                        msg.longitude = lon
                        msg.altitude = alt
                        self.gps_pub.publish(msg)

                # ---------- MOTOR STATE ----------
                elif line.startswith("MOTOR,"):
                    data = line.replace("MOTOR,", "")
                    self.motor_pub.publish(String(data=data))

                # ---------- MOTOR CMD ACK ----------
                elif line.startswith("ACK:"):
                    self.motor_pub.publish(String(data=line))


            except Exception as e:
                self.get_logger().error(f"Serial read error: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

