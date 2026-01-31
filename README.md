# Disclaimer:
Para a realização das atividades aqui presentes foi utilizada a ajuda de duas IA's: chat gpt, e grok. As duas foram utlizadas para acelerar a busca de inrofrmações pelo internet e auxliar criando modelos de código para modificação e adição no código oficial. Nenhum código presente é puramente feito pela inteligencia artificial, mas a combinação entre o indivíduo (eu - Pedro) e essa tecnologia foi o que permitiu a realização das atividades como as mesmas se encontram.

# Utilização:
Antes de inicializar o código vefifique seexiste alguma pasta ou arquuivo dentro da pasta documents. Caso exista e caso queria testar o programa por completo apague tudo dentro dessa pasta. Todas as pastas e arquivos em documents serão criados durante a execução dos códigos.
Para executar o programa baixe uma cópia do mesmo e os coloque em uma pasta. Abra o arquivo principal main.py em qualquer IDE e execute no terminal o comando python main.py. O terminal mostrará um menu para a execução de todas as atividades e cada atividade possui um menu para executar suas partes ou a mesma por completo.

# Documentação:

### main.py:
O arquivo main.py serve de menu geral para acessar todas as atividades. Ele foi desenvolvido dessa forma para haver um controle simples, porém efetivo de acessar cada atividade sem precisar reiniciar o programa

### prog1:
Para a realização de todos os pontos da atividade 1 foi necessário criar variáveis globais para os caminhos das diferentes pastas que serão utilizadas além de de gerar as pastas. Foi escolhido essa divisão de pastas para melhor organização de arquivos, visto que existem uma série de arquivos que são baixados, modificados e gerados pelo código.

## Atividade 1.1:
O objetivo da atividade é adquirir as demonstrações contábeis dos 3 ultimos trimestres informados pela ANS.
O código acessa a API em "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/" e busca todos os seus links.
São identificados os links com formato exato "YYYY/". Este padrão é seguido em todos os links referentes aos anos na URl indicada.
Todos os links referente aos anos são salvos em ordem decrescente e em cada um deles é buscado os arquivos de trimestres.
Foi desenvolvido um filtro para aceitar diferentes padrões de nomeclaturas dos arquivos referente a um semestre. Exemplo de nomes aceitos: "1T2025", "2025_2_trimestre", "1_trimestre".
Cada arquivo é passado pelo filtro e pela verificação de ser um arquivo .zip vistos que todos os arquivos de despesas de trimestres são .zip.
Caso passe o caminho do arquivo é adicionado a uma variável. Após 3 arquivos adicionados o sistema não busca por mais arquivos. Os arquivos são colocados em ordem decrescente (do trimestre mais recente ao mais antigo). O caminho dos 3 arquivos também é enviado a uma variável global chamada ARQUIVOS_ESPERADOS para indicar a existencia dos arquivos trimestrais desejados.
Cada caminho de arquivo é acessado e é verificado a conexão com a url. Seu nome é extraido da url e é verificado se já não existe um arquivo com o mesmo nome. Caso não o mesmo é baixado na pasta downloads.

## Atividade 1.2:
O objetivo da atividade é acessar e processar os arquivos de despesas dos 3 ultimos trimestres com relação ao tipo de despesa: "Despesas com
Eventos/Sinistros".
Para isso foi definido que os arquivos originais não seriam modificados, mas seria criado um novo arquivo chamado "dados_normalizados.csv".
O programa busca a variavel global ARQUIVOS_ESPERADOS e verifica se os arquivos .zip desejados já estão na pasta downloads. Caso não estejam eles são baixados.
Os arquivos .zip são extraidos por completo para a pasta extraidos/.
Nessa pasta são buscados arquivos com o padrão XTYYY - onde X é um numero de um a quatro e YYYY é o ano. Esse padrão foi identificado em todos os arquivos de despesas da ANS.
Cada um dos arquivos que passam neste filtro são lidos através de uma função auxiliar que testa sua extensão e enconding para realizar a leitura correta dos mesmos.
Então é buscada a coluna chamada DESCRICAO. Caso não seja encontrada é verificado se a terceira coluna é de texto. Caso também não seja é feito um filtro mais demorado que percorre as colunas buscando uma que conenha texto. Ao achar a coluna desejada é buscado o texto exato "Despesas com Eventos / Sinistros".
Motivo do uso do texto exato: o texto exato existe em todos os documentos identificados, existem outras linhas de texto contendo a palavra "evento" ou "sinistro". Portanto foi suposto que o texto exat oé um padrão de indicativo de despesa e o mesmo deveria ser respeitado.
As linhas que atendem ao critério são adicionadas a varivável: linhas_normalizadas.
Após todos os arquivos serem percorridos os dados em "linhas_normalizadas" são normalizados: é feita concatenação das linhas filtradas em um dataframe, as colunas são renomeadas para melhor entendimento, é feita conversão de valores monetários (mudança de vírgula por ponto e transofrmação em float), cria colunas derivadas de mês e ano a partir da data de referencia no documento.
Por fim esse dataframe é salvo como "dados_normalizados.csv" na pasta normalizados/
Trade-off técnico - Foi escolhida a estratégia de processamento em memória (obter todas as linhas desejadas e concatenadas em uma variavel só e depois normalizar todasde uma única vez). Devido ao tamanho pequeno em relação ao poder computacional dos 3 arquivos de trimestres (abaixo de 1 GB) foi preferido este formato que não irá agredir a memória para o processamento. Em caso da necessidade de aumentar a quantidade de arquivos processados, ou processar mais linhas além das de "Despesas com Eventos / Sinistros" então deve ser avaliado a opção de tratar os dados de cada arquivo individualmente e depois unir os mesmos já tratados.

## Atividade 1.3:
O objetivo do programa é gerar um documento chamado "consolidado_despesas.csv" unindo os dados dos 3 trimestres existentes. Para isso foi utilizado o arquivo normalizado "dados_normalizados.csv" e também foi preciso criar um arquivo que converta registro ans em cnpj e razão social chamado "mapa_registro_ans_cnpj.csv". Para registro de erros e inconcistencias foi criado o arquivo "consolidado_despesas_erros.csv".
O programa realiza uma consulta na API da ANS para operadoras ativas e canceladas, com o objetivo de construir um mapa de conversão entre registro ANS, CNPJ e razão social. O código busca por arquivos com nome cadop (aparente padrão dos arquivos listando operadoras), os baixa e lê usando uma função auxiliar.
Os nomes das colunas são normalizados e é feita busca por 3 colunas: registro ANS, CNPJ e razão social. A busca é feita de forma flexível permitindo encontra-las caso aja mudanças pequenas em seus nomes no futuro.
É criada uma coluna status para indicar se o CNPJ é de uma operadora ativa ou cancelada e depois todas as linhas e colunas são unidas.
Durante a consolidação é feita verificação de CNPJ's duplicados. CNPJ's ativos duplicados sofrem modificação no nome da razão social para indicar que a mesma possui 2 ou mais CNPJ's. CNPJ's entre as tabelas ativas e canceladas tem o CNPJ duplicado da tabela cancelado removido, visto que isso indica uma operadora reativada. Manter CNPJ's ativos duplicados tem como objetivo manter a documentação clara, permitir a análise humana dos dados incorretos e definir um tratamento mais preciso. 
Ao final dessa eta é gerado o arquivo "mapa_registro_ans_cnpj.csv".
Na sequência, o programa lê o arquivo dados_normalizados.csv, gerado no exercício anterior e criado um novo Data Frame. É usava a função auxiliar "buscar_cnpj_razao" para converter o registro ans dos dados normalizados em cnpj's e razões sociais. Essa função, por sua vez usa a função "carregar_mapa_conversor". A ultima tem o objetivo de abrir o arquivo csv do mapa conversor apenas uma vez e salva-lo em uma variável global para não haver demorar ou sobrecarga ao abrir o arquivo toda vez que uma conversão seja feita.
São criadas as colunas CNPJ e RazaoSocial. O campo Ano é obtido diretamente do arquivo normalizado, enquanto o Trimestre é calculado a partir do número do mês, convertendo-o para o trimestre correspondente. A coluna ValorDespesas é gerada pela diferença entre o valor final e o valor inicial, representando o montante efetivo de despesas (ou variações financeiras) no período analisado.
Durante essa etapa, são identificados valores zerados e negativos. Valores zerados são removidos do arquivo final por não representarem movimentação financeira relevante, mas são registrados no arquivo de erros para rastreabilidade. Já os valores negativos não são descartados automaticamente, eles são mantidos no conjunto de erros com uma marcação específica, pois podem ocorrer legitimamente em situações como reversão de provisões. A decisão de apenas sinalizá-los, e não eliminá-los, segue uma abordagem conservadora, reconhecendo que uma validação definitiva exigiria uma análise estatística mais aprofundada, considerando frequência, distribuição e concentração desses valores ao longo do tempo.
Todos os erros são documentados no documento "consolidado_despesas_erros.csv".
Após o tratamento e documentação de todas as inconsistências identificadas, o arquivo consolidado_despesas.csv é gerado contendo as colunas exigidas no enunciado: CNPJ, RazaoSocial, Trimestre, Ano e ValorDespesas, com os dados consolidados dos três trimestres. Por fim, esse arquivo é compactado no formato ZIP com o nome consolidado_despesas.zip, conforme solicitado.

## Atividade 2.1
O objetivo é tratar com mais detalhes os erros presentes no arquivo "consolidado_despesas.csv". Todos os erros são registrados em "consolidado_despesas_erros.csv".
Para facilitar a identificação de linhas com problemas é criada a coluna status. Ela recebe "OK" ou "NOK". A segunda opção indica que há algum erro nessa linha.
São feitas as seguintes validações:
- Verificação de CNPJ através de função auxiliar "cnpj_valido". Ele busca por valor inexistente, tamanho, correto, todos os números iguais e validas os digitos verificadores utilizando o algoritmo oficial do CNPJ.
- Verificação de razão social garantindo que o valor esteja preenchido.
- Verificação de ValorDespesas, realizando as mesmas verificações que no exercício 1.3. Basicamente uma redundancia para atender a atividade.
Novamente apenas as linhas com ValorDespesas zerados são removidas e documentas. Todas as outras são apenas documentadas com o objetivo de manter todos os dados presentes até que seja possível definir uma ação correta de como trata-los sem perder informação que pode ser validada ou corrigida.
Após o registro de todos os erros eles são comparados com os itens presentes no arquivo "consolidado_despesas_erros.csv" e adicionados apenas aqueles que ainda não existem, evitando duplicatas em multiplas execuções do código.
Por fim o arquivo "consolidado_despesas.csv" é atualizado com a coluna Status criada anteriormente.
Trade-off técnico - essa abordagem dá preferencia a transparencia e auditoria de dados com o risco de grande quantidade de retrabalho. Porém este retrabalho tende a diminuir com o tempo a medida que são definidas as ações para se lidar com os tipos de inconsistencia. Ainda assim é importante haver um registro dos dados originais errados ao menos em um documento separado para permitir rastreabilidade.







Atividade 2.2:
O programa acessa os arquivos baixados da atividade 1.3 de operadoras ativas e canceladas para buscar as novas colunas a serem adicionadas no arquivo "despesas_consolidadas.csv". Não haverá problemas com CNPJ, pois os mesmos foram identificados no exercício anterior. CNPJ não identificados são marcados como NOK e é adicionada uma linha no arquivo de erros para verificação manual. Novamente como a modificação ou eliminação de dados oficiais da ANS pode prejudicar analises futuras os valores são matidos como estão e suas inconsistencias documentadas até que seja possível haver um padronização de como lidar com cada tipo de inconsistencia. Este programa lê os dois arquivos de operadors buscando as colunas desejadas para a dição, além do arquivo já existente de despesas. É criado um data frame com a união das colunas que serão adicionadas além de uma coluna auxiliar que usa CNPJ como a chave de verificação. As colunas desejadas são todas verificadas para sua existencia e caso aja alguma faltante o código informa.
É criado um segundo data frame para o arquivo de despesas também criando a coluna auxiliar de cnpj. Essas duas colunas são normalizadas da mesma forma para evitar diferenças ligadas a uso de pontos, espaços em branco entre outros.
Para fazer o join entre os data frames foi escolhido a opção de usar um dicionário que fazr a relação do CNPJ com os outros itens a serem adicionados em despesas. O dicionário foi escolhido como o melhor formato para este caso por ser eficiente em quantidades pequenas de dados (poucos milhares de linhas) e por possuir um tempo de execução para adicionar as novas linhas linear -> O(n). Além disso o mesmo é simples de ser aplicado.