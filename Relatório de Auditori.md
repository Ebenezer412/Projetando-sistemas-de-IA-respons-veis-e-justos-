Relatório de Auditoria de Viés (Dataset COMPAS)

Tarefa: Parte 3 - Auditoria Prática (AI Fairness 360)
Dataset: COMPAS (Conjunto de dados de Reincidência)
Atributo Sensível: Raça (Grupos: "White" e "Black")

Sumário das Descobertas

A auditoria simulada do sistema de avaliação de risco COMPAS confirmou a presença de viés algorítmico racial, manifestado principalmente na métrica de Justiça de Erro (Error Equity). O Índice de Impacto Desigual (DI) calculado demonstrou que o grupo "Black" (não-privilegiado) tem uma taxa de resultados favoráveis (previsão de baixo risco) significativamente menor do que o grupo "White".

No entanto, a disparidade mais crítica reside na Taxa de Falsos Positivos (FPR). A análise revelou que indivíduos no grupo "Black" que não reincidiram em dois anos (resultado real favorável) foram classificados erroneamente como de "Alto Risco" a uma taxa que é aproximadamente X vezes maior do que a observada no grupo "White".

Implicações: Esta disparidade significa que o sistema COMPAS está injustamente estigmatizando e rotulando indivíduos não-reincidentes do grupo "Black" como ameaças. Isso pode levar a sentenças mais longas, negação de liberdade condicional e supervisão excessiva, violando diretamente o princípio de Justiça. O sistema está cometendo o erro mais prejudicial em um grupo específico.

Etapas de Correção Sugeridas

Para mitigar este viés de erro, a abordagem mais eficaz é a mitigação inprocessing usando técnicas de rebalanceamento de pesos durante o treinamento do modelo. Sugerimos a implementação do algoritmo PrejudiceRemover do AI Fairness 360.

Este algoritmo adiciona um termo de penalidade à função de custo do modelo que tenta igualar a previsão do modelo em relação ao atributo sensível (race). O objetivo não é remover a raça da entrada, mas garantir que a saída (pontuação de risco) seja estatisticamente independente do grupo, reduzindo drasticamente a disparidade nas taxas de Falsos Positivos e Falsos Negativos, e restaurando a equidade do processo decisório.