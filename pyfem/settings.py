
class Config(object):
    DEBUG               = False
    
    HOME_PATH           = './'
    SECRET_KEY          = 'yougonnawannachangethis'
    
    LOG_FILE            = 'C:/Users/Larry/__prjs/__py/pyfem/pyfem/logs/pyfem.log'
    LOG_LEVEL           = 'debug'
    
    DEFAULT_MAIL_SENDER = ("mail manager", "mail@manager.com")
    SECRET_KEY          = '5WOGba[U\\^yGXA6"^^a+9|Nx|xfF\:U;N_[U\\'
    
    HOST                = 'localhost'
    TESTING_HOST        = 'localhost:5000/test'
    
    DEFAULT_MAIL_SENDER = ("mail manager", "mail@manager.com")
    SECRET_KEY          = 'asdfasdfasdfasdfasdfasdfadsfasdf'
    
    MONGO_HOST          = 'localhost'
    MONGO_PORT          = None
    MONGO_DBNAME        = 'pyfem'
    MONGO_USERNAME      = None
    MONGO_PASSWORD      = None
    MONGO_TEST_DBNAME   = 'pyfem-test'
    
    # used by mongoengine
    MONGODB_SETTINGS    = dict(host=MONGO_HOST, port=MONGO_PORT, me=MONGO_DBNAME, username=MONGO_USERNAME, password=MONGO_PASSWORD)
    
    ES_HOST             = 'localhost'
    ES_PORT             = 9200
    ES_NAME             = 'index'
    ES_TEST_HOST        = 'localhost'
    ES_TEST_PORT        = 9200
    ES_TEST_NAME        = 'index-test'
    
    ES                  = {
    'host'              : 'localhost',
    'port'              : 9200,
    'name'              : 'index'
    }
    
    #WTForms Settings
    CSRF_ENABLED        = True
    CSRF_SESSION_KEY    = '_csrf_token'
    
    #Flask Mail settings
    MAIL_SERVER         = 'localhost'
    MAIL_PORT           =  25
    MAIL_USE_TLS        = False
    MAIL_USE_SSL        = False
    MAIL_DEBUG          = DEBUG
    MAIL_USERNAME       = None
    MAIL_PASSWORD       = None
    DEFAULT_MAIL_SENDER = None


# try to COMPLETELY override the above Config with a local one
# TODO: Override vs Replace entire Object
try:
    from local_settings import Config as LocalConfig
    class Config(LocalConfig): pass

except ImportError:
    pass