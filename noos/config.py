



HOST = "http://localhost:5002"
ES_ADDRESS="localhost"
SECRET_KEY='dev'

ACCOUNT_CREATION_NEEDS_INVITATION = False
AUTH_TOKEN_MAX_AGE = 30 * 24 * 3600  # default 30 days
RECOVERY_TOKEN_MAX_AGE = 24 * 3600 # default 1 days
USER_ACCOUNT_LIMIT = 0

# == SMTP ==
INVITATION_EMAIL = "mail@exmaple.com"
MAIL_SERVER   = "mail.gandi.net"
#MAIL_PORT    = "25"
MAIL_PORT     = "587"
MAIL_USERNAME = "noreply@padagraph.io"
MAIL_PASSWORD = "43F,lzdf:0q"