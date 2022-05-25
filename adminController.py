from flask import Blueprint, request, redirect, render_template, session, redirect

from functions.DataBaseConnection import connect, DBInsert, sql_delete,sql_edit,sql_query_var, sql_query, getIDTypes, getCategories

from functions.methods import random_key, hashPasswd, getExtension, getNameWithoutExtension

from functions.Persistence import generarCSVJugadores

import os

admin_controller =  Blueprint('admin',__name__,template_folder='templates')

@admin_controller.route('/personToEdit', methods=["POST", "GET"])
def personToEdit():
    if 'user' in session:
        if request.method == "GET":
            Key = request.args.get("personKey")

            eresult = sql_query_var('''SELECT PersonKey, FirstName, LastName, IDType, ID 
                                                    FROM Person 
                                                    WHERE PersonKey = %s;''', (personKey,))
            print(eresult[0])

            TiposID = getIDTypes()

            return render_template("agregar_asistentes.html", eresult=eresult[0], IDTypes=TiposID)
    else:
        return render_template("index.html")


@admin_controller.route('/personEdit', methods=['POST', 'GET'])
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
            DBInsert(PersonInsertQuery, (PersonFName, PersonLName, PersonIDType,
                                         PersonID, assisKey))

            return redirect('/agregar_personas')
    else:
        return render_template("index.html")


@admin_controller.route('/PersonDelete', methods=['POST', 'GET'])
def deletePerson():
    if 'user' in session:
        if request.method == 'GET':
            personKey = request.args.get("personKey")
            assisDeleteQuery = '''DELETE FROM Person WHERE PersonKey = %s'''
            sql_delete(assisDeleteQuery, (personKey,))
            return redirect('/agregar_personas')

    else:
        return redirect('/')


@admin_controller.route('/agregar_personas', methods=['POST', 'GET'])
def load_personas():
    if 'user' in session:
        if request.method == 'GET':
            results = sql_query('''Select PersonKey, FirstName, LastName, IDType, ID FROM Person;''')
            return render_template('agregar_personas.html', IDTypes=getIDTypes(), results=results)
    else:
        return render_template('index.html')


@admin_controller.route('/insertPerson', methods=["POST", "GET"])
def insertPerson():
    if 'user' in session:
        if request.method == "POST":
            PersonFName = request.form["FirstName"]
            PersonLName = request.form["LastName"]

            PersonIDType = request.form["IDType"]
            PersonID = request.form["ID"]
            PersonInsertQuery = '''INSERT INTO Person(FirstName, LastName, IDType, ID)
                                    Values(%s,%s,%s,%s);'''
            DBInsert(PersonInsertQuery, (PersonFName, PersonLName, PersonIDType,
                                         PersonID))

            return redirect("/agregar_personas")
    else:
        return render_template("index.html")


@admin_controller.route('/coaches', methods=['POST', 'GET'])
def load_Coaches():
    if "user" in session:
        if session['user'] == "admin":
            if request.method == 'GET':
                coachesQuery = '''SELECT CoachKey, UserName FROM Coach;'''
                result = sql_query(coachesQuery)
                print(result)
                return render_template("entrenadores.html", results=result)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@admin_controller.route('/partidos', methods=['POST', 'GET'])
def load_partidos():
    if "user" in session:
        if session['user'] == "admin":
            if request.method == 'GET':
                return render_template("partidos.html", categorias=getCategories())
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@admin_controller.route('/goles', methods=['POST', 'GET'])
def load_goles():
    if "user" in session:
        if session['user'] == "admin":
            if request.method == 'GET':
                return render_template("goles.html", categorias=getCategories())
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@admin_controller.route('/insertNewCoach', methods=['POST', 'GET'])
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
                print(result)
                return render_template('entrenadores.html', results=result)
        else:
            render_template("index.html")
    else:
        return render_template("index.html")


@admin_controller.route('/toEditCoach', methods=['POST', 'GET'])
def toEditCoach():
    if 'user' in session:
        if session["user"] == 'admin':
            if request.method == 'GET':
                eCoachKey = request.args.get("toEditCoachKey")
                eresultsQuery = '''SELECT CoachKey, UserName FROM Coach
                                    WHERE CoachKey = %s;'''
                eresults = sql_query_var(eresultsQuery, (eCoachKey,))
                coachesQuery = '''SELECT CoachKey, UserName FROM Coach;'''
                result = sql_query(coachesQuery)
                return render_template('entrenadores.html', results=result, eresults=eresults)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@admin_controller.route('/editCoach', methods=['POST', 'GET'])
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
                print(result)
                return render_template('entrenadores.html', results=result)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@admin_controller.route('/deleteCoach', methods=['POST', 'GET'])
def deleteCoach():
    if 'user' in session:
        if session["user"] == "admin":
            if request.method == 'GET':
                dCoachKey = request.args.get("toDeleteCoachKey")

                deleteCoachQueries = []

                deleteCoachQueries.admin_controllerend('''DELETE FROM Goal
                                WHERE PlayerKey IN (SELECT P.PlayerKey FROM Player P LEFT OUTER JOIN Team T
                                                        ON T.TeamKey = P.TeamKey
                                                    WHERE T.CoachKey = %s
                                                            OR T.CoachKey = %s);''')

                deleteCoachQueries.admin_controllerend('''DELETE FROM Game
                                WHERE TeamOneKey IN (SELECT TeamKey FROM Team WHERE CoachKey = %s)
                                        OR TeamTwoKey IN (SELECT TeamKey FROM Team WHERE CoachKey = %s);''')

                deleteCoachQueries.admin_controllerend(
                    '''DELETE FROM Player WHERE TeamKey IN (SELECT TeamKey FROM Team WHERE CoachKey = %s OR CoachKey = %s);''')

                deleteCoachQueries.admin_controllerend('''DELETE FROM Team WHERE CoachKey = %s OR CoachKey = %s;''')

                deleteCoachQueries.admin_controllerend('''DELETE FROM Coach
                                WHERE CoachKey = %s OR CoachKey = %s;''')

                for query in deleteCoachQueries:
                    sql_delete(query, (dCoachKey, dCoachKey))
                coachesQuery = '''SELECT CoachKey, UserName FROM Coach;'''
                result = sql_query(coachesQuery)
                return render_template('entrenadores.html', results=result)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


