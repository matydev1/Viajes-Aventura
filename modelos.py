"""Definición de clases de dominio según el diagrama UML."""

class Usuario:
    def __init__(self, id_usuario, nombre, nombre_usuario, rut, rol):
        self.id = id_usuario
        self.nombre = nombre
        self.nombre_usuario = nombre_usuario
        self.rut = rut
        self.rol = rol


class Cliente(Usuario):
    def __init__(self, id_usuario, nombre, nombre_usuario, rut):
        super().__init__(id_usuario, nombre, nombre_usuario, rut, "cliente")


class Administrador(Usuario):
    def __init__(self, id_usuario, nombre, nombre_usuario, rut):
        super().__init__(id_usuario, nombre, nombre_usuario, rut, "administrador")


class Destino:
    def __init__(self, id_destino, nombre, pais, costo_diario):
        self.id = id_destino
        self.nombre = nombre
        self.pais = pais
        self.costo_diario = costo_diario


class Paquete:
    def __init__(self, id_paquete, nombre, precio_base, fecha_inicio, fecha_termino, cupos, destinos=None):
        self.id = id_paquete
        self.nombre = nombre
        self.precio_base = precio_base
        self.fecha_inicio = fecha_inicio
        self.fecha_termino = fecha_termino
        self.cupos = cupos
        self.destinos = destinos or []


class Reserva:
    def __init__(self, id_reserva, id_cliente, id_paquete, fecha, estado, cliente=None, paquete_nombre=None):
        self.id = id_reserva
        self.id_cliente = id_cliente
        self.id_paquete = id_paquete
        self.fecha = fecha
        self.estado = estado
        self.cliente = cliente
        self.paquete_nombre = paquete_nombre