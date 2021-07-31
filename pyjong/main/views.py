from flask import Blueprint,render_template,redirect,url_for,flash,session
from flask_login import login_required,current_user
from pyjong import db
from pyjong.models import UserData
from pyjong.main.forms import FriendRequest,AcceptFriendRequest,DeleteFriend,InviteFriend,AcceptInvite
import datetime

main_blueprint = Blueprint('main',__name__,template_folder='templates/main')

#################################################
#########DB FUNCTIONS##########################
#################################################


#adds new friend to both the requester and requested
def add_friend(requested_username,requester_username):
    #add requester to requested
    result1 = UserData.query.filter_by(username=requested_username).first()
    new_friends_list = eval(result1.friends_list)
    new_friends_list.append(requester_username)
    result1.friends_list = str(new_friends_list)
    #add requested to requester
    result2 = UserData.query.filter_by(username=requester_username).first()
    new_friends_list = eval(result2.friends_list)
    new_friends_list.append(requested_username)
    result2.friends_list = str(new_friends_list)

    db.session.add_all([result1,result2])
    db.session.commit()

    ##check to see if written correctly
    # result1 = UserData.query.filter_by(username=requested_username).first()
    # result2 = UserData.query.filter_by(username=requester_username).first()
    # print(result1.friends_list,result2.friends_list)

#removes friends from both users
def delete_friend(requested_username,requester_username):
    #add requester to requested
    result1 = UserData.query.filter_by(username=requested_username).first()
    new_friends_list = eval(result1.friends_list)
    new_friends_list.remove(requester_username)
    result1.friends_list = str(new_friends_list)
    #add requested to requester
    result2 = UserData.query.filter_by(username=requester_username).first()
    new_friends_list = eval(result2.friends_list)
    new_friends_list.remove(requested_username)
    result2.friends_list = str(new_friends_list)

    db.session.add_all([result1,result2])
    db.session.commit()

    ##check to see if written correctly
    result1 = UserData.query.filter_by(username=requested_username).first()
    result2 = UserData.query.filter_by(username=requester_username).first()
    print(result1.friends_list,result2.friends_list)


#adds new friend request to requested user from requesting user
def send_request(requester_username,requested_username):
    result = UserData.query.filter_by(username=requested_username).all()
    if len(result) > 0 and requester_username != requested_username:
        result = result[0]
        new_friend_requests = eval(result.friend_requests)
        #check to make sure multiple requests are not being sent
        if requester_username in new_friend_requests:
            return False
        else:
            new_friend_requests.append(requester_username)
            result.friend_requests = str(new_friend_requests)
            db.session.add(result)
            db.session.commit()
            return True
    else:
        return False

#gets new friend request from db and adds to session, deleting from db
def get_new_requests(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    new_requests_list = eval(current_usr.friend_requests)

    if session['updated'] == False:
        if len(new_requests_list) > 0:
            session['requests'] = new_requests_list
            session['new_requests'] = True
            current_usr.friend_requests = str([])
            db.session.add(current_usr)
            db.session.commit()
            session['updated'] = True
        else:
            print('new requests set to false')
            session['new_requests'] = False
            session['updated'] = True
    else:
        if len(new_requests_list) > 0:
            for request in new_requests_list:
                session['requests'].append(request)
            session['new_requests'] = True
            current_usr.friend_requests = str([])
            db.session.add(current_usr)
            db.session.commit()
        else:
            pass

#retrieve list of users friends
def get_friends_list(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    friends_list = eval(current_usr.friends_list)
    session['friends'] = friends_list
    if len(friends_list) > 0:
        session['has_friends'] = True
        #retrieve friend stats
        session['friend_stats'] = dict()
        # for friend in session['friends']:
        #     current_usr = UserData.query.filter_by(username=friend).first()
    else:
        session['has_friends'] = False
    return friends_list

#call username and retrieve invites. invites retrieved will be transferred to session memory and deleted form database
def get_invites(session_username):
    current_usr = UserData.query.filter_by(username=session_username).first()
    invites = eval(current_usr.invites)
    if session['has_new_invites'] and len(invites) > 0:
        for invite in invites:
            session['invites'].append(invite)
        current_usr.invites = str([])
        db.session.add(current_usr)
        db.session.commit()
    elif len(invites) > 0 and session['has_new_invites'] == False:
        session['has_new_invites'] = True
        session['invites'] = invites
        current_usr.invites = str([])
        db.session.add(current_usr)
        db.session.commit()
    elif session['has_new_invites']:
        pass
    else:
        session['has_new_invites'] = False

#invites will include senders name and room name '['username','room']'
def send_invite(session_username,invited_username,room):
    user = UserData.query.filter_by(username=invited_username).first()
    invites = eval(user.invites)
    invites.append((session_username,room))
    user.invites = str(invites)
    db.session.add(user)
    db.session.commit()

#########################################################
##########################################################

##########FORM FUNCTIONS
#function to generate friend lists for invite choice
def add_friends_to_form(form):
    if len(session['friends']) > 0:
        form.select_friend.choices = [(usr,usr) for usr in session['friends']]
        session['has_friends'] = True
    else:
        session['has_friends'] = False
    return form
#function to generate friend lists for invite choice
def add_friends_to_form(form):
    if len(session['friends']) > 0:
        form.select_friend.choices = [(usr,usr) for usr in session['friends']]
        session['has_friends'] = True
    else:
        session['has_friends'] = False
    return form
#function to add friend requests to form
def add_friend_requests_to_form(form):
    if session['new_requests']:
        form.select_friend.choices = [(usr,usr) for usr in session['requests']]
    else:
        form.select_friend.choices = [('no_friends','友達はまだいないようです')]
    return form
def add_invites_to_form(form):
    if session['has_new_invites']:
        form.select_friend.choices = [(room,usr) for usr,room in session['invites']]
    else:
        pass
    return form

#######################################################

#####ROUTE FUNCTIONS

@main_blueprint.route('/info')
def info():
    return render_template('info.html')

@main_blueprint.route('/game',methods=['GET','POST'])
@login_required
def game():

    #forms
    form = InviteFriend()
    form = add_friends_to_form(form)

    if session['in_room']:
        name = session['username']
        room = session['room']
        return render_template('game.html',form=form,name=name,room=room)

    #validation check
    if form.validate_on_submit():
        send_invite(session_username=current_user.username,invited_username=form.select_friend.data,room=form.room_name.data)
        session['room'] = form.room_name.data
        flash("招待状を送りました！",'alert-success')
        return redirect(url_for('main.game'))

    return render_template('game.html',form=form)

@main_blueprint.route('/friends',methods=['GET','POST'])
@login_required
def friends():

    #update information
    get_new_requests(current_user.username)
    get_invites(current_user.username)
    get_friends_list(current_user.username)
    #add choices to forms
    form_delete = DeleteFriend()
    form_delete = add_friends_to_form(form_delete)
    form_req = FriendRequest()
    form_add = AcceptFriendRequest()
    form_add = add_friend_requests_to_form(form_add)
    accept_invite_form = AcceptInvite()
    accept_invite_form = add_invites_to_form(accept_invite_form)


    #check all forms for positive return
    if accept_invite_form.validate_on_submit():
        session['room'] = accept_invite_form.select_friend.data
        session['in_room'] = True
        flash(f"{session['room']}に入りました！","alert-success")
        return redirect(url_for('main.game'))
    if form_delete.validate_on_submit():
        delete_friend(requested_username=form_delete.select_friend.data,requester_username=current_user.username)
        flash("友達を削除しました。",'alert-success')
        return redirect(url_for('main.friends'))
    if form_req.validate_on_submit():
        if send_request(requester_username=current_user.username,requested_username=form_req.username.data):
            flash(f'{form_req.username.data}にリクエストを送りました！','alert-success')
            return redirect(url_for('main.friends'))
        else:
            flash('入力に問題があるようです。すでにリクエストを送ったか、ユーザーネームが間違っていないかご確認ください。','alert-warning')
            return redirect(url_for('main.friends'))
    if form_add.validate_on_submit():
        for friend in form_add.select_friend.data:
            add_friend(requested_username=current_user.username,requester_username=friend)
        session['new_requests'] = False
        session['requests'] = []
        flash('友達を追加しました！','alert-success')
        return redirect(url_for('main.friends'))
    return render_template('friends.html',form_delete=form_delete,form_add=form_add,form_req=form_req,accept_invite_form=accept_invite_form)
