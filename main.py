"""Punto de entrada de Viajes Aventura."""
import sys


def main():
    while True:
        print("\n" + "=" * 40)
        print("      VIAJES AVENTURA")
        print("=" * 40)
        print("1. Modo consola")
        print("2. Modo interfaz gráfica")
        print("3. Salir")
        op = input("Seleccione una opción: ").strip()

        if op == "1":
            from console import ejecutar_consola
            ejecutar_consola()
        elif op == "2":
            try:
                from gui import ejecutar_gui
                ejecutar_gui()
            except ImportError as e:
                print(f"No se pudo iniciar la GUI: {e}")
                print("Verifique que tkinter esté instalado.")
        elif op == "3":
            print("Hasta pronto.")
            sys.exit(0)
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()