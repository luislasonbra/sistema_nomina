"""
seed.py
Pobla la base de datos con datos de ejemplo para empezar a usar el sistema.
Ejecutar: python seed.py
"""
from datetime import date

from werkzeug.security import generate_password_hash

from app import app
from models import (
    db,
    Usuario,
    Departamento,
    Cargo,
    TipoDeduccion,
    Empleado,
    DescuentoEmpleado,
    Periodo,
    Nomina,
    NominaDetalle,
)


def seed():
    with app.app_context():
        # Limpiar datos existentes para poder re-ejecutar el seed sin duplicados.
        NominaDetalle.query.delete()
        Nomina.query.delete()
        DescuentoEmpleado.query.delete()
        Empleado.query.delete()
        Cargo.query.delete()
        Departamento.query.delete()
        TipoDeduccion.query.delete()
        Periodo.query.delete()
        Usuario.query.delete()
        db.session.commit()

        usuarios_data = [
            ("Administrador General", "admin@nomina.local", "admin123"),
            ("Recursos Humanos", "rrhh@nomina.local", "rrhh123"),
        ]
        for nombre, email, password in usuarios_data:
            db.session.add(
                Usuario(
                    nombre=nombre,
                    email=email.lower(),
                    password_hash=generate_password_hash(password),
                    activo="si",
                )
            )
        db.session.flush()

        deptos_data = [
            ("Administracion", "ADM", "Area administrativa general"),
            ("Ventas", "VEN", "Area comercial y ventas"),
            ("Tecnologia", "TEC", "Sistemas e informatica"),
            ("Operaciones", "OPE", "Logistica y operaciones"),
            ("RRHH", "RRH", "Recursos Humanos"),
        ]
        deptos = {}
        for nombre, codigo, desc in deptos_data:
            d = Departamento(nombre=nombre, codigo=codigo, descripcion=desc)
            db.session.add(d)
            deptos[codigo] = d
        db.session.flush()

        cargos_data = [
            ("Gerente General", "ADM", "directivo", 120000, 150000),
            ("Asistente Administrativo", "ADM", "operativo", 25000, 35000),
            ("Gerente de Ventas", "VEN", "gerencial", 80000, 100000),
            ("Vendedor", "VEN", "operativo", 20000, 35000),
            ("Desarrollador Senior", "TEC", "tecnico", 60000, 90000),
            ("Soporte TI", "TEC", "tecnico", 30000, 45000),
            ("Supervisor Operaciones", "OPE", "supervisorio", 45000, 60000),
            ("Analista RRHH", "RRH", "tecnico", 35000, 50000),
        ]
        cargos = {}
        for nombre, dept_cod, nivel, sal_base, sal_max in cargos_data:
            c = Cargo(
                nombre=nombre,
                dept_id=deptos[dept_cod].id,
                nivel=nivel,
                sal_base=sal_base,
                sal_max=sal_max,
            )
            db.session.add(c)
            cargos[nombre] = c
        db.session.flush()

        tipos_data = [
            ("AFP Empleado", "porcentaje", 2.87, "todos", "si"),
            ("SFS Empleado", "porcentaje", 3.04, "todos", "si"),
            ("ISR", "porcentaje", 0, "todos", "si"),
            ("Prestamo Empresa", "fijo", 0, "todos", "no"),
            ("Cooperativa", "fijo", 0, "todos", "no"),
            ("Embargo", "porcentaje", 0, "todos", "no"),
            ("Seguro Medico", "fijo", 0, "todos", "no"),
            ("Ahorro Voluntario", "porcentaje", 0, "todos", "no"),
        ]
        tipos = {}
        for nombre, tipo, valor, aplica, oblig in tipos_data:
            t = TipoDeduccion(
                nombre=nombre,
                tipo=tipo,
                valor=valor,
                aplica=aplica,
                obligatoria=oblig,
            )
            db.session.add(t)
            tipos[nombre] = t
        db.session.flush()

        emps_data = [
            ("Maria", "Gonzalez", "001-1234567-8", "809-555-0001", "maria@emp.com", date(2022, 3, 15), "RRH", "Analista RRHH", "fijo", 35000, "activo"),
            ("Juan", "Perez", "001-2345678-9", "809-555-0002", "juan@emp.com", date(2021, 7, 1), "VEN", "Gerente de Ventas", "fijo", 85000, "activo"),
            ("Carlos", "Martinez", "001-3456789-0", "809-555-0003", "carlos@emp.com", date(2023, 1, 10), "TEC", "Desarrollador Senior", "fijo", 65000, "activo"),
            ("Ana", "Rodriguez", "001-4567890-1", "809-555-0004", "ana@emp.com", date(2020, 9, 20), "ADM", "Gerente General", "fijo", 130000, "activo"),
            ("Luis", "Mendez", "001-5678901-2", "809-555-0005", "luis@emp.com", date(2023, 6, 1), "OPE", "Supervisor Operaciones", "fijo", 48000, "activo"),
            ("Paola", "Santos", "001-6789012-3", "809-555-0006", "paola@emp.com", date(2022, 11, 15), "VEN", "Vendedor", "fijo", 22000, "activo"),
            ("Roberto", "Diaz", "001-7890123-4", "809-555-0007", "roberto@emp.com", date(2024, 1, 2), "TEC", "Soporte TI", "fijo", 32000, "activo"),
        ]
        emps = {}
        for nombres, apellidos, cedula, tel, email, ingreso, dept_cod, cargo_nom, tipo, salario, estado in emps_data:
            e = Empleado(
                nombres=nombres,
                apellidos=apellidos,
                cedula=cedula,
                telefono=tel,
                email=email,
                ingreso=ingreso,
                dept_id=deptos[dept_cod].id,
                cargo_id=cargos[cargo_nom].id,
                tipo=tipo,
                salario=salario,
                estado=estado,
            )
            db.session.add(e)
            emps[cedula] = e
        db.session.flush()

        desc_data = [
            ("001-2345678-9", "Prestamo Empresa", "Prestamo personal ene-2025", "fijo", 3000, date(2025, 1, 1), None, 12, "si", "Aprobado por RRHH"),
            ("001-5678901-2", "Cooperativa", "Cooperativa empleados", "fijo", 1500, date(2024, 6, 1), None, 0, "si", ""),
            ("001-3456789-0", "Embargo", "Embargo judicial", "porcentaje", 10, date(2025, 2, 1), date(2025, 12, 31), 0, "si", "Orden 2024-1234"),
        ]
        for cedula, tipo_nom, concepto, tipo_val, valor, ini, fin, cuotas, activo, obs in desc_data:
            db.session.add(
                DescuentoEmpleado(
                    emp_id=emps[cedula].id,
                    tipo_id=tipos[tipo_nom].id,
                    nombre=concepto,
                    tipo_val=tipo_val,
                    valor=valor,
                    inicio=ini,
                    fin=fin,
                    cuotas=cuotas,
                    activo=activo,
                    obs=obs,
                )
            )

        periodos_data = [
            ("Enero 2025", "mensual", date(2025, 1, 1), date(2025, 1, 31), 23, "cerrado"),
            ("Febrero 2025", "mensual", date(2025, 2, 1), date(2025, 2, 28), 20, "cerrado"),
            ("Marzo 2025", "mensual", date(2025, 3, 1), date(2025, 3, 31), 21, "abierto"),
        ]
        for nombre, tipo, inicio, fin, dias, estado in periodos_data:
            db.session.add(
                Periodo(
                    nombre=nombre,
                    tipo=tipo,
                    inicio=inicio,
                    fin=fin,
                    dias=dias,
                    estado=estado,
                )
            )

        db.session.commit()
        print("Base de datos poblada exitosamente.")
        print(f"   {len(usuarios_data)} usuarios")
        print(f"   {len(deptos_data)} departamentos")
        print(f"   {len(cargos_data)} cargos")
        print(f"   {len(tipos_data)} tipos de deduccion")
        print(f"   {len(emps_data)} empleados")
        print(f"   {len(desc_data)} descuentos individuales")
        print(f"   {len(periodos_data)} periodos")
        print("   Usuarios demo:")
        print("   - admin@nomina.local / admin123")
        print("   - rrhh@nomina.local / rrhh123")


if __name__ == "__main__":
    seed()
