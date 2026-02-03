# Instruções
Esse exercício é uma aplicação web. 
No diretório raiz digite o comando 'npm run dev'.
O sistema irá rodar o frontend e o backend em cojunto.
É necessário haver um banco de dados disponível.
É necessário rodar a primeira opção de código na atividade 3 para gerar as tabelas.
É necessário atualizar a função auxiliar conectar_banco() em support_code.py e em db.py.
É necessário atualizar o CORS em app.py principalmente "allow_origins"

## Prog 4
Essa etapa foi construida uma API em FastAPI e uma interface web para apresentar os dados do banco de dados criado no exer´cicio anterior.

### Backend
Em app.py estão a configuração da API, middlewares para validação e também para evitar erros de permissão. Além disso estão presentes as rotas:
- /api/operadoras: para lista de operadoras
- /api/operadoras/{cnpj}: para dados de uma operadora específica
- /api/operadoras/{cnpj}/despesas: para lista de despesas de uma operadora específica
- /api/estatisticas: para estatísticas gerais baseadas nas queries do exercício anterior
A primeira rota possui sistema de filtro e paginação. O filtro é feito através dos cnpj's e razões sociais enquanto a paginção utiliza off-set para gerar páginas com listas de até 10 operadoras. Um query lista o total de registros para a paginação e a próxima busca as operadoras e seus dados para serem enviadas ao frontend.
A segunda rota recebe um cnpj específico e retorna informações do mesmo. Primeiro são buscados dados na tabela "registro_operadora". Depois É feita relação do cnpj com sua primeira aparição na tabela "despesas_operadoras" para ser encontrada a razão social da mesma. Com a razão social os ultimos dados pendentes são buscados na tabela de "despesas_agregadas".
A terceira rota recebe um CNPJ e devolve todas as despesas registradas naquele CNPJ da tabela "despesas_operadoras".
A quarta rota faz uma séria de queries para buscar diferentes dados que popularam gráficos na interface web. A rota busca:
- 5 operadoras com maior crescimento percentual de despesas com dados completos e incompletos.
- Despesas por estado.
- Operadoras cusjo gasto ultrapassou sua média trimestral
Trade-off técnico:
Framework - o framework escolhi foi o FatsAPI pelo suporte nativo a APIs REST e validação automática de dados. Apesar de complexidade inicial ele permitiu gerar código um pouco menor e mais limpo.
Estratégia de Paginação - Foi utilizada a estratégia offset-based. Para o volume de dados deste caso o uso do offset não causa prejuizo de processamento, mas isso precisa ser observado em caso de aumento nos dados. O mesmo também permite uma visualização mais limpa limitando quantos itens estarão representados na página web. Em resumo foi definido pela estratégia mais simples visto que a demanda da paginação não necessitava de uma solução mais complexa.
Cache vs Queries Diretas - Visto que a rota de estatística realiza diversas queries que passam por todas as tabelas criadas foi decidio utilizar a opção de um cache temporário. Apesar da quantidade de dados permite sempre calculo na hora a existencia do cache reduz ainda mais qualquer chance de travamento por sobrexarg no sprocessamento e o FastAPI possui um sistema de cache proprio rapidamente aplicável.
Estrutura de Resposta da API: a paginação retorna dados e metadados. O uso de metadados facilita a implementação da paginação no frontend e evita novas chamadas desnecessárias da API a custo de mais inforação necessitar de ser transmitida. Essa informação extra não prejudica a comunicação entre front e backend e portanto vale a aplicação.

### Frontend
A aplicação web foi feita em Vue. Foi montada uma interface simples e funcional para a presentação dos dados conforme solicitado.
Foi utilizado o vue router para fazer mudança de páginas. As telas da interfce são a tela com a lista de operadoras, tela de detalhes da operadora, tela de despesas da operadora e a tela d estatísticas.
Toda estilização foi feita através do styles.css na pasta assets.
A página "Companies" lista as operadoras usando o componente "CompaniesList". É este componente que faz a chamada API e controla a paginação. Além disso o mesmo possui dois botões que levam a pagina de detalhes ou despesas da operadora selecionada. Cada botão recebe o dado do CNPJ da operadora e passa ele como parametro de rota que é absorvido pelas outras páginas para fazer suas próprias chamadas.
A página de "Statistics" utiliza Charts.js e o componente "StatsChart" para gerar gráficos baseados nos dados da rota de estatisticas da API. O componente configura os gráficos e faz ajustes gerais e especificos para cada um dos gráficos mostrados e a página faz a chamada de API separando os dados de cada gráfico e chamando um componente para cada conjunto de dados.
A página de "Details" e "Costs" funciona de forma semelhante, recebendo o cnpj como parametro de rota e fazendo sua chamada API correpsondente. Os dados então são mostrados em tela de forma estilizada.
Trade-off técnico:
Estratégia de Busca/Filtro - visto que o volume de dados permite e para não haver travamento ou sobrecarga de processamento pelo cliente foi escolhido uma busca no servidor. Isso permite utilizar da melhor eficinecia do banco de dados em filtrar e paginar os elementos e mandar para a interface penas os dados necessários.
Gerenciamento de Estado - visto que as páginas não precisam exibir dados simultaneos, trabalham de forma idependente e não há problema em trasnmitir o cnpj pela rota (já que é uma dado publico) foi definido o uso de  Props/Events simples. basicamente o mesmo é passado como parametro na rota. Novamente a necessidade permitiu a utilização da solução mais simples e limpa.
Performance da Tabela - foi utilizado um método de paginação onde os dados chegam ao frontend parcializados. São enviadas da API apenas 10 operadoras por vez e portanto a interface apresenta epans essa quantidade por vez. Renderizar todas as operadoras tratria uma tela muito esticada e difícil de visualizar ou buscar pleo item desejado.
Tratamento de Erros e Loading - O tratamento de erros e estados de carregamento é realizado de forma consistente nas diferentes telas da aplicação. Erros de rede ou da API são capturados por blocos try/catch, exibindo mensagens específicas quando fornecidas pelo backend ou mensagens genéricas como fallback. Estados de loading são tratados por flags explícitas ou verificações condicionais de dados, garantindo feedback visual ao usuário. Para dados vazios, optou-se por mensagens simples e genéricas em telas de listagem, priorizando simplicidade, enquanto telas de detalhe apresentam mensagens mais específicas