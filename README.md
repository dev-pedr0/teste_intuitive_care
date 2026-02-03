# Disclaimer:
Para a realização das atividades aqui presentes, foi utilizada a ajuda de duas IAs: ChatGPT e Grok. Ambas foram utilizadas para acelerar a busca de informações pela internet e auxiliar na criação de modelos de código para modificação e adição ao código oficial. Nenhum código presente foi puramente feito por inteligência artificial; a combinação entre o indivíduo (eu — Pedro) e essa tecnologia foi o que permitiu a realização das atividades da forma como se encontram.

# Utilização:
Antes de inicializar o código, verifique se existe alguma pasta ou arquivo dentro da pasta documents. Caso exista e você queira testar o programa por completo, apague tudo dentro dessa pasta. Todas as pastas e arquivos em documents serão criados durante a execução dos códigos.
Para executar o programa, baixe uma cópia do mesmo e coloque os arquivos em uma pasta. Abra o arquivo principal main.py em qualquer IDE e execute, no terminal, o comando python main.py. O terminal exibirá um menu para a execução de todas as atividades, e cada atividade possui um menu próprio para executar suas partes individualmente ou de forma completa.

# Documentação:

### main.py:
O arquivo main.py serve como um menu geral para acessar todas as atividades. Ele foi desenvolvido dessa forma para proporcionar um controle simples, porém efetivo, permitindo acessar cada atividade sem a necessidade de reiniciar o programa.

## prog1:
Para a realização de todos os pontos da atividade 1, foi necessário criar variáveis globais para os caminhos das diferentes pastas que seriam utilizadas, além de gerar essas pastas automaticamente. Essa divisão de pastas foi escolhida para melhorar a organização dos arquivos, visto que existe uma série de arquivos que são baixados, modificados e gerados pelo código.

### Atividade 1.1:
O objetivo da atividade é adquirir as demonstrações contábeis dos três últimos trimestres disponibilizados pela ANS.
O código acessa a API no endereço https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/ e busca todos os links disponíveis. São identificados os links que seguem exatamente o formato YYYY/, padrão utilizado para representar os anos na URL indicada.
Todos os links referentes aos anos são armazenados em ordem decrescente e, para cada um deles, são buscados os arquivos correspondentes aos trimestres. Foi desenvolvido um filtro capaz de aceitar diferentes padrões de nomenclatura dos arquivos trimestrais. Exemplos de nomes aceitos incluem: 
- 1T2025,
- 2025_2_trimestre
- 1_trimestre.
Cada arquivo encontrado passa por esse filtro e pela verificação de extensão, sendo considerados apenas arquivos no formato .zip, já que todas as demonstrações trimestrais de despesas são disponibilizadas nesse formato. Caso o arquivo atenda aos critérios, o seu caminho é adicionado a uma variável de controle. Após a identificação de três arquivos válidos, o sistema interrompe a busca por novos arquivos. Os arquivos selecionados são organizados em ordem decrescente, do trimestre mais recente para o mais antigo.
Os caminhos dos três arquivos selecionados também são armazenados em uma variável global chamada ARQUIVOS_ESPERADOS, indicando a existência dos arquivos trimestrais desejados.
Por fim, cada caminho de arquivo é acessado e a conexão com a URL é verificada. O nome do arquivo é extraído da URL e é verificado se já existe um arquivo com o mesmo nome na pasta de downloads. Caso não exista, o arquivo é baixado para a pasta downloads.

### Atividade 1.2:
O objetivo da atividade é acessar e processar os arquivos de despesas dos três últimos trimestres, especificamente em relação ao tipo de despesa “Despesas com Eventos / Sinistros”.
Para isso, foi definido que os arquivos originais não seriam modificados. Em vez disso, é criado um novo arquivo chamado dados_normalizados.csv.
O programa utiliza a variável global ARQUIVOS_ESPERADOS e verifica se os arquivos .zip desejados já estão presentes na pasta downloads. Caso não estejam, eles são baixados automaticamente. Em seguida, os arquivos .zip são extraídos integralmente para a pasta extraidos/.
Dentro dessa pasta, o programa busca arquivos que sigam o padrão X T YYYY, onde X é um número de um a quatro e YYYY representa o ano. Esse padrão foi identificado em todos os arquivos de despesas disponibilizados pela ANS.
Cada arquivo que passa por esse filtro é lido por meio de uma função auxiliar, que testa sua extensão e o encoding para garantir a leitura correta. Em seguida, é realizada a busca pela coluna chamada DESCRICAO. Caso essa coluna não seja encontrada, o programa verifica se a terceira coluna contém dados textuais. Se ainda assim não for identificada uma coluna adequada, é aplicado um filtro mais abrangente, que percorre todas as colunas em busca de uma coluna que contenha texto.
Após identificar a coluna correta, é buscado o texto exato “Despesas com Eventos / Sinistros”. O uso do texto exato foi uma decisão técnica, pois esse valor está presente de forma consistente em todos os documentos analisados, enquanto existem outras linhas que contêm apenas as palavras “evento” ou “sinistro” isoladamente. Dessa forma, considerou-se que o texto exato representa corretamente o padrão desejado para identificação do tipo de despesa.
As linhas que atendem a esse critério são adicionadas à variável linhas_normalizadas. Após o processamento de todos os arquivos, os dados armazenados nessa variável passam por uma etapa de normalização: as linhas filtradas são concatenadas em um único DataFrame, as colunas são renomeadas para facilitar o entendimento, os valores monetários são convertidos (substituição de vírgula por ponto e conversão para float), e são criadas colunas derivadas de mês e ano a partir da data de referência presente nos documentos.
Por fim, o DataFrame resultante é salvo como dados_normalizados.csv na pasta normalizados/.
Trade-off técnico: foi escolhida a estratégia de processamento em memória, na qual todas as linhas desejadas são carregadas e concatenadas em uma única estrutura antes da normalização. Considerando que o tamanho total dos três arquivos trimestrais é relativamente pequeno (inferior a 1 GB) em relação ao poder computacional disponível, essa abordagem foi considerada adequada e eficiente, sem impacto significativo no uso de memória. Em um cenário em que fosse necessário processar um volume maior de arquivos ou incluir outros tipos de despesas além de “Despesas com Eventos / Sinistros”, seria recomendável avaliar uma estratégia alternativa, processando cada arquivo individualmente e unindo os dados já tratados ao final.

### Atividade 1.3:
O objetivo do programa é gerar um documento chamado consolidado_despesas.csv, unificando os dados dos três trimestres disponíveis. Para isso, é utilizado o arquivo normalizado dados_normalizados.csv, além da criação de um arquivo auxiliar responsável por converter registro ANS em CNPJ e razão social, denominado mapa_registro_ans_cnpj.csv. Para o registro de erros e inconsistências identificadas durante o processamento, foi criado o arquivo consolidado_despesas_erros.csv.
O programa realiza uma consulta à API da ANS, considerando operadoras ativas e canceladas, com o objetivo de construir um mapa de conversão entre registro ANS, CNPJ e razão social. O código busca arquivos com o nome cadop (aparente padrão dos arquivos que listam operadoras), realiza o download desses arquivos e os lê utilizando uma função auxiliar.
Os nomes das colunas são normalizados e é feita a busca por três colunas essenciais: registro ANS, CNPJ e razão social. Essa busca é realizada de forma flexível, permitindo identificá-las mesmo em caso de pequenas alterações em seus nomes no futuro. Em seguida, é criada uma coluna Status para indicar se o CNPJ pertence a uma operadora ativa ou cancelada, e todas as linhas e colunas resultantes são consolidadas em uma única estrutura.
Durante a consolidação, é realizada a verificação de CNPJs duplicados. CNPJs ativos duplicados têm o nome da razão social modificado para indicar que a operadora possui dois ou mais registros associados. Já os CNPJs duplicados entre as tabelas de operadoras ativas e canceladas têm o registro da tabela de canceladas removido, pois esse cenário indica uma possível reativação da operadora. A manutenção de CNPJs ativos duplicados tem como objetivo preservar a transparência dos dados, permitir a análise humana das inconsistências e possibilitar a definição de um tratamento mais preciso no futuro. Ao final dessa etapa, é gerado o arquivo mapa_registro_ans_cnpj.csv.
Na sequência, o programa lê o arquivo dados_normalizados.csv, gerado na atividade anterior, e cria um novo DataFrame. É utilizada a função auxiliar buscar_cnpj_razao para converter o registro ANS presente nos dados normalizados em CNPJ e razão social. Essa função, por sua vez, utiliza a função carregar_mapa_conversor, cujo objetivo é carregar o arquivo CSV do mapa de conversão apenas uma vez e armazená-lo em uma variável global, evitando sobrecarga e atrasos decorrentes de múltiplas leituras do mesmo arquivo.
São então criadas as colunas CNPJ e RazaoSocial. O campo Ano é obtido diretamente do arquivo normalizado, enquanto o Trimestre é calculado a partir do número do mês, sendo convertido para o trimestre correspondente. A coluna ValorDespesas é calculada a partir da diferença entre o valor final e o valor inicial, representando o montante efetivo de despesas (ou variações financeiras) no período analisado.
Durante essa etapa, são identificados valores zerados e negativos. Valores zerados são removidos do arquivo final por não representarem movimentação financeira relevante, mas são devidamente registrados no arquivo de erros para fins de rastreabilidade. Já os valores negativos não são descartados automaticamente; eles são mantidos no conjunto de erros com uma marcação específica, pois podem ocorrer legitimamente em situações como reversão de provisões. A decisão de apenas sinalizá-los, e não eliminá-los, segue uma abordagem conservadora, reconhecendo que uma validação definitiva exigiria uma análise estatística mais aprofundada, considerando frequência, distribuição e concentração desses valores ao longo do tempo.
Todos os erros e inconsistências identificados são documentados no arquivo consolidado_despesas_erros.csv. Após o tratamento e a documentação dessas ocorrências, o arquivo consolidado_despesas.csv é gerado contendo as colunas exigidas no enunciado: CNPJ, RazaoSocial, Trimestre, Ano e ValorDespesas, com os dados consolidados dos três trimestres. Por fim, esse arquivo é compactado no formato ZIP com o nome consolidado_despesas.zip, conforme solicitado.

## Prog 2
### Atividade 2.1
O objetivo desta etapa é tratar com maior nível de detalhe os erros presentes no arquivo consolidado_despesas.csv. Todas as inconsistências identificadas são registradas no arquivo consolidado_despesas_erros.csv.
Para facilitar a identificação de linhas problemáticas, é criada a coluna Status, que recebe os valores "OK" ou "NOK". O valor "NOK" indica que existe pelo menos uma inconsistência associada àquela linha.
São realizadas as seguintes validações:
- Verificação de CNPJ, por meio da função auxiliar cnpj_valido, que verifica a existência do valor, o tamanho correto, a presença apenas de números, a ocorrência de sequências com todos os dígitos iguais e valida os dígitos verificadores utilizando o algoritmo oficial do CNPJ.
- Verificação da Razão Social, garantindo que o campo esteja devidamente preenchido.
- Verificação de ValorDespesas, repetindo as mesmas validações realizadas no exercício 1.3. Essa redundância foi adotada para atender explicitamente aos requisitos da atividade.
Assim como nas etapas anteriores, apenas as linhas com ValorDespesas zerado são removidas do arquivo principal e devidamente documentadas no arquivo de erros. Todas as demais inconsistências são apenas registradas, sem remoção dos dados, com o objetivo de preservar a informação até que seja possível definir uma estratégia adequada de tratamento, evitando a perda de dados que ainda possam ser validados ou corrigidos.
Após o registro de todos os erros identificados, esses registros são comparados com os itens já existentes no arquivo consolidado_despesas_erros.csv, sendo adicionados apenas aqueles que ainda não constam no arquivo, evitando duplicidades em execuções múltiplas do programa.
Por fim, o arquivo consolidado_despesas.csv é atualizado com a coluna Status, refletindo o resultado das validações realizadas.
Trade-off técnico: essa abordagem prioriza a transparência e a auditabilidade dos dados, ao custo de um possível aumento de retrabalho manual. No entanto, esse retrabalho tende a diminuir ao longo do tempo, à medida que ações específicas passam a ser definidas para cada tipo de inconsistência identificada. Ainda assim, manter um registro separado dos dados originais com erro é fundamental para garantir rastreabilidade e permitir análises futuras.

### Atividade 2.2:
O objetivo foi enriquecer o arquivo "consolidado_despesas.csv" com dados de "RegistroANS", "Modalidade" e "UF". Para isso, são acessados os arquivos "Relatorio_cadop_canceladas.csv" e "Relatorio_cadop.csv", já baixados no exercício anterior.
Os dois arquivos são lidos. Em cada um deles, são buscadas as colunas desejadas e, em seguida, eles são unidos em um único data frame. O arquivo consolidado também é lido, e ambos os arquivos têm sua coluna de CNPJ normalizada para facilitar a adição de novo conteúdo.
Se houver CNPJs duplicados no arquivo compilado do Cadop, eles são tratados de duas formas:
- Se forem CNPJs em que um registro veio do documento de operadoras ativas e outro do documento de operadoras canceladas, o registro ativo é mantido.
- Se forem CNPJs apenas do documento de operadoras ativas, são utilizados os dados do primeiro registro e é informado um erro de duplicação de CNPJ.
Além disso, se o CNPJ estiver vazio, a linha é removida e um erro também é registrado. A escolha de remover a linha se deve à poluição do conjunto de dados com valores NaN, visto que o CNPJ é a chave para buscar as novas colunas a serem adicionadas. Ainda assim, o caso é documentado para tratamento manual posterior mais robusto.
É feito um join, ou seja, a adição das colunas ocorre por meio de um merge direto. Essa estratégia foi escolhida por ser adequada ao volume estimado de dados (poucos milhares de registros), oferecer boa legibilidade, manutenção simples e desempenho satisfatório, além de preservar todos os registros válidos do consolidado de despesas.
Por fim, as colunas auxiliares são removidas e o arquivo "consolidado_despesas.csv" é sobrescrito com os dados enriquecidos.
Trade-off técnico: a abordagem de merge direto prioriza a agilidade do processo, além de ser simples e trabalhar bem em conjunto com toda a análise de dados feita anteriormente para eliminação e/ou documentação de erros. Após o tratamento dos dados, não houve necessidade de uma abordagem mais robusta ou complexa para a adição das novas colunas e, portanto, uma solução simples e direta foi preferida.

### Atividade 2.3:
O objetivo é realizar a agregação dos dados presentes no arquivo "consolidado_despesas.csv", agrupando as informações por RazaoSocial e UF Além do total de despesas, são calculadas as métricas de média e desvio padrão por trimestre.
Inicialmente, o arquivo consolidado de despesas é lido e a coluna ValorDespesas é convertida para o tipo numérico, garantindo que os cálculos estatísticos sejam executados corretamente. Antes do processo de agregação, é realizada uma validação dos dados linha a linha, com o objetivo de identificar inconsistências como valores nulos, inválidos ou negativos, bem como a ausência de campos considerados chave para a análise, como RazaoSocial e UF. Todas as inconsistências encontradas são registradas no arquivo de erros por meio da função auxiliar de registro. RazaoSocial e UF nulos são removidos para não poluir o documento final, mas se mantém registrados para posterior análise.
É feito um agrupamento inicial para serem calculados os dados necessários por trimestre. Esses dados são reorganizados usando operações pivot para se tornarem as cólunas de médias e desvio padrão.
Os ados são novamente agrupados para o formato desajado de razão social e UF. Após isso é calculado o total geral de despesas por RazaoSocial e UF, utilizado como critério principal de ordenação. Todos esses resultados são então consolidados em um único data frame final. O conjunto de dados agregado é ordenado pelo total de despesas, do maior para o menor. A estratégia de ordenação adotada foi utilizando a função sort_values. A mesma é adequada ao volume estimado de dados (poucos milhares de registros), apresentando desempenho satisfatório, simplicidade de implementação e boa legibilidade do código, sem a necessidade de abordagens mais complexas.
Por fim, o resultado é salvo em um novo arquivo CSV denominado "despesas_agregadas.csv", preservando o arquivo consolidado original. Conforme solicitado no enunciado, o arquivo gerado é compactado em um arquivo ZIP no formato "Teste_{meu_nome}.zip", padronizando a entrega e facilitando o compartilhamento do resultado final.
Trade-off técnico: optou-se pelo uso de operações diretas de groupby, pivot e merge, priorizando clareza, manutenção simples e desempenho adequado ao volume de dados analisado. Considerando as características do problema e o tamanho estimado do conjunto de dados, não houve necessidade de empregar estratégias mais complexas de processamento ou ordenação, sendo adotada uma solução direta, eficiente e alinhada às etapas de validação e documentação de inconsistências realizadas nas atividades anteriores.

## Prog 3
Nesta etapa foi feita a criação de um banco de dados juntamente queries para verificar seu funcionamento correto.

### Atividade 3.1 - Gerar Banco:
O objetivo é realizar a criação de um banco em MySQL com tabelas baseados nos arquivos - "consolidado_despesas", "despesas_agregadas" e "cadastro_operadoras".
Fora do código python foi utilizado o MysqlWorkbench para produzir um banco de dados com o qual o código pudesse se conectar.
Em código foram buscados os arquivos desejados e feita sua leitura. Todos eram checados para garantir sua existencia antes da execução seguir.
Todos os arquivos passaram por correções de possíveis erros ainda presentes, mesmo com as limpexas feitas em atividades anteriores.
Foram verificados campos importantes para a criação de tabelas buscando por:
- Valores nulos
- Valores vazios
- Valores inválidos
Todos os erros foram registradoas no arquivo de erro para manter histórico e documentação. Para este caso, como os valores observados poderiam impedir a construção das tabelas as linhas identificadas com erros foram removidas, pois sua presença poderia interromper o funcionamento do código.
Posteriormente os valores foram normalizados para melhor padronização. Nesta etapa os valores são ajustados para seus tipos corretos.
Caso ajam valores NaN em colunas que não impedem o funcionamento do código elas são convertidas para None, mas não são removidas.
Obs: caso específico:
Foi observado um único caso onde duas linhas eram entendidas como diferentes tanto visualmente quanto nas verificações de duplicação de exercicios anteriores. Essas linhas do arquivo "despesas_agregadas" apresentada suas razões sociais indicadas como iguais para o SQL e o programa não dava seguimento. No campo "Operação Específica" é feita justmente a verificação encontrada onde foi possível identificar essas linhas como repetidas. A linha repetida é removida e o código segue para a geração de tabelas.
Cada tabela foi gerada individualmente, uma tabela para um arquivo.
A tabela de despesas consolidadas chamada "despesas_operadoras" teve uma chave principal Id artificialmente criada visto qu a mesma possui repetição de todos os seus valores chave, já que representa um histórico de despesas onde uma operadora aparecerá diversas vezes.
A tabela "despesas_agregadas" usou a razão social e uf como chaves visto que o arquivo está agrupado nesses valores ep ortanto não existem repetições.
A tabela de cadastro utilizou o cnpj como chave visto que há um cnpj por operadora. Suas duplicatas tratadas em exer´cicios anteriores.
Após isso todos os dados são adicionados.
Trade-off técnico:
Normalização - foi escolhida a opçlão de tabelas separadas e normalizadas. Apesar do volume de dados não impedir uma única tabela desnormalizada a normalização permite dados mais claros e com menor necessidade de tratamento quando forem buscados por outros códigos. ALém disso tabelas separadas permitem buscas mais assertivas pela informação desejada e facilita organização.
Tipo de dados - foi escolhido o demical para valores monetários por sua precisão e fácil leitura, evitando ajuste dos dados após ele ser buscado. Apesar de ser mais pesados queoutra opção como o INTERGER o volume de dados atual não é grande para que essa diferença se torne relevante. Não foram armazenadas datas nas tabelas apenas um número indicando o trimestre e o ano portanto não foi preciso definir por um tipo de dado para datas.

### Atividade 3.2, 3.3, 3.4 - Queries
Todas as queries baixo seguem alguns padrões:
Todas iniciam estabelecendo conexão com o banco de dados e configurando o cursor com dictionary=True para que os resultados sejam retornados como dicionários, facilitando a leitura e o uso posterior dos dados.
Além disso a consulta utiliza CTEs (Common Table Expressions – cláusula WITH) para organizar o processamento em etapas lógicas, aumentando a legibilidade, a manutenção e a confiabilidade da análise.

#### Operadoras com maior aumento percentual de gastos:
O objetivo é consultar as operadoras que apresentaram o maior crescimento percentual de despesas entre o primeiro e o último trimestre disponível no histórico, utilizando a tabela "despesas_operadoras".
As estapas desta query são:
- Primeiro é contada a quantidade total de trimestres distintos existentes na tabela. Isso é feito para garantir que as operadoras avaliadas tenham dados em todos os trimestres.
- São agrupados os dados por CNPJ, razão social e trimestre, somando os valores de despesas.
- É feito um filtro que busca apenas operadoras que possuem dados para todos os trimestres analisados.
- É identificado o primeiro e o último trimestre disponível no histórico para cada operadora.
- É calculado o crescimento percentual com a formula ((valor_final - valor_inicial)/valor_inicial)*100.
- Os registros são ordenados de forma decrescente e são buscados apenas os 5 primeiros registros (os 5 maiores).
Existe uma segunda query abaixo que faz praticamente o mesmo que a query acima, mas buscando as operadoras que não possuem dados em todos os trimestres e mostrando qual trimestre está sem dados para as mesmas. Essa separação foi feita para permitir uma comparação justa entre as operadoras e não levar a conclusões falsas de crescimento percentual visto que existem empresas com mais dados que outras.

#### Estados com maiores gastos:
O objetivo é consultar os estados e ordena-los pelo maior valor total de gastos utilizando a tabela "despesas_operadoras".
As estapas desta query são:
- É feito um agrupamento por cnpj e uf somando todos os valores destas linhas.
- Depois é feito um agrupamento apenas por UF somando os valores de todos os CNPJ's naquela UF e calculando o valor médio de despesas também.
- Os registros são ordenados de forma decrescente e são buscados apenas os 5 primeiros registros (os 5 maiores).

#### Despesas que ultrapassaram valor médio por operadora:
O objetivo desta consulta é identificar as operadoras que tiveram valores de despesas acima da sua média geral em pelo menos dois trimestres, utilizando de forma conjunta as tabelas "despesas_agregadas" e "despesas_operadoras".
- É feito um cálculo de média geral de despesas por operadora, utilizando as médias trimestrais já existentes na tabela "despesas_agregadas". Aqui valores nulos são tratados como "COALESCE", evitando erros de cálculo. Apenas os trimestres que possuem valores válidos entram no cálculo da média.
- Este valor médio é comparado com os valores da tabela "despesas_operadoras" para cada operadora. Aqui os dados são associados por razão social e UF aso o valor seja maior que a média, o trimestre recebe o indicador 1, caso contrário, 0.
- Os resultados são agrupados por operadora e são somados os valores atribuidos aos semestres. Se o valor for maior ou igual a 2 a operadora teve valores naquele semestre que ultrapassaram sua média. Essas operadoras são mantidas enquanto as outras são descartadas.
- Os registros são ordenados por ordem descrecente pelo número de trimestres acima da médida.

## Prog 4
