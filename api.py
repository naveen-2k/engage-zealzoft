from flask import Flask,jsonify,request,render_template
from pymysql.cursors import DictCursor
from flask_cors import CORS
import random
from twilio.rest import Client
import backapi as ba
import socket
import os
import datetime
import string
import uuid
import jwt
#cors
app=Flask(__name__)
CORS(app)

def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(('8.8.8.8', 80))
        # Get the local IP address
        local_ip = sock.getsockname()[0] 
    finally:
        sock.close()
    return local_ip

def baseurl():
    data="http://"+get_local_ip()+":5000/static/images/"
    #print(data)
    return data

@app.route("/")
def index():
    return render_template('index.html')


#insert into database
def insert_user(number,otp):
    try:  
        connection=ba.dbconnection()
        connection.cursorclass=DictCursor
        cursor=connection.cursor()
        print(otp)
        with connection.cursor() as cursor:
            # Insert the data into the database
            sql = "INSERT INTO users (number,passcode) VALUES (%s,%s)"
            cursor.execute(sql, (number,otp))
            connection.commit()
            return "success"

    except Exception as e:
        print('Error:', str(e))
        return jsonify({'success': False, 'message': 'Error occurred while saving data'})

    finally:
        connection.close()
        print("Completed")
   
   
def update_user(number,otp):
    db=ba.dbconnection()
    cursor=db.cursor()
    print(otp)
    cursor.execute("update users set passcode='"+otp+"' where number='"+number+"'")
    db.commit()
    
   
        
# otp generation code
def otp_gen(number):
    otp=str(random.randint(1000,9999))
    print(number)
    
    account_sid = 'AC87818a9a01d29cb12a29f379c33a68fc'# 'AC2cd6fa63b9f246b4edd6231e5aab172b'
    auth_token = '63b543a3f989f9113395fa97e4d8f8e8'#'a7bbfa66bacc681fee8f250630edf06d'
    client = Client(account_sid, auth_token)
    body="Here is your OTP:"+otp
    message = client.messages.create(
                              from_='+14176510380',#+13614207704
                              body=body,
                              to="+91"+str(number)
                          )
    if message.sid:
        return otp
    else: 
        return False

   
   
@app.route('/get-otp',methods=['get','post'])
def get_otp():
    req_data=request.get_json()
    print(req_data)
    cursor=ba.get_cursor()
    sqlquery="select * from users"
    cursor.execute(sqlquery)
    data=cursor.fetchall()
    #print(data) 
    found = any(str(item['number']) == str(req_data['mobileNumber']) for item in data)
    if found:
        print(f"The number '{req_data['mobileNumber']}' is present in the dictionary.")
        otp=otp_gen(str(req_data['mobileNumber']))
        update_user(req_data['mobileNumber'],otp)
        return jsonify({"number":req_data['mobileNumber'],"otp":otp,"message":"user already exists"})
    else:
        print(f"The number '{req_data['mobileNumber']}' is not found in the dictionary.")  
        otp=otp_gen(req_data['mobileNumber'])
        insert_user(req_data['mobileNumber'],otp)
        return jsonify({"number":req_data['mobileNumber'],"otp":otp,"message":"new user"})


    
@app.route('/verify-otp',methods=['get','post'])
def verify_otp():
    data=request.get_json()
    print(data)
    cursor=ba.get_cursor()
    cursor.execute(f"select * from users where number='{data['mobileNumber']}'")
    res=cursor.fetchone()
    print(res['passcode'])
    if res['passcode'] == data['otp']:
        print("done") 
        session_token = jwt.encode({'uid': res['uid']}, 'login_confidential_key', algorithm='HS256')
        print(session_token)
        return jsonify({"message":"done","data":res,"sessiotoken":session_token})
    else:
        print("false")
        return jsonify({"messgae":"false"})
    
    
#get event details posted by users
@app.route('/event-details',methods=['get','post'])#http://192.168.29.34:5000/event-details
def event_details():
    base_url="http://"+get_local_ip()+":5000/static/images/"
    category=request.get_json()
    print(category)
    data=ba.get_images(category['category'])
    
    for i in range(len(data)):
        data[i]['imageurl']=base_url+data[i]['imageurl']
        data[i]['profilepic']=base_url+data[i]['profilepic']
        # print(data[i]['imageurl'])
    print(data)
    print("data fetched")
    return jsonify(data)

@app.route('/user-details')
def get_user_details():
    return None


@app.route('/fetch-image',methods=['get','post'])#http://192.168.29.34:5000/fetch-image
def get(): 
    base_url="http://192.168.29.34:5000/static/images/"
    return jsonify({"img":""+base_url+"OIP.png"})     #"http://127.0.0.1:5000/static/images/OIP.png"

@app.route('/insert-post-details',methods=['get','post'])  #http://127.0.0.1:5000/insert-post-details
def insertpostdetais():
    data = request.get_json()
    print(data.keys())
    res,data=ba.insert_post_details(data)
    print(res)
    return jsonify({"res":res,"data":data})  

@app.route('/get-users-post',methods=['post'])
def getuserspost():
    base_url="http://"+get_local_ip()+":5000/static/images/"
    data=request.get_json()
    data=ba.get_users_posts(data)
    print(data)
    if data=="no data":
        return jsonify({"data":"no data","statuscode":200})
    else:
     for i in range(len(data)):
        data[i]['imageurl']=base_url+data[i]['imageurl']   
     print(data) 
     return jsonify({"data":data})


@app.route('/insert-users-details',methods=['get','post'])  #http://127.0.0.1:5000/insert-users-details
def insertusersdetais():
    data = request.get_json()
    print(data.keys())
    res,data=ba.insert_user_details(data)
    print(res)
    return jsonify({"res":res,"data":data})  

@app.route('/fetch-user-details',methods=['post'])
def fetchuserdetails():
    data=request.get_json()
    print(data)
    res,data=ba.fetch_user_details(data["uid"])
    base_url="http://"+get_local_ip()+":5000/static/images/"
    for i in range(len(data)):
        data[i]['profilepic']=base_url+data[i]['profilepic']
    print(res,data)
    return jsonify({"res":res,"data":data})

@app.route('/update-user-details',methods=['get','post'])
def updateuserdetails():
    data=request.get_json()
    print(data)
    res=ba.update_user_details(data)
    return jsonify({"res":res})

@app.route('/fetch-other-users',methods=['get','post'])
def fetchotherusers():
    data=request.get_json()
    print(data)
    res,datae=ba.fetch_other_users(data['ouid'])
    base_url="http://"+get_local_ip()+":5000/static/images/"
    for i in range(len(datae)):
        datae[i]['profilepic']=base_url+datae[i]['profilepic']
    return({"res":res,"data":datae})
   
 
@app.route('/fetch-url',methods=['get','post'])
def urlfetch():
    data=get_local_ip()
    print(data)
    return jsonify(data)


@app.route('/upload-image', methods=['POST'])
def upload_image():
    image = request.files['image']
    ct = datetime.datetime.now()
    print(ct)
    snip=uuid.uuid4()
    filename = str(snip)+image.filename
    print(filename)
    filepath = os.path.join('static', 'images', filename)
    filepath=filepath.replace("\\","/")
    serverimagepath="http://"+get_local_ip()+":5000/"+filepath
    print(filepath)
    print(serverimagepath)
    image.save(filepath)
    return jsonify({'imageurl': filepath,"serverimagepath":serverimagepath,"filename":filename})

@app.route('/follow-request',methods=['get','post'])
def follow_req():
    res=ba.follow(request.json['follower'],request.json['following'])
    return jsonify(res)

@app.route('/check-user-details',methods=['get','post'])
def checkuserdetails():
    try:
        data=request.get_json()
        db=ba.dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor()
        cursor.execute("select * from users_details where uid=%s",(data['uid']))
        res=cursor.fetchall()
        if res.count>0:
            print(res)
            return jsonify({"res":True,"data":res})
        else:
            return jsonify({"res":False, "msg":"No user found"})
    except Exception as e:
        return jsonify({"res":False, "msg":str(e)})
    
@app.route('/mail-verify',methods=['get','post'])
def mailverification():
    data=request.get_json()
    res,otp=ba.send_email(data)
    return jsonify(res,otp)

@app.route('/mail-verify-results',methods=['get','post'])
def mailverificationresults():
    data=request.get_json()
    res=ba.mail_verify_result(data)
    return jsonify(res)
    
@app.route('/particular-event-details',methods=['get','post'])
def particulareventdetails():
    base_url="http://"+get_local_ip()+":5000/static/images/"
    eventid=request.get_json()
    print(eventid)
    data=ba.particular_event_details(eventid['event_id'])
    for i in range(len(data)):
        data[i]['imageurl']=base_url+data[i]['imageurl']
        data[i]['profilepic']=base_url+data[i]['profilepic']
    print(data)
    return jsonify({"data":data})

@app.route('/current-user-posts',methods=['post'])
def currentuserposts():
    data=request.get_json()
    print(data)
    dbdata,res=ba.current_user_posts(data)
    return jsonify({"res":res,"data":dbdata})

@app.route('/check-requested-details',methods=['post'])
def checkrequesteddetails():
    ddata=request.get_json()
    print(ddata)
    data=ba.check_requested_details(ddata)
    base_url="http://"+get_local_ip()+":5000/static/images/"
    for i in range(len(data)):
        data[i]['imageurl']=base_url+data[i]['imageurl']
        data[i]['profilepic']=base_url+data[i]['profilepic']
    return jsonify({"res":data,})

@app.route('/accept-engage',methods=['post'])
def acceptengage():
    data=request.get_json()
    print(data)
    res=ba.accept_engage(data)
    return jsonify({res})

@app.route('/like-unlike-post',methods=['post'])
def likeunlikepost():
    data=request.get_json()
    print(data)
    res=ba.like_unlike_post(data)
    return jsonify({res})

@app.route('/liked-post-details',methods=['post'])
def likedpostdetails():
    data=request.get_json()
    print(data)
    res,edata=ba.liked_post_details(data)
    return jsonify({"res":res,"data":edata})

@app.route('/friends-engage',methods=['post'])
def friendsrequest():
    data=request.get_json()
    print(data)
    res=ba.friends_engage(data)
    return jsonify({"res":res})
@app.route('/unfollow-engage',methods=['post'])
def unfollowengage():
    data=request.get_json()
    print(data)
    res=ba.unfollow_engage(data)
    return jsonify({"res":res})
    

@app.route('/request-engage',methods=['post'])
def requestengage():
    data=request.get_json()
    print(data)
    res=ba.request_engage_event(data)
    return jsonify({"data":data,"res":res})

@app.route('/delete-request',methods=['post'])
def deleterequest():
    data=request.get_json()
    res=ba.delete_request(data)
    return jsonify({"data":data,"res":res})

@app.route('/check-if-requested',methods=['post'])
def checkifrequested():
    data=request.get_json()
    res=ba.check_if_requested(data)
    return jsonify(res)

@app.route('/logout', methods=['POST'])
def logout():
    # Retrieve the session token from the request headers
    session_token = request.headers.get('Authorization')
    if session_token:
        try:
            # Decode the session token to validate and extract the username
            payload = jwt.decode(session_token, 'login_confidential_key', algorithms=['HS256'])
            username = payload['uid']
            print(username)
            return jsonify({'message': 'Logout successful'})
        except jwt.exceptions.DecodeError:
            return jsonify({'error': 'Invalid session token'}), 401
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({'error': 'Session token has expired'}), 401
    else:
        return jsonify({'error': 'No session token provided'}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0" ,debug=True)
    local_ip = get_local_ip()
    print("Local IP address:"+local_ip)
    
    