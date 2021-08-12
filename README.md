About this Project
__________________________

This is an online mahjong application experimenting with Flask-SocketIO to allow communication between server and user in realtime to conduct multiplayer games.
The GUI and text of this project are all written in Japanese. Most of the terms used referring to MahJong concepts are Japanese.

Built with:
1. Flask
2. Flask-SocketIO
3. javascript SocketIO
4. SQLAlchemy
5. PostgreSQL
6. bootstrap
7. jquery

Getting Started
__________________________

Prerequisites:
You must have a hosting acount such as Heroku or Azure to host this software.

Steps for Heroku:
0. clone this repository locally
1. Login or register
2. From dashboard navigate to create new application
3. Enter app name and other config
4. install Heroku CLI (https://devcenter.heroku.com/articles/heroku-command-line)
5. login to heroku from prompt
  $ heroku login
6. add heroku SQL with commands below
    $ heroku addons:create heroku-postgresql:<hobby-dev>
7. get the database address with the following command
    $ heroku config
8. change the database url to a format compatible with SQLAlchemy
    Ex. postgres://foo:foo@heroku.com:5432/hellodb -> postgresql://foo:foo@heroku.com:5432/hellodb
9. add the adjusted database url to flask app config in __init__.py
    app.config['SQLALCHEMY_DATABASE_URI'] = postgresql://foo:foo@heroku.com:5432/hellodb
10. cd to the location of local repository in prompt
11. input following command
  $ git init
  $ heroku git:remote -a YOUR_APP_NAME_HERE
  $ git add .
  $ git commit -am "YOUR NOTE HERE"
  $ git push heroku master
12. Then you should have this app running!

Steps for Google Cloud
1. Create a new Project in Google Cloud
2. Open console
3. Clone this git using git cli
  $ git https://github.com/inoueaus/pymahjong/ -b google-cloud-version
4. cd to the cloned repository
  $ cd pymahjong
5. Deploy app using gcloud
  $ gcloud app deploy
6. You're good to go!


Usage
__________________________

This project acts as an example of how you can use SocketIO to have users directly interact with a server and implement interactive usage of Python with user interface. Feel free to adapt it or improve it as you see fit.

Playing:
1. create account
2. navigate to game paginate
3. click 一人で遊ぶ to play one player


Roadmap
__________________________

I plan on improving the userinterface of the game and of course getting rid of remaining (yet to be found) bugs. I need better understanding of Javascript to do this.
Also, there are known issues posted in the open issues section of this git.
The point calculation system is still very buggy.


Contributing
__________________________

You are more than welcome to build upon the code I have here! Please create a new branch before doing so.


License
__________________________

Distributed under the MIT license.


Acknowledgements
__________________________
I relied heavily on Miguel Grinbergs Flask-SocketIO and examples he provides.
