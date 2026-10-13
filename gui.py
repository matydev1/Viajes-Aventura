"""Interfaz gráfica Tkinter con diseño modern flat para Viajes Aventura."""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

# Paleta flat
BG = "#ecf0f1"; CARD = "#ffffff"; PRIMARY = "#3498db"
DARK = "#2c3e50"; DANGER = "#e74c3c"; SUCCESS = "#27ae60"
TEXT = "#2c3e50"; MUTED = "#7f8c8d"; BORDER = "#dfe6e9"
FONT = "Segoe UI"


def _flat_btn(parent, text, color, cmd, width=None):
    b = tk.Button(parent, text=text, bg=color, fg="white",
                  activebackground=color, activeforeground="white",
                  bd=0, padx=16, pady=8, font=(FONT, 10, "bold"),
                  cursor="hand2", command=cmd)
    if width:
        b.config(width=width)
    return b


def _entry(parent, label, show=None):
    tk.Label(parent, text=label, bg=CARD, fg=TEXT, font=(FONT, 9)).pack(anchor="w", pady=(8, 2))
    e = tk.Entry(parent, font=(FONT, 10), bd=1, relief="flat", bg="#f5f7fa",
                 highlightbackground=BORDER, highlightcolor=PRIMARY,
                 highlightthickness=1, show=show)
    e.pack(fill="x", ipady=6)
    return e


def _setup_styles(root):
    s = ttk.Style(root); s.theme_use("clam")
    s.configure(".", background=BG, foreground=TEXT, font=(FONT, 10))
    s.configure("Bg.TFrame", background=BG)
    s.configure("TNotebook", background=BG, borderwidth=0)
    s.configure("TNotebook.Tab", background=BG, foreground=MUTED,
                padding=(18, 10), borderwidth=0, font=(FONT, 10, "bold"))
    s.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", PRIMARY)])
    s.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
                rowheight=28, borderwidth=0)
    s.configure("Treeview.Heading", background=DARK, foreground="white",
                borderwidth=0, font=(FONT, 10, "bold"), padding=6)
    s.map("Treeview.Heading", background=[("active", "#34495e")])
    s.map("Treeview", background=[("selected", PRIMARY)], foreground=[("selected", "white")])
    s.configure("TCombobox", padding=4)


class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Viajes Aventura")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)
        self.db = Database()
        self.usuario = None
        self.intentos = 0
        self.sel_destino = None
        self.sel_paquete = None
        self._notebook = None
        _setup_styles(root)
        self.container = ttk.Frame(root, style="Bg.TFrame")
        self.container.pack(fill="both", expand=True)
        self.show_login()

    # ---------- utilitarios ----------
    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _header(self, titulo, subtitulo):
        h = tk.Frame(self.container, bg=DARK, height=72)
        h.pack(fill="x"); h.pack_propagate(False)
        left = tk.Frame(h, bg=DARK); left.pack(side="left", padx=25)
        tk.Label(left, text=titulo, bg=DARK, fg="white",
                 font=(FONT, 14, "bold")).pack(anchor="w", pady=(10, 0))
        tk.Label(left, text=subtitulo, bg=DARK, fg="#95a5a6",
                 font=(FONT, 9)).pack(anchor="w")
        right = tk.Frame(h, bg=DARK); right.pack(side="right", padx=25)
        tk.Label(right, text=f"Usuario: {self.usuario['nombre']}", bg=DARK, fg="white",
                 font=(FONT, 10)).pack(side="left", padx=(0, 15))
        _flat_btn(right, "Cerrar sesión", DANGER, self._logout).pack(side="left")

    def _logout(self):
        self.usuario = None; self.intentos = 0; self.show_login()

    # ---------- LOGIN ----------
    def show_login(self):
        self._clear()
        wrap = ttk.Frame(self.container, style="Bg.TFrame")
        wrap.place(relx=0.5, rely=0.5, anchor="center")
        card = tk.Frame(wrap, bg=CARD, padx=40, pady=35,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack()
        tk.Label(card, text="VIAJES AVENTURA", bg=CARD, fg=DARK,
                 font=(FONT, 20, "bold")).pack(pady=(0, 4))
        tk.Label(card, text="Sistema de gestión turística", bg=CARD, fg=MUTED,
                 font=(FONT, 10)).pack(pady=(0, 25))

        if not self.db.hay_administrador():
            tk.Label(card, text="Crear administrador inicial", bg=CARD, fg=PRIMARY,
                     font=(FONT, 11, "bold")).pack(anchor="w", pady=(0, 8))
            self.e_nombre = _entry(card, "Nombre completo")
            self.e_usuario = _entry(card, "Nombre de usuario")
            self.e_rut = _entry(card, "RUT (con guion)")
            self.e_clave = _entry(card, "Clave (mínimo 8)", show="*")
            _flat_btn(card, "Crear administrador", PRIMARY,
                      self._crear_admin).pack(fill="x", pady=(20, 0))
            return

        self.e_usuario = _entry(card, "Usuario")
        self.e_clave = _entry(card, "Clave", show="*")
        self.e_clave.bind("<Return>", lambda e: self._login())
        _flat_btn(card, "Iniciar sesión", PRIMARY,
                  self._login).pack(fill="x", pady=(20, 6))
        _flat_btn(card, "Registrarse como cliente", SUCCESS,
                  self.show_register).pack(fill="x")

    def _crear_admin(self):
        n, u, r, c = (self.e_nombre.get().strip(), self.e_usuario.get().strip(),
                      self.e_rut.get().strip(), self.e_clave.get())
        if not all([n, u, r, c]):
            messagebox.showwarning("Datos incompletos", "Complete todos los campos."); return
        if len(c) < 8:
            messagebox.showwarning("Clave débil", "La clave debe tener al menos 8 caracteres."); return
        if "-" not in r:
            messagebox.showwarning("RUT inválido", "El RUT debe incluir guion."); return
        if self.db.crear_usuario(n, u, r, c, "administrador"):
            messagebox.showinfo("Listo", "Administrador creado."); self.show_login()
        else:
            messagebox.showerror("Error", "El usuario ya existe.")

    def show_register(self):
        self._clear()
        wrap = ttk.Frame(self.container, style="Bg.TFrame")
        wrap.place(relx=0.5, rely=0.5, anchor="center")
        card = tk.Frame(wrap, bg=CARD, padx=40, pady=35,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack()
        tk.Label(card, text="CREAR CUENTA DE CLIENTE", bg=CARD, fg=DARK,
                 font=(FONT, 16, "bold")).pack(pady=(0, 4))
        tk.Label(card, text="Regístrate para reservar paquetes",
                 bg=CARD, fg=MUTED, font=(FONT, 10)).pack(pady=(0, 20))

        self.r_nombre = _entry(card, "Nombre completo")
        self.r_usuario = _entry(card, "Nombre de usuario")
        self.r_rut = _entry(card, "RUT (con guion)")
        self.r_clave = _entry(card, "Clave (mínimo 8)", show="*")
        self.r_clave2 = _entry(card, "Repetir clave", show="*")
        self.r_clave2.bind("<Return>", lambda e: self._registrar_cliente())

        _flat_btn(card, "Registrarme", SUCCESS,
                  self._registrar_cliente).pack(fill="x", pady=(20, 6))
        _flat_btn(card, "Volver al login", MUTED,
                  self.show_login).pack(fill="x")

    def _registrar_cliente(self):
        n = self.r_nombre.get().strip()
        u = self.r_usuario.get().strip()
        r = self.r_rut.get().strip()
        c1 = self.r_clave.get()
        c2 = self.r_clave2.get()

        if not all([n, u, r, c1, c2]):
            messagebox.showwarning("Datos incompletos", "Complete todos los campos."); return
        if len(c1) < 8:
            messagebox.showwarning("Clave débil", "La clave debe tener al menos 8 caracteres."); return
        if c1 != c2:
            messagebox.showwarning("Claves distintas", "Las claves no coinciden."); return
        if "-" not in r:
            messagebox.showwarning("RUT inválido", "El RUT debe incluir guion."); return

        if self.db.crear_usuario(n, u, r, c1, "cliente"):
            messagebox.showinfo("Listo", "Cuenta creada. Ya puedes iniciar sesión.")
            self.show_login()
        else:
            messagebox.showerror("Error", "El nombre de usuario ya existe.")

    def _login(self):
        u = self.db.autenticar(self.e_usuario.get().strip(), self.e_clave.get())
        if u:
            self.usuario = u; self.intentos = 0
            if u["rol"] == "administrador":
                self.show_admin()
            else:
                self.show_cliente()
        else:
            self.intentos += 1
            restantes = 3 - self.intentos
            if restantes <= 0:
                messagebox.showerror("Bloqueado", "Demasiados intentos. Cerrando.")
                self.root.quit(); self.root.destroy()
            else:
                messagebox.showerror("Error", f"Usuario o clave incorrectos.\nIntentos: {restantes}")
                self.e_clave.delete(0, "end")

    # ---------- DASHBOARD ADMIN ----------
    def show_admin(self):
        self._clear()
        self._header("Viajes Aventura · Panel de Administración",
                     "Gestión de destinos, paquetes y reservas")
        nb = ttk.Notebook(self.container)
        nb.pack(fill="both", expand=True, padx=15, pady=15)
        tab1 = ttk.Frame(nb, style="Bg.TFrame")
        tab2 = ttk.Frame(nb, style="Bg.TFrame")
        tab3 = ttk.Frame(nb, style="Bg.TFrame")
        nb.add(tab1, text="  Destinos  ")
        nb.add(tab2, text="  Paquetes  ")
        nb.add(tab3, text="  Reservas  ")
        self._tab_destinos(tab1)
        self._tab_paquetes(tab2)
        self._tab_reservas_admin(tab3)
        self._notebook = nb
        nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, _event):
        try:
            idx = self._notebook.index(self._notebook.select())
        except Exception:
            return
        if idx == 0:
            self._refrescar_destinos()
        elif idx == 1:
            self._refrescar_paquetes()
        elif idx == 2:
            self._refrescar_reservas_admin()

    # ---------- TAB DESTINOS ----------
    def _tab_destinos(self, parent):
        left = ttk.Frame(parent, style="Bg.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        right = tk.Frame(parent, bg=CARD, padx=20, pady=20,
                         highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="right", fill="y", padx=(8, 0), pady=8)

        cols = ("id", "nombre", "pais", "costo")
        self.tv_dest = ttk.Treeview(left, columns=cols, show="headings")
        for c, t, w, a in zip(cols, ("ID", "Nombre", "País", "Costo diario"),
                              (50, 200, 150, 120), ("center", "w", "w", "e")):
            self.tv_dest.heading(c, text=t); self.tv_dest.column(c, width=w, anchor=a)
        self.tv_dest.pack(fill="both", expand=True)
        self.tv_dest.bind("<<TreeviewSelect>>", self._sel_destino)

        tk.Label(right, text="Datos del destino", bg=CARD, fg=DARK,
                 font=(FONT, 12, "bold")).pack(anchor="w", pady=(0, 12))
        self.d_nombre = _entry(right, "Nombre")
        self.d_pais = _entry(right, "País")
        self.d_costo = _entry(right, "Costo diario")
        _flat_btn(right, "Crear", PRIMARY, self._crear_destino).pack(fill="x", pady=(10, 3))
        _flat_btn(right, "Modificar", "#f39c12", self._modificar_destino).pack(fill="x", pady=3)
        _flat_btn(right, "Eliminar", DANGER, self._eliminar_destino).pack(fill="x", pady=3)
        _flat_btn(right, "Limpiar", MUTED, self._limpiar_destino).pack(fill="x", pady=3)
        self._refrescar_destinos()

    def _refrescar_destinos(self):
        for i in self.tv_dest.get_children():
            self.tv_dest.delete(i)
        for d in self.db.listar_destinos():
            self.tv_dest.insert("", "end", values=(d["id"], d["nombre"], d["pais"],
                                                   f"${d['costo_diario']:,.0f}"))

    def _sel_destino(self, _):
        s = self.tv_dest.selection()
        if not s:
            return
        v = self.tv_dest.item(s[0], "values")
        self.sel_destino = int(v[0])
        self.d_nombre.delete(0, "end"); self.d_nombre.insert(0, v[1])
        self.d_pais.delete(0, "end"); self.d_pais.insert(0, v[2])
        self.d_costo.delete(0, "end")
        self.d_costo.insert(0, v[3].replace("$", "").replace(",", ""))

    def _limpiar_destino(self):
        for e in (self.d_nombre, self.d_pais, self.d_costo):
            e.delete(0, "end")
        self.sel_destino = None
        self.tv_dest.select_remove(*self.tv_dest.selection())

    def _crear_destino(self):
        try:
            if self.db.crear_destino(self.d_nombre.get().strip(),
                                     self.d_pais.get().strip(),
                                     float(self.d_costo.get())):
                self._refrescar_destinos()
                self._limpiar_destino()
                self._refrescar_paquetes()
                messagebox.showinfo("OK", "Destino creado.")
            else:
                messagebox.showerror("Error", "Nombre duplicado.")
        except ValueError:
            messagebox.showwarning("Inválido", "Revise los datos.")

    def _modificar_destino(self):
        if not self.sel_destino:
            return messagebox.showwarning("Sin selección", "Seleccione un destino.")
        try:
            if self.db.modificar_destino(self.sel_destino,
                                         self.d_nombre.get().strip(),
                                         self.d_pais.get().strip(),
                                         float(self.d_costo.get())):
                self._refrescar_destinos()
                self._refrescar_paquetes()
                messagebox.showinfo("OK", "Modificado.")
            else:
                messagebox.showerror("Error", "No se pudo.")
        except ValueError:
            messagebox.showwarning("Inválido", "Revise los datos.")

    def _eliminar_destino(self):
        if not self.sel_destino:
            return messagebox.showwarning("Sin selección", "Seleccione un destino.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar este destino?"):
            return
        if self.db.eliminar_destino(self.sel_destino):
            self._refrescar_destinos()
            self._refrescar_paquetes()
            self._limpiar_destino()
            messagebox.showinfo("OK", "Eliminado.")
        else:
            messagebox.showerror("Error", "Asociado a un paquete.")

    # ---------- TAB PAQUETES ----------
    def _tab_paquetes(self, parent):
        left = ttk.Frame(parent, style="Bg.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        right = tk.Frame(parent, bg=CARD, padx=18, pady=18,
                         highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="right", fill="y", padx=(8, 0), pady=8)

        cols = ("id", "nombre", "precio", "fechas", "libres")
        self.tv_paq = ttk.Treeview(left, columns=cols, show="headings")
        for c, t, w in zip(cols, ("ID", "Nombre", "Precio base", "Fechas", "Cupos libres"),
                           (40, 160, 110, 160, 90)):
            self.tv_paq.heading(c, text=t); self.tv_paq.column(c, width=w)
        self.tv_paq.pack(fill="both", expand=True)
        self.tv_paq.bind("<<TreeviewSelect>>", self._sel_paquete)

        tk.Label(right, text="Datos del paquete", bg=CARD, fg=DARK,
                 font=(FONT, 12, "bold")).pack(anchor="w", pady=(0, 10))
        self.p_nombre = _entry(right, "Nombre")
        self.p_precio = _entry(right, "Precio base")
        self.p_fi = _entry(right, "Fecha inicio (YYYY-MM-DD)")
        self.p_ft = _entry(right, "Fecha término")
        self.p_cupos = _entry(right, "Cupos")
        tk.Label(right, text="Destinos (Ctrl+clic para varios)", bg=CARD, fg=TEXT,
                 font=(FONT, 9)).pack(anchor="w", pady=(10, 2))
        self.lb_dest = tk.Listbox(right, selectmode="extended", height=6,
                                  font=(FONT, 9), bd=0, highlightthickness=1,
                                  highlightbackground=BORDER, bg="#f5f7fa",
                                  selectbackground=PRIMARY, selectforeground="white")
        self.lb_dest.pack(fill="x")
        _flat_btn(right, "Crear", PRIMARY, self._crear_paquete).pack(fill="x", pady=(10, 2))
        _flat_btn(right, "Modificar", "#f39c12", self._modificar_paquete).pack(fill="x", pady=2)
        _flat_btn(right, "Eliminar", DANGER, self._eliminar_paquete).pack(fill="x", pady=2)
        _flat_btn(right, "Limpiar", MUTED, self._limpiar_paquete).pack(fill="x", pady=2)
        self._refrescar_paquetes()

    def _refrescar_paquetes(self):
        for i in self.tv_paq.get_children():
            self.tv_paq.delete(i)
        for p in self.db.listar_paquetes():
            libres = p["cupos"] - p["reservas_activas"]
            self.tv_paq.insert("", "end",
                               values=(p["id"], p["nombre"],
                                       f"${p['precio_base']:,.0f}",
                                       f"{p['fecha_inicio']} -> {p['fecha_termino']}",
                                       libres))

        self.lb_dest.delete(0, "end")
        self._destinos_cache = self.db.listar_destinos()
        if not self._destinos_cache:
            self.lb_dest.insert("end", "(No hay destinos. Cree uno en la pestaña Destinos)")
            self.lb_dest.itemconfig(0, {"fg": MUTED})
            self.lb_dest.config(state="disabled")
        else:
            self.lb_dest.config(state="normal")
            for d in self._destinos_cache:
                self.lb_dest.insert("end",
                                    f"[{d['id']}] {d['nombre']} - {d['pais']} - ${d['costo_diario']:,.0f}")

    def _sel_paquete(self, _):
        s = self.tv_paq.selection()
        if not s:
            return
        pid = int(self.tv_paq.item(s[0], "values")[0])
        self.sel_paquete = pid
        p = self.db.obtener_paquete(pid)
        self.p_nombre.delete(0, "end"); self.p_nombre.insert(0, p["nombre"])
        self.p_precio.delete(0, "end"); self.p_precio.insert(0, p["precio_base"])
        self.p_fi.delete(0, "end"); self.p_fi.insert(0, p["fecha_inicio"])
        self.p_ft.delete(0, "end"); self.p_ft.insert(0, p["fecha_termino"])
        self.p_cupos.delete(0, "end"); self.p_cupos.insert(0, p["cupos"])
        self.lb_dest.selection_clear(0, "end")
        ids = [d["id"] for d in p["destinos"]]
        for i, d in enumerate(self._destinos_cache):
            if d["id"] in ids:
                self.lb_dest.selection_set(i)

    def _limpiar_paquete(self):
        for e in (self.p_nombre, self.p_precio, self.p_fi, self.p_ft, self.p_cupos):
            e.delete(0, "end")
        self.lb_dest.selection_clear(0, "end")
        self.sel_paquete = None
        #self.tv_paq.select_remove(*self.tv_paq.selection())
        seleccionados = self.tv_paq.selection()
        if seleccionados:
            self.tv_paq.selection_remove(seleccionados)
    def _leer_paquete_form(self):
        ids = [self._destinos_cache[i]["id"] for i in self.lb_dest.curselection()]
        return (self.p_nombre.get().strip(), float(self.p_precio.get()),
                self.p_fi.get().strip(), self.p_ft.get().strip(),
                int(self.p_cupos.get()), ids)

    def _crear_paquete(self):
        try:
            datos = self._leer_paquete_form()
            if not datos[5]:
                return messagebox.showwarning("Inválido", "Seleccione al menos un destino.")
            if self.db.crear_paquete(*datos):
                self._refrescar_paquetes(); self._limpiar_paquete()
                messagebox.showinfo("OK", "Paquete creado.")
            else:
                messagebox.showerror("Error", "Nombre duplicado.")
        except ValueError:
            messagebox.showwarning("Inválido", "Revise los datos.")

    def _modificar_paquete(self):
        if not self.sel_paquete:
            return messagebox.showwarning("Sin selección", "Seleccione un paquete.")
        try:
            if self.db.modificar_paquete(self.sel_paquete, *self._leer_paquete_form()):
                self._refrescar_paquetes()
                messagebox.showinfo("OK", "Modificado.")
            else:
                messagebox.showerror("Error", "No se pudo.")
        except ValueError:
            messagebox.showwarning("Inválido", "Revise los datos.")

    def _eliminar_paquete(self):
        if not self.sel_paquete:
            return messagebox.showwarning("Sin selección", "Seleccione un paquete.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar este paquete?"):
            return
        if self.db.eliminar_paquete(self.sel_paquete):
            self._refrescar_paquetes(); self._limpiar_paquete()
            messagebox.showinfo("OK", "Eliminado.")
        else:
            messagebox.showerror("Error", "Tiene reservas asociadas.")

    # ---------- TAB RESERVAS ADMIN ----------
    def _tab_reservas_admin(self, parent):
        # ---- Barra de filtros y acciones ----
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(top, text="Estado:", bg=BG, fg=TEXT,
                 font=(FONT, 10)).pack(side="left")
        self.res_estado = ttk.Combobox(top, values=["Todas", "confirmada", "cancelada"],
                                       state="readonly", width=12, font=(FONT, 10))
        self.res_estado.current(0)
        self.res_estado.pack(side="left", padx=(4, 15))
        self.res_estado.bind("<<ComboboxSelected>>",
                             lambda e: self._refrescar_reservas_admin())

        tk.Label(top, text="Buscar:", bg=BG, fg=TEXT,
                 font=(FONT, 10)).pack(side="left")
        self.res_buscar = tk.Entry(top, font=(FONT, 10), bd=1, relief="flat",
                                   bg="#f5f7fa", highlightthickness=1,
                                   highlightbackground=BORDER, width=25)
        self.res_buscar.pack(side="left", padx=(4, 8), ipady=4)
        self.res_buscar.bind("<Return>", lambda e: self._refrescar_reservas_admin())

        _flat_btn(top, "Filtrar", PRIMARY,
                  self._refrescar_reservas_admin).pack(side="left", padx=2)
        _flat_btn(top, "Limpiar filtros", MUTED,
                  self._limpiar_filtros_res).pack(side="left", padx=2)

        _flat_btn(top, "Eliminar", "#c0392b",
                  self._eliminar_reserva).pack(side="right", padx=2)
        _flat_btn(top, "Reactivar", "#f39c12",
                  self._reactivar_reserva).pack(side="right", padx=2)
        _flat_btn(top, "Cancelar", DANGER,
                  self._cancelar_reserva_admin).pack(side="right", padx=2)

        # ---- Tabla ----
        f = ttk.Frame(parent, style="Bg.TFrame")
        f.pack(fill="both", expand=True, padx=8, pady=8)
        cols = ("id", "cliente", "paquete", "fecha", "estado")
        self.tv_res_admin = ttk.Treeview(f, columns=cols, show="headings")
        for c, t, w in zip(cols, ("ID", "Cliente", "Paquete", "Fecha", "Estado"),
                           (50, 180, 220, 180, 110)):
            self.tv_res_admin.heading(c, text=t); self.tv_res_admin.column(c, width=w)
        self.tv_res_admin.pack(fill="both", expand=True)
        # Colores por estado
        self.tv_res_admin.tag_configure("confirmada", background="#eafaf1", foreground="#1e8449")
        self.tv_res_admin.tag_configure("cancelada", background="#fdecea", foreground="#c0392b")

        self._refrescar_reservas_admin()

    def _refrescar_reservas_admin(self):
        for i in self.tv_res_admin.get_children():
            self.tv_res_admin.delete(i)
        estado = self.res_estado.get() if hasattr(self, "res_estado") else ""
        busqueda = self.res_buscar.get().strip() if hasattr(self, "res_buscar") else ""
        for r in self.db.listar_reservas_filtradas(estado, busqueda):
            self.tv_res_admin.insert("", "end",
                                     values=(r["id"], r["cliente"], r["paquete_nombre"],
                                             r["fecha"], r["estado"]),
                                     tags=(r["estado"],))

    def _limpiar_filtros_res(self):
        self.res_estado.current(0)
        self.res_buscar.delete(0, "end")
        self._refrescar_reservas_admin()

    def _obtener_reserva_seleccionada(self):
        s = self.tv_res_admin.selection()
        if not s:
            messagebox.showwarning("Sin selección", "Seleccione una reserva en la tabla.")
            return None
        return self.tv_res_admin.item(s[0], "values")

    def _cancelar_reserva_admin(self):
        v = self._obtener_reserva_seleccionada()
        if not v:
            return
        rid, estado = int(v[0]), v[4]
        if estado == "cancelada":
            return messagebox.showinfo("Información", "Esta reserva ya está cancelada.")
        if not messagebox.askyesno("Confirmar", f"¿Cancelar la reserva #{rid}?"):
            return
        if self.db.cancelar_reserva(rid):
            self._refrescar_reservas_admin()
            messagebox.showinfo("OK", f"Reserva #{rid} cancelada.")

    def _reactivar_reserva(self):
        v = self._obtener_reserva_seleccionada()
        if not v:
            return
        rid, estado = int(v[0]), v[4]
        if estado == "confirmada":
            return messagebox.showinfo("Información", "Esta reserva ya está activa.")
        if not messagebox.askyesno("Confirmar", f"¿Reactivar la reserva #{rid}?"):
            return
        ok, msg = self.db.reactivar_reserva(rid)
        if ok:
            self._refrescar_reservas_admin()
            messagebox.showinfo("OK", msg)
        else:
            messagebox.showerror("No se pudo reactivar", msg)

    def _eliminar_reserva(self):
        v = self._obtener_reserva_seleccionada()
        if not v:
            return
        rid = int(v[0])
        if not messagebox.askyesno(
                "Confirmar",
                f"¿Eliminar permanentemente la reserva #{rid}?\n"
                "Esta acción no se puede deshacer."):
            return
        if self.db.eliminar_reserva(rid):
            self._refrescar_reservas_admin()
            messagebox.showinfo("OK", f"Reserva #{rid} eliminada.")

    # ---------- DASHBOARD CLIENTE ----------
    def show_cliente(self):
        self._clear()
        self._header("Viajes Aventura · Portal del Cliente",
                     "Consulta y reserva tus paquetes turísticos")
        nb = ttk.Notebook(self.container)
        nb.pack(fill="both", expand=True, padx=15, pady=15)
        tab1 = ttk.Frame(nb, style="Bg.TFrame")
        tab2 = ttk.Frame(nb, style="Bg.TFrame")
        nb.add(tab1, text="  Paquetes disponibles  ")
        nb.add(tab2, text="  Mis reservas  ")
        self._tab_cliente_paquetes(tab1)
        self._tab_cliente_reservas(tab2)
        self._notebook = nb
        nb.bind("<<NotebookTabChanged>>", self._on_tab_change_cliente)

    def _on_tab_change_cliente(self, _event):
        try:
            idx = self._notebook.index(self._notebook.select())
        except Exception:
            return
        if idx == 0:
            self._refrescar_cliente_paquetes()
        elif idx == 1:
            self._refrescar_cliente_reservas()

    def _tab_cliente_paquetes(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(top, text="Selecciona un paquete y haz clic en Reservar",
                 bg=BG, fg=MUTED, font=(FONT, 10)).pack(side="left")
        _flat_btn(top, "Reservar seleccionado", SUCCESS, self._reservar).pack(side="right")

        cols = ("id", "nombre", "destinos", "fechas", "precio", "libres")
        self.tv_cli_paq = ttk.Treeview(parent, columns=cols, show="headings")
        for c, t, w in zip(cols, ("ID", "Paquete", "Destinos", "Fechas", "Precio base", "Cupos libres"),
                           (40, 180, 260, 180, 110, 90)):
            self.tv_cli_paq.heading(c, text=t); self.tv_cli_paq.column(c, width=w)
        self.tv_cli_paq.pack(fill="both", expand=True, padx=8, pady=8)
        self._refrescar_cliente_paquetes()

    def _refrescar_cliente_paquetes(self):
        for i in self.tv_cli_paq.get_children():
            self.tv_cli_paq.delete(i)
        for p in self.db.listar_paquetes():
            det = self.db.obtener_paquete(p["id"])
            ds = ", ".join(d["nombre"] for d in det["destinos"])
            self.tv_cli_paq.insert("", "end",
                                   values=(p["id"], p["nombre"], ds,
                                           f"{p['fecha_inicio']} -> {p['fecha_termino']}",
                                           f"${p['precio_base']:,.0f}",
                                           p["cupos"] - p["reservas_activas"]))

    def _reservar(self):
        s = self.tv_cli_paq.selection()
        if not s:
            return messagebox.showwarning("Sin selección", "Seleccione un paquete.")
        pid = int(self.tv_cli_paq.item(s[0], "values")[0])
        ok, msg = self.db.crear_reserva(self.usuario["id"], pid)
        if ok:
            messagebox.showinfo("Reserva", msg)
        else:
            messagebox.showerror("Error", msg)
        self._refrescar_cliente_paquetes()
        self._refrescar_cliente_reservas()

    def _tab_cliente_reservas(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(top, text="Tus reservas registradas", bg=BG, fg=MUTED,
                 font=(FONT, 10)).pack(side="left")
        _flat_btn(top, "Cancelar seleccionada", DANGER,
                  self._cancelar_reserva).pack(side="right")

        cols = ("id", "paquete", "fecha", "estado")
        self.tv_cli_res = ttk.Treeview(parent, columns=cols, show="headings")
        for c, t, w in zip(cols, ("ID", "Paquete", "Fecha", "Estado"), (50, 260, 200, 120)):
            self.tv_cli_res.heading(c, text=t); self.tv_cli_res.column(c, width=w)
        self.tv_cli_res.pack(fill="both", expand=True, padx=8, pady=8)
        self.tv_cli_res.tag_configure("confirmada", background="#eafaf1", foreground="#1e8449")
        self.tv_cli_res.tag_configure("cancelada", background="#fdecea", foreground="#c0392b")
        self._refrescar_cliente_reservas()

    def _refrescar_cliente_reservas(self):
        for i in self.tv_cli_res.get_children():
            self.tv_cli_res.delete(i)
        for r in self.db.listar_reservas_cliente(self.usuario["id"]):
            self.tv_cli_res.insert("", "end",
                                   values=(r["id"], r["paquete_nombre"],
                                           r["fecha"], r["estado"]),
                                   tags=(r["estado"],))

    def _cancelar_reserva(self):
        s = self.tv_cli_res.selection()
        if not s:
            return messagebox.showwarning("Sin selección", "Seleccione una reserva.")
        rid = int(self.tv_cli_res.item(s[0], "values")[0])
        if not messagebox.askyesno("Confirmar", "¿Cancelar esta reserva?"):
            return
        if self.db.cancelar_reserva(rid):
            self._refrescar_cliente_reservas()
            self._refrescar_cliente_paquetes()
            messagebox.showinfo("OK", "Reserva cancelada.")


def ejecutar_gui():
    root = tk.Tk()
    AppGUI(root)
    root.mainloop()