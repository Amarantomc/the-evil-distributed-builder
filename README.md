# the-evil-distributed-builder

A Distributed System to Build and Test projects

## Pasos para runear y testear esta versión

* **Construir la imagen de Docker**

```bash
docker build -t evil-builder:latest .
```

* **Levantar Primero el Container Head de Ray**

```bash  
docker run -d --name ray-head --network ci-net --shm-size=1g -p 8265:8265 -e NODE_NAME=ray-head evil-builder:latest ray start --head --port=6379 --ray-client-server-port=10001  --dashboard-host=0.0.0.0 --num-cpus=0 --block
```

* **Levantar los Worker cambiando el id**

```bash

docker run -d --name ray-worker-1 --network ci-net --shm-size=1g --cpus=2 --memory=2g -e NODE_NAME=ray-worker-1 evil-builder:latest ray start --address=ray-head:6379 --num-cpus=2 --block   
```

* **Levantar el Gateway**

```bash
docker run -d --name ci-gateway --network ci-net --shm-size=1g   -e NODE_NAME=ci-gateway -e RAY_ADDRESS=ray://ray-head:10001  evil-builder:latest bash -lc "tail -f /dev/null"      
```

### Pruebas Simples del Sistema

#### Comprobar si levantó correctamente todos los nodos

```bash
docker exec -it ci-gateway python -m gateway.cli ping    
```

#### Ejecutar una Tarea Simple

```bash
docker exec -it ci-gateway python -m gateway.cli submit "echo hola" --timeout 30 --wait 
```
