# Bases de Datos 2 - Persistencia Políglota

## 👋 Introducción

// todo (acá una breve descripción del trabajo)

Este fue el [Enunciado](docs/Trabajo_obligatorio_2025-1.pdf)

### ❗ Requisitos

- Python3 (La aplicación se probó en la versión de Python 3.11.*)
- pip3
- [pipenv](https://pypi.org/project/pipenv)
- docker y docker-compose (en windows vienen con Docker Desktop)

### 💻 Instalación

En caso de no tener python, descargarlo desde la [página oficial](https://www.python.org/downloads/release/python-3119/)

Utilizando pip (o pip3 en mac/linux) instalar la dependencia de **pipenv**:

```sh
pip install pipenv
```

Parado en la carpeta del proyecto ejecutar:

```sh
pipenv install
```

para instalar las dependencias necesarias en el ambiente virtual.

Vertificar tener docker y docker-compose instalados escribiendo en la terminal:

```sh
docker --version
docker-compose --version
```
// Todo: poner algún comando o algo acá para instalar docker y docker-compose (asumo que el equipo lo tendrá)

Deberían mostrar algo así:
```sh
Docker version 28.0.1, build 068a01e
Docker Compose version v2.33.1-desktop.1
```

## 🏃 Ejecución

Parándose en el root del proyecto correr:
```sh
docker-compose up -d
```
Esto inicializará los contenedores con las bases de datos (En caso de que ya existan, abrirá los contenedores existentes). Se pueden observar dichos contenedores usando:
```sh
docker ps
```

Para detenerlos usar:
```sh
docker-compose stop
```

Y para eliminarlos (esto lógicamente borrará lo que haya en las bases de datos) usar:
```sh
docker-compose down
```

Si deseas acceder a la terminal de MongoDB correr:
```sh
docker exec -it bd2-tp-mongo mongosh
```

Si deseas acceder a la terminal de Cassandra correr:
```sh
docker exec -it bd2-tp-cassandra cqlsh
```

Para el caso de Neo4j acceder a http://localhost:7474 con el usuario `neo4j` y contraseña `password` para correr la terminal y visualizar la información.

Para probar la aplicación, correr:
```shell
pipenv run python main.py
```