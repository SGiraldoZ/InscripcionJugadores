
from flask import Flask, request, redirect, render_template, session, redirect

from functions.DataBaseConnection import connect, DBInsert, sql_delete,sql_edit,sql_query_var, sql_query, getIDTypes, getCategories

from functions.methods import random_key, hashPasswd, getExtension, getNameWithoutExtension

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
            if hashPasswd(request.form["password"]) == "04ec614eed673d26b74660602044740195302cce31372a6c7ac9dd155f58df91":
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
@app.route('/personToEdit', methods = ["POST","GET"])
def personToEdit():
    if 'user' in session:
        if request.method == "GET":
                Key = request.args.get("personKey")

                eresult = sql_query_var('''SELECT PersonKey, FirstName, LastName, IDType, ID 
                                                    FROM Person 
                                                    WHERE PersonKey = %s;''',(personKey,))
                print (eresult[0])


                TiposID = getIDTypes()
                            
                return render_template("agregar_asistentes.html", eresult = eresult[0], IDTypes = TiposID)
    else:
        return render_template("index.html")


@app.route('/personEdit', methods=['POST','GET'])
def personEdit():
    if 'user' in session:
        if request.method == "POST":
            assisKey = request.form["PersonKey"]
            PersonFName = request.form["FirstName"]
            PersonLName = request.form["LastName"]
            PersonIDType = request.form["IDType"]
            PersonID = request.form["ID"]
            PersonInsertQuery = '''UPDATE Person
                                    SET FirstName = %s,
                                    LastName = %s,
                                    IDType = %s,
                                    ID = %s
                                    WHERE PersonKey = %s;'''
            DBInsert(PersonInsertQuery, (PersonFName, PersonLName,  PersonIDType,
                    PersonID, assisKey))

            return redirect('/agregar_personas')
    else:
        return render_template("index.html")

@app.route('/PersonDelete', methods = ['POST','GET'])
def deletePerson():
    if 'user' in session:
        if request.method == 'GET':
            personKey = request.args.get("personKey")
            assisDeleteQuery = '''DELETE FROM Person WHERE PersonKey = %s'''
            sql_delete(assisDeleteQuery,(personKey,))
            return redirect('/agregar_personas')

    else:
        return redirect('/')




@app.route('/agregar_personas', methods = ['POST','GET'])
def load_personas():
    if 'user' in session:
        if request.method == 'GET':
            
            results = sql_query('''Select PersonKey, FirstName, LastName, IDType, ID FROM Person;''')
            return render_template('agregar_personas.html', IDTypes = getIDTypes(), results = results)
    else:
        return render_template('index.html')


@app.route('/insertPerson', methods = ["POST", "GET"])
def insertPerson():
    if 'user' in session:
        if request.method == "POST":
            PersonFName = request.form["FirstName"]
            PersonLName = request.form["LastName"]
          
            PersonIDType = request.form["IDType"]
            PersonID = request.form["ID"]
            PersonInsertQuery = '''INSERT INTO Person(FirstName, LastName, IDType, ID)
                                    Values(%s,%s,%s,%s);'''
            DBInsert(PersonInsertQuery, (PersonFName, PersonLName,  PersonIDType,
                    PersonID))

            
            
            return redirect("/agregar_personas")
    else:
        return render_template("index.html")



@app.route('/coaches', methods = ['POST', 'GET'])
def load_Coaches():
    if "user" in session:
        if session['user'] == "admin":
            if request.method == 'GET':
                coachesQuery = '''SELECT CoachKey, UserName FROM Coach;'''
                result = sql_query(coachesQuery)
                print(result)
                return render_template("entrenadores.html", results = result)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")

@app.route('/partidos', methods = ['POST', 'GET'])
def load_partidos():
    if "user" in session:
        if session['user'] == "admin":
            if request.method == 'GET':

                return render_template("partidos.html", categorias=getCategories())
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@app.route('/goles', methods = ['POST', 'GET'])
def load_goles():
    if "user" in session:
        if session['user'] == "admin":
            if request.method == 'GET':
                return render_template("goles.html", categorias=getCategories())
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")



@app.route('/insertNewCoach', methods = ['POST', 'GET'])
def createCoach():
    if 'user' in session:
        if session['user'] == 'admin':
            if request.method == 'POST':
                newUserName = request.form["UserName"]
                newPassHash = hashPasswd(request.form["Password"])
                createCoachQuery = '''INSERT INTO Coach(UserName, PassHash)
                                    VALUES(%s, %s);'''
                DBInsert(createCoachQuery, (newUserName, newPassHash))
                coachesQuery = '''SELECT CoachKey, UserName FROM Coach;'''
                result = sql_query(coachesQuery)
                print (result)
                return render_template('entrenadores.html', results = result)
        else:
            render_template("index.html")
    else:
        return render_template("index.html")

@app.route('/toEditCoach', methods= ['POST', 'GET'])
def toEditCoach():
    if 'user' in session:
        if session["user"]=='admin':
            if request.method == 'GET':
                eCoachKey = request.args.get("toEditCoachKey")
                eresultsQuery = '''SELECT CoachKey, UserName FROM Coach
                                    WHERE CoachKey = %s;'''
                eresults = sql_query_var(eresultsQuery, (eCoachKey,))
                coachesQuery = '''SELECT CoachKey, UserName FROM Coach;'''
                result = sql_query(coachesQuery)
                return render_template('entrenadores.html', results = result, eresults = eresults)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")

@app.route('/editCoach', methods = ['POST', 'GET'])
def editCoach():
    if 'user' in session:
        if session['user'] == 'admin':
            if request.method == 'POST':
                eCoachKey = request.form["CoachKey"]
                newUserName = request.form["UserName"]
                newPasswd = hashPasswd(request.form["Password"])

                editQuery = '''UPDATE Coach
                                SET UserName = %s, passHash = %s
                                WHERE CoachKey = %s;'''
                sql_edit(editQuery, (newUserName, newPasswd, eCoachKey))

                coachesQuery = '''SELECT CoachKey, UserName FROM Coach;'''
                result = sql_query(coachesQuery)
                print (result)
                return render_template('entrenadores.html', results = result)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@app.route('/deleteCoach', methods=['POST', 'GET'])
def deleteCoach():
    if 'user' in session:
        if session["user"] == "admin":
            if request.method == 'GET':
                dCoachKey = request.args.get("toDeleteCoachKey")
                
                deleteCoachQueries = []

                deleteCoachQueries.append('''DELETE FROM Goal
                                WHERE PlayerKey IN (SELECT P.PlayerKey FROM Player P LEFT OUTER JOIN Team T
                                                        ON T.TeamKey = P.TeamKey
                                                    WHERE T.CoachKey = %s
                                                            OR T.CoachKey = %s);''')

                deleteCoachQueries.append('''DELETE FROM Game
                                WHERE TeamOneKey IN (SELECT TeamKey FROM Team WHERE CoachKey = %s)
                                        OR TeamTwoKey IN (SELECT TeamKey FROM Team WHERE CoachKey = %s);''')

                deleteCoachQueries.append('''DELETE FROM Player WHERE TeamKey IN (SELECT TeamKey FROM Team WHERE CoachKey = %s OR CoachKey = %s);''')

                deleteCoachQueries.append('''DELETE FROM Team WHERE CoachKey = %s OR CoachKey = %s;''')

                deleteCoachQueries.append('''DELETE FROM Coach
                                WHERE CoachKey = %s OR CoachKey = %s;''')

                for query in deleteCoachQueries:
                    sql_delete(query, (dCoachKey,dCoachKey))
                coachesQuery = '''SELECT CoachKey, UserName FROM Coach;'''
                result = sql_query(coachesQuery)
                return render_template('entrenadores.html', results = result)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")
            








######################################################COACHES METHODS################################################################
@app.route('/assistantToEdit', methods = ["POST","GET"])
def assistantToEdit():
    if 'user' in session:
        if request.method == "GET":
            assistantKey = request.args.get("assistantKey")

            eresult = sql_query_var('''SELECT AssistantKey, FirstName, LastName, IDType, ID 
                                                FROM Assistant 
                                                WHERE AssistantKey = %s;''',(assistantKey,))
            print (eresult[0])


            TiposID = getIDTypes()
                        
            return render_template("agregar_personas.html", eresult = eresult[0], IDTypes = TiposID)
    else:
        return render_template("index.html")


@app.route('/AssistantEdit', methods=['POST','GET'])
def assitantEdit():
    if 'user' in session:
        if request.method == "POST":
            assisKey = request.form["AssistantKey"]
            AssistantFName = request.form["FirstName"]
            AssistantLName = request.form["LastName"]
            AssistantIDType = request.form["IDType"]
            AssistantID = request.form["ID"]
            AssistantInsertQuery = '''UPDATE Assistant
                                    SET FirstName = %s,
                                    LastName = %s,
                                    IDType = %s,
                                    ID = %s
                                    WHERE AssistantKey = %s;'''
            DBInsert(AssistantInsertQuery, (AssistantFName, AssistantLName,  AssistantIDType,
                    AssistantID, assisKey))

            return redirect('/agregarAsistentes')
    else:
        return render_template("index.html")

@app.route('/AssistantDelete', methods = ['POST','GET'])
def assistantDelete():
    if 'user' in session:
        if request.method == 'GET':
            assistantKey = request.args.get("dAssistantKey")
            assisDeleteQuery = '''DELETE FROM Assistant WHERE AssistantKey = %s'''
            sql_delete(assisDeleteQuery,(assistantKey,))
            return redirect('/agregarAsistentes')

    else:
        return redirect('/')

@app.route('/verJugadoresInscritos', methods = ['POST','GET'])
def cargarJugadoresResults():
    if 'user' in session:
        if request.method == "GET":
            results = sql_query('''SELECT P.PlayerKey, P.EPS, P.FirstName, P.LastName, P.IDType, P.ID, P.DBirth, P.PictureURL, T.CategoryKey
                                            FROM Coach C LEFT OUTER JOIN Team T
                                            ON C.CoachKey = T.CoachKey
                                            RIGHT OUTER JOIN Player P
                                            ON T.TeamKey = P.TeamKey
                                            WHERE C.CoachKey = '''+ session["user"]+';')
            categorias = sql_query('''SELECT Ca.CategoryName, Ca.CategoryKey FROM Category Ca RIGHT OUTER JOIN Team T
                            ON T.CategoryKey = Ca.CategoryKey
                            WHERE T.CoachKey = ''' + session["user"]+";")

                                                        
            return render_template("verJugadoresInscritos.html", results=results, categories = categorias)
    else:
        return render_template("index.html")


@app.route('/agregarAsistentes', methods = ['POST','GET'])
def load_asistentes():
    if 'user' in session:
        if request.method == 'GET':
            
            results = sql_query('''Select AssistantKey, FirstName, LastName, IDType, ID FROM Assistant WHERE CoachKey = ''' + session["user"] + ''';''')
            return render_template('agregar_asistentes.html', IDTypes = getIDTypes(), results = results)
    else:
        return render_template('index.html')

@app.route('/playerToEdit', methods = ["POST","GET"])
def playerToEdit():
    if 'user' in session:
        if request.method == "GET":
            playerKey = request.args.get("ePlayerKey")

            eresult = sql_query_var('''SELECT P.PlayerKey, P.EPS, P.FirstName, P.LastName, P.IDType, P.ID, P.DBirth, T.CategoryKey, P.PictureURL
                                                FROM Coach C LEFT OUTER JOIN Team T
                                                ON C.CoachKey = T.CoachKey
                                                RIGHT OUTER JOIN Player P
                                                ON T.TeamKey = P.TeamKey
                                                WHERE P.PlayerKey = %s;''',(playerKey,))
            print (eresult)
            categorias = sql_query('''SELECT Ca.CategoryName, Ca.CategoryKey FROM Category Ca RIGHT OUTER JOIN Team T
                                    ON T.CategoryKey = Ca.CategoryKey
                                    WHERE T.CoachKey = ''' + session["user"]+";")
            print(categorias)

            TiposID = getIDTypes()
                        
            return render_template("agregar_jugadores.html",categories = categorias, eresult = eresult[0], IDTypes = TiposID)
    else:
        return render_template("index.html")


@app.route('/playerEdit', methods=['POST', 'GET'])
def updatePlayer():
    if 'user' in session:
        
        if request.method == 'POST':
            FirstName = request.form["FirstName"]
            LastName = request.form["LastName"]
            EPS = request.form["EPS"]
            IDType = request.form["IDType"]
            ID = request.form["ID"]
            DBirth = request.form["DBirth"]
            playerKey = request.form["playerKey"]
            

            editQuery = '''UPDATE Player SET
                        FirstName = %s,
                        LastName = %s,
                        EPS = %s,
                        IDType = %s,
                        ID = %s,
                        DBirth = %s
                        WHERE playerKey = %s'''

            pictureURLQuery =  ("SELECT PictureURL FROM Player WHERE PlayerKey = %s;")
            pictureURL = sql_query_var(pictureURLQuery, (playerKey,))[0]['PictureURL']
            
            sql_edit(editQuery,(FirstName,LastName,EPS,IDType,ID,DBirth,playerKey))
            print("ya alteré la información")
            try:
                picture = request.files["playerPicture"]
            except:
                picture = None

            print("ya revisé si existe la imagen")
            if picture is not None:
                print("existe")
                if os.path.exists(pictureURL):
                    print("la imagen debería estar en: " +pictureURL)
                    print("toca borrar")
                    os.remove(pictureURL)
                    print("ya la borré")
                    newURL = getNameWithoutExtension(pictureURL)+"."+(getExtension(request.files['playerPicture'].filename))
                    print (newURL)
                    print ("voy a guardar la imagen en: " + newURL)
                    request.files["playerPicture"].save(newURL)
                    print("ya la guardé")
                    sql_edit('''UPDATE Player
                                SET PictureURL = %s
                                WHERE PlayerKey = %s;''',(newURL,playerKey))
                else:
                    print ("no toca borrar")
                    newURL = getNameWithoutExtension(pictureURL)+(getExtension(request.files['playerPicture'].filename))
                    print ("voy a guardar la imagen en: " + newURL)
                    request.files["playerPicture"].save(newURL)
                    print("ya la guardé")
                    sql_edit('''UPDATE Player
                                SET PictureURL = %s
                                WHERE PlayerKey = %s;''',(newURL,playerKey))
        
            return redirect('/verJugadoresInscritos')
    else:
        return render_template("index.html")

@app.route('/playerDelete', methods = ["POST","GET"])
def playerDelete():
    if 'user' in session:
        if request.method == "GET":
            deleteQuery  = '''DELETE FROM Player WHERE PlayerKey = %s;'''

            DelPlayerKey = request.args.get("dPlayerKey")
            sql_delete(deleteQuery, (DelPlayerKey,))
            print ("se borró el jugador " + DelPlayerKey)
            
            return redirect('verJugadoresInscritos')
    else:
        return render_template("index.html")

@app.route('/insertAssistant', methods = ["POST", "GET"])
def insertAssistant():
    if 'user' in session:
        if request.method == "POST":
            AssistantFName = request.form["FirstName"]
            AssistantLName = request.form["LastName"]
          
            AssistantIDType = request.form["IDType"]
            AssistantID = request.form["ID"]
            AssistantInsertQuery = '''INSERT INTO Assistant(FirstName, LastName, IDType, ID, CoachKey)
                                    Values(%s,%s,%s,%s,''' + session["user"] +");"
            DBInsert(AssistantInsertQuery, (AssistantFName, AssistantLName,  AssistantIDType,
                    AssistantID))

            
            
            return redirect("/agregar_asistentes")
    else:
        return render_template("index.html")


@app.route('/insertCoach', methods = ["POST", "GET"])
def insertCoach():
    if 'user' in session:
        if request.method == "POST":
            CoachFName = request.form["FirstName"]
            CoachLName = request.form["LastName"]
            CoachEps = request.form["EPS"]
            CoachIDType = request.form["IDType"]
            CoachID = request.form["ID"]
            CoachInsertQuery = '''UPDATE Coach
                                    SET FirstName = %s,
                                    LastName = %s,
                                    EPS = %s,
                                    IDType = %s,
                                    ID = %s
                                    WHERE CoachKey = ''' + session["user"] +";"
            DBInsert(CoachInsertQuery, (CoachFName, CoachLName, CoachEps, CoachIDType,
                    CoachID))
            
            return render_template("info_equipos.html")
    else:
        return render_template("index.html")

@app.route('/agregar_jugadores', methods = ['POST', 'GET'])
def CargarAgregar_jugadores():
    if 'user' in session:
        if request.method=='GET':
            results = sql_query('''SELECT P.PlayerKey, P.EPS, P.FirstName, P.LastName, P.IDType, P.ID, P.DBirth
                        FROM Coach C LEFT OUTER JOIN Team T
                        ON C.CoachKey = T.CoachKey
                        RIGHT OUTER JOIN Player P
                        ON T.TeamKey = P.TeamKey
                        WHERE C.CoachKey = '''+ session["user"]+';')
            categorias = sql_query('''SELECT Ca.CategoryName, Ca.CategoryKey FROM Category Ca RIGHT OUTER JOIN Team T
                                    ON T.CategoryKey = Ca.CategoryKey
                                    WHERE T.CoachKey = ''' + session["user"]+";")
            print(categorias)
            numeroJugadoresParaInscribir = 7
            TiposID = getIDTypes()
                    
            return render_template("agregar_jugadores.html",categories = categorias, results=results, numPlayers = numeroJugadoresParaInscribir, IDTypes = TiposID)
    else:
        return render_template("index.html")


@app.route('/defineNumPlayers', methods = ['POST','GET'])
def ActualizarNumPlayers():
    if 'user' in session:    
        if request.method == 'POST':
            results = sql_query('''SELECT P.PlayerKey, P.EPS, P.FirstName, P.LastName, P.IDType, P.ID, P.DBirth
                            FROM Coach C LEFT OUTER JOIN Team T
                            ON C.CoachKey = T.CoachKey
                            RIGHT OUTER JOIN Player P
                            ON T.TeamKey = P.TeamKey
                            WHERE C.CoachKey = '''+ session["user"]+';')
            categorias = sql_query('''SELECT Ca.CategoryName, Ca.CategoryKey FROM Category Ca RIGHT OUTER JOIN Team T
                                    ON T.CategoryKey = Ca.CategoryKey
                                    WHERE T.CoachKey = ''' + session["user"]+";")
            print(categorias)
            numeroJugadoresParaInscribir = int(request.form["numPlayers"])
            TiposID = getIDTypes()
        
            return render_template("agregar_jugadores.html",categories = categorias, results=results, numPlayers = numeroJugadoresParaInscribir, IDTypes = TiposID)
    else:
        return render_template("index.html")


@app.route('/insertTeams', methods = ["POST","GET"])
def createTeams():
    if 'user' in session:
        if request.method == "POST":
            clubCoach = request.form["ClubName"]

            addCoachClubQuery = '''UPDATE Coach
                                    SET ClubName = %s
                                    WHERE CoachKey = ''' + session["user"] + ';'
            
            addTeamQuery = '''INSERT INTO Team(TeamName, CoachKey, CategoryKey)
                            VALUES(%s,''' + session["user"] + ', (SELECT CategoryKey FROM Category WHERE CategoryName LIKE %s));'
            
            DBInsert(addCoachClubQuery,(clubCoach,))

            if request.form.get("infantil") == "on":
                DBInsert(addTeamQuery, (clubCoach,"infantil"))

            if request.form.get("cadetemasculino") == "on":
                DBInsert(addTeamQuery, (clubCoach,"cadetes masculino"))
            
            if request.form.get("cadetefemenino") == "on":
                DBInsert(addTeamQuery, (clubCoach,"cadetes femenino"))
            
            print("En teoría, se insertaron los equipos")
        
            return redirect('/agregar_jugadores')
    else:
        return render_template("index.html")


@app.route('/insertPlayers', methods = ['POST','GET'])
def insertPlayer():
    if 'user' in session:
        if request.method == 'POST':
            
            photos = request.files.getlist("playerPicture")
            category = request.form["categoriaJugador"]
            FirstName = request.form.getlist("FirstName")
            LastName = request.form.getlist("LastName")
            EPS = request.form.getlist("EPS")
            IDType = request.form.getlist("IDType")
            ID = request.form.getlist("ID")
            DBirth = request.form.getlist("DBirth")
            insertPlayerQuery = '''INSERT INTO Player(EPS, FirstName, LastName, IDType, ID, DBirth, TeamKey)
                                        VALUES(%s,%s,%s,%s,%s,%s,
                                        (SELECT TeamKey FROM Team 
                                        WHERE CoachKey = ''' + session["user"] + ''' AND CategoryKey = %s))'''
            var = (EPS[0], FirstName[0], LastName[0], IDType[0], ID[0], DBirth[0], category)

            print(IDType)
            print("\n")
            print(ID)


            
            for n in range(1, len(FirstName)):
                addValuesQuery = '''(%s,%s,%s,%s,%s,%s,
                                        (SELECT TeamKey FROM Team 
                                        WHERE CoachKey = ''' + session["user"] + ''' AND CategoryKey = %s))'''
                insertPlayerQuery += "," + addValuesQuery
                var = var + (EPS[n], FirstName[n], LastName[n], IDType[n], ID[n], DBirth[n], category)


                            
            insertPlayerQuery += ";"
            
            DBInsert(insertPlayerQuery,var)                
                
            for n in range(len(FirstName)):    
                playerKeyQuery = '''SELECT MAX(PlayerKey) FROM Player
                                WHERE FirstName LIKE %s
                                AND LastName LIKE %s
                                AND EPS LIKE %s
                                AND IDType = %s
                                AND ID LIKE %s
                                AND DBirth LIKE %s;'''
                playerKey = sql_query_var(playerKeyQuery, (FirstName[n], LastName[n], EPS[n], IDType[n], ID[n], DBirth[n]))[0]
                updatePictureURL = ("UPDATE Player SET PictureURL = 'Uploaded/Players/" + str(playerKey["MAX(PlayerKey)"]) +"." +getExtension(photos[n].filename)+
                                    "' WHERE PlayerKey = "+str(playerKey["MAX(PlayerKey)"]) +";")
                
                sql_edit(updatePictureURL, None)

                photos[n].save("Uploaded/Players/" +  str(playerKey["MAX(PlayerKey)"]) +"."+ getExtension(photos[n].filename))
                


                       
            return redirect('/verJugadoresInscritos')
    else:
        return render_template("index.html")



        


    

if __name__ == "__main__":
    
    app.secret_key = random_key()
    print(app.secret_key)
    app.run(debug= True )

