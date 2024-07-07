# API Tienda

Este proyecto implementa una API para gestionar una tienda virtual utilizando Flask y SQLAlchemy.

## Características

- Autenticación JWT para diferentes roles de usuario.
- Gestión de usuarios, productos, pedidos y pagos.
- Acceso basado en roles: administrador, cliente, vendedor, bodeguero y contador.

## Requisitos

- Python 3.x
- MySQL

## Instalación

### Clonar el repositorio

git clone https://github.com/paulodelflow/api_tienda.git
cd api_tienda

### Configuración del entorno virtual (opcional)

#### Unix/Linux

virtualenv venv
source venv/bin/activate

#### Windows

virtualenv venv
venv\Scripts\activate

### Instalar dependencias

pip install -r requirements.txt

### Configuración de la base de datos

- Crea una base de datos MySQL llamada `apii`.
- Configura las credenciales de acceso en `app.py`:

  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/apii'

### Inicializar la base de datos

python app.py

Esto creará las tablas necesarias en la base de datos.

## Roles y Funcionalidades

- Administrador
  - Crear Categoría: POST /categorias
  - Crear Producto: POST /productos

- Cliente
  - Ver Catálogo: GET /catalogo
  - Añadir al Carrito: POST /carrito

- Vendedor
  - Ver Productos en Almacén: GET /almacen/productos
  - Administrar Pedidos: PUT /pedidos/administrar/<order_id>

- Bodeguero
  - Ver Pedidos Pendientes: GET /almacen/pedidos
  - Marcar Pedidos como Preparados: PUT /almacen/pedidos/<order_id>

- Contador
  - Confirmar Pagos: PUT /pagos/confirmar/<payment_id>

## Ejemplos de Uso

### Autenticación

curl -X POST -H "Content-Type: application/json" -d '{"username":"tu_usuario","password":"tu_contraseña"}' http://localhost:5000/login

### Crear una Categoría (Administrador)

curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <tu_token_jwt>" -d '{"nombre":"Nueva Categoría"}' http://localhost:5000/categorias

### Crear un Producto (Administrador)

curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <tu_token_jwt>" -d '{"codigo":"1234", "marca":"Marca", "nombre":"Nuevo Producto", "precio":99.99, "stock":100, "categoria_id":1}' http://localhost:5000/productos

Asegúrate de ajustar las URLs y detalles según tu configuración específica. Este README.md proporciona una guía básica para empezar con tu API Tienda.
