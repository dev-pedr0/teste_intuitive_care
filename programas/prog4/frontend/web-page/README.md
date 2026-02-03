# Instruções
Este exercício consiste em uma aplicação web.
No diretório raiz, execute o comando npm run dev.
O sistema irá iniciar o frontend e o backend em conjunto.
É necessário que exista um banco de dados disponível.
É necessário executar a primeira opção de código da Atividade 3 para gerar as tabelas.
É necessário atualizar a função auxiliar conectar_banco() nos arquivos support_code.py e db.py.
É necessário configurar o CORS no arquivo app.py, principalmente o parâmetro allow_origins.

## prog4
Nesta etapa, foi construída uma API em FastAPI e uma interface web para apresentar os dados do banco de dados criado no exercício anterior. Dentro da pasta prog4 também um json POSTMAN com testes da API

### Backend
No arquivo app.py estão as configurações da API, middlewares para validação e também para evitar erros de permissão. Além disso, estão definidas as seguintes rotas:
- /api/operadoras: lista de operadoras,
- /api/operadoras/{cnpj}: dados de uma operadora específica,
- /api/operadoras/{cnpj}/despesas: lista de despesas de uma operadora específica,
- /api/estatisticas: estatísticas gerais baseadas nas queries do exercício anterior,
A primeira rota possui sistema de filtro e paginação. O filtro é feito por meio de CNPJs e razões sociais, enquanto a paginação utiliza a estratégia de offset para gerar páginas com listas de até 10 operadoras. Uma query obtém o total de registros para controle da paginação, e outra busca as operadoras e seus respectivos dados para envio ao frontend.
A segunda rota recebe um CNPJ específico e retorna suas informações. Inicialmente, são buscados os dados na tabela registro_operadora. Em seguida, é feita a relação do CNPJ com sua primeira aparição na tabela despesas_operadoras, a fim de identificar a razão social correspondente. Com a razão social identificada, os dados agregados mais recentes são buscados na tabela despesas_agregadas.
A terceira rota recebe um CNPJ e retorna todas as despesas registradas para essa operadora na tabela despesas_operadoras.
A quarta rota executa uma série de queries para obter os dados que alimentam os gráficos da interface web. Essa rota retorna:
- As cinco operadoras com maior crescimento percentual de despesas, considerando apenas dados completos.
- Despesas agregadas por estado.
- Operadoras cujo gasto ultrapassou sua média trimestral.
Trade-off técnico:
Framework: o framework escolhido foi o FastAPI, devido ao suporte nativo a APIs REST e à validação automática de dados. Apesar da complexidade inicial, ele permitiu a criação de um código mais enxuto e organizado.
Estratégia de paginação: foi utilizada a estratégia offset-based. Para o volume de dados deste projeto, o uso de offset não causa prejuízo significativo de desempenho, mas essa decisão deve ser reavaliada em caso de crescimento do volume de dados. A estratégia também contribui para uma visualização mais limpa, limitando a quantidade de itens exibidos por página.
Cache vs. queries diretas: como a rota de estatísticas executa diversas queries que percorrem todas as tabelas criadas, optou-se pelo uso de cache temporário. Embora o volume de dados permita cálculos em tempo real, a existência do cache reduz ainda mais o risco de sobrecarga no processamento. Além disso, o FastAPI possui mecanismos de cache de fácil implementação.
Estrutura de resposta da API: a paginação retorna tanto os dados quanto metadados. O uso de metadados facilita a implementação da paginação no frontend e evita chamadas adicionais à API, ao custo de um pequeno aumento no volume de informações transmitidas. Esse acréscimo não impacta negativamente a comunicação entre frontend e backend e, portanto, foi considerado vantajoso.

### Frontend
A aplicação web foi desenvolvida em Vue, com uma interface simples e funcional para apresentação dos dados conforme solicitado.
Foi utilizado o Vue Router para navegação entre páginas. As telas da interface incluem:
- Tela de listagem de operadoras
- Tela de detalhes da operadora
- Tela de despesas da operadora
- Tela de estatísticas
Toda a estilização foi realizada por meio do arquivo styles.css, localizado na pasta assets.
A página Companies lista as operadoras utilizando o componente CompaniesList. Esse componente é responsável por realizar a chamada à API e controlar a paginação. Além disso, ele possui dois botões que direcionam o usuário para as páginas de detalhes ou despesas da operadora selecionada. Cada botão recebe o CNPJ da operadora e o transmite como parâmetro de rota, que é utilizado pelas demais páginas para realizar suas respectivas chamadas à API.
A página Statistics utiliza a biblioteca Chart.js e o componente StatsChart para gerar gráficos com base nos dados retornados pela rota de estatísticas da API. O componente configura os gráficos e aplica ajustes gerais e específicos para cada visualização. A página realiza a chamada à API, separa os dados por tipo de gráfico e instancia um componente para cada conjunto de informações.
As páginas Details e Costs funcionam de forma semelhante, recebendo o CNPJ como parâmetro de rota e realizando a chamada correspondente à API. Os dados retornados são então exibidos de forma organizada e estilizada.
Trade-off técnico:
Estratégia de busca e filtro: considerando o volume de dados e para evitar sobrecarga de processamento no cliente, optou-se por realizar buscas e filtros no servidor. Essa abordagem aproveita melhor a eficiência do banco de dados para filtrar e paginar os registros, enviando ao frontend apenas os dados necessários.
Gerenciamento de estado: como as páginas não precisam exibir dados simultaneamente, funcionam de forma independente e não há restrições quanto ao uso do CNPJ (dado público), optou-se por uma abordagem simples utilizando props e parâmetros de rota. Essa estratégia atendeu à necessidade do projeto de forma clara e direta.
Performance da tabela: foi adotada a paginação no backend, enviando ao frontend apenas 10 operadoras por requisição. Essa abordagem evita telas excessivamente longas, melhora a usabilidade e facilita a navegação e a busca visual pelos dados.
Tratamento de erros e loading: o tratamento de erros e estados de carregamento é realizado de forma consistente em todas as telas da aplicação. Erros de rede ou da API são capturados por blocos try/catch, exibindo mensagens específicas quando fornecidas pelo backend ou mensagens genéricas como fallback. Estados de loading são controlados por flags explícitas ou verificações condicionais, garantindo feedback visual ao usuário. Para casos de dados vazios, optou-se por mensagens simples em telas de listagem, enquanto telas de detalhe apresentam mensagens mais específicas.