from app import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import sys

@app.route("/api/users", methods=["GET", "POST", "PATCH", "DELETE" ])
def tweeter_user():
    if request.method == "POST":
        data = request.json
    user_email = data.get("email")
    user_username = data.get("username")
    user_password = data.get("password")
    user_birthday = data.get("birthday")
    user_bio = data.get("bio")
    user_image = data.get("imageURL")
    conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user(email, username, password, birthday, bio, imageURL) VALUES (?,?,?,?,?,?)",[user_email,user_username,user_password, user_birthday, user_bio, user_image])
    conn.commit()
    cursor.close()
    conn.close()
    return Response("Sucessful post created",
                    mimetype='text/plain',
                    status=200)