import json

import requests
from flask import Flask, flash, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from flask import jsonify
from wtforms import Form, TextField, validators
from bson import ObjectId

app = Flask(__name__)

app.secret_key = 'secret key'
app.config['MONGO_DBNAME'] = 'emailTest'
app.config['MONGO_URI'] ='mongodb://localhost:27017/emailTest'

mongo = PyMongo(app)


#send email form
class SendEmail(Form):
    To = TextField("TO",[validators.DataRequired()])
    From = TextField("From",[validators.DataRequired()])
    Subject = TextField("Subject",[validators.DataRequired()])
    Message = TextField("Message",[validators.DataRequired()])

@app.route('/email',methods=['GET','POST'])
def email():

    # received_Emails = mongo.db.rEmail
    # output =[]
    # for e in received_Emails.find():
    #     output.append({'To': e['To'],'Message':e['Message']})
    #     return jsonify({'result': output})
    if request.method == 'GET':
        emails = mongo.db.rEmail   
        output =[]
        for e in emails.find({"Type": "Received"}):
            #if emails.find({"Type": "Received"}):
            output.append({'_id':e['_id'],'To': e['To'],'From': e['From'],'Subject': e['Subject'],'Message':e['Message'],'Type':e['Type']})

        return render_template('index.html',results=output)
    
    elif request.method == 'POST':
        emails = mongo.db.rEmail
        To = request.form['To']
        From = request.form['From']
        Subject = request.form['Subject']
        Message = request.form['Message']
        try:
            emails.insert({"To":To,
                            "From": From,
                            "Subject": Subject,
                            "Message": Message,
                            "Type":"Received"
                        })
        except Exception as e:
            print("Error in inserting: ",e)

        redirect('/email')

@app.route('/email/sendEmail', methods=['GET','POST'])
def sendEmail():

    form = SendEmail(request.form)
    if request.method == 'POST' and form.validate():
        emails = mongo.db.rEmail
        To = request.form['To']
        From = request.form['From']
        Subject = request.form['Subject']
        Message = request.form['Message']
        try:
            emails.insert({"To":To,
                            "From": From,
                            "Subject": Subject,
                            "Message": Message,
                            "Type":"Sent"
                        })
            flash("Email has been sent")
        except Exception as e:
            print("Error in inserting: ",e)

        redirect('/sendEmail')
       

    return render_template('send.html')

@app.route('/email/sentEmails', methods=['GET'])
def sentEmails():
    if request.method == 'GET':
        emails = mongo.db.rEmail
        output =[]
        for e in emails.find({"Type": "Sent"}):
            #if emails.find({"Type": "Sent"}):
            output.append({'_id':e['_id'],'To': e['To'],'From': e['From'],'Subject': e['Subject'],'Message':e['Message'],'Type':e['Type']})

        return render_template('sentEmails.html',results=output)

    return render_template('sentEmails.html')

@app.route('/email/archive', methods=['GET','POST'])
def archive():
    emails = mongo.db.rEmail
    key = request.values.get("_id")
    print('Key ARchive: ',key)
    EmailType = request.values.get("Type")
    print('EmailType: ', EmailType)
    output =[]
    if request.method == 'GET':
        if emails.find({"_id": key}):
                emails.update({"Type": EmailType},{"$set":{"Type":"Arch"}})
       
            
        for e in emails.find({"Type": "Arch"}):
            output.append({'_id':e['_id'],'To': e['To'],'From': e['From'],'Subject': e['Subject'],'Message':e['Message']})


    return render_template('archive.html',results=output)

@app.route('/email/delete', methods=['GET','DELETE'])
def deleteEmail():

    key = request.values.get("_id")
    emails = mongo.db.rEmail
    emails.remove({"_id":ObjectId(key)})

    return render_template('index.html')

@app.route('/email/searchSender', methods=['GET','POST'])
def searchSender():
    emails = mongo.db.rEmail
    output = []
    
    sender_user = request.form['Sender']
    for e in emails.find({"From": sender_user}):
        output.append({'_id':e['_id'],'To': e['To'],'From': e['From'],'Subject': e['Subject'],'Message':e['Message']})
    

    return render_template('results.html',results=output)


if __name__ == '__main__':
    app.run(debug=True)