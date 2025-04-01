import pymysql.cursors
from flask import Flask, render_template
from controllers import routes
#Importando o model
from models.database import db, Game
#Importando a biblioteca OS
import os
import pymysql

# criando a instancia do Flask na variável app
app = Flask(__name__, template_folder='views')  # representa o nome do arquivo
routes.init_app(app)

#Define o nome do banco
DB_NAME = 'thegames'
app.config['DATABASE_NAME'] = DB_NAME

#Passando o endereeço do banco ao SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root@localhost/{DB_NAME}'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'myssql://root:admin@localhost/{DB_NAME}'

#Secret para as flash messages
app.config['SECRET_KEY'] = 'thegamessecret'

#Define o tempo de duração da sessão
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# iniciando o servidor
if __name__ == '__main__':
    
    #Conectando ao MYSQL para criar o banco(se necessário)
    connection = pymysql.connect(
        host='localhost', user='root', password='',
        charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    
    try:
        with connection.cursor() as cursor:
            # Check if database exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            print('Banco criado')
    except Exception as e:
                # Create the database
            print(f'Erro ao criar banco {e}')        
    finally:
        connection.close()
        
        #Inicializa a aplicação flask e cria as tabelas do banco
        
    db.init_app(app=app)
    with app.test_request_context():
        db.create_all()
        
    app.run(host='localhost', port=5000, debug=True)
