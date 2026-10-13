"""Capa de dominio: autenticación, destinos, paquetes y reservas."""
import hashlib
import secrets
from datetime import datetime
from dbmodel import BaseDeDatos
from modelos import Cliente, Administrador, Destino, Paquete, Reserva

TABLAS = [
    """CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        nombre_usuario TEXT UNIQUE NOT NULL,
        rut TEXT NOT NULL,
        hash TEXT NOT NULL,
        sal TEXT NOT NULL,
        rol TEXT NOT NULL CHECK (rol IN ('administrador','cliente'))
    )""",
    """CREATE TABLE IF NOT EXISTS destinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        pais TEXT NOT NULL,
        costo_diario REAL NOT NULL CHECK (costo_diario > 0)
    )""",
    """CREATE TABLE IF NOT EXISTS paquetes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        precio_base REAL NOT NULL CHECK (precio_base >= 0),
        fecha_inicio TEXT NOT NULL,
        fecha_termino TEXT NOT NULL,
        cupos INTEGER NOT NULL CHECK (cupos > 0)
    )""",
    """CREATE TABLE IF NOT EXISTS paquete_destinos (
        id_paquete INTEGER NOT NULL,
        id_destino INTEGER NOT NULL,
        PRIMARY KEY (id_paquete, id_destino),
        FOREIGN KEY (id_paquete) REFERENCES paquetes(id) ON DELETE CASCADE,
        FOREIGN KEY (id_destino) REFERENCES destinos(id)
    )""",
    """CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER NOT NULL,
        id_paquete INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        estado TEXT NOT NULL CHECK (estado IN ('confirmada','cancelada')),
        FOREIGN KEY (id_cliente) REFERENCES usuarios(id),
        FOREIGN KEY (id_paquete) REFERENCES paquetes(id)
    )""",
]


class Database:
    def __init__(self, ruta="viajes_aventura.db"):
        self.bd = BaseDeDatos(ruta)
        self.bd.inicializar_tablas(TABLAS)

    def hay_administrador(self):
        return self.bd.contar("usuarios", "rol=?", ("administrador",)) > 0

    @staticmethod
    def _hashear(clave, sal):
        return hashlib.sha256((sal + clave).encode()).hexdigest()

    def crear_usuario(self, nombre, usuario, rut, clave, rol):
        sal = secrets.token_hex(8)
        return self.bd.crear("usuarios", {
            "nombre": nombre, "nombre_usuario": usuario,
            "rut": rut, "hash": self._hashear(clave, sal),
            "sal": sal, "rol": rol,
        })

    def autenticar(self, usuario, clave):
        row = self.bd.leer_uno("usuarios", condicion="nombre_usuario=?", parametros=(usuario,))
        if row and self._hashear(clave, row["sal"]) == row["hash"]:
            return row
        return None

    # Métodos convertidores opcionales a Clases UML
    def obtener_usuario_objeto(self, id_usuario):
        row = self.bd.leer_uno("usuarios", condicion="id=?", parametros=(id_usuario,))
        if not row:
            return None
        if row["rol"] == "administrador":
            return Administrador(row["id"], row["nombre"], row["nombre_usuario"], row["rut"])
        return Cliente(row["id"], row["nombre"], row["nombre_usuario"], row["rut"])

    def crear_destino(self, nombre, pais, costo):
        return self.bd.crear("destinos", {"nombre": nombre, "pais": pais, "costo_diario": float(costo)})

    def listar_destinos(self):
        return self.bd.leer("destinos", orden="nombre")

    def listar_destinos_objetos(self):
        return [Destino(d["id"], d["nombre"], d["pais"], d["costo_diario"]) for d in self.listar_destinos()]

    def obtener_destino(self, id_destino):
        return self.bd.leer_uno("destinos", condicion="id=?", parametros=(id_destino,))

    def modificar_destino(self, id_destino, nombre, pais, costo):
        return self.bd.actualizar("destinos", {"nombre": nombre, "pais": pais, "costo_diario": float(costo)}, "id=?", (id_destino,))

    def eliminar_destino(self, id_destino):
        if self.bd.contar("paquete_destinos", "id_destino=?", (id_destino,)) > 0:
            return False
        return self.bd.eliminar("destinos", "id=?", (id_destino,))

    def crear_paquete(self, nombre, precio_base, fi, ft, cupos, destinos_ids):
        id_paquete = self.bd.crear("paquetes", {
            "nombre": nombre, "precio_base": float(precio_base),
            "fecha_inicio": fi, "fecha_termino": ft, "cupos": int(cupos),
        })
        if not id_paquete:
            return None
        for idd in destinos_ids:
            self.bd.crear("paquete_destinos", {"id_paquete": id_paquete, "id_destino": idd})
        return id_paquete

    def listar_paquetes(self):
        return self.bd.consulta_libre("""
            SELECT p.*, (
                SELECT COUNT(*) FROM reservas r
                WHERE r.id_paquete = p.id AND r.estado = 'confirmada'
            ) AS reservas_activas
            FROM paquetes p
            ORDER BY p.nombre
        """)

    def obtener_paquete(self, id_paquete):
        paquete = self.bd.leer_uno("paquetes", condicion="id=?", parametros=(id_paquete,))
        if not paquete:
            return None
        paquete["destinos"] = self.bd.consulta_libre("""
            SELECT d.* FROM destinos d
            JOIN paquete_destinos pd ON pd.id_destino = d.id
            WHERE pd.id_paquete = ?
        """, (id_paquete,))
        return paquete

    def modificar_paquete(self, id_p, nombre, precio, fi, ft, cupos, destinos_ids):
        ok = self.bd.actualizar("paquetes", {
            "nombre": nombre, "precio_base": float(precio),
            "fecha_inicio": fi, "fecha_termino": ft, "cupos": int(cupos),
        }, "id=?", (id_p,))
        if not ok:
            return False
        self.bd.eliminar("paquete_destinos", "id_paquete=?", (id_p,))
        for idd in destinos_ids:
            self.bd.crear("paquete_destinos", {"id_paquete": id_p, "id_destino": idd})
        return True

    def eliminar_paquete(self, id_p):
        if self.bd.contar("reservas", "id_paquete=?", (id_p,)) > 0:
            return False
        self.bd.eliminar("paquete_destinos", "id_paquete=?", (id_p,))
        return self.bd.eliminar("paquetes", "id=?", (id_p,))

    def crear_reserva(self, id_cliente, id_paquete):
        paquete = self.bd.leer_uno("paquetes", condicion="id=?", parametros=(id_paquete,))
        if not paquete:
            return False, "El paquete no existe."

        activas = self.bd.contar("reservas", "id_paquete=? AND estado='confirmada'", (id_paquete,))
        if activas >= paquete["cupos"]:
            return False, "No hay cupos disponibles."

        duplicada = self.bd.contar("reservas", "id_cliente=? AND id_paquete=? AND estado='confirmada'", (id_cliente, id_paquete))
        if duplicada > 0:
            return False, "Ya tienes una reserva para este paquete."

        self.bd.crear("reservas", {
            "id_cliente": id_cliente, "id_paquete": id_paquete,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "estado": "confirmada",
        })
        return True, "Reserva confirmada."

    def listar_reservas_cliente(self, id_cliente):
        return self.bd.consulta_libre("""
            SELECT r.*, p.nombre AS paquete_nombre
            FROM reservas r
            JOIN paquetes p ON p.id = r.id_paquete
            WHERE r.id_cliente = ?
            ORDER BY r.fecha DESC
        """, (id_cliente,))

    def listar_todas_reservas(self):
        return self.bd.consulta_libre("""
            SELECT r.*, p.nombre AS paquete_nombre, u.nombre AS cliente
            FROM reservas r
            JOIN paquetes p ON p.id = r.id_paquete
            JOIN usuarios u ON u.id = r.id_cliente
            ORDER BY r.fecha DESC
        """)

    def listar_reservas_filtradas(self, estado="", busqueda=""):
        condiciones, parametros = [], []
        if estado and estado.lower() != "todas":
            condiciones.append("r.estado = ?")
            parametros.append(estado.lower())
        if busqueda:
            condiciones.append("(u.nombre LIKE ? OR p.nombre LIKE ?)")
            like = f"%{busqueda}%"
            parametros.extend([like, like])
        where = "WHERE " + " AND ".join(condiciones) if condiciones else ""
        return self.bd.consulta_libre(f"""
            SELECT r.*, p.nombre AS paquete_nombre, u.nombre AS cliente
            FROM reservas r
            JOIN paquetes p ON p.id = r.id_paquete
            JOIN usuarios u ON u.id = r.id_cliente
            {where}
            ORDER BY r.fecha DESC
        """, tuple(parametros))

    def cancelar_reserva(self, id_reserva):
        return self.bd.actualizar("reservas", {"estado": "cancelada"}, "id=?", (id_reserva,))

    def reactivar_reserva(self, id_reserva):
        reserva = self.bd.leer_uno("reservas", condicion="id=?", parametros=(id_reserva,))
        if not reserva:
            return False, "Reserva no encontrada."
        if reserva["estado"] == "confirmada":
            return False, "La reserva ya está activa."

        paquete = self.bd.leer_uno("paquetes", condicion="id=?", parametros=(reserva["id_paquete"],))
        if not paquete:
            return False, "El paquete ya no existe."

        activas = self.bd.contar("reservas", "id_paquete=? AND estado='confirmada'", (reserva["id_paquete"],))
        if activas >= paquete["cupos"]:
            return False, "No hay cupos disponibles para reactivar."

        duplicada = self.bd.contar("reservas", "id_cliente=? AND id_paquete=? AND estado='confirmada'", (reserva["id_cliente"], reserva["id_paquete"]))
        if duplicada > 0:
            return False, "El cliente ya tiene otra reserva activa para este paquete."

        self.bd.actualizar("reservas", {"estado": "confirmada"}, "id=?", (id_reserva,))
        return True, "Reserva reactivada."

    def eliminar_reserva(self, id_reserva):
        return self.bd.eliminar("reservas", "id=?", (id_reserva,))