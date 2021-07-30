from flask import Blueprint,render_template,redirect,url_for,flash,session
from flask_login import login_required,current_user
from pyjong import db
from pyjong.models import UserData
from pyjong.main.forms import InviteFriend,FriendRequest,AcceptFriendRequest,JoinGame
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
    if len(invites) > 0:
        session['has_new_invites'] = True
        session['invites'] = invites
        current_usr.invites = str([])
        db.session.add(current_usr)
        db.session.commit()
    else:
        session['has_new_invites'] = False


#########################################################
##########################################################

@main_blueprint.route('/info')
def info():
    return render_template('info.html')

@main_blueprint.route('/game',methods=['GET','POST'])
@login_required
def game():
    return render_template('game.html')

@main_blueprint.route('/friends',methods=['GET','POST'])
@login_required
def friends():
    #function to generate friend lists for invite choice
    def add_friends_to_form(form_invite):
        if len(session['friends']) > 0:
            form_invite.select_friend.choices = [(usr,usr) for usr in session['friends']]
        else:
            form_invite.select_friend.choices = [('no_friends','友達はまだいないようです')]
        return form_invite
    #function to add friend requests to form
    def add_friend_requests_to_form(form_add):
        if session['new_requests']:
            form_add.select_friend.choices = [(usr,usr) for usr in session['requests']]
        else:
            form_add.select_friend.choices = [('no_friends','友達はまだいないようです')]
        return form_add

    #update information
    get_new_requests(current_user.username)
    get_invites(current_user.username)
    get_friends_list(current_user.username)
    #add choices to forms
    form_invite = InviteFriend()
    form_invite = add_friends_to_form(form_invite)
    form_req = FriendRequest()
    form_add = AcceptFriendRequest()
    form_add = add_friend_requests_to_form(form_add)


    #check all forms for positive return
    if form_invite.validate_on_submit():
        pass
    if form_req.validate_on_submit():
        if send_request(requester_username=session['username'],requested_username=form_req.username.data):
            flash(f'{form_req.username.data}にリクエストを送りました！','alert-success')
            return render_template('friends.html',form_invite=form_invite,form_add=form_add,form_req=form_req)
        else:
            flash('入力に問題があるようです。すでにリクエストを送ったか、ユーザーネームが間違っていないかご確認ください。','alert-warning')
            return render_template('friends.html',form_invite=form_invite,form_add=form_add,form_req=form_req)
    if form_add.validate_on_submit():
        for friend in form_add.select_friend.data:
            add_friend(requested_username=session['username'],requester_username=friend)
            print('friend added')
        session['new_requests'] = False
        session['requests'] = []
        get_friends_list(session['username'])
        flash('友達を追加しました！','alert-success')
        return render_template('friends.html',form_invite=form_invite,form_add=form_add,form_req=form_req)
    return render_template('friends.html',form_invite=form_invite,form_add=form_add,form_req=form_req)
