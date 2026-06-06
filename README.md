# ROS2 Robot Deneyleri

Bu repository, Raspberry Pi 5 üzerinde Ubuntu ve ROS2 Jazzy kullanılarak gerçekleştirilen robot deneylerine ait kaynak kodları içermektedir.

## İçerik

- Kamera görüntüsünü ROS2 üzerinden okuma ve gösterme
- Lidar sensöründen `/scan` verilerinin alınması
- Lidar verisi ile engel algılama
- `/cmd_vel` üzerinden Arduino köprüsü ile motor kontrolü

## Klasör Yapısı

```txt
ros_deneyleri_robot/
├── robot_ws/
│   └── src/
│       └── kamera_pkg
├── ros2_ws/
│   └── src/
│       ├── arduino_bridge
│       ├── obstacle_stop
│       └── sllidar_ros2
└── README.md
