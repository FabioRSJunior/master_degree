import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
from sensor_msgs.msg import Image, Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import csv
import cv2
import os
from cv_bridge import CvBridge
from datetime import datetime, time
from std_msgs.msg import Float32


class DataCollector(Node):
    def __init__(self):
        super().__init__('data_collector')
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.cmd_vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.linear_velocity_sub = self.create_subscription(Odometry, '/odom', self.linear_velocity_callback, 10) # novo vel linar 
        self.imu_sub = self.create_subscription(Imu, '/imu', self.imu_callback, 10)
        self.error_sub = self.create_subscription(Float32, '/error_value', self.error_callback, 10)
        self.action_sub = self.create_subscription(Float32, '/action_value', self.action_callback, 10)

        self.bridge = CvBridge()

        self.odom_data = []
        self.cmd_vel_data = []
        self.imu_data = []
        self.start_time = None # salva o tempo na simulação 
        self.error_data = [] # salva os erros de posição
        self.linear_velocity_data = [] # salva a velocidade linear

        # Criar serviços
        self.start_service = self.create_service(Empty, 'start_data_collector', self.start_data_collector_callback)
        self.stop_service = self.create_service(Empty, 'stop_data_collector', self.stop_data_collector_callback)

        self.collecting_data = False
        self.simulation_dir = None

    def start_data_collector_callback(self, request, response):
        if not self.collecting_data:
            self.simulation_dir = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            os.makedirs(self.simulation_dir, exist_ok=True)
            self.collecting_data = True
            
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.salvar_tempo_simulacao(self.simulation_dir, 'início', start_time)
            
            self.get_logger().info(f'Data collection started. Directory: {self.simulation_dir}')
        else:
            self.get_logger().info('Data collection is already running.')
        return response

    def stop_data_collector_callback(self, request, response):

        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.salvar_tempo_simulacao(self.simulation_dir, 'fim', end_time)

        if self.collecting_data:
            self.collecting_data = False
            self.get_logger().info('Data collection stopped.')
        else:
            self.get_logger().info('Data collection is not running.')
        return response

    def salvar_tempo_simulacao(self, diretorio, tipo, horario):
        """
        Salva o tempo de início ou fim da simulação em um arquivo txt.

        Args:
            diretorio (str): Caminho da pasta da simulação.
            tipo (str): 'início' ou 'fim'.
            horario (str): Horário formatado como string.
        """
        caminho_arquivo = os.path.join(diretorio, 'tempo_simulacao.txt')
        linha = f'Tempo de {tipo}: {horario}\n'
        with open(caminho_arquivo, 'a') as f:
            f.write(linha)


    def odom_callback(self, msg):
        if self.collecting_data:
            odom_record = [msg.header.stamp.sec, msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z,
                           msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w]
            self.odom_data.append(odom_record)
            with open(os.path.join(self.simulation_dir, 'odom_data.csv'), 'a') as f:
                writer = csv.writer(f)
                writer.writerow(odom_record)

    def cmd_vel_callback(self, msg):
        if self.collecting_data:
            cmd_vel_record = [msg.linear.x, msg.linear.y, msg.linear.z, msg.angular.x, msg.angular.y, msg.angular.z]
            self.cmd_vel_data.append(cmd_vel_record)
            with open(os.path.join(self.simulation_dir, 'cmd_vel_data.csv'), 'a') as f:
                writer = csv.writer(f)
                writer.writerow(cmd_vel_record)

    def linear_velocity_callback(self, msg):
        if self.collecting_data:
            linear_velocity_record = [
                msg.header.stamp.sec,
                msg.twist.twist.linear.x,
                msg.twist.twist.linear.y,
                msg.twist.twist.linear.z
            ]
            self.linear_velocity_data.append(linear_velocity_record)
            with open(os.path.join(self.simulation_dir, 'linear_velocity_data.csv'), 'a') as f:
                writer = csv.writer(f)
                writer.writerow(linear_velocity_record)


    def imu_callback(self, msg):
        if self.collecting_data:
            imu_record = [msg.header.stamp.sec, msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w,
                          msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z,
                          msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z]
            self.imu_data.append(imu_record)
            with open(os.path.join(self.simulation_dir, 'imu_data.csv'), 'a') as f:
                writer = csv.writer(f)
                writer.writerow(imu_record)

    def error_callback(self, msg):
        if self.collecting_data:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            error_record = [timestamp, msg.data]
            self.error_data.append(error_record)
            with open(os.path.join(self.simulation_dir, 'error_data.csv'), 'a') as f:
                writer = csv.writer(f)
                writer.writerow(error_record)

    def action_callback(self, msg):
        if self.collecting_data:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            action_record = [timestamp, msg.data]
            with open(os.path.join(self.simulation_dir, 'action_data.csv'), 'a') as f:
                writer = csv.writer(f)
                writer.writerow(action_record)             

    
def main(args=None):
    rclpy.init(args=args)
    data_collector = DataCollector()
    rclpy.spin(data_collector)
    data_collector.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

