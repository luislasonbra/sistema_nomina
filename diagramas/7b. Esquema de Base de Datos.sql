BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    reset_token VARCHAR(120),
    reset_expira DATETIME,
    activo VARCHAR(3) DEFAULT 'si',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cargos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    dept_id INTEGER NOT NULL,
    nivel VARCHAR(30) DEFAULT 'operativo',
    sal_base NUMERIC(12, 2) DEFAULT 0,
    sal_max NUMERIC(12, 2) DEFAULT 0,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departamentos(id)
);

CREATE TABLE IF NOT EXISTS empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres VARCHAR(80) NOT NULL,
    apellidos VARCHAR(80) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(120),
    direccion VARCHAR(255),
    ingreso DATE NOT NULL,
    dept_id INTEGER NOT NULL,
    cargo_id INTEGER NOT NULL,
    tipo VARCHAR(20) DEFAULT 'fijo',
    salario NUMERIC(12, 2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'activo',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departamentos(id),
    FOREIGN KEY (cargo_id) REFERENCES cargos(id)
);

CREATE TABLE IF NOT EXISTS tipos_deduccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(20) DEFAULT 'porcentaje',
    valor NUMERIC(10, 4) DEFAULT 0,
    aplica VARCHAR(20) DEFAULT 'todos',
    obligatoria VARCHAR(3) DEFAULT 'no',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS descuentos_empleado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    tipo_id INTEGER,
    nombre VARCHAR(120) NOT NULL,
    tipo_val VARCHAR(20) DEFAULT 'fijo',
    valor NUMERIC(12, 4) NOT NULL,
    inicio DATE,
    fin DATE,
    cuotas INTEGER DEFAULT 0,
    activo VARCHAR(3) DEFAULT 'si',
    obs VARCHAR(255),
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES empleados(id),
    FOREIGN KEY (tipo_id) REFERENCES tipos_deduccion(id)
);

CREATE TABLE IF NOT EXISTS periodos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(80) NOT NULL,
    tipo VARCHAR(20) DEFAULT 'mensual',
    inicio DATE NOT NULL,
    fin DATE NOT NULL,
    dias INTEGER DEFAULT 23,
    estado VARCHAR(20) DEFAULT 'abierto',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nominas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    periodo_id INTEGER NOT NULL,
    total_emps INTEGER DEFAULT 0,
    total_bruto NUMERIC(14, 2) DEFAULT 0,
    total_neto NUMERIC(14, 2) DEFAULT 0,
    fecha_proc DATE,
    estado VARCHAR(20) DEFAULT 'procesada',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (periodo_id) REFERENCES periodos(id)
);

CREATE TABLE IF NOT EXISTS nominas_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomina_id INTEGER NOT NULL,
    emp_id INTEGER NOT NULL,
    salario_base NUMERIC(12, 2) DEFAULT 0,
    dias INTEGER DEFAULT 23,
    sal_calculado NUMERIC(12, 2) DEFAULT 0,
    bonificacion NUMERIC(12, 2) DEFAULT 0,
    desc_oblig NUMERIC(12, 2) DEFAULT 0,
    desc_indiv NUMERIC(12, 2) DEFAULT 0,
    total_desc NUMERIC(12, 2) DEFAULT 0,
    salario_neto NUMERIC(12, 2) DEFAULT 0,
    FOREIGN KEY (nomina_id) REFERENCES nominas(id),
    FOREIGN KEY (emp_id) REFERENCES empleados(id)
);

COMMIT;

