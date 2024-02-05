from flask import Flask, redirect, render_template, request, url_for,flash,session
from hashlib import scrypt
import warnings
from flask import Flask, redirect, render_template, request, url_for
import mysql.connector
cnx = mysql.connector.connect(
  host='127.0.0.1',
  user='root',
  password=''
)

# Executar a instrução SQL para verificar se o banco de dados existe
cursor = cnx.cursor()
cursor.execute('SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "notas";')

# Obter o número de resultados
num_results = cursor.fetchone()[0]

# Fechar a conexão com o banco de dados
cnx.close()

# Se o número de resultados for maior que zero, o banco de dados existe
if num_results > 0:
  print('O banco de dados notas existe e esta pronto para uso.')
else:
    # Conectar-se ao servidor MySQL para criar o banco de dados
    cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password=''
    )

    cursor = cnx.cursor()
    cursor.execute('CREATE DATABASE notas;')
    cnx.commit()

    cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='notas'  
    )

    # Criar a tabela aluno
    cursor = cnx.cursor()
    cursor.execute('CREATE TABLE aluno (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), email VARCHAR(255),senha VARCHAR(255));')
    cursor.execute("""
      CREATE TABLE informacoes (id INT AUTO_INCREMENT PRIMARY KEY,
      professor varchar(20),
      aluno_id int
      turma_id int,
      materias_id int,
      
    )
  """)
    
    cursor.execute('ALTER TABLE aluno ADD CONSTRAINT fk_aluno_turma FOREIGN KEY (turma_id) REFERENCES turma (id),ADD CONSTRAINT fk_aluno_materias FOREIGN KEY (materias_id) REFERENCES materias (id))')
    cnx.close()
    
 
 
app = Flask(__name__)

@app.route('/login',methods=['POST','GET'])
def pagina_login():
     return render_template("login.html")

@app.route('/')
def pagina_inicial():
     return render_template("paginainicial.html")
   
      
@app.route('/informacoes')
def pagina_informacoes():
  cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='notas'  # Especificar o banco de dados
    )
  cursor = cnx.cursor()
  cursor.execute('SELECT * FROM informacoes')
  informacoes = cursor.fetchall()

  return render_template("informacoes.html", informacoes=informacoes)
@app.route('/aluno')
def pagina_aluno():
  cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='notas'  
    )

  cursor = cnx.cursor()
  cursor.execute('SELECT * FROM aluno')
  alunos = cursor.fetchall()

  return render_template("aluno.html", alunos=alunos)

@app.route('/cadastro', methods=["POST","GET"])
def pagina_cadastro():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    if request.method != 'POST':
        return render_template('cadastro.html', error='Método HTTP inválido.')
    if not nome:
        return render_template('cadastro.html', error='O nome é obrigatório.')
    if not email:
        return render_template('cadastro.html', error='O e-mail é obrigatório.')
    if not senha:
        return render_template('cadastro.html', error='A senha é obrigatória.')
    if len(senha) < 8:
        return render_template('cadastro.html', error='A senha deve ter pelo menos 8 caracteres.')  
  

 
   
   
  
    cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='notas'
    )
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM aluno
        WHERE email = %s;
    """, (email,))
    existe = cursor.fetchone()[0]
    cursor.close()
    cnx.close()

    if existe > 0:
        return render_template('cadastro.html', error='O usuário já existe.')
    else:
      try:
          cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='notas'
          )
          cursor = cnx.cursor()
          

          sql = 'INSERT INTO aluno (nome, email, senha) VALUES (%s, %s, %s)'
          values = (nome, email, senha)

          cursor.execute(sql, list(values))
          cursor.close()
          cnx.commit()

          return redirect(url_for('pagina_inicial'))
      
      except mysql.connector.Error as e:
        return render_template('cadastro.html', error=str(e))  
    
    # Salvando os dados
@app.route('/excluir_aluno/<id>', methods=['GET', 'POST'])
def excluir_aluno(id):
    # Validar o ID
    if not id.isdigit():
        return render_template('excluir-aluno.html', error='ID inválido')
    # Executando a exclusão
    try:
        cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='notas'
        )
        cursor = cnx.cursor()
        cursor.execute("""
            DELETE FROM aluno
            WHERE id = %s;
        """, (id,))
        cursor.close()
        cnx.commit()

        return redirect(url_for('pagina_aluno'))
    except mysql.connector.Error as e:
        return render_template('excluir-aluno.html', error=str(e))

@app.route('/editaraluno/<id>', methods=['GET', 'POST'])
def atualizaraluno(id):

    # Valida o ID do usuário
    if not id.isdigit():
        return render_template('editaraluno/<id>', error='ID inválido.')

    # Obtém os dados do usuário do banco de dados
    cnx = mysql.connector.connect( host='127.0.0.1',
            user='root',
            password='',
            database='notas')
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT id, nome, email
        FROM aluno
        WHERE id = %s;
    """, (id,))
    dados_aluno = cursor.fetchone()
    cursor.close()
    cnx.close()

    # Processa o formulário
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        # Valida o input
        if not nome:
            flash('O nome é obrigatório.')
            return render_template('aluno/<id>', dados_aluno=dados_aluno)
        if not email:
            flash('O e-mail é obrigatório.')
            return render_template('editaraluno/<id>', dados_aluno=dados_aluno)
        if not senha:
            flash('A senha é obrigatória.')
            return render_template('editaraluno/<id>', dados_aluno=dados_aluno)
       

        # Realiza a atualização no banco de dados
        cnx = mysql.connector.connect( host='127.0.0.1',
            user='root',
            password='',
            database='notas')
        cursor = cnx.cursor()
        sql = 'UPDATE aluno SET nome = %s, email = %s, senha= %s WHERE id = %s;'
        values = (nome, email, senha, id)
        cursor.execute(sql, values)
        cnx.commit()
        cursor.close()
        cnx.close()

        # Redireciona para a página inicial
        return redirect(url_for('pagina_inicial'))

    # Exibe o formulário
    return render_template('editaraluno.html', id=id, dados_aluno=dados_aluno)

@app.route('/atualizareditaraluno', methods=['POST','GET'])
def atualizareditaraluno(id):

    # Valida os dados do usuário.
    if not id.isdigit():
        return render_template('/editaraluno/<id>', error='ID inválido.')

    # Obtém os valores dos campos "nome", "email" e "senha" do formulário submetido via POST.
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    # Valida os campos obrigatórios.
    if not nome:
        return render_template('editaraluno.html', error='O nome é obrigatório.')
    if not email:
        return render_template('editaraluno.html', error='O e-mail é obrigatório.')
    if not senha:
        return render_template('editaraluno.html', error='A senha é obrigatória.')

    # Abre uma conexão com o banco de dados MySQL usando as credenciais especificadas.

    try:
        # Reabre a conexão com o banco.
        cnx = mysql.connector.connect(host='127.0.0.1',
    user='root',
    password='',
    database='notas')
        cursor = cnx.cursor()

        # Prepara a consulta SQL de atualização.
        sql = 'UPDATE aluno ' \
              'SET nome = %s, ' \
              'email = %s, ' \
              'senha = %s ' \
              'WHERE id = %s;'
        values = (nome, email, senha, id)

        # Executa a consulta com os valores obtidos do formulário.
        cursor.execute(sql, values)

        # Fecha o cursor e confirma a transação (commit).
        cursor.close()
        cnx.commit()

        # Redireciona para a página inicial.
        return redirect(url_for('pagina_inicial'))

    except mysql.connector.Error as e:
        return render_template('/editaraluno/<id>',id, error=str(e))




@app.route('/validalogin', methods=['POST', 'GET'])
def login():
  
  email = request.form.get('nome')
  senha = request.form.get('senha')

  # Validar as credenciais
  cnx = mysql.connector.connect(
     host='127.0.0.1',
     user='root',
     password='',
     database='notas'
     )
  cursor = cnx.cursor()
  cursor.execute("""
            SELECT *
            FROM aluno
            WHERE email = %s AND senha = %s;
        """, (email, senha,))
  aluno = cursor.fetchone()
  cursor.close()
  cnx.close()

  if aluno:
  # Login bem-sucedido
   session['aluno_id'] = aluno[0]
   session['senha']=aluno[3]
   if aluno[3] == "senha=%s":
        return redirect(url_for('pagina_inicial'))
   else:
        return redirect(url_for('pagina_inicial'))
   
  else:
    # Login inválido
    return redirect(url_for('pagina_login'))      
   
      
      
    

if __name__ == '__main__':
      app.run