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
        #checking the data before connecting to the database
        if (len(user_token) == 32  and isinstance(tweet_id, int) == True):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[user_token,])
            session_userID = cursor.fetchone()
        #checking the comment is not empty but also isnt over 150 characters before passing to the database
            if(len(user_comment) <= 150 and len(user_comment) > 0):
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
    #expects a tweet id to collect all the comments on that tweet, a loop because there can be more than one comment on a single tweet
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
        com_token = data.get("loginToken")
        com_id = data.get("commentId")
        content_edit = data.get("content")
        patch_fail = {
            "message" : "something went wrong with editing your comment"
        }
        if_empty = {
            "message" : "Enter in required data"
        }
        #before connecting the db check the passed data 
        if (com_id == ''):
            return Response(json.dumps(if_empty, default=str),
                                mimetype='application/json',
                                status=409)
        if (content_edit == ''):
            return Response(json.dumps(if_empty, default=str),
                                mimetype='application/json',
                                status=409)
        if (len(com_token) != 32):
            return Response(json.dumps(patch_fail, default=str),
                                mimetype='application/json',
                                status=409)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[com_token,])
            session_userId = cursor.fetchone()
            cursor.execute("SELECT user_id FROM comment WHERE id=?",[com_id,])
            com_userId = cursor.fetchone()
        #checking if the same userID owns the login token and the comment
            if (session_userId == com_userId):
                cursor.execute("UPDATE comment SET content=? WHERE id=?",[content_edit,com_id])
                conn.commit()
        #return the comment with the newly updated content on the same userID we checked above 
                cursor.execute("SELECT comment.id, comment.tweet_id, comment.user_id, user.username, comment.content, comment.created_at FROM comment INNER JOIN user ON comment.user_id=user.id WHERE user_id=?",[com_userId[0],])
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
        comID = data.get("commentId")
        delete_fail = {
            "message" : "something went wrong with deleting your comment"
        }
        confirm = {
            "message" : "comment deleted"
        }
        data_error = {
            "message" : "something wrong with passed data"
        }
        #before connecting the db check the passed data 
        if (len(token) == 32 and isinstance(comID, int) == True):
            try:
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[token,])
                session_userID = cursor.fetchone()
                cursor.execute("SELECT user_id FROM comment WHERE id=?",[comID,])
                tweet_userID = cursor.fetchone()
            #checking if the owner of the token is also the owner of the comment 
                if(session_userID == tweet_userID):
                    cursor.execute("DELETE from comment WHERE id=?",[comID])
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