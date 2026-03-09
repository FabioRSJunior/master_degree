import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
from std_msgs.msg import String
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

class SimulationNode(Node):
    def __init__(self):
        super().__init__('simulation_node')
        
        self.callback_group = ReentrantCallbackGroup()
        
        # Cria o serviço start_simulation
        self.start_service = self.create_service(Empty, 'start_simulation', self.start_simulation_callback, callback_group=self.callback_group)
        
        # Assinar o tópico 'status_message' para monitorar quando o stop_follower for iniciado
        self.status_subscription = self.create_subscription(String, 'status_message', self.status_callback, 10)
        
        self.should_move = True
        self.finalization_countdown = None

    def start_simulation_callback(self, request, response):
        self.get_logger().info('Serviço start_simulation chamado.')

        # Chama o serviço reset_simulation
        self.call_reset_simulation()

        # Chama o serviço start_follower
        self.call_start_follower()

        # Chama o serviço start_data_collector
        self.call_start_data_collector()

        return response

    def call_reset_simulation(self):
        self.get_logger().info('Chamando o serviço reset_simulation...')
        cli = self.create_client(Empty, 'reset_simulation')
        while not cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Serviço reset_simulation não disponível, tentando novamente...')
        req = Empty.Request()
        future = cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info('reset_simulation executado com sucesso')
        else:
            self.get_logger().error('Falha ao chamar reset_simulation')

    def call_start_follower(self):
        self.get_logger().info('Chamando o serviço start_follower...')
        cli = self.create_client(Empty, 'start_follower')
        while not cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Serviço start_follower não disponível, tentando novamente...')
        req = Empty.Request()
        future = cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info('start_follower executado com sucesso')
        else:
            self.get_logger().error('Falha ao chamar start_follower')

    def call_start_data_collector(self):
        self.get_logger().info('Chamando o serviço start_data_collector...')
        cli = self.create_client(Empty, 'start_data_collector')
        while not cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Serviço start_data_collector não disponível, tentando novamente...')
        req = Empty.Request()
        future = cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info('start_data_collector executado com sucesso')
        else:
            self.get_logger().error('Falha ao chamar start_data_collector')

    def call_stop_data_collector(self):
        self.get_logger().info('Chamando o serviço stop_data_collector...')
        cli = self.create_client(Empty, 'stop_data_collector')
        while not cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Serviço stop_data_collector não disponível, tentando novamente...')
        req = Empty.Request()
        future = cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info('stop_data_collector executado com sucesso')
        else:
            self.get_logger().error('Falha ao chamar stop_data_collector')

    def status_callback(self, msg):
        print("status_callback rodando .... DEBUG")
        if msg.data == "stop_follower initiated":
            self.get_logger().info("stop_follower detected. Stopping data collector...")
            self.call_stop_data_collector()

def main(args=None):
    rclpy.init(args=args)
    node = SimulationNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
