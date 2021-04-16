from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import psycopg2
import json
from django.views.decorators.csrf import csrf_exempt
import base64
import requests


def get_notebook(request, id, cur):
    cur.execute("""SELECT row_to_json(row) FROM(
        SELECT * FROM public.notebooks WHERE notebook_id = {}) row;""".format(id))
    notebook = cur.fetchone()
    if notebook:
        return JsonResponse(notebook[0], safe=False, status=200)
    else:
        return HttpResponse("Notebook with id doesn't exist", status=404)


def put_notebook(request, id, cur, conn):
    temp = get_notebook(request, id, cur)
    if temp.status_code is not 200:
        return temp

    body = json.loads(request.body)
    if not body['label']:
        body['label'] = 'null'
    if not body['collaborator_id']:
        body['collaborator_id'] = 'null'
    if not body['notebook_icon']:
        body['notebook_icon'] = 'null'

    cur.execute("""UPDATE public.notebooks
    SET notebook_name = '{}', label = '{}', 
    notebook_color = '{}', collaborator_id = {}, notebook_icon = {}, update_date = CURRENT_DATE
    WHERE notebook_id = {};""".format(body['notebook_name'], body['label'],
                                      body['notebook_color'], body['collaborator_id'], body['notebook_icon'], id))
    conn.commit()

    return get_notebook(request, id, cur)


def delete_notebook(request, id, cur, conn):
    response = requests.post('http://127.0.0.1:8000/users/auth/valid', request.body)
    print(response)
    if response.status_code == 200:
        temp = get_notebook(request, id, cur)
        if temp.status_code is not 200:
            return temp

        cur.execute("""DELETE FROM public.notebooks WHERE notebook_id = {}""".format(id))
        conn.commit()

        return HttpResponse("Succesfully deleted", status=200)
    return HttpResponse("Not veriefied", status=401)


def create_notebook(request, cur, conn):
    body = json.loads(request.body)
    if not body['label']:
        body['label'] = 'null'
    if not body['collaborator_id']:
        body['collaborator_id'] = 'null'
    if not body['notebook_icon']:
        body['notebook_icon'] = 'null'

    cur.execute("""INSERT INTO public.notebooks (creator_id, creator_date, notebook_type,
    notebook_name, label, notebook_color, update_date, collaborator_id,
    notebook_icon) VALUES ({}, CURRENT_DATE, {}, '{}', '{}', '{}',
    CURRENT_DATE, {}, '{}');""".format(body['creator_id'], body['notebook_type'],
                                       body['notebook_name'], body['label'], body['notebook_color'],
                                       body['collaborator_id'], body['notebook_icon']))
    conn.commit()

    return HttpResponse("Notebook succesfully created", status=201)


def get_notebooks(request, cur, conn):
    cur.execute("""SELECT row_to_json(row) FROM(SELECT notebook_id, creator_id, creator_date,
    notebook_type, notebook_name, label, notebook_color, update_date, collaborator_id 
    FROM public.notebooks) as row;""")

    notebooks = []
    notebook = cur.fetchone()
    while (True):
        if not notebook:
            break

        notebooks.append(notebook[0])
        notebook = cur.fetchone()

    return JsonResponse(notebooks, safe=False, status=200)


def get_note(request, id, note_id, cur):
    temp = get_notebook(request, id, cur)
    if temp.status_code is not 200:
        return temp

    cur.execute("""SELECT row_to_json(row) FROM(
        SELECT * FROM public.notes WHERE note_id = {} AND notebook_id = {}) row;""".format(
        note_id, id))
    note = cur.fetchone()
    if note:
        return JsonResponse(note[0], safe=False, status=200)
    else:
        return HttpResponse("Note with id doesn't exist", status=404)


def put_note(request, id, note_id, cur, conn):
    temp = get_note(request, id, note_id, cur)
    if temp.status_code is not 200:
        return temp

    body = json.loads(request.body)

    cur.execute("""UPDATE public.notes
    SET name = '{}', note_content = '{}' WHERE note_id = {}""".format(
        body['name'], body['note_content'], note_id))
    conn.commit()

    return get_note(request, id, note_id, cur)


def delete_note(request, id, note_id, cur, conn):
    temp = get_note(request, id, note_id, cur)
    if temp.status_code is not 200:
        return temp

    cur.execute("""DELETE FROM public.notes WHERE note_id = {}""".format(note_id))
    conn.commit()

    return HttpResponse("Succesfully deleted", status=200)


def get_icon(request, id, cur):
    cur.execute("""SELECT notebook_icon FROM public.notebooks where notebook_id = {}""".format(id))
    return HttpResponse(cur.fetchone()[0].tobytes(), content_type="image/jpeg")


def post_icon(request, id, cur, conn):
    body = json.loads(request.body)
    data = base64.b64decode(body['base64'])

    cur.execute("""UPDATE public.notebooks SET notebook_icon = {} where
    notebook_id = {}""".format(psycopg2.Binary(data), id))
    conn.commit()

    return HttpResponse("Succesfully uploaded image", status=200)


def post_note(request, id, cur, conn):
    if not id.isnumeric():
        return HttpResponse("Incorrect id", status=404)

    body = json.loads(request.body)

    cur.execute("""
    insert into public.notes (notebook_id, name, create_date, update_date,
	note_type, note_content) values ({}, '{}', 
    CURRENT_DATE, CURRENT_DATE, {}, '{}');""".format(
        id, body['name'], body['note_type'], body['note_content']
    ))

    conn.commit()


def get_notes(request, id, cur):
    cur.execute("""SELECT row_to_json(row) FROM(
        SELECT * FROM public.notes WHERE notebook_id = {}) row;""".format(id))

    notes = []
    note = cur.fetchone()
    while (True):
        if not note:
            break

        notes.append(note[0])
        note = cur.fetchone()

    return JsonResponse(notes, safe=False, status=200)


@csrf_exempt
def get_types(request):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    cur = conn.cursor()

    cur.execute("""SELECT row_to_json(row) FROM(SELECT * FROM public.notebook_types) as row;""")

    types = []
    temp = cur.fetchone()
    while (True):
        if not temp:
            break
        types.append(temp[0])
        temp = cur.fetchone()

    cur.close()
    conn.close()
    return JsonResponse(types, safe=False, status=200)


@csrf_exempt
def handle_notebooks(request):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    cur = conn.cursor()

    if request.method == 'POST':
        return create_notebook(request, cur, conn)
    elif request.method == 'GET':
        return get_notebooks(request, cur, conn)

    cur.close()
    conn.close()


@csrf_exempt
def handle_notebook(request, id):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    cur = conn.cursor()

    if id == 'notebook_types':
        return get_types(request)
    elif not id.isnumeric():
        return HttpResponse("Incorrect id", status=404)

    if request.method == "GET":
        return get_notebook(request, id, cur)

    elif request.method == "PUT":
        return put_notebook(request, id, cur, conn)

    elif request.method == "DELETE":
        return delete_notebook(request, id, cur, conn)

    cur.close()
    conn.close()


@csrf_exempt
def handle_notes(request, id, note_id):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    cur = conn.cursor()
    if (not id.isnumeric()) or (not note_id.isnumeric()):
        return HttpResponse("Incorrect id", status=404)

    if request.method == "GET":
        return get_note(request, id, note_id, cur)

    elif request.method == "PUT":
        return put_note(request, id, note_id, cur, conn)

    elif request.method == "DELETE":
        return delete_note(request, id, note_id, cur, conn)

    cur.close()
    conn.close()


@csrf_exempt
def handle_note(request, id):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    cur = conn.cursor()

    if request.method == "POST":
        return post_note(request, id, cur, conn)
    elif request.method == "GET":
        return get_notes(request, id, cur)

    cur.close()
    conn.close()
    return HttpResponse("Note succsesfully created", status=200)


@csrf_exempt
def handle_icons(request, id):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    cur = conn.cursor()

    if request.method == "POST":
        return post_icon(request, id, cur, conn)
    elif request.method == "GET":
        return get_icon(request, id, cur)

    conn.commit()
    cur.close()
    conn.close()

@csrf_exempt
def handle_userNotebooks(request, id):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    cur = conn.cursor()

    cur.execute("""SELECT row_to_json(row) FROM(SELECT notebook_id, creator_id, creator_date,
    notebook_type, notebook_name, label, notebook_color, update_date, collaborator_id 
    FROM public.notebooks WHERE creator_id = {}) as row;""".format(id))

    notebooks = []
    notebook = cur.fetchone()
    while (True):
        if not notebook:
            break

        notebooks.append(notebook[0])
        notebook = cur.fetchone()
        
    cur.close()
    conn.close()

    return JsonResponse(notebooks, safe=False, status=200)
