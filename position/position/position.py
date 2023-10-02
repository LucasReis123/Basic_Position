import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import numpy as np
import matplotlib.pyplot as plt
import time


class Position(Node):
    def __init__(self):
        super().__init__('Position')
        self.get_logger().info('Position node initialized.')
        self.tempo_inicio = time.time()
        self.time_1 = self.create_timer(0.1, self.Position)
        self.create_subscription(Twist, '/cmd_vel', self.callback_cmd_vel, 10)
        
        self.msg = Twist() #       CRIA UM OBJETO DO TIPO TWIST QUE CONTERÁ AS 
        self.msg.angular.z = 0.0 # INFORMAÇÕES DAS MENSAGENS ANTERIORES QUE 
        self.msg.linear.x = 0.0 #  INICIALMENTE SÃO SETADAS PARA 0
        self.buffer = []
        self.time_1 = self.create_timer(0.1, self.Odometry) # FUNÇÃO PARA
        # DESCARREGAR O BUFFER

        self.position = np.array([[0.0], [0.0], [0.0]]) # VETOR DE ESTADO
        self.index = 0

        self.X_axis = []
        self.Y_axis = []
        self.Angle = []

    def Odometry(self):
        if len(self.buffer) == 0:
            return
        
        # Descarrega o buffer
        
        aux = self.buffer[0] # PEGA O PRIMEIRO ELEMENTO DO BUUFER
        dt = aux[0] # PEGA O TEMPO
        linear_vel = aux[1].linear.x # PEGA A VELOCIDADE LINEAR
        angular_vel = aux[1].angular.z # PEGA A VELOCIDADE ANULAR
        theta = self.position[2][0] # PEGA A ORIENTAÇÃO ANTERIOR
        self.buffer.pop(0) # APAGA O PRIMEIRO ELEMTNO DO BUFFER

        Tranf_line = np.array([[np.cos(theta), 0], [np.sin(theta), 0], [0, 1]])
        # MATRIZ DE TRANSFORMAÇÃO LINEAR 

        vel = np.array([[linear_vel], [angular_vel]]) # MATRIZ CONTENDO AS VELOCIDADES

        # CALCULA O "TAMANHO" DO NOVO PASSO
        passo = Tranf_line @ vel

        self.X_axis.append(self.position[0][0])
        self.Y_axis.append(self.position[1][0])
        self.Angle.append(self.position[2][0])
        
        print(self.position)

        self.position += (passo * dt) # CALCULA A NOVA POSIÇÃO

        self.index += 1 # VARIAVEL PARA DEFINIR O NUMERO DE PASSOS QUE SERÁ PLOTADO
        #print(self.index)

        if self.index == 150:
            self.Plot()

    def Plot(self):
        # ESSA FUNÇÃO PLOTA UM GRAFICO CONTENDO OS PASSOS REALIZADOS
        vector_lengths = 0.2
        x_components = vector_lengths * np.cos(self.Angle)
        y_components = vector_lengths * np.sin(self.Angle)

        plt.quiver(self.X_axis, self.Y_axis, x_components, y_components)
        #plt.xlim(-5, 5)
        #plt.ylim(-5, 5)
        plt.xlabel('Eixo X')
        plt.ylabel('Eixo Y')
        plt.title('Campo Vetorial')
        plt.savefig('Position.pdf')
        #plt.show()


            

    def Position(self):
        """
            ESSA FUNÇÃO É RESPONSÁVEL POR CARREGAR O BUFFER QUE FARÁ A ODOMETRIA
            GUARDANDO NELE OS ELESMENTOS:

            PRIMEIRO ELEMENTO (dt): INTERVALO DE TEMPO
            
            SEGUNDO ELEMENTO (self.msg): CONTEM A INFORMAÇÃO DO ULTIMO TWIST
            REGISTRADO  

        """
        tempo_final = time.time()
        dt = tempo_final - self.tempo_inicio
        self.tempo_inicio = time.time()

        aux = []
        aux.append(dt)
        aux.append(self.msg)
        self.buffer.append(aux)

    def callback_cmd_vel(self, msg):
        self.msg = msg
        self.Position()
    

def main(args=None):
    rclpy.init(args=args)
    position = Position()
    rclpy.spin(position)
    position.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()