import socket
import threading
import time
import hashlib
import os
import json
from datetime import datetime

class RC4Simulado:
    def __init__(self, clave):
        self.clave = self._preparar_clave(clave)
    
    def _preparar_clave(self, clave):
        return hashlib.md5(clave.encode()).digest()
    
    def cifrar_descifrar(self, texto):
        resultado = []
        clave_extendida = self.clave * (len(texto) // len(self.clave) + 1)
        
        for i, char in enumerate(texto):
            resultado_char = chr(ord(char) ^ clave_extendida[i % len(self.clave)])
            resultado.append(resultado_char)
        
        return ''.join(resultado)

class ServidorChat:
    def __init__(self, host='0.0.0.0', puerto=8080):
        self.host = host
        self.puerto = puerto
        self.clientes = {}  # {usuario: {'conexion': conexion, 'rc4': rc4}}
        self.clave_secreta = "clave_secreta_globalfinance_2024"
        
        # Crear directorio de logs
        os.makedirs('logs', exist_ok=True)
        
    def log_evento(self, mensaje):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {mensaje}\n"
        print(log_entry, end='')
        
        # Escribir en archivo de log
        with open('logs/servidor.log', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def broadcast(self, mensaje, usuario_origen=None):
        """Enviar mensaje a todos los clientes conectados"""
        usuarios_desconectados = []
        
        for usuario, datos in self.clientes.items():
            try:
                if usuario != usuario_origen:  # No enviar al remitente
                    mensaje_cifrado = datos['rc4'].cifrar_descifrar(mensaje)
                    datos['conexion'].send(mensaje_cifrado.encode())
            except:
                usuarios_desconectados.append(usuario)
        
        # Limpiar clientes desconectados
        for usuario in usuarios_desconectados:
            if usuario in self.clientes:
                del self.clientes[usuario]
                self.log_evento(f"Usuario {usuario} desconectado")
    
    def enviar_mensaje_privado(self, destino, mensaje, usuario_origen):
        """Enviar mensaje a un cliente específico"""
        if destino in self.clientes:
            try:
                mensaje_completo = f"[PRIVADO de {usuario_origen}] {mensaje}"
                mensaje_cifrado = self.clientes[destino]['rc4'].cifrar_descifrar(mensaje_completo)
                self.clientes[destino]['conexion'].send(mensaje_cifrado.encode())
                return True
            except Exception as e:
                self.log_evento(f"Error enviando mensaje privado: {e}")
                return False
        return False
    
    def manejar_cliente(self, conexion, direccion):
        cliente_ip = direccion[0]
        usuario = None
        
        try:
            # Autenticación
            conexion.send("Usuario: ".encode())
            usuario = conexion.recv(1024).decode().strip()
            conexion.send("Contraseña: ".encode())
            password = conexion.recv(1024).decode().strip()
            
            if self.verificar_credenciales(usuario, password):
                conexion.send("OK:Autenticación exitosa\n".encode())
                
                # Inicializar RC4 para este cliente
                rc4 = RC4Simulado(self.clave_secreta)
                self.clientes[usuario] = {'conexion': conexion, 'rc4': rc4}
                
                self.log_evento(f"Usuario {usuario} autenticado desde {cliente_ip}")
                self.log_evento(f"Clientes conectados: {list(self.clientes.keys())}")
                
                # Notificar a todos los clientes
                mensaje_bienvenida = f"{usuario} se ha unido al chat"
                self.broadcast(mensaje_bienvenida)
                
                # Enviar instrucciones al cliente
                instrucciones = "\n Chat seguro activo. Comandos:\n- @usuario mensaje → Mensaje privado\n- listar → Ver usuarios conectados\n- salir → Salir del chat\n"
                conexion.send(rc4.cifrar_descifrar(instrucciones).encode())
                
            else:
                conexion.send("ERROR:Credenciales inválidas\n".encode())
                conexion.close()
                return
            
            # Loop principal de mensajes
            while True:
                mensaje_cifrado = conexion.recv(1024).decode('utf-8', errors='ignore')
                if not mensaje_cifrado:
                    break
                
                mensaje_claro = rc4.cifrar_descifrar(mensaje_cifrado)
                self.log_evento(f"[{usuario}] → {mensaje_claro}")
                
                # Procesar comandos especiales
                if mensaje_claro.lower() == 'salir':
                    break
                elif mensaje_claro.lower() == 'listar':
                    usuarios_conectados = ", ".join(self.clientes.keys())
                    respuesta = f"👥 Usuarios conectados: {usuarios_conectados}"
                    conexion.send(rc4.cifrar_descifrar(respuesta).encode())
                elif mensaje_claro.startswith('@'):
                    # Mensaje privado: @usuario mensaje
                    partes = mensaje_claro.split(' ', 1)
                    if len(partes) == 2:
                        destino = partes[0][1:]  # Quitar el @
                        mensaje_privado = partes[1]
                        
                        if self.enviar_mensaje_privado(destino, mensaje_privado, usuario):
                            confirmacion = f"Mensaje enviado a {destino}"
                            conexion.send(rc4.cifrar_descifrar(confirmacion).encode())
                        else:
                            error_msg = f"Usuario {destino} no encontrado o desconectado"
                            conexion.send(rc4.cifrar_descifrar(error_msg).encode())
                else:
                    # Mensaje broadcast
                    mensaje_publico = f"[{usuario}]: {mensaje_claro}"
                    self.broadcast(mensaje_publico, usuario_origen=usuario)
                
        except Exception as e:
            self.log_evento(f"Error con {cliente_ip}: {e}")
        finally:
            if usuario and usuario in self.clientes:
                del self.clientes[usuario]
                mensaje_desconexion = f"{usuario} ha abandonado el chat"
                self.broadcast(mensaje_desconexion)
                self.log_evento(f"Usuario {usuario} desconectado")
            conexion.close()
    
    def verificar_credenciales(self, usuario, password):
        credenciales_validas = {
            "gerente": "clave_gerente123",
            "subgerente1": "clave_subgerente1", 
            "subgerente2": "clave_subgerente2"
        }
        return credenciales_validas.get(usuario) == password
    
    def iniciar(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((self.host, self.puerto))
        servidor.listen(5)
        
        self.log_evento(f"Servidor iniciado en {self.host}:{self.puerto}")
        self.log_evento("Esperando conexiones...")
        
        try:
            while True:
                conexion, direccion = servidor.accept()
                hilo = threading.Thread(target=self.manejar_cliente, args=(conexion, direccion))
                hilo.daemon = True
                hilo.start()
        except KeyboardInterrupt:
            self.log_evento("Servidor detenido por el usuario")
        finally:
            servidor.close()

if __name__ == "__main__":
    servidor = ServidorChat()
    servidor.iniciar()