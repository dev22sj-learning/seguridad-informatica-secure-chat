
# Comandos para Ejecutar con Docker

```bash
# 1. Reconstruir y ejecutar
docker-compose down
docker-compose up --build -d

# 2. Ver logs del servidor 
docker-compose logs -f servidor

# 3. En terminales separadas, conectar clientes:

# Terminal 1 - Cliente Gerente
docker exec -it chat-cliente-gerente python cliente.py
# Usuario: gerente
# Contraseña: clave_gerente123

# Terminal 2 - Cliente Subgerente1  
docker exec -it chat-cliente-subgerente python cliente.py
# Usuario: subgerente1
# Contraseña: clave_subgerente1

# Terminal 3 - Cliente Subgerente2
docker exec -it chat-cliente-subgerente python cliente.py
# Usuario: subgerente2
# Contraseña: clave_subgerente2
```