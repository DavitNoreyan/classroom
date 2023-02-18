class Config:
    SQLALCHEMY_DATABASE_URI = ""
    SECRET_KEY = 'secret-key'
    SECURITY_FRESHNESS_GRACE_PERIOD = 3600
    SECURITY_DEFAULT_REMEMBER_ME = True
    SECURITY_REGISTERABLE = True



class DevEnvConfig(Config):
    HOST = '127.0.0.1'
    PORT = 5000
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/davit/Desktop/projects/personal/classroom/classroom.db"
    UPLOAD_FOLDER = '/home/davit/Desktop/projects/personal/classroom/videos'

