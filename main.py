from flask import Flask, render_template, request
import database as db
import datetime
import time
app = Flask(__name__)
password = "2365"
@app.route('/')
def index():
    return render_template('index.html')

#returns rendered leaderboard for classgroup.
@app.route('/class/<classgroup>')
def classList(classgroup):
    #--- determine the text
    textClassGroup = classgroup #human friendly classgroup label
    if textClassGroup.isdigit():
        textClassGroup = "Year " + textClassGroup
    else:
        textClassGroup = "Class " + textClassGroup
    content = db.generateTable(classgroup)
    return render_template('leaderboard.html', classgroup=textClassGroup, tableContent=content)

#returns table view for editing team information and adding new teams.
@app.route('/edit')
def edit():
    query = request.args.get('q')
    if not query:
        query = "*"
    return render_template('edit.html', edittable=db.productEditTable(query))

#--- API helper for /edit for udating team
@app.route('/updateTeam',methods=['POST'])
def updateTeam():
    data = request.json
    #-- check pswd
    if (data['pkey'] != password):
        return 'WRONG PASSWORD', 401
    #-- password okay so save data
    db.updateTeam(data['#'],data['changes'])
    return "OKAY"

#--- API helper for /edit for creating team
@app.route('/newTeam', methods=['POST'])
def newTeam():
    data = request.json
    #-- check pswd
    if (data['pkey'] != password):
        return 'WRONG PASSWORD', 401
    #-- password okay so save data
    STATUS = db.createTeam(data['#'],data['members'],data['name'],data['classgroup'])
    if STATUS == 'ALREADY_EXISTS':
        return 'TEAM ALREADY EXISTS', 400
    elif STATUS == 'ERROR':
        return 'INTERNAL SERVER ERROR', 500
    else:
        return 'OKAY',200

#--- rendered view that shows information about team, including past times.
@app.route('/team/<teamNo>')
def viewTeamInfo(teamNo):
    team = db.loadData()[teamNo]
    #--- compile times
    lblList = []
    timeList = []
    sortedTimes = sorted_items = sorted(team['times'].items(), key=lambda item: int(item[0]))
    for i in sortedTimes:
        time = i[1]
        if (time > 9):
            continue
        ##make timestamp pretty
        dt_object = datetime.datetime.fromtimestamp(int(i[0]))
        formatted_date = dt_object.strftime('%Y-%m-%d %H:%M')
        lblList.append(formatted_date)
        timeList.append(time*1000)

    fastest = team['fast']
    if fastest > 9:
        fastest = "YET TO RACE"
    return render_template('teamInfo.html', teamName=team['name'],teamNumber=teamNo,classgroup=team['class'],membersList=", ".join(team['members']),fastestTime=fastest,labelsList=str(lblList), timesList=str(timeList))

#-- displays view for recording times
@app.route('/recordTime', methods=['GET'])
def recordTimes():
    return render_template('addTime.html', alert="")

#-- backend for recording new times
@app.route('/recordTime', methods=['POST'])
def recordTimesBackend():
    data = request.form
    #-- check pswd
    if (data['pkey'] != password):
         return render_template('addTime.html', alert="Error! Wrong Password!")
    #-- password okay so save data

    #- get team info
    rawData = db.loadData()
    team = rawData[data['teamNo']]
    #-- add time:
    team['times'].update({str(int(time.time())):float(data['time'])})
    #-- calculate fastest:
    lowest = 999
    for t in team['times']:
        if int(team['times'][t]) < lowest: 
            lowest = team['times'][t]
    team['fast'] = lowest
    
    rawData.update({data['teamNo']:team})
    db.saveData(rawData)


    #-- render success message
    return render_template('addTime.html', alert="Successfully saved time.")


#-- front end for changing times
@app.route('/editTimes/<teamNo>', methods=['GET'])
def editTimes(teamNo):
    team = db.loadData()[teamNo]
    table = ""
    #-- generate times table
    for t in team['times']:
        #print(t, team['times'][t])
        formatted_date = "N/A"
        if int(t) != 0:
            dt_object = datetime.datetime.fromtimestamp(int(t))

            formatted_date = dt_object.strftime('%Y-%m-%d %H:%M')
        table += "<tr><td data-time=\"" + str(t) + "\">" +  formatted_date + "</td><td contenteditable=\"true\">" +  str(team['times'][t]) + "</td><td><button onClick=deleteEntry(" + str(t) + ")>Delete</button></tr>\n"
    return render_template("editTimes.html", teamName = team['name'], table=table, teamNo = teamNo)

#-- backend update of times:
@app.route('/editTimes', methods=['POST'])
def updateEditiedTimes():
    data = request.json
    #-- check pswd
    if (data['pkey'] != password):
        return 'WRONG PASSWORD', 401
    #-- password okay so save data
    rawData = db.loadData()
    team = rawData[str(data['#'])]
    team.update(data['changes'])
    rawData.update({str(data['#']):team})
    db.saveData(rawData)
    return "OKAY"

#-- backend to delete team API helper for EDIT view
@app.route('/deleteTeam', methods=['POST'])
def deleteTeamAPI():
    data = request.json
    #-- check pswd
    if (data['pkey'] != password):
        return 'WRONG PASSWORD', 401
    #-- password okay so delete team
    teamNo = str(data['#'])
    print("DELETING: ", teamNo)
    rawData = db.loadData()
    del rawData[teamNo]
    db.saveData(rawData)
    return "OK",200
if __name__ == '__main__':
    app.run(debug=True)