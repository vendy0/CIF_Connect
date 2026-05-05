import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. On charge les données (ex: crimes et éclairage par rue)
data = {
    'rue': ['Regent', 'George', 'King', 'Smythe', 'Dundonald'],
    'incidents_nocturnes': [12, 2, 15, 8, 1],
    'lampadaires_en_panne': [5, 0, 7, 3, 0]
}

df = pd.DataFrame(data)

# 2. On calcule la corrélation (Le fameux chiffre !)
# Cela mesure si les deux variables montent ensemble
correlation = df['incidents_nocturnes'].corr(df['lampadaires_en_panne'])

print(f"Analyse terminée. Corrélation : {correlation:.2f}")

# 3. On crée le graphique pour le devoir de Criminologie
sns.regplot(x='lampadaires_en_panne', y='incidents_nocturnes', data=df)
plt.title('Lien entre éclairage et criminalité à Fredericton')
plt.show()

