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
            print(user_id)
            if (len(user_id) == 1):
                cursor.execute("INSERT INTO tweet(user_id, content) VALUES (?,?)",[user_id[0], user_tweet])
                conn.commit()
                cursor.execute("SELECT tweet.id, tweet.user_id,user.username, tweet.content, tweet.created_at FROM tweet INNER JOIN user ON tweet.user_id=user.id WHERE user_id=?",[user_id[0],])
                tweet_info = cursor.fetchone()
                tweet_resp = {
                "tweetId" : tweet_info[0],
                "userId" : tweet_info[1],
                "username" : tweet_info[2],
                "content" : tweet_info[3],
                "createdAt" : tweet_info[4]
                }
                return Response(json.dumps(tweet_resp, default=str),
                            mimetype='application/json',
                            status=200)
        else:
            return Response(json.dumps(tweet_fail,default=str),
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