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

1. **Clonar el repositorio:**

    ```bash
    git clone https://github.com/paulodelflow/api_tienda.git
    cd api_tienda
    ```

2. **Configurar el entorno virtual (opcional):**

    #### Unix/Linux

    ```bash
    virtualenv venv
    source venv/bin/activate
    ```

    #### Windows

    ```bash
    virtualenv venv
    venv\Scripts\activate
    ```

3. **Instalar las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configurar la base de datos:**

    - Crea una base de datos MySQL llamada `apii`.
    - Configura las credenciales de acceso en `app.py`:

      ```python
      app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/apii'
      ```

5. **Inicializar la base de datos:**

    ```bash
    python app.py
    ```

    Esto creará las tablas necesarias en la base de datos.

## Roles y Funcionalidades

- **Administrador**
  - Crear Categoría: `POST /categorias`
  - Crear Producto: `POST /productos`

- **Cliente**
  - Ver Catálogo: `GET /catalogo`
  - Añadir al Carrito: `POST /carrito`

- **Vendedor**
  - Ver Productos en Almacén: `GET /almacen/productos`
  - Administrar Pedidos: `PUT /pedidos/administrar/<order_id>`

- **Bodeguero**
  - Ver Pedidos Pendientes: `GET /almacen/pedidos`
  - Marcar Pedidos como Preparados: `PUT /almacen/pedidos/<order_id>`

- **Contador**
  - Confirmar Pagos: `PUT /pagos/confirmar/<payment_id>`

## Ejemplos de Uso

### Autenticación

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username":"tu_usuario","password":"tu_contraseña"}' http://localhost:5000/login
