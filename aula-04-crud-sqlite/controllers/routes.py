import urllib.request
from flask import render_template, request, redirect, url_for
#importando Model
from models.database import db, Game
#essa bibilioteca serve para ler determinada URL
import urllib
#Converte dados para o formato JSON
import json

jogadores = []
gamelist = [{'titulo': 'CS-GO',
        'ano': 2012,
        'categoria': 'FPS Online'}]


def init_app(app):
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