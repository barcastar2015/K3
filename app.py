from flask import Flask, session, redirect, url_for, escape, request, render_template, json
from hashlib import md5
from flask.ext.mysql import MySQL

app = Flask(__name__)

#######################
#   DATABASE CONFIG   #
#######################
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'k3'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cur = conn.cursor()

@app.route('/delete', methods = ['GET'])
def delete():
    loomaNimi = request.args.get('loomaNimi')
    cur.execute("DELETE FROM loomad WHERE Nimi=%s", loomaNimi)
    conn.commit()
    cur.execute("DELETE FROM nägemine WHERE Nimi=%s", loomaNimi)
    conn.commit()
    return redirect(url_for('index'))

@app.route('/update', methods = ['POST','GET'])
def update():
    loomaNimi = request.args.get('loomaNimi')
    liigiNimi = request.args.get('liigiNimi')
    cur.execute("UPDATE loomad SET Liik=%s WHERE Nimi=%s", (liigiNimi, loomaNimi))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/updateLocation', methods = ['POST','GET'])
def updateLocation():
    loomaNimi = request.args.get('loomaNimi')
    asukoht = request.args.get('asukoht')
    aeg = request.args.get('aeg')
    cur.execute("UPDATE nägemine SET Asukoht=%s WHERE Nimi=%s AND Aeg=%s", (asukoht, loomaNimi, aeg))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/updateTime', methods = ['POST','GET'])
def updateTime():
    loomaNimi = request.args.get('loomaNimi')
    asukoht = request.args.get('asukoht')
    aeg = request.args.get('aeg')
    cur.execute("UPDATE nägemine SET Aeg=%s WHERE Nimi=%s AND Asukoht=%s", (aeg, loomaNimi, asukoht))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/', methods=['POST', 'GET'])
def index():
    cur.execute('SELECT Nimi FROM loomad')
    options=""
    for row in cur.fetchall():
        options += "<option value='" + row[0] + "'>" + row[0] + "</option>"
    if request.method == 'POST':
        if len(request.form['loomaNimi']) > 0:
            loomaNimi = request.form['loomaNimi']
            loomaTabel = getSpeiceByName(loomaNimi)
            nagemisTabel = getSeeingsOfOneAnimal(loomaNimi)
            tabNr = "1"
            return render_template("index.html", loomaNimi=loomaNimi, loomaTabel1=loomaTabel, nagemisTabel1 = nagemisTabel, options=options, tabNr=tabNr)
        if len(request.form['liigiNimi']) > 0:
            liigiNimi = request.form['liigiNimi']
            loomaTabel = getDataFromAnimalsTable(liigiNimi)
            nagemisTabel = getDataFromSeeingTable(liigiNimi)
            tabNr = "2"
            return render_template("index.html", liigiNimi=liigiNimi, loomaTabel2=loomaTabel, nagemisTabel2 = nagemisTabel, options=options, tabNr=tabNr)
        if len(request.form['uusNimi']) > 0 and len(request.form['uusLiik']) > 0:
            loomaNimi = request.form['uusNimi']
            loomaLiik = request.form['uusLiik']
            cur.execute("""INSERT INTO loomad (Nimi, Liik) VALUES (%s, %s)""", (loomaNimi, loomaLiik))
            conn.commit()

            tabNr=1
            return render_template("index.html", loomaNimi=loomaNimi, options=options, tabNr=tabNr)
        if len(request.form['koht']) > 0:
            nimi = request.form['nimi']
            koht = request.form['koht']
            aeg = request.form['aeg']
            cur.execute("INSERT INTO nägemine (Nimi, Asukoht, Aeg) VALUES (%s, %s, %s)", (nimi, koht, aeg))
            conn.commit()
            tabNr = "1"
            return render_template("index.html", result=nimi, options=options, tabNr=tabNr)
        if len(request.form['asukoht']) > 0:
            asukoht = request.form['asukoht']
            nagemisTabel = getSeeingsByLocation(asukoht)
            tabNr = "5"
            return render_template("index.html", asukoht=asukoht, nagemisTabel3=nagemisTabel, options=options, tabNr=tabNr)

        return render_template("index.html", options=options)
    tabNr = "1"
    return render_template("index.html", options=options, tabNr=tabNr)

def getSeeingsOfOneAnimal(loomaNimi):
    cur.execute('SELECT * FROM nägemine WHERE Nimi = %s', loomaNimi)
    nagemisTabel = "<table class='table'><thead><tr><th>Nimi</th><th>Koht</th><th>Aeg</th></tr></thead><tbody>"
    count = 0
    for row in cur.fetchall():
        count += 1
        string = str(count)
        nagemisTabel += "<tr><td id='animalName"+string+"'>" + row[0] + "</td><td id='location"+string+"' contenteditable>" + row[1] \
                        + "</td><td contenteditable id='time"+string+"'>" + row[2].strftime("%Y-%m-%d %H:%M:%S") + "</td></tr>"
    nagemisTabel += "</tbody></table>"
    return nagemisTabel


def getSpeiceByName(loomaNimi):
    str = "<input type='hidden' name='delete' value='true'>"
    str1 = "<input type='hidden' name='loomaNimi' value="+loomaNimi+">"
    str2 = "<input type='submit' id='submit' value='Kustuta'>"
    str3 = str + str1 + str2

    cur.execute('SELECT * FROM loomad WHERE Nimi = %s', loomaNimi)
    loomaTabel = "<table class='table'><thead><tr><th>Nimi</th><th>Liik</th><th></th></tr></thead><tbody>"
    for row in cur.fetchall():
        loomaTabel += "<tr><td id='name'>" + row[0] + "</td><td contenteditable id='speice'>" + row[1] + "</td><td><a href='/delete?loomaNimi="+loomaNimi+"'>Kustuta</a></td></tr>"
    loomaTabel += "</tbody></table>"
    return loomaTabel



def getDataFromSeeingTable(liigiNimi):
    cur.execute('SELECT nägemine.* FROM nägemine INNER JOIN loomad ON nägemine.Nimi = loomad.Nimi WHERE loomad.Liik=%s',
                liigiNimi)
    nagemisTabel = "<table class='table'><thead><tr><th>Nimi</th><th>Koht</th><th>Aeg</th></tr></thead><tbody>"
    for row in cur.fetchall():
        nagemisTabel += "<tr><td>" + row[0] + "</td><td>" + row[1] + "</td><td>" + row[
                            2].strftime("%Y-%m-%d %H:%M:%S") + "</td></tr>"
    nagemisTabel += "</tbody></table>"
    return nagemisTabel

def getDataFromAnimalsTable(liigiNimi):
    cur.execute('SELECT * FROM loomad WHERE Liik = %s', liigiNimi)
    loomaTabel = "<table class='table'><thead><tr><th>Nimi</th><th>Liik</th></tr></thead><tbody>"
    for row in cur.fetchall():
        loomaTabel += "<tr><td>" + row[0] + "</td><td>" + row[1] + "</td></tr>"
    loomaTabel += "</tbody></table>"
    return loomaTabel

def getSeeingsByLocation(asukoht):
    cur.execute('SELECT * FROM nägemine WHERE Asukoht = %s', asukoht)
    nagemisTabel = "<table class='table'><thead><tr><th>Nimi</th><th>Koht</th><th>Aeg</th></tr></thead><tbody>"
    for row in cur.fetchall():
        nagemisTabel += "<tr><td>" + row[0] + "</td><td>" + row[1] + "</td><td>" + row[
            2].strftime(
            "%Y-%m-%d %H:%M:%S") + "</td></tr>"
    nagemisTabel += "</tbody></table>"
    return nagemisTabel

if __name__ == '__main__':
    app.run(port=5003)