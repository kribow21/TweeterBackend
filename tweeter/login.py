from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime
from uuid import uuid4
import re


@app.route("/api/login", methods=["POST", "DELETE"])
def login():
    conn = None
    cursor = None
    pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"

    if request.method == "POST":
        data = request.json
        user_email = data.get("email")
        user_pass = data.get("password")
        if_empty = {
            "message" : "Enter in required data"
        }
        invalid_email = {
            "messgae" : "please use a valid email"
                    }
        fail_login = {
            "message" : "Failed to login"
        }
    #checks if things are empty or not correct email format before opening db
        if (user_email == ''):
            return Response(json.dumps(if_empty),
                                mimetype='application/json',
                                status=400)
        elif(re.search(pattern, user_email) == None):
            return Response(json.dumps(invalid_email,default=str),
                                mimetype='application/json',
                                status=400)
        elif (user_pass == ''):
            return Response(json.dumps(if_empty),
                                mimetype='application/json',
                                status=400)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT password,id from user WHERE email=?",[user_email,])
            user_info = cursor.fetchone()
        #accounts for if password does not match or email does not match. the elif if it does match
            if(user_info == None):
                    return Response(json.dumps(fail_login, default=str),
                                            mimetype='application/json',
                                            status=401)
            #if userid's correspond then create/insert a token for their session
            elif (user_pass == user_info[0]):
                tokenID = uuid4().hex
                cursor.execute("INSERT INTO user_session (login_token,user_id) VALUES (?,?)",[tokenID,user_info[1]])
                conn.commit()
            else:
                return Response(json.dumps(fail_login, default=str),
                                            mimetype='application/json',
                                            status=401)
            if (user_info != None):
                cursor.execute("SELECT user_session.user_id, user.email, user.username, user.bio, user.birthday, user_session.login_token, user.image_URL FROM user_session INNER JOIN user ON user_session.user_id=user.id WHERE user_id=?",[user_info[1],])
                select_user = cursor.fetchone()
                a_user = {
                    "userId" : select_user[0],
                    "email" : select_user[1],
                    "username" : select_user[2],
                    "bio" : select_user[3],
                    "birthdate" : select_user[4],
                    "loginToken" : select_user[5],
                    "imageUrl" : select_user[6]
                }
                return Response(json.dumps(a_user, default=str),
                                            mimetype='application/json',
                                            status=200)
        except mariadb.DatabaseError:
            print('Something went wrong with connecting to database')
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

    if request.method == "DELETE":
        data = request.json
        user_token = data.get("loginToken")
        invalid = {
            "message" : "invalid token"
        }
        confirm = {
            "message" : "valid token, deleted"
        }
        try:
            if (len(user_token) == 32):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                print(user_token)
                cursor.execute("DELETE FROM user_session WHERE login_token=?",[user_token,])
                conn.commit()
                if (cursor.rowcount ==1):
                    return Response(json.dumps(confirm, default=str),
                                    mimetype="application/json",
                                    status=200)
            else:
                return Response(json.dumps(invalid, default=str),
                                mimetype="application/json",
                                status=401)
        except mariadb.DatabaseError:
            print('Something went wrong with connecting to database')
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