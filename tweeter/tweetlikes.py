from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

@app.route("/api/tweet-likes", methods=["GET","POST","DELETE"])
def tweetlikes():
    conn = None
    cursor = None
    data_error = {
            "message" : "invalid data sent"
        }
    if request.method == "POST":
        data = request.json
        tweetID = data.get("tweetId")
        repeat = {
            "message" : "conflict, user already liked"
        }
        resp = {
            "message" : "like OK"
        }
    try:
        token = data.get("loginToken")
        if (len(token) == 32 and isinstance(tweetID, int) == True):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[token,])
            user_id = cursor.fetchone()
            cursor.execute("SELECT * FROM tweet_like WHERE tweet_id=? AND user_id=?",[tweetID, user_id[0]])
            already_liked = cursor.fetchone()
        # checking if those two inputs already exsist in the db , if not it returns none if they do exsist the variable will have a length of 2
            if(already_liked == None):
                cursor.execute("INSERT INTO tweet_like(tweet_id, user_id) VALUES (?,?)",[tweetID, user_id[0]])
                conn.commit()
                return Response(json.dumps(resp, default=str),
                                    mimetype='application/json',
                                    status=200)
            #if it hits this the like already exsists
            elif(len(already_liked) == 2):
                return Response(json.dumps(repeat, default=str),
                                mimetype='application/json',
                                status=409)
            # returns if the user sent in data that does not match the if statement about the token being 32 and the tweetid being a int
        else:
            return Response(json.dumps(data_error, default=str),
                                mimetype='application/json',
                                status=409)
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

    if request.method == "GET":
        params = request.args
        tweet_ID = params.get("tweetId")
        print(tweet_ID)
    try:
        #sends back all the likes with expected data response
        if (tweet_ID == None):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT tweet_like.tweet_id , tweet_like.user_id,user.username FROM tweet_like INNER JOIN user ON tweet_like.user_id=user.id")
            everyones_likes = cursor.fetchall()
            like_coll = []
            for like in everyones_likes:
                collection = {
                        "tweetId" : like[0],
                        "userId" : like[1],
                        "username" : like[2]
                    }
                like_coll.append(collection)
            return Response(json.dumps(like_coll, default=str),
                                    mimetype='application/json',
                                    status=200)
        #sends back all the likes on that tweetID and the info of who liked that tweet
        elif (len(params) == 1):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT tweet_like.tweet_id , tweet_like.user_id,user.username FROM tweet_like INNER JOIN user ON tweet_like.user_id=user.id WHERE tweet_id=?",[tweet_ID,])
            all_likes = cursor.fetchall()
            tweet_likes = []
            for likes in all_likes:
                resp = {
                    "tweetId" : likes[0],
                    "userId" : likes[1],
                    "username" : likes[2]
                }
                tweet_likes.append(resp)
            return Response(json.dumps(tweet_likes, default=str),
                                mimetype='application/json',
                                status=200)
        else:
            return Response(json.dumps(data_error, default=str),
                                mimetype='application/json',
                                status=409)
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
        loginTok = data.get("loginToken")
        tweetid = data.get("tweetId")
        delete_fail = {
            "message" : "something went wrong with editing your like"
        }
        confirm = {
            "message" : "tweet like deleted"
        }
        data_error = {
            "message" : "something wrong with passed data"
        }
    try:
        if (len(loginTok) == 32 and isinstance(tweetid, int) == True):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[loginTok,])
            session_userID = cursor.fetchone()
            cursor.execute("SELECT user_id FROM tweet_like WHERE tweet_id=?",[tweetid,])
            tweetlike_userID = cursor.fetchone()
        #checking if the owner of the token is also the owner of the tweet like
            if(session_userID == tweetlike_userID):
                cursor.execute("DELETE from tweet_like WHERE tweet_id=?",[tweetid])
                conn.commit()
                return Response(json.dumps(confirm, default=str),
                                    mimetype="application/json",
                                    status=200)
            else:
                return Response(json.dumps(delete_fail, default=str),
                                mimetype='application/json',
                                status=409)
        else:
            return Response(json.dumps(data_error, default=str),
                                mimetype='application/json',
                                status=409)
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




