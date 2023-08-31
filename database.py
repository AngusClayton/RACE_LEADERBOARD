import json, time
datafile = "data.json"

def loadData():
    data = {}
    try:
        with open(datafile) as json_file: 
            data = json.load(json_file)
        print("Data loaded successfully")
    except:
        print("Error loading data filename: " + datafile)
    return data

#preconditions: data to sort
#postconditions returns sorted list (loads fresh data)
def sortList(toSort): 
    return 0


#produces HTML table for leaderboard
def generateTable(class_name):
    rawData = loadData() #load the data
    #--- filter the data:
    yearFilteredData = []
    for i in rawData:
        team = rawData[i]
        if class_name in team['class']:
            yearFilteredData.append(team)
    #--- sort the data
    sorted_data = sorted(yearFilteredData, key=lambda x: x['fast'])
    # ----- display the data
    output = ""
    counter = 1 #position
    for i in sorted_data:
        #-------- determine format for 1/2/3
        if counter == 1:
            output += "<tr class='first'>"
        elif counter == 2:
            output +=  "<tr class='second'>"
        elif counter == 3:
            output +=  "<tr class='third'>"
        else:
            output += "<tr>"
        #-----
        output += "<td>" + str(counter) + "</td>"
        output += "<td>" + str(i['#']) + "</td>"
        output += "<td> <a href='/team/" + str(i['#']) + "'>"+ str(i['name']) + "</a></td>"
        output += "<td>" + str(i['fast']) + "</td>"
        output += "<td>" + str(i['class']) + "</td>"

        output +="</tr>"
        counter +=1 #position
    

    #sortedList = sortList(data) #list sorted by times
    return output

#produces HTML table for editing team information
def productEditTable(query):
    data = loadData()
    outputhtml = ""
    count = 1
    for i in data:
        team = data[i]
        searchableQuery = i+" "+str(team['members']) + " " + team['class'] + team['name']
        if query == '*' or query.lower() in searchableQuery.lower():
            outputhtml += "<tr><td>{}</td><td contenteditable=\"true\">{}</td><td contenteditable=\"true\">{}</td><td contenteditable=\"true\">{}</td><td><button onclick=\"save({})\">Save Changes</button><td><a href=\"/editTimes/{}\"><button>Edit Times</button></a></td><td><button onclick=deleteTeam({})>Delete Team</button></td></tr>".format(team['#'], team['class'], team['name'],", ".join(team['members']),team['#'] +", " +str(count),team['#'],team['#'])
            count +=1
    return outputhtml

def createTeam(teamNo, members,name, classgroup):
    data = loadData()
    #-- check teamno not in data already:
    if str(teamNo) in data:
        return 'ALREADY_EXISTS'
    try:
        membersRAW = members.split(",")
        members = []
        for i in membersRAW:
            members.append(i.strip())
        teamNo = str(teamNo)
        team = {teamNo:{'members': members, 'class':classgroup, 'name': name,"times": {"0": 999.0},"fast": 999.0, "#": teamNo}}
        data.update(team)
        saveData(data)
        return 'OK'
    except:
        return 'ERROR'

def updateTeam(teamNo, changes):
        changes = changes['changes']
        teamName = changes['name']
        classgroup = changes['classgroup']
        members = changes['members'].split(", ")
        data = loadData()
        team = data[teamNo]
        
        team.update({"name":teamName,"members":members,"class":classgroup})
        print("UPDATING TEAM", teamNo, "to: ",team)
        data.update({teamNo:team})
        saveData(data)



def saveData(data):
    try:
        with open(datafile, 'w') as outfile:
            json.dump(data, outfile)
        print("SAVED DATA")
    except:
        print("ERROR SAVING DATA")
