import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import abort,render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
  stats = {}
  stats = db.execute('''
   SELECT * FROM
      (SELECT COUNT(*) n_atletas FROM Atletas)
      JOIN
      (SELECT COUNT(*) n_modalidades FROM Modalidades)   
      JOIN
      (SELECT COUNT(*) n_categorias FROM Categorias) 
      JOIN 
      (SELECT COUNT(*) n_eventos FROM Eventos)       
      JOIN
      (SELECT COUNT(*) n_equipas FROM Equipas)
  ''').fetchone()
  logging.info(stats)
  return render_template('index.html',stats = stats)

#athletes 
@APP.route('/athletes/')
def list_athletes():
    athletes = db.execute(
      '''
    SELECT MAX(idAtletas) AS idAtletas, name
    FROM Atletas
    GROUP BY name
    ORDER BY name
      ''').fetchall()
    return render_template('athletes-list.html', athletes=athletes)
  
#athletes id  
@APP.route('/athletes/<int:id_atleta>/')
def get_athlete(id_atleta):
  athlete_data= db.execute(
      '''
      SELECT name, idAtletas, age, sex
      FROM Atletas
      WHERE idAtletas = :id
      ''', {'id': id_atleta}).fetchall()
  
  athlete_participations = db.execute(
    '''
    select a.name, e.city, e.season, e.year, c.event, medal
    from Eventos e join Participacoes p on e.idEventos = p.idEventos
    join Categorias c on p.idCategorias = c.idCategorias
    join Atletas a on p.idAtletas = a.idAtletas
    where a.name like (
    select name
    from Atletas
    where idAtletas = :id);
    ''', {'id': id_atleta}).fetchall()
  
  return render_template('athletes.html', 
           athlete_data = athlete_data, athlete_participations = athlete_participations)


#athletes search
@APP.route('/athletes/search/<expr>/')
def search_athletes(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  athletes = db.execute(
      ''' 
      SELECT DISTINCT name
      FROM Atletas
      WHERE name LIKE ?
      ''', [expr]).fetchall()
  return render_template('athletes-search.html',
           search=search,athletes=athletes)
  
#eventos
@APP.route('/games/')
def list_games():
    games = db.execute(
      '''
    SELECT idEventos, year, season
    FROM Eventos
    ORDER BY idEventos
      ''').fetchall()
    return render_template('games-list.html', games=games)
  
#games id  
@APP.route('/games/<int:id_evento>/')
def get_game(id_evento):
  evento_data= db.execute(
      '''
      SELECT idEventos, year, season, city
      FROM Eventos
      WHERE idEventos = :id
      ''', {'id': id_evento}).fetchall()

  stats_events_atletas = db.execute(
    '''
    select count(*) as n_atletas
    from Atletas a 
    where a.idAtletas in
    (
    select a.idAtletas
    from Atletas a join Equipas eq on (eq.idEquipas)
    join Participacoes p on (a.idAtletas = p.idAtletas)
    join Eventos e on (e.idEventos = p.idEventos)
    where e.idEventos = :id
    )
    ''', {'id': id_evento}).fetchall()
  return render_template('games.html', 
           evento_data = evento_data, stats_events_atletas = stats_events_atletas)