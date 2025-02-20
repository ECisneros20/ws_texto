import logging
import os
import re
import string
import sys
from collections.abc import Iterable
from io import StringIO

import networkx as nx
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, status
from nltk.cluster.util import cosine_distance
from nltk.corpus import stopwords
from num2words import num2words

# from pydantic import Field
from constantes_texto import ConstantesTexto

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import Validaciones, setup_logging

# Configura el logging
setup_logging()
# Obtiene un logger para este módulo
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

router = APIRouter()


@router.post("/df2str", status_code=status.HTTP_200_OK)
async def convertir_df_a_str(df: str, nombre_columna: str) -> str:
    # Intenta convertir el df a str
    try:
        df = pd.read_json(StringIO(df))
        if nombre_columna not in df.columns:
            mensaje = "El nombre de la columna no se encuentra en el df"
            logger.exception(mensaje)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=mensaje)
        df.fillna("", inplace=True)
        texto = " ".join(df[nombre_columna].astype(str).to_list())
        texto = texto.strip()
        return texto
    except Exception as e:
        mensaje = f"No se convirtió el df a str, problema imprevisto: {e}"
        logger.exception(mensaje)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=mensaje)


@router.post("/reemplazar_patron", status_code=status.HTTP_200_OK)
async def reemplazar_patron():
    pass


class Texto:
    """Una clase que contiene métodos para limpieza y preprocesamiento de texto,
    similaridad de oraciones, entre otras actividades similares
    """

    @staticmethod
    def convertir_df_a_str(
        df: pd.DataFrame, nombre_columna: str = "Contenido", credenciales: dict = {}
    ) -> tuple[str, str]:
        """Convierte la columna indicada de un df en un string

        Args:
            df (pd.DataFrame): Df cuya columna será compartida
            nombre_columna (str): Nombre de la columna del df
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[str, str]: Texto obtenido al unir una columna y mensaje de error
        """
        # Validar que 'df' sea del tipo dataframe
        res, msj = Validaciones.es_tipo(df, pd.DataFrame, credenciales)
        if not res:
            return None, msj
        # Validar que 'nombre columna' sea del tipo str
        res, msj = Validaciones.es_tipo(nombre_columna, str, credenciales)
        if not res:
            return None, msj
        # Intenta convertir el df a str
        try:
            df.fillna("", inplace=True)
            texto = " ".join(df[nombre_columna].to_list())
            texto = texto.strip()
            return texto, None
        except Exception as e:
            mensaje = f"No se convirtió el df a str, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def reemplazar_patron(
        texto: str,
        patron_busqueda: str,
        reemplazo: str,
        credenciales: dict = {},
    ) -> tuple[str, str]:
        """Reemplaza el patrón deseado en todas las coincidencias en el texto

        Args:
            texto (str): Texto donde se realiza la búsqueda
            patron_busqueda (str): Patrón en formato regex a buscar
            reemplazo (str): Contenido que reemplazará al anterior dentro del texto
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[str, str]: Texto después de aplicar los reemplazos y mensaje de error
        """
        # Validar que 'texto' sea del tipo str
        res, msj = Validaciones.es_tipo(texto, str, credenciales)
        if not res:
            return None, msj
        # Validar que 'patron_busqueda' sea del tipo str
        res, msj = Validaciones.es_tipo(patron_busqueda, str, credenciales)
        if not res:
            return None, msj
        # Validar que 'reemplazo' sea del tipo str
        res, msj = Validaciones.es_tipo(reemplazo, str, credenciales)
        if not res:
            return None, msj
        # Intenta reemplazar el 'patron_busqueda'
        try:
            return re.sub(patron_busqueda, reemplazo, texto), None
        except Exception as e:
            mensaje = f"No se encontró el patrón de búsqueda, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def obtener_posicion_patron(
        texto: str,
        patron_busqueda: str,
        pos_inicial: bool = True,
        credenciales: dict = {},
    ) -> tuple[int, str]:
        """Devuelve la posición del match, puede ser la posición inicial o final del
        match según se indique

        Args:
            texto (str): Texto donde se realiza la búsqueda
            patron_busqueda (str): Patrón en formato regex a buscar
            credenciales (dict): Datos a registrar en el log
            pos_inicial (bool, optional): Devuelve el inicio o final del match.
            Defaults to True.

        Returns:
            tuple[int, str]: Posición del match encontrado y mensaje de error
        """
        # Validar que 'texto' sea del tipo str
        res, msj = Validaciones.es_tipo(texto, str, credenciales)
        if not res:
            return None, msj
        # Validar que 'patron_busqueda' sea del tipo str
        res, msj = Validaciones.es_tipo(patron_busqueda, str, credenciales)
        if not res:
            return None, msj
        # Validar que 'pos_inicial' sea del tipo bool
        res, msj = Validaciones.es_tipo(pos_inicial, bool, credenciales)
        if not res:
            return None, msj
        # Intenta encontrar coincidencia
        try:
            if match := re.search(patron_busqueda, texto):
                if pos_inicial:
                    return match.start(), None
                else:
                    return match.end(), None
            mensaje = f"No se encontró el patrón de búsqueda: {patron_busqueda}"
            logger.error(mensaje)
            return None, "Error texto"
        except Exception as e:
            mensaje = f"No se encontró el patrón de búsqueda, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def limpiar_corpus(corpus: str, credenciales: dict = {}) -> tuple[str, str]:
        """Limpia el texto de saltos de línea o similares y sin espacios seguidos

        Args:
            corpus (str): Texto a limpiar
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[str, str]: Texto sin saltos de línea o similares y mensaje de error
        """
        # Validar que 'corpus' sea del tipo str
        res, msj = Validaciones.es_tipo(corpus, str, credenciales)
        if not res:
            return None, msj
        # Intenta limpiar el corpus
        try:
            # Eliminar símbolos usando expresiones regulares
            corpus_limpio = re.sub(r"[!#$%^&*\+{}[\]|\\]", "", corpus.strip())
            # Reemplazar saltos de línea seguidos o separados por uno o más espacios
            # por un solo salto de línea por vez
            corpus_limpio = re.sub(r"(\n *)+", "\n", corpus_limpio)
            # Reemplazar los dos saltos de líneas por puntos cuando haya un subtítulo
            # con números romanos en el medio, o esté al inicio o
            # al final del string
            corpus_limpio = re.sub(
                r"(^|\n)([MDCLXVI]+\.)( *)([a-zA-ZÁáÉéÍíÓóÚúÜü ]*)(\n*)$",
                r". \2 \4.",
                corpus_limpio,
            )
            corpus_limpio = re.sub(
                r"(^|\n)([MDCLXVI]+\.)( *)([a-zA-ZÁáÉéÍíÓóÚúÜü ]*)\n",
                r". \2 \4. ",
                corpus_limpio,
            )
            # Reemplazar salto de línea antes del párrafo inicial por un punto
            corpus_limpio = re.sub(
                r"\n(?=.*con RUC *(N°)?)", ". ", corpus_limpio, count=1
            )
            # Reemplazar el salto de línea por un espacio, simulando oraciones seguidas
            corpus_limpio = corpus_limpio.replace("\n", " ")
            # Reemplazar el signo ´ por '
            corpus_limpio = corpus_limpio.replace("´", "'")
            # Reemplazar espacios vacíos y/o cualquier expresión tipo \n seguidos o
            # separados por uno o más espacios por un solo espacio vacío
            corpus_limpio = re.sub(r"(\s *)+", " ", corpus_limpio)
            # Quitar el número seguido del mismo en palabras al inicio de las páginas,
            # que representan la numeración de la página
            for pagina in range(1, 101):
                corpus_limpio_new = re.sub(
                    "^"
                    + re.escape(
                        f"{str(pagina)} {num2words(pagina, lang='es').capitalize()}"
                    )
                    + " *",
                    "",
                    corpus_limpio,
                )
                if len(corpus_limpio_new) < len(corpus_limpio):
                    corpus_limpio = corpus_limpio_new
                    break
            # Agregar un espacio entre el signo de puntuación y el caracter
            # alfanumérico siguiente
            corpus_limpio = re.sub(r"\)(?=\w)", ") ", corpus_limpio)
            corpus_limpio = re.sub(r"\.(\w{2,})", r". \1", corpus_limpio)
            corpus_limpio = re.sub(r":(?=\w)", ": ", corpus_limpio)
            corpus_limpio = re.sub(r",(?=\w)", ", ", corpus_limpio)
            # Quitar el espacio entre la última palabra y el signo de puntuación
            corpus_limpio = corpus_limpio.replace(" )", ")")
            corpus_limpio = corpus_limpio.replace(" /", "/")
            corpus_limpio = corpus_limpio.replace(" .", ".")
            corpus_limpio = corpus_limpio.replace(" :", ":")
            corpus_limpio = corpus_limpio.replace(" ,", ",")
            # Quitar el punto generado por un salto de línea que venga después de otro
            # signo de puntuación
            corpus_limpio = corpus_limpio.replace("/.", "/")
            corpus_limpio = corpus_limpio.replace("..", ".")
            corpus_limpio = corpus_limpio.replace(":.", ":")
            corpus_limpio = corpus_limpio.replace(",.", ",")
            return corpus_limpio, None
        except Exception as e:
            mensaje = f"No se limpió el corpus, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def preprocesar_corpus(corpus: str, credenciales: dict = {}) -> tuple[str, str]:
        """Preprocesa el texto con correcciones de tildación y puntuación

        Args:
            corpus (str): Texto a preprocesar
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[str, str]: Texto con correcciones de tildación y mensaje de error
        """
        # Validar que 'corpus' sea del tipo str
        res, msj = Validaciones.es_tipo(corpus, str, credenciales)
        if not res:
            return None, msj
        # Intenta preprocesar el corpus
        try:
            # Colocar el símbolo de sol donde corresopnda
            corpus_limpio = corpus.replace("S/", "S/.")
            # Reemplazar palabras incorrectamente separadas
            trama = []
            for caracter in corpus_limpio:
                if caracter.islower():
                    trama.append(0)
                else:
                    trama.append(1)
            corpus_aux = corpus_limpio.lower()
            for error, correccion in ConstantesTexto.correciones.value:
                corpus_aux = corpus_aux.replace(error, correccion)
            corpus_limpio = ""
            for caracter, patron in zip(corpus_aux, trama):
                if patron:
                    caracter = caracter.upper()
                corpus_limpio += caracter
            # Reemplazar las vocales con tilde francesa a tilde estándar
            corpus_limpio = corpus_limpio.replace("â", "á")
            corpus_limpio = corpus_limpio.replace("ê", "é")
            corpus_limpio = corpus_limpio.replace("ô", "ó")
            corpus_limpio = corpus_limpio.replace("à", "á")
            # Reemplazar caracteres especiales del francés a español
            corpus_limpio = corpus_limpio.replace("ç", "c")
            # Agregar un espacio entre el signo de puntuación y el caracter
            # alfanumérico siguiente
            corpus_limpio = re.sub(r"\)(?=\w)", ") ", corpus_limpio)
            corpus_limpio = re.sub(r"\.(\w{2,})", r". \1", corpus_limpio)
            corpus_limpio = re.sub(r":(?=\w)", ": ", corpus_limpio)
            corpus_limpio = re.sub(r",(?=\w)", ", ", corpus_limpio)
            # Quitar el espacio entre la última palabra y el signo de puntuación
            corpus_limpio = corpus_limpio.replace(" )", ")")
            corpus_limpio = corpus_limpio.replace(" /", "/")
            corpus_limpio = corpus_limpio.replace(" .", ".")
            corpus_limpio = corpus_limpio.replace(" :", ":")
            corpus_limpio = corpus_limpio.replace(" ,", ",")
            # Quitar el punto generado por un salto de línea que venga después de otro
            # signo de puntuación
            corpus_limpio = corpus_limpio.replace("..", ".")
            corpus_limpio = corpus_limpio.replace(":.", ":")
            corpus_limpio = corpus_limpio.replace(",.", ",")
            # Quita el espacio luego del punto que indica los céntimos en los montos
            corpus_limpio = re.sub(r"(S/\. [0-9]*). (?=[0-9])", r"\1.", corpus_limpio)
            # Quitar el espacio luego del punto que precede a la terminación de un
            # correo electrónico
            corpus_limpio = re.sub(
                r"(?<=@)( *)(\w+)( *)\.( *)(?=com|org|net|edu|gov|co|uk|de|ca|es|pe)",
                r"\2.",
                corpus_limpio,
            )
            return corpus_limpio, None
        except Exception as e:
            mensaje = f"No se preprocesó el corpus, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def reconstruir_nombre_completo(
        datos: Iterable[str], credenciales: dict = {}
    ) -> tuple[str, str]:
        """Une un nombre basado en un Iterable compuesto de 3 valores, acepta None e
        ignora signos de puntuación

        Args:
            datos (Iterable[str]): Iterable con 3 valores: apellido paterno, apellido
            materno y nombres
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[str, str]: Nombre con las 3 partes unidas y mensaje de error
        """
        # Validar que 'datos' sea del tipo Iterable
        res, msj = Validaciones.es_tipo(datos, Iterable, credenciales)
        if not res:
            return None, msj
        # Validar que 'datos' esté compuesto de 3 elementos: Apellido paterno, apellido
        # materno y nombres o nombre institucional en partes
        res, msj = Validaciones.es_len_correcto(datos, 3, credenciales)
        if not res:
            return None, msj
        # Intenta reconstruir el nombre
        datos_aux = []
        try:
            for dato in datos:
                # Limpiar dato
                dato, msj = Texto.limpiar_corpus(dato, credenciales)
                if dato is None:
                    return None, msj
                # Preprocesar dato
                dato, msj = Texto.preprocesar_corpus(dato, credenciales)
                if dato is None:
                    return None, msj
                # El dato debe ser del tipo str con al menos un caracter y no ser solo
                # un caracter de puntuación
                if len(dato) > 0 and dato not in string.punctuation:
                    datos_aux.append(dato)
            # Validar que datos_aux haya conservado al menos un dato para reconstruir
            res, msj = Validaciones.es_len_correcto(datos_aux, 0, credenciales)
            if res:
                return None, "Error texto"
            else:
                return " ".join(datos_aux), None
        except Exception as e:
            mensaje = f"No se pudo reconstruir nombre, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def separar_por_oraciones(
        corpus: str, credenciales: dict = {}
    ) -> tuple[list[list[str]], str]:
        """Separa un párrafo en una lista de palabras, agrupadas por oraciones

        Args:
            corpus (str): Texto a separar
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[list[list[str]], str]: Lista de listas de oraciones separadas por
            palabras y mensaje de error
        """
        # Validar que 'corpus' sea del tipo str
        res, msj = Validaciones.es_tipo(corpus, str, credenciales)
        if not res:
            return None, msj
        # Intenta separar el corpus por oraciones
        try:
            oraciones = []
            # Cuando encuentra un punto y espacio divide el párrafo
            oraciones = corpus.split(". ")
            for oracion in oraciones:
                # Limpiar oración
                oracion, msj = Texto.limpiar_corpus(oracion, credenciales)
                if oracion is None:
                    return None, msj
                # Preprocesar oración
                oracion, msj = Texto.preprocesar_corpus(oracion, credenciales)
                if oracion is None:
                    return None, msj
                if oracion != "":
                    oraciones.append(oracion.split(" "))
            return oraciones, None
        except Exception as e:
            mensaje = f"No se creó la lista de oraciones, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def calcular_valor_similaridad(
        oracion1: list[str], oracion2: list[str], credenciales: dict = {}
    ) -> tuple[float, str]:
        """Calcula el valor de similaridad entre dos oraciones sin stopwords

        Args:
            oracion1 (list[str]): Oración 1 para calcular valor de similaridad
            oracion2 (list[str]): Oración 2 para calcular valor de similaridad
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[float, str]: Valor de similaridad y mensaje de error
        """
        # Validar que 'oracion1' sea del tipo list
        res, msj = Validaciones.es_tipo(oracion1, list, credenciales)
        if not res:
            return None, msj
        # Validar que 'oracion2' sea del tipo list
        res, msj = Validaciones.es_tipo(oracion2, list, credenciales)
        if not res:
            return None, msj
        # Intenta calcular la similaridad de dos oraciones separadas por palabras
        try:
            # Carga diccionario de stopwords
            stop_words = stopwords.words("spanish")
            # Crea lista de palabras del párrafo 1 y las almacena en minúsculas
            oracion1_aux = []
            for w in oracion1:
                # Validar que cada componente sea un str
                res, msj = Validaciones.es_tipo(w, str, credenciales)
                if not res:
                    return None, msj
                if w not in stop_words:
                    oracion1_aux.append(w.lower)
            # Crea lista de palabras del párrafo 2 y las almacena en minúsculas
            oracion2_aux = []
            for w in oracion2:
                # Validar que cada componente sea un str
                res, msj = Validaciones.es_tipo(w, str, credenciales)
                if not res:
                    return None, msj
                if w not in stop_words:
                    oracion2_aux.append(w.lower)
            # Une las dos listas
            all_words = list(set(oracion1_aux + oracion2_aux))
            # Crea vector de longitud igual a la cantidad de palabras de all_words
            vector1 = [0] * len(all_words)
            # Crea vector de longitud igual a la cantidad de palabras de all_words
            vector2 = [0] * len(all_words)
            # Primer párrafo, cuenta la frecuencia de aparición de cada palabra
            for w in oracion1_aux:
                # Suma frecuencia de aparición de las palabras
                vector1[all_words.index(w)] += 1
            # Segundo párrafo, cuenta la frecuencia de aparición de cada palabra
            for w in oracion2_aux:
                # Suma frecuencia de aparición de las palabras
                vector2[all_words.index(w)] += 1
            # Retorna valor de similaridad de los dos párrafos
            return 1 - cosine_distance(vector1, vector2), None
        except Exception as e:
            mensaje = f"No se calculó la similaridad, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def calcular_matriz_similaridad(
        oraciones: list[list[str]], credenciales: dict = {}
    ) -> tuple[np.ndarray, str]:
        """Calcula la matriz de similaridad para una lista de oraciones

        Args:
            oraciones (list[list[str]]): Lista de oraciones separadas por palabras
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[np.ndarray, str]: Matriz de similaridad y mensaje de error
        """
        # Validar que 'oraciones' sea del tipo list
        res, msj = Validaciones.es_tipo(oraciones, list, credenciales)
        if not res:
            return None, msj
        # Intenta calcular la matriz de similaridad para cada par de oraciones de la
        # lista de oraciones dada
        try:
            # Carga diccionario de stopwords
            stop_words = stopwords.words("spanish")
            # Verifica que cada componente sea una lista y este esté compuesto a su vez
            # de solo str
            for oracion in oraciones:
                res, msj = Validaciones.es_tipo(oracion, list, credenciales)
                if not res:
                    return None, msj
                for palabra in oracion:
                    res, msj = Validaciones.es_tipo(palabra, str, credenciales)
                    if not res:
                        return None, msj
            # Crea matriz cuadrada de cantidad de párrafos
            similarity_matrix = np.zeros((len(oraciones), len(oraciones)))
            for idx1 in range(len(oraciones)):
                for idx2 in range(len(oraciones)):
                    # Compara si los indices son iguales
                    if idx1 == idx2:
                        # Si son iguales, no calcula la similaridad
                        continue
                    # Calcula similaridad de dos sentencias
                    res, msj = Texto.calcular_valor_similaridad(
                        oraciones[idx1], oraciones[idx2], stop_words, credenciales
                    )
                    if res is None:
                        return None, msj
                    similarity_matrix[idx1][idx2] = res
            # Devuelve matriz con cálculos de similaridad
            return similarity_matrix, None
        except Exception as e:
            mensaje = f"No se calculó matriz de similaridad, problema imprevisto: {e}"
            logger.exception(mensaje)
            return None, "Error texto"

    @staticmethod
    def resumir_extractivo(
        corpus: str, top_n: int, credenciales: dict = {}
    ) -> tuple[str, str]:
        """Genera resumen extractivo basado en las oraciones con el mayor conteo de
        palabras no stopwords

        Args:
            corpus (str): Texto a resumir con técnica extractiva
            top_n (int): Porcentaje del texto a conservar en el rango <0, 100]
            credenciales (dict): Datos a registrar en el log

        Returns:
            tuple[str, str]: Texto resumido con técnica extractiva y mensaje de error
        """
        # Validar que 'corpus' sea del tipo str
        res, msj = Validaciones.es_tipo(corpus, str, credenciales)
        if not res:
            return None, msj
        # Validar que 'top_n' sea del tipo int
        res, msj = Validaciones.es_tipo(top_n, str, credenciales)
        if not res:
            return None, msj
        # Validar que el porcentaje de resumen esté en el rango <0, 100]
        if 0 < top_n <= 100:
            # Intenta extraer las oraciones más relevantes del corpus
            try:
                # Limpiar y preprocesar el texto
                corpus, msj = Texto.limpiar_corpus(corpus, credenciales)
                if corpus is None:
                    return None, msj
                corpus, msj = Texto.preprocesar_corpus(corpus, credenciales)
                if corpus is None:
                    return None, msj
                texto_resumido = []
                # Lista de oraciones separada en lista de palabras
                oraciones, msj = Texto.separar_por_oraciones(corpus, credenciales)
                if oraciones is None:
                    return None, msj
                # Establece la cantidad de oraciones que contendrá el resumen
                if (top_n := int(len(oraciones) * top_n / 100)) < 1:
                    top_n = 1
                # Calcula la matriz de similaridades de párrafos
                matriz_similaridad, msj = Texto.calcular_matriz_similaridad(
                    oraciones, credenciales
                )
                if matriz_similaridad is None:
                    return None, msj
                # Grafica la matriz
                sentence_similarity_graph = nx.from_numpy_array(matriz_similaridad)
                # Rankea la matriz
                scores = nx.pagerank(sentence_similarity_graph)
                # Conserva los párrafos con mejor puntaje en el top_n
                ranked_sentence = sorted(
                    (
                        (nro_pagina, scores[nro_pagina], lst_palabras)
                        for nro_pagina, lst_palabras in enumerate(oraciones)
                    ),
                    key=lambda index: index[1],
                    reverse=True,
                )[:top_n]
                # Reordena los párrafos en el orden de aparición en el archivo original
                texto_resumido = sorted(
                    (
                        (nro_pagina, " ".join(lst_palabras))
                        for nro_pagina, _, lst_palabras in ranked_sentence
                    ),
                    key=lambda index: index[0],
                )
                texto_resumido = ".\a\a".join([texto for _, texto in texto_resumido])
            except Exception as e:
                mensaje = f"No se obtuvo un resumen, problema imprevisto: {e}"
                logger.exception(mensaje)
                return None, "Error texto"
            # Validar que el resumen tenga al menos un carácter
            if len(texto_resumido) > 0:
                if texto_resumido[-1] != ".":
                    texto_resumido = f"{texto_resumido}."
                return texto_resumido, None
            else:
                mensaje = f"No se obtuvo un resumen, puede aumentar `top_n`: {top_n}"
                logger.error(mensaje)
                return None, "Error texto"
        else:
            mensaje = f"El `top_n` no está en el rango <0, 100], sino es {top_n}"
            logger.error(mensaje)
            return None, "Error texto"
