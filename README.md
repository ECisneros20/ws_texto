# ws_texto

# 1. Descripción del proyecto

Se entrega un template de proyecto con lo siguiente:

<table border="1">
    <tr>
        <th>Carpeta / Archivo</th>
        <th>Ejemplos</th>
        <th>Descripción</th>
    </tr>
    <tr>
        <td>log/</td>
        <td>20240802.log, log.csv, ...</td>
        <td>archivo de registro de actividades, se sugiere uno por proyecto back-end</td>
    </tr>
    <tr>
        <td>models/</td>
        <td>modelo_rf.pkl, modelo_pred.h5, ...</td>
        <td>modelos de ML o DL entrenados a partir de la información en data</td>
    </tr>
    <tr>
        <td>notebooks/</td>
        <td>prueba.ipynb, ...</td>
        <td>notebooks para pruebas de nuevas librerías, modelos o algoritmos</td>
    </tr>
    <tr>
        <td>reports/</td>
        <td>prueba_resumen.docx, metricas.jpg, ...</td>
        <td>carpeta con archivos de salida agrupados por número de expediente u otros criterios (audios, csv, docs, imgs)</td>
    </tr>
    <tr>
        <td>scripts/</td>
        <td>prueba.py, ...</td>
        <td>scripts para pruebas de nuevas librerías, modelos o algoritmos</td>
    </tr>
    <tr>
        <td>src/</td>
        <td>main.py, ...</td>
        <td>código principal y funciones específicas del proyecto</td>
    </tr>
    <tr>
        <td>tests/</td>
        <td>test_ocr.py, ...</td>
        <td>pruebas unitarias y de integración</td>
    </tr>
    <tr>
        <td>tmp/</td>
        <td>ESTADISTICA.xlsx, ...</td>
        <td>archivos temporales o de prueba no necesarios que se crean para no perdurar en el proyecto</td>
    </tr>
    <tr>
        <td>.gitignore</td>
        <td>-</td>
        <td>permite ignorar archivos al actualizar el repo en git</td>
    </tr>
    <tr>
        <td>CHANGELOG.rst</td>
        <td>-</td>
        <td>muestra un registro de cambios manual al actualizar el repo en git</td>
    </tr>
    <tr>
        <td>README.md</td>
        <td>-</td>
        <td>pasos para setear el proyecto</td>
    </tr>
</table>

Se deben de crear estas carpetas manualmente porque no se guardan en git sino en un backup FTP

<table border="1">
    <tr>
        <th>Carpeta / Archivo</th>
        <th>Ejemplos</th>
        <th>Descripción</th>
    </tr>
    <tr>
        <td>data/</td>
        <td>audiencia.mp4, ...</td>
        <td>carpeta con archivos de entrada como datasets para entrenamiento de modelos (audios, csv, docs, imgs) o agrupados por número de expediente para procesar expedientes</td>
    </tr>
</table>

# 2. Realizar cambios al template

Si se quieren hacer cambios en la estructura de este template, colocar el siguiente comando (asegurarse de crear un token y tener acceso al repo privado). No hay más pasos:
```bash
git clone -b develop https://<token>@github.com/ECisneros20/back_end_template.git
```

# 3. Utilizar el template para un nuevo proyecto (tiene que estar dentro de un proyecto front-end)

Si se quiere emplear el template para un nuevo proyecto, colocar el siguiente comando (asegurarse de crear un token y tener acceso al repo privado):
```bash
git clone https://<token>@github.com/ECisneros20/back_end_template.git
```

## 3.1. Renombrar proyecto template por nombre del proyecto

No usar espacios, sino guiones bajo. Cambiar nombre de la carpeta raíz y el título del archivo README.md con el nuevo nombre del proyecto.

## 3.2. Borrar archivo oculto .git y reiniciar nuevo proyecto en GitHub

Ubicarse en la ruta principal del proyecto y colocar los siguientes comandos:
```bash
git init -b main
git add .
git commit -m "0.1.0 - setup inicial"
```

Crear repositorio en GitHub con el mismo nombre del proyecto nuevo sin archivos extras, usar la sección "Adding a local repository to GitHub using Git" de este [link](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github). Luego subir la información del repo local al repo de GitHub:
```bash
git remote add origin <REMOTE-URL>
git push origin main
```

Crear un branch develop en GitHub, copiando el main recién creado y luego clonar este branch al repo local. Esta parte final se hace de la siguiente manera:
```bash
git branch --set-upstream-to=origin/main main
git pull
git checkout develop
```

## 3.3. Clonar repo con el codebase desarrollado utils

Ubicarse en la ruta principal y colocar el siguiente comando (asegurarse de crear un token y tener acceso al repo privado):
```bash
git clone https://<token>@github.com/ECisneros20/utils.git
```

Adicionalmente, este repo utils se encuentra en desarrollo constante, por lo que se sugiere actualizarlo. Ubicarse en la ruta principal de utils y colocar el siguiente comando:
```bash
cd utils
git pull
```

## 3.4. Revisar el archivo README.md del codebase utils clonado para configuración extra

## 3.5. Copiar archivo .env dentro de la ruta principal del proyecto clonado
El archivo .env incluye credenciales y datos sensibles que no se suben a git por seguridad
