


def generarCSVJugadores(info):
    stringToWrite = "nombre;apellido;docid;cargo;categoría;bandera;@colorid;@foto \n"

    for dic in info:
        stringToWrite = stringToWrite + dic["FirstName"]+";"+dic["LastName"]+";"+dic["ID"]+";DEPORTISTA;"+dic["Category"]+";;;" + dic["PictureURL"] + "\n"

    