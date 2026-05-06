# Informe del Sistema de Nomina RD

## 1. Descripcion general

El proyecto actual es un **Sistema de Nomina para Republica Dominicana** construido con **Flask**, **SQLAlchemy**, **SQLite**, **Bootstrap** y JavaScript.

Su objetivo es administrar el ciclo basico de nomina de una empresa: usuarios, empleados, departamentos, cargos, deducciones, descuentos individuales, periodos de pago, calculo de nomina, procesamiento, recibos y reportes.

El sistema funciona como una aplicacion web completa servida desde Flask. El backend expone endpoints REST y el frontend consume esos endpoints desde una interfaz web incluida en `templates/index.html`.

## 2. Archivos principales

| Archivo | Funcion |
|---|---|
| `app.py` | Contiene la configuracion Flask, rutas API, autenticacion, calculo de deducciones, procesamiento de nomina y reportes. |
| `models.py` | Define los modelos de la base de datos con SQLAlchemy. |
| `templates/index.html` | Contiene toda la interfaz web: login, dashboard, formularios, tablas, recibos y reportes. |
| `seed.py` | Carga datos iniciales de ejemplo para probar y presentar el sistema. |
| `nominard.db` | Base de datos SQLite actual del sistema. |
| `nominard.db.sql` | Script SQL con la estructura y datos base. |
| `requirements.txt` | Dependencias necesarias para ejecutar el proyecto. |

## 3. Tecnologias utilizadas

| Tecnologia | Uso en el sistema |
|---|---|
| Flask | Servidor web y API REST. |
| Flask-SQLAlchemy | ORM para manejar la base de datos desde Python. |
| Flask-Cors | Soporte para peticiones CORS. |
| SQLite | Base de datos local. |
| Bootstrap | Estilos visuales y componentes responsive. |
| Bootstrap Icons | Iconos de la interfaz. |
| JavaScript | Logica del frontend, consumo de API y actualizacion dinamica de pantallas. |

## 4. Arquitectura general

El sistema esta organizado en tres capas principales:

1. **Backend**

   Implementado en `app.py`. Maneja autenticacion, reglas de negocio, rutas API, calculos de nomina, recibos y reportes.

2. **Modelo de datos**

   Implementado en `models.py`. Define las tablas, columnas y relaciones del sistema.

3. **Frontend**

   Implementado en `templates/index.html`. Presenta la interfaz de usuario y consume los endpoints del backend mediante funciones JavaScript.

## 5. Modulo de autenticacion

El sistema incluye autenticacion por sesion.

### Funciones disponibles

- Registrar usuario.
- Iniciar sesion.
- Cerrar sesion.
- Solicitar recuperacion de contrasena.
- Restablecer contrasena con token temporal.
- Consultar la sesion actual.

### Endpoints principales

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/api/auth/session` | Consulta si existe una sesion activa. |
| `POST` | `/api/auth/register` | Crea un usuario nuevo. |
| `POST` | `/api/auth/login` | Inicia sesion. |
| `POST` | `/api/auth/logout` | Cierra sesion. |
| `POST` | `/api/auth/forgot-password` | Genera un token temporal de recuperacion. |
| `POST` | `/api/auth/reset-password` | Cambia la contrasena usando el token. |

### Proteccion de la API

El backend usa `before_request` para proteger las rutas `/api/*`.

Todas las rutas de la API requieren sesion iniciada, excepto las rutas de autenticacion que empiezan con `/api/auth/`.

Esto evita que usuarios no autenticados accedan a empleados, departamentos, nominas o reportes.

## 6. Modulo dashboard

El dashboard es la pantalla inicial del sistema despues del inicio de sesion.

### Informacion que muestra

- Total de empleados activos.
- Masa salarial.
- Total de departamentos.
- Cantidad de nominas procesadas.
- Empleados registrados recientemente.

### Endpoint utilizado

| Metodo | Ruta |
|---|---|
| `GET` | `/api/dashboard` |

Este modulo sirve como resumen ejecutivo para Recursos Humanos o administracion.

## 7. Modulo departamentos

Este modulo administra las areas internas de la empresa.

### Funciones

- Listar departamentos.
- Crear departamentos.
- Editar departamentos.
- Eliminar departamentos.

### Campos principales

| Campo | Descripcion |
|---|---|
| `nombre` | Nombre del departamento. |
| `codigo` | Codigo unico del departamento. |
| `descripcion` | Descripcion breve del area. |
| `creado_en` | Fecha de creacion del registro. |

### Regla importante

No se puede eliminar un departamento si tiene empleados asignados.

### Endpoints

| Metodo | Ruta |
|---|---|
| `GET` | `/api/departamentos` |
| `POST` | `/api/departamentos` |
| `PUT` | `/api/departamentos/<id>` |
| `DELETE` | `/api/departamentos/<id>` |

## 8. Modulo cargos

Este modulo administra los puestos laborales dentro de cada departamento.

### Funciones

- Listar cargos.
- Filtrar cargos por departamento.
- Crear cargos.
- Editar cargos.
- Eliminar cargos.

### Campos principales

| Campo | Descripcion |
|---|---|
| `nombre` | Nombre del cargo. |
| `dept_id` | Departamento al que pertenece. |
| `nivel` | Nivel jerarquico del cargo. |
| `sal_base` | Salario base sugerido. |
| `sal_max` | Salario maximo sugerido. |

### Niveles utilizados

- `operativo`
- `tecnico`
- `supervisorio`
- `gerencial`
- `directivo`

### Regla importante

No se puede eliminar un cargo si tiene empleados asignados.

## 9. Modulo empleados

El modulo de empleados es uno de los componentes centrales del sistema.

Permite registrar y mantener la informacion laboral de cada trabajador.

### Funciones

- Listar empleados.
- Buscar empleados por nombre, apellido, cedula o correo.
- Filtrar empleados por estado.
- Ver datos de un empleado.
- Crear empleado.
- Editar empleado.
- Eliminar empleado.

### Campos principales

| Campo | Descripcion |
|---|---|
| `nombres` | Nombres del empleado. |
| `apellidos` | Apellidos del empleado. |
| `cedula` | Documento unico de identidad. |
| `telefono` | Telefono de contacto. |
| `email` | Correo electronico. |
| `direccion` | Direccion del empleado. |
| `ingreso` | Fecha de ingreso a la empresa. |
| `dept_id` | Departamento asignado. |
| `cargo_id` | Cargo asignado. |
| `tipo` | Tipo de empleado. |
| `salario` | Salario mensual. |
| `estado` | Estado laboral. |

### Estados posibles

- `activo`
- `inactivo`
- `suspendido`

### Tipos de empleado

- `fijo`
- `por_hora`
- `temporal`

### Regla importante

La cedula es unica. El sistema valida que no se registre una cedula duplicada.

## 10. Modulo tipos de deduccion

Este modulo funciona como catalogo global de deducciones.

### Ejemplos de tipos de deduccion

- AFP Empleado.
- SFS Empleado.
- ISR.
- Prestamo Empresa.
- Cooperativa.
- Embargo.
- Seguro Medico.
- Ahorro Voluntario.

### Campos principales

| Campo | Descripcion |
|---|---|
| `nombre` | Nombre de la deduccion. |
| `tipo` | Define si se calcula por porcentaje o monto fijo. |
| `valor` | Porcentaje o monto de referencia. |
| `aplica` | Tipo de empleado al que aplica. |
| `obligatoria` | Indica si se aplica automaticamente en nomina. |

### Tipos de calculo

- `porcentaje`
- `fijo`

### Ambito de aplicacion

- `todos`
- `fijo`
- `por_hora`

Las deducciones obligatorias se aplican automaticamente al calcular la nomina.

## 11. Modulo descuentos por empleado

Este modulo permite asignar descuentos especificos a empleados concretos.

### Funciones

- Listar descuentos.
- Filtrar descuentos por empleado.
- Crear descuento.
- Editar descuento.
- Eliminar descuento.
- Activar o pausar descuento.

### Campos principales

| Campo | Descripcion |
|---|---|
| `emp_id` | Empleado al que se le aplica el descuento. |
| `tipo_id` | Tipo de deduccion relacionado. Puede ser nulo. |
| `nombre` | Concepto o descripcion del descuento. |
| `tipo_val` | Tipo de valor: fijo o porcentaje. |
| `valor` | Monto o porcentaje del descuento. |
| `inicio` | Fecha de inicio. |
| `fin` | Fecha de fin. |
| `cuotas` | Cantidad de cuotas. |
| `activo` | Indica si el descuento esta activo. |
| `obs` | Observaciones. |

### Reglas importantes

- Solo se aplican descuentos activos.
- Si un descuento tiene fecha de fin vencida, no se aplica.
- Si un descuento se pausa y no tenia fecha de fin, el sistema coloca la fecha actual como fecha de fin.

## 12. Modulo periodos

El periodo representa el rango de tiempo para calcular una nomina.

### Funciones

- Crear periodo.
- Editar periodo.
- Eliminar periodo.
- Listar periodos.
- Enviar un periodo abierto al modulo de nomina.

### Campos principales

| Campo | Descripcion |
|---|---|
| `nombre` | Nombre del periodo, por ejemplo "Marzo 2025". |
| `tipo` | Tipo de periodo. |
| `inicio` | Fecha inicial. |
| `fin` | Fecha final. |
| `dias` | Dias laborables usados para el calculo. |
| `estado` | Estado del periodo. |

### Tipos de periodo

- `mensual`
- `quincenal`
- `semanal`

### Estados posibles

- `abierto`
- `procesado`
- `cerrado`

### Formula base del periodo

El salario calculado del periodo usa la siguiente formula:

```text
salario_calculado = salario_mensual / 23 * dias_del_periodo
```

El sistema toma 23 dias como base laboral mensual.

## 13. Modulo nomina

El modulo de nomina permite calcular y procesar la nomina de los empleados activos.

### 13.1 Calcular nomina

El calculo de nomina no guarda informacion definitiva. Sirve para revisar los montos antes de procesar.

### Informacion generada por empleado

- Empleado.
- Departamento.
- Salario base.
- Dias del periodo.
- Salario calculado.
- Deducciones obligatorias.
- Descuentos individuales.
- Total descontado.
- Salario neto.

### Totales generados

- Total bruto.
- Total de descuentos.
- Total neto.

### Endpoint

| Metodo | Ruta |
|---|---|
| `POST` | `/api/nomina/calcular` |

### 13.2 Procesar nomina

El procesamiento guarda la nomina definitivamente.

Cuando se procesa una nomina:

1. Se obtiene el periodo seleccionado.
2. Se validan los empleados activos.
3. Se calcula el salario de cada empleado.
4. Se calculan deducciones obligatorias.
5. Se calculan descuentos individuales.
6. Se calcula el salario neto.
7. Se crea un registro en `nominas`.
8. Se crean registros por empleado en `nominas_detalle`.
9. El periodo queda marcado como `procesado`.

### Endpoint

| Metodo | Ruta |
|---|---|
| `POST` | `/api/nomina/procesar` |

### Regla importante

Si ya existe una nomina para el periodo, el sistema elimina la anterior y genera una nueva. Esto permite reprocesar la nomina antes de cerrarla definitivamente.

## 14. Calculo de deducciones

El sistema maneja dos grupos de deducciones:

1. **Deducciones obligatorias**
2. **Descuentos individuales**

### 14.1 Deducciones obligatorias

Las deducciones obligatorias se toman desde la tabla `tipos_deduccion`, filtrando los registros donde `obligatoria = "si"`.

Ejemplos:

- AFP Empleado.
- SFS Empleado.
- ISR.

### 14.2 Calculo de ISR

El ISR se calcula con una escala anual incluida en el backend:

| Rango anual | Calculo |
|---|---|
| Hasta RD$416,220 | No paga ISR. |
| De RD$416,220 a RD$624,329 | 15% sobre el excedente. |
| De RD$624,329 a RD$867,123 | RD$31,216 mas 20% sobre el excedente. |
| Sobre RD$867,123 | RD$79,776 mas 25% sobre el excedente. |

Luego el ISR anual se divide entre 12 para obtener el monto mensual.

```text
ISR_mensual = ISR_anual / 12
```

### 14.3 Descuentos individuales

Los descuentos individuales se obtienen desde `descuentos_empleado`.

Se aplican cuando:

- El descuento esta activo.
- No tiene fecha de fin vencida.
- El monto calculado es mayor que cero.

## 15. Modulo recibo de pago

El recibo de pago permite generar un comprobante para un empleado en un periodo especifico.

### Informacion incluida

- Datos del empleado.
- Cedula.
- Cargo.
- Departamento.
- Periodo.
- Fecha de inicio y fin.
- Salario mensual.
- Salario calculado.
- Deducciones obligatorias.
- Descuentos individuales.
- Total descontado.
- Salario neto a pagar.

### Endpoint

| Metodo | Ruta |
|---|---|
| `GET` | `/api/nomina/recibo?emp_id=N&periodo_id=N` |

La interfaz tambien permite imprimir el recibo desde el navegador.

## 16. Modulo reportes

El sistema incluye reportes para analisis administrativo y salarial.

### 16.1 Reporte resumen

Muestra:

- Empleados activos.
- Masa salarial.
- Salario promedio.
- Total de departamentos.
- Tipos de deduccion.
- Descuentos activos.
- Nominas procesadas.
- Distribucion de empleados por estado.

Endpoint:

| Metodo | Ruta |
|---|---|
| `GET` | `/api/reportes/resumen` |

### 16.2 Reporte por departamento

Muestra por departamento:

- Cantidad de empleados.
- Total salarial.
- Salario promedio.
- Porcentaje dentro de la masa salarial total.

Endpoint:

| Metodo | Ruta |
|---|---|
| `GET` | `/api/reportes/por-departamento` |

### 16.3 Reporte por empleado

Muestra por empleado:

- Nombre.
- Departamento.
- Cargo.
- Salario.
- Deducciones obligatorias.
- Descuentos individuales.
- Neto estimado.

Endpoint:

| Metodo | Ruta |
|---|---|
| `GET` | `/api/reportes/por-empleado?q=texto` |

## 17. Modelos de la base de datos

La base de datos contiene 9 tablas principales.

## 17.1 Tabla `usuarios`

Guarda los usuarios que pueden acceder al sistema.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `nombre` | Nombre del usuario. |
| `email` | Correo unico. |
| `password_hash` | Contrasena cifrada. |
| `reset_token` | Token temporal para recuperar contrasena. |
| `reset_expira` | Fecha y hora de expiracion del token. |
| `activo` | Indica si el usuario esta activo. |
| `creado_en` | Fecha de creacion. |

## 17.2 Tabla `departamentos`

Representa las areas de la empresa.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `nombre` | Nombre unico del departamento. |
| `codigo` | Codigo unico del departamento. |
| `descripcion` | Descripcion del area. |
| `creado_en` | Fecha de creacion. |

Relaciones:

- Un departamento tiene muchos cargos.
- Un departamento tiene muchos empleados.

## 17.3 Tabla `cargos`

Representa los puestos laborales.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `nombre` | Nombre del cargo. |
| `dept_id` | Departamento al que pertenece. |
| `nivel` | Nivel jerarquico. |
| `sal_base` | Salario base. |
| `sal_max` | Salario maximo. |
| `creado_en` | Fecha de creacion. |

Relaciones:

- Un cargo pertenece a un departamento.
- Un cargo puede tener muchos empleados.

## 17.4 Tabla `empleados`

Almacena la ficha del trabajador.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `nombres` | Nombres del empleado. |
| `apellidos` | Apellidos del empleado. |
| `cedula` | Cedula unica. |
| `telefono` | Telefono. |
| `email` | Correo. |
| `direccion` | Direccion. |
| `ingreso` | Fecha de ingreso. |
| `dept_id` | Departamento asignado. |
| `cargo_id` | Cargo asignado. |
| `tipo` | Tipo de empleado. |
| `salario` | Salario mensual. |
| `estado` | Estado laboral. |
| `creado_en` | Fecha de creacion. |

Relaciones:

- Un empleado pertenece a un departamento.
- Un empleado pertenece a un cargo.
- Un empleado puede tener muchos descuentos.
- Un empleado puede aparecer en muchos detalles de nomina.

## 17.5 Tabla `tipos_deduccion`

Define el catalogo de deducciones.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `nombre` | Nombre unico de la deduccion. |
| `tipo` | Porcentaje o fijo. |
| `valor` | Valor de referencia. |
| `aplica` | Tipo de empleado al que aplica. |
| `obligatoria` | Indica si se aplica automaticamente. |
| `creado_en` | Fecha de creacion. |

Relaciones:

- Un tipo de deduccion puede asociarse a muchos descuentos individuales.

## 17.6 Tabla `descuentos_empleado`

Representa descuentos asignados a empleados especificos.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `emp_id` | Empleado afectado. |
| `tipo_id` | Tipo de deduccion relacionado. |
| `nombre` | Concepto del descuento. |
| `tipo_val` | Fijo o porcentaje. |
| `valor` | Monto o porcentaje. |
| `inicio` | Fecha de inicio. |
| `fin` | Fecha de fin. |
| `cuotas` | Cantidad de cuotas. |
| `activo` | Indica si esta activo. |
| `obs` | Observaciones. |
| `creado_en` | Fecha de creacion. |

Relaciones:

- Un descuento pertenece a un empleado.
- Un descuento puede estar asociado a un tipo de deduccion.

## 17.7 Tabla `periodos`

Define los periodos de pago.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `nombre` | Nombre del periodo. |
| `tipo` | Mensual, quincenal o semanal. |
| `inicio` | Fecha inicial. |
| `fin` | Fecha final. |
| `dias` | Dias laborables. |
| `estado` | Abierto, procesado o cerrado. |
| `creado_en` | Fecha de creacion. |

Relaciones:

- Un periodo puede tener muchas nominas.

## 17.8 Tabla `nominas`

Representa el encabezado de una nomina procesada.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `periodo_id` | Periodo procesado. |
| `total_emps` | Cantidad de empleados incluidos. |
| `total_bruto` | Total bruto calculado. |
| `total_neto` | Total neto a pagar. |
| `fecha_proc` | Fecha de procesamiento. |
| `estado` | Estado de la nomina. |
| `creado_en` | Fecha de creacion. |

Relaciones:

- Una nomina pertenece a un periodo.
- Una nomina tiene muchos detalles.

## 17.9 Tabla `nominas_detalle`

Representa el detalle de nomina por empleado.

| Campo | Descripcion |
|---|---|
| `id` | Identificador unico. |
| `nomina_id` | Nomina a la que pertenece. |
| `emp_id` | Empleado incluido. |
| `salario_base` | Salario mensual registrado. |
| `dias` | Dias calculados. |
| `sal_calculado` | Salario proporcional del periodo. |
| `bonificacion` | Bonificacion aplicada. |
| `desc_oblig` | Total de deducciones obligatorias. |
| `desc_indiv` | Total de descuentos individuales. |
| `total_desc` | Total descontado. |
| `salario_neto` | Neto a pagar. |

Relaciones:

- Un detalle pertenece a una nomina.
- Un detalle pertenece a un empleado.

## 18. Relaciones principales de la base de datos

```text
Departamento 1 ---- N Cargo
Departamento 1 ---- N Empleado
Cargo        1 ---- N Empleado
Empleado     1 ---- N DescuentoEmpleado
TipoDeduccion 1 --- N DescuentoEmpleado
Periodo      1 ---- N Nomina
Nomina       1 ---- N NominaDetalle
Empleado     1 ---- N NominaDetalle
```

## 19. Datos actuales de la base

Segun la base `nominard.db` actual:

| Tabla | Cantidad |
|---|---:|
| `usuarios` | 2 |
| `departamentos` | 5 |
| `cargos` | 8 |
| `empleados` | 7 |
| `tipos_deduccion` | 8 |
| `descuentos_empleado` | 3 |
| `periodos` | 3 |
| `nominas` | 1 |
| `nominas_detalle` | 7 |

### Estado de empleados

| Estado | Cantidad |
|---|---:|
| Activo | 7 |

### Estado de periodos

| Estado | Cantidad |
|---|---:|
| Cerrado | 2 |
| Procesado | 1 |

Esto indica que la base actual contiene una nomina procesada para los 7 empleados registrados.

## 20. Flujo principal del sistema

Para presentar el sistema, se recomienda explicar el flujo de esta manera:

1. El usuario inicia sesion.
2. Entra al dashboard y observa el resumen general.
3. Configura departamentos.
4. Configura cargos.
5. Registra empleados.
6. Define deducciones obligatorias y opcionales.
7. Asigna descuentos individuales cuando aplica.
8. Crea un periodo de nomina.
9. Calcula la nomina.
10. Revisa el detalle de bruto, descuentos y neto.
11. Procesa la nomina.
12. Consulta el historial.
13. Genera recibos de pago.
14. Revisa reportes generales, por departamento y por empleado.

## 21. Fortalezas del sistema

- Tiene autenticacion y proteccion de API.
- Usa una estructura de datos clara y relacional.
- Centraliza departamentos, cargos, empleados y deducciones.
- Calcula nomina automaticamente.
- Maneja deducciones obligatorias como AFP, SFS e ISR.
- Permite descuentos individuales personalizados.
- Genera recibos de pago.
- Incluye reportes utiles para Recursos Humanos.
- Tiene datos demo para pruebas y presentacion.
- La interfaz esta integrada en una sola aplicacion web.

## 22. Mejoras futuras recomendadas

- Enviar el token de recuperacion por correo electronico real.
- Mover `SECRET_KEY` a una variable de entorno.
- Agregar roles y permisos, por ejemplo Administrador y Recursos Humanos.
- Agregar auditoria de cambios.
- Versionar nominas reprocesadas en vez de eliminar la anterior.
- Agregar exportacion a PDF o Excel.
- Agregar validaciones legales mas completas para topes de AFP, SFS e ISR.
- Migrar de SQLite a PostgreSQL o MySQL para uso empresarial.

## 23. Conclusion

El Sistema de Nomina RD es una aplicacion funcional que cubre el flujo completo de gestion de nomina: configuracion organizacional, registro de empleados, deducciones, descuentos, periodos, calculo, procesamiento, recibos y reportes.

Para una presentacion, el sistema puede explicarse como una solucion integral para Recursos Humanos, donde el usuario configura la estructura de la empresa, registra los colaboradores, procesa la nomina y obtiene informacion final para analisis y pago.
