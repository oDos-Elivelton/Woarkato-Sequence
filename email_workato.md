# Documentação dos Itens

## Funções

### criar_sessao()

- **Descrição**: Cria uma sessão HTTP configurada com um mecanismo de retry para lidar com falhas temporárias em requisições.
- **Utilidade**: Garante maior resiliência em requisições HTTP, permitindo tentativas automáticas em caso de erros como timeouts ou falhas de conexão.

### fazer_requisicao(url, json, headers)

- **Descrição**: Realiza uma requisição HTTP POST com tratamento de erros.
- **Utilidade**: Simplifica o envio de requisições HTTP, lidando automaticamente com exceções e retornando a resposta ou mensagens de erro.

### alterar_campo_card(card_id, field_id, novo_valor)

- **Descrição**: Atualiza um campo específico de um card no Pipefy.
- **Utilidade**: Automatiza a atualização de informações em cards do Pipefy, como status ou detalhes de um processo.

### buscar_email(nome_da_empresa)

- **Descrição**: Busca os e-mails associados a uma empresa específica no Pipefy.
- **Utilidade**: Facilita a recuperação de contatos de empresas cadastradas no Pipefy para envio de comunicações.

### baixar_arquivo(url)

- **Descrição**: Faz o download do conteúdo de um arquivo a partir de uma URL.
- **Utilidade**: Permite obter arquivos externos para processamento ou envio.

### processar_anexos(file_urls)

- **Descrição**: Processa uma lista de URLs de arquivos, codificando-os em base64 e organizando-os em um dicionário.
- **Utilidade**: Prepara anexos para envio em e-mails, garantindo compatibilidade com formatos esperados.

### gerar_links_anexos(urls)

- **Descrição**: Gera um HTML contendo links clicáveis para os arquivos anexados.
- **Utilidade**: Cria uma interface amigável para acessar anexos diretamente no corpo do e-mail.

### montar_email_html(tipo_solicitacao, corpo_email, email_reply)

- **Descrição**: Monta o HTML do corpo do e-mail com base nos dados fornecidos.
- **Utilidade**: Gera um e-mail formatado e estilizado para envio.

### definir_destinatarios(departamento, emails)

- **Descrição**: Define os destinatários e o e-mail de resposta com base no departamento informado.
- **Utilidade**: Automatiza a seleção de destinatários e remetentes para diferentes departamentos.

### main(input)

- **Descrição**: Função principal que processa dados, envia e-mail e atualiza informações no Pipefy.
- **Utilidade**: Centraliza o fluxo de envio de e-mails e atualização de registros, integrando diferentes funcionalidades.

## Variáveis de Entrada

### card_id

- **Descrição**: Identificador único de um card no Pipefy.
- **Utilidade**: Usado para localizar e atualizar informações específicas de um card.

### field_id

- **Descrição**: Identificador único de um campo em um card no Pipefy.
- **Utilidade**: Necessário para alterar valores de campos específicos.

### nome_da_empresa

- **Descrição**: Nome da empresa para a qual os e-mails serão buscados.
- **Utilidade**: Filtra registros no Pipefy para encontrar os contatos associados.

### departamento

- **Descrição**: Nome do departamento responsável pela solicitação.
- **Utilidade**: Define os destinatários e o e-mail de resposta com base no setor.

### tipo_de_solicitacao

- **Descrição**: Tipo de solicitação ou processo que está sendo concluído.
- **Utilidade**: Personaliza o conteúdo do e-mail enviado.

### assunto

- **Descrição**: Assunto do e-mail.
- **Utilidade**: Define o título do e-mail enviado.

### corpo_do_email

- **Descrição**: Texto principal do corpo do e-mail.
- **Utilidade**: Contém as informações que serão comunicadas no e-mail.

### anexos

- **Descrição**: URLs dos arquivos que serão anexados ao e-mail.
- **Utilidade**: Permite o envio de documentos ou outros arquivos junto ao e-mail.

### novo_valor

- **Descrição**: Novo valor a ser definido em um campo do card no Pipefy.
- **Utilidade**: Atualiza informações no Pipefy após o envio do e-mail, indicando se foi sucesso ou não.
