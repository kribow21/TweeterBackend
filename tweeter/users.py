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

    if request.method == "POST":
        data = request.json
        user_email = data.get("email")         
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
        invalid_email = {
            "messgae" : "please use a valid email"
                    }
        pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
        try:
            datetime.datetime.strptime(user_birthday, '%Y-%m-%d')
        except ValueError:
            return Response(json.dumps(birthday_wrong, default=str),
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
            if(re.search(pattern, user_email) == None):
                return Response(json.dumps(invalid_email,default=str),
                                mimetype='application/json',
                                status=409)
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, username, password, birthday, bio, image_URL) VALUES (?,?,?,?,?,?)",[user_email,user_username,user_password, user_birthday, user_bio, user_image])
        #in order to send back at token you need the userid and token in the data user_session table created
            cursor.execute("SELECT id FROM user WHERE username=?",[user_username,])
            userID = cursor.fetchone()
            print(userID)
            tokenID = uuid4().hex
            cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (?, ?)",[tokenID, userID[0],])
            conn.commit()
        #using a join to bring together all the info i need to return to the client and then organizing it in the format expected
            cursor.execute("SELECT user_session.user_id, user.email, user.username, user.bio, user.birthday, user.image_URL, user_session.login_token FROM user_session INNER JOIN user ON user_session.user_id=user.id WHERE id=?",[userID[0],])
            login_info = cursor.fetchone()
            print(login_info)
            login_resp = {
                "userId" : login_info[0],
                "email" : login_info[1],
                "username" : login_info[2],
                "bio" : login_info[3],
                "birthday" : login_info[4],
                "imageURL" : login_info[5],
                "loginToken" : login_info[6]
            }
            return Response(json.dumps(login_resp, default=str),
                            mimetype='application/json',
                            status=200)
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
    #an if for if the client sent in paramas and else if the client sent in NO paramas
        if(len(client_params) == 1):
            client = client_params.get("user_id")
            try:
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[client,])
                user_info = cursor.fetchone()
                a_user = {
                    "userId" : user_info[0],
                    "email" : user_info[1],
                    "username" : user_info[2],
                    "bio" : user_info[3],
                    "birthday" : user_info[4],
                    "imageURL" : user_info[5],
                }
                return Response(json.dumps(a_user, default=str),
                                            mimetype='application/json',
                                            status=200)
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
        else:
            try:
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user")
                all_users = cursor.fetchall()
            #loops through all the databases info to put in expected format for response
                user_list = []
                for user in all_users:
                    getDict = {
                        "userId" : user[0],
                        "email" : user[1],
                        "username" : user[2],
                        "bio" : user[3],
                        "birthday" : user[4],
                        "imageURL" : user[5]
                        }
                    user_list.append(getDict)
                return Response(json.dumps(user_list, default=str),
                mimetype='application/json',
                status=200)
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
        print(data)
        user_password = data.get("password")
        print(user_password)
        user_token = data.get("loginToken")
        sucess_del = {
            "message" : "user now deleted"
        }
        fail_del = {
            "message" : "something went wrong with deleteing the user"
        }
        if_empty = {
            "message" : "Enter in required data"
        }
        if (user_password == ''):
                return Response(json.dumps(if_empty),
                                mimetype='application/json',
                                status=409)
        if (len(user_token) != 32):
            return Response(json.dumps(fail_del),
                                mimetype='application/json',
                                status=409)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT login_token FROM user_session WHERE login_token=?",[user_token,])
            valid_token = cursor.fetchone()
            if(len(valid_token) != 1):
                    return Response(json.dumps(fail_del, default=str),
                                mimetype="application/json",
                                status=409)
            cursor.execute("SELECT password FROM user WHERE password=?",[user_password,])
            valid_pass = cursor.fetchone()
            if(valid_pass == None):
                    return Response(json.dumps(fail_del, default=str),
                                mimetype="application/json",
                                status=409)
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
                                                status=409)
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
        edit_birthday = data.get("birthday")
        edit_img = data.get("imageURL")
        patch_fail = {
            "message" : "failed to match the login token to a profile"
        }
        try:
            if (len(edit_token) == 32):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[edit_token,])
                varified_user = cursor.fetchone()
                if (len(varified_user) == 1):
                    try:
                        if "bio" in edit_keys:
                            cursor.execute("UPDATE user set bio=? WHERE id=?",[edit_bio, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        elif "email" in edit_keys:
                            cursor.execute("UPDATE user set email=? WHERE id=?",[edit_email, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        elif "username" in edit_keys:
                            cursor.execute("UPDATE user set username=? WHERE id=?",[edit_username, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        elif "birthday" in edit_keys:
                            cursor.execute("UPDATE user set birthday=? WHERE id=?",[edit_birthday, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, username, bio, birthday, image_URL FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        elif "imageURL" in edit_keys:
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
                                "birthday" : user_info[4],
                                "imageURL" : user_info[5],
                            }
                            return Response(json.dumps(a_user, default=str),
                                                    mimetype='application/json',
                                                    status=200)
            else:
                return Response(json.dumps(patch_fail, default=str),
                                    mimetype="application/json",
                                    status=409)
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

