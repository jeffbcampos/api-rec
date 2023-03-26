# API REC

## Instrução de uso e instalação

Clone o repositório e no terminal execute pip install -r requirements.txt

Isso instalará todas as bibliotecas listadas no arquivo requirements.txt que serão necessários pra rodar o projeto.

## Uso

Esta API foi criada para ser usada com o site https://rec-eight.vercel.app/. Abaixo estão alguns exemplos de como usar a API:

## Rotas

- `POST /usuarios`: Autentica um usuário com base em seu e-mail e senha. Retorna um token de acesso JWT se a autenticação for bem-sucedida.

- `POST /atualizarUsuario`: Atualiza as informações de um usuário autenticado. Requer um token de acesso válido.

- `POST /atualizarSenha`: Atualiza a senha de um usuário autenticado. Requer um token de acesso válido.

- `POST /inserirUsuario`: Insere um novo usuário no sistema. Envia um e-mail de verificação para o endereço fornecido.

- `POST /deletarUsuario`: Deleta um usuário autenticado e todas as suas informações associadas. Requer um token de acesso válido.

- `GET /filmes`: Retorna uma lista de filmes associados ao usuário autenticado. Requer um token de acesso válido.

- `POST /filmes`: Verifica se um filme específico está associado ao usuário autenticado. Requer um token de acesso válido.

- `POST /inserirFilme`: Insere um novo filme associado ao usuário autenticado. Requer um token de acesso válido.

- `POST /removerFilme`: Remove um filme associado ao usuário autenticado. Requer um token de acesso válido.

- `GET /series`: Retorna uma lista de séries associadas ao usuário autenticado. Requer um token de acesso válido.

- `POST /series`: Verifica se uma série específica está associada ao usuário autenticado. Requer um token de acesso válido.

- `POST /inserirSerie`: Insere uma nova série associada ao usuário autenticado. Requer um token de acesso válido.

- `POST /removerSerie`: Remove uma série associada ao usuário autenticado. Requer um token de acesso válido.

- `GET /listaDesejo`: Retorna uma lista de desejos associada ao usuário autenticado. Requer um token de acesso válido.

- `POST /inserirListaDesejo`: Insere um novo item na lista de desejos do usuário autenticado. Requer um token de acesso válido.

- `POST /removerListaDesejo`: Remove um item da lista de desejos do usuário autenticado. Requer um token de acesso válido.

- `GET /confirmarEmail/<token>`: Confirma o cadastro de um novo usuário usando o token fornecido no e-mail de verificação.

- `GET /enviarEmail`: Envia um e-mail de verificação para o endereço fornecido durante o cadastro do usuário.

- `POST /recuperarSenha`: Envia um e-mail com instruções para redefinir a senha do usuário para o endereço fornecido.

- `GET /check-token/<token>`: Verifica se o token fornecido é válido para redefinir a senha do usuário.

- `POST /novaSenha/<token>`: Redefine a senha do usuário usando o token fornecido no e-mail enviado pelo endpoint `/recuperarSenha`.


## Autenticação

A autenticação é realizada usando tokens JWT. Os tokens expiram após 5 dias e podem ser atualizados usando o endpoint apropriado.
