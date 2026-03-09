#!/usr/bin/env python3

# pip install customtkinter

from time import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
import customtkinter as ctk

# Inicializa ROS 2
rclpy.init()
node = Node('manual_controller')

# Publisher para movimento
publisher = node.create_publisher(Twist, '/cmd_vel', 10)

# Clientes de serviço
start_data_client = node.create_client(Empty, 'start_data_collector')
stop_data_client = node.create_client(Empty, 'stop_data_collector')
start_follower_client = node.create_client(Empty, 'start_follower')
stop_follower_client = node.create_client(Empty, 'stop_follower')
status_follower_client = node.create_client(Empty, 'status_follower')
reset_globals_client = node.create_client(Empty, 'reset_globals')
reset_model_poses_client = node.create_client(Empty, 'reset_model_poses')



# Função genérica para chamar serviços
def call_service(client):
    if not client.wait_for_service(timeout_sec=1.0):
        print(f'Serviço {client.srv_name} não disponível.')
        return
    request = Empty.Request()
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    if future.result() is not None:
        print(f'Serviço {client.srv_name} chamado com sucesso.')
    else:
        print(f'Erro ao chamar {client.srv_name}: {future.exception()}')


# Funções de movimento
def move_forward():
    msg = Twist()
    msg.linear.x = 0.2
    msg.angular.z = 0.0
    publisher.publish(msg)

def turn_left():
    msg = Twist()
    msg.linear.x = 0.1
    msg.angular.z = 0.5
    publisher.publish(msg)

def turn_right():
    msg = Twist()
    msg.linear.x = 0.1
    msg.angular.z = -0.5
    publisher.publish(msg)

def stop():
    msg = Twist()
    msg.linear.x = 0.0
    msg.angular.z = 0.0
    publisher.publish(msg)


def reset_model_poses():
    call_service(reset_model_poses_client) 



## faz uma simulação completa ## 
from std_msgs.msg import String 

gravando = False
timer_obj = None
tempo_restante = (60*5)  # segundos

def atualizar_timer():
    global tempo_restante, gravando

    if gravando and tempo_restante > 0:
        minutos = tempo_restante // 60
        segundos = tempo_restante % 60
        timer_label.configure(text=f"Tempo restante: {minutos:02d}:{segundos:02d}")
        tempo_restante -= 1
        app.after(1000, atualizar_timer)  # chama novamente em 1 segundo
    elif gravando and tempo_restante == 0:
        print('[TEMPO] Tempo esgotado. Parando coleta de dados automaticamente.')
        call_service(stop_data_client)
        gravando = False
        timer_label.configure(text="Tempo encerrado.")

def status_callback(msg):
    global gravando

    if msg.data == 'start_follower initiated':
        print('eu escutei o start follower')

    elif msg.data == 'stop_follower initiated':
        print('eu escutei o stop follower')
        if gravando:
            print('[AÇÃO] Parando coleta de dados...')
            call_service(stop_data_client)
            gravando = False
            timer_label.configure(text="Coleta encerrada.")

def iniciar_e_gravar():
    global gravando, tempo_restante
    gravando = True

    print('[DEBUG] Função iniciar_e_gravar foi chamada.')
    call_service(start_data_client)
    call_service(start_follower_client)
    atualizar_timer()


node.create_subscription(String, 'status_message', status_callback, 10) 


def salvar_dados_erro():
    # Implementar a lógica para salvar os dados de erro
    print("Salvar dados de erro - função não implementada ainda.")  

# Interface gráfica
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Controle Manual do Robô")
app.geometry("400x600")

label = ctk.CTkLabel(app, text="Movimento", font=("Arial", 20))
label.pack(pady=10)

ctk.CTkButton(app, text="Frente", command=move_forward).pack(pady=5)
ctk.CTkButton(app, text="Esquerda", command=turn_left).pack(pady=5)
ctk.CTkButton(app, text="Direita", command=turn_right).pack(pady=5)
ctk.CTkButton(app, text="Parar", command=stop).pack(pady=5)
ctk.CTkButton(app, text="Resetar Posições dos Modelos", command=reset_model_poses).pack(pady=5)


label2 = ctk.CTkLabel(app, text="Serviços ROS", font=("Arial", 20))
label2.pack(pady=20)

ctk.CTkButton(app, text="Iniciar Coleta de Dados", command=lambda: call_service(start_data_client)).pack(pady=5)
ctk.CTkButton(app, text="Parar Coleta de Dados", command=lambda: call_service(stop_data_client)).pack(pady=5)
ctk.CTkButton(app, text="Iniciar Seguidor", command=lambda: call_service(start_follower_client)).pack(pady=5)
ctk.CTkButton(app, text="Parar Seguidor", command=lambda: call_service(stop_follower_client)).pack(pady=5)
ctk.CTkButton(app, text="Status do Seguidor", command=lambda: call_service(status_follower_client)).pack(pady=5)
#ctk.CTkButton(app, text="Resetar Variáveis", command=lambda: call_service(reset_globals_client)).pack(pady=5)
ctk.CTkButton(app, text="Iniciar e gravar", command=iniciar_e_gravar).pack(pady=5)



timer_label = ctk.CTkLabel(app, text="Tempo restante: --:--", font=("Arial", 16))
timer_label.pack(pady=10)


app.mainloop()

# Finaliza ROS 2 ao fechar a janela
node.destroy_node()
rclpy.shutdown()
