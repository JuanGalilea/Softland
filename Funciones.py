from tkinter import filedialog
emp=input("Seleccione empresa a trabajar (MG/GC) : ")
while emp.upper() not in ["MG","GC"]:
    emp=input("Seleccione un valor valido (MG/GC) : ")
if emp.upper()=="MG":
    from CodigosMG import *
else:
    from CodigosGC import *

class ErrorTipo(Exception):
    pass


class ErrorCuadre(Exception):
    pass


class Log:
    def __init__(self):
        with open("log_rechazos_cuadre.csv", "w") as file:
            file.write("TIPO;FOLIO;RUT;TOTAL;RAZON\n")
        with open("log_rechazos_tipo.csv", "w") as file:
            file.write("TIPO;FOLIO;RUT;TOTAL;RAZON\n")
        with open("log_rechazos_softland.csv", "w") as file:
            file.write("TIPO;FOLIO;RUT;TOTAL;RAZON\n")
        with open("log_rechazos_tropero.csv", "w") as file:
            file.write("TIPO;FOLIO;RUT;TOTAL;RAZON\n")
        with open("log_no_ingresadas.csv", "w") as file:
            file.write("TIPO;FOLIO;RUT;TOTAL;RAZON\n")
        with open("log_proveedores.txt", "w") as file:
            pass

    @staticmethod
    def write(texto, tipo=0):
        if tipo == 1:
            with open("log_rechazos_cuadre.csv", "a") as file:
                file.write(texto + "\n")
        if tipo == 2:
            with open("log_rechazos_tipo.csv", "a") as file:
                file.write(texto + "\n")
        if tipo == 3:
            with open("log_rechazos_softland.csv", "a") as file:
                file.write(texto + "\n")
        if tipo == 4:
            with open("log_rechazos_tropero.csv", "a") as file:
                file.write(texto + "\n")
        if tipo == 5:
            with open("log_no_ingresadas.csv", "a") as file:
                file.write(texto + "\n")
        if tipo == 6:
            with open("log_proveedores.txt", "a") as file:
                file.write(texto + "\n")


def check_presencia(factura, datos):
    for i in range(0, len(datos)):
        if factura[3] == datos[i][2] and factura[1] == datos[i][10].replace(".", ""):
            return i
    return -1


def presencia_softland(factura, datos):
    for dato in datos:
        if dato[16] == factura[3] and dato[14] == factura[1][:-2]:
            return True
    return False


def diccionario_csv(direccion):
    res = {}
    with open(direccion, "r") as file:
        for linea in file:
            aux = linea.replace("\n", "").split(";")
            res[aux[0]] = aux[1]
    return res


def cargar_csv(direccion):
    with open(direccion, "r") as file:
        res = []
        separador=""
        for linea in file:
            if separador=="":
                separador=get_separator(linea)
            res.append(linea.replace("\n", "").split(separador))
    return res

def get_separator(linea):
    if linea.count(";")>linea.count(","):
        return ";"
    else:
        return ","

def trabajar_lineas(linea,separador=";"):
    linea = linea.strip("\n")
    res = linea.split(separador)
    return res


def check_factura(factura):
    if factura[0] not in ["FL", "FT"]:
        raise ErrorTipo(f"tipo de factura es {factura[0]}")
    try:
        if int(factura[9]) - int(factura[8]) - int(factura[7]) - int(factura[6]) - int(factura[11]) != 0:
            raise ErrorCuadre(f"total-glosa={factura[9]}-{factura[8]}-{factura[7]}-{factura[6]}-{factura[11]}")
    except ValueError:
        if int(factura[9]) - int(factura[8]) - int(factura[7]) - int(factura[6]) != 0:
            raise ErrorCuadre(f"total-glosa={factura[9]}-{factura[8]}-{factura[7]}-{factura[6]}")


def filtro_facturas(factura):
    try:
        check_factura(factura)
    except ErrorTipo:
        return False
    except ErrorCuadre:
        return False
    return True


def facturar(datos):
    res = []
    try:
        res.append(codigos_tipos[datos[1]])
    except KeyError:
        return None
    res.append(datos[3])
    res.append(datos[4])
    res.append(datos[5])
    res.append(datos[6])
    res.append(datos[7])
    res.append(datos[9])
    res.append(datos[10])
    res.append(datos[11])
    res.append(datos[14])
    try:
        res.append(codigos_impuestos[datos[24]])
    except KeyError:
        res.append(None)
    res.append(datos[25])
    return res


def creador_lineas(lista,separador=";"):
    res = ""
    for linea in lista:
        res += linea
        res += separador
    res = res[:-1]
    res += "\n"
    return res


def guardar_csv(datos,separador=";"):
    with open(filedialog.asksaveasfilename(title="Indique archivo de salida", filetypes=[("CSV (*.csv)", ".csv")],
                                           defaultextension=".csv"), "w",encoding="latin-1") as file:
        # file.write(
        #    "Codigo Plan de Cuenta;Monto al Debe Moneda Base;Monto al Haber Moneda Base;Descripcion Movimiento;\
        # Equivalencia Moneda;Monto al Debe Moneda Adicional;Monto al Haber Moneda Adicional;Codigo Condicion de Venta;\
        # Codigo Vendedor;Codigo Ubicacion;Codigo Concepto de Caja;Codigo Instrumento Financiero;Cantidad Instrumento \
        # Financiero;Codigo Detalle de Gasto;Cantidad Concepto de Gasto;Codigo Centro de Costo;Tipo Docto. Conciliacion;\
        # Nro. Docto. Conciliacion;Codigo Auxiliar;Tipo Documento;Nro. Documento;Fecha Emision Docto.(DD/MM/AAAA);Fecha \
        # Vencimiento Docto.(DD/MM/AAAA);Tipo Docto. Referencia;Nro. Docto. Referencia;Nro. Correlativo Interno;Monto 1 \
        # Detalle Libro;Monto 2 Detalle Libro;Monto 3 Detalle Libro;Monto 4 Detalle Libro;Monto 5 Detalle Libro;Monto 6 \
        # Detalle Libro;Monto 7 Detalle Libro;Monto 8 Detalle Libro;Monto 9 Detalle Libro;Monto Suma Detalle Libro;\
        # Numero Documento Desde;Numero Documento Hasta;Nro. agrupacion en igual comprobante\n")
        for linea in datos:
            file.write(creador_lineas(linea,separador=separador))


global_corr = 0


def desglosar(factura, correlativo):
    global global_corr
    if global_corr == 0:
        global_corr = int(correlativo)
    corr_actual = global_corr
    res = []
    if factura[9] != "0":  # total
        aux = [""] * 39
        aux[0] = codigos_cuentas["proveedores"]  # cuenta
        aux[1] = "0"  # debe
        aux[2] = str(factura[9])  # haber
        aux[3] = factura[0] + " " + factura[3] + " " + codigos_centros_cortos[factura[5]] + " MERCADERIA"  # descripcion
        aux[15] = factura[5]  # centro de costo
        aux[18] = factura[1][:-2]  # auxiliar
        aux[19] = factura[0]  # tipo documento
        aux[20] = factura[3]  # folio
        aux[21] = factura[4]  # fecha
        aux[22] = factura[12]  # fecha
        aux[23] = factura[0]  # tipo doc referencia
        aux[24] = factura[3]  # folio doc referencia
        aux[25] = str(corr_actual)
        corr_actual += 1
        aux[26] = factura[7]  # detalle neto
        aux[27] = factura[6]  # detalle exento
        aux[28] = factura[8]  # detalle iva
        if factura[10] == "":
            aux[29] = factura[11]
        else:
            aux[31] = factura[11]
        aux[35] = factura[9]

        aux[38] = "1"  # numero comprobantes
        res.append(aux)
    if factura[8] != "0":  # iva y neto
        aux = [""] * 39
        aux[0] = codigos_cuentas["iva"]
        aux[1] = str(factura[8])
        aux[2] = "0"
        aux[3] = "IVA"
        aux[15] = factura[5]
        aux[38] = "1"
        res.append(aux)
        aux = [""] * 39
        aux[0] = codigos_cuentas["mercaderia"]
        aux[1] = str(factura[7])
        aux[2] = "0"
        aux[3] = "MERCADERIA"
        aux[15] = factura[5]
        aux[38] = "1"
        res.append(aux)
    if factura[6] != "0":  # exento
        aux = [""] * 39
        aux[0] = codigos_cuentas["mercaderia"]
        aux[1] = str(factura[6])
        aux[2] = "0"
        aux[15] = factura[5]
        aux[38] = "1"
        res.append(aux)
    if not factura[10] is None:  # otro impuesto
        aux = [""] * 39
        aux[0] = codigos_cuentas[factura[10]]
        aux[1] = str(factura[11])
        aux[2] = "0"
        aux[15] = factura[5]
        aux[38] = "1"
        res.append(aux)
    global_corr = corr_actual
    return res


def unir_facturas(factura1, factura2):
    res = factura1
    if factura1[3] == factura2[3] and factura1[1] == factura2[1]:
        res[11] = str(int(res[11]) + int(factura2[11]))
    return res
