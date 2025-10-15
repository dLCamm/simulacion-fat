import json
import os
import uuid
from datetime import datetime

documento = 'fat_system.json'
espacio_doc = 20
users = ['ElAdmin', 'Camilo', 'Juanito']
current_user = 'ElAdmin'

for_datos = {"fat": [], "blocks": {}}

def fecha_hora():
    return datetime.utcnow().isoformat() + 'Z'


def datos_carga():
    global for_datos
    if os.path.exists(documento):
        with open(documento, 'r', encoding='utf-8') as f:
            for_datos = json.load(f)
    else:
        for_datos = {"fat": [], "blocks": {}}


def guardar_datos():
    with open(documento, 'w', encoding='utf-8') as f:
        json.dump(for_datos, f, indent=2, ensure_ascii=False)


def encontrar_doc(name):
    for e in for_datos['fat']:
        if e['nombre'] == name:
            return e
    return None

#Para lo s bloques

def crear_blocke(text):
    if text is None:
        text = ''
    partes = [text[i:i+espacio_doc] for i in range(0, len(text), espacio_doc)] or ['']
    primer_id = None
    id_anterior = None
    for i, chunk in enumerate(partes):
        id_blocke = str(uuid.uuid4())
        if primer_id is None:
            primer_id = id_blocke
        for_datos['blocks'][id_blocke] = {
            'datos': chunk,
            'siguiente': None,
            'eof': (i == len(partes) - 1)
        }
        if id_anterior:
            for_datos['blocks'][id_anterior]['siguiente'] = id_blocke
            for_datos['blocks'][id_anterior]['eof'] = False
        id_anterior = id_blocke
    return primer_id


def leer_block(id_inicio):
    contenido = []
    id_blocke = id_inicio
    visited = set()
    while id_blocke and id_blocke not in visited:
        visited.add(id_blocke)
        block = for_datos['blocks'].get(id_blocke)
        if not block:
            break
        contenido.append(block['datos'])
        if block.get('eof'):
            break
        id_blocke = block.get('siguiente')
    return ''.join(contenido)


def eliminarblock(id_inicio):
    id_blocke = id_inicio
    visited = set()
    while id_blocke and id_blocke not in visited:
        visited.add(id_blocke)
        block = for_datos['blocks'].pop(id_blocke, None)
        if not block or block.get('eof'):
            break
        id_blocke = block.get('siguiente')



def creardoc():
    nombre = input('Nombre del archivo: ').strip()
    if not nombre:
        print('Nombre inválido.')
        return
    if encontrar_doc(nombre) and not encontrar_doc(nombre).get('papelera', False):
        print('Ya existe un archivo con ese nombre.')
        return
    contenido = input('Contenido del archivo: ')
    blockeprimero = crear_blocke(contenido)
    now = fecha_hora()
    entry = {
        'nombre': nombre,
        'ruta_datos_inicial': blockeprimero,
        'papelera': False,
        'cantidad_caracteres': len(contenido),
        'fecha_creacion': now,
        'fecha_modificacion': now,
        'fecha_eliminacion': None,
        'usuario': current_user,
        'permisos': {'lectura': [], 'escritura': []}
    }
    for_datos['fat'].append(entry)
    guardar_datos()
    print(f'Archivo "{nombre}" creado correctamente.')


def listardocs():
    print('\n    Archivos')
    archivoo = [f for f in for_datos['fat'] if not f['papelera']]
    if not archivoo:
        print('No hay archivos.')
        return
    for e in archivoo:
        print(f"- {e['nombre']} (usuario: {e['usuario']}) tam: {e['cantidad_caracteres']}")


def ver_papelera():
    print('\nEsta es la Papelera')
    basura = [f for f in for_datos['fat'] if f['papelera']]
    if not basura:
        print('Papelera vacía.')
        return
    for e in basura:
        print(f"- {e['nombre']} eliminado: {e['fecha_eliminacion']}")


def abrirdoc():
    nombre = input('Nombre del archivo: ').strip()
    entry = encontrar_doc(nombre)
    if not entry or entry['papelera']:
        print('Archivo no encontrado o en papelera.')
        return
    if (entry['usuario'] != current_user) and (current_user not in entry['permisos']['lectura']):
        print('Sin permiso de lectura.')
        return
    contenido = leer_block(entry['ruta_datos_inicial'])
    print(f"\n {nombre} \n{contenido}")


def modificacion():
    nombre = input('Ingrese el Nombre del Archivo a modificar: ').strip()
    entry = encontrar_doc(nombre)
    if not entry or entry['papelera']:
        print('Archivo no encontrado o en papelera.')
        return
    if (entry['usuario'] != current_user) and (current_user not in entry['permisos']['escritura']):
        print('Sin permiso de escritura.')
        return
    print('Contenido actual:')
    print(leer_block(entry['ruta_datos_inicial']))
    nuevo = input('Nuevo contenido: ')
    eliminarblock(entry['ruta_datos_inicial'])
    entry['ruta_datos_inicial'] = crear_blocke(nuevo)
    entry['cantidad_caracteres'] = len(nuevo)
    entry['fecha_modificacion'] = fecha_hora()
    guardar_datos()
    print('Archivo modificado.')


def eliminardoc():
    nombre = input('Archivo a eliminar: ').strip()
    entry = encontrar_doc(nombre)
    if not entry or entry['papelera']:
        print('Archivo no encontrado o ya en papelera.')
        return
    entry['papelera'] = True
    entry['fecha_eliminacion'] = fecha_hora()
    guardar_datos()
    print('Archivo movido a papelera.')


def recuperardoc():
    nombre = input('Archivo a recuperar: ').strip()
    entry = encontrar_doc(nombre)
    if not entry or not entry['papelera']:
        print('Archivo no encontrado o no en papelera.')
        return
    entry['papelera'] = False
    entry['fecha_eliminacion'] = None
    guardar_datos()
    print('Archivo recuperado.')


def permisos_manejo():
    nombre = input('Archivo: ').strip()
    entry = encontrar_doc(nombre)
    if not entry:
        print('Archivo no encontrado.')
        return
    if entry['usuario'] != current_user:
        print('Solo el usuario puede gestionar permisos.')
        return
    user = input('Usuario objetivo: ').strip()
    if user not in users:
        print('Usuario no existe.')
        return
    tipo = input('Tipo (lectura/escritura): ').strip()
    accion = input('Acción (permitir/quitar): ').strip()
    if tipo not in ('lectura', 'escritura'):
        print('Tipo inválido.')
        return
    lista = entry['permisos'][tipo]
    if accion == 'permitir':
        if user not in lista:
            lista.append(user)
            print(f'{tipo} permitida a {user}.')
    elif accion == 'quitar':
        if user in lista:
            lista.remove(user)
            print(f'{tipo} revocado a {user}.')
    guardar_datos()


def cambio_usuario():
    global current_user
    print('Usuarios disponibles:', ', '.join(users))
    u = input('Usuario: ').strip()
    if u not in users:
        users.append(u)
        print(f'Usuario {u} creado.')
    current_user = u
    print(f'Usuario actual: {current_user}')

datos_carga()
print(f'Simulador iniciado. Usuario actual: {current_user}')
while True:
    print('''\n Bienvenido a Fat
    Ingrese número según lo que desea hacer:
    1. Crear archivo
    2. Listar archivos
    3. Abrir archivo
    4. Modificar archivo
    5. Eliminar archivo
    6. Papelera
    7. Recuperar archivo
    8. Permisos de los usuarios
    9. Cambiar de usuario
    10. Salir''')
    
    

    op = input(' ').strip()
    if op == '1': 
        creardoc()
        input()
    elif op == '2': 
        listardocs()
        input()
    elif op == '6': 
        ver_papelera()
        input()
    elif op == '3': 
        abrirdoc()
        input()
    elif op == '4': 
        modificacion()
        input()
    elif op == '5': 
        eliminardoc()
        input()
    elif op == '7': 
        recuperardoc()
        input()
    elif op == '8': 
        permisos_manejo()
        input()
    elif op == '9': 
        cambio_usuario()
        input()
    elif op == '10': 
        break
    else: print('Opción inválida.')


