from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

@app.route("/api/comments", methods=["GET","POST","PATCH","DELETE"])
def comments():
    conn = None
    cursor = None

    if request.method == "POST":
        data = request.json
        user_token = data.get("loginToken")
        tweet_id = data.get("tweetId")
        user_comment = data.get("content")
        comment_fail = {
        "message" : "failed to post comment"
            }
        content_error = {
            "message" : "Length of comment error"
        }
    try:
        if (len(user_token) == 32  and isinstance(tweet_id, int) == True):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[user_token,])
            session_userID = cursor.fetchone()
            if(len(user_comment) <= 120 and len(user_comment) > 0):
                cursor.execute("INSERT INTO comment (tweet_id, content, user_id) VALUES (?,?,?)",[tweet_id, user_comment, session_userID[0]])
                conn.commit()
                cursor.execute("SELECT comment.id, comment.tweet_id, comment.user_id, user.username, comment.content, comment.created_at FROM comment INNER JOIN user ON comment.user_id=user.id WHERE user_id=?",[session_userID[0],])
                comment_info = cursor.fetchone()
                resp = {
                    "commentId" : comment_info[0],
                    "tweetId" : comment_info[1],
                    "userId" : comment_info[2],
                    "username" : comment_info[3],
                    "content" : comment_info[4],
                    "createdAt" : comment_info[5]
                }
                return Response(json.dumps(resp, default=str),
                                mimetype='application/json',
                                status=200)
            else:
                return Response(json.dumps(content_error,default=str),
                                mimetype='application/json',
                                status=409)
        else:
            return Response(json.dumps(comment_fail,default=str),
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
    if request.method == "GET":
            params = request.args
            tweetID = params.get("tweetId")
            data_error = {
            "message" : "something wrong with passed data"
            }
    try:
        if(len(params) == 1):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT comment.id, comment.tweet_id, comment.user_id, user.username, comment.content, comment.created_at FROM comment INNER JOIN user ON comment.user_id=user.id WHERE tweet_id=?",[tweetID,])
            all_comments = cursor.fetchall()
            comment_list = []
            for comment in all_comments:
                resp = {
                "commentId" : comment[0],
                "tweetId" : comment[1],
                "userId" : comment[2],
                "username" : comment[3],
                "content" : comment[4],
                "createdAt" : comment[5]
                }
                comment_list.append(resp)
            return Response(json.dumps(comment_list, default=str),
                                        mimetype='application/json',
                                        status=200)
        else:
            return Response(json.dumps(data_error, default=str),
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