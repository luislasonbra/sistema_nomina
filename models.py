"""
models.py
Definición de todas las tablas del Sistema de Nómina RD
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id            = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    reset_token   = db.Column(db.String(120))
    reset_expira  = db.Column(db.DateTime)
    activo        = db.Column(db.String(3), default="si")
    creado_en     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_safe_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "activo": self.activo,
        }


# ─────────────────────────────────────────
#  DEPARTAMENTO
# ─────────────────────────────────────────
class Departamento(db.Model):
    __tablename__ = "departamentos"

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(100), nullable=False, unique=True)
    codigo      = db.Column(db.String(10),  nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    creado_en   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    cargos    = db.relationship("Cargo",    backref="departamento", lazy=True, cascade="all, delete-orphan")
    empleados = db.relationship("Empleado", backref="departamento", lazy=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "codigo":      self.codigo,
            "descripcion": self.descripcion or "",
            "creado_en":   self.creado_en.isoformat() if self.creado_en else None,
        }


# ─────────────────────────────────────────
#  CARGO
# ─────────────────────────────────────────
class Cargo(db.Model):
    __tablename__ = "cargos"

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(100), nullable=False)
    dept_id     = db.Column(db.Integer, db.ForeignKey("departamentos.id"), nullable=False)
    nivel       = db.Column(db.String(30), default="operativo")   # operativo|tecnico|supervisorio|gerencial|directivo
    sal_base    = db.Column(db.Numeric(12, 2), default=0)
    sal_max     = db.Column(db.Numeric(12, 2), default=0)
    creado_en   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    empleados = db.relationship("Empleado", backref="cargo", lazy=True)

    def to_dict(self):
        return {
            "id":       self.id,
            "nombre":   self.nombre,
            "dept_id":  self.dept_id,
            "nivel":    self.nivel,
            "sal_base": float(self.sal_base or 0),
            "sal_max":  float(self.sal_max  or 0),
        }


# ─────────────────────────────────────────
#  EMPLEADO
# ─────────────────────────────────────────
class Empleado(db.Model):
    __tablename__ = "empleados"

    id         = db.Column(db.Integer, primary_key=True)
    nombres    = db.Column(db.String(80),  nullable=False)
    apellidos  = db.Column(db.String(80),  nullable=False)
    cedula     = db.Column(db.String(20),  nullable=False, unique=True)
    telefono   = db.Column(db.String(20))
    email      = db.Column(db.String(120))
    direccion  = db.Column(db.String(255))
    ingreso    = db.Column(db.Date,        nullable=False)
    dept_id    = db.Column(db.Integer, db.ForeignKey("departamentos.id"), nullable=False)
    cargo_id   = db.Column(db.Integer, db.ForeignKey("cargos.id"),        nullable=False)
    tipo       = db.Column(db.String(20),  default="fijo")   # fijo|por_hora|temporal
    salario    = db.Column(db.Numeric(12, 2), nullable=False)
    estado     = db.Column(db.String(20),  default="activo") # activo|inactivo|suspendido
    creado_en  = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    descuentos      = db.relationship("DescuentoEmpleado", backref="empleado", lazy=True, cascade="all, delete-orphan")
    nominas_detalle = db.relationship("NominaDetalle",     backref="empleado", lazy=True)

    def to_dict(self):
        return {
            "id":        self.id,
            "nombres":   self.nombres,
            "apellidos": self.apellidos,
            "cedula":    self.cedula,
            "telefono":  self.telefono or "",
            "email":     self.email    or "",
            "direccion": self.direccion or "",
            "ingreso":   self.ingreso.isoformat() if self.ingreso else None,
            "dept_id":   self.dept_id,
            "cargo_id":  self.cargo_id,
            "tipo":      self.tipo,
            "salario":   float(self.salario or 0),
            "estado":    self.estado,
        }


# ─────────────────────────────────────────
#  TIPO DE DEDUCCIÓN  (catálogo global)
# ─────────────────────────────────────────
class TipoDeduccion(db.Model):
    __tablename__ = "tipos_deduccion"

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(100), nullable=False, unique=True)
    tipo        = db.Column(db.String(20),  default="porcentaje")  # porcentaje|fijo
    valor       = db.Column(db.Numeric(10, 4), default=0)          # % o monto referencia
    aplica      = db.Column(db.String(20),  default="todos")       # todos|fijo|por_hora
    obligatoria = db.Column(db.String(3),   default="no")          # si|no
    creado_en   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    descuentos = db.relationship("DescuentoEmpleado", backref="tipo_deduccion", lazy=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "tipo":        self.tipo,
            "valor":       float(self.valor or 0),
            "aplica":      self.aplica,
            "obligatoria": self.obligatoria,
        }


# ─────────────────────────────────────────
#  DESCUENTO POR EMPLEADO  (asignación individual)
# ─────────────────────────────────────────
class DescuentoEmpleado(db.Model):
    __tablename__ = "descuentos_empleado"

    id         = db.Column(db.Integer, primary_key=True)
    emp_id     = db.Column(db.Integer, db.ForeignKey("empleados.id"),        nullable=False)
    tipo_id    = db.Column(db.Integer, db.ForeignKey("tipos_deduccion.id"),   nullable=True)   # puede ser personalizado
    nombre     = db.Column(db.String(120), nullable=False)  # descripción/concepto
    tipo_val   = db.Column(db.String(20),  default="fijo")  # fijo|porcentaje
    valor      = db.Column(db.Numeric(12, 4), nullable=False)
    inicio     = db.Column(db.Date)
    fin        = db.Column(db.Date)
    cuotas     = db.Column(db.Integer, default=0)           # 0 = indefinido
    activo     = db.Column(db.String(3), default="si")      # si|no
    obs        = db.Column(db.String(255))
    creado_en  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":       self.id,
            "emp_id":   self.emp_id,
            "tipo_id":  self.tipo_id,
            "nombre":   self.nombre,
            "tipo_val": self.tipo_val,
            "valor":    float(self.valor or 0),
            "inicio":   self.inicio.isoformat() if self.inicio else None,
            "fin":      self.fin.isoformat()    if self.fin    else None,
            "cuotas":   self.cuotas or 0,
            "activo":   self.activo,
            "obs":      self.obs or "",
        }


# ─────────────────────────────────────────
#  PERÍODO DE NÓMINA
# ─────────────────────────────────────────
class Periodo(db.Model):
    __tablename__ = "periodos"

    id        = db.Column(db.Integer, primary_key=True)
    nombre    = db.Column(db.String(80),  nullable=False)
    tipo      = db.Column(db.String(20),  default="mensual")   # mensual|quincenal|semanal
    inicio    = db.Column(db.Date,        nullable=False)
    fin       = db.Column(db.Date,        nullable=False)
    dias      = db.Column(db.Integer,     default=23)
    estado    = db.Column(db.String(20),  default="abierto")   # abierto|procesado|cerrado
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    nominas = db.relationship("Nomina", backref="periodo", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":     self.id,
            "nombre": self.nombre,
            "tipo":   self.tipo,
            "inicio": self.inicio.isoformat() if self.inicio else None,
            "fin":    self.fin.isoformat()    if self.fin    else None,
            "dias":   self.dias,
            "estado": self.estado,
        }


# ─────────────────────────────────────────
#  NÓMINA  (encabezado)
# ─────────────────────────────────────────
class Nomina(db.Model):
    __tablename__ = "nominas"

    id          = db.Column(db.Integer, primary_key=True)
    periodo_id  = db.Column(db.Integer, db.ForeignKey("periodos.id"), nullable=False)
    total_emps  = db.Column(db.Integer,       default=0)
    total_bruto = db.Column(db.Numeric(14, 2), default=0)
    total_neto  = db.Column(db.Numeric(14, 2), default=0)
    fecha_proc  = db.Column(db.Date,           default=date.today)
    estado      = db.Column(db.String(20),     default="procesada")
    creado_en   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    detalles = db.relationship("NominaDetalle", backref="nomina", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":           self.id,
            "periodo_id":   self.periodo_id,
            "total_emps":   self.total_emps,
            "total_bruto":  float(self.total_bruto or 0),
            "total_neto":   float(self.total_neto  or 0),
            "fecha_proc":   self.fecha_proc.isoformat() if self.fecha_proc else None,
            "estado":       self.estado,
        }


# ─────────────────────────────────────────
#  NÓMINA DETALLE  (una fila por empleado)
# ─────────────────────────────────────────
class NominaDetalle(db.Model):
    __tablename__ = "nominas_detalle"

    id           = db.Column(db.Integer, primary_key=True)
    nomina_id    = db.Column(db.Integer, db.ForeignKey("nominas.id"),    nullable=False)
    emp_id       = db.Column(db.Integer, db.ForeignKey("empleados.id"),  nullable=False)
    salario_base = db.Column(db.Numeric(12, 2), default=0)
    dias         = db.Column(db.Integer,        default=23)
    sal_calculado= db.Column(db.Numeric(12, 2), default=0)
    bonificacion = db.Column(db.Numeric(12, 2), default=0)
    desc_oblig   = db.Column(db.Numeric(12, 2), default=0)   # AFP+SFS+ISR
    desc_indiv   = db.Column(db.Numeric(12, 2), default=0)   # descuentos individuales
    total_desc   = db.Column(db.Numeric(12, 2), default=0)
    salario_neto = db.Column(db.Numeric(12, 2), default=0)

    def to_dict(self):
        return {
            "id":            self.id,
            "nomina_id":     self.nomina_id,
            "emp_id":        self.emp_id,
            "salario_base":  float(self.salario_base  or 0),
            "dias":          self.dias,
            "sal_calculado": float(self.sal_calculado or 0),
            "bonificacion":  float(self.bonificacion  or 0),
            "desc_oblig":    float(self.desc_oblig    or 0),
            "desc_indiv":    float(self.desc_indiv    or 0),
            "total_desc":    float(self.total_desc    or 0),
            "salario_neto":  float(self.salario_neto  or 0),
        }
