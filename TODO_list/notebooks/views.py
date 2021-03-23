from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import psycopg2, psycopg2.extras
import json
from django.views.decorators.csrf import csrf_exempt


def get_notebook(request, id, cur):
    cur.execute("""SELECT row_to_json(row) FROM(
        SELECT * FROM public.notebooks WHERE notebook_id = {}) row;""".format(id))
    notebook = cur.fetchone()
    if notebook:
        return JsonResponse(notebook[0], safe=False, status = 200)
    else:
        return HttpResponse("Notebook with id doesn't exist", status = 404)

def put_notebook(request, id, cur, conn):
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
    pass

# Create your views here.
@csrf_exempt
def handle_notebooks(request, id):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                                    password='postgres',
                                    host='localhost', port="5432")
    cur = conn.cursor()

#    cur.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
#
#    foo = cur.fetchone()
    if not (id.isnumeric()):
        return HttpResponse("Incorrect id", status = 404)

    if(request.method == "GET"):
        return get_notebook(request, id, cur)

    elif(request.method == "PUT"):
        return put_notebook(request, id, cur, conn)

    elif(request.method == "DELETE"):
        return delete_notebook(request, id, cur, conn)

    cur.close()
    conn.close()

    

