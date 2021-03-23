from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import psycopg2


def dict_fetch_all(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# Create your views here.
def handle_users(request, id):
    if not id.isnumeric():
        return HttpResponse("Incorrect user id", status=404)
    if request.method == 'GET':
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

    return JsonResponse(rows[0], safe=False)
