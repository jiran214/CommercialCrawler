
# Mongodb数据配置
import pymongo

DEV_HOST = '127.0.0.1'
DEV_PORT = 27017
DEV_NAME = 'company'
DEV_DOCNAME = ''

# 生产环境配置
PROD_HOST = '39.101.132.159'
PROD_PORT = 27019
PROD_NAME = 't_s_gm'
PROD_DOCNAME = ''

USERNAME = 'jiran'
PASSWORD = 'nar.ij#*@6541'
AUTH_DB = 't_s_gm'

DEV_CONFIG = {
    'host': DEV_HOST,
    'port': DEV_PORT,
}

PROD_CONFIG = {
    'host':PROD_HOST,
    'port':PROD_PORT,
    'username':USERNAME,
    'password' :PASSWORD,
    'authMechanism' : 'SCRAM-SHA-1',
    'authSource' : AUTH_DB
}
client = pymongo.MongoClient(**DEV_CONFIG)
db =client[DEV_NAME]
# client = pymongo.MongoClient(**PROD_CONFIG)
# db =client[PROD_NAME]