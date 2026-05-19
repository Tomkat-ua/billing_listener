import os
from dotenv import load_dotenv
from infisical_sdk import InfisicalSDKClient

load_dotenv()
secret_env = os.getenv("ENV")

params={}

# 1. Ініціалізація клієнта
client = InfisicalSDKClient(host = os.getenv("INFISICAL_SITE_URL"))

# 2. Авторизація через Machine Identity
client.auth.universal_auth.login(
    client_id=os.getenv("INFISICAL_CLIENT_ID"),
    client_secret=os.getenv("INFISICAL_CLIENT_SECRET")
)

def get_secret_value(secret_name,env,path):
    secret = client.secrets.get_secret_by_name(
        secret_name=secret_name,
        project_id=os.getenv("INFISICAL_PROJECT_ID"),
        environment_slug=env,
        secret_path=path,
        expand_secret_references=True, # Optional
        view_secret_value=True, # Optional
        include_imports=True, # Optional
        version=None # Optional
    )
    return secret.secretValue

params = {
# MariaDB params
    'db_host'        : get_secret_value("DB_HOST", secret_env,"/database"),
    'db_port'        : int(get_secret_value("DB_PORT", secret_env,"/database")),
    'db_user'        : get_secret_value("DB_USER", secret_env,"/database"),
    'db_password'    : get_secret_value("DB_PASSWORD", secret_env,"/database"),
    'db_name'        : get_secret_value("DB_NAME", secret_env,"/database"),
# MONO params
    'bill_webhook_url'   : get_secret_value('BILL_WEBHOOK_URL',secret_env,"/bank"),
# sus params
    'debug_mode' : int(os.getenv('DEBUG_MODE',0)),
    'env' : os.getenv('ENV')
}

if params.get('debug_mode') == 1:
    for key,value in params.items():
        print(key,':',value)
