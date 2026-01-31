# Disclaimer:
Para a realização das atividades aqui presentes, foi utilizada a ajuda de duas IAs: ChatGPT e Grok. Ambas foram utilizadas para acelerar a busca de informações pela internet e auxiliar na criação de modelos de código para modificação e adição ao código oficial. Nenhum código presente foi puramente feito por inteligência artificial; a combinação entre o indivíduo (eu — Pedro) e essa tecnologia foi o que permitiu a realização das atividades da forma como se encontram.

# Utilização:
Antes de inicializar o código, verifique se existe alguma pasta ou arquivo dentro da pasta documents. Caso exista e você queira testar o programa por completo, apague tudo dentro dessa pasta. Todas as pastas e arquivos em documents serão criados durante a execução dos códigos.
Para executar o programa, baixe uma cópia do mesmo e coloque os arquivos em uma pasta. Abra o arquivo principal main.py em qualquer IDE e execute, no terminal, o comando python main.py. O terminal exibirá um menu para a execução de todas as atividades, e cada atividade possui um menu próprio para executar suas partes individualmente ou de forma completa.

# Documentação:

### main.py:
O arquivo main.py serve como um menu geral para acessar todas as atividades. Ele foi desenvolvido dessa forma para proporcionar um controle simples, porém efetivo, permitindo acessar cada atividade sem a necessidade de reiniciar o programa.

### prog1:
Para a realização de todos os pontos da atividade 1, foi necessário criar variáveis globais para os caminhos das diferentes pastas que seriam utilizadas, além de gerar essas pastas automaticamente. Essa divisão de pastas foi escolhida para melhorar a organização dos arquivos, visto que existe uma série de arquivos que são baixados, modificados e gerados pelo código.

## Atividade 1.1:
O objetivo da atividade é adquirir as demonstrações contábeis dos três últimos trimestres disponibilizados pela ANS.
O código acessa a API no endereço https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/ e busca todos os links disponíveis. São identificados os links que seguem exatamente o formato YYYY/, padrão utilizado para representar os anos na URL indicada.
Todos os links referentes aos anos são armazenados em ordem decrescente e, para cada um deles, são buscados os arquivos correspondentes aos trimestres. Foi desenvolvido um filtro capaz de aceitar diferentes padrões de nomenclatura dos arquivos trimestrais. Exemplos de nomes aceitos incluem: 
- 1T2025,
- 2025_2_trimestre
- 1_trimestre.
Cada arquivo encontrado passa por esse filtro e pela verificação de extensão, sendo considerados apenas arquivos no formato .zip, já que todas as demonstrações trimestrais de despesas são disponibilizadas nesse formato. Caso o arquivo atenda aos critérios, o seu caminho é adicionado a uma variável de controle. Após a identificação de três arquivos válidos, o sistema interrompe a busca por novos arquivos. Os arquivos selecionados são organizados em ordem decrescente, do trimestre mais recente para o mais antigo.
Os caminhos dos três arquivos selecionados também são armazenados em uma variável global chamada ARQUIVOS_ESPERADOS, indicando a existência dos arquivos trimestrais desejados.
Por fim, cada caminho de arquivo é acessado e a conexão com a URL é verificada. O nome do arquivo é extraído da URL e é verificado se já existe um arquivo com o mesmo nome na pasta de downloads. Caso não exista, o arquivo é baixado para a pasta downloads.

## Atividade 1.2:
O objetivo da atividade é acessar e processar os arquivos de despesas dos três últimos trimestres, especificamente em relação ao tipo de despesa “Despesas com Eventos / Sinistros”.
Para isso, foi definido que os arquivos originais não seriam modificados. Em vez disso, é criado um novo arquivo chamado dados_normalizados.csv.
O programa utiliza a variável global ARQUIVOS_ESPERADOS e verifica se os arquivos .zip desejados já estão presentes na pasta downloads. Caso não estejam, eles são baixados automaticamente. Em seguida, os arquivos .zip são extraídos integralmente para a pasta extraidos/.
Dentro dessa pasta, o programa busca arquivos que sigam o padrão X T YYYY, onde X é um número de um a quatro e YYYY representa o ano. Esse padrão foi identificado em todos os arquivos de despesas disponibilizados pela ANS.
Cada arquivo que passa por esse filtro é lido por meio de uma função auxiliar, que testa sua extensão e o encoding para garantir a leitura correta. Em seguida, é realizada a busca pela coluna chamada DESCRICAO. Caso essa coluna não seja encontrada, o programa verifica se a terceira coluna contém dados textuais. Se ainda assim não for identificada uma coluna adequada, é aplicado um filtro mais abrangente, que percorre todas as colunas em busca de uma coluna que contenha texto.
Após identificar a coluna correta, é buscado o texto exato “Despesas com Eventos / Sinistros”. O uso do texto exato foi uma decisão técnica, pois esse valor está presente de forma consistente em todos os documentos analisados, enquanto existem outras linhas que contêm apenas as palavras “evento” ou “sinistro” isoladamente. Dessa forma, considerou-se que o texto exato representa corretamente o padrão desejado para identificação do tipo de despesa.
As linhas que atendem a esse critério são adicionadas à variável linhas_normalizadas. Após o processamento de todos os arquivos, os dados armazenados nessa variável passam por uma etapa de normalização: as linhas filtradas são concatenadas em um único DataFrame, as colunas são renomeadas para facilitar o entendimento, os valores monetários são convertidos (substituição de vírgula por ponto e conversão para float), e são criadas colunas derivadas de mês e ano a partir da data de referência presente nos documentos.
Por fim, o DataFrame resultante é salvo como dados_normalizados.csv na pasta normalizados/.
Trade-off técnico: foi escolhida a estratégia de processamento em memória, na qual todas as linhas desejadas são carregadas e concatenadas em uma única estrutura antes da normalização. Considerando que o tamanho total dos três arquivos trimestrais é relativamente pequeno (inferior a 1 GB) em relação ao poder computacional disponível, essa abordagem foi considerada adequada e eficiente, sem impacto significativo no uso de memória. Em um cenário em que fosse necessário processar um volume maior de arquivos ou incluir outros tipos de despesas além de “Despesas com Eventos / Sinistros”, seria recomendável avaliar uma estratégia alternativa, processando cada arquivo individualmente e unindo os dados já tratados ao final.

## Atividade 1.3:
O objetivo do programa é gerar um documento chamado consolidado_despesas.csv, unificando os dados dos três trimestres disponíveis. Para isso, é utilizado o arquivo normalizado dados_normalizados.csv, além da criação de um arquivo auxiliar responsável por converter registro ANS em CNPJ e razão social, denominado mapa_registro_ans_cnpj.csv. Para o registro de erros e inconsistências identificadas durante o processamento, foi criado o arquivo consolidado_despesas_erros.csv.
O programa realiza uma consulta à API da ANS, considerando operadoras ativas e canceladas, com o objetivo de construir um mapa de conversão entre registro ANS, CNPJ e razão social. O código busca arquivos com o nome cadop (aparente padrão dos arquivos que listam operadoras), realiza o download desses arquivos e os lê utilizando uma função auxiliar.
Os nomes das colunas são normalizados e é feita a busca por três colunas essenciais: registro ANS, CNPJ e razão social. Essa busca é realizada de forma flexível, permitindo identificá-las mesmo em caso de pequenas alterações em seus nomes no futuro. Em seguida, é criada uma coluna Status para indicar se o CNPJ pertence a uma operadora ativa ou cancelada, e todas as linhas e colunas resultantes são consolidadas em uma única estrutura.
Durante a consolidação, é realizada a verificação de CNPJs duplicados. CNPJs ativos duplicados têm o nome da razão social modificado para indicar que a operadora possui dois ou mais registros associados. Já os CNPJs duplicados entre as tabelas de operadoras ativas e canceladas têm o registro da tabela de canceladas removido, pois esse cenário indica uma possível reativação da operadora. A manutenção de CNPJs ativos duplicados tem como objetivo preservar a transparência dos dados, permitir a análise humana das inconsistências e possibilitar a definição de um tratamento mais preciso no futuro. Ao final dessa etapa, é gerado o arquivo mapa_registro_ans_cnpj.csv.
Na sequência, o programa lê o arquivo dados_normalizados.csv, gerado na atividade anterior, e cria um novo DataFrame. É utilizada a função auxiliar buscar_cnpj_razao para converter o registro ANS presente nos dados normalizados em CNPJ e razão social. Essa função, por sua vez, utiliza a função carregar_mapa_conversor, cujo objetivo é carregar o arquivo CSV do mapa de conversão apenas uma vez e armazená-lo em uma variável global, evitando sobrecarga e atrasos decorrentes de múltiplas leituras do mesmo arquivo.
São então criadas as colunas CNPJ e RazaoSocial. O campo Ano é obtido diretamente do arquivo normalizado, enquanto o Trimestre é calculado a partir do número do mês, sendo convertido para o trimestre correspondente. A coluna ValorDespesas é calculada a partir da diferença entre o valor final e o valor inicial, representando o montante efetivo de despesas (ou variações financeiras) no período analisado.
Durante essa etapa, são identificados valores zerados e negativos. Valores zerados são removidos do arquivo final por não representarem movimentação financeira relevante, mas são devidamente registrados no arquivo de erros para fins de rastreabilidade. Já os valores negativos não são descartados automaticamente; eles são mantidos no conjunto de erros com uma marcação específica, pois podem ocorrer legitimamente em situações como reversão de provisões. A decisão de apenas sinalizá-los, e não eliminá-los, segue uma abordagem conservadora, reconhecendo que uma validação definitiva exigiria uma análise estatística mais aprofundada, considerando frequência, distribuição e concentração desses valores ao longo do tempo.
Todos os erros e inconsistências identificados são documentados no arquivo consolidado_despesas_erros.csv. Após o tratamento e a documentação dessas ocorrências, o arquivo consolidado_despesas.csv é gerado contendo as colunas exigidas no enunciado: CNPJ, RazaoSocial, Trimestre, Ano e ValorDespesas, com os dados consolidados dos três trimestres. Por fim, esse arquivo é compactado no formato ZIP com o nome consolidado_despesas.zip, conforme solicitado.

## Atividade 2.1
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
















Atividade 2.2:
O programa acessa os arquivos baixados da atividade 1.3 de operadoras ativas e canceladas para buscar as novas colunas a serem adicionadas no arquivo "despesas_consolidadas.csv". Não haverá problemas com CNPJ, pois os mesmos foram identificados no exercício anterior. CNPJ não identificados são marcados como NOK e é adicionada uma linha no arquivo de erros para verificação manual. Novamente como a modificação ou eliminação de dados oficiais da ANS pode prejudicar analises futuras os valores são matidos como estão e suas inconsistencias documentadas até que seja possível haver um padronização de como lidar com cada tipo de inconsistencia. Este programa lê os dois arquivos de operadors buscando as colunas desejadas para a dição, além do arquivo já existente de despesas. É criado um data frame com a união das colunas que serão adicionadas além de uma coluna auxiliar que usa CNPJ como a chave de verificação. As colunas desejadas são todas verificadas para sua existencia e caso aja alguma faltante o código informa.
É criado um segundo data frame para o arquivo de despesas também criando a coluna auxiliar de cnpj. Essas duas colunas são normalizadas da mesma forma para evitar diferenças ligadas a uso de pontos, espaços em branco entre outros.
Para fazer o join entre os data frames foi escolhido a opção de usar um dicionário que fazr a relação do CNPJ com os outros itens a serem adicionados em despesas. O dicionário foi escolhido como o melhor formato para este caso por ser eficiente em quantidades pequenas de dados (poucos milhares de linhas) e por possuir um tempo de execução para adicionar as novas linhas linear -> O(n). Além disso o mesmo é simples de ser aplicado.