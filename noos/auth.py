#-*- coding:utf-8 -*-
from flask import Blueprint, current_app, render_template, request, jsonify, redirect, flash, url_for, g
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from itsdangerous import URLSafeTimedSerializer

from .datastorage.user_db import Users

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField,  PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

infos = {
            "desc" : "user api",
            "version" : "0.2dev"
        }

serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

class AuthError(Exception):
    pass

class UserLoginExistsError(AuthError):
    pass

class UserPasswordInvalidError(AuthError):
    pass

class UserLoginNotFoundError(AuthError):
    pass

class EmailExistsValidationError(Exception):
    def __init__(self, message, user):
        super(EmailExistsValidationError, self).__init__(message)
        self.user = user


def handleEmailExistsValidationError(err):
    if err.user : #and not err.user.is_active():
        
        email = err.user.email
        token = serialiser.dumps(("activation", email))

        return render_template('account-creation.xhtml',
                                step="email-in-use",
                                token=token,
                                email=email,
                                username = err.user.username,
                                activ = err.user.is_active() )


class InvitationForm(FlaskForm):
    email = StringField('email', [DataRequired(), Email()], default="")
    invite = BooleanField('invite', [DataRequired()], default="")

    def validate(self):
        rv = FlaskForm.validate(self)
        if rv:
            user =  Users.get_by_email(self.email.data)
            if user :
                message = 'An account exists with this email'
                raise EmailExistsValidationError(message, user)
        return rv  


class CreateUserForm(FlaskForm):

    invitation = StringField('invitation', [DataRequired()] if current_app.config['ACCOUNT_CREATION_NEEDS_INVITATION']  else [], default="")
    username = StringField('username', [DataRequired()], default="")
    email = StringField('email', [DataRequired(), Email()], default="")
    password = PasswordField('New Password', [DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password', [DataRequired()])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        rv = FlaskForm.validate(self)
        print(rv)

        # parse invitation token
        invitation = self.invitation.data
        email = ""

        try:
            if current_app.config['ACCOUNT_CREATION_NEEDS_INVITATION'] :
                seed, email = serialiser.loads(invitation)

                if seed != "invitation":
                    raise ValueError("")

            if self.email.data == "":
                self.email.data = email

        except Exception as err:
            self.invitation.errors.append('Wrong token' + err.message)
            return False


        rv = self.email.validate(email)
        if rv :
            self.username.errors.append('Adresse invalide.')

        # uniqness
        if Users.has_pseudo(self.username.data):
            self.username.errors.append('Ce pseudo utilisé')
            rv = False

        user =  Users.get_by_email(self.email.data)
        if user :
            message = 'Un compte est déja enregistré pour cette adresse %s' % email
            self.email.errors.append(message)
            raise EmailExistsValidationError(message, user)

        # password complexity
        if not self.password.data or len(self.password.data) < 8:
            self.password.errors.append('La longueur de password minimal est de 8 caractères')
            rv = False

        return rv

        
class UserAccountLimitException(Exception):
    def __init__(self):
        super(Exception, self).__init__("Maximum user account %s" % current_app.config['USER_ACCOUNT_LIMIT'])


def handleUserAccountLimitException(err):
    return render_template(
                'account-creation.xhtml' ,
                step="user-account-limit",
                count=current_app.config['USER_ACCOUNT_LIMIT'],
            )


class UserAccountNotActiveError(Exception):
    def __init__(self, uuid, email, message):
        super(Exception, self).__init__("")
        self.email = email
        self.message = message
        self.uuid = uuid

def handleUserAccountNotActiveError(err):
    return render_template(
                'account-creation.xhtml',
                step="email-in-use",
                message = err.message,
                email = err.email,
                uuid = err.uuid,
                activ = False
            )

class EmailNotExistsAccountError(Exception):
    def __init__(self, message, email):
        super(EmailNotExistsAccountError, self).__init__(message)
        self.email = email


def handleEmailNotExistsAccountError(err):
    return render_template(
                'account-recovery.xhtml' ,
                step="email-not-in-use",
                email=err.email,
            )


class RecoveryEmailForm(FlaskForm):
    email = StringField('email', [DataRequired(), Email()], default="")

    def validate(self):
        rv = FlaskForm.validate(self)
        
        if rv:
            email = self.email.data
            user = Users.get_by_email(email)
            
            if user is None :
                message = 'No account exists with this email'
                raise EmailNotExistsAccountError(message, email)
        return rv


class RecoveryPasswordForm(FlaskForm):
    password = PasswordField('New Password', [DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password', [DataRequired()])
    token = StringField('token', [DataRequired()], default="")
    
    def  validate(self):
        rv = FlaskForm.validate(self)

        # password complexity
        if len(self.password.data) < 8:
            self.password.errors.append('Password length must be at least 8 ')
            rv = False
        return rv


class SendMailError(Exception):
    def __init__(self, email, error):
        super(SendMailError, self).__init__("can't send email to %s" % email)
        self.email = email
        self.error = error


def handleSendMailError(err):
    return render_template(
                'account-creation.xhtml' ,
                step="cant-send-email",
                email=err.email,
            )


def send_invitation_link(email):
    
    token = serialiser.dumps(( "invitation", email ))
    url = "%s/account/create-account/%s" % (current_app.config['HOST'], token)

    subject = "%s // Invitation" % current_app.config['HOST'][7:]
    body   = """
        This address requested an invitation to join noos citoyens:
          %s

        Follow this link to create a new account
          %s
    """% (email, url)

    send_to = email
   
    noreply_send(subject, send_to, body.replace("    ", ""))


def send_activation_link(email):
    
    token = serialiser.dumps(("activation", email))
    url = current_app.config['HOST'] + url_for("auth.activate_account", token=token)

    subject = "%s // Activez cette adresse" % current_app.config['HOST'][7:]

    body = """
        Bienvenu sur NOos-citoyen
            
        Vous êtes désormais incrit sur la plateforme NOos-Citoyens.
        Pour valider votre inscription, veuillez suivre le lien suivant:
         %s
        
        Nous vous contacterons par la suite pour vous tenir informé des avancées de la plate-forme.
        Dans quelques jours vous recevrez un courriel pour vous prévenir de l'ouverture des votes.
        
        N’hésitez pas à nous contacter pour coopérer si vous le souhaitez.
        À bientot,
        
        **L'équipe de NOos-Citoyens**
        
        
        *Toutes les données collectées sur la plate-forme NOos-Citoyens sont téléchargeables en version anonymisées 
        dans des formats ouverts, ce qui permet à tout citoyen, de produire ses propres analyses sur ces données. 
        Tous les outils qui permettent à NOos-Citoyens de fonctionner pour récolter, cartographier, analyser et synthétiser 
        les propositions et les opinions citoyennes sont diffusés sous licence libre. 
        Notre objectif est de répondre dans une totale transparence aux besoins de compréhension, de dialogue et d’expression des citoyens. 
        Le plan n’est pas figé, le code s’écrit au fil des besoins et des événements. 
        Chacun qui est intéressé peut participer à la vie de la plate-forme en émettant des propositions, 
        en prenant position J'APPROUVE ou JE DÉSAPPROUVE les propositions, et en participant à l’analyse des données 
        au travers de campagnes de «crowdsourcing» que nous allons bientôt mettre en place.
        
        Toutes les contributions sont les bienvenues
        N’hésitez pas à nous contacter pour coopérer ou établir des liens entre les sites utilisant les données récoltées par ces outils.*
        
    """ % url
    
    noreply_send(subject, email, body.replace("    ", ""))


def send_password_recovery_link(email, hashed_password ):
    
    token = serialiser.dumps(("recovery", email, hashed_password  ))
    
    url = current_app.config['HOST'] + url_for("auth.change_password") + "/" + token
    subject = "%s // Reset your password" % current_app.config['HOST'][7:]

    body   = """
        You recently requested a password reset.
         
        To change your password, click here or paste the following link into your browser:  

        %s
        
        The link will expire in 24 hours.

        If you didn't request this, you don't need to do anything; you won't receive any more email from us. Please do not reply to this e-mail;
        
    """ % url
    
    noreply_send(subject, email, body.replace("    ", ""))


def noreply_send(subject, to, body):
    try:
        message = Message(sender = ( "noos-citoyen", "ne.pas.repondre@padagraph.io" ))
        message.recipients = [to]
        message.body = body
        message.subject = subject
        current_app.logger.info("sending message %s " % subject)
        current_app.mail.send(message)
    except Exception as err:
        current_app.logger.info('ERR send mail %s %s \n %s' % (subject, to, err))
        raise SendMailError(to, err)


def authenticate_user(request):
    # GET
    email = None
    password = None

    if request.method == 'POST':

        email = request.form.get('email', None )
        password = request.form.get('password', None )

        if request.json:
            email = request.json.get('email', None )
            password = request.json.get('password', None )

        user = Users.get_by_email(email)
        if user is None:
            raise EmailNotExistsAccountError("Aucun compte n'est enregistré avec cette adresse.", email)
        if not user.is_active():
            raise UserAccountNotActiveError(user.uuid, email, "Un compte est crée avec cette adresse mais n a pas été activé.")

    return Users.authenticate(email, password, hashed=False)


def blueprint(*args, **kwargs):
    """ user authentication api """

    api = Blueprint(*args, **kwargs)

    @api.route("/about", methods=['GET', 'POST'])
    def about():
        return jsonify( infos )

    # === auth ====

    @api.route("/authenticate", methods=['GET', 'POST'])
    def auth():
        user = authenticate_user(request)

        if user:
            login_user(user)
            return jsonify({
                'logged' : True,
                'user' : user.as_dict(),
                'token': user.get_auth_token(),
            })

        return "login failed", 401

    @api.route("/login", methods=['GET', 'POST'])
    def login():
        logged = False

        user = authenticate_user(request)
        if user:
            login_user(user)
            flash('Logged in successfully.')

            url = request.args.get('redirect', "/")
            return redirect(url)


        return redirect( url_for("auth.login_form", ))
    
    @api.route("/logout", methods=['GET', 'POST'])
    def logout():

        try:
            logout_user()
        finally:
            pass

        return redirect(url_for('index'))
        
    # === create account ===

    @api.route("/invitation", methods=['POST'])
    def invite(invitation=None):
        
        # validate token
        form = InvitationForm()

        if form.validate():
            send_invitation_link(form.email.data)
            return render_template('account-creation.xhtml' , step="invitation-send")

        return redirect('/?invalid=1')

    @api.route("/connexion")
    def login_form():
        if not current_user.is_authenticated:
            step = "login"
            return render_template('account-login.xhtml', step="login")

        return redirect(url_for('index'))

    @api.route("/create-account", methods=['POST', 'GET'])
    @api.route("/create-account/<string:invitation>", methods=['GET'])
    def create_account(invitation=None):

        step = "create"
        has_error = False

        if current_app.config['USER_ACCOUNT_LIMIT'] > 0:
            if Users.get_user_count() >= current_app.config['USER_ACCOUNT_LIMIT']:
                raise UserAccountLimitException()

        form = CreateUserForm()

        if request.method == "GET":
            form.invitation.data = invitation

            if not form.validate():
                print (form.invitation.errors)
                if len(form.invitation.errors):
                    return render_template('account-creation.xhtml' , step="invitation-invalid")

        elif request.method == "POST":
            if form.validate():
                # create user
                username = form.username.data
                email = form.email.data
                password = form.password.data

                Users.add_user(email, username, password)

                send_activation_link(email)

                return render_template('account-creation.xhtml', step="validate", form=form )

            else:
                has_error = True

                if len(form.invitation.errors):
                    return render_template('account-creation.xhtml' , step="invitation-invalid" )

        return render_template('account-creation.xhtml', step=step, form=form, has_error=has_error)

    @api.route("/resend-validation/<string:uuid>", methods=['GET'])
    def resend_validation(uuid=None):

        # validate token
        try :

            user = Users.get_by_uuid(uuid)
            send_activation_link(user.email)
            return render_template('account-creation.xhtml' ,
                                   step="validation-resent",
                                   username=user.username,
                                   email=user.email)

        except :
            return render_template('account-creation.xhtml', step="token-invalid")

    @api.route("/activate-account/<string:token>", methods=['GET'])
    def activate_account(token=None):

        # validate token
        try :
            seed, email = serialiser.loads(token)
            print("activate account %s %s" %(seed, email))

            if seed != "activation":
                raise ValueError("wrong token")
                

            user = Users.get_by_email(email)
            Users.activate(email)
            login_user(user)
            return render_template('account-creation.xhtml' , step="active", username=user.username)
            
        except Exception as err :
            current_app.logger.info("Activation error %s /n %s " % (email,err))
            return render_template('account-creation.xhtml', step="token-invalid" )

    # === / password recovery ===


    @api.route("/password-recovery", methods=['GET', 'POST'])
    def password_recovery():

        form = RecoveryEmailForm()
        
        if request.method == "POST" and form.validate():
            
            # send email recovery 
            try :
                email = form.email.data
                if Users.has_email(email):
                    user = Users.get_by_email(email)
                    send_password_recovery_link(email, user.password )
                return render_template('account-recovery.xhtml', step="email-sent", email= email )
            except :

                return render_template('account-recovery.xhtml' , step="token-invalid" )

        return render_template('account-recovery.xhtml', step="email-form")
    
    @api.route("/change-password", methods=['POST'])
    @api.route("/change-password/<string:token>", methods=['GET'])
    def change_password(token=None):
        form =  RecoveryPasswordForm()

        if request.method == "POST":
            token = form.token.data

        try :
            # validate 24h token
            
            seed, email, pwd = serialiser.loads(token, max_age=current_app.config['RECOVERY_TOKEN_MAX_AGE'])
            current_app.logger.info("change-password")
            if seed != "recovery":
                raise ValueError("wrong token, %s" % seed)

            user = Users.get_by_email(email)
            if not user.verify_password(pwd, hashed=True):
                raise ValueError("wrong token, %s" % seed)

            if request.method == "POST":
                if  form.validate():                
                    user.change_password(form.password.data)
                    login_user(user)
                    return render_template('account-recovery.xhtml', step="password-changed" )
                    
                return render_template('account-recovery.xhtml', step="password-form", token=token, email=email,
                                       has_error=True, errors=form.errors )
        except :
            return render_template('account-recovery.xhtml', step="token-invalid")

        return render_template('account-recovery.xhtml', step="password-form", token=token, has_error=False)

    @api.route("/u/<string:uid>", methods=['GET'])
    @login_required
    def user(uuid):
        """ Get public info for user <user> """
        user = Users.get_by_uuid(uuid)
        return jsonify({ uuid : user.as_dict() })

    @api.route("/me", methods=['GET'])
    @login_required
    def me():
        user = current_user
        return jsonify(user.as_dict())

    @api.route("/me/generate_auth_token", methods=['GET'])
    @login_required
    def generate_auth_token():
        user = current_user
        return jsonify({'user': user.as_dict(),
                        'token': user.get_auth_token(),
                        })
    return api
