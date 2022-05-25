from flask import Blueprint, request, redirect, render_template, session, redirect

from functions.DataBaseConnection import connect, DBInsert, sql_delete,sql_edit,sql_query_var, sql_query, getIDTypes, getCategories

from functions.methods import random_key, hashPasswd, getExtension, getNameWithoutExtension

from functions.Persistence import generarCSVJugadores

import os

user_controller =  Blueprint('user',__name__,template_folder='templates')


@user_controller.route('/assistantToEdit', methods=["POST", "GET"])
def assistantToEdit():
    if 'user' in session:
        if request.method == "GET":
            assistantKey = request.args.get("assistantKey")

            eresult = sql_query_var('''SELECT AssistantKey, FirstName, LastName, IDType, ID 
                                                FROM Assistant 
                                                WHERE AssistantKey = %s;''', (assistantKey,))
            print(eresult[0])

            TiposID = getIDTypes()

            return render_template("agregar_personas.html", eresult=eresult[0], IDTypes=TiposID)
    else:
        return render_template("index.html")


@user_controller.route('/AssistantEdit', methods=['POST', 'GET'])
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
            DBInsert(AssistantInsertQuery, (AssistantFName, AssistantLName, AssistantIDType,
                                            AssistantID, assisKey))

            return redirect('/agregarAsistentes')
    else:
        return render_template("index.html")


@user_controller.route('/AssistantDelete', methods=['POST', 'GET'])
def assistantDelete():
    if 'user' in session:
        if request.method == 'GET':
            assistantKey = request.args.get("dAssistantKey")
            assisDeleteQuery = '''DELETE FROM Assistant WHERE AssistantKey = %s'''
            sql_delete(assisDeleteQuery, (assistantKey,))
            return redirect('/agregarAsistentes')

    else:
        return redirect('/')


@user_controller.route('/verJugadoresInscritos', methods=['POST', 'GET'])
def cargarJugadoresResults():
    if 'user' in session:
        if request.method == "GET":
            results = sql_query('''SELECT P.PlayerKey, P.EPS, P.FirstName, P.LastName, P.IDType, P.ID, P.DBirth, P.PictureURL, T.CategoryKey
                                            FROM Coach C LEFT OUTER JOIN Team T
                                            ON C.CoachKey = T.CoachKey
                                            RIGHT OUTER JOIN Player P
                                            ON T.TeamKey = P.TeamKey
                                            WHERE C.CoachKey = ''' + session["user"] + ';')
            categorias = sql_query('''SELECT Ca.CategoryName, Ca.CategoryKey FROM Category Ca RIGHT OUTER JOIN Team T
                            ON T.CategoryKey = Ca.CategoryKey
                            WHERE T.CoachKey = ''' + session["user"] + ";")

            return render_template("verJugadoresInscritos.html", results=results, categories=categorias)
    else:
        return render_template("index.html")


@user_controller.route('/agregarAsistentes', methods=['POST', 'GET'])
def load_asistentes():
    if 'user' in session:
        if request.method == 'GET':
            results = sql_query(
                '''Select AssistantKey, FirstName, LastName, IDType, ID FROM Assistant WHERE CoachKey = ''' + session[
                    "user"] + ''';''')
            return render_template('agregar_asistentes.html', IDTypes=getIDTypes(), results=results)
    else:
        return render_template('index.html')


@user_controller.route('/playerToEdit', methods=["POST", "GET"])
def playerToEdit():
    if 'user' in session:
        if request.method == "GET":
            playerKey = request.args.get("ePlayerKey")

            eresult = sql_query_var('''SELECT P.PlayerKey, P.EPS, P.FirstName, P.LastName, P.IDType, P.ID, P.DBirth, T.CategoryKey, P.PictureURL
                                                FROM Coach C LEFT OUTER JOIN Team T
                                                ON C.CoachKey = T.CoachKey
                                                RIGHT OUTER JOIN Player P
                                                ON T.TeamKey = P.TeamKey
                                                WHERE P.PlayerKey = %s;''', (playerKey,))
            print(eresult)
            categorias = sql_query('''SELECT Ca.CategoryName, Ca.CategoryKey FROM Category Ca RIGHT OUTER JOIN Team T
                                    ON T.CategoryKey = Ca.CategoryKey
                                    WHERE T.CoachKey = ''' + session["user"] + ";")
            print(categorias)

            TiposID = getIDTypes()

            return render_template("agregar_jugadores.html", categories=categorias, eresult=eresult[0], IDTypes=TiposID)
    else:
        return render_template("index.html")


@user_controller.route('/playerEdit', methods=['POST', 'GET'])
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

            pictureURLQuery = ("SELECT PictureURL FROM Player WHERE PlayerKey = %s;")
            pictureURL = sql_query_var(pictureURLQuery, (playerKey,))[0]['PictureURL']

            sql_edit(editQuery, (FirstName, LastName, EPS, IDType, ID, DBirth, playerKey))
            print("ya alteré la información")
            try:
                picture = request.files["playerPicture"]
            except:
                picture = None

            print("ya revisé si existe la imagen")
            if picture is not None:
                print("existe")
                if os.path.exists(pictureURL):
                    print("la imagen debería estar en: " + pictureURL)
                    print("toca borrar")
                    os.remove(pictureURL)
                    print("ya la borré")
                    newURL = getNameWithoutExtension(pictureURL) + "." + (
                        getExtension(request.files['playerPicture'].filename))
                    print(newURL)
                    print("voy a guardar la imagen en: " + newURL)
                    request.files["playerPicture"].save(newURL)
                    print("ya la guardé")
                    sql_edit('''UPDATE Player
                                SET PictureURL = %s
                                WHERE PlayerKey = %s;''', (newURL, playerKey))
                else:
                    print("no toca borrar")
                    newURL = getNameWithoutExtension(pictureURL) + "." + (
                        getExtension(request.files['playerPicture'].filename))
                    print("voy a guardar la imagen en: " + newURL)
                    request.files["playerPicture"].save(newURL)
                    print("ya la guardé")
                    sql_edit('''UPDATE Player
                                SET PictureURL = %s
                                WHERE PlayerKey = %s;''', (newURL, playerKey))

            return redirect('/verJugadoresInscritos')
    else:
        return render_template("index.html")


@user_controller.route('/playerDelete', methods=["POST", "GET"])
def playerDelete():
    if 'user' in session:
        if request.method == "GET":
            deleteQuery = '''DELETE FROM Player WHERE PlayerKey = %s;'''

            DelPlayerKey = request.args.get("dPlayerKey")
            sql_delete(deleteQuery, (DelPlayerKey,))
            print("se borró el jugador " + DelPlayerKey)

            return redirect('verJugadoresInscritos')
    else:
        return render_template("index.html")


@user_controller.route('/insertAssistant', methods=["POST", "GET"])
def insertAssistant():
    if 'user' in session:
        if request.method == "POST":
            AssistantFName = request.form["FirstName"]
            AssistantLName = request.form["LastName"]

            AssistantIDType = request.form["IDType"]
            AssistantID = request.form["ID"]
            AssistantInsertQuery = '''INSERT INTO Assistant(FirstName, LastName, IDType, ID, CoachKey)
                                    Values(%s,%s,%s,%s,''' + session["user"] + ");"
            DBInsert(AssistantInsertQuery, (AssistantFName, AssistantLName, AssistantIDType,
                                            AssistantID))

            return redirect("/agregar_asistentes")
    else:
        return render_template("index.html")


@user_controller.route('/insertCoach', methods=["POST", "GET"])
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
                                    WHERE CoachKey = ''' + session["user"] + ";"
            DBInsert(CoachInsertQuery, (CoachFName, CoachLName, CoachEps, CoachIDType,
                                        CoachID))

            return render_template("info_equipos.html")
    else:
        return render_template("index.html")


@user_controller.route('/agregar_jugadores', methods=['POST', 'GET'])
def CargarAgregar_jugadores():
    if 'user' in session:
        if request.method == 'GET':
            results = sql_query('''SELECT P.PlayerKey, P.EPS, P.FirstName, P.LastName, P.IDType, P.ID, P.DBirth
                        FROM Coach C LEFT OUTER JOIN Team T
                        ON C.CoachKey = T.CoachKey
                        RIGHT OUTER JOIN Player P
                        ON T.TeamKey = P.TeamKey
                        WHERE C.CoachKey = ''' + session["user"] + ';')
            categorias = sql_query('''SELECT Ca.CategoryName, Ca.CategoryKey FROM Category Ca RIGHT OUTER JOIN Team T
                                    ON T.CategoryKey = Ca.CategoryKey
                                    WHERE T.CoachKey = ''' + session["user"] + ";")
            print(categorias)
            numeroJugadoresParaInscribir = 7
            TiposID = getIDTypes()

            return render_template("agregar_jugadores.html", categories=categorias, results=results,
                                   numPlayers=numeroJugadoresParaInscribir, IDTypes=TiposID)
    else:
        return render_template("index.html")


@user_controller.route('/defineNumPlayers', methods=['POST', 'GET'])
def ActualizarNumPlayers():
    if 'user' in session:
        if request.method == 'POST':
            results = sql_query('''SELECT P.PlayerKey, P.EPS, P.FirstName, P.LastName, P.IDType, P.ID, P.DBirth
                            FROM Coach C LEFT OUTER JOIN Team T
                            ON C.CoachKey = T.CoachKey
                            RIGHT OUTER JOIN Player P
                            ON T.TeamKey = P.TeamKey
                            WHERE C.CoachKey = ''' + session["user"] + ';')
            categorias = sql_query('''SELECT Ca.CategoryName, Ca.CategoryKey FROM Category Ca RIGHT OUTER JOIN Team T
                                    ON T.CategoryKey = Ca.CategoryKey
                                    WHERE T.CoachKey = ''' + session["user"] + ";")
            print(categorias)
            numeroJugadoresParaInscribir = int(request.form["numPlayers"])
            TiposID = getIDTypes()

            return render_template("agregar_jugadores.html", categories=categorias, results=results,
                                   numPlayers=numeroJugadoresParaInscribir, IDTypes=TiposID)
    else:
        return render_template("index.html")


@user_controller.route('/insertTeams', methods=["POST", "GET"])
def createTeams():
    if 'user' in session:
        if request.method == "POST":
            clubCoach = request.form["ClubName"]

            addCoachClubQuery = '''UPDATE Coach
                                    SET ClubName = %s
                                    WHERE CoachKey = ''' + session["user"] + ';'

            addTeamQuery = '''INSERT INTO Team(TeamName, CoachKey, CategoryKey)
                            VALUES(%s,''' + session[
                "user"] + ', (SELECT CategoryKey FROM Category WHERE CategoryName LIKE %s));'

            DBInsert(addCoachClubQuery, (clubCoach,))

            if request.form.get("infantil") == "on":
                DBInsert(addTeamQuery, (clubCoach, "infantil"))

            if request.form.get("cadetemasculino") == "on":
                DBInsert(addTeamQuery, (clubCoach, "cadetes masculino"))

            if request.form.get("cadetefemenino") == "on":
                DBInsert(addTeamQuery, (clubCoach, "cadetes femenino"))

            print("En teoría, se insertaron los equipos")

            return redirect('/agregar_jugadores')
    else:
        return render_template("index.html")


@user_controller.route('/insertPlayers', methods=['POST', 'GET'])
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

            DBInsert(insertPlayerQuery, var)

            for n in range(len(FirstName)):
                playerKeyQuery = '''SELECT MAX(PlayerKey) FROM Player
                                WHERE FirstName LIKE %s
                                AND LastName LIKE %s
                                AND EPS LIKE %s
                                AND IDType = %s
                                AND ID LIKE %s
                                AND DBirth LIKE %s;'''
                playerKey = \
                sql_query_var(playerKeyQuery, (FirstName[n], LastName[n], EPS[n], IDType[n], ID[n], DBirth[n]))[0]
                updatePictureURL = ("UPDATE Player SET PictureURL = 'Uploaded/Players/" + str(
                    playerKey["MAX(PlayerKey)"]) + "." + getExtension(photos[n].filename) +
                                    "' WHERE PlayerKey = " + str(playerKey["MAX(PlayerKey)"]) + ";")

                sql_edit(updatePictureURL, None)

                photos[n].save(
                    "Uploaded/Players/" + str(playerKey["MAX(PlayerKey)"]) + "." + getExtension(photos[n].filename))

            return redirect('/verJugadoresInscritos')
    else:
        return render_template("index.html")
