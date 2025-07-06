import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'regenerated-jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 3600  # 24 hours
    JWT_ALGORITHM = 'HS256'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://taskflow:changeme@db:5432/taskflow')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Documentation
    SWAGGER_UI_DOC_EXPANSION = 'list'
    SWAGGER_UI_JSONEDITOR = True
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 3600  # 24 hours

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
