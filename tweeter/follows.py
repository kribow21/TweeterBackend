from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

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
        try:
            if (len(followerToken) == 32 and isinstance(followedID, int) == True):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[followerToken,])
                follower_user_id = cursor.fetchone()
                print(follower_user_id)
            else:
                return Response(json.dumps(data_error, default=str),
                                        mimetype='application/json',
                                        status=409)
            try:
                cursor.execute("INSERT INTO follow (follower, followed) VALUES (?,?)",[follower_user_id[0], followedID])
                conn.commit()
                return Response(json.dumps(resp, default=str),
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

