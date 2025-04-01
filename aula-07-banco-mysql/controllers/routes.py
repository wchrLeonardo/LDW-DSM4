import urllib.request
from flask import render_template, request, redirect, url_for, flash, session
#importando Model
from models.database import db, Game, Usuario
#essa bibilioteca serve para ler determinada URL
import urllib
#Converte dados para o formato JSON
import json
#Importando biblioteca para Hash de Senha
from werkzeug.security import generate_password_hash, check_password_hash
#Biblioteca para EDITAR a flash message
from markupsafe import Markup #Inclui HTML dentro das Flash Messages



jogadores = []
gamelist = [{'titulo': 'CS-GO',
        'ano': 2012,
        'categoria': 'FPS Online'}]


def init_app(app):
    #Função de middleware para verificar a autenticação do usuário
    @app.before_request
    def check_auth():
        #Rotas que não precisam de autenticação
        routes = ['login', 'caduser', 'home']
        
        #Se a rota atual não requer autenticação, permite o acesso
        if request.endpoint in routes and request.path.startswith('/static/'):
            return
        #Se o usuário não estiver autenticado, redireciona para página de login
        if 'user_id' not in session:
            return redirect(url_for('login'))

    @app.route('/')
    # view function - função de visualização
    def home():
        return render_template('index.html')

    @app.route('/games', methods=['GET', 'POST'])
    def games():
        game = gamelist[0]

        if request.method == 'POST':
            if request.form.get('jogador'):
                jogadores.append(request.form.get('jogador'))
                return redirect(url_for('games'))

        return render_template('games.html',
                               game=game,
                               jogadores=jogadores)

    @app.route('/cadgames', methods=['GET', 'POST'])
    def cadgames():
        if request.method == 'POST':
            form_data = request.form.to_dict()
            gamelist.append(form_data)
            return (redirect(url_for('cadgames'))) 
        return render_template('cadgames.html', 
                               gamelist=gamelist)
    
    @app.route('/apigames', methods=['GET','POST'])
    # Passando parâmetros para rota
    #id numero inteiro, informamos o tipo como <int:id>, se fosse string não porecisaria do tipo
    @app.route('/apigames/<int:id>', methods=['GET', 'POST'])
    #Definindo que o parâmetro é opcional
    def apigames(id=None):
        url = 'https://www.freetogame.com/api/games'
        res = urllib.request.urlopen(url)
        # print(res)
        data = res.read()
        gamesjson = json.loads(data)
        
        if id:
            ginfo = []
            for g in gamesjson:
                if g['id'] == id:
                    ginfo = g
                    break
            if ginfo:
                return render_template('gameinfo.html', ginfo=ginfo)
            else:
                return f'Gmae com a ID {id} não encontrado.'
        return render_template('apigames.html', 
                               gamesjson=gamesjson)
    
    
    #Rota com CRUD de Jogos
    @app.route('/estoque', methods=['GET', 'POST'])
    @app.route('/estoque/delete/<int:id>')
    def estoque(id=None):
        if id:
            #Get para pegar o jogo no banco para ser excluido
            game = Game.query.get(id)
            #Delete no game
            db.session.delete(game)
            db.session.commit()
            return redirect(url_for('estoque'))
            
        if request.method == 'POST':
            newgame = Game(request.form['titulo'],request.form['ano'],request.form['categoria'],request.form['plataforma'],request.form['preco'],request.form['quantidade'])
            #Envia os valores para o banco
            db.session.add(newgame)
            db.session.commit()
            return redirect(url_for('estoque')) 
        else:
            #Paginação
            #A variável abaaixo captura o valor de 'page' que foi passado pelo método GET.
            #E define como padrão o valor 1 e o tipo inteiro
            page = request.args.get('page', 1, type=int)
            #Valor padrão de registros por página (definimos 5)
            per_page = 5
            #abaixo está sendo feito um select no banco a partir da página informada (page) e filtrando
            #os registros de 5 em 5 
            games_page = Game.query.paginate(page=page, per_page=per_page) 
            return render_template('estoque.html', gamesestoque=games_page)             
            #Método que faz select geral no banco na tabela Games
            # gamesestoque = Game.query.all()
            # return render_template('estoque.html', gamesestoque=gamesestoque)

    #Rota Edição
    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit(id):
        #Buscando informações do jogo:
        game = Game.query.get(id)
        #EDITA JOOG DE ACORDO COM FORMULARIO
        if request.method == 'POST':
            game.titulo = request.form['titulo']
            game.ano = request.form['ano']
            game.categoria = request.form['categoria']
            game.plataforma = request.form['plataforma']
            game.preco = request.form['preco']
            game.quantidade = request.form['quantidade']
            db.session.commit()
            return redirect(url_for('estoque'))
        return render_template('editgame.html', game=game)
    
    #ROTA DE LOGIN
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            #Aqui você deveria fazer a validação do login
            email = request.form['email']
            password = request.form['password']
            #Verificando se o usuário existe
            user = Usuario.query.filter_by(email=email).first()
            #Se o usuário não existe, retorna uma flash message
            if not user or not check_password_hash(user.password, password):
                msg = Markup("Usuário ou senha inválidos. Tente novamente!")
                flash(msg, 'danger')
                return redirect(url_for('login'))
            #Caso o usuário exista
            session['user_id'] = user.id  # Armazenando o ID do usuário na sessão
            session['email'] = email
            nickname = user.email.split('@')
            flash(f'Login efetuado com sucesso! Bem vindo {nickname[0]}', 'success')  # Mostrando uma flash message de sucesso
            #Redirecionando para a página inicial
            return redirect(url_for('home'))
        return render_template('login.html')
    
    
    #ROTA DE LOGOUT
    @app.route('/logout')
    def logout():
        session.clear()  # Limpando a sessão
        flash('Logout efetuado com sucesso!', 'info')  # Mostrando uma flash message de logout
        return redirect(url_for('home'))
    
    #ROTA DE REGISTRO
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            #Aqui você deveria fazer a validação do registro
            #Capturando os dados
            email = request.form['email']
            password = request.form['password']
            #Verificando se o usuário existe
            user = Usuario.query.filter_by(email=email).first()
            #Se o usuário já existe, retorna uma flash message
            if user:
                msg = Markup("O usuário já cadastrado. Faça <a href='/login'></a>")
                flash(msg, 'danger')
                return redirect(url_for('register'))
            #Caso o usuário não exista
            else:
                #Gerando hash da senha
                hashed_password = generate_password_hash(password, method='script')
                new_user = Usuario(email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                #Mensagem de sucesso após cadastro
                flash('Registro realizado, faça o login!', 'success')
                return redirect(url_for('login'))
        return render_template('register.html')
    