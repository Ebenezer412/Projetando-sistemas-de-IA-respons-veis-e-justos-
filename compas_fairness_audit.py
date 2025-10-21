# compas_fairness_audit.py
# Código Python para a Tarefa de Auditoria Prática (Parte 3).
# Simulação da análise de viés racial no dataset COMPAS usando conceitos do AI Fairness 360 (AIF360).

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Simulação do Carregamento do Dataset COMPAS ---
# Criando um dataset mock-up com os atributos essenciais para a auditoria
np.random.seed(42)
data_size = 1000

# Atributo Sensível: Raça (Black, White)
races = np.random.choice(['Black', 'White', 'Other'], size=data_size, p=[0.4, 0.5, 0.1])
# Rótulo de Justiça: Reincidência real (0=Não reincidiu, 1=Reincidiu)
actual_recidivism = np.random.randint(0, 2, size=data_size) 
# Previsão do Modelo: high_risk_score (1=Alto risco, 0=Baixo risco)
# Simulamos o viés: o grupo 'Black' tem uma taxa maior de Falsos Positivos (previsto como 1, mas real é 0).
predicted_risk = np.where(
    (races == 'Black') & (np.random.rand(data_size) < 0.6), 
    np.random.randint(0, 2, size=data_size, p=[0.3, 0.7]), # Mais previsão de alto risco para 'Black'
    np.random.randint(0, 2, size=data_size, p=[0.6, 0.4])  # Menos previsão de alto risco para 'White'
)

df = pd.DataFrame({
    'race': races,
    'two_year_recid': actual_recidivism,
    'high_risk_score': predicted_risk
})

print("Dataset COMPAS mock-up criado (1000 entradas).\n")

# --- 2. Definição de Grupos de Interesse (AIF360 Setup Conceitual) ---
PRIVILEGED_GROUP = "White"
UNPRIVILEGED_GROUP = "Black"
FAVORABLE_OUTCOME = 0 # Resultado favorável é 'Não reincidir' (0)

# --- 3. Cálculo da Métrica de Justiça: Disparate Impact (Simulação) ---
# Disparate Impact (Índice de Impacto Desigual) = (Taxa de Resultado Favorável (U)) / (Taxa de Resultado Favorável (P))

def calculate_disparate_impact(df, group_col, outcome_col, privileged, unprivileged, favorable_outcome):
    # Taxa para o grupo privilegiado
    fav_rate_p = df[df[group_col] == privileged][outcome_col].value_counts(normalize=True).get(favorable_outcome, 0)
    # Taxa para o grupo não-privilegiado
    fav_rate_u = df[df[group_col] == unprivileged][outcome_col].value_counts(normalize=True).get(favorable_outcome, 0)
    
    if fav_rate_p == 0:
        return np.inf
    
    # Índice de Impacto Desigual (Simulação da saída AIF360)
    return fav_rate_u / fav_rate_p

di_score = calculate_disparate_impact(df, 'race', 'high_risk_score', PRIVILEGED_GROUP, UNPRIVILEGED_GROUP, 0)

print(f"Grupo Privilegiado (P): {PRIVILEGED_GROUP}")
print(f"Grupo Não-Privilegiado (U): {UNPRIVILEGED_GROUP}")
print(f"Índice de Impacto Desigual (DI): {di_score:.3f}")

# Regra de 80%: Se DI < 0.8, há evidência de viés (impacto adverso).
if di_score < 0.8:
    print("STATUS: Viés Detectado (Impacto Adverso).")
else:
    print("STATUS: DI está dentro do limite de 80%.")

# --- 4. Análise de Erros: Diferença nas Taxas de Falsos Positivos (FPR) ---
# Um Falso Positivo (FP) ocorre quando high_risk_score=1 (previsto como perigoso) E two_year_recid=0 (não reincidiu).

def calculate_fpr_by_group(df, group):
    # Condição para o grupo específico
    df_group = df[df['race'] == group]
    
    # Verdadeiros Negativos (TN): high_risk_score=0 E two_year_recid=0
    tn = len(df_group[(df_group['high_risk_score'] == 0) & (df_group['two_year_recid'] == 0)])
    # Falsos Positivos (FP): high_risk_score=1 E two_year_recid=0
    fp = len(df_group[(df_group['high_risk_score'] == 1) & (df_group['two_year_recid'] == 0)])
    
    # FPR = FP / (FP + TN) -> De todos que NÃO reincidiram (two_year_recid=0), quantos foram classificados erroneamente como alto risco (high_risk_score=1)?
    total_non_recidivist = fp + tn
    if total_non_recidivist == 0:
        return 0
        
    return fp / total_non_recidivist

fpr_black = calculate_fpr_by_group(df, UNPRIVILEGED_GROUP)
fpr_white = calculate_fpr_by_group(df, PRIVILEGED_GROUP)

print(f"\nTaxa de Falsos Positivos (FPR):")
print(f"- {UNPRIVILEGED_GROUP} (U): {fpr_black:.2f}")
print(f"- {PRIVILEGED_GROUP} (P): {fpr_white:.2f}")
print(f"Disparidade de Falsos Positivos: {fpr_black / fpr_white:.2f}x mais alta para o grupo não-privilegiado.")


# --- Visualização ---
groups = [PRIVILEGED_GROUP, UNPRIVILEGED_GROUP]
fpr_values = [fpr_white, fpr_black]

plt.figure(figsize=(8, 5))
bars = plt.bar(groups, fpr_values, color=['#4CAF50', '#FF5722'])
plt.title('Disparidade na Taxa de Falsos Positivos (FPR) por Raça (COMPAS)')
plt.ylabel('Falsos Positivos (FPR)')
plt.ylim(0, max(fpr_values) * 1.2)
plt.axhline(fpr_white, color='gray', linestyle='--', label=f'FPR {PRIVILEGED_GROUP} (Referência)')
plt.legend()

# Adicionando a disparidade
plt.text(1, fpr_black * 0.9, f'{fpr_black / fpr_white:.2f}x', ha='center', color='black', fontsize=12, fontweight='bold')
plt.annotate(f"Viés: Maior erro no grupo Black", 
             xy=(1, fpr_black), xytext=(0.5, max(fpr_values) * 1.1), 
             arrowprops=dict(facecolor='black', shrink=0.05, width=1), 
             fontsize=10)

plt.grid(axis='y', alpha=0.5)
plt.show()
