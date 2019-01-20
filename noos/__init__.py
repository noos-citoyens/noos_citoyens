import os
from _datetime import datetime
import html

from flask import Flask, render_template, request, jsonify, g, redirect, url_for, flash, abort, current_app
from flask_login import LoginManager, current_user, login_required

from .datastorage.user_db import Users, User



def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        ES_ADDRESS="localhost",
        USER_DATABASE = os.path.join(app.instance_path, 'noos_users.sqlite'),
        HOST = "http://localhost:5000",
        INVITATION_EMAIL = "no-reply@noos-citoyens.fr",
        ACCOUNT_CREATION_NEEDS_INVITATION = False,
        AUTH_TOKEN_MAX_AGE = 30 * 24 * 3600,  # default 30 days
        RECOVERY_TOKEN_MAX_AGE = 24 * 3600, # default 1 days
        USER_ACCOUNT_LIMIT = 0,

        # == SMTP ==

        MAIL_SERVER="localhost",
        MAIL_PORT = "465",  # "587"
        MAIL_USE_TLS = True,
        MAIL_USERNAME = None, # "noreply@example.com",
        MAIL_PASSWORD = None, #"secret",
    )

    conf_py = app.root_path + '/config.py'

    if os.path.exists(conf_py):
        app.logger.info ("reading config %s" % conf_py)
        app.config.from_pyfile(conf_py)

    if test_config is not None:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    login_manager = LoginManager()
    login_manager.init_app(app)

    # Flask-Mail
    from flask_mail import Mail
    app.mail = Mail(app)

    from flask_wtf.csrf import CSRFProtect
    app.config["WTF_CSRF_CHECK_DEFAULT"] = False
    csrf = CSRFProtect(app)
    csrf. init_app(app)

    from . import datastorage
    datastorage.init_app(app)


    with app.app_context():

        from . import auth
        auth_api = auth.blueprint("auth", __name__, url_prefix='/compte')
        app.register_blueprint(auth_api)

        with app.app_context():
            app.register_error_handler(auth.UserAccountLimitException, auth.handleUserAccountLimitException)
            app.register_error_handler(auth.EmailExistsValidationError, auth.handleEmailExistsValidationError)
            app.register_error_handler(auth.EmailNotExistsAccountError, auth.handleEmailNotExistsAccountError)
            app.register_error_handler(auth.UserAccountNotActiveError, auth.handleUserAccountNotActiveError)
            app.register_error_handler(auth.SendMailError, auth.handleSendMailError)

        errors = (
            (auth.UserLoginNotFoundError, 401, "User not found", ""),
            (401, 401, "Unauthorized",
             """The server could not verify that you are authorized to access the URL requested. "
             You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand "
             how to supply the credentials required."""),
            (404, 404, "Page not found",
             """The requested URL was not found on the server. 
             If you entered the URL manually please check your spelling and try again."""),
            (405, 405, "Method Not Allowed", "The method is not allowed for the requested URL."),
            (500,  500, "", "")
        )

        def handle_error(code, title, message):
            def wrapped(e):
                params = {'error_code': code,
                          'error_title': title,
                          'error_message': e.message if hasattr(e, 'message') else ""}

                load_from_cookie = getattr(g, 'load_from_cookie', False)
                load_from_request = getattr(g, 'load_from_request', False)

                if code == 500:
                    params['error_title'] = "C'est une erreur."
                    params['error_message'] = "There is something wrong. %s " % e.message

                if code == 401 and load_from_cookie:
                    return redirect('/')
                else:
                    return render_template('40x.xhtml', **params), code

            return wrapped

        for code_or_err, status, title, msg in errors:
            pass
            app.register_error_handler(code_or_err, handle_error(status, title, msg))


    @login_manager.user_loader
    def load_user(uuid):
        return Users.get_one_by('uuid', uuid)

    @app.route('/')
    def index():
        data = {'a':1, 'b': 2}
        return render_template('index.xhtml', title="Noos - plateforme de revendications citoyennes", data=data)

    @app.route('/test')
    def test_page():
        return render_template('test.xhtml', title='page de test')

    @app.route('/search_propositions', methods=['POST'])
    @login_required
    def test_query():
        params = request.get_json(force=True)
        q = params.get('query', None)
        limit = min(10, params.get('limit', 10))
        start = params.get('start',0)
        if q:
            results = datastorage.Proposition.simple_search(q, start, limit)
            data = []
            props = results['hits']
            for p in props:
                data.append(p.to_dict())
                data[-1]['id'] = p.meta.id
            return jsonify({"count":results['count'], "hits":data})
        else:
            return jsonify([])

    @app.route('/newprop', methods=['GET','POST'])
    @login_required
    def new_prop():
        if current_user is None:
            return redirect(url_for("auth.login"))
        if request.method == "GET":
            return render_template('newprop.xhtml', title="faire une proposition")
        else:
            try:
                cause = html.escape(request.form.get('cause'), quote=False).strip()
                content = html.escape(request.form.get('content'), quote=False).strip()
                date = datetime.now()
                ip = request.remote_addr
                if ip is None or ip == '':
                    if 'X-Forwarded-For' in request.headers:
                        ip = request.headers.getlist("X-Forwarded-For")[0].rpartition(',')[-1]
                    else:
                        ip = "127.0.0.1"
                if 5 < len(content) < 500:
                    p = datastorage.Proposition(ip=ip,
                                                uid=current_user.uuid,
                                                cause=cause,
                                                content=content,
                                                date=date)
                    p.save()
                    return redirect(url_for('get_proposition', id=p.meta.id, msg="nouveau"))
                else:
                    return render_template('newprop.xhtml', title="faire une proposition") #todo : message d'erreur avec lien vers les guidelines
            except:
                return render_template('newprop.xhtml', title="faire une proposition")

    @app.route('/proposition/<string:id>/<string:msg>')
    @app.route('/proposition/<string:id>')
    @app.route('/proposition')
    def get_proposition(id=None,msg=None):
        p = datastorage.Proposition.get(id, ignore=404)
        if p is not None:
            data = p.to_dict()
            if msg:
                data['msg'] = """
                Merci de votre contribution, il vous sera possible prochainement d'accéder à la liste complète de toutes les propositions
                """
            else:
                data['msg'] = ""
            data['id'] = p.meta.id
            user = datastorage.user_db.Users.get_one_by('uuid', p.uid)
            if user is not None:
                data['username'] = user.username
            else:
                data['username'] = "illustre anonyme"
            return render_template('proposition.xhtml', prop=data, host=current_app.config['HOST'])
        else:
            return abort(404)
    return app
