from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime
import re

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
            cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (UUID(), ?)",[userID[0],])
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
                print(all_users)
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
        sucess_del = {
            "message" : "user now deleted"
        }
        fail_del = {
            "message" : "something went wrong with deleteing the user"
        }
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user.password, user_session.login_token FROM user_session INNER JOIN user ON user_session.user_id=user.id WHERE password=?",[user_password,])
            user_info_for_deleteing = cursor.fetchone()
            if (user_info_for_deleteing != None):
                cursor.execute("DELETE FROM user_session WHERE login_token=?",[user_info_for_deleteing[1]])
                cursor.execute("DELETE FROM user WHERE password=?",[user_info_for_deleteing[0]])
                conn.commit()
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
        patch_fail = {
            "message" : "failed to match the login token to a profile"
        }
        try:
            if (len(edit_token) == 36):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_session WHERE login_token=?",[edit_token,])
                varified_user = cursor.fetchone()
                if (varified_user == 1):
                    pass
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

