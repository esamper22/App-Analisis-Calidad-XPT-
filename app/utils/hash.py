import os

def generar_hash(tam=25):
    # Si el tamaño es menor o igual a 25, se establece a 25
    if tam <= 25: tam = 25
    
    # Genera un hash aleatorio de 'tam' bytes
    data = os.urandom(tam)
    
    return {'dato binario':data} , {'dato hexadecimal':data.hex()}

if __name__ == "__main__":
    # Imprime el hash generado en formato binario y en formato hexadecimal
    print(generar_hash())