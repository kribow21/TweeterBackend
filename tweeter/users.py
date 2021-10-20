from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime
import re
from uuid import uuid4


@app.route("/api/users", methods=["GET", "POST", "PATCH", "DELETE" ])
def tweeter_user():
    conn = None
    cursor = None
    if_empty = {
            "message" : "Enter in required data"
        }
    birthday_wrong = {
                    "message" : "Enter in correct format"
                    }
    invalid_email = {
            "messgae" : "please use a valid email"
                    }
    pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
    len_error = {
        "message" : "Length of input exceeds limit"
    }
    if request.method == "POST":
        data = request.json
        user_email = data.get("email")         
        user_username = data.get("username")   
        user_password = data.get("password")   
        user_birthday = data.get("birthdate")
        user_bio = data.get("bio")
        user_image = data.get("imageUrl")
        try:
            #datetime is a module that has a class called datetime that has the proper format to check if the passed datetime match
            datetime.datetime.strptime(user_birthday, '%Y-%m-%d')
        except ValueError:
            return Response(json.dumps(birthday_wrong, default=str),
                                mimetype='application/json',
                                status=409)
        try:
            if (user_email == ''):
                return Response(json.dumps(if_empty, default=str),
                                mimetype='application/json',
                                status=409)
            elif (len(user_username) > 31 and len(user_username) > 0):
                return Response(json.dumps(len_error, default=str),
                                mimetype='application/json',
                                status=409)
            elif (len(user_password) > 21 and len(user_password) > 0):
                return Response(json.dumps(len_error,default=str),
                                mimetype='application/json',
                                status=409)
            #used regular expression to match the passed email to the pattern above
            if(re.search(pattern, user_email) == None):
                return Response(json.dumps(invalid_email,default=str),
                                mimetype='application/json',
                                status=409)
            if(len(user_bio) > 101):
                return Response(json.dumps(len_error,default=str),
                                mimetype='application/json',
                                status=409)
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, username, password, birthday, bio, image_URL) VALUES (?,?,?,?,?,?)",[user_email,user_username,user_password, user_birthday, user_bio, user_image])
        #in order to send back a token you need to create a token in the data user_session table created with the selected id 
            cursor.execute("SELECT id FROM user WHERE username=?",[user_username,])
            userID = cursor.fetchone()
            tokenID = uuid4().hex
            cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (?, ?)",[tokenID, userID[0],])
            conn.commit()
        #using a join to bring together all the info needed to return to the client and then organizing it in the format expected
            cursor.execute("SELECT user_session.user_id, user.email, user.username, user.bio, user.birthday, user.image_URL, user_session.login_token FROM user_session INNER JOIN user ON user_session.user_id=user.id WHERE id=?",[userID[0],])
            login_info = cursor.fetchone()
            print(login_info)
            login_resp = {
                "userId" : login_info[0],
                "email" : login_info[1],
                "username" : login_info[2],
                "bio" : login_info[3],
                "birthdate" : login_info[4],
                "imageUrl" : login_info[5],
                "loginToken" : login_info[6]
            }
            return Response(json.dumps(login_resp, default=str),
                            mimetype='application/json',
                            status=201)
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

    elif request.method == "GET":
        client_params = request.args
        print(client_params)
    #if the client sent in paramas and else if the client sent in NO paramas
        try:
            if(len(client_params) == 1):
                client = client_params.get("userId")
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[client,])
                user_info = cursor.fetchone()
                a_user = {
                    "userId" : user_info[0],
                    "email" : user_info[1],
                    "username" : user_info[2],
                    "bio" : user_info[3],
                    "birthdate" : user_info[4],
                    "imageUrl" : user_info[5],
                }
                return Response(json.dumps(a_user, default=str),
                                            mimetype='application/json',
                                            status=200)
            else:
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user")
                all_users = cursor.fetchall()
            #loops through all the user databases info to put in expected format for response
                user_list = []
                for user in all_users:
                    getDict = {
                        "userId" : user[0],
                        "email" : user[1],
                        "username" : user[2],
                        "bio" : user[3],
                        "birthdate" : user[4],
                        "imageUrl" : user[5]
                        }
                    user_list.append(getDict)
                return Response(json.dumps(user_list, default=str),
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

    elif request.method == "DELETE":
        data = request.json
        user_password = data.get("password")
        user_token = data.get("loginToken")
        sucess_del = {
            "message" : "user now deleted"
        }
        fail_del = {
            "message" : "something went wrong with deleteing the user"
        }
        #checking passed data 
        if (len(user_password) > 21 and len(user_password) > 0):
                return Response(json.dumps(if_empty),
                                mimetype='application/json',
                                status=400)
        if (len(user_token) != 32):
            return Response(json.dumps(fail_del),
                                mimetype='application/json',
                                status=400)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT login_token FROM user_session WHERE login_token=?",[user_token,])
            valid_token = cursor.fetchone()
            if(len(valid_token) != 1):
                    return Response(json.dumps(fail_del, default=str),
                                mimetype="application/json",
                                status=401)
            cursor.execute("SELECT password FROM user WHERE password=?",[user_password,])
            valid_pass = cursor.fetchone()
            if(valid_pass == None):
                    return Response(json.dumps(fail_del, default=str),
                                mimetype="application/json",
                                status=401)
            #first checks if the token is in the db, then id the password is in the db and if they are and match then they have the permission to delete the user
            if (valid_token[0] == user_token and valid_pass[0] == user_password):
                cursor.execute("DELETE FROM user_session WHERE login_token=?",[valid_token[0]])
                cursor.execute("DELETE FROM user WHERE password=?",[user_password,])
                conn.commit()
                if (cursor.rowcount == 1):
                    return Response(json.dumps(sucess_del, default=str),
                                                mimetype='application/json',
                                                status=200)
                else:
                    return Response(json.dumps(fail_del, default=str),
                                                mimetype="application/json",
                                                status=400)
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
                
    elif request.method == "PATCH":
        data = request.json
        edit_token = data.get("loginToken")
        edit_keys = data.keys()
        print(edit_keys)
        edit_bio = data.get("bio")
        edit_email = data.get("email")
        edit_username = data.get("username")
        edit_birthday = data.get("birthdate")
        edit_img = data.get("imageUrl")
        patch_fail = {
            "message" : "failed to match the login token to a profile"
        }
        if(edit_bio != None and len(edit_bio) > 100):
                    return Response(json.dumps(len_error,default=str),
                                mimetype='application/json',
                                status=400)
        if(edit_birthday!= None):
            try:
                datetime.datetime.strptime(edit_birthday, '%Y-%m-%d')
            except ValueError:
                return Response(json.dumps(birthday_wrong, default=str),
                                    mimetype='application/json',
                                    status=400)
        if(edit_email != None):
            if(re.search(pattern, edit_email) == None):
                    return Response(json.dumps(invalid_email,default=str),
                                mimetype='application/json',
                                status=400)
        if (edit_username != None and len(edit_username) > 31):
                    return Response(json.dumps(len_error),
                                mimetype='application/json',
                                status=400)
        #checks passed data before connecting to db
        try:
            if (len(edit_token) == 32):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                #from the token grab the userid to then make changes to the users info
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[edit_token,])
                varified_user = cursor.fetchone()
                if (len(varified_user) == 1):
                    try:
                        if "bio" in edit_keys:
                            cursor.execute("UPDATE user set bio=? WHERE id=?",[edit_bio, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        if "email" in edit_keys:
                            cursor.execute("UPDATE user set email=? WHERE id=?",[edit_email, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        if "username" in edit_keys:
                            cursor.execute("UPDATE user set username=? WHERE id=?",[edit_username, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        if "birthdate" in edit_keys:
                            cursor.execute("UPDATE user set birthday=? WHERE id=?",[edit_birthday, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        if "imageUrl" in edit_keys:
                            cursor.execute("UPDATE user set image_URL=? WHERE id=?",[edit_img, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                    finally:
                            a_user = {
                                "userId" : user_info[0],
                                "email" : user_info[1],
                                "username" : user_info[2],
                                "bio" : user_info[3],
                                "birthdate" : user_info[4],
                                "imageUrl" : user_info[5],
                            }
                            return Response(json.dumps(a_user, default=str),
                                                    mimetype='application/json',
                                                    status=200)
            else:
                return Response(json.dumps(patch_fail, default=str),
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

