import json
import time

from django.http import JsonResponse, HttpResponse
import psycopg2
from django.views.decorators.csrf import csrf_exempt

import jwt

from django.conf import settings

expire_time_in_seconds = 1200


@csrf_exempt
def login_request(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        name = body['username']
        passw = body['password']

        conn = psycopg2.connect(database='mtaa', user='postgres',
                                password='postgres',
                                host='localhost', port="5432")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT exists (select * from users WHERE (users.user_name = '" + name + "' AND  users.user_passw = '" + passw + "'))")
        # if matched it must return 1
        if cursor.fetchone()[0]:
            # get the details of the user if matched
            cursor.execute("select * from users where users.user_name ='" + name + "'")
            secret_key = settings.SECRET_KEY  # get server's secret key from settings.py
            json_data = dict_fetch_all(cursor)
            actual_json_data = json_data[0]  # dict
        else:
            return HttpResponse("Nope", status=404)

        refresh_token_content = {
            "id": actual_json_data.get('user_id'),
            "username": actual_json_data.get('user_name'),
            "password": actual_json_data.get('user_passw'),
            "email": actual_json_data.get('user_mail')
        }

        refresh_token = {'refreshToken': jwt.encode(refresh_token_content, secret_key)}
        actual_refresh_token = refresh_token.get('refreshToken')

        ts = int(time.time())  # adding issual_time and expire_time
        access_token_content = {
            "id": actual_json_data.get('user_id'),
            "username": actual_json_data.get('username'),
            "password": actual_json_data.get('password'),
            "email": actual_json_data.get('email'),
            "issual_time": ts,
            "expire_time": ts + expire_time_in_seconds
        }

        jwt_token = {'token': jwt.encode(access_token_content, secret_key)}
        actual_access_token = jwt_token.get('token')
        ts = float(time.time())

        final_payload_x = {"user":
            {
                "id": actual_json_data.get('user_id'),
                "userName": actual_json_data.get('user_name'),
                "email": actual_json_data.get('user_mail'),
                "issual_time": int(ts),
                "expire_time": int(ts + expire_time_in_seconds)
            },

            "jwtToken": actual_access_token,
            "refreshToken": actual_refresh_token
        }

        return JsonResponse(final_payload_x, status=200, content_type="application/json")
    return HttpResponse("ahoj")


# TODO treba vyriesit overovanie tokenu (t.j. nie len validitu v case, ale aj aby s tokenom usera a neslo mazat
#  nieco usera b)
@csrf_exempt
def check_if_token_is_valid(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        secret_key = settings.SECRET_KEY
        token = jwt.encode(body, secret_key, algorithm="HS256")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        print(payload.get("user")['userName'])
        received_username = payload.get("user")['userName']
        received_expire_time = payload.get("user")['expire_time']
        received_issual_time = payload.get("user")['issual_time']

        if int(time.time()) > received_expire_time:
            print("current tym", int(time.time()))
            print("expire tym ", received_expire_time)
            print("issue tym  ", received_issual_time)
            return HttpResponse('Token Expired', status=401)

        conn = psycopg2.connect(database='mtaa', user='postgres',
                                password='postgres',
                                host='localhost', port="5432")
        cursor = conn.cursor()
        print("current tym", int(time.time()))
        print("expire tym", received_expire_time)
        print("issue tym", received_issual_time)
        cursor.execute("SELECT exists (select * from users WHERE users.user_name = '" + received_username + "')")
        if cursor.rowcount == 1:
            return HttpResponse("Welcome " + received_username, status=200)
        else:
            return HttpResponse("NOT verified", status=401)
    else:
        return HttpResponse(('Invalid Method'), status=500)


def dict_fetch_all(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


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


def put_user(request, id):
    if get_user(request, id).status_code is not 200:
        return HttpResponse("User not found", status=404)
    else:
        body = json.loads(request.body)
        conn = psycopg2.connect(database='mtaa', user='postgres',
                                password='postgres',
                                host='localhost', port="5432")
        print("Database opened successfully")
        cur = conn.cursor()
        cur.execute("""UPDATE public.users
    SET user_name = '{}', user_passw = '{}', user_mail = '{}' WHERE user_id = {}""".format(
            body['user_name'], body['user_passw'], body['user_mail'], id))
        conn.commit()
        conn.close()
    return HttpResponse("OK", status=200)


@csrf_exempt
def create_user(request):
    if request.method == 'POST':

        body = json.loads(request.body)

        conn = psycopg2.connect(database='mtaa', user='postgres',
                                password='postgres',
                                host='localhost', port="5432")
        print("Database opened successfully")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(user_name, user_passw, user_mail) VALUES (\'{}\', \'{}\', \'{}\') ;".format(
                body['username'], body['password'],
                body['email']))
        conn.commit()
        conn.close()
        return HttpResponse("User created", status=201)
    else:
        return HttpResponse("Bad request", status=400)


@csrf_exempt
def handle_users(request, id):
    if not id.isnumeric():
        return HttpResponse("Incorrect user id", status=404)

    if request.method == 'GET':
        return get_user(request, id)
    elif request.method == 'DELETE':
        return delete_user(request, id)
    elif request.method == 'PUT':
        return put_user(request, id)
    else:
        return HttpResponse("Bad request", status=400)

@csrf_exempt
def handle_userByName(request):
    name = request.GET.get('name', '')
    print(name)

    conn = psycopg2.connect(database='mtaa', user='postgres',
                            password='postgres',
                            host='localhost', port="5432")
    print("Database opened successfully")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_name='{}';".format(name))
    rows = dict_fetch_all(cur)
    conn.commit()
    conn.close()

    if len(rows) == 0:  # if there is not such a user (by id)
        return HttpResponse("User not found", status=404)

    return HttpResponse(rows[0]['user_id'], status=200)
