# AI Stock Analyzer

Application Streamlit pédagogique pour étudier une action à partir des cours historiques, des métriques fondamentales accessibles, d'indicateurs techniques, d'actualités et de modèles prédictifs. Les prédictions sont incertaines et ne constituent pas un conseil financier.

## Objectif et cible

La cible est le rendement entre la clôture de la séance courante et celle de la séance suivante : `Close[t+1] / Close[t] - 1`. Cette cible permet de comparer des titres à des niveaux de prix différents; l'application convertit ensuite le rendement prévu en prix indicatif.

Les données restent ordonnées dans le temps : entraînement, validation et test utilisent des fenêtres chronologiques, sans découpage aléatoire. Le scaler est ajusté sur les seules séances d'entraînement. Les scores des trois piliers ne sont ajoutés aux features qu'à partir d'instantanés locaux enregistrés au fil de l'utilisation; les valeurs actuelles ne sont jamais recopiées dans les dates anciennes. Les sources gratuites ne donnent pas l'historique complet des dates de publication et peuvent réviser les données : les instantanés datés réduisent le risque sans remplacer une base institutionnelle point-in-time.

## Technologies et sources

- Python, Pandas, NumPy, scikit-learn, Plotly et Streamlit
- `yfinance` pour cours et informations d'entreprise disponibles
- Yahoo Finance puis Google News RSS pour les nouvelles, sans clé; NewsAPI en source de secours facultative (`NEWSAPI_KEY`)
- FinBERT (`ProsusAI/finbert`) via Transformers/PyTorch pour le sentiment financier; petit lexique de secours si le modèle ne charge pas, avec fiabilité inférieure
- TensorFlow/Keras facultatif pour le LSTM

Les champs et articles accessibles varient selon le titre, le fournisseur et les quotas. L'application indique les données manquantes et n'invente pas d'actualités.

## Architecture

```text
app.py                       Interface Streamlit et orchestration
src/data_loader.py           Cours, fondamentaux et actualités
src/fundamental.py           Tableau et score fondamental explicable
src/technical.py             Indicateurs, score et graphiques Plotly
src/sentiment.py             FinBERT et repli lexical
src/preprocessing.py         Features et cible sans décalage futur
src/ml_models.py             Régression, Random Forest et LSTM facultatif
src/prediction.py            Rendement prévu et prix indicatif
src/evaluation.py            Choix par validation chronologique et test final indépendant
src/stocks.py                Univers de plus de 100 actions Nasdaq-100
src/scoring.py               Étiquettes de synthèse
```

## Installation (PowerShell Windows)

Dans le dossier du projet :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

TensorFlow est optionnel car la compatibilité dépend de la plateforme et de la version Python. Installez-le séparément dans un environnement compatible pour activer le LSTM; sinon les modèles de référence fonctionnent seuls.

FinBERT est également optionnel : les modèles PyTorch/Transformers sont volumineux. Pour l'installer localement, exécutez `pip install -r requirements-finbert.txt`. Sans ces paquets, le lexique de secours permet tout de même une analyse de sentiment simplifiée.

Pour les actualités, définissez facultativement la clé dans la session PowerShell avant le lancement :

```powershell
$env:NEWSAPI_KEY = "votre-cle-newsapi"
```

Ne partagez pas cette clé et ne l'ajoutez pas au code source. Yahoo Finance et Google News RSS sont utilisés sans clé; si ces deux sources ne renvoient aucun article, l'application indique que le sentiment n'a pas pu être calculé.

## Lancement

```powershell
streamlit run app.py
```

Entrez un symbole (ex. `AAPL`), sélectionnez une période et cliquez sur **Analyze**. Une connexion internet est requise pour télécharger les données.

## Explication des méthodes

**Score fondamental (0–100)** : moyenne pondérée des multiples P/E, P/B et EV/EBITDA, d'une estimation DCF en trois scénarios, de la rentabilité, du ROE/ROIC, de l'endettement, de la liquidité, de la couverture des intérêts et du flux de trésorerie disponible. Chaque note utilise un classement par percentile si des observations de pairs sectoriels comparables sont fournies; sinon, une heuristique progressive est explicitement signalée. Les valeurs manquantes apparaissent dans le tableau avec leur avertissement et sont exclues du dénominateur pondéré. Le DCF utilise une croissance, un taux d'actualisation et une croissance terminale prudents; il est omis pour les banques et les flux de trésorerie disponibles non positifs. Les tendances ne s'affichent que si au moins trois périodes annuelles (ou environ trois années trimestrielles) existent. Les dates de fin de période ne sont pas des dates de publication.

**Score technique (0–100)** : moyenne des notes continues par écart au niveau de référence pour les moyennes mobiles 20/50/200, MACD, RSI, ADX/+DI/−DI, position dans les bandes de Bollinger, confirmation par le volume et distance au plus haut annuel. Le RSI affiche survente, zone neutre ou surachat et n'est pas un test binaire. ATR, support et résistance sont montrés comme contexte de risque/niveaux, sans voter pour une direction. Le graphique marque les croisements SMA50/SMA200.

**Verdict des trois analyses** : les scores sont combinés avec des poids par défaut 40 % fondamentaux, 40 % technique et 20 % sentiment. Avec au moins 100 instantanés datés, les poids fondés sur les corrélations d'entraînement ne sont utilisés que s'ils dépassent les poids par défaut sur une période de validation chronologique ultérieure. Les contributions et la force du score sont affichées; cette force n'est pas une probabilité de réussite.

**Apprentissage ML à trois piliers** : chaque analyse lancée enregistre localement, une fois par séance boursière, les scores datés de fondamentaux, technique et sentiment dans `data/pillar_history.csv`. Cela construit des entrées historiques honnêtes sans recopier le score actuel dans le passé. À partir de 100 séances complètes (avec actualités), les modèles comparent les indicateurs de prix et les trois scores dans une validation chronologique; avant ce seuil, la prévision utilise seulement les données de prix. Les actualités et fondamentaux passés ne sont pas fournis par les sources actuelles, donc la collecte commence avec l’utilisation de l’application.

**Sentiment** : les doublons et certains titres de remplissage sont filtrés; les articles sont pondérés selon leur fraîcheur et la qualité indicative de la source, avec un poids réduit pour les textes non anglais. FinBERT note les titres et descriptions. La moyenne pondérée, l'échelle −1 à +1, la répartition des labels, la tendance sur 30 jours et les titres les plus influents sont affichés. Le repli lexical est élémentaire et beaucoup moins fiable.

**Modèles et intervalles** : régression linéaire, Random Forest et Gradient Boosting sont comparés sur des fenêtres chronologiques; un LSTM facultatif peut être ajouté. La prévision affiche des plages indicatives 50 % et 90 %, avec quantiles conformes en échantillon fini calibrés sur les résidus walk-forward; la dépendance temporelle rend leur couverture approximative. Une probabilité hausse/baisse et des effets locaux de variables complètent le prix prévu. Les effets ne sont pas disponibles pour tous les modèles.

**Évaluation du modèle** : l'onglet dédié garde les séances les plus récentes pour un test final chronologique (65 % entraînement, 15 % validation, 20 % test) et ajoute des fenêtres walk-forward à entraînement croissant. À chaque fenêtre, la sélection utilise uniquement les données antérieures. Le modèle est comparé au cours inchangé, à une prédiction toujours haussière et à la moyenne mobile sur 20 séances. MAE, RMSE, exactitude directionnelle et taille de test sont affichées. Le backtest est long/liquidités, retire 10 points de base de frais et 5 points de base de glissement à chaque changement de position, et rapporte Sharpe, drawdown maximal et taux de réussite. Il reste pédagogique : fiscalité, dividendes, liquidité et impact de marché sont exclus.

**Univers d’actions** : le menu propose plus de 100 symboles issus de la liste des sociétés de l’indice Nasdaq-100 publiée par Nasdaq. La composition de l’indice évolue; la liste incluse dans le projet doit être actualisée périodiquement depuis [la page Nasdaq-100](https://www.nasdaq.com/articles/global-indexes/nasdaq-100-index).

## Limites

- Les prix sont intrinsèquement imprévisibles; un test passé ne garantit pas les performances futures.
- Les données gratuites peuvent être différées, limitées ou incomplètes.
- Le sentiment dépend de la couverture d'articles, du quota API et du modèle NLP.
- Les fondamentaux ponctuels ne sont pas intégrés au modèle historique faute d'instantanés datés; cela limite l'objectif de combiner toutes les catégories dans l'entraînement.
- Les validations glissantes améliorent la robustesse, sans remplacer une évaluation sur d’autres titres et régimes de marché. Frais, dividendes, liquidité et événements extrêmes ne sont pas modélisés.
- L’évaluation séparée utilise un test final chronologique; le résultat dépend du titre et de la période choisis et ne prédit pas les performances futures.
- Toute prédiction reste expérimentale et ne doit pas être considérée comme un conseil financier.
