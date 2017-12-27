print("INICIALIZANDO.......")
print("")
print("Programado por: Juan Galilea")
print("version 1.2.0")
import logging
import sys
import tkinter as tk
from datetime import datetime, timedelta
from API import extract_sheet


print("###########################################################")
root = tk.Tk()
root.withdraw()
logging.basicConfig(filename="log_errores.txt", filemode="w", level=logging.ERROR)
print("")
from Funciones import *
proveed = extract_sheet(id=codigo_proovedores)

def condicion_venta(factura, proveedores):
    codigo = factura[1][:-2]
    for proved in proveedores:
        if not proved == []:
            if proved[0] == codigo:
                try:
                    if proved[3] in ["CONTADO", "contado", "Contado"]:
                        return 0
                except IndexError:
                    return 0
                return proved[3]
    return -1


def filtro_tropero(facturas, datos):
    for factura in facturas:
        pos = check_presencia(factura, datos)
        if pos != -1:
            res = factura
            res[5] = codigos_centros[datos[pos][13].replace(" ", "")]
            yield res
        else:
            Log.write(f"{factura[0]};{factura[3]};{factura[1]};{factura[9]};{factura[2]};", tipo=4)


def filtro_softland(facturas, datos, invertido=False):
    for factura in facturas:
        if not presencia_softland(factura, datos):
            if invertido:
                Log.write(f"{factura[0]};{factura[3]};{factura[1]};{factura[9]};{factura[2]}", tipo=5)
            else:
                yield factura
        else:
            Log.write(f"{factura[0]};{factura[3]};{factura[1]};{factura[9]};{factura[2]}", tipo=3)


correlativo = input("INGRESE CORRELATIVO INTERNO DEL PRIMER DOCUMENTO: ")
while not str.isnumeric(correlativo):
    correlativo = input("VALOR INCORRECTO, INGRESE UN VALOR NUMERICO: ")
registro = []
print("")
print("ELIJA ARCHIVO DEL SII")
print("")
try:
    with open(filedialog.askopenfilename(title="seleccione csv del SII", filetypes=[("CSV (*.csv)", ".csv")]), "r",
              encoding='utf8') as file:
        file.readline()
        for linea in file:
            registro.append(trabajar_lineas(linea))
except FileNotFoundError:
    sys.exit()
except UnicodeDecodeError:
    input("[ERROR DE CODEC] asegurese que los archivos estan en encoding utf-8 \nPresione cualquier tecla para salir")
    sys.exit()
try:
    facturas = list(facturar(x) for x in registro)
except IndexError:
    input("[ERROR DE INDICE] Recuerde agregarle las columnas extra al archivo pendientes \nPresione cualquier tecla para salir")
    sys.exit()
aux = list()
aux.append(facturas[0])
print("TRANSFORMANDO FORMATO DEL SII...")
logger = Log()
for i in range(1, len(facturas)):
    if facturas[i] is None:
        break
    if facturas[i][3] == aux[-1][3]:
        aux[-1] = unir_facturas(aux[-1], facturas[i])
    else:
        aux.append(facturas[i])

for i in range(0, len(aux)):
    emision = datetime(year=int(aux[i][4][-4:]), month=int(aux[i][4][3:5]), day=int(aux[i][4][:2]))
    cond = condicion_venta(aux[i], proveed)
    if cond == -1:
        logger.write(f"Proveedor rut {aux[i][1]} no encontrado", tipo=6)
        cond = 0
    delta = timedelta(days=int(cond))
    fecha = str((emision + delta).date())
    aux[i].append(f"{fecha[-2:]}/{fecha[5:7]}/{fecha[:4]}")

total_facturas = aux

for factura in aux:
    try:
        check_factura(factura)
    except ErrorCuadre:
        print(f"WARNING: FACTURA {factura} no cuadra")
        Log.write(f"{factura[0]};{factura[3]};{factura[1]};{factura[9]};{factura[2]}", tipo=1)
    except ErrorTipo:
        print(f"WARNING: FACTURA {factura} no tiene un tipo soportado")
        Log.write(f"{factura[0]};{factura[3]};{factura[1]};{factura[9]};{factura[2]}", tipo=2)

print("SELECCIONE ARCHIVO ACTUALIZADO DE TROPERO")
try:
    datos_tropero = cargar_csv(
        filedialog.askopenfilename(title="Seleccione csv de tropero", filetypes=[("CSV (*.csv)", ".csv")]))
except FileNotFoundError:
    exit()
except UnicodeDecodeError:
    input("[ERROR DE CODEC] asegurese que los archivos estan en encoding utf-8 \nPresione cualquier tecla para salir")
    sys.exit()

datos_tropero = datos_tropero[1:]
aux = list(filtro_tropero(aux, datos_tropero))
print("")
separad = input("INGRESE EL SEPARADOR DEL ARCHIVO CVMOVIM :")
print("")
print("SELECCIONE ARCHIVO CVMOVIM ACTUALIZADO")
try:
    movim_softland = cargar_csv(
        filedialog.askopenfilename(title="Seleccione csv de cwmovim de softland", filetypes=[("CSV (*.csv)", ".csv")]),
        separador=separad)
except FileNotFoundError:
    exit()
except UnicodeDecodeError:
    input("[ERROR DE CODEC] asegurese que los archivos estan en encoding utf-8 \nPresione cualquier tecla para salir")
    sys.exit()

print("PREPARANDO FILTRO CVMOVIM...")
print("")
ano = input("INGRESE AÑO A TRABAJAR: ")
print("")
while not ano in ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028"]:
    ano = input("INGRESE AÑO VÁLIDO: ")

print("FILTRANDO CVMOVIM...")
movim_softland = list(filter(lambda x: x[0] == ano, movim_softland))

print("FILTRANDO FACTURAS CON DATOS SOFTLAND...")
aux = list(filtro_softland(aux, movim_softland))
filtro_softland(total_facturas, movim_softland, invertido=True)
print("FILTRANDO FACTURAS POR ERRORES Y PREPARANDO ARCHIVO FINAL...")
resultados = [desglosar(x, correlativo) for x in list(filter(filtro_facturas, aux))]
print(f"NUMERO DE DOCUMENTOS A INGRESAR = {len(resultados)}")
print(f"CORRELATIVOS VAN DE {correlativo} A {int(correlativo)+len(aux)-1}")
final = []
for i in resultados:
    final += i
print(f"NUMERO DE MOVIMIENTOS A INGRESAR = {len(final)}")
print("")
separad = input("INGRESE EL SEPARADOR DEL ARCHIVO DE SALIDA :")
print("")
try:
    guardar_csv(final)
except FileNotFoundError:
    exit()
