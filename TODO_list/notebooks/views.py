from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import psycopg2, psycopg2.extras
import json



# Create your views here.
def handle_notebooks(request, id):
    conn = psycopg2.connect(database='mtaa', user='postgres',
                                    password='postgres',
                                    host='localhost', port="5432")
    cur = conn.cursor()

#    cur.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
#
#    foo = cur.fetchone()



    if(request.method == "GET"):
        cur.execute("""SELECT row_to_json(row) FROM(
            SELECT * FROM public.notebooks WHERE notebook_id = {}) row;""".format(id))

        if (cur.fetchone()):
            return JsonResponse(cur.fetchone()[0], safe=False, status = 200)
        else:
            return HttpResponse("User with id doesn't exist", status = 404)

    elif(request.method == "PUT"):
        print("he")

    elif(request.method == "DELETE"):
        print("hi")


    cur.close()
    conn.close()

    