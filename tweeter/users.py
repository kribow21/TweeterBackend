from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime


@app.route("/api/users", methods=["GET", "POST", "PATCH", "DELETE" ])
def tweeter_user():
    conn = None
    cursor = None

    if request.method == "POST":
        data = request.json
    user_email = data.get("email")         #TODO: figure out regex 
    user_username = data.get("username")   
    user_password = data.get("password")   
    user_birthday = data.get("birthday")
    user_bio = data.get("bio")
    user_image = data.get("image_URL")
    if_empty = {
        "message" : "Enter in required data"
    }
    birthday_wrong = {
                "message" : "Enter in correct format"
                }
    try:
        datetime.datetime.strptime(user_birthday, '%Y-%m-%d')
    except ValueError:
        return Response(json.dumps(birthday_wrong),
                            mimetype='application/json',
                            status=409)
    try:
        if (user_email == ''):
            return Response(json.dumps(if_empty),
                            mimetype='application/json',
                            status=409)
        elif (user_username == ''):
            return Response(json.dumps(if_empty),
                            mimetype='application/json',
                            status=409)
        elif (user_password == ''):
            return Response(json.dumps(if_empty),
                            mimetype='application/json',
                            status=409)
        conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user(email, username, password, birthday, bio, image_URL) VALUES (?,?,?,?,?,?)",[user_email,user_username,user_password, user_birthday, user_bio, user_image])
    #in order to send back at token you need the userid in the data user_session table created
        cursor.execute("SELECT id FROM user WHERE username=?",[user_username,])
        userID = cursor.fetchone()
        print(userID)
        cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (UUID(), ?)",[userID[0],])
        conn.commit()
        return Response("Sucessful user created",
                        mimetype='text/plain',
                        status=200)
        # return Response(json.dumps(, default=str),
        #                 mimetype='application/json',
        #                 status=409)
    except mariadb.DataError: 
        print('Something went wrong with your data')
    except mariadb.OperationalError:
        print('Something wrong with the connection')
    except mariadb.ProgrammingError:
        print('Your query was wrong')
    except mariadb.IntegrityError:
        print('Your query would have broken the database and we stopped it')
    except mariadb.InterfaceError:
        print('Something wrong with database interface')
    except:
        print('Something went wrong')
    finally:
        if(cursor != None):
            cursor.close()
            print('cursor closed')
        else:
            print('no cursor to begin with')
        if(conn != None):   
            conn.rollback()
            conn.close()
            print('connection closed')
        else:
            print('the connection never opened, nothing to close')