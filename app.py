"""
app.py
API REST + servidor del frontend para el Sistema de Nómina RD
"""
from flask import Flask, jsonify, request, render_template, abort, session, g
from flask_cors import CORS
from models import (db, Usuario, Departamento, Cargo, Empleado,
                    TipoDeduccion, DescuentoEmpleado,
                    Periodo, Nomina, NominaDetalle)
from datetime import date, datetime, timedelta
from decimal import Decimal
from secrets import token_urlsafe
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)

# ── Configuración ───────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "nominard.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "nomina-rd-secret-2025"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

db.init_app(app)

with app.app_context():
    db.create_all()


# ── Helpers ─────────────────────────────────────────────────────
def parse_date(s):
    """Convierte string ISO a date, o None."""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def calcular_isr(salario_mensual):
    """Escala ISR República Dominicana (vigente 2024-2025)."""
    anual = float(salario_mensual) * 12
    if anual <= 416220:
        isr = 0
    elif anual <= 624329:
        isr = (anual - 416220) * 0.15
    elif anual <= 867123:
        isr = 31216 + (anual - 624329) * 0.20
    else:
        isr = 79776 + (anual - 867123) * 0.25
    return round(isr / 12, 2)


def calcular_deducciones_obligatorias(salario, tipo_emp):
    """Retorna lista de {nombre, monto} para deducciones obligatorias."""
    resultado = []
    tipos = TipoDeduccion.query.filter_by(obligatoria="si").all()
    for t in tipos:
        aplica = t.aplica == "todos" or t.aplica == tipo_emp
        if not aplica:
            continue
        if t.nombre == "ISR":
            monto = calcular_isr(salario)
        elif t.tipo == "porcentaje":
            monto = round(float(salario) * (float(t.valor) / 100), 2)
        else:
            monto = float(t.valor)
        if monto > 0:
            resultado.append({"nombre": t.nombre, "monto": monto, "cat": "obligatoria"})
    return resultado


def calcular_deducciones_individuales(salario, emp_id):
    """Retorna lista de {nombre, monto} para descuentos individuales activos."""
    hoy = date.today()
    resultado = []
    descuentos = DescuentoEmpleado.query.filter_by(emp_id=emp_id, activo="si").all()
    for d in descuentos:
        if d.fin and d.fin < hoy:
            continue
        if d.tipo_val == "porcentaje":
            monto = round(float(salario) * (float(d.valor) / 100), 2)
        else:
            monto = float(d.valor)
        if monto > 0:
            resultado.append({"nombre": d.nombre, "monto": monto, "cat": "individual"})
    return resultado


def err(msg, code=400):
    return jsonify({"error": msg}), code


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return Usuario.query.get(user_id)


def auth_payload(user):
    return user.to_safe_dict() if user else None


@app.before_request
def protect_api():
    g.user = current_user()
    if request.path.startswith("/api/") and not request.path.startswith("/api/auth/"):
        if not g.user:
            return err("Debes iniciar sesión para continuar", 401)


# ════════════════════════════════════════════════════════════════════════
#  AUTH
# ════════════════════════════════════════════════════════════════════════
@app.route("/api/auth/session", methods=["GET"])
def auth_session():
    return jsonify({
        "authenticated": g.user is not None,
        "user": auth_payload(g.user),
    })


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json() or {}
    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not nombre or not email or not password:
        return err("Nombre, correo y contraseña son requeridos")
    if len(password) < 6:
        return err("La contraseña debe tener al menos 6 caracteres")
    if Usuario.query.filter_by(email=email).first():
        return err("Ya existe un usuario con ese correo")

    user = Usuario(
        nombre=nombre,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    session.permanent = True
    session["user_id"] = user.id
    return jsonify({"ok": True, "user": auth_payload(user)}), 201


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = Usuario.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return err("Correo o contraseña inválidos", 401)
    if user.activo != "si":
        return err("Este usuario está inactivo", 403)

    session.permanent = True
    session["user_id"] = user.id
    return jsonify({"ok": True, "user": auth_payload(user)})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.pop("user_id", None)
    return jsonify({"ok": True})


@app.route("/api/auth/forgot-password", methods=["POST"])
def auth_forgot_password():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    user = Usuario.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "ok": True,
            "message": "Si el correo existe, podrás restablecer la contraseña.",
        })

    token = token_urlsafe(16)
    user.reset_token = token
    user.reset_expira = datetime.utcnow() + timedelta(minutes=30)
    db.session.commit()

    return jsonify({
        "ok": True,
        "message": "Se generó un token temporal de recuperación.",
        "reset_token": token,
        "expires_in_minutes": 30,
    })


@app.route("/api/auth/reset-password", methods=["POST"])
def auth_reset_password():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    token = (data.get("token") or "").strip()
    password = data.get("password") or ""

    if not email or not token or not password:
        return err("Correo, token y nueva contraseña son requeridos")
    if len(password) < 6:
        return err("La nueva contraseña debe tener al menos 6 caracteres")

    user = Usuario.query.filter_by(email=email, reset_token=token).first()
    if not user or not user.reset_expira or user.reset_expira < datetime.utcnow():
        return err("El token es inválido o ya expiró", 400)

    user.password_hash = generate_password_hash(password)
    user.reset_token = None
    user.reset_expira = None
    db.session.commit()
    return jsonify({"ok": True, "message": "Contraseña actualizada correctamente"})


# ════════════════════════════════════════════════════════════════
#  FRONTEND
# ════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html", auth_user=auth_payload(g.user))


# ════════════════════════════════════════════════════════════════
#  API – DEPARTAMENTOS
# ════════════════════════════════════════════════════════════════
@app.route("/api/departamentos", methods=["GET"])
def get_departamentos():
    return jsonify([d.to_dict() for d in Departamento.query.order_by(Departamento.nombre).all()])


@app.route("/api/departamentos", methods=["POST"])
def create_departamento():
    data = request.get_json()
    if not data.get("nombre") or not data.get("codigo"):
        return err("Nombre y código son requeridos")
    if Departamento.query.filter_by(codigo=data["codigo"].upper()).first():
        return err("El código ya existe")
    d = Departamento(
        nombre=data["nombre"].strip(),
        codigo=data["codigo"].strip().upper(),
        descripcion=data.get("descripcion", "")
    )
    db.session.add(d)
    db.session.commit()
    return jsonify(d.to_dict()), 201


@app.route("/api/departamentos/<int:id>", methods=["PUT"])
def update_departamento(id):
    d = Departamento.query.get_or_404(id)
    data = request.get_json()
    d.nombre      = data.get("nombre",      d.nombre).strip()
    d.codigo      = data.get("codigo",      d.codigo).strip().upper()
    d.descripcion = data.get("descripcion", d.descripcion)
    db.session.commit()
    return jsonify(d.to_dict())


@app.route("/api/departamentos/<int:id>", methods=["DELETE"])
def delete_departamento(id):
    d = Departamento.query.get_or_404(id)
    if d.empleados:
        return err("No se puede eliminar: tiene empleados asignados")
    db.session.delete(d)
    db.session.commit()
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════════════════
#  API – CARGOS
# ════════════════════════════════════════════════════════════════
@app.route("/api/cargos", methods=["GET"])
def get_cargos():
    dept_id = request.args.get("dept_id", type=int)
    q = Cargo.query
    if dept_id:
        q = q.filter_by(dept_id=dept_id)
    return jsonify([c.to_dict() for c in q.order_by(Cargo.nombre).all()])


@app.route("/api/cargos", methods=["POST"])
def create_cargo():
    data = request.get_json()
    if not data.get("nombre") or not data.get("dept_id"):
        return err("Nombre y departamento requeridos")
    c = Cargo(
        nombre   = data["nombre"].strip(),
        dept_id  = int(data["dept_id"]),
        nivel    = data.get("nivel", "operativo"),
        sal_base = data.get("sal_base", 0),
        sal_max  = data.get("sal_max",  0),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201


@app.route("/api/cargos/<int:id>", methods=["PUT"])
def update_cargo(id):
    c = Cargo.query.get_or_404(id)
    data = request.get_json()
    c.nombre   = data.get("nombre",   c.nombre).strip()
    c.dept_id  = data.get("dept_id",  c.dept_id)
    c.nivel    = data.get("nivel",    c.nivel)
    c.sal_base = data.get("sal_base", c.sal_base)
    c.sal_max  = data.get("sal_max",  c.sal_max)
    db.session.commit()
    return jsonify(c.to_dict())


@app.route("/api/cargos/<int:id>", methods=["DELETE"])
def delete_cargo(id):
    c = Cargo.query.get_or_404(id)
    if c.empleados:
        return err("No se puede eliminar: tiene empleados asignados")
    db.session.delete(c)
    db.session.commit()
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════════════════
#  API – EMPLEADOS
# ════════════════════════════════════════════════════════════════
@app.route("/api/empleados", methods=["GET"])
def get_empleados():
    q_str  = request.args.get("q", "").lower()
    estado = request.args.get("estado", "")
    q = Empleado.query
    if estado:
        q = q.filter_by(estado=estado)
    emps = q.order_by(Empleado.apellidos, Empleado.nombres).all()
    if q_str:
        emps = [e for e in emps if q_str in f"{e.nombres} {e.apellidos} {e.cedula} {e.email or ''}".lower()]
    return jsonify([e.to_dict() for e in emps])


@app.route("/api/empleados/<int:id>", methods=["GET"])
def get_empleado(id):
    return jsonify(Empleado.query.get_or_404(id).to_dict())


@app.route("/api/empleados", methods=["POST"])
def create_empleado():
    data = request.get_json()
    required = ["nombres", "apellidos", "cedula", "ingreso", "dept_id", "cargo_id", "salario"]
    for f in required:
        if not data.get(f):
            return err(f"Campo requerido: {f}")
    if Empleado.query.filter_by(cedula=data["cedula"]).first():
        return err("La cédula ya está registrada")
    e = Empleado(
        nombres   = data["nombres"].strip(),
        apellidos = data["apellidos"].strip(),
        cedula    = data["cedula"].strip(),
        telefono  = data.get("telefono", ""),
        email     = data.get("email", ""),
        direccion = data.get("direccion", ""),
        ingreso   = parse_date(data["ingreso"]),
        dept_id   = int(data["dept_id"]),
        cargo_id  = int(data["cargo_id"]),
        tipo      = data.get("tipo", "fijo"),
        salario   = float(data["salario"]),
        estado    = data.get("estado", "activo"),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify(e.to_dict()), 201


@app.route("/api/empleados/<int:id>", methods=["PUT"])
def update_empleado(id):
    e    = Empleado.query.get_or_404(id)
    data = request.get_json()
    # verificar cédula duplicada si se cambia
    if "cedula" in data and data["cedula"] != e.cedula:
        if Empleado.query.filter_by(cedula=data["cedula"]).first():
            return err("La cédula ya está registrada")
    e.nombres   = data.get("nombres",   e.nombres).strip()
    e.apellidos = data.get("apellidos", e.apellidos).strip()
    e.cedula    = data.get("cedula",    e.cedula).strip()
    e.telefono  = data.get("telefono",  e.telefono)
    e.email     = data.get("email",     e.email)
    e.direccion = data.get("direccion", e.direccion)
    e.ingreso   = parse_date(data["ingreso"]) if "ingreso" in data else e.ingreso
    e.dept_id   = data.get("dept_id",   e.dept_id)
    e.cargo_id  = data.get("cargo_id",  e.cargo_id)
    e.tipo      = data.get("tipo",      e.tipo)
    e.salario   = data.get("salario",   e.salario)
    e.estado    = data.get("estado",    e.estado)
    db.session.commit()
    return jsonify(e.to_dict())


@app.route("/api/empleados/<int:id>", methods=["DELETE"])
def delete_empleado(id):
    e = Empleado.query.get_or_404(id)
    db.session.delete(e)
    db.session.commit()
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════════════════
#  API – TIPOS DE DEDUCCIÓN
# ════════════════════════════════════════════════════════════════
@app.route("/api/tipos-deduccion", methods=["GET"])
def get_tipos():
    return jsonify([t.to_dict() for t in TipoDeduccion.query.order_by(TipoDeduccion.nombre).all()])


@app.route("/api/tipos-deduccion", methods=["POST"])
def create_tipo():
    data = request.get_json()
    if not data.get("nombre"):
        return err("Nombre requerido")
    if TipoDeduccion.query.filter_by(nombre=data["nombre"].strip()).first():
        return err("Ya existe un tipo con ese nombre")
    t = TipoDeduccion(
        nombre      = data["nombre"].strip(),
        tipo        = data.get("tipo", "porcentaje"),
        valor       = data.get("valor", 0),
        aplica      = data.get("aplica", "todos"),
        obligatoria = data.get("obligatoria", "no"),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201


@app.route("/api/tipos-deduccion/<int:id>", methods=["PUT"])
def update_tipo(id):
    t = TipoDeduccion.query.get_or_404(id)
    data = request.get_json()
    t.nombre      = data.get("nombre",      t.nombre).strip()
    t.tipo        = data.get("tipo",        t.tipo)
    t.valor       = data.get("valor",       t.valor)
    t.aplica      = data.get("aplica",      t.aplica)
    t.obligatoria = data.get("obligatoria", t.obligatoria)
    db.session.commit()
    return jsonify(t.to_dict())


@app.route("/api/tipos-deduccion/<int:id>", methods=["DELETE"])
def delete_tipo(id):
    t = TipoDeduccion.query.get_or_404(id)
    if t.descuentos:
        return err("No se puede eliminar: tiene descuentos asignados a empleados")
    db.session.delete(t)
    db.session.commit()
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════════════════
#  API – DESCUENTOS POR EMPLEADO
# ════════════════════════════════════════════════════════════════
@app.route("/api/descuentos", methods=["GET"])
def get_descuentos():
    emp_id = request.args.get("emp_id", type=int)
    q = DescuentoEmpleado.query
    if emp_id:
        q = q.filter_by(emp_id=emp_id)
    return jsonify([d.to_dict() for d in q.order_by(DescuentoEmpleado.creado_en.desc()).all()])


@app.route("/api/descuentos", methods=["POST"])
def create_descuento():
    data = request.get_json()
    if not data.get("emp_id"):
        return err("emp_id requerido")
    if not data.get("nombre"):
        return err("El concepto/nombre es requerido")
    if not data.get("valor") or float(data["valor"]) <= 0:
        return err("El valor debe ser mayor a 0")
    d = DescuentoEmpleado(
        emp_id   = int(data["emp_id"]),
        tipo_id  = int(data["tipo_id"]) if data.get("tipo_id") else None,
        nombre   = data["nombre"].strip(),
        tipo_val = data.get("tipo_val", "fijo"),
        valor    = float(data["valor"]),
        inicio   = parse_date(data.get("inicio")),
        fin      = parse_date(data.get("fin")),
        cuotas   = int(data.get("cuotas", 0)),
        activo   = data.get("activo", "si"),
        obs      = data.get("obs", "").strip(),
    )
    db.session.add(d)
    db.session.commit()
    return jsonify(d.to_dict()), 201


@app.route("/api/descuentos/<int:id>", methods=["PUT"])
def update_descuento(id):
    d = DescuentoEmpleado.query.get_or_404(id)
    data = request.get_json()
    d.tipo_id  = int(data["tipo_id"]) if data.get("tipo_id") else None
    d.nombre   = data.get("nombre",   d.nombre).strip()
    d.tipo_val = data.get("tipo_val", d.tipo_val)
    d.valor    = data.get("valor",    d.valor)
    d.inicio   = parse_date(data.get("inicio")) if "inicio" in data else d.inicio
    d.fin      = parse_date(data.get("fin"))    if "fin"    in data else d.fin
    d.cuotas   = data.get("cuotas",   d.cuotas)
    d.activo   = data.get("activo",   d.activo)
    d.obs      = data.get("obs",      d.obs or "").strip()
    db.session.commit()
    return jsonify(d.to_dict())


@app.route("/api/descuentos/<int:id>", methods=["DELETE"])
def delete_descuento(id):
    d = DescuentoEmpleado.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/descuentos/<int:id>/toggle", methods=["PATCH"])
def toggle_descuento(id):
    d = DescuentoEmpleado.query.get_or_404(id)
    data = request.get_json()
    d.activo = "si" if data.get("activo") else "no"
    if d.activo == "no" and not d.fin:
        d.fin = date.today()
    db.session.commit()
    return jsonify(d.to_dict())


# ════════════════════════════════════════════════════════════════
#  API – PERÍODOS
# ════════════════════════════════════════════════════════════════
@app.route("/api/periodos", methods=["GET"])
def get_periodos():
    return jsonify([p.to_dict() for p in Periodo.query.order_by(Periodo.inicio.desc()).all()])


@app.route("/api/periodos", methods=["POST"])
def create_periodo():
    data = request.get_json()
    if not data.get("nombre") or not data.get("inicio") or not data.get("fin"):
        return err("Nombre y fechas son requeridos")
    p = Periodo(
        nombre = data["nombre"].strip(),
        tipo   = data.get("tipo", "mensual"),
        inicio = parse_date(data["inicio"]),
        fin    = parse_date(data["fin"]),
        dias   = int(data.get("dias", 23)),
        estado = data.get("estado", "abierto"),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@app.route("/api/periodos/<int:id>", methods=["PUT"])
def update_periodo(id):
    p = Periodo.query.get_or_404(id)
    data = request.get_json()
    p.nombre = data.get("nombre", p.nombre).strip()
    p.tipo   = data.get("tipo",   p.tipo)
    p.inicio = parse_date(data["inicio"]) if "inicio" in data else p.inicio
    p.fin    = parse_date(data["fin"])    if "fin"    in data else p.fin
    p.dias   = data.get("dias",   p.dias)
    p.estado = data.get("estado", p.estado)
    db.session.commit()
    return jsonify(p.to_dict())


@app.route("/api/periodos/<int:id>", methods=["DELETE"])
def delete_periodo(id):
    p = Periodo.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════════════════
#  API – NÓMINA  (calcular + procesar)
# ════════════════════════════════════════════════════════════════
@app.route("/api/nomina/calcular", methods=["POST"])
def calcular_nomina():
    """
    Calcula la nómina (sin guardar) y retorna el detalle por empleado.
    Body: { periodo_id, dept_id? }
    """
    data      = request.get_json()
    periodo_id = data.get("periodo_id")
    dept_id    = data.get("dept_id")

    if not periodo_id:
        return err("periodo_id requerido")

    periodo = Periodo.query.get_or_404(periodo_id)
    q = Empleado.query.filter_by(estado="activo")
    if dept_id:
        q = q.filter_by(dept_id=int(dept_id))
    empleados = q.all()

    filas = []
    for e in empleados:
        sal_calc = round(float(e.salario) / 23 * periodo.dias, 2)
        obl      = calcular_deducciones_obligatorias(sal_calc, e.tipo)
        ind      = calcular_deducciones_individuales(sal_calc, e.id)
        tot_obl  = round(sum(x["monto"] for x in obl), 2)
        tot_ind  = round(sum(x["monto"] for x in ind), 2)
        tot_desc = round(tot_obl + tot_ind, 2)
        neto     = round(sal_calc - tot_desc, 2)
        filas.append({
            "emp_id":        e.id,
            "nombre":        f"{e.nombres} {e.apellidos}",
            "dept":          e.departamento.nombre if e.departamento else "",
            "salario_base":  float(e.salario),
            "sal_calculado": sal_calc,
            "desc_oblig":    tot_obl,
            "desc_indiv":    tot_ind,
            "total_desc":    tot_desc,
            "salario_neto":  neto,
            "detalle_obl":   obl,
            "detalle_ind":   ind,
        })

    total_bruto = round(sum(f["sal_calculado"] for f in filas), 2)
    total_desc  = round(sum(f["total_desc"]    for f in filas), 2)
    total_neto  = round(sum(f["salario_neto"]  for f in filas), 2)

    return jsonify({
        "periodo":     periodo.to_dict(),
        "filas":       filas,
        "total_bruto": total_bruto,
        "total_desc":  total_desc,
        "total_neto":  total_neto,
    })


@app.route("/api/nomina/procesar", methods=["POST"])
def procesar_nomina():
    """
    Guarda la nómina definitivamente y marca el período como procesado.
    Body: { periodo_id, filas: [{emp_id, sal_calculado, bonificacion, ...}] }
    """
    data       = request.get_json()
    periodo_id = data.get("periodo_id")
    if not periodo_id:
        return err("periodo_id requerido")

    periodo = Periodo.query.get_or_404(periodo_id)
    if periodo.estado == "cerrado":
        return err("El período está cerrado")

    # Eliminar nómina anterior si existe (re-proceso)
    Nomina.query.filter_by(periodo_id=periodo_id).delete()
    db.session.flush()

    emps = Empleado.query.filter_by(estado="activo").all()
    detalles = []
    for e in emps:
        sal_calc = round(float(e.salario) / 23 * periodo.dias, 2)
        obl      = calcular_deducciones_obligatorias(sal_calc, e.tipo)
        ind      = calcular_deducciones_individuales(sal_calc, e.id)
        tot_obl  = round(sum(x["monto"] for x in obl), 2)
        tot_ind  = round(sum(x["monto"] for x in ind), 2)
        tot_desc = round(tot_obl + tot_ind, 2)
        neto     = round(sal_calc - tot_desc, 2)
        detalles.append(NominaDetalle(
            emp_id       = e.id,
            salario_base = float(e.salario),
            dias         = periodo.dias,
            sal_calculado= sal_calc,
            bonificacion = 0,
            desc_oblig   = tot_obl,
            desc_indiv   = tot_ind,
            total_desc   = tot_desc,
            salario_neto = neto,
        ))

    nomina = Nomina(
        periodo_id  = periodo_id,
        total_emps  = len(detalles),
        total_bruto = round(sum(d.sal_calculado for d in detalles), 2),
        total_neto  = round(sum(d.salario_neto  for d in detalles), 2),
        fecha_proc  = date.today(),
        estado      = "procesada",
    )
    db.session.add(nomina)
    db.session.flush()

    for det in detalles:
        det.nomina_id = nomina.id
        db.session.add(det)

    periodo.estado = "procesado"
    db.session.commit()
    return jsonify(nomina.to_dict()), 201


@app.route("/api/nomina/historial", methods=["GET"])
def historial_nominas():
    nominas = Nomina.query.order_by(Nomina.fecha_proc.desc()).all()
    result = []
    for n in nominas:
        d = n.to_dict()
        d["periodo_nombre"] = n.periodo.nombre if n.periodo else "—"
        result.append(d)
    return jsonify(result)


@app.route("/api/nomina/recibo", methods=["GET"])
def recibo_pago():
    """Genera el recibo de un empleado para un período específico."""
    emp_id     = request.args.get("emp_id",     type=int)
    periodo_id = request.args.get("periodo_id", type=int)
    if not emp_id or not periodo_id:
        return err("emp_id y periodo_id requeridos")

    e = Empleado.query.get_or_404(emp_id)
    p = Periodo.query.get_or_404(periodo_id)

    sal_calc = round(float(e.salario) / 23 * p.dias, 2)
    obl      = calcular_deducciones_obligatorias(sal_calc, e.tipo)
    ind      = calcular_deducciones_individuales(sal_calc, e.id)
    tot_obl  = round(sum(x["monto"] for x in obl), 2)
    tot_ind  = round(sum(x["monto"] for x in ind), 2)
    tot_desc = round(tot_obl + tot_ind, 2)
    neto     = round(sal_calc - tot_desc, 2)

    return jsonify({
        "empleado": e.to_dict(),
        "periodo":  p.to_dict(),
        "departamento": e.departamento.nombre if e.departamento else "",
        "cargo":        e.cargo.nombre        if e.cargo        else "",
        "sal_calculado":sal_calc,
        "deducciones_obligatorias": obl,
        "descuentos_individuales":  ind,
        "total_oblig":  tot_obl,
        "total_indiv":  tot_ind,
        "total_desc":   tot_desc,
        "salario_neto": neto,
    })


# ════════════════════════════════════════════════════════════════
#  API – REPORTES
# ════════════════════════════════════════════════════════════════
@app.route("/api/reportes/resumen", methods=["GET"])
def reporte_resumen():
    act     = Empleado.query.filter_by(estado="activo").all()
    masa    = sum(float(e.salario) for e in act)
    prom    = masa / len(act) if act else 0
    d_activos = DescuentoEmpleado.query.filter_by(activo="si").count()
    return jsonify({
        "empleados_activos":  len(act),
        "masa_salarial":      round(masa, 2),
        "salario_promedio":   round(prom, 2),
        "departamentos":      Departamento.query.count(),
        "tipos_deduccion":    TipoDeduccion.query.count(),
        "descuentos_activos": d_activos,
        "nominas_procesadas": Nomina.query.count(),
        "distribucion_estado": {
            "activo":     Empleado.query.filter_by(estado="activo").count(),
            "inactivo":   Empleado.query.filter_by(estado="inactivo").count(),
            "suspendido": Empleado.query.filter_by(estado="suspendido").count(),
        }
    })


@app.route("/api/reportes/por-departamento", methods=["GET"])
def reporte_por_dept():
    depts = Departamento.query.all()
    total_sal = sum(float(e.salario) for e in Empleado.query.all()) or 1
    result = []
    for d in depts:
        emps  = d.empleados
        total = sum(float(e.salario) for e in emps)
        prom  = total / len(emps) if emps else 0
        result.append({
            "dept_id":  d.id,
            "nombre":   d.nombre,
            "empleados":len(emps),
            "total":    round(total, 2),
            "promedio": round(prom,  2),
            "pct":      round(total / total_sal * 100, 1),
        })
    result.sort(key=lambda x: x["total"], reverse=True)
    return jsonify(result)


@app.route("/api/reportes/por-empleado", methods=["GET"])
def reporte_por_empleado():
    q = request.args.get("q", "").lower()
    emps = Empleado.query.order_by(Empleado.apellidos).all()
    if q:
        emps = [e for e in emps if q in f"{e.nombres} {e.apellidos}".lower()]
    result = []
    for e in emps:
        obl = sum(x["monto"] for x in calcular_deducciones_obligatorias(float(e.salario), e.tipo))
        ind = sum(x["monto"] for x in calcular_deducciones_individuales(float(e.salario), e.id))
        result.append({
            "emp_id":    e.id,
            "nombre":    f"{e.nombres} {e.apellidos}",
            "dept":      e.departamento.nombre if e.departamento else "",
            "cargo":     e.cargo.nombre        if e.cargo        else "",
            "salario":   float(e.salario),
            "desc_oblig":round(obl, 2),
            "desc_indiv":round(ind, 2),
            "neto":      round(float(e.salario) - obl - ind, 2),
        })
    return jsonify(result)


# ════════════════════════════════════════════════════════════════
#  DASHBOARD  (stats rápidas)
# ════════════════════════════════════════════════════════════════
@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    act  = Empleado.query.filter_by(estado="activo").all()
    masa = sum(float(e.salario) for e in act)
    recent = Empleado.query.order_by(Empleado.creado_en.desc()).limit(6).all()
    return jsonify({
        "total_empleados":   len(act),
        "masa_salarial":     round(masa, 2),
        "departamentos":     Departamento.query.count(),
        "nominas_procesadas":Nomina.query.count(),
        "empleados_recientes": [e.to_dict() for e in recent],
    })


# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(debug=True, port=5000)
