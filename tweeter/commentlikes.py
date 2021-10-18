from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

@app.route("/api/comment-likes", methods=["GET","POST","DELETE"])
def commentlikes():
    conn = None
    cursor = None
    data_error = {
            "message" : "invalid data sent"
        }
    if request.method == "POST":
        try:
            data = request.json
            commentID = data.get("commentId")
            token = data.get("loginToken")
            repeat = {
                "message" : "conflict, user already liked"
            }
            resp = {
                "message" : "like OK"
            }
            if (len(token) == 32 and isinstance(commentID, int) == True):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[token,])
                user_id = cursor.fetchone()
                cursor.execute("SELECT * FROM comment_like WHERE comment_id=? AND user_id=?",[commentID, user_id[0]])
                already_liked = cursor.fetchone()
            # checking if those two inputs already exsist in the db , if not it returns none if they do exsist the variable will have a length of 2
                if(already_liked == None):
                    cursor.execute("INSERT INTO comment_like(comment_id, user_id) VALUES (?,?)",[commentID, user_id[0]])
                    conn.commit()
                    return Response(json.dumps(resp, default=str),
                                        mimetype='application/json',
                                        status=200)
                elif(len(already_liked) == 2):
                    return Response(json.dumps(repeat, default=str),
                                    mimetype='application/json',
                                    status=409)
                # returns if the user sent in data that does not match the if statement about the token being 32 and the commentid being a int
            else:
                return Response(json.dumps(data_error, default=str),
                                    mimetype='application/json',
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