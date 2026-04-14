# Sistema de Nomina RD

Sistema de nomina para Republica Dominicana construido con Flask, SQLAlchemy, SQLite y una interfaz web en Bootstrap.

## Resumen

El proyecto incluye:

- Gestion de departamentos, cargos y empleados
- Tipos de deduccion y descuentos por empleado
- Periodos, calculo y procesamiento de nomina
- Reportes y recibo de pago
- Autenticacion de usuarios con `login`, `register`, `forgot password` y `reset password`
- Seed de datos de ejemplo actualizado

## Estructura del proyecto

```text
SistemaNomina/
├── app.py
├── models.py
├── seed.py
├── nominard.db
├── nominard.db.sql
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

## Modelos principales

La base de datos contiene estas tablas principales:

- `usuarios`
- `departamentos`
- `cargos`
- `empleados`
- `tipos_deduccion`
- `descuentos_empleado`
- `periodos`
- `nominas`
- `nominas_detalle`

## Instalacion

### 1. Requisitos

- Python 3.9 o superior
- `pip`

### 2. Crear entorno virtual

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Inicializar la base de datos

Para crear o resembrar la base con datos de ejemplo:

```bash
python seed.py
```

`seed.py` ahora limpia los datos principales antes de insertar de nuevo, para evitar duplicados al re-ejecutarlo.

### Datos demo creados por el seed

- 2 usuarios
- 5 departamentos
- 8 cargos
- 8 tipos de deduccion
- 7 empleados
- 3 descuentos individuales
- 3 periodos

### Usuarios demo

| Correo | Clave |
|---|---|
| `admin@nomina.local` | `admin123` |
| `rrhh@nomina.local` | `rrhh123` |

## Ejecutar la aplicacion

```bash
python app.py
```

Abrir en el navegador:

```text
http://localhost:5000
```

## Flujo de autenticacion

La aplicacion ahora protege las rutas `/api/*` y exige sesion iniciada para acceder al sistema.

Funciones disponibles:

- `Login`
- `Register user`
- `Forgot password`
- `Reset password`
- `Logout`

### Recuperacion de contrasena

El flujo actual genera un token temporal desde la UI. Como el proyecto aun no envia correos, el token se muestra en pantalla para usarlo inmediatamente en el formulario de restablecimiento.

## Endpoints principales

### Auth

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/api/auth/session` | Estado de la sesion actual |
| `POST` | `/api/auth/register` | Crear usuario |
| `POST` | `/api/auth/login` | Iniciar sesion |
| `POST` | `/api/auth/logout` | Cerrar sesion |
| `POST` | `/api/auth/forgot-password` | Generar token de recuperacion |
| `POST` | `/api/auth/reset-password` | Cambiar contrasena con token |

### Departamentos

| Metodo | Ruta |
|---|---|
| `GET` | `/api/departamentos` |
| `POST` | `/api/departamentos` |
| `PUT` | `/api/departamentos/<id>` |
| `DELETE` | `/api/departamentos/<id>` |

### Cargos

| Metodo | Ruta |
|---|---|
| `GET` | `/api/cargos?dept_id=N` |
| `POST` | `/api/cargos` |
| `PUT` | `/api/cargos/<id>` |
| `DELETE` | `/api/cargos/<id>` |

### Empleados

| Metodo | Ruta |
|---|---|
| `GET` | `/api/empleados?q=texto&estado=activo` |
| `GET` | `/api/empleados/<id>` |
| `POST` | `/api/empleados` |
| `PUT` | `/api/empleados/<id>` |
| `DELETE` | `/api/empleados/<id>` |

### Tipos de deduccion

| Metodo | Ruta |
|---|---|
| `GET` | `/api/tipos-deduccion` |
| `POST` | `/api/tipos-deduccion` |
| `PUT` | `/api/tipos-deduccion/<id>` |
| `DELETE` | `/api/tipos-deduccion/<id>` |

### Descuentos

| Metodo | Ruta |
|---|---|
| `GET` | `/api/descuentos?emp_id=N` |
| `POST` | `/api/descuentos` |
| `PUT` | `/api/descuentos/<id>` |
| `DELETE` | `/api/descuentos/<id>` |
| `PATCH` | `/api/descuentos/<id>/toggle` |

### Periodos

| Metodo | Ruta |
|---|---|
| `GET` | `/api/periodos` |
| `POST` | `/api/periodos` |
| `PUT` | `/api/periodos/<id>` |
| `DELETE` | `/api/periodos/<id>` |

### Nomina

| Metodo | Ruta |
|---|---|
| `POST` | `/api/nomina/calcular` |
| `POST` | `/api/nomina/procesar` |
| `GET` | `/api/nomina/historial` |
| `GET` | `/api/nomina/recibo?emp_id=N&periodo_id=N` |

### Reportes

| Metodo | Ruta |
|---|---|
| `GET` | `/api/reportes/resumen` |
| `GET` | `/api/reportes/por-departamento` |
| `GET` | `/api/reportes/por-empleado?q=texto` |

## Cambios recientes

- Se agrego autenticacion de usuarios en backend y frontend
- Se incorporo la tabla `usuarios` en el modelo y en el SQL base
- Se actualizo `seed.py` para crear usuarios demo y permitir re-ejecucion segura
- Se ajusto la UI para mostrar login/registro/recuperacion antes de entrar al sistema
- Se corrigio la logica de tabs para limpiar el contenido anterior al cambiar entre paneles

## Archivo SQL

El archivo [nominard.db.sql](./nominard.db.sql) incluye la estructura actualizada, incluyendo la tabla `usuarios`.

## Comandos utiles

Ejecutar la aplicacion:

```bash
python app.py
```

Resembrar la base:

```bash
python seed.py
```

Compilar y verificar archivos Python:

```bash
python -m py_compile app.py models.py seed.py
```
