from flask import Flask, render_template
from controllers import routes
#Importando o model
from models.database import db, Game
#Importando a biblioteca OS
import os

# criando a instancia do Flask na variável app
app = Flask(__name__, template_folder='views')  # representa o nome do arquivo
routes.init_app(app)

#Permite ler um diretório absoluto de um determinado diretório
dir = os.path.abspath(os.path.dirname(__file__))

# Passando o diretorio do banco ao SQlAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(dir, 'models/games.sqlite3')

# iniciando o servidor
if __name__ == '__main__':
    db.init_app(app=app)
    #Cria o banco de dados quando a aplicação é rodada (se não existir)
    with app.test_request_context():
        db.create_all()
    app.run(host='localhost', port=5000, debug=True)
