from app import crear_app

def funcion_principal():
    app = crear_app()
    app.run(debug=True)

if __name__ == "__main__":
    funcion_principal()