from flask import Blueprint,render_template,redirect,url_for,flash,session
from flask_login import login_required,current_user
from pyjong import db,room_players
from pyjong.models import UserData,retrieve_game_updates,add_friend,delete_friend,send_request,get_new_requests,get_friends_list,get_invites,send_invite
from pyjong.main.forms import FriendRequest,AcceptFriendRequest,DeleteFriend,InviteFriend,AcceptInvite,PlaySolo
import datetime
from time import time

main_blueprint = Blueprint('main',__name__,template_folder='templates/main')

#initialise socketiofunctions
from pyjong.apps.socketioapps import chat,mahjongsocketio


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
    solo_form = PlaySolo()

    if session['in_room']:
        name = session['username']
        room = session['room']
        return render_template('game.html',form=form,name=name,room=room)

    #validation check for invite
    if form.validate_on_submit():
        send_invite(session_username=current_user.username,invited_username=form.select_friend.data,room=form.room_name.data)
        session['room'] = form.room_name.data
        session['in_room'] = True
        session['players'] = 2
        #set inviter as player one
        session['player_id'] = 1
        #add names to variable to be accessed on game 0=player1_name,1=player3_name
        room_players[session['room']] = [session['username'],form.select_friend.data]

        flash("招待状を送りました！",'alert-success')
        return redirect(url_for('main.game'))
    #setup solo room
    if solo_form.validate_on_submit():
        session['room'] = str(int(time()))
        session['players'] = 1
        session['in_room'] = True
        session['player_id'] = 1
        #set name for player2 to none
        room_players[session['room']] = [session['username'],None]
        return redirect(url_for('main.game'))

    return render_template('game.html',form=form,solo_form=solo_form)

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
    game_updates = retrieve_game_updates()


    #check all forms for positive return
    if accept_invite_form.validate_on_submit():
        #room name is linked to select_friend value
        session['room'] = accept_invite_form.select_friend.data
        session['in_room'] = True
        session['players'] = 2
        #set joining user as player 2
        session['player_id'] = 2
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
    return render_template('friends.html',form_delete=form_delete,form_add=form_add,form_req=form_req,accept_invite_form=accept_invite_form,game_updates=game_updates)
