import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class TaskDemo(Node):

    def __init__(self):
        super().__init__('task_demo')
        self.pub = self.create_publisher(String, '/motor/cmd', 10)

    def send(self, cmd):
        msg = String()
        msg.data = cmd
        self.pub.publish(msg)
        self.get_logger().info(f"Gönderildi: {cmd}")

def main(args=None):
    rclpy.init(args=args)
    node = TaskDemo()

    node.get_logger().info("Görev başlatıldı...")

    # 1️⃣ İleri
    node.send("FORWARD,300")
    time.sleep(2)

    node.send("STOP,0")
    time.sleep(2)

    # 2️⃣ Geri
    node.send("REVERSE,300")
    time.sleep(2)

    node.send("STOP,0")
    time.sleep(2)

    # 3️⃣ Sola dön
    node.send("TURN_LEFT,200")
    time.sleep(2)

    node.send("STOP,0")
    time.sleep(2)

    # 4️⃣  ➜ Eski hizaya dön (sağa dönüş)
    node.send("TURN_RIGHT,200")
    time.sleep(2)

    node.send("STOP,0")
    time.sleep(1)

    node.get_logger().info("Görev tamamlandı.")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
