
from flask import Flask, request, redirect, render_template, session, redirect

from functions.DataBaseConnection import connect, DBInsert, sql_delete,sql_edit,sql_query_var, sql_query, getIDTypes, getCategories

from functions.methods import random_key, hashPasswd, getExtension, getNameWithoutExtension

from adminController import admin_controller

from user_controller import user_controller

from functions.Persistence import generarCSVJugadores

import os




app = Flask(__name__)




@app.route('/')
def sql_database():
    
    return render_template('index.html', failedAttempt = False)   

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        print(request.form["email"] + "  :  "+ request.form["password"] + "\n" + hashPasswd(request.form["password"]))
        inputName = request.form["email"]
        if inputName == "admin":
            if hashPasswd(request.form["password"]) == "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918":
                session["user"] = "admin"
                return render_template("admin_home.html")

            else:
                return render_template('index.html', failedAttempt = True)

            
        else:
            passwdsQuery = '''SELECT CoachKey, PassHash FROM Coach
                            WHERE UserName like %s'''
            
            print (inputName)
            inputPassHash = hashPasswd(request.form["password"])
            storedhashes = sql_query_var(passwdsQuery, (inputName,))
            print (storedhashes)
            loggedIn = False
            for dic in storedhashes:
                if inputPassHash == dic["PassHash"]:
                    loggedIn = True
                    session["user"] = str(dic["CoachKey"])
                    infoCoach = sql_query('''SELECT FirstName, LastName, EPS, ID, IDType FROM Coach WHERE CoachKey = "''' + session["user"] + '''";''')[0]
            if loggedIn:
                CoachHasNoInfo = False
                print("Bienvenido " + session["user"])
                for infop in infoCoach:
                    if not CoachHasNoInfo:
                        CoachHasNoInfo = infoCoach[infop] is None
                        
                        print(infop, infoCoach[infop])



                if CoachHasNoInfo:
                    tiposID = getIDTypes()
                    return render_template("info_entrenador.html", IDTypes = tiposID)
                else: 
                    print("ingresó un entrenador que tiene información")
                    coachHasTeams = False
                    coachNTeamsQuery = '''SELECT COUNT(CoachKey) AS '#Equipos' FROM Team WHERE CoachKey = ''' + session["user"]
                    coachNTeams = sql_query(coachNTeamsQuery)[0]["#Equipos"]
                    if coachNTeams > 0:
                        coachHasTeams = True
                    
                    if coachHasTeams:
                        return redirect('/verJugadoresInscritos')

                        
                    else:
                        return render_template("info_equipos.html")
            
            else:
                return render_template("index.html", failedAttempt = True)



#############################################################ADMIN#METHODS###############################################################



app.register_blueprint(admin_controller, url_prefix='')



######################################################COACHES METHODS################################################################

app.register_blueprint(user_controller, url_prefix='')


    

if __name__ == "__main__":
    
    app.secret_key = random_key()
    print(app.secret_key)
    app.run(debug= True )

