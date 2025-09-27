import socket
import sys
import hashlib
import os
import threading

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

class ClienteChat:
    def __init__(self, clave_secreta):
        self.rc4 = RC4Simulado(clave_secreta)
        self.conectado = False
        self.socket = None
    
    def escuchar_mensajes(self):
        """Hilo para recibir mensajes del servidor"""
        while self.conectado:
            try:
                mensaje_cifrado = self.socket.recv(1024).decode('utf-8', errors='ignore')
                if mensaje_cifrado:
                    mensaje_claro = self.rc4.cifrar_descifrar(mensaje_cifrado)
                    print(f"\n {mensaje_claro}\nTú: ", end='', flush=True)
            except:
                if self.conectado:
                    print("\n Conexión perdida con el servidor")
                    self.conectado = False
                break
    
    def conectar(self, host='servidor', puerto=8080):
        try:
            print(f"Conectando a {host}:{puerto}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(60)
            self.socket.connect((host, puerto))
            self.conectado = True
            
            # Autenticación
            usuario_input = self.socket.recv(1024).decode()
            usuario = input(usuario_input)
            self.socket.send(usuario.encode())
            
            password_input = self.socket.recv(1024).decode()
            password = input(password_input)
            self.socket.send(password.encode())
            
            respuesta = self.socket.recv(1024).decode()
            if respuesta.startswith("OK:"):
                print("" + respuesta[3:])
                
                # Iniciar hilo para escuchar mensajes
                hilo_escucha = threading.Thread(target=self.escuchar_mensajes)
                hilo_escucha.daemon = True
                hilo_escucha.start()
                
                return True
            else:
                print("" + respuesta[6:])
                return False
                
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def iniciar_chat(self):
        print("\n Chat seguro iniciado. Escribe 'salir' para terminar.")
        print("Todos los mensajes están cifrados con RC4")
        print("Usa '@usuario mensaje' para mensajes privados\n")
        
        while self.conectado:
            try:
                mensaje = input("Tú: ")
                if not self.conectado:
                    break
                    
                if mensaje.lower() == 'salir':
                    # Enviar comando de salida al servidor
                    mensaje_cifrado = self.rc4.cifrar_descifrar(mensaje)
                    self.socket.send(mensaje_cifrado.encode())
                    break
                
                # Cifrar y enviar
                mensaje_cifrado = self.rc4.cifrar_descifrar(mensaje)
                self.socket.send(mensaje_cifrado.encode())
                
            except KeyboardInterrupt:
                print("\n Sesión terminada")
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        
        self.conectado = False
        if self.socket:
            self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "servidor":
        from servidor import ServidorChat
        servidor = ServidorChat()
        servidor.iniciar()
    else:
        cliente = ClienteChat("clave_secreta_globalfinance_2024")
        
        # Determinar host basado en entorno
        host = 'servidor' if os.path.exists('/.dockerenv') else 'localhost'
        
        if cliente.conectar(host=host):
            cliente.iniciar_chat()