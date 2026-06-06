import os
from glob import glob
from setuptools import find_packages, setup

# Paketin adı
package_name = 'kamera_pkg'

setup(
    name=package_name,
    version='0.0.0',
    # Bu satır, Python'a hangi alt klasörün ROS modülü olduğunu söyler.
    packages=find_packages(include=[package_name, package_name + '.*']),
    data_files=[
        # ROS 2'nin paketleri bulması için standart dosyalar
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        (os.path.join('share', package_name), glob('package.xml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robot',
    maintainer_email='robot@todo.todo',
    description='ROS 2 package for reading and displaying camera images using CvBridge',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Çalıştırılabilir düğümü tanımlıyoruz
            'image_viewer = kamera_pkg.image_viewer:main',
        ],
    },
)
