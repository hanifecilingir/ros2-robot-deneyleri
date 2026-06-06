#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2 

class ImageViewer(Node):

    def __init__(self):
        super().__init__('image_viewer')
        self.subscription = self.create_subscription(
            Image,
            '/image_raw', # v4l2_camera node'u genellikle /camera/image_raw yerine /image_raw yayınlar
            self.listener_callback,
            10)
        self.br = CvBridge()
        self.get_logger().info('Kamera Görüntü Dinleyicisi Başlatıldı.')
        self.get_logger().info('Pencere açılmazsa, kamera yayıncısını ve X-Forwarding ayarlarını kontrol edin.')


    def listener_callback(self, data):
        """ROS Image mesajını alır, OpenCV formatına çevirir ve ekranda gösterir."""
        
        try:
            # KRİTİK ÇÖZÜM: 'bgr8' en yaygın format olsa da, YUYV sorunlarında 'rgb8' veya 'passthrough' 
            # çevirisini denemek genellikle çözüm olur. Pi'nin az işlem yapması için 'passthrough' deneyelim.
            # Passthrough, CvBridge'in çeviri yükünü azaltır.
            current_frame = self.br.imgmsg_to_cv2(data, desired_encoding='passthrough')
         
        except Exception as e:
            self.get_logger().error(f"CvBridge çeviri hatası: {e}")
            return
        
        # Görüntüyü ekranda gösterme
        cv2.imshow("Robot Kamera Görüntüsü", current_frame)
        cv2.waitKey(50) # Görüntü penceresini güncelleyen komut

def main(args=None):
    rclpy.init(args=args)
    image_viewer = ImageViewer()
    
    rclpy.spin(image_viewer)
    
    image_viewer.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
