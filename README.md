# Disclaimer:
Para a realização das atividades aqui apresentadas, foi utilizada a ajuda de duas IAs: ChatGPT e Grok. Ambas foram empregadas para acelerar a busca de informações na internet e auxiliar na criação de modelos de código para modificação e adição ao código oficial. Nenhum código presente foi feito puramente por inteligência artificial; a combinação entre o indivíduo (eu — Pedro) e essa tecnologia foi o que permitiu a realização das atividades da forma como se encontram.

# Utilização:
Antes de inicializar o código, verifique se existe alguma pasta ou arquivo dentro da pasta documents. Caso exista e você queira testar o programa por completo, apague tudo dentro dessa pasta. Todas as pastas e arquivos em documents serão criados durante a execução do código.
Para executar o programa, baixe uma cópia do mesmo e coloque os arquivos em uma pasta. Abra o arquivo principal main.py em qualquer IDE e execute, no terminal, o comando python main.py. O terminal exibirá um menu para a execução de todas as atividades, e cada atividade possui um menu próprio para executar suas partes individualmente ou de forma completa.

# Documentação

### main.py:
O arquivo main.py serve como um menu geral para acessar todas as atividades. Ele foi desenvolvido dessa forma para proporcionar um controle simples, porém efetivo, permitindo acessar cada atividade sem a necessidade de reiniciar o programa.

## prog1
Para a realização de todos os pontos da Atividade 1, foi necessário criar variáveis globais para os caminhos das diferentes pastas que seriam utilizadas, além de gerar essas pastas automaticamente. Essa divisão de pastas foi escolhida para melhorar a organização dos arquivos, visto que há uma série de arquivos que são baixados, modificados e gerados pelo código.

### Atividade 1.1:
O objetivo da atividade é adquirir as demonstrações contábeis dos três últimos trimestres disponibilizados pela ANS.
O código acessa a API no endereço https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/
e busca todos os links disponíveis. São identificados os links que seguem exatamente o formato YYYY/, padrão utilizado para representar os anos na URL indicada.
Todos os links referentes aos anos são armazenados em ordem decrescente e, para cada um deles, são buscados os arquivos correspondentes aos trimestres. Foi desenvolvido um filtro capaz de aceitar diferentes padrões de nomenclatura dos arquivos trimestrais. Exemplos de nomes aceitos incluem:
- 1T2025,
- 2025_2_trimestre,
- 1_trimestre,
Cada arquivo encontrado passa por esse filtro e pela verificação de extensão, sendo considerados apenas arquivos no formato .zip, já que todas as demonstrações trimestrais de despesas são disponibilizadas nesse formato. Caso o arquivo atenda aos critérios, o seu caminho é adicionado a uma variável de controle. Após a identificação de três arquivos válidos, o sistema interrompe a busca por novos arquivos. Os arquivos selecionados são organizados em ordem decrescente, do trimestre mais recente para o mais antigo.
Os caminhos dos três arquivos selecionados também são armazenados em uma variável global chamada ARQUIVOS_ESPERADOS, indicando a existência dos arquivos trimestrais desejados.
Por fim, cada caminho de arquivo é acessado e a conexão com a URL é verificada. O nome do arquivo é extraído da URL, e é verificado se já existe um arquivo com o mesmo nome na pasta downloads. Caso não exista, o arquivo é baixado para essa pasta.

### Atividade 1.2:
O objetivo da atividade é acessar e processar os arquivos de despesas dos três últimos trimestres, especificamente em relação ao tipo de despesa “Despesas com Eventos / Sinistros”.
Para isso, foi definido que os arquivos originais não seriam modificados. Em vez disso, é criado um novo arquivo chamado dados_normalizados.csv.
O programa utiliza a variável global ARQUIVOS_ESPERADOS e verifica se os arquivos .zip desejados já estão presentes na pasta downloads. Caso não estejam, eles são baixados automaticamente. Em seguida, os arquivos .zip são extraídos integralmente para a pasta extraidos/.
Dentro dessa pasta, o programa busca arquivos que sigam o padrão X T YYYY, em que X é um número de um a quatro e YYYY representa o ano. Esse padrão foi identificado em todos os arquivos de despesas disponibilizados pela ANS.
Cada arquivo que passa por esse filtro é lido por meio de uma função auxiliar, que testa sua extensão e o encoding para garantir a leitura correta. Em seguida, é realizada a busca pela coluna chamada DESCRICAO. Caso essa coluna não seja encontrada, o programa verifica se a terceira coluna contém dados textuais. Se ainda assim não for identificada uma coluna adequada, é aplicado um filtro mais abrangente, que percorre todas as colunas em busca de uma coluna que contenha texto.
Após identificar a coluna correta, é buscado o texto exato “Despesas com Eventos / Sinistros”. O uso do texto exato foi uma decisão técnica, pois esse valor está presente de forma consistente em todos os documentos analisados, enquanto existem outras linhas que contêm apenas as palavras “evento” ou “sinistro” isoladamente. Dessa forma, considerou-se que o texto exato representa corretamente o padrão desejado para a identificação do tipo de despesa.
As linhas que atendem a esse critério são adicionadas à variável linhas_normalizadas. Após o processamento de todos os arquivos, os dados armazenados nessa variável passam por uma etapa de normalização: as linhas filtradas são concatenadas em um único DataFrame, as colunas são renomeadas para facilitar o entendimento, os valores monetários são convertidos (substituição de vírgula por ponto e conversão para float), e são criadas colunas derivadas de mês e ano a partir da data de referência presente nos documentos.
Por fim, o DataFrame resultante é salvo como dados_normalizados.csv na pasta normalizados/.
Trade-off técnico: foi escolhida a estratégia de processamento em memória, na qual todas as linhas desejadas são carregadas e concatenadas em uma única estrutura antes da normalização. Considerando que o tamanho total dos três arquivos trimestrais é relativamente pequeno (inferior a 1 GB) em relação ao poder computacional disponível, essa abordagem foi considerada adequada e eficiente, sem impacto significativo no uso de memória. Em um cenário no qual fosse necessário processar um volume maior de arquivos ou incluir outros tipos de despesas além de “Despesas com Eventos / Sinistros”, seria recomendável avaliar uma estratégia alternativa, processando cada arquivo individualmente e unindo os dados já tratados ao final.

### Atividade 1.3:
O objetivo do programa é gerar um documento chamado consolidado_despesas.csv, unificando os dados dos três trimestres disponíveis. Para isso, é utilizado o arquivo normalizado dados_normalizados.csv, além da criação de um arquivo auxiliar responsável por converter registro ANS em CNPJ e razão social, denominado mapa_registro_ans_cnpj.csv. Para o registro de erros e inconsistências identificadas durante o processamento, foi criado o arquivo consolidado_despesas_erros.csv.
O programa realiza uma consulta à API da ANS, considerando operadoras ativas e canceladas, com o objetivo de construir um mapa de conversão entre registro ANS, CNPJ e razão social. O código busca arquivos com o nome cadop (aparente padrão dos arquivos que listam operadoras), realiza o download desses arquivos e os lê utilizando uma função auxiliar.
Os nomes das colunas são normalizados e é feita a busca por três colunas essenciais: registro ANS, CNPJ e razão social. Essa busca é realizada de forma flexível, permitindo identificá-las mesmo em caso de pequenas alterações em seus nomes no futuro. Em seguida, é criada uma coluna Status para indicar se o CNPJ pertence a uma operadora ativa ou cancelada, e todas as linhas e colunas resultantes são consolidadas em uma única estrutura.
Durante a consolidação, é realizada a verificação de CNPJs duplicados. CNPJs ativos duplicados têm o nome da razão social modificado para indicar que a operadora possui dois ou mais registros associados. Já os CNPJs duplicados entre as tabelas de operadoras ativas e canceladas têm o registro da tabela de canceladas removido, pois esse cenário indica uma possível reativação da operadora. A manutenção de CNPJs ativos duplicados tem como objetivo preservar a transparência dos dados, permitir a análise humana das inconsistências e possibilitar a definição de um tratamento mais preciso no futuro. Ao final dessa etapa, é gerado o arquivo mapa_registro_ans_cnpj.csv.
Na sequência, o programa lê o arquivo dados_normalizados.csv, gerado na atividade anterior, e cria um novo DataFrame. É utilizada a função auxiliar buscar_cnpj_razao para converter o registro ANS presente nos dados normalizados em CNPJ e razão social. Essa função, por sua vez, utiliza a função carregar_mapa_conversor, cujo objetivo é carregar o arquivo CSV do mapa de conversão apenas uma vez e armazená-lo em uma variável global, evitando sobrecarga e atrasos decorrentes de múltiplas leituras do mesmo arquivo.
São então criadas as colunas CNPJ e RazaoSocial. O campo Ano é obtido diretamente do arquivo normalizado, enquanto o Trimestre é calculado a partir do número do mês, sendo convertido para o trimestre correspondente. A coluna ValorDespesas é calculada a partir da diferença entre o valor final e o valor inicial, representando o montante efetivo de despesas (ou variações financeiras) no período analisado.
Durante essa etapa, são identificados valores zerados e negativos. Valores zerados são removidos do arquivo final por não representarem movimentação financeira relevante, mas são devidamente registrados no arquivo de erros para fins de rastreabilidade. Já os valores negativos não são descartados automaticamente; eles são mantidos no conjunto de erros com uma marcação específica, pois podem ocorrer legitimamente em situações como reversão de provisões. A decisão de apenas sinalizá-los, e não eliminá-los, segue uma abordagem conservadora, reconhecendo que uma validação definitiva exigiria uma análise estatística mais aprofundada, considerando frequência, distribuição e concentração desses valores ao longo do tempo.
Todos os erros e inconsistências identificados são documentados no arquivo consolidado_despesas_erros.csv. Após o tratamento e a documentação dessas ocorrências, o arquivo consolidado_despesas.csv é gerado contendo as colunas exigidas no enunciado — CNPJ, RazaoSocial, Trimestre, Ano e ValorDespesas — com os dados consolidados dos três trimestres. Por fim, esse arquivo é compactado no formato ZIP com o nome consolidado_despesas.zip, conforme solicitado.

## prog2
### Atividade 2.1
O objetivo desta etapa é tratar, com maior nível de detalhe, os erros presentes no arquivo consolidado_despesas.csv. Todas as inconsistências identificadas são registradas no arquivo consolidado_despesas_erros.csv.
Para facilitar a identificação de linhas problemáticas, é criada a coluna Status, que recebe os valores "OK" ou "NOK". O valor "NOK" indica que existe pelo menos uma inconsistência associada àquela linha.
São realizadas as seguintes validações:
- Verificação de CNPJ, por meio da função auxiliar cnpj_valido, que verifica a existência do valor, o tamanho correto, a presença apenas de números, a ocorrência de sequências com todos os dígitos iguais e valida os dígitos verificadores utilizando o algoritmo oficial do CNPJ.
- Verificação da Razão Social, garantindo que o campo esteja devidamente preenchido.
- Verificação de ValorDespesas, repetindo as mesmas validações realizadas na Atividade 1.3. Essa redundância foi adotada para atender explicitamente aos requisitos da atividade.
Assim como nas etapas anteriores, apenas as linhas com ValorDespesas zerado são removidas do arquivo principal e devidamente documentadas no arquivo de erros. Caso aja uma linha sem cnpj ou razão social essa linha é removida pela dificuldade da identificação da empresa e prejuízo nos tratamentos futuros.
Todas as demais inconsistências são apenas registradas, sem remoção dos dados, com o objetivo de preservar a informação até que seja possível definir uma estratégia adequada de tratamento, evitando a perda de dados que ainda possam ser validados ou corrigidos.
Após o registro de todos os erros identificados, esses registros são comparados com os itens já existentes no arquivo consolidado_despesas_erros.csv, sendo adicionados apenas aqueles que ainda não constam no arquivo, evitando duplicidades em execuções múltiplas do programa.
Por fim, o arquivo consolidado_despesas.csv é atualizado com a coluna Status, refletindo o resultado das validações realizadas.
Trade-off técnico: essa abordagem prioriza a transparência e a auditabilidade dos dados, ao custo de um possível aumento de retrabalho manual. No entanto, esse retrabalho tende a diminuir ao longo do tempo, à medida que ações específicas passam a ser definidas para cada tipo de inconsistência identificada. Ainda assim, manter um registro separado dos dados originais com erro é fundamental para garantir rastreabilidade e permitir análises futuras.

### Atividade 2.2:
O objetivo foi enriquecer o arquivo consolidado_despesas.csv com os dados de RegistroANS, Modalidade e UF. Para isso, são acessados os arquivos Relatorio_cadop_canceladas.csv e Relatorio_cadop.csv, já baixados no exercício anterior.
Os dois arquivos são lidos e, em cada um deles, são buscadas as colunas desejadas. Em seguida, eles são unidos em um único DataFrame. O arquivo consolidado também é lido, e ambos os conjuntos de dados têm a coluna de CNPJ normalizada para facilitar a adição de novo conteúdo.
Caso existam CNPJs duplicados no arquivo compilado do Cadop, eles são tratados de duas formas:
- Se forem CNPJs em que um registro veio do documento de operadoras ativas e outro do documento de operadoras canceladas, o registro ativo é mantido.
- Se forem CNPJs apenas do documento de operadoras ativas, são utilizados os dados do primeiro registro e é registrado um erro de duplicação de CNPJ.
Além disso, se o CNPJ estiver vazio, a linha é removida e um erro também é registrado. A escolha de remover a linha se deve à poluição do conjunto de dados com valores NaN, visto que o CNPJ é a chave para buscar as novas colunas a serem adicionadas. Ainda assim, o caso é documentado para posterior tratamento manual mais robusto.
É realizado um join, ou seja, a adição das colunas ocorre por meio de um merge direto. Essa estratégia foi escolhida por ser adequada ao volume estimado de dados (poucos milhares de registros), oferecer boa legibilidade, manutenção simples e desempenho satisfatório, além de preservar todos os registros válidos do consolidado de despesas.
Por fim, as colunas auxiliares são removidas e o arquivo consolidado_despesas.csv é sobrescrito com os dados enriquecidos.
Trade-off técnico: a abordagem de merge direto prioriza a agilidade do processo, além de ser simples e funcionar bem em conjunto com toda a análise de dados realizada anteriormente para eliminação e/ou documentação de erros. Após o tratamento dos dados, não houve necessidade de uma abordagem mais robusta ou complexa para a adição das novas colunas e, portanto, uma solução simples e direta foi preferida.

### Atividade 2.3:
O objetivo é realizar a agregação dos dados presentes no arquivo consolidado_despesas.csv, agrupando as informações por RazaoSocial e UF. Além do total de despesas, são calculadas as métricas de média e desvio padrão por trimestre.
Inicialmente, o arquivo consolidado de despesas é lido e a coluna ValorDespesas é convertida para o tipo numérico, garantindo que os cálculos estatísticos sejam executados corretamente. Antes do processo de agregação, é realizada uma validação dos dados linha a linha, com o objetivo de identificar inconsistências como valores nulos, inválidos ou negativos, bem como a ausência de campos considerados chave para a análise, como RazaoSocial e UF. Todas as inconsistências encontradas são registradas no arquivo de erros por meio de uma função auxiliar de registro. Linhas com RazaoSocial ou UF nulos são removidas para não poluir o documento final, mas permanecem registradas para posterior análise.
É realizado um agrupamento inicial para o cálculo dos dados necessários por trimestre. Esses dados são reorganizados utilizando operações de pivot para se tornarem as colunas de médias e desvios padrão.
Os dados são então novamente agrupados no formato desejado de razão social e UF. Em seguida, é calculado o total geral de despesas por RazaoSocial e UF, utilizado como critério principal de ordenação. Todos esses resultados são consolidados em um único DataFrame final. O conjunto de dados agregado é ordenado pelo total de despesas, do maior para o menor. A estratégia de ordenação adotada utiliza a função sort_values, considerada adequada ao volume estimado de dados (poucos milhares de registros), apresentando desempenho satisfatório, simplicidade de implementação e boa legibilidade do código, sem a necessidade de abordagens mais complexas.
Por fim, o resultado é salvo em um novo arquivo CSV denominado despesas_agregadas.csv, preservando o arquivo consolidado original. Conforme solicitado no enunciado, o arquivo gerado é compactado em um arquivo ZIP no formato Teste_{meu_nome}.zip, padronizando a entrega e facilitando o compartilhamento do resultado final.
Trade-off técnico: optou-se pelo uso de operações diretas de groupby, pivot e merge, priorizando clareza, manutenção simples e desempenho adequado ao volume de dados analisado. Considerando as características do problema e o tamanho estimado do conjunto de dados, não houve necessidade de empregar estratégias mais complexas de processamento ou ordenação, sendo adotada uma solução direta, eficiente e alinhada às etapas de validação e documentação de inconsistências realizadas nas atividades anteriores.

## prog3
Nesta etapa, foi realizada a criação de um banco de dados, juntamente com queries para verificar o seu funcionamento correto.

### Atividade 3.1 - Gerar Banco:
O objetivo é realizar a criação de um banco de dados em MySQL, com tabelas baseadas nos arquivos consolidado_despesas, despesas_agregadas e cadastro_operadoras.
Fora do código Python, foi utilizado o MySQL Workbench para produzir um banco de dados com o qual o código pudesse se conectar.
No código, os arquivos desejados foram localizados e lidos. Todos foram verificados previamente para garantir sua existência antes da continuação da execução.
Todos os arquivos passaram por correções de possíveis erros ainda presentes, mesmo após as limpezas realizadas em atividades anteriores. Foram verificados campos importantes para a criação das tabelas, buscando:
- Valores nulos,
- Valores vazios,
- Valores inválidos,
Todos os erros foram registrados no arquivo de erros, mantendo histórico e documentação. Neste caso específico, como os valores observados poderiam impedir a construção das tabelas, as linhas identificadas com erros foram removidas, pois sua permanência poderia interromper o funcionamento do código.
Posteriormente, os valores foram normalizados para melhor padronização. Nesta etapa, os dados são ajustados para seus tipos corretos.
Caso existam valores NaN em colunas que não impedem o funcionamento do código, eles são convertidos para None, mas não são removidos.
Observação – caso específico:
Foi identificado um único caso em que duas linhas eram consideradas diferentes tanto visualmente quanto nas verificações de duplicidade realizadas em exercícios anteriores. Essas linhas, no arquivo despesas_agregadas, apresentavam razões sociais que eram interpretadas como iguais pelo SQL, impedindo o prosseguimento do programa. No campo Operação Específica, foi implementada uma verificação adicional que permitiu identificar essas linhas como duplicadas. A linha repetida foi removida, permitindo a continuidade da geração das tabelas.
Cada tabela foi gerada individualmente, sendo uma tabela para cada arquivo:
- A tabela de despesas consolidadas, denominada despesas_operadoras, recebeu uma chave primária artificial (Id), visto que possui repetição de todos os seus campos-chave, pois representa um histórico de despesas no qual uma operadora pode aparecer diversas vezes.
- A tabela despesas_agregadas utilizou RazaoSocial e UF como chaves, visto que o arquivo já se encontra agregado nesses campos e, portanto, não apresenta repetições.
- A tabela de cadastro utilizou o CNPJ como chave primária, visto que existe um CNPJ por operadora, com duplicidades já tratadas em exercícios anteriores.
Após essas definições, todos os dados foram inseridos nas respectivas tabelas.
Trade-off técnico:
Normalização: optou-se por tabelas separadas e normalizadas. Apesar de o volume de dados não impedir a utilização de uma única tabela desnormalizada, a normalização proporciona dados mais claros e reduz a necessidade de tratamentos adicionais em consultas futuras. Além disso, tabelas separadas permitem buscas mais assertivas e facilitam a organização do banco.
Tipo de dados: foi escolhido o tipo DECIMAL para valores monetários, devido à sua precisão e facilidade de leitura, evitando ajustes posteriores após a recuperação dos dados. Embora seja mais pesado do que alternativas como INTEGER, o volume atual de dados não torna essa diferença relevante. Não foram armazenadas datas completas nas tabelas, apenas valores numéricos indicando trimestre e ano, não sendo necessário o uso de tipos específicos para datas.

### Atividade 3.2, 3.3, 3.4 - Queries
Todas as queries abaixo seguem alguns padrões comuns:
Todas iniciam estabelecendo conexão com o banco de dados e configurando o cursor com dictionary=True, para que os resultados sejam retornados como dicionários, facilitando a leitura e o uso posterior dos dados.
As consultas utilizam CTEs (Common Table Expressions – cláusula WITH) para organizar o processamento em etapas lógicas, aumentando a legibilidade, a manutenção e a confiabilidade da análise.

#### Operadoras com maior aumento percentual de gastos:
O objetivo é consultar as operadoras que apresentaram o maior crescimento percentual de despesas entre o primeiro e o último trimestre disponível no histórico, utilizando a tabela despesas_operadoras.
As etapas dessa query são:
- É contabilizado o número total de trimestres distintos existentes na tabela, garantindo que as operadoras avaliadas possuam dados em todos os períodos.
- Os dados são agrupados por CNPJ, razão social e trimestre, somando os valores de despesas.
- É aplicado um filtro que mantém apenas as operadoras com dados em todos os trimestres analisados.
São identificados o primeiro e o último trimestre disponíveis no histórico para cada operadora.
- É calculado o crescimento percentual utilizando a fórmula((valor_final - valor_inicial)/valor_inicial)*100.
- Os registros são ordenados de forma decrescente, retornando apenas os cinco primeiros (maiores crescimentos).
Existe uma segunda query complementar que executa lógica semelhante, porém identifica operadoras que não possuem dados em todos os trimestres, indicando quais períodos estão ausentes. Essa separação permite uma comparação mais justa entre as operadoras, evitando conclusões incorretas sobre crescimento percentual quando há dados incompletos.

#### Estados com maiores gastos:
O objetivo é consultar os estados e ordená-los pelo maior valor total de gastos, utilizando a tabela despesas_operadoras.
As etapas dessa query são:
- Agrupamento inicial por CNPJ e UF, somando os valores de despesas.
- Novo agrupamento apenas por UF, somando os valores de todos os CNPJs daquele estado e calculando também o valor médio de despesas.
- Os registros são ordenados de forma decrescente, retornando apenas os cinco estados com maiores gastos.

#### Despesas que ultrapassaram valor médio por operadora:
O objetivo desta consulta é identificar operadoras que apresentaram valores de despesas acima de sua média geral em pelo menos dois trimestres, utilizando conjuntamente as tabelas despesas_agregadas e despesas_operadoras.
As etapas são:
- Cálculo da média geral de despesas por operadora, utilizando as médias trimestrais já existentes na tabela despesas_agregadas. - Valores nulos são tratados com COALESCE, evitando erros de cálculo, e apenas trimestres com valores válidos são considerados.
Comparação desse valor médio com os registros da tabela despesas_operadoras. Os dados são associados por razão social e UF; quando o valor do trimestre é superior à média, o período recebe o indicador 1, caso contrário, 0.
- Os resultados são agrupados por operadora e os indicadores são somados. Se o total for maior ou igual a 2, a operadora é considerada elegível, indicando que ultrapassou sua média em pelo menos dois trimestres.
- Os registros finais são ordenados de forma decrescente pelo número de trimestres acima da média.

## prog4
Nesta etapa, foi construída uma API em FastAPI e uma interface web para apresentar os dados do banco de dados criado no exercício anterior. Dentro da pasta prog4 também um json POSTMAN com testes da API.

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