from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

#sends back the info of all the users that follow the passed params userID
@app.route("/api/followers", methods=["GET"])
def get_followers():
    conn = None
    cursor = None
    data_error = {
            "message" : "invalid data sent"
        }
    if request.method == "GET":
        params = request.args
        userID = params.get("userId")
        try:
            if(len(params) == 1):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user.id, user.email, user.username, user.bio, user.birthday, user.image_URL, follow.follower, follow.followed FROM user INNER JOIN follow ON follow.follower=user.id WHERE followed=?",[userID,])
                users_followers = cursor.fetchall()
            #loops through all the fetched info of the users that follow the given userid and formats the data as expected
                follower_list = []
                for follow in users_followers:
                    getDict = {
                        "userId" : follow[0],
                        "email" : follow[1],
                        "username" : follow[2],
                        "bio" : follow[3],
                        "birthdate" : follow[4],
                        "imageURL" : follow[5]
                        }
                    follower_list.append(getDict)
                return Response(json.dumps(follower_list, default=str),
                                        mimetype='application/json',
                                        status=200)
            #if the client sent in no params this else returns a message
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