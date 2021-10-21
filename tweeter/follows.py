from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
#a user following another user. followID refers to the person being followed follower is the user passing the token
@app.route("/api/follows", methods=["GET","POST","DELETE"])
def get_follows():
    conn = None
    cursor = None
    data_error = {
            "message" : "invalid data sent"
        }
    if request.method == "POST":
        data = request.json
        followerToken = data.get("loginToken")
        followedID = data.get("followId")
        resp = {
                "message" : "follow OK"
            }
        db_error = {
            "message" : "CONFLICT data passed failed contraint in database"
        }
        #checking the data passed to ensure its what the database expects before connecting to it. else catches if its not whats expected
        try:
            if (len(followerToken) == 32 and isinstance(followedID, int) == True):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
        #using the token to find the userID of the person currently logged in trying to make a follow relationship
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[followerToken,])
                follower_user_id = cursor.fetchone()
                print(follower_user_id)
            else:
                return Response(json.dumps(data_error, default=str),
                                        mimetype='application/json',
                                        status=401)
        #use the collected userID to insert the relationship into the table
            try:
                cursor.execute("INSERT INTO follow (follower, followed) VALUES (?,?)",[follower_user_id[0], followedID])
                conn.commit()
                return Response(json.dumps(resp, default=str),
                                        mimetype='application/json',
                                        status=201)
            except mariadb.DataError: 
                print('Something went wrong with your data')
            except mariadb.OperationalError:
                print('Something wrong with the connection')
            except mariadb.ProgrammingError:
                print('Your query was wrong')
            except mariadb.IntegrityError:
                print('Your query would have broken the database and we stopped it')
        #catching the error from the database so that repeat follows and following yourself are not permitted 
                return Response(json.dumps(db_error, default=str),
                                        mimetype='application/json',
                                        status=409)
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

    if request.method == "GET":
        params = request.args
        followerID = params.get("userId")
    #expects a parma and if it doesnt get one the else with respond
        try:
            if(len(params) == 1):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user.id, user.email, user.username, user.bio, user.birthday, user.image_URL, follow.follower, follow.followed FROM user INNER JOIN follow ON follow.followed=user.id WHERE follower=?",[followerID,])
                users_followed = cursor.fetchall()
        #grabbing all the info about all the (followers)users that passed followID(userID) follows
                follow_list = []
                for follow in users_followed:
                    getDict = {
                        "userId" : follow[0],
                        "email" : follow[1],
                        "username" : follow[2],
                        "bio" : follow[3],
                        "birthday" : follow[4],
                        "imageURL" : follow[5]
                        }
                    follow_list.append(getDict)
                return Response(json.dumps(follow_list, default=str),
                                        mimetype='application/json',
                                        status=200)
            else:
                return Response(json.dumps(data_error, default=str),
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
    if request.method == "DELETE":
        data = request.json
        follower_token = data.get("loginToken")
        followed_id = data.get("followId")
        delete_fail = {
            "message" : "something went wrong with deleting your follow"
        }
        confirm = {
            "message" : "follow deleted"
        }
        data_error = {
            "message" : "something wrong with passed data"
        }
        #to unfollow a user the token and followID(userID) are passed and checked for expected data
        try:
            if (len(follower_token) == 32 and isinstance(followed_id, int) == True):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[follower_token,])
                session_userID = cursor.fetchone()
                cursor.execute("SELECT follower FROM follow WHERE followed=?",[followed_id])
                follower_userID = cursor.fetchone()
            #comparing if the userID of the passed token also owns the follow relationship where they are the follower
                if(session_userID == follower_userID):
                    cursor.execute("DELETE from follow WHERE follower=? AND followed=?",[session_userID[0], followed_id])
                    conn.commit()
                    return Response(json.dumps(confirm, default=str),
                                        mimetype="application/json",
                                        status=200)
                else:
                    return Response(json.dumps(delete_fail, default=str),
                                    mimetype='application/json',
                                    status=401)
            else:
                return Response(json.dumps(data_error, default=str),
                                mimetype='application/json',
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