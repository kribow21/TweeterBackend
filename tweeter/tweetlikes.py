from sys import version_info
from tweeter import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

@app.route("/api/tweet-likes", methods=["GET","POST","DELETE"])
def tweetlikes():
    if request.method == "POST":
        pass