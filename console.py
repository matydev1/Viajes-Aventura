"""Interfaz de consola para Viajes Aventura."""
from database import Database


def _in(msg): return input(msg).strip()


def _in_float(msg):
    while True:
        try: return float(_in(msg))
        except ValueError: print("  Número inválido.")


def _in_int(msg):
    while True:
        try: return int(_in(msg))
        except ValueError: print("  Entero inválido.")


def _crear_admin_inicial(db):
    print("\n=== CREAR ADMINISTRADOR INICIAL ===")
    nombre, usuario = _in("Nombre: "), _in("Usuario: ")
    rut, clave = _in("RUT con guion: "), _in("Clave (mín. 8): ")
    if len(clave) < 8 or "-" not in rut:
        print("Clave o RUT inválidos."); return False
    if db.crear_usuario(nombre, usuario, rut, clave, "administrador"):
        print("Administrador creado."); return True
    print("El usuario ya existe."); return False


def _registrar_cliente(db):
    print("\n=== REGISTRO DE CLIENTE ===")
    nombre = _in("Nombre: ")
    usuario = _in("Usuario: ")
    rut = _in("RUT con guion: ")
    clave = _in("Clave (mín. 8): ")
    if len(clave) < 8 or "-" not in rut:
        print("Clave o RUT inválidos.")
        return
    if db.crear_usuario(nombre, usuario, rut, clave, "cliente"):
        print("Cuenta creada. Ya puedes iniciar sesión.")
    else:
        print("El usuario ya existe.")


def _login(db):
    while True:
        print("\n--- ACCESO ---")
        print("1. Iniciar sesión")
        print("2. Registrarse como cliente")
        print("3. Volver")
        op = _in("Opción: ")

        if op == "1":
            for i in range(3):
                print(f"\n--- Login ({i + 1}/3) ---")
                u = db.autenticar(_in("Usuario: "), _in("Clave: "))
                if u:
                    print(f"Bienvenido, {u['nombre']}.")
                    return u
                print("Usuario o clave incorrectos.")
            print("Demasiados intentos.")
            return None

        elif op == "2":
            _registrar_cliente(db)

        elif op == "3":
            return None
        else:
            print("Opción inválida.")


# ============ MENÚ ADMIN ============
def _menu_destinos(db):
    while True:
        print("\n--- DESTINOS ---\n1.Listar 2.Crear 3.Modificar 4.Eliminar 5.Volver")
        op = _in("Opción: ")
        if op == "1":
            for d in db.listar_destinos():
                print(f"  [{d['id']}] {d['nombre']} - {d['pais']} - ${d['costo_diario']:,.0f}")
        elif op == "2":
            if db.crear_destino(_in("Nombre: "), _in("País: "), _in_float("Costo diario: ")):
                print("Creado.")
            else:
                print("Error: nombre duplicado.")
        elif op == "3":
            idd = _in_int("ID: ")
            d = db.obtener_destino(idd)
            if not d:
                print("No existe."); continue
            n = _in(f"Nombre [{d['nombre']}]: ") or d["nombre"]
            p = _in(f"País [{d['pais']}]: ") or d["pais"]
            c = _in_float(f"Costo [{d['costo_diario']}]: ")
            print("Modificado." if db.modificar_destino(idd, n, p, c) else "Error.")
        elif op == "4":
            print("Eliminado." if db.eliminar_destino(_in_int("ID: "))
                  else "No se pudo (asociado a paquete).")
        elif op == "5":
            return


def _menu_paquetes(db):
    while True:
        print("\n--- PAQUETES ---\n1.Listar 2.Crear 3.Modificar 4.Eliminar 5.Volver")
        op = _in("Opción: ")
        if op == "1":
            for p in db.listar_paquetes():
                libres = p["cupos"] - p["reservas_activas"]
                print(f"  [{p['id']}] {p['nombre']} - base ${p['precio_base']:,.0f} - libres: {libres}")
        elif op == "2":
            _crear_paquete_console(db)
        elif op == "3":
            _modificar_paquete_console(db)
        elif op == "4":
            print("Eliminado." if db.eliminar_paquete(_in_int("ID: "))
                  else "No se pudo (tiene reservas).")
        elif op == "5":
            return


def _seleccionar_destinos(db):
    for d in db.listar_destinos():
        print(f"  [{d['id']}] {d['nombre']} - ${d['costo_diario']:,.0f}")
    ids = _in("IDs separados por coma: ")
    return [int(x) for x in ids.split(",") if x.strip().isdigit()]


def _crear_paquete_console(db):
    if not db.listar_destinos():
        print("Primero cree destinos."); return
    n = _in("Nombre: ")
    pb = _in_float("Precio base: ")
    fi = _in("Fecha inicio (YYYY-MM-DD): ")
    ft = _in("Fecha término: ")
    c = _in_int("Cupos: ")
    print("Destinos disponibles:")
    ids = _seleccionar_destinos(db)
    if not ids:
        print("Seleccione al menos uno."); return
    print("Creado." if db.crear_paquete(n, pb, fi, ft, c, ids) else "Error.")


def _modificar_paquete_console(db):
    idd = _in_int("ID: ")
    p = db.obtener_paquete(idd)
    if not p:
        print("No existe."); return
    n = _in(f"Nombre [{p['nombre']}]: ") or p["nombre"]
    pb = _in_float(f"Precio base [{p['precio_base']}]: ")
    fi = _in(f"Fecha inicio [{p['fecha_inicio']}]: ") or p["fecha_inicio"]
    ft = _in(f"Fecha término [{p['fecha_termino']}]: ") or p["fecha_termino"]
    c = _in_int(f"Cupos [{p['cupos']}]: ")
    print("Destinos:")
    for d in db.listar_destinos():
        print(f"  [{d['id']}] {d['nombre']}")
    actuales = ",".join(str(d["id"]) for d in p["destinos"])
    ids_str = _in(f"IDs [{actuales}]: ") or actuales
    ids = [int(x) for x in ids_str.split(",") if x.strip().isdigit()]
    print("Modificado." if db.modificar_paquete(idd, n, pb, fi, ft, c, ids) else "Error.")


def _ver_reservas_admin(db):
    print("\n--- TODAS LAS RESERVAS ---")
    for r in db.listar_todas_reservas():
        print(f"  [{r['id']}] {r['cliente']} -> {r['paquete_nombre']} - {r['fecha']} - {r['estado']}")


def _menu_admin(db, u):
    while True:
        print(f"\n=== ADMIN ({u['nombre']}) ===\n1.Destinos 2.Paquetes 3.Reservas 4.Cerrar sesión")
        op = _in("Opción: ")
        if op == "1":
            _menu_destinos(db)
        elif op == "2":
            _menu_paquetes(db)
        elif op == "3":
            _ver_reservas_admin(db)
        elif op == "4":
            return


# ============ MENÚ CLIENTE ============
def _menu_cliente(db, u):
    while True:
        print(f"\n=== CLIENTE ({u['nombre']}) ===\n"
              "1.Ver paquetes 2.Reservar 3.Mis reservas 4.Cancelar reserva 5.Cerrar sesión")
        op = _in("Opción: ")
        if op == "1":
            for p in db.listar_paquetes():
                libres = p["cupos"] - p["reservas_activas"]
                det = db.obtener_paquete(p["id"])
                ds = ", ".join(d["nombre"] for d in det["destinos"])
                print(f"  [{p['id']}] {p['nombre']} ({p['fecha_inicio']} - {p['fecha_termino']})")
                print(f"      Destinos: {ds} | base ${p['precio_base']:,.0f} | libres: {libres}")
        elif op == "2":
            ok, msg = db.crear_reserva(u["id"], _in_int("ID paquete: "))
            print(msg)
        elif op == "3":
            rs = db.listar_reservas_cliente(u["id"])
            if not rs:
                print("Sin reservas.")
            for r in rs:
                print(f"  [{r['id']}] {r['paquete_nombre']} - {r['fecha']} - {r['estado']}")
        elif op == "4":
            print("Cancelada." if db.cancelar_reserva(_in_int("ID reserva: ")) else "Error.")
        elif op == "5":
            return


def ejecutar_consola():
    db = Database()
    if not db.hay_administrador() and not _crear_admin_inicial(db):
        return
    u = _login(db)
    if not u:
        return
    if u["rol"] == "administrador":
        _menu_admin(db, u)
    else:
        _menu_cliente(db, u)