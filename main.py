from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restful import Api, Resource
from datetime import timedelta

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/apii'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'

# Inicialización de extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

# Definición de modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

# Rutas y recursos de la API

# Endpoint para login y obtener token JWT
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            return {'mensaje': 'Credenciales inválidas'}, 401
        
        access_token = create_access_token(identity={'id': user.id, 'username': user.username, 'role': user.role})
        return {'access_token': access_token}, 200


# Vista Cliente
class Catalog(Resource):
    def get(self):
        products = Product.query.all()
        return jsonify([{
            'id': product.id,
            'codigo': product.code,
            'marca': product.brand,
            'nombre': product.name,
            'precio': product.price,
            'stock': product.stock,
            'categoria': product.category.name  # Incluir el nombre de la categoría
        } for product in products])

class ShoppingCart(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        current_user = get_jwt_identity()
        user_id = current_user.get('id')  # Verifica que 'id' esté presente en el payload
        if not user_id:
            return {'mensaje': 'Identidad de usuario no encontrada en el token'}, 400
        
        product = Product.query.get(data['id_producto'])
        if not product or product.stock < data['cantidad']:
            return {'mensaje': 'Producto no disponible o stock insuficiente'}, 400
        
        total_price = product.price * data['cantidad']
        new_order = Order(
            user_id=user_id,
            product_id=data['id_producto'],
            quantity=data['cantidad'],
            total_price=total_price,
            status='pendiente'
        )
        product.stock -= data['cantidad']
        db.session.add(new_order)
        db.session.commit()
        return {'mensaje': 'Orden realizada con éxito.'}, 201

class PaymentResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        current_user = get_jwt_identity()
        user_id = current_user.get('id')  # Verifica que 'id' esté presente en el payload
        if not user_id:
            return {'mensaje': 'Identidad de usuario no encontrada en el token'}, 400

        new_payment = Payment(
            order_id=data['id_pedido'],
            payment_type=data['tipo_pago'],
            confirmed=False
        )
        db.session.add(new_payment)
        db.session.commit()
        return {'mensaje': 'Pago registrado con éxito.'}, 201

# Vista Vendedor
class WarehouseProducts(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        if identity['role'] != 'vendedor':
            return {'mensaje': 'No autorizado'}, 403
        products = Product.query.all()
        return jsonify([{
            'id': product.id,
            'codigo': product.code,
            'marca': product.brand,
            'nombre': product.name,
            'precio': product.price,
            'stock': product.stock,
            'categoria': product.category.name  # Incluir el nombre de la categoría
        } for product in products])

class ManageOrders(Resource):
    @jwt_required()
    def put(self, order_id):
        identity = get_jwt_identity()
        if identity['role'] != 'vendedor':
            return {'mensaje': 'No autorizado'}, 403
        data = request.get_json()
        order = Order.query.get(order_id)
        if not order:
            return {'mensaje': 'Pedido no encontrado'}, 404
        order.status = data['estado']
        db.session.commit()
        return {'mensaje': 'Pedido actualizado con éxito.'}, 200

# Vista Bodeguero
class WarehouseOrders(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        if identity['role'] != 'bodeguero':
            return {'mensaje': 'No autorizado'}, 403
        orders = Order.query.filter_by(status='pendiente').all()
        return jsonify([{
            'id': order.id,
            'id_usuario': order.user_id,
            'id_producto': order.product_id,
            'cantidad': order.quantity,
            'precio_total': order.total_price,
            'estado': order.status
        } for order in orders])

    @jwt_required()
    def put(self, order_id):
        identity = get_jwt_identity()
        if identity['role'] != 'bodeguero':
            return {'mensaje': 'No autorizado'}, 403
        data = request.get_json()
        order = Order.query.get(order_id)
        if not order:
            return {'mensaje': 'Pedido no encontrado'}, 404
        order.status = 'preparado'
        db.session.commit()
        return {'mensaje': 'Pedido preparado con éxito.'}, 200

# Vista Contador
class ConfirmPayments(Resource):
    @jwt_required()
    def put(self, payment_id):
        identity = get_jwt_identity()
        if identity['role'] != 'contador':
            return {'mensaje': 'No autorizado'}, 403
        payment = Payment.query.get(payment_id)
        if not payment:
            return {'mensaje': 'Pago no encontrado'}, 404
        payment.confirmed = True
        db.session.commit()
        return {'mensaje': 'Pago confirmado con éxito.'}, 200

# Vista Administrador para Crear Categoría
class CrearCategoria(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'mensaje': 'Acceso denegado. Solo los administradores pueden crear categorías.'}, 403

        data = request.get_json()
        nueva_categoria = Category(name=data['nombre'])
        db.session.add(nueva_categoria)
        db.session.commit()
        return {'mensaje': 'Categoría creada correctamente.', 'id': nueva_categoria.id}, 201

# Vista Administrador para Crear Producto
class CrearProducto(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'mensaje': 'Acceso denegado. Solo los administradores pueden crear productos.'}, 403

        data = request.get_json()
        category_id = data.get('categoria_id')

        # Verificar si la categoría existe
        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return {'mensaje': 'La categoría especificada no existe'}, 404

        nuevo_producto = Product(
            code=data['codigo'],
            brand=data['marca'],
            name=data['nombre'],
            price=data['precio'],
            stock=data['stock'],
            category_id=category_id
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        return {'mensaje': 'Producto creado correctamente.'}, 201

# Vista para Registrar nuevos Usuarios
class Register(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        # Validar que se proporcionen todos los campos necesarios
        if not username or not password or not role:
            return {'mensaje': 'Faltan campos requeridos'}, 400

        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {'mensaje': 'El usuario ya existe'}, 400

        # Hash del password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Crear nuevo usuario
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return {'mensaje': 'Usuario creado correctamente.'}, 201

# Rutas de la API
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(CrearCategoria, '/categorias')
api.add_resource(CrearProducto, '/productos')
api.add_resource(Catalog, '/catalogo')
api.add_resource(ShoppingCart, '/carrito')
api.add_resource(PaymentResource, '/pagos')
api.add_resource(WarehouseProducts, '/almacen/productos')
api.add_resource(ManageOrders, '/pedidos/administrar/<int:order_id>')
api.add_resource(WarehouseOrders, '/almacen/pedidos')
api.add_resource(ConfirmPayments, '/pagos/confirmar/<int:payment_id>')

# Función para crear las tablas en la base de datos
def create_tables():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True)
