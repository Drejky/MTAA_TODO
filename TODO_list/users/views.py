from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import psycopg2
from django.views.decorators.csrf import csrf_exempt


def dict_fetch_all(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# @csrf_exempt
def get_user(request, id):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    print("Database opened successfully")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id={};".format(id))
    rows = dict_fetch_all(cur)
    conn.commit()
    conn.close()

    if len(rows) == 0:  # if there is not such a user (by id)
        return HttpResponse("User not found", status=404)

    return JsonResponse(rows[0], safe=False, status=200)

def delete_user(request, id):
    if get_user(request, id).status_code is not 200:
        return HttpResponse("User not found", status=404)
    else:
        conn = psycopg2.connect(database='mtaa', user='postgres',
                                password='postgres',
                                host='localhost', port="5432")
        print("Database opened successfully")
        cur = conn.cursor()
        cur.execute("DELETE  FROM users WHERE user_id={};".format(id))
        conn.commit()
        conn.close()
    return HttpResponse("OK", status=200)

@csrf_exempt
def handle_users(request, id):
    if not id.isnumeric():
        return HttpResponse("Incorrect user id", status=404)

    if request.method == 'GET':
        return get_user(request, id)
    elif request.method == 'DELETE':
        return delete_user(request, id)

