from dotenv import load_dotenv
from Controle.classConexao import Conexao
from Controle.func import verificaSenha
load_dotenv()
import os
from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
from psycopg2 import Error
from bcrypt import hashpw, gensalt, checkpw
from datetime import timedelta
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, decode_token

try:
  con = Conexao(host=os.getenv("HOST"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), port=os.getenv("PORT"), database=os.getenv("DATABASE"))   
      
  app = Flask(__name__)
  app.config['JWT_SECRET_KEY'] = os.getenv("KEY")
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=5)  
  
  jwt = JWTManager(app)
  
  CORS(app)
  print("Conectado")
  mail = Mail(app)
  
  app.config['MAIL_SERVER'] = 'smtp.office365.com'
  app.config['MAIL_PORT'] = 587
  app.config['MAIL_USERNAME'] = os.getenv("MAIL")
  app.config['MAIL_PASSWORD'] = os.getenv("PWD_MAIL")
  app.config['MAIL_USE_TLS'] = True
  app.config['MAIL_USE_SSL'] = False
  
  mail.init_app(app)
  
  apiUrl = 'https://api-rec.vercel.app/'
  recUrl = 'https://rec-eight.vercel.app'
    
  @app.route("/")
  def home():
      return "API ainda não explodiu"
  
  @jwt.expired_token_loader
  def my_expired_token_callback(jwt_header, jwt_payload): 
    return redirect(f'{recUrl}/token-expired')

  @app.route("/usuarios", methods =['POST'])    
  def checarUsuarios():
    email = request.json['email']
    senha = request.json['senha'].encode('utf-8')      
    sql = f"SELECT * FROM usuarios WHERE email = '{email}'"
    resposta = con.querySelectOne(sql)                 
    if(resposta is None):
      return jsonify({'status' : 'fail'})
    else:      
      if checkpw(senha, resposta[3].encode('utf-8')):          
        access_token = create_access_token(identity=resposta[0])       
        return jsonify({'status' : 'sucess', 'id': f'{resposta[0]}', 'nome' : f'{resposta[1]}', 'access_token': f'{access_token}'})        
      else:
        return jsonify({'status' : 'fail'})
  
  @app.route('/atualizarUsuario', methods=['POST'])
  @jwt_required()
  def atualizar_user():        
      nome = request.json['nome']
      email = request.json['email']
      senha = request.json['senha']
      id_usuario = get_jwt_identity()
      if verificaSenha(senha):
        senha = senha.encode('utf-8')
        salt = gensalt()
        senha = hashpw(senha, salt).decode('utf-8')
        sql = f"UPDATE usuarios SET nome=%s, email =%s, senha=%s WHERE id = %s"
        values = (nome, email, senha, id_usuario)
        con.queryExecute(sql, values)        
        return jsonify({'status': 'success'})
      else:
        return jsonify({'status': 'senhaFraca'})
  
  @app.route("/inserirUsuario", methods =['POST'])    
  def inserirUsuario():
    nome = request.json['nome']
    email = request.json['email']
    senha = request.json['senha']           
    sql = f"SELECT nome FROM usuarios WHERE email = '{email}';"
    resposta = con.querySelectOne(sql)                 
    if resposta is None:
      if verificaSenha(senha):
        senha = senha.encode('utf-8')
        salt = gensalt()
        senha = hashpw(senha, salt).decode('utf-8')
        return redirect(url_for('enviarEmail', email=email, nome=nome, senha=senha))        
      else:
        return jsonify({'status': 'senhaFraca'})
    else:  
      return jsonify({'status': 'fail'})
  
  @app.route("/deletarUsuario", methods = ['POST'])
  @jwt_required()
  def deletarUsuario():
    id_usuario = get_jwt_identity()
    sql = f'''DELETE FROM filmes WHERE id_usuario = '{id_usuario}';
    DELETE FROM series WHERE id_usuario = '{id_usuario}';
    DELETE FROM listadesejo WHERE id_usuario = '{id_usuario}';
    DELETE FROM usuarios WHERE id = '{id_usuario}';'''
    con.queryExecute(sql, values=None)      
    return jsonify({'status' : 'sucess'})
  
  @app.route("/filmes", methods =['GET' ,'POST'])
  @jwt_required()
  def consultarFilmes():      
    if(request.method == 'GET'):
      id = get_jwt_identity()
      sql = f"SELECT * FROM filmes WHERE id_usuario = '{id}'"
      results = con.querySelect(sql)               
      return results
    elif(request.method == 'POST'):
      titulo = request.json['titulo']
      id_usuario = get_jwt_identity()
      sql = f"SELECT * FROM filmes WHERE titulo = '{titulo}' AND id_usuario = '{id_usuario}'"
      resposta = con.querySelectOne(sql)        
      if(resposta is None):
        return jsonify({'status' : 'fail'})
      else:
        return jsonify({'status' : 'sucess'})
  
  @app.route("/inserirFilme", methods =['POST'])
  @jwt_required()
  def inserirFilme():
    titulo = request.json['titulo']
    imagem = request.json['imagem']
    nota = request.json['nota']
    tipo = request.json['tipo']
    id_api = request.json['id_api']
    id_usuario = get_jwt_identity()
    sql = f"INSERT INTO filmes (titulo, imagem, nota, tipo, id_api, id_usuario) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM filmes WHERE titulo = %s AND id_usuario = %s)"
    values = (titulo, imagem, nota, tipo, id_api, id_usuario, titulo, id_usuario)
    con.queryExecute(sql, values)           
    return jsonify({'status': 'sucess'})
  
  @app.route("/removerFilme", methods = ['POST'])
  @jwt_required()
  def removerFilme():
    titulo = request.json['titulo']
    id_usuario = get_jwt_identity()
    sql = f"DELETE FROM filmes WHERE id_usuario = '{id_usuario}' AND titulo = '{titulo}'"
    con.queryExecute(sql, values=None)          
    return jsonify({'status' : 'sucess'})
  
  @app.route("/series", methods =['GET', 'POST'])
  @jwt_required()
  def consultarSeries():      
    if(request.method == 'GET'):
      id = get_jwt_identity()
      sql = f"SELECT * FROM series WHERE id_usuario = '{id}'"        
      results = con.querySelect(sql)
      return results
    elif(request.method == 'POST'):
      titulo = request.json['titulo']
      id_usuario = get_jwt_identity()
      sql = f"SELECT * FROM series WHERE titulo = '{titulo}' AND id_usuario = '{id_usuario}'"        
      resposta = con.querySelectOne(sql)
      if(resposta is None):
        return jsonify({'status' : 'fail'})
      else:
        return jsonify({'status' : 'sucess'})
  
  @app.route("/inserirSerie", methods =['POST'])
  @jwt_required()
  def inserirSerie():
    titulo = request.json['titulo']
    imagem = request.json['imagem']
    nota = request.json['nota']
    tipo = request.json['tipo']
    id_api = request.json['id_api']
    id_usuario = get_jwt_identity()      
    sql = f"INSERT INTO series (titulo, imagem, nota, tipo, id_api, id_usuario) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM series WHERE titulo = %s AND id_usuario = %s)"
    values = (titulo, imagem, nota, tipo, id_api, id_usuario, titulo, id_usuario)
    con.queryExecute(sql, values)           
    return jsonify({'status': 'sucess'})
  
  @app.route("/removerSerie", methods = ['POST'])
  @jwt_required()
  def removerSerie():
    titulo = request.json['titulo']
    id_usuario = get_jwt_identity()
    sql = f"DELETE FROM series WHERE id_usuario = '{id_usuario}' AND titulo = '{titulo}'"
    con.queryExecute(sql, values=None)      
    return jsonify({'status' : 'sucess'})
  
  @app.route("/listaDesejo", methods =['GET'])
  @jwt_required()
  def consultarListaDesejo():
    id = get_jwt_identity()
    sql = f"SELECT * FROM listadesejo WHERE id_usuario = '{id}'"
    results = con.querySelect(sql)      
    return results
  
  @app.route("/inserirListaDesejo", methods =['POST'])
  @jwt_required()
  def inserirListaDesejo():
    titulo = request.json['titulo']
    imagem = request.json['imagem']
    nota = request.json['nota']
    tipo = request.json['tipo']
    id_api = request.json['id_api']
    id_usuario = get_jwt_identity()
    sql = f"INSERT INTO listadesejo (titulo, imagem, nota, tipo, id_api, id_usuario) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM listadesejo WHERE titulo = %s AND id_usuario = %s)"
    values = (titulo, imagem, nota, tipo, id_api, id_usuario, titulo, id_usuario)
    con.queryExecute(sql, values)       
    return jsonify({'status': 'sucess'})
  
  @app.route("/removerListaDesejo", methods =['POST'])
  @jwt_required()
  def removerListaDesejo():
    titulo = request.json['titulo']
    id_usuario = get_jwt_identity()      
    sql = f"DELETE FROM listadesejo WHERE titulo = '{titulo}'  AND id_usuario = '{id_usuario}';"
    con.queryExecute(sql, values=None)        
    return jsonify({'status': 'sucess'})
    
  @app.route("/confirmarEmail/<token>", methods =['GET'])      
  def confirmarEmail(token):
    try:
        tokenConfirm = decode_token(token)
        email = tokenConfirm['sub']
        sql = f"SELECT * FROM verificacao WHERE email = '{email}' AND token = '{token}' AND isValid = 'false'"
        resposta = con.querySelectOne(sql)
        if(resposta is None):
            return jsonify({'status': 'fail'})
        else:            
            sql = f"UPDATE verificacao SET isValid=true WHERE token = %s"
            values = (token,)
            con.queryExecute(sql, values)
            sql = f'''INSERT INTO usuarios (nome, email, senha) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE email = %s);'''
            values = (resposta[1], resposta[2], resposta[3], resposta[2])
            con.queryExecute(sql, values)
            return redirect(f'{recUrl}/finalizado')
    except Exception as e:      
      return redirect(f'{recUrl}/token-expired')
  
  @app.route("/enviarEmail", methods =['GET'])
  def enviarEmail():
    email = request.args.get('email')
    nome = request.args.get('nome')
    senha = request.args.get('senha')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
    tokenEmail = create_access_token(identity=email)
    sql = f"INSERT INTO verificacao (nome, email, senha, token) VALUES (%s, %s, %s, %s);"
    values = (nome, email, senha, tokenEmail)
    con.queryExecute(sql, values)
    msg = Message('Confirmação de Cadastro', sender='project-rec@outlook.com', recipients=[f'{email}'])          
    url = f'{apiUrl}/confirmarEmail/{tokenEmail}'        
    img_url = 'https://lh3.googleusercontent.com/2CcVt2GM39JTHyH5i9os6JpHm8woe1MOB0TIDVTWhq4Pp1lJnomoIAR5hbG8z6cKgJI1Get64RWMCSe1X8XgCl6uocww-pTJgh1fQW5_5JJDqeIRhNJn6hnvVtTde0yvvoGD8LGZlBNli1Y6R0teEm-O1wmrintEn1_J80RqqfmabQsw8ummBc2dMptMuh0YxklGST5KvhjBxtBDjGcmW7uUHJnCfNe3Sny8ecZxVXVZbQ8Nifs5mc_1TizmxrvTGo1k_q8UJFBHYHcGJhUcEi4nlQZtnPbjp8vNWyw8g5ry2qmQfJTuuU2DSj4lRxjH7l57h2Tr_ocgifUjDiF6TJBY9lnwGwtGqxbn1bQrWUKuqJF3icAhgVq726WPNK-bJZenx5R1eBwcaoX46d2MYyW_-dHy7vsBv9xAFGvy3cOfFqDhKwlWfl4BdZpDGuysaeCgysBD7Lxi24YE0JAzX-Q2MGgMf0CSUkm__N3I4itHrQ7G90VVOaiFoGIMaNymTjoT3OefUQ49yg6wJaVb2_sXUzRVmAYjFlVsrs9kW5Qg9oHDfqJGcSP7VBlAwdmRuQh0WrQ8YZjn3iVn1cTZd1R0XrNWhKR8HCZzYStMqo8u55bAZmCzgf566h_5TiaiibSYYCK4m_O-mgwnEESxFsEqRxutqVoKDVqva1kqwrpu4Z8OvTNYjdk7ReI7AKO0qTekjFtBwoy8J7_TvE5UN1knSqtwKgzXpbtWumVGuXi2EadJPxfefAMSQfFpok9bJr6Qe8hAzR6-qIwJ48-txvxp2xxbVE0aBo0R7U0BeUPtT9i7kApoHZyOCC_38hx4yGf2xRtiUCXwrLJ9AVIIwGEE87llLiVkgqmYxVYTv0En0kPpEvBQBTeRk8yxhSKh0XQl9VU_mIchw8myQrmYFATM-fWotYLa5g621WnnZCuffJSRKIQm5IWzMwINq3_VaFKZHZ3n5VgD0iVAd0g=w180-h180-s-no?authuser=0'
    msg.html = f'''        
      <p>Clique no botão abaixo para confirmar seu cadastro:</p>
      <a href="{url}">
          <img src="{img_url}" alt="Confirmar Cadastro">
      </a>'''
    mail.send(msg)               
    return jsonify({'status': 'sucess'})
  
  @app.route('/recuperarSenha', methods =['POST'])
  def recuperarSenha():
    email = request.json['email']
    sql = f"SELECT * FROM usuarios WHERE email = '{email}'"
    resposta = con.querySelectOne(sql)
    if (resposta is None):
      return jsonify({'status' : 'fail'})
    else:
      app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
      tokenEmail = create_access_token(identity=email)
      msg = Message('Alteração de Senha', sender='project-rec@outlook.com', recipients=[f'{email}'])
      url = f'{apiUrl}/check-token/{tokenEmail}'
      msg.html = f'''        
      <p>Clique no botão abaixo para alterar sua senha:</p>
      <a href="{url}">
          <button>Alterar Senha</button>
      </a>'''
      mail.send(msg)
      return jsonify({'status' : 'sucess'})
  
  @app.route('/check-token/<token>', methods =['GET'])    
  def checkToken(token):
    try:
      decoded_token = decode_token(token)
      if decoded_token == 'access':
        return redirect(f'{recUrl}/alterar-senha/{token}')
      else:
        return redirect(f'{recUrl}/erro404')
    except Exception as e:      
      return redirect(f'{recUrl}/token-expired')  
  
  
  @app.route('/alterarSenha/<token>', methods =['POST'])  
  def alterarSenha(token):    
    try:      
      tokenConfirm = decode_token(token)    
      email = tokenConfirm['sub']
      senha = request.json['senha']
      if verificaSenha(senha):
        senha = senha.encode('utf-8')
        salt = gensalt()
        senha = hashpw(senha, salt).decode('utf-8')
        sql = f"UPDATE usuarios SET senha = %s WHERE email = %s"
        values = (senha, email)
        con.queryExecute(sql, values)
        return jsonify({'status' : 'sucess', 'msg' : 'Senha alterada com sucesso!'})
      else:
        return jsonify({'status' : 'senhaFraca'})
    except Exception as e:      
      return redirect(f'{recUrl}/token-expired')  

  if __name__ == '__main__':
    app.run(debug=True)

except(Error) as error:
  print(error)
