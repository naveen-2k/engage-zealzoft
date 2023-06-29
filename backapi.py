from pymysql.cursors import DictCursor
import pymysql
from flask import jsonify
import smtplib
import random
from datetime import date


def calc_age(dob_str):
    dob=int(dob_str[6:])
    tyear=date.today().year
    return tyear-dob


def dbconnection():
    db=pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="engage"
    )
    db.cursorclass=DictCursor
    return db
    
def get_cursor():
    db=dbconnection()
    db.cursorclass=DictCursor
    cursor=db.cursor()
    return cursor

def get_images(category=""):
    db=dbconnection()
    cursor=get_cursor()
    sql = """
    SELECT *
    FROM users_detail
    JOIN events ON users_detail.uid = events.user_id
    WHERE events.main_category LIKE %s or events.category LIKE %s
    """
    cursor.execute(sql,('%' + category + '%','%' + category + '%'))
    data=cursor.fetchall()
    db.commit()
    return data

def particular_event_details(eid):
    db=dbconnection()
    db.cursorclass=DictCursor
    cursor=db.cursor()
    sql="""SELECT * FROM users_detail INNER JOIN events ON users_detail.uid=events.user_id
    where events.event_id=%s"""
    print(eid)
    cursor.execute(sql,(eid))
    data=cursor.fetchall()
    return data

def insert_post_details(datas):
    try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor()       
        datas["elocation"]=str(datas["elocation"])      # datas["edate"] = datas["edate"].replace("/", "-") # datas["estime"]=datas["edate"] + " " + datas["estime"]  # datas["eetime"]=datas["edate"] + " " + datas["eetime"] 
        # Prepare the query
        columns = ", ".join(datas.keys())
        placeholders = ", ".join(["%s"] * len(datas))
        query = f"INSERT INTO events ({columns}) VALUES ({placeholders})"
        values=datas.values()
        cursor.execute(query, tuple(values))
        db.commit()
        print(query)
        print(tuple(values))
        return True,datas     
    except Exception as e:
        print(e)
        return False,str(e)
    
def current_user_posts(data):
    try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor()
        cursor.execute("select * from events where user_id=%s",(data['cuid']))
        res=cursor.fetchall()
        return res,True
    except Exception as e:
        print(e)
        return str(e),False
    
def check_requested_details(data):
    try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor()
        sql="""select * from engage_event ee 
        inner join events e on e.event_id=ee.eventid
        inner join users_detail ud on ee.request_uid=ud.uid
        where e.user_id=%s"""
        cursor.execute(sql,(data['cuid']))
        res=cursor.fetchall()
        return res
    except Exception as e:
        print(e)
        return False
    
def accept_engage(data):
    try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor()
        sql="""update engage_event set state='accepted' where request_uid=%s and eventid=%s"""
        cursor.execute(sql,(data['ruid'],data['eventid']))
        res=cursor.fetchall()
        return res
    except Exception as e:
        print(e)
        return False
    
    
    
    
def insert_user_details(datas):
    try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor()       
        columns = ", ".join(datas.keys())
        placeholders = ", ".join(["%s"] * len(datas))
        query = f"INSERT INTO users_detail ({columns}) VALUES ({placeholders})"
        values=datas.values()
        cursor.execute(query, tuple(values))
        db.commit()
        print(query)
        print(tuple(values))
        return True,datas     
    except Exception as e:
        print(e)
        return False,str(e)
    
def check_user_details(uid):
    try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor()
        cursor.execute("select * from users_details where uid=%s",(uid))
        res=cursor.fetchall()
        if res.count>0:
            print(res)
            return {"res":True,"data":res}
        else:
            return {"res":False, "msg":"No user found"}
    except Exception as e:
        return {"res":"error", "msg":str(e)}
    
def fetch_user_details(uid):
    try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor() 
        query=f"select * from users_detail where uid={uid}"
        cursor.execute(query)
        res=cursor.fetchall()
        return True,res
    except Exception as e:
        return False,str(e)
    
def fetch_other_users(uid):
    try:
        print(uid)
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor() 
        query=f"select * from users_detail where uid = {uid}"
        cursor.execute(query)
        res=cursor.fetchall()
        print(res)
        return True,res
    except Exception as e:
        print(str(e))
        return False,str(e)
    
    
def update_user_details(data):
   try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor() 
        columns=list(data.keys())
        values=list(data.values())
        print(columns,values)
        for i,j in zip(columns,values):
            sql=f"update user_details set {i}= '{j}' where uid={data['uid']}"
            cursor.execute(sql)
            db.commit()
        return True,"updated"
   except Exception as e:
        return False,str(e)
    
def follow(follower,following):
    try:
        db=dbconnection()
        cursor=db.cursor()
        sql="insert into follow (followerid,followingid) values ('%s','%s')"
        cursor.execute(sql,(follower,following))
        db.commit()
        return jsonify({"res":"done"})
    except Exception as e:
        print(e)
        return jsonify({"res":"fail","message":str(e)})
    
def send_email(data):
    email =data['email']
    
    # Generate a random 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # or the appropriate SMTP port
    smtp_username = 'madinaveen2001@gmail.com'
    smtp_password = 'dpkgnbbakaywcwyu'
    sender_email = 'madinaveen2001@gmail.com'
    
    # Compose the email
    subject = 'Your OTP'
    message = f'Your OTP is: {otp}'
    email_text = f"Subject: {subject}\n\n{message}"
    
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        # Send the email
        server.sendmail(sender_email, email, email_text)
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor() 
        cursor.execute("select * from mail_verify where uid=%s",(data['uid']))
        res=cursor.fetchall()
        if res.count>0:
            update_mail_otp(data['uid'],otp)
        else:
            insert_mail_otp(data['uid'],otp)
        
        server.quit()
        
        return 'OTP sent successfully!',otp
    except Exception as e:
        return f'An error occurred: {str(e)}'
    
       
def update_mail_otp(uid,otp):
     db=dbconnection()
     db.cursorclass=DictCursor
     cursor=db.cursor() 
     cursor.execute("update table mail_verify set otp=%s where uid=%s ",(otp,uid))
     db.commit()
def insert_mail_otp(uid,otp):
     db=dbconnection()
     db.cursorclass=DictCursor
     cursor=db.cursor() 
     cursor.execute("insert into mail_verify (uid,otp,mail) values ('%s','%s','%s') ",(otp,uid))
     db.commit()
     
    
    
def like_unlike_post(data):
    try:
         db=dbconnection()
         db.cursorclass=DictCursor
         cursor=db.cursor() 
         if data['state']=='yes':
          cursor.execute("insert into likes (user_id,event_id) values(%s,%s)",(data['user_id'],data['event_id']))
          db.commit()
          return "liked"
         else:
          cursor.execute("delete from likes where user_id=%s and event_id=%s",(data['user_id'],data['event_id']))
          db.commit()
          return "unliked"   
    except Exception as e:
         print(str(e))
         return str(e)
     
def liked_post_details(data):
    try:
        db=dbconnection()
        db.cursorclass=DictCursor
        cursor=db.cursor() 
        cursor.execute('select * from likes l inner join events e on l.event_id=e.event_id  where l.user_id=%s',(data['uid']))
        res=cursor.fetchall()
        return True,res
    except Exception as e:
        print(str(e))
        return False,str(e)
    
def friends_engage(data):
    try:
     db=dbconnection()
     db.cursorclass=DictCursor
     cursor=db.cursor() 
     cursor.execute("insert into friends_list (follower,following) values (%s,%s)",(data['followersuid'],data['followinguid']))
     db.commit()
     return data
    except Exception as e:
        print(str(e))
        return False,str(e)

def unfollow_engage(data):
    try:
     db=dbconnection()
     db.cursorclass=DictCursor
     cursor=db.cursor() 
     cursor.execute("delete from friends_list where follower=%s and following=%s",(data['followersuid'],data['followinguid']))
     db.commit()
     return data
    except Exception as e:
        print(str(e))
        return False,str(e)
    
def ffcount(data):
    try:
     db=dbconnection()
     db.cursorclass=DictCursor
     cursor=db.cursor() 
     cursor.execute("select count(*) from friends_list where follower=%s ",(data['uid']))
     follower_result = cursor.fetchone()['count']
     cursor.execute("select count(*) from friends_list where following=%s ",(data['uid']))
     following_result = cursor.fetchone()['count']   
     db.commit()
     return follower_result,following_result
    except Exception as e:
        print(str(e))
        return False,str(e)

def already_requested(data):
    db=dbconnection()
    db.cursorclass=DictCursor
    cursor=db.cursor() 
    cursor.execute("select * from engage_event where request_uid=%s and eventid=%s",(data['request_id'],data['eventid']))
    res=cursor.fetchall()
    if res.count>0:
        return True
    else:
        return False

def request_engage_event(data):#request to connect people
    try:
     print(data)
     db=dbconnection()
     db.cursorclass=DictCursor
     cursor=db.cursor() 
     sameuser=checksameuser(data)
     if sameuser:
         return False
     else:
    #   alreadyreq=already_requested(data) 
    #   if alreadyreq==True:
    #       return "Already requested"
    #   else: 
            cursor.execute("insert into engage_event (request_uid,eventid,state) values(%s,%s,%s)",(data['request_id'],data['eventid'],"requested"))  
            db.commit()
            return True 
    except Exception as e:
        print(e)
        return "error"
def delete_request(data):
    try:
     print(data)
     db=dbconnection()
     db.cursorclass=DictCursor
     cursor=db.cursor() 
     cursor.execute("delete from engage_event where request_uid=%s and eventid=%s",(data['request_id'],data['eventid'],))  
     db.commit()
     return True 
    except Exception as e:
        print(e)
        return "error"
    
    
    
def checksameuser(data):
     db=dbconnection()
     db.cursorclass=DictCursor
     cursor=db.cursor() 
     cursor.execute("select user_id from events where event_id=%s",(data['eventid']))
     res=cursor.fetchall()
     print(res)
     if res[0]['user_id']==data['request_id']:
         return True
     else:
         return False
     
def check_if_requested(data):
    print(data)
    db=dbconnection()
    db.cursorclass=DictCursor
    cursor=db.cursor() 
    sql="""select * from events e inner join engage_event ee on ee.eventid=e.event_id where e.user_id=%s """
    cursor.execute(sql,(data['cuid']))
    dbdata=cursor.fetchall()
    if dbdata:
        return dbdata
    else:
        return "No data"
    
def get_users_posts(data):
    print(data)
    db=dbconnection()
    db.cursorclass=DictCursor
    cursor=db.cursor() 
    cursor.execute("select * from events WHERE user_id=%s",(data['uid']))
    res=cursor.fetchall()
    if res:
        return res
    else:
        return "no data"
def mail_verify_result(data):
    return data
    