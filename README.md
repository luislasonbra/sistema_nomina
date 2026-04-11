# 🇩🇴 Sistema de Nómina RD — Flask + SQLite

Sistema completo de nómina para la República Dominicana con Flask, SQLAlchemy y SQLite.

---

## 📁 Estructura del proyecto

```
nominard/
├── app.py           ← Servidor Flask + todas las rutas API REST
├── models.py        ← Modelos de la base de datos (SQLAlchemy)
├── seed.py          ← Script para poblar datos de ejemplo
├── requirements.txt ← Dependencias Python
├── nominard.db      ← Base de datos SQLite (se crea automáticamente)
└── templates/
    └── index.html   ← Frontend completo (Bootstrap 5 + JS)
```

---

## 🗃️ Diagrama de la Base de Datos

```
departamentos          cargos
─────────────          ──────────────────────────────
id (PK)                id (PK)
nombre                 nombre
codigo                 dept_id ──────────────────────→ departamentos.id
descripcion            nivel
creado_en              sal_base
                       sal_max
                       creado_en

empleados
─────────────────────────────────────
id (PK)
nombres
apellidos
cedula (UNIQUE)
telefono
email
direccion
ingreso
dept_id ─────────────────────────────→ departamentos.id
cargo_id ────────────────────────────→ cargos.id
tipo           (fijo|por_hora|temporal)
salario
estado         (activo|inactivo|suspendido)
creado_en

tipos_deduccion                     descuentos_empleado
─────────────────────────           ──────────────────────────────────
id (PK)                             id (PK)
nombre (UNIQUE)                     emp_id ──────────────→ empleados.id
tipo    (porcentaje|fijo)           tipo_id ─────────────→ tipos_deduccion.id
valor                               nombre
aplica  (todos|fijo|por_hora)       tipo_val  (fijo|porcentaje)
obligatoria (si|no)                 valor
creado_en                           inicio
                                    fin
                                    cuotas
                                    activo (si|no)
                                    obs
                                    creado_en

periodos                nominas                 nominas_detalle
────────────────        ──────────────────      ──────────────────────────
id (PK)                 id (PK)                 id (PK)
nombre                  periodo_id ──→ periodos.id   nomina_id ──→ nominas.id
tipo                    total_emps              emp_id ──────→ empleados.id
inicio                  total_bruto             salario_base
fin                     total_neto              dias
dias                    fecha_proc              sal_calculado
estado                  estado                  bonificacion
creado_en               creado_en               desc_oblig
                                                desc_indiv
                                                total_desc
                                                salario_neto
```

---

## 🚀 Instalación paso a paso

### 1. Requisitos previos
- Python 3.9 o superior
- pip

Verificar:
```bash
python --version   # debe ser 3.9+
pip --version
```

### 2. Crear entorno virtual (recomendado)
```bash
# Crear el entorno
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Mac/Linux
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear la base de datos y poblar datos de ejemplo
```bash
python seed.py
```
Esto creará `nominard.db` con:
- 5 departamentos
- 8 cargos
- 8 tipos de deducción (AFP, SFS, ISR, etc.)
- 7 empleados de ejemplo
- 3 descuentos individuales demo
- 3 períodos de nómina

### 5. Ejecutar el servidor
```bash
python app.py
```

### 6. Abrir en el navegador
```
http://localhost:5000
```

---

## 🔌 API REST — Endpoints

### Departamentos
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/api/departamentos` | Listar todos |
| POST   | `/api/departamentos` | Crear nuevo |
| PUT    | `/api/departamentos/<id>` | Actualizar |
| DELETE | `/api/departamentos/<id>` | Eliminar |

### Cargos
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/api/cargos?dept_id=N` | Listar (filtrar por depto.) |
| POST   | `/api/cargos` | Crear nuevo |
| PUT    | `/api/cargos/<id>` | Actualizar |
| DELETE | `/api/cargos/<id>` | Eliminar |

### Empleados
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/api/empleados?q=texto&estado=activo` | Listar con filtros |
| GET    | `/api/empleados/<id>` | Obtener uno |
| POST   | `/api/empleados` | Crear nuevo |
| PUT    | `/api/empleados/<id>` | Actualizar |
| DELETE | `/api/empleados/<id>` | Eliminar |

### Tipos de Deducción
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/api/tipos-deduccion` | Listar todos |
| POST   | `/api/tipos-deduccion` | Crear nuevo |
| PUT    | `/api/tipos-deduccion/<id>` | Actualizar |
| DELETE | `/api/tipos-deduccion/<id>` | Eliminar |

### Descuentos por Empleado
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/api/descuentos?emp_id=N` | Listar (filtrar por empleado) |
| POST   | `/api/descuentos` | Asignar descuento |
| PUT    | `/api/descuentos/<id>` | Actualizar |
| DELETE | `/api/descuentos/<id>` | Eliminar |
| PATCH  | `/api/descuentos/<id>/toggle` | Activar/desactivar |

### Períodos
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/api/periodos` | Listar todos |
| POST   | `/api/periodos` | Crear nuevo |
| PUT    | `/api/periodos/<id>` | Actualizar |
| DELETE | `/api/periodos/<id>` | Eliminar |

### Nómina
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST   | `/api/nomina/calcular` | Calcular (sin guardar) |
| POST   | `/api/nomina/procesar` | Procesar y guardar |
| GET    | `/api/nomina/historial` | Historial procesadas |
| GET    | `/api/nomina/recibo?emp_id=N&periodo_id=N` | Recibo de pago |

### Reportes
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/api/reportes/resumen` | Resumen general |
| GET    | `/api/reportes/por-departamento` | Por departamento |
| GET    | `/api/reportes/por-empleado?q=texto` | Por empleado |

---

## 🔄 Migrar a PostgreSQL / MySQL

Solo cambia la línea de conexión en `app.py`:

```python
# SQLite (por defecto, ideal para desarrollo)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nominard.db"

# PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@localhost/nominard"

# MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:password@localhost/nominard"
```

Instalar el driver correspondiente:
```bash
pip install psycopg2-binary  # PostgreSQL
pip install pymysql          # MySQL
```

---

## 📝 Escala ISR República Dominicana (2024-2025)

| Renta Anual | Tasa |
|-------------|------|
| Hasta RD$ 416,220 | Exento |
| RD$ 416,220 – RD$ 624,329 | 15% |
| RD$ 624,329 – RD$ 867,123 | 20% |
| Más de RD$ 867,123 | 25% |

AFP Empleado: **2.87%** del salario  
SFS Empleado: **3.04%** del salario

---

## 🛠️ Comandos útiles

```bash
# Ejecutar en modo producción con Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Resetear la base de datos
rm nominard.db
python seed.py

# Ver la BD con SQLite CLI
sqlite3 nominard.db
.tables
SELECT * FROM empleados;
.quit
```
