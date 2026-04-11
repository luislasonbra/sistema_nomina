BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS cargos (
	id INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	dept_id INTEGER NOT NULL, 
	nivel VARCHAR(30), 
	sal_base NUMERIC(12, 2), 
	sal_max NUMERIC(12, 2), 
	creado_en DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(dept_id) REFERENCES departamentos (id)
);
CREATE TABLE IF NOT EXISTS departamentos (
	id INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	codigo VARCHAR(10) NOT NULL, 
	descripcion VARCHAR(255), 
	creado_en DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (nombre), 
	UNIQUE (codigo)
);
CREATE TABLE IF NOT EXISTS descuentos_empleado (
	id INTEGER NOT NULL, 
	emp_id INTEGER NOT NULL, 
	tipo_id INTEGER, 
	nombre VARCHAR(120) NOT NULL, 
	tipo_val VARCHAR(20), 
	valor NUMERIC(12, 4) NOT NULL, 
	inicio DATE, 
	fin DATE, 
	cuotas INTEGER, 
	activo VARCHAR(3), 
	obs VARCHAR(255), 
	creado_en DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(emp_id) REFERENCES empleados (id), 
	FOREIGN KEY(tipo_id) REFERENCES tipos_deduccion (id)
);
CREATE TABLE IF NOT EXISTS empleados (
	id INTEGER NOT NULL, 
	nombres VARCHAR(80) NOT NULL, 
	apellidos VARCHAR(80) NOT NULL, 
	cedula VARCHAR(20) NOT NULL, 
	telefono VARCHAR(20), 
	email VARCHAR(120), 
	direccion VARCHAR(255), 
	ingreso DATE NOT NULL, 
	dept_id INTEGER NOT NULL, 
	cargo_id INTEGER NOT NULL, 
	tipo VARCHAR(20), 
	salario NUMERIC(12, 2) NOT NULL, 
	estado VARCHAR(20), 
	creado_en DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (cedula), 
	FOREIGN KEY(dept_id) REFERENCES departamentos (id), 
	FOREIGN KEY(cargo_id) REFERENCES cargos (id)
);
CREATE TABLE IF NOT EXISTS nominas (
	id INTEGER NOT NULL, 
	periodo_id INTEGER NOT NULL, 
	total_emps INTEGER, 
	total_bruto NUMERIC(14, 2), 
	total_neto NUMERIC(14, 2), 
	fecha_proc DATE, 
	estado VARCHAR(20), 
	creado_en DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(periodo_id) REFERENCES periodos (id)
);
CREATE TABLE IF NOT EXISTS nominas_detalle (
	id INTEGER NOT NULL, 
	nomina_id INTEGER NOT NULL, 
	emp_id INTEGER NOT NULL, 
	salario_base NUMERIC(12, 2), 
	dias INTEGER, 
	sal_calculado NUMERIC(12, 2), 
	bonificacion NUMERIC(12, 2), 
	desc_oblig NUMERIC(12, 2), 
	desc_indiv NUMERIC(12, 2), 
	total_desc NUMERIC(12, 2), 
	salario_neto NUMERIC(12, 2), 
	PRIMARY KEY (id), 
	FOREIGN KEY(nomina_id) REFERENCES nominas (id), 
	FOREIGN KEY(emp_id) REFERENCES empleados (id)
);
CREATE TABLE IF NOT EXISTS periodos (
	id INTEGER NOT NULL, 
	nombre VARCHAR(80) NOT NULL, 
	tipo VARCHAR(20), 
	inicio DATE NOT NULL, 
	fin DATE NOT NULL, 
	dias INTEGER, 
	estado VARCHAR(20), 
	creado_en DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS tipos_deduccion (
	id INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	tipo VARCHAR(20), 
	valor NUMERIC(10, 4), 
	aplica VARCHAR(20), 
	obligatoria VARCHAR(3), 
	creado_en DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
);
INSERT INTO "cargos" ("id","nombre","dept_id","nivel","sal_base","sal_max","creado_en") VALUES (1,'Gerente General',1,'directivo',120000,150000,'2026-04-11 17:14:14.112388'),
 (2,'Asistente Administrativo',1,'operativo',25000,35000,'2026-04-11 17:14:14.112390'),
 (3,'Gerente de Ventas',2,'gerencial',80000,100000,'2026-04-11 17:14:14.112391'),
 (4,'Vendedor',2,'operativo',20000,35000,'2026-04-11 17:14:14.112392'),
 (5,'Desarrollador Senior',3,'tecnico',60000,90000,'2026-04-11 17:14:14.112393'),
 (6,'Soporte TI',3,'tecnico',30000,45000,'2026-04-11 17:14:14.112393'),
 (7,'Supervisor Operaciones',4,'supervisorio',45000,60000,'2026-04-11 17:14:14.112394'),
 (8,'Analista RRHH',5,'tecnico',35000,50000,'2026-04-11 17:14:14.112395');
INSERT INTO "departamentos" ("id","nombre","codigo","descripcion","creado_en") VALUES (1,'Administración','ADM','Área administrativa general','2026-04-11 17:14:14.110219'),
 (2,'Ventas','VEN','Área comercial y ventas','2026-04-11 17:14:14.110222'),
 (3,'Tecnología','TEC','Sistemas e informática','2026-04-11 17:14:14.110224'),
 (4,'Operaciones','OPE','Logística y operaciones','2026-04-11 17:14:14.110225'),
 (5,'RRHH','RRH','Recursos Humanos','2026-04-11 17:14:14.110226');
INSERT INTO "descuentos_empleado" ("id","emp_id","tipo_id","nombre","tipo_val","valor","inicio","fin","cuotas","activo","obs","creado_en") VALUES (1,2,4,'Préstamo personal ene-2025','fijo',3000,'2025-01-01',NULL,12,'si','Aprobado por RRHH','2026-04-11 17:14:14.116103'),
 (2,5,5,'Cooperativa empleados','fijo',1500,'2024-06-01',NULL,0,'si','','2026-04-11 17:14:14.116105'),
 (3,3,6,'Embargo judicial','porcentaje',10,'2025-02-01','2025-12-31',0,'si','Orden 2024-1234','2026-04-11 17:14:14.116106');
INSERT INTO "empleados" ("id","nombres","apellidos","cedula","telefono","email","direccion","ingreso","dept_id","cargo_id","tipo","salario","estado","creado_en") VALUES (1,'María','González','001-1234567-8','809-555-0001','maria@emp.com',NULL,'2022-03-15',5,8,'fijo',35000,'activo','2026-04-11 17:14:14.114871'),
 (2,'Juan','Pérez','001-2345678-9','809-555-0002','juan@emp.com',NULL,'2021-07-01',2,3,'fijo',85000,'activo','2026-04-11 17:14:14.114873'),
 (3,'Carlos','Martínez','001-3456789-0','809-555-0003','carlos@emp.com',NULL,'2023-01-10',3,5,'fijo',65000,'activo','2026-04-11 17:14:14.114874'),
 (4,'Ana','Rodríguez','001-4567890-1','809-555-0004','ana@emp.com',NULL,'2020-09-20',1,1,'fijo',130000,'activo','2026-04-11 17:14:14.114874'),
 (5,'Luis','Méndez','001-5678901-2','809-555-0005','luis@emp.com',NULL,'2023-06-01',4,7,'fijo',48000,'activo','2026-04-11 17:14:14.114875'),
 (6,'Paola','Santos','001-6789012-3','809-555-0006','paola@emp.com',NULL,'2022-11-15',2,4,'fijo',22000,'activo','2026-04-11 17:14:14.114876'),
 (7,'Roberto','Díaz','001-7890123-4','809-555-0007','roberto@emp.com',NULL,'2024-01-02',3,6,'fijo',32000,'activo','2026-04-11 17:14:14.114877');
INSERT INTO "periodos" ("id","nombre","tipo","inicio","fin","dias","estado","creado_en") VALUES (1,'Enero 2025','mensual','2025-01-01','2025-01-31',23,'cerrado','2026-04-11 17:14:14.116736'),
 (2,'Febrero 2025','mensual','2025-02-01','2025-02-28',20,'cerrado','2026-04-11 17:14:14.116738'),
 (3,'Marzo 2025','mensual','2025-03-01','2025-03-31',21,'abierto','2026-04-11 17:14:14.116739');
INSERT INTO "tipos_deduccion" ("id","nombre","tipo","valor","aplica","obligatoria","creado_en") VALUES (1,'AFP Empleado','porcentaje',2.87,'todos','si','2026-04-11 17:14:14.113526'),
 (2,'SFS Empleado','porcentaje',3.04,'todos','si','2026-04-11 17:14:14.113528'),
 (3,'ISR','porcentaje',0,'todos','si','2026-04-11 17:14:14.113529'),
 (4,'Préstamo Empresa','fijo',0,'todos','no','2026-04-11 17:14:14.113529'),
 (5,'Cooperativa','fijo',0,'todos','no','2026-04-11 17:14:14.113530'),
 (6,'Embargo','porcentaje',0,'todos','no','2026-04-11 17:14:14.113531'),
 (7,'Seguro Médico','fijo',0,'todos','no','2026-04-11 17:14:14.113532'),
 (8,'Ahorro Voluntario','porcentaje',0,'todos','no','2026-04-11 17:14:14.113533');
COMMIT;
