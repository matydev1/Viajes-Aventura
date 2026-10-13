"""Capa genérica de acceso a SQLite: CRUD reutilizable y seguro."""
import sqlite3


class BaseDeDatos:
    """Clase genérica que centraliza las consultas SQL parametrizadas."""

    def __init__(self, ruta_bd="viajes_aventura.db"):
        self.ruta_bd = ruta_bd

    # ---------- Conexión ----------
    def _conectar(self):
        conexion = sqlite3.connect(self.ruta_bd)
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON;")
        return conexion

    def inicializar_tablas(self, tablas):
        """Recibe una lista de sentencias CREATE TABLE IF NOT EXISTS."""
        with self._conectar() as conexion:
            for sentencia in tablas:
                conexion.execute(sentencia)

    # ---------- CREATE ----------
    def crear(self, tabla, datos: dict):
        columnas = ", ".join(datos.keys())
        placeholders = ", ".join("?" * len(datos))
        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
        try:
            with self._conectar() as conexion:
                cursor = conexion.execute(query, list(datos.values()))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    # ---------- READ ----------
    def leer(self, tabla, columnas="*", condicion="", parametros=(), orden=""):
        query = f"SELECT {columnas} FROM {tabla}"
        if condicion:
            query += f" WHERE {condicion}"
        if orden:
            query += f" ORDER BY {orden}"
        with self._conectar() as conexion:
            filas = conexion.execute(query, parametros).fetchall()
            return [dict(f) for f in filas]

    def leer_uno(self, tabla, columnas="*", condicion="", parametros=()):
        filas = self.leer(tabla, columnas, condicion, parametros)
        return filas[0] if filas else None

    def consulta_libre(self, query, parametros=()):
        """Para JOIN o agregaciones que no encajan en el CRUD básico."""
        with self._conectar() as conexion:
            filas = conexion.execute(query, parametros).fetchall()
            return [dict(f) for f in filas]

    def existe(self, tabla, condicion, parametros=()):
        resultado = self.leer(tabla, "1", condicion, parametros)
        return len(resultado) > 0

    def contar(self, tabla, condicion="", parametros=()):
        query = f"SELECT COUNT(*) AS total FROM {tabla}"
        if condicion:
            query += f" WHERE {condicion}"
        with self._conectar() as conexion:
            return conexion.execute(query, parametros).fetchone()["total"]

    # ---------- UPDATE ----------
    def actualizar(self, tabla, datos: dict, condicion="", parametros=()):
        asignaciones = ", ".join(f"{clave}=?" for clave in datos.keys())
        query = f"UPDATE {tabla} SET {asignaciones}"
        if condicion:
            query += f" WHERE {condicion}"
        valores = list(datos.values()) + list(parametros)
        try:
            with self._conectar() as conexion:
                cursor = conexion.execute(query, valores)
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False

    # ---------- DELETE ----------
    def eliminar(self, tabla, condicion="", parametros=()):
        query = f"DELETE FROM {tabla}"
        if condicion:
            query += f" WHERE {condicion}"
        with self._conectar() as conexion:
            cursor = conexion.execute(query, parametros)
            return cursor.rowcount > 0