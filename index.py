from dotenv import load_dotenv
from Controle.classConexao import Conexao
from Controle.func import verificaSenha
load_dotenv()
import os
from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS, cross_origin
from psycopg2 import Error
from bcrypt import hashpw, gensalt, checkpw
from datetime import timedelta
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, decode_token, create_refresh_token

try:
  con = Conexao(host=os.getenv("HOST"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), port=os.getenv("PORT"), database=os.getenv("DATABASE"))   
      
  app = Flask(__name__)
  app.config['JWT_SECRET_KEY'] = os.getenv("KEY")
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=5)
  app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=5)
  
  
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
  
  apiUrl = 'https://api-rec.vercel.app'
  recUrl = 'https://rec-eight.vercel.app'
    
  @app.route("/")
  def home():
      return "API ainda não explodiu"
  
  @jwt.expired_token_loader
  @cross_origin()
  def my_expired_token_callback(jwt_header, jwt_payload): 
    return redirect(f'{recUrl}/token-expired')
  
  # @app.route('/refresh', methods=['POST'])
  # @jwt_required(refresh=True)
  # def refresh():
  #     current_user = get_jwt_identity()
  #     ret = {
  #         'access_token': create_access_token(identity=current_user)
  #     }
  #     return jsonify(ret)

  @app.route("/usuarios", methods =['POST'])    
  def checarUsuarios():
    try:
      email = request.json['email']
      senha = request.json['senha'].encode('utf-8')      
      sql = f"SELECT * FROM usuarios WHERE email = '{email}'"
      resposta = con.querySelectOne(sql)                 
      if(resposta is None):
        return jsonify({'status' : 'fail'})
      else:      
        if checkpw(senha, resposta[3].encode('utf-8')):          
          app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=5)
          access_token = create_access_token(identity=resposta[0])                       
          return jsonify({'status' : 'sucess', 'id': f'{resposta[0]}', 'nome' : f'{resposta[1]}', 'access_token': f'{access_token}'})        
        else:
          return jsonify({'status' : 'fail'})
    except Exception as e:
      return redirect(f'{recUrl}/error404')    
  
  @app.route('/atualizarUsuario', methods=['POST'])
  @jwt_required()
  def atualizar_user():
    try:        
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
    except Exception as e:
      return redirect(f'{recUrl}/error404')
    
  @app.route("/inserirUsuario", methods =['POST'])    
  def inserirUsuario():
    try:
      nome = request.json['nome']
      email = request.json['email']
      senha = request.json['senha']           
      sql = f"SELECT * FROM usuarios WHERE email = '{email}';"
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
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/deletarUsuario", methods = ['POST'])
  @jwt_required()
  def deletarUsuario():
    try:
      id_usuario = get_jwt_identity()
      sql = f'''DELETE FROM filmes WHERE id_usuario = '{id_usuario}';
      DELETE FROM series WHERE id_usuario = '{id_usuario}';
      DELETE FROM listadesejo WHERE id_usuario = '{id_usuario}';
      DELETE FROM usuarios WHERE id = '{id_usuario}';'''
      con.queryExecute(sql, values=None)      
      return jsonify({'status' : 'sucess'})
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/filmes", methods =['GET' ,'POST'])
  @jwt_required()
  def consultarFilmes():
    try:      
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
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/inserirFilme", methods =['POST'])
  @jwt_required()
  def inserirFilme():
    try:
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
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/removerFilme", methods = ['POST'])
  @jwt_required()
  def removerFilme():
    try:
      titulo = request.json['titulo']
      id_usuario = get_jwt_identity()
      sql = f"DELETE FROM filmes WHERE id_usuario = '{id_usuario}' AND titulo = '{titulo}'"
      con.queryExecute(sql, values=None)          
      return jsonify({'status' : 'sucess'})
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/series", methods =['GET', 'POST'])
  @jwt_required()
  def consultarSeries():
    try:      
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
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/inserirSerie", methods =['POST'])
  @jwt_required()
  def inserirSerie():
    try:
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
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/removerSerie", methods = ['POST'])
  @jwt_required()
  def removerSerie():
    try:
      titulo = request.json['titulo']
      id_usuario = get_jwt_identity()
      sql = f"DELETE FROM series WHERE id_usuario = '{id_usuario}' AND titulo = '{titulo}'"
      con.queryExecute(sql, values=None)      
      return jsonify({'status' : 'sucess'})
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/listaDesejo", methods =['GET'])
  @jwt_required()
  def consultarListaDesejo():
    try:
      id = get_jwt_identity()
      sql = f"SELECT * FROM listadesejo WHERE id_usuario = '{id}'"
      results = con.querySelect(sql)      
      return results
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/inserirListaDesejo", methods =['POST'])
  @jwt_required()
  def inserirListaDesejo():
    try:
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
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route("/removerListaDesejo", methods =['POST'])
  @jwt_required()
  def removerListaDesejo():
    try:
      titulo = request.json['titulo']
      id_usuario = get_jwt_identity()      
      sql = f"DELETE FROM listadesejo WHERE titulo = '{titulo}'  AND id_usuario = '{id_usuario}';"
      con.queryExecute(sql, values=None)        
      return jsonify({'status': 'sucess'})
    except Exception as e:
      return redirect(f'{recUrl}/error404')
  
  @app.route('/check-email/<token>', methods =['GET'])    
  def checkEmail(token):
    try:
      decoded_token = decode_token(token)
      email = decoded_token['sub']
      if decoded_token['type'] == 'access':
        return redirect(url_for('confirmarEmail', email=email, token=token))
      else:
        return redirect(f'{recUrl}/erro404')
    except Exception as e:      
      return redirect(f'{recUrl}/mandou-errado')    
    
  @app.route("/confirmarEmail", methods =['GET'])      
  def confirmarEmail():    
    email = request.args.get('email')
    token = request.args.get('token')
    sql = f"SELECT * FROM verificacao WHERE email = '{email}' AND token = '{token}' AND isValid = 'false';"         
    resposta = con.querySelectOne(sql)
    tokenConfirm = decode_token(resposta[5])
    email = tokenConfirm['sub']      
    if(resposta is None):
      return redirect(f'{recUrl}/rota-none')
    else:            
      sql = f"UPDATE verificacao SET isValid=true WHERE token = %s"
      values = (token,)
      con.queryExecute(sql, values)
      sql = f'''INSERT INTO usuarios (nome, email, senha) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE email = %s);'''
      values = (resposta[1], resposta[2], resposta[3], resposta[2])
      con.queryExecute(sql, values)
      return redirect(f'{recUrl}/finalizado')
  
  @app.route("/enviarEmail", methods =['GET'])
  def enviarEmail():
    try:
      email = request.args.get('email')
      nome = request.args.get('nome')
      senha = request.args.get('senha')
      app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=3)
      tokenEmail = create_access_token(identity=email)
      sql = f"INSERT INTO verificacao (nome, email, senha, token) VALUES (%s, %s, %s, %s);"
      values = (nome, email, senha, tokenEmail)
      con.queryExecute(sql, values)
      msg = Message('Confirmação de Cadastro', sender='project-rec@outlook.com', recipients=[f'{email}'])          
      url = f'{apiUrl}/check-email/{tokenEmail}'     
      msg.html = f'''        
        <p>Confirme seu cadastro através do link abaixo:</p>
        <a href="{url}">
            {url}
        </a>'''
      mail.send(msg)               
      return jsonify({'status': 'sucess'})
    except Exception as e:
      return redirect(f'{recUrl}/error')
  
  @app.route('/recuperarSenha', methods =['POST'])
  def recuperarSenha():
    try:
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
        <p>Altere sua senha através do link abaixo:</p>
        <a href="{url}">
            {url}
        </a>'''
        mail.send(msg)
        return jsonify({'status' : 'sucess'})
    except Exception as e:
      return redirect(f'{recUrl}/error')  
  
  @app.route('/check-token/<token>', methods =['GET'])    
  def checkToken(token):
    try:
      decoded_token = decode_token(token)
      if decoded_token['type'] == 'access':
        return redirect(f'{recUrl}/novaSenha?q={token}')
      else:
        return redirect(f'{recUrl}/erro404')
    except Exception as e:      
      return redirect(f'{recUrl}/token-expired') 
  
  @app.route('/novaSenha/<token>', methods =['POST'])  
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
