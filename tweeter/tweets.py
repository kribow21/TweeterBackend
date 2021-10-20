from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

@app.route("/api/tweets", methods=["GET","POST","PATCH","DELETE"])
def tweets():
    conn = None
    cursor = None
    tweet_fail = {
        "message" : "failed to post tweet"
    }
    content_error = {
            "message" : "Length of tweet error"
        }
    if request.method == "POST":
        data = request.json
        user_token = data.get("loginToken")
        user_tweet = data.get("content")
    try:
        if (len(user_token) == 32):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id from user_session WHERE login_token=?",[user_token,])
            user_id = cursor.fetchone()
        #checking if user is logged in. if so, allow them to create a tweet
            if (len(user_tweet) <= 200 and len(user_tweet) > 0):
                cursor.execute("INSERT INTO tweet(user_id, content) VALUES (?,?)",[user_id[0], user_tweet])
                conn.commit()
                cursor.execute("SELECT tweet.id, tweet.user_id,user.username, user.image_URL, tweet.content, tweet.created_at, tweet.image_URL FROM tweet INNER JOIN user ON tweet.user_id=user.id WHERE user_id=?",[user_id[0],])
                tweet_info = cursor.fetchone()
                tweet_resp = {
                "tweetId" : tweet_info[0],
                "userId" : tweet_info[1],
                "username" : tweet_info[2],
                "userImageUrl" : tweet_info[3],
                "content" : tweet_info[4],
                "createdAt" : tweet_info[5],
                "imageURL" : tweet_info[6]
                }
                return Response(json.dumps(tweet_resp, default=str),
                            mimetype='application/json',
                            status=200)
            else:
                    return Response(json.dumps(content_error,default=str),
                                mimetype='application/json',
                                status=409)
        else:
            return Response(json.dumps(tweet_fail,default=str),
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
        client_params = request.args
    #if the client sent in paramas and else if the client sent in NO paramas
    try:
        if(len(client_params) == 1):
            client = client_params.get("userId")
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT tweet.id, tweet.user_id, user.username, tweet.content, tweet.created_at, user.image_URL, tweet.image_URL FROM user INNER JOIN tweet ON user.id=tweet.user_id WHERE user_id=?",[client,])
            tweet_info = cursor.fetchall()
            tweet_list = []
            for tweet in tweet_info:
                a_tweet = {
                "tweetId" : tweet[0],
                "userId" : tweet[1],
                "username" : tweet[2],
                "content" : tweet[3],
                "createdAt" : tweet[4],
                "userImageURL" : tweet[5],
                "tweetImageUrl" : tweet[6]
                }
                tweet_list.append(a_tweet)
            return Response(json.dumps(tweet_list, default=str),
                                        mimetype='application/json',
                                        status=200)
        else:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT tweet.id, tweet.user_id, user.username, tweet.content, tweet.created_at, user.image_URL, tweet.image_URL FROM user INNER JOIN tweet ON user.id=tweet.user_id")
            all_tweets = cursor.fetchall()
        #loops through all the databases info to put in expected format for response
            tweets_list = []
            for tweet in all_tweets:
                getDict = {
                "tweetId" : tweet[0],
                "userId" : tweet[1],
                "username" : tweet[2],
                "content" : tweet[3],
                "createdAt" : tweet[4],
                "userImageURL" : tweet[5],
                "tweetImageUrl" : tweet[6]
                    }
                tweets_list.append(getDict)
            return Response(json.dumps(tweets_list, default=str),
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
    if request.method == "PATCH":
        data = request.json
        tweet_token = data.get("loginToken")
        tweet_id = data.get("tweetId")
        tweet_content = data.get("content")
        patch_fail = {
            "message" : "something went wrong with editing your tweet"
        }
        if_empty = {
            "message" : "Enter in required data"
        }
        if (tweet_id == ''):
                    return Response(json.dumps(if_empty, default=str),
                                mimetype='application/json',
                                status=409)
        if (tweet_content == '' or len(tweet_content) > 200 ):
                    return Response(json.dumps(if_empty, default=str),
                                mimetype='application/json',
                                status=409)
        if (len(tweet_token) != 32):
            return Response(json.dumps(patch_fail, default=str),
                                mimetype='application/json',
                                status=409)
    try:
        conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[tweet_token,])
        session_userId = cursor.fetchone()
        cursor.execute("SELECT user_id FROM tweet WHERE id=?",[tweet_id,])
        tweet_userId = cursor.fetchone()
    #checking if the user owns the login token and if the user owns the tweet
        if (session_userId == tweet_userId):
            cursor.execute("UPDATE tweet SET content=? WHERE id=?",[tweet_content,tweet_id])
            conn.commit()
            cursor.execute("SELECT id, content FROM tweet WHERE id=?",[tweet_id,])
            edited_tweet = cursor.fetchone()
            response = {
                "tweetId" : edited_tweet[0],
                "content" : edited_tweet[1]
            }
            return Response(json.dumps(response, default=str),
                                        mimetype='application/json',
                                        status=200)
        else:
            return Response(json.dumps(patch_fail, default=str),
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
        token = data.get("loginToken")
        tweetID = data.get("tweetId")
        delete_fail = {
            "message" : "something went wrong with deleting your tweet"
        }
        confirm = {
            "message" : "tweet deleted"
        }
        data_error = {
            "message" : "something wrong with passed data"
        }
        if (len(token) == 32 and isinstance(tweetID, int) == True):
            try:
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[token,])
                session_userID = cursor.fetchone()
                cursor.execute("SELECT user_id FROM tweet WHERE id=?",[tweetID,])
                tweet_userID = cursor.fetchone()
            #checking if the owner of the token is also the owner of the tweet 
                if(session_userID == tweet_userID):
                    cursor.execute("DELETE from tweet WHERE id=?",[tweetID])
                    conn.commit()
                    return Response(json.dumps(confirm, default=str),
                                        mimetype="application/json",
                                        status=200)
                else:
                    return Response(json.dumps(delete_fail, default=str),
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
        else:
            return Response(json.dumps(data_error, default=str),
                                mimetype='application/json',
                                status=409)
