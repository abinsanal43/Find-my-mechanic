from flask import Flask, render_template, request, session, jsonify, redirect
from DBConnection import Db

app = Flask(__name__)
app.secret_key="key"

@app.route('/')
def log():
    return render_template("index.html")

@app.route("/login_post", methods=['post'])
def login_post():
    uname=request.form['name']
    pswd=request.form['password']
    db=Db()
    res=db.selectall("SELECT * FROM login WHERE username='"+uname+"' AND PASSWORD='"+pswd+"'")
    if res is not None:
        res=res[0]
        session['lid']=res['login_id']
        if res['usertype']=="admin":
            return "<script>alert('Welcome admin');window.location='/admin_home';</script>"
        elif res['usertype']=="worker":
            db=Db()
            res2=db.selectone("SELECT * FROM worker WHERE login_id='"+str(res['login_id'])+"'")
            session['wid'] = res2['worker_id']
            return "<script>alert('Welcome worker');window.location='/worker_home';</script>"
        elif res['usertype']=="user":
            db=Db()
            res2=db.selectone("SELECT * FROM user WHERE login_id='"+str(res['login_id'])+"'")
            session['uid'] = res2['user_id']
            return "<script>alert('Welcome user');window.location='/user_home';</script>"
        else:
            return "<script>alert('Unauthorised access');window.location='/';</script>"
    else:
        return "<script>alert('Invalid details');window.location='/';</script>"

@app.route("/admin_home")
def admin_home():
    session['head'] = "ADMIN DASHBOARD"
    return render_template("admin/index.html")

@app.route("/adm_view_workers")
def adm_view_workers():
    session['head'] = "WORKER APPROVAL"
    db=Db()
    res=db.selectall("SELECT * FROM worker, login WHERE worker.login_id=login.login_id AND login.usertype='pending'")
    return render_template("admin/view_workers_and_approve.html", data=res)

@app.route("/adm_approve_worker/<lid>")
def adm_approve_worker(lid):
    db=Db()
    db.nonreturn("UPDATE login SET usertype='worker' WHERE login_id='"+lid+"'")
    return adm_view_workers()

@app.route("/adm_reject_worker/<lid>")
def adm_reject_worker(lid):
    db=Db()
    db.nonreturn("UPDATE login SET usertype='rejected' WHERE login_id='"+lid+"'")
    return adm_view_workers()

@app.route("/adm_view_approved_workers")
def adm_view_approved_workers():
    session['head'] = "APPROVED WORKERS"
    db=Db()
    res=db.selectall("SELECT * FROM worker, login WHERE worker.login_id=login.login_id AND login.usertype='worker'")
    return render_template("admin/view_approved_workers.html", data=res)

@app.route("/adm_view_users")
def adm_view_users():
    session['head'] = "VIEW USERS"
    db=Db()
    res=db.selectall("select * from user")
    return render_template("admin/view_users.html", data=res)

@app.route("/adm_view_feedback")
def adm_view_feedback():
    session['head'] = "VIEW FEEDBACK"
    db=Db()
    res=db.selectall("SELECT `feedback`.*, user.name FROM feedback, USER WHERE feedback.user_id=user.user_id order by feedback.feedback_id desc")
    return render_template("admin/view_feedback.html", data=res)




###################     WORKER
@app.route("/worker_reg")
def worker_reg():
    return render_template("worker_reg.html")
@app.route("/worker_reg_post", methods=['POST'])
def worker_reg_post():
    name=request.form['username']
    email=request.form['email']
    phone=request.form['phone']
    place=request.form['place']
    post=request.form['post']
    pin=request.form['pin']
    cat=request.form['cat']
    password=request.form['password']

    db=Db()
    res=db.nonreturn("INSERT INTO login VALUES(NULL, '"+email+"', '"+password+"', 'pending')")
    db.nonreturn("INSERT INTO `worker`(NAME, email, phone, place, post, pin, category, login_id) "
                 "VALUES('"+name+"', '"+email+"', '"+phone+"', '"+place+"', '"+post+"', '"+pin+"', '"+str(cat)+"',"
                 "'"+str(res)+"')")
    return "<script>alert('Registered');window.location='/';</script>"


@app.route("/worker_home")
def worker_home():
    session['head'] = "WORKER DASHBOARD"
    return render_template("worker/index.html")

@app.route("/wrk_view_profile")
def wrk_view_profile():
    session['head'] = "VIEW PROFILE"
    db=Db()
    res=db.selectone("SELECT * FROM worker WHERE worker_id='"+str(session['wid'])+"'")
    return render_template("worker/view_profile.html", data=res)

@app.route("/wrk_edit_profile")
def wrk_edit_profile():
    session['head'] = "EDIT PROFILE"
    db = Db()
    res = db.selectone("SELECT * FROM worker WHERE worker_id='" + str(session['wid']) + "'")
    return render_template("worker/edit_profile.html", data=res)
@app.route("/wrk_edit_profile_post", methods=['post'])
def wrk_edit_profile_post():
    name=request.form['textfield']
    phone=request.form['textfield2']
    place=request.form['textfield3']
    post=request.form['textfield4']
    pin=request.form['textfield5']
    cat=request.form['cat']
    db=Db()
    db.nonreturn("UPDATE worker SET NAME='"+name+"', phone='"+phone+"', place='"+place+"', post='"+post+"',"
                " pin='"+pin+"', category='"+cat+"' WHERE worker_id='" + str(session['wid']) + "'")
    return "<script>alert('Profile updated');window.location='/wrk_view_profile#content';</script>"

@app.route("/wrk_add_service")
def wrk_add_service():
    session['head'] = "ADD SERVICE"
    return render_template("worker/add_service.html")
@app.route("/wrk_add_service_post", methods=['post'])
def wrk_add_service_post():
    sname=request.form['sname']
    amount=request.form['amount']
    db=Db()
    db.nonreturn("INSERT INTO service(service_name, amount, worker_id) VALUES('"+sname+"', '"+amount+"', '"+str(session['wid'])+"')")
    return "<script>alert('Service added');window.location='/wrk_add_service#content';</script>"

@app.route("/wrk_view_service")
def wrk_view_service():
    session['head'] = "VIEW SERVICES"
    db=Db()
    res=db.selectall("SELECT * FROM service WHERE worker_id='"+str(session['wid'])+"'")
    return render_template("worker/view_service.html", data=res)

@app.route("/wrk_delete_service/<sid>")
def wrk_delete_service(sid):
    db=Db()
    db.nonreturn("DELETE FROM service WHERE service_id='"+str(sid)+"'")
    return "<script>alert('Service deleted');window.location='/wrk_view_service#content';</script>"

@app.route("/wrk_edit_service/<sid>")
def wrk_edit_service(sid):
    session['head'] = "EDIT SERVICE"
    db=Db()
    res=db.selectone("SELECT * FROM service WHERE service_id='"+str(sid)+"'")
    return render_template("worker/edit_service.html", data=res)
@app.route("/wrk_edit_service_post/<sid>", methods=['post'])
def wrk_edit_service_post(sid):
    sname = request.form['sname']
    amount = request.form['amount']
    db=Db()
    db.nonreturn("UPDATE service SET service_name='"+sname+"', amount='"+amount+"' WHERE service_id='"+str(sid)+"'")
    return "<script>alert('Service updated');window.location='/wrk_view_service#content';</script>"




@app.route("/wrk_view_booking")
def wrk_view_booking():
    session['head'] = "BOOKINGS"
    db=Db()
    res=db.selectall("SELECT * FROM booking, service, USER WHERE booking.user_id=user.user_id AND booking.service_id=service.service_id AND service.worker_id='"+str(session['wid'])+"'")
    return render_template("worker/view_booking.html", data=res)
@app.route("/wrk_approve_booking/<bid>")
def wrk_approve_booking(bid):
    db=Db()
    db.nonreturn("UPDATE `booking` SET STATUS='Approved' WHERE booking_id='"+str(bid)+"'")
    return "<script>alert('Booking approved');window.location='/wrk_view_booking#content';</script>"
@app.route("/wrk_reject_booking/<bid>")
def wrk_reject_booking(bid):
    db=Db()
    db.nonreturn("UPDATE `booking` SET STATUS='Rejected' WHERE booking_id='"+str(bid)+"'")
    return "<script>alert('Booking rejected');window.location='/wrk_view_booking#content';</script>"
@app.route("/wrk_complete_booking/<bid>")
def wrk_complete_booking(bid):
    db=Db()
    db.nonreturn("UPDATE `booking` SET STATUS='Completed' WHERE booking_id='"+str(bid)+"'")
    return "<script>alert('Booking completed');window.location='/wrk_view_booking#content';</script>"


@app.route("/wrk_view_booking_post", methods=['post'])
def wrk_view_booking_post():
    type=request.form['select']
    if type == "Pending Requests":
        db=Db()
        res=db.selectall("SELECT * FROM booking, service, USER WHERE booking.user_id=user.user_id AND booking.service_id=service.service_id AND service.worker_id='"+str(session['wid'])+"' and booking.status='pending'")
    elif type == "Approved Requests":
        db=Db()
        res=db.selectall("SELECT * FROM booking, service, USER WHERE booking.user_id=user.user_id AND booking.service_id=service.service_id AND service.worker_id='"+str(session['wid'])+"' and booking.status='Approved'")
    elif type == "Completed Requests":
        db=Db()
        res=db.selectall("SELECT * FROM booking, service, USER WHERE booking.user_id=user.user_id AND booking.service_id=service.service_id AND service.worker_id='"+str(session['wid'])+"' and booking.status='Completed'")
    return render_template("worker/view_booking.html", data=res)


@app.route("/worker_chat/<uid>")
def worker_chat(uid):
    session['chat_ulid']=uid
    return render_template("worker/chat.html", uid=uid)

@app.route("/worker_chatrply", methods=['post'])
def worker_chatrply():
    db=Db()
    wid=str(session['lid'])
    uid=str(session['chat_ulid'])
    lmid=request.form['lmid']
    print("Lmid  ", lmid)
    qry="SELECT * FROM chat WHERE ((from_id='"+uid+"' AND to_id='"+wid+"') OR (from_id='"+wid+"' AND to_id='"+uid+"')) and chat_id>"+lmid+" ORDER BY chat_id"
    res=db.selectall(qry)
    print(qry)
    print(res)
    for i in res:
        lmid=i['chat_id']
    print("New lmid ", lmid)
    return jsonify(status="ok", data=res, lmid=lmid)

@app.route("/woker_send_chat", methods=['post'])
def woker_send_chat():
    wid = str(session['lid'])
    uid = str(session['chat_ulid'])
    msg=request.form['msg']
    db=Db()
    db.nonreturn("INSERT INTO `chat`(from_id, to_id, message, DATE, type) VALUES('"+wid+"', '"+uid+"', '"+msg+"', CURDATE(), 'worker')")
    return jsonify(status="ok")

@app.route("/wrk_view_rating")
def wrk_view_rating():
    session['head'] = "RATINGS"
    db=Db()
    res=db.selectall("SELECT * FROM rating, USER WHERE rating.user_id=user.user_id AND rating.worker_id='"+str(session['wid'])+"'")
    return render_template("worker/view_rating.html", data=res)

##########################      USER
@app.route("/user_reg")
def user_reg():
    return render_template("user_reg.html")
@app.route("/user_reg_post", methods=['POST'])
def user_reg_post():
    name=request.form['username']
    email=request.form['email']
    phone=request.form['phone']
    place=request.form['place']
    post=request.form['post']
    pin=request.form['pin']
    password=request.form['password']

    db=Db()
    res=db.nonreturn("INSERT INTO login VALUES(NULL, '"+email+"', '"+password+"', 'user')")
    db.nonreturn("INSERT INTO `user`(NAME, email, phone, place, post, pin, login_id) "
                 "VALUES('"+name+"', '"+email+"', '"+phone+"', '"+place+"', '"+post+"', '"+pin+"', '"+str(res)+"')")
    return "<script>alert('Registered');window.location='/';</script>"


@app.route("/user_home")
def user_home():
    session['head'] = "USER DASHBOARD"
    return render_template("user/index.html")


@app.route("/user_view_profile")
def user_view_profile():
    session['head'] = "VIEW PROFILE"
    db=Db()
    res=db.selectone("SELECT * FROM user WHERE user_id='"+str(session['uid'])+"'")
    return render_template("user/view_profile.html", data=res)
@app.route("/user_edit_profile")
def user_edit_profile():
    session['head'] = "EDIT PROFILE"
    db=Db()
    res=db.selectone("SELECT * FROM user WHERE user_id='"+str(session['uid'])+"'")
    return render_template("user/edit_profile.html", data=res)
@app.route("/user_edit_profile_post", methods=['post'])
def user_edit_profile_post():
    name=request.form['textfield']
    phone=request.form['textfield2']
    place=request.form['textfield3']
    post=request.form['textfield4']
    pin=request.form['textfield5']
    db=Db()
    db.nonreturn("UPDATE user SET NAME='"+name+"', phone='"+phone+"', place='"+place+"', post='"+post+"',"
                " pin='"+pin+"' WHERE user_id='" + str(session['uid']) + "'")
    return "<script>alert('Profile updated');window.location='/user_view_profile#content';</script>"

@app.route("/user_view_services")
def user_view_services():
    session['head'] = "SERVICES"
    db=Db()
    res=db.selectall("SELECT * FROM service, worker, login WHERE service.worker_id=worker.worker_id AND worker.login_id=login.login_id AND login.usertype='worker'")
    return render_template("user/view_service.html", data=res)

@app.route("/user_view_services_post", methods=['post'])
def user_view_services_post():
    sname=request.form['text']
    db=Db()
    res=db.selectall("SELECT * FROM service, worker, login WHERE service.worker_id=worker.worker_id AND worker.login_id=login.login_id AND login.usertype='worker' and service_name like '"+sname+"%'")
    return render_template("user/view_service.html", data=res)

@app.route("/user_view_rating/<wid>")
def user_view_rating(wid):
    session['head'] = "RATINGS"
    db=Db()
    res=db.selectall("SELECT * FROM rating, USER WHERE rating.user_id=user.user_id AND rating.worker_id='"+str(wid)+"'")
    return render_template("user/view_rating.html", data=res)

@app.route("/user_book_service/<sid>")
def user_book_service(sid):
    db=Db()
    db.nonreturn("INSERT INTO booking(DATE, STATUS, user_id, service_id) VALUES(curdate(), 'pending', '"+str(session['uid'])+"', '"+str(sid)+"')")
    return "<script>alert('Service booked');window.location='/user_view_services#content';</script>"

@app.route("/user_view_booking")
def user_view_booking():
    session['head'] = "MY BOOKINGS"
    db=Db()
    res=db.selectall("SELECT * FROM booking, service, worker WHERE booking.user_id='"+str(session['uid'])+"' AND booking.service_id=service.service_id AND service.worker_id=worker.worker_id")
    return render_template("user/view_booking.html", data=res)



@app.route("/user_view_booking_post", methods=['post'])
def user_view_booking_post():
    type=request.form['select']
    if type == "Pending Requests":
        db=Db()
        res=db.selectall("SELECT * FROM booking, service, worker WHERE booking.user_id='"+str(session['uid'])+"' AND booking.service_id=service.service_id AND service.worker_id=worker.worker_id and booking.status='pending'")
    elif type == "Approved Requests":
        db=Db()
        res=db.selectall("SELECT * FROM booking, service, worker WHERE booking.user_id='"+str(session['uid'])+"' AND booking.service_id=service.service_id AND service.worker_id=worker.worker_id and booking.status='Approved'")
    elif type == "Completed Requests":
        db=Db()
        res=db.selectall("SELECT * FROM booking, service, worker WHERE booking.user_id='"+str(session['uid'])+"' AND booking.service_id=service.service_id AND service.worker_id=worker.worker_id and booking.status='Completed'")
    return render_template("user/view_booking.html", data=res)

@app.route("/user_send_rating/<wid>")
def user_send_rating(wid):
    session['head'] = "SEND RATING"
    return render_template("user/send_rating.html", wid=wid)

@app.route("/user_send_rating_post/<wid>", methods=['post'])
def user_send_rating_post(wid):
    rating=request.form['rating']
    db=Db()
    res=db.selectone("select * from rating where worker_id='"+str(wid)+"' and user_id='"+str(session['uid'])+"'")
    if res is None:
        db=Db()
        db.nonreturn("INSERT INTO rating(worker_id, user_id, rating, DATE) VALUES('"+str(wid)+"', '"+str(session['uid'])+"', '"+str(rating)+"', CURDATE())")
    else:
        db=Db()
        db.nonreturn("update rating set rating='"+str(rating)+"' where rating_id='"+str(res['rating_id'])+"'")
    return user_view_booking()

@app.route("/user_chat/<wid>")
def user_chat(wid):
    session['chat_wlid']=wid
    return render_template("user/chat.html", wid=wid)

@app.route("/user_chatrply", methods=['post'])
def user_chatrply():
    db=Db()
    wid=str(session['chat_wlid'])
    uid=str(session['lid'])
    lmid=request.form['lmid']
    print("Lmid ", lmid)
    qry="SELECT * FROM chat WHERE ((from_id='"+uid+"' AND to_id='"+wid+"') OR (from_id='"+wid+"' AND to_id='"+uid+"')) and chat_id>"+lmid+" ORDER BY chat_id"
    print(qry)
    res=db.selectall(qry)
    print(res)
    # lmid=""
    for i in res:
        lmid=i['chat_id']
    print("New lmid ", lmid)
    return jsonify(status="ok", data=res, lmid=lmid)

@app.route("/user_send_chat", methods=['post'])
def user_send_chat():
    wid = str(session['chat_wlid'])
    uid = str(session['lid'])
    msg=request.form['msg']
    db=Db()
    db.nonreturn("INSERT INTO `chat`(from_id, to_id, message, DATE, type) VALUES('"+uid+"', '"+wid+"', '"+msg+"', CURDATE(), 'user')")
    return jsonify(status="ok")

@app.route("/user_send_feedback")
def user_send_feedback():
    session['head'] = "SEND FEEDBACK"
    return render_template("user/send_feedback.html")

@app.route("/user_send_feedback_post", methods=['post'])
def user_send_feedback_post():
    feed=request.form['textfield']
    db=Db()
    db.nonreturn("INSERT INTO feedback(DATE, feedback, user_id) VALUES(CURDATE(), '"+feed+"', '"+str(session['uid'])+"')")
    return "<script>alert('Feedback sent');window.location='/user_send_feedback#content';</script>"


@app.route("/logout")
def logout():
    return redirect("/")
if __name__ == '__main__':
    app.run()
