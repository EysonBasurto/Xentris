from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:098078@localhost/facturacion'
db = SQLAlchemy(app)
app.secret_key = 'sexo'

class ControlExistencias:
    # Simula el control de existencias
    def existe_cliente(self, documento):
        return documento == "123456"

ctrl = ControlExistencias()

@app.route('/')
def index():
    return render_template('index.html')
class TipoDocumento(db.Model):
    __tablename__ = 'tipo_de_documento'
    id_tipo_documento = db.Column(db.Integer, primary_key=True)
    Descripcion = db.Column(db.String(10), nullable=False)
class Cliente(db.Model):
    Documento = db.Column(db.String(15), primary_key=True)
    cod_tipo_documento = db.Column(db.Integer, db.ForeignKey('tipo_de_documento.id_tipo_documento'), nullable=False)
    Nombres = db.Column(db.String(30), nullable=False)
    Apellidos = db.Column(db.String(30), nullable=False)
    Direccion = db.Column(db.String(20))
    cod_ciudad = db.Column(db.Integer, db.ForeignKey('ciudad.Codigo_ciudad'), nullable=False)
    Telefono = db.Column(db.String(20))
    Telefono = db.Column(db.String(20))
    ciudad = db.relationship('Ciudad', backref='cliente', lazy=True)
    tipo_documento = db.relationship('TipoDocumento', foreign_keys=[cod_tipo_documento], backref='cliente')
@app.route('/registrar_clientes', methods=['GET', 'POST'])
def registrar_clientes():
    mensaje = ""

    if request.method == 'POST':
        doccliente = request.form['doccliente']
        combo_tipo = request.form['combo_tipo']
        nomcliente = request.form['nomcliente']
        apellcliente = request.form['apellcliente']
        dircliente = request.form['dircliente']
        ciudad_combo = request.form['ciudad_combo']
        telefonocliente = request.form['telefonocliente']

        nuevo_cliente = Cliente(Documento=doccliente, cod_tipo_documento=combo_tipo,
                                Nombres=nomcliente, Apellidos=apellcliente,
                                Direccion=dircliente, cod_ciudad=ciudad_combo,
                                Telefono=telefonocliente)

        try:
            db.session.add(nuevo_cliente)
            db.session.commit()
            mensaje = "Cliente registrado exitosamente."
        except:
            db.session.rollback()
            mensaje = "Error al registrar el cliente."

    return render_template('registrar_clientes.html', mensaje=mensaje)
class Ciudad(db.Model):
    Codigo_ciudad = db.Column(db.Integer, primary_key=True)
    Nombre_ciudad = db.Column(db.String(30), nullable=False)

    
@app.route('/buscar_clientes', methods=['GET', 'POST'])
def buscar_clientes():
    documento_buscar = request.form.get('documento_buscar')
    if documento_buscar:
        clientes = Cliente.query.filter_by(Documento=documento_buscar).all()
    else:
        clientes = Cliente.query.all()

    ciudades = Ciudad.query.all()

    return render_template('buscar_clientes.html', clientes=clientes, ciudades=ciudades)
@app.route('/articulos')
def articulos():
    return render_template('articulos.html')

class TipoArticulo(db.Model):
    cod_tipo_articulo = db.Column(db.String(30), primary_key=True)
    descripcion_articulo = db.Column(db.String(30), nullable=False)
class Articulo(db.Model):
    __tablename__ = 'articulo'
    id_articulo = db.Column(db.String(30), primary_key=True)  # Cambia el tipo de columna según tus necesidades
    descripcion = db.Column(db.String(30), nullable=False)
    precio_venta = db.Column(db.Integer, nullable=False)
    precio_costo = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    cod_tipo_articulo = db.Column(db.String(30), nullable=True)  # Cambia a nullable=True
    fecha_ingreso = db.Column(db.String(15), nullable=False)
@app.route('/agregar_articulo', methods=['GET', 'POST'])
def agregar_articulo():
    if request.method == 'POST':
        id_articulo = request.form['id_articulo']
        descripcion = request.form['descripcion']
        precio_venta = int(request.form['precio_venta'])
        precio_costo = int(request.form['precio_costo'])
        stock = int(request.form['stock'])
        fecha_ingreso = request.form['fecha_ingreso']

        try:
            nuevo_articulo = Articulo(
                id_articulo=id_articulo,
                descripcion=descripcion,
                precio_venta=precio_venta,
                precio_costo=precio_costo,
                stock=stock,
                fecha_ingreso=fecha_ingreso
            )
            db.session.add(nuevo_articulo)
            db.session.commit()
            return render_template('agregar_articulo.html', success=True)
        except Exception as e:
            return f"Error: {e}"

    return render_template('agregar_articulo.html')
@app.route('/consultar_articulos')
def consultar_articulos():
    try:
        # Consulta todos los artículos
        articulos = Articulo.query.all()

        # Renderiza la plantilla y pasa los datos de los artículos
        return render_template('consultar_articulos.html', articulos=articulos)
    except Exception as e:
        print(f"Error: {e}")
@app.route('/actualizar_stock', methods=['GET', 'POST'])
def actualizar_stock():
    articulos = Articulo.query.all()

    if request.method == 'POST':
        id_articulo = request.form['id_articulo']
        nuevo_stock = int(request.form['nuevo_stock'])

        articulo = Articulo.query.get(id_articulo)
        if articulo:
            articulo.stock = nuevo_stock
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('actualizar_stock.html', articulos=articulos)
class Factura(db.Model):
    Nnm_factura = db.Column(db.String(20), primary_key=True)
    cod_cliente = db.Column(db.String(15), db.ForeignKey('cliente.Documento'), nullable=False)
    Nombre_empleado = db.Column(db.String(30), nullable=False)
    Fecha_facturacion = db.Column(db.String(15), nullable=False)
    cod_formapago = db.Column(db.Integer, nullable=False)
    total_factura = db.Column(db.Float)
    IVA = db.Column(db.Float)
    detalle_factura = db.relationship('DetalleFactura', backref='factura', lazy=True)

class FormaPago(db.Model):
    __tablename__ = 'forma_de_pago'
    
    id_formapago = db.Column(db.Integer, primary_key=True)
    Descripcion_formapago = db.Column(db.String(20), nullable=False)
 

class DetalleFactura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cod_factura = db.Column(db.String(20), db.ForeignKey('factura.Nnm_factura'), nullable=False)
    cod_articulo = db.Column(db.Integer, db.ForeignKey('articulo.id_articulo'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

@app.route('/doc_cliente', methods=['GET', 'POST'])
def doc_cliente():
    if request.method == 'POST':
        documento = request.form.get('doccliente')
        cliente = Cliente.query.filter_by(Documento=documento).first()
        if cliente:
            session['cod_cliente'] = cliente.Documento  # Almacena el código del cliente en la sesión
            return redirect(url_for('registrar_factura'))
        else:
            flash('Cliente no encontrado', 'error')
    return render_template('doc_cliente.html')
def GenerarNumeroFactura():
    codigo = "FACT-"
    for _ in range(6):
        num = str(random.randint(6, 10))
        codigo += num
    return codigo
@app.route('/registrar_factura', methods=['GET', 'POST'])
def registrar_factura():
    if request.method == 'POST':
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        Nnm_factura = f'FACT-{timestamp}'
        
        cod_cliente = session.get('cod_cliente')
        Nombre_empleado = request.form.get('Nombre_empleado')
        Fecha_facturacion = request.form.get('Fecha_facturacion')
        cod_formapago = request.form.get('cod_formapago')
        detalle_factura_ids = request.form.getlist('detalle_factura')
        
        factura = Factura(Nnm_factura=Nnm_factura, cod_cliente=cod_cliente, Nombre_empleado=Nombre_empleado,
                          Fecha_facturacion=Fecha_facturacion, cod_formapago=cod_formapago)
        
        total_factura = 0
        
        detalles_factura = []
        for articulo_id in detalle_factura_ids:
            articulo = Articulo.query.get(articulo_id)
            if articulo:
                detalles_factura.append(articulo)
                total_factura += int(articulo.precio_venta)
            else:
                flash(f'El artículo con ID {articulo_id} no fue encontrado', 'error')
                return redirect(url_for('registrar_factura'))
        
        iva = total_factura * 0.12
        total_factura += iva
        
        factura.total_factura = total_factura
        factura.IVA = iva
        
        db.session.add(factura)
        db.session.commit()
        
        flash('Factura registrada exitosamente', 'success')
        return redirect(url_for('index'))
    
    clientes = Cliente.query.all()
    formapagos = FormaPago.query.all()
    articulos = Articulo.query.all()
    return render_template('registrar_factura.html', clientes=clientes, formas_pago=formapagos, articulos=articulos)
@app.route('/registrar_detalle_factura', methods=['POST'])
def registrar_detalle_factura():
    Nnm_factura = request.form.get('Nnm_factura')
    detalle_factura = request.form.getlist('detalle_factura')
    
    total_factura = 0
    for detalle in detalle_factura:
        articulo_id, cantidad = detalle.split('-')
        articulo = Articulo.query.get(articulo_id)
        subtotal = float(articulo.precio_venta) * int(cantidad)
        total_factura += subtotal
        detalle = DetalleFactura(cod_factura=Nnm_factura, cod_articulo=articulo_id, cantidad=cantidad, total=subtotal)
        db.session.add(detalle)
    
    iva = total_factura * 0.12
    factura = Factura.query.get(Nnm_factura)
    factura.total_factura = total_factura + iva
    factura.IVA = iva
    
    db.session.commit()
    
    flash('Detalle de factura registrado exitosamente', 'success')
    return redirect(url_for('registrar_factura', cliente_documento=factura.cod_cliente))

if __name__ == '__main__':
    app.run(port=3000, debug=True)