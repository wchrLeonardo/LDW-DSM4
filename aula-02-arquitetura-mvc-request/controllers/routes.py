from flask import render_template, request, redirect, url_for

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
        return render_template('cadgames.html', gamelist=gamelist)
