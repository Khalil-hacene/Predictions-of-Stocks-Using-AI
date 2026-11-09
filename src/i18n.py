"""Small French/English interface dictionary."""
TEXT = {
"fr": {
"app_title":"Prédiction des marchés boursiers avec l’IA","hero":"Un tableau de bord pour comprendre les tendances, les fondamentaux et le sentiment du marché.","market_label":"MARCHÉS · ANALYSE · DONNÉES",
"analysis":"🔎 Votre analyse","choose":"Choisissez une entreprise et la période à étudier.","language":"Langue","french":"Français","english":"Anglais",
"stock":"Action populaire","stock_help":"Choisissez une entreprise dans la liste; aucun symbole à saisir.","symbol":"Symbole","history":"Historique","p6":"6 mois","p1":"1 an","p2":"2 ans","p5":"5 ans","p10":"10 ans",
"run":"Lancer l’analyse","refresh":"Actualiser toutes les données","refresh_help":"Force une nouvelle récupération au lieu d’utiliser le cache de 15 minutes.","third_party":"Données fournies par des services tiers. Analyse à but pédagogique.",
"invalid_symbol":"Choisissez un symbole boursier valide.","loading":"Récupération des données pour {symbol}…","generic_error":"Une erreur a empêché l’analyse : {error}","quick_view":"Vue rapide · cours à la dernière séance disponible; les fournisseurs peuvent publier les données avec un délai.",
"price_fetch_error":"Impossible de récupérer les cours pour {symbol} : {error}","price_missing":"Aucun historique disponible pour « {symbol} ». Vérifiez le symbole ou la période.","price_incomplete":"Les données reçues sont incomplètes (OHLCV manquant).",
"close":"Cours de clôture","daily_change":"Variation quotidienne","volume":"Volume échangé","market_cap":"Capitalisation boursière","data_status":"Cours datés du {market_date} · cours récupérés le {prices_time} · données d’entreprise récupérées le {fundamentals_time} · actualités récupérées le {news_time}. Cache : 15 minutes.",
"overview":"📊 Vue d’ensemble","technical":"📉 Analyse technique","news":"📰 Actualités et sentiment","forecast":"🤖 Prévision","scores":"Scores de l’entreprise","fundamentals":"Fondamentaux","sentiment":"Sentiment des actualités","fundamentals_table":"Indicateurs fondamentaux","technical_title":"Évolution et indicateurs du marché","technical_score":"Score technique","last_sessions":"Voir les 10 dernières séances",
"news_title":"Ce que disent les actualités","sentiment_avg":"Sentiment moyen","news_count":"{count} articles pertinents, datés et dédupliqués · période : {date_range} · méthode : {method}.","positives":"Positifs","neutrals":"Neutres","negatives":"Négatifs","lexical_warning":"Le lexique de secours analyse les titres et extraits avec des règles simples. Il est moins fiable que FinBERT et ne doit pas être interprété comme une mesure certaine du marché.","original_headlines":"Les titres des actualités restent dans leur langue d’origine.","sentiment_loading":"Chargement de FinBERT et analyse des actualités…","finbert_missing":"FinBERT n’est pas installé dans cet environnement. Dans PowerShell, exécutez `pip install -r requirements-finbert.txt`, puis redémarrez l’application. Au premier usage, le modèle doit aussi être téléchargé.","finbert_load_error":"FinBERT n’a pas pu démarrer; le lexique de secours est utilisé. Vérifiez l’accès Internet pour le téléchargement initial et consultez le détail ci-dessous.","finbert_error_details":"Détail technique du chargement FinBERT",
"forecast_title":"Estimation expérimentale de la prochaine séance","forecast_description":"La cible est le rendement entre la clôture actuelle et celle de la prochaine séance. Les fondamentaux et actualités sont exclus de l’entraînement faute d’historique daté homogène; ils ne sont pas recopiés artificiellement dans les anciennes données.","spinner":"Entraînement et comparaison des modèles sur plusieurs fenêtres temporelles…","forecast_price":"Prix indicatif à la prochaine clôture","model_used":"Modèle retenu : {model} · rendement estimé : {return_pct:+.2%}.","baseline_warning":"Aucun modèle entraîné n’a surpassé la référence sans variation pendant la validation; la prévision affichée reste donc stable.","price_band":"Plage indicative : ${low:,.2f} à ${high:,.2f}. Elle s’appuie sur le 90e centile des erreurs absolues de validation; ce n’est pas un intervalle garanti.","validation_title":"Comparaison en validation temporelle","validation_note":"{folds} fenêtres chronologiques · {rows} séances évaluées · un modèle n’est retenu que s’il fait mieux que la référence sans variation (rendement prévu nul). Chaque modèle est entraîné uniquement sur les séances antérieures.","chart_actual":"Rendement réel","chart_predicted":"Rendement estimé en validation","chart_title":"Rendements réels et estimés en validation chronologique","chart_date":"Date","chart_return":"Rendement quotidien","forecast_error":"La prévision IA n’a pas pu être calculée : {error}. Les autres analyses restent disponibles.",
"conclusion":"Conclusion","conclusion_main":"Pour <b>{symbol}</b>, l’analyse fondamentale est <b>{fund}</b>, l’analyse technique est <b>{technical}</b> et le sentiment des actualités est <b>{sentiment}</b>.","conclusion_forecast":"Le modèle <b>{model}</b> estime le prochain rendement à <b>{change:+.2f}%</b>, soit un prix indicatif de <b>${price:,.2f}</b>.","forecast_missing":"La prévision IA n’a pas pu être calculée avec les données disponibles.","news_missing":"Le sentiment n’a pas pu être évalué faute d’articles récents.","disclaimer":"Ces signaux sont expérimentaux et peuvent se contredire; cette conclusion n’est pas certaine et ne constitue pas un conseil financier.","summary":"Résumé des signaux","summary_line":"Fondamentaux {fund} · Technique {technical} · Sentiment {sentiment} · Prévision {forecast}.","disclaimer_short":"Analyse expérimentale, non garantie et sans valeur de conseil financier.","prompt":"Choisissez une entreprise et une période, puis cliquez sur **{run}**.","recent_none":"Aucun article pertinent, daté et récent n’a été retourné. Les articles sans date et ceux de plus de 30 jours sont écartés.",
"fund_income":"Chiffre d’affaires","net_income":"Résultat net","eps":"Bénéfice par action","pe":"Ratio cours/bénéfice","roe":"Rendement des capitaux propres","debt":"Dette totale","free_cash":"Flux de trésorerie disponible","revenue_growth":"Croissance du chiffre d’affaires","margin":"Marge bénéficiaire","missing":"Indisponible","table_metric":"Indicateur","table_value":"Valeur","table_model":"Modèle","fund_explanation":"{count}/5 critères renseignés : croissance du chiffre d’affaires, marge bénéficiaire, rendement des capitaux propres et flux de trésorerie positifs; ratio cours/bénéfice positif inférieur à 25. Critères équipondérés; les données absentes sont exclues et le score est recalculé sur les critères disponibles. Le seuil est pédagogique, pas un conseil.",
"technical_explanation":"Signaux équipondérés disponibles : clôture > MM20, MM20 > MM50, MACD > ligne de signal, RSI dans la zone 30–70. Les conditions vraies sont divisées par les signaux calculables. Score pédagogique, non prédictif à lui seul.","chart_prices":"{symbol} — cours et moyennes mobiles","chart_volume":"Volume échangé","chart_close":"Clôture","chart_sma20":"MM 20 séances","chart_sma50":"MM 50 séances","chart_volume_axis":"Volume","chart_indicator":"Valeur de l’indicateur","bullish":"Haussier","neutral":"Neutre","bearish":"Baissier","positive":"Positif","negative":"Négatif","unavailable":"Indisponible","lexicon":"Lexique renforcé (mode de secours)","finbert_fallback":"FinBERT + lexique de secours","linear":"Régression linéaire","linear_numpy":"Régression linéaire (NumPy)","forest":"Forêt aléatoire","lstm":"LSTM","zero_baseline":"Référence sans variation","metric_mae":"MAE (rendement)","metric_rmse":"RMSE (rendement)","metric_direction":"Exactitude directionnelle","not_available":"N/D","positive_label":"Positif","neutral_label":"Neutre","negative_label":"Négatif",
"evaluation_tab":"🧪 Évaluation du modèle","evaluation_title":"Évaluation du modèle sur des données inédites","evaluation_description":"Comparaison des cours réellement observés et des estimations sur une période de test chronologique qui n’a pas servi à l’entraînement ni au choix du modèle. L’action et l’historique sélectionnés dans le panneau latéral s’appliquent ici.","evaluation_split":"Découpage chronologique : 65 % entraînement · 15 % validation pour le choix du modèle · 20 % test final tenu à l’écart.","evaluation_no_data":"L’évaluation n’a pas pu être calculée : {error}","evaluation_error_details":"Détail technique de l’erreur","evaluation_insufficient_history":"L’historique est trop court pour un test chronologique indépendant. Choisissez une période plus longue, idéalement au moins un an de données quotidiennes.","evaluation_no_labelled_rows":"Aucune ligne exploitable ne permet d’évaluer le modèle.","evaluation_no_closing_prices":"Les cours réels de clôture sont indisponibles.","evaluation_no_feature_rows":"Aucune ligne complète de caractéristiques n’est disponible.","evaluation_no_aligned_prices":"Il ne reste pas assez de couples de cours réels alignés pour effectuer le test.","evaluation_tab_error":"L’évaluation a rencontré une erreur de calcul. Consultez son détail ci-dessous; les autres analyses restent disponibles.","evaluation_model":"Modèle testé","evaluation_baseline":"Référence (dernier cours connu)","evaluation_mae":"MAE","evaluation_rmse":"RMSE","evaluation_mape":"MAPE","evaluation_direction":"Exactitude directionnelle","evaluation_mae_help":"Erreur absolue moyenne du prix estimé sur le test final, dans la devise de cotation de l’action. Plus bas signifie une erreur moyenne plus faible.","evaluation_rmse_help":"Racine de l’erreur quadratique moyenne, dans la devise de cotation. Les grandes erreurs pèsent davantage.","evaluation_mape_help":"Erreur absolue moyenne en pourcentage. Elle peut être inadaptée si les cours sont nuls ou proches de zéro.","evaluation_direction_help":"Part des séances de test où le modèle a correctement prévu la hausse, la baisse ou l’absence de variation par rapport au cours précédent.","evaluation_chart_title":"Cours observés et estimés sur le test final","evaluation_error_title":"Erreurs au fil du temps","evaluation_distribution_title":"Distribution des erreurs de prix","evaluation_comparison_title":"Modèle et référence sur les mêmes séances de test","evaluation_worst":"Les cinq plus grandes erreurs absolues","evaluation_summary":"Interprétation des résultats","evaluation_no_improvement":"Sur le test final, le modèle sélectionné n’a pas fait mieux que la référence du dernier cours connu selon la MAE. Ce résultat décrit uniquement cette période historique.","evaluation_improvement":"Sur le test final, la MAE du modèle est inférieure à celle de la référence du dernier cours connu. Cette comparaison décrit uniquement cette période historique et ne garantit pas de meilleurs résultats futurs.","evaluation_equal":"Sur le test final, la MAE du modèle est égale à celle de la référence du dernier cours connu, à l’arrondi affiché. Cette comparaison décrit uniquement cette période historique.","evaluation_mape_na":"MAPE non calculable de façon fiable : les prix réels du test sont nuls ou trop proches de zéro.","evaluation_mape_partial":"MAPE calculée sur {count} des {total} observations, les prix proches de zéro étant exclus.","evaluation_period":"Période de test : {start} au {end} · {count} séances · entraînement {train} · validation {validation} · test final {test}.","evaluation_disclaimer":"Un test historique ne garantit pas les performances futures et ne constitue pas un conseil financier.","evaluation_date":"Date","evaluation_actual":"Cours réel","evaluation_predicted":"Cours prédit","evaluation_benchmark":"Référence · dernier cours connu","evaluation_error":"Erreur (prédit − réel)","evaluation_abs_error":"Erreur absolue","evaluation_pct_error":"Erreur (%)","evaluation_direction_correct":"Direction correcte","evaluation_currency_unknown":"devise de cotation","evaluation_export_report":"Télécharger le rapport CSV","evaluation_export_rows":"Télécharger les observations du test (CSV)","evaluation_report_period":"Période de test","evaluation_report_model":"Modèle évalué","evaluation_report_observations":"Observations de test","evaluation_report_train":"Observations d’entraînement","evaluation_report_validation":"Observations de validation","evaluation_report_mae":"MAE modèle","evaluation_report_rmse":"RMSE modèle","evaluation_report_mape":"MAPE modèle (%)","evaluation_report_direction":"Exactitude directionnelle modèle (%)","evaluation_report_baseline_mae":"MAE référence","evaluation_report_baseline_rmse":"RMSE référence","evaluation_report_baseline_mape":"MAPE référence (%)","evaluation_report_baseline_direction":"Exactitude directionnelle référence (%)","evaluation_report_currency":"Devise","evaluation_validation_choice":"Le meilleur candidat entraîné selon la validation est comparé à la référence sur le test final séparé.",
},
"en": {
"app_title":"Stock Market Prediction Using AI","hero":"A dashboard for understanding market trends, company fundamentals, and news sentiment.","market_label":"MARKETS · ANALYSIS · DATA",
"analysis":"🔎 Your analysis","choose":"Choose a company and the period to review.","language":"Language","french":"French","english":"English",
"stock":"Popular stock","stock_help":"Choose a company from the list; no symbol entry required.","symbol":"Symbol","history":"History","p6":"6 months","p1":"1 year","p2":"2 years","p5":"5 years","p10":"10 years",
"run":"Run analysis","refresh":"Refresh all data","refresh_help":"Fetch new data instead of using the 15-minute cache.","third_party":"Data comes from third-party providers. For educational use.",
"invalid_symbol":"Choose a valid stock symbol.","loading":"Fetching data for {symbol}…","generic_error":"The analysis could not be completed: {error}","quick_view":"Quick view · prices are shown for the latest available session; providers may report with a delay.",
"price_fetch_error":"Could not retrieve prices for {symbol}: {error}","price_missing":"No price history is available for {symbol}. Check the symbol or selected period.","price_incomplete":"The returned market data is incomplete (missing OHLCV fields).",
"close":"Closing price","daily_change":"Daily change","volume":"Trading volume","market_cap":"Market capitalization","data_status":"Prices dated {market_date} · prices retrieved {prices_time} · company data retrieved {fundamentals_time} · news retrieved {news_time}. Cache: 15 minutes.",
"overview":"📊 Overview","technical":"📉 Technical analysis","news":"📰 News & sentiment","forecast":"🤖 Forecast","scores":"Company scores","fundamentals":"Fundamentals","sentiment":"News sentiment","fundamentals_table":"Fundamental indicators","technical_title":"Price history and market indicators","technical_score":"Technical score","last_sessions":"Show the last 10 sessions",
"news_title":"What the news is saying","sentiment_avg":"Average sentiment","news_count":"{count} relevant, dated, deduplicated articles · date range: {date_range} · method: {method}.","positives":"Positive","neutrals":"Neutral","negatives":"Negative","lexical_warning":"The fallback lexicon scores headlines and excerpts with simple rules. It is less reliable than FinBERT and should not be treated as a certain measure of the market.","original_headlines":"News headlines remain in their original language.","sentiment_loading":"Loading FinBERT and analysing the news…","finbert_missing":"FinBERT is not installed in this environment. In PowerShell, run `pip install -r requirements-finbert.txt`, then restart the app. The model also needs to download on first use.","finbert_load_error":"FinBERT could not start; the fallback lexicon is being used. Check internet access for the initial download and see the details below.","finbert_error_details":"FinBERT loading details",
"forecast_title":"Experimental next-session estimate","forecast_description":"The target is the return from today’s close to the next session’s close. Fundamentals and news are excluded from training because comparable point-in-time histories are unavailable; current data is not copied into historical rows.","spinner":"Training and comparing models across multiple chronological windows…","forecast_price":"Indicative next-session closing price","model_used":"Selected model: {model} · estimated return: {return_pct:+.2%}.","baseline_warning":"None of the trained models beat the no-change baseline during validation, so the displayed estimate is stable.","price_band":"Indicative range: ${low:,.2f} to ${high:,.2f}. It uses the 90th percentile of absolute validation errors; it is not a guaranteed interval.","validation_title":"Walk-forward validation comparison","validation_note":"{folds} chronological windows · {rows} sessions evaluated · a model is selected only if it beats the no-change baseline (zero predicted return). Each model is trained only on earlier sessions.","chart_actual":"Actual return","chart_predicted":"Validation estimate","chart_title":"Actual and estimated returns in chronological validation","chart_date":"Date","chart_return":"Daily return","forecast_error":"The AI forecast could not be calculated: {error}. The other analyses are still available.",
"conclusion":"Conclusion","conclusion_main":"For <b>{symbol}</b>, the fundamental analysis is <b>{fund}</b>, the technical analysis is <b>{technical}</b>, and news sentiment is <b>{sentiment}</b>.","conclusion_forecast":"The <b>{model}</b> estimates the next return at <b>{change:+.2f}%</b>, or an indicative price of <b>${price:,.2f}</b>.","forecast_missing":"An AI forecast could not be calculated from the available data.","news_missing":"Sentiment could not be assessed because there are no recent articles.","disclaimer":"These experimental signals can conflict. This conclusion is uncertain and is not financial advice.","summary":"Signal summary","summary_line":"Fundamentals {fund} · Technical {technical} · Sentiment {sentiment} · Forecast {forecast}.","disclaimer_short":"Experimental analysis; not guaranteed and not financial advice.","prompt":"Choose a company and period, then click **{run}**.","recent_none":"No relevant, dated, recent articles were returned. Undated articles and articles older than 30 days are excluded.",
"fund_income":"Revenue","net_income":"Net income","eps":"Earnings per share","pe":"Price-to-earnings ratio","roe":"Return on equity","debt":"Total debt","free_cash":"Free cash flow","revenue_growth":"Revenue growth","margin":"Profit margin","missing":"Unavailable","table_metric":"Metric","table_value":"Value","table_model":"Model","fund_explanation":"{count}/5 criteria available: positive revenue growth, profit margin, return on equity, and free cash flow; positive P/E below 25. Criteria are equally weighted; missing data is excluded and the score is recalculated using available criteria. The threshold is educational, not investment advice.",
"technical_explanation":"Available equally weighted signals: close > SMA20, SMA20 > SMA50, MACD > signal line, RSI between 30 and 70. True signals are divided by the number of calculable signals. Educational score; not predictive on its own.","chart_prices":"{symbol} — price and moving averages","chart_volume":"Trading volume","chart_close":"Close","chart_sma20":"20-session MA","chart_sma50":"50-session MA","chart_volume_axis":"Volume","chart_indicator":"Indicator value","bullish":"Bullish","neutral":"Neutral","bearish":"Bearish","positive":"Positive","negative":"Negative","unavailable":"Unavailable","lexicon":"Enhanced lexicon (fallback)","finbert_fallback":"FinBERT + lexical fallback","linear":"Linear regression","linear_numpy":"Linear regression (NumPy)","forest":"Random forest","lstm":"LSTM","zero_baseline":"No-change baseline","metric_mae":"MAE (return)","metric_rmse":"RMSE (return)","metric_direction":"Directional accuracy","not_available":"N/A","positive_label":"Positive","neutral_label":"Neutral","negative_label":"Negative",
"evaluation_tab":"🧪 Model evaluation","evaluation_title":"Model evaluation on unseen data","evaluation_description":"Comparison of observed closing prices and model estimates over a chronological test period that was not used to train or select the model. The stock and history selected in the sidebar also apply here.","evaluation_split":"Chronological split: 65% training · 15% validation for model selection · final 20% held out for testing.","evaluation_no_data":"The evaluation could not be calculated: {error}","evaluation_error_details":"Technical error details","evaluation_insufficient_history":"There is not enough history for an independent chronological test. Choose a longer period, ideally at least one year of daily data.","evaluation_no_labelled_rows":"There are no usable rows available to evaluate the model.","evaluation_no_closing_prices":"Actual closing prices are unavailable.","evaluation_no_feature_rows":"No complete feature rows are available.","evaluation_no_aligned_prices":"Too few aligned actual price pairs remain for the test.","evaluation_tab_error":"The evaluation encountered a calculation error. See details below; the other analyses are still available.","evaluation_model":"Tested model","evaluation_baseline":"Baseline (last known close)","evaluation_mae":"MAE","evaluation_rmse":"RMSE","evaluation_mape":"MAPE","evaluation_direction":"Directional accuracy","evaluation_mae_help":"Mean absolute closing-price error on the final test, in the stock’s quoted currency. Lower means a smaller average error.","evaluation_rmse_help":"Root mean squared closing-price error, in the quoted currency. Larger errors have more weight.","evaluation_mape_help":"Mean absolute percentage error. It can be unsuitable when actual prices are zero or close to zero.","evaluation_direction_help":"Share of test sessions where the model correctly predicted an increase, decrease, or no change from the previous close.","evaluation_chart_title":"Observed and estimated prices on the final test","evaluation_error_title":"Errors over time","evaluation_distribution_title":"Closing-price error distribution","evaluation_comparison_title":"Model and baseline on the same test sessions","evaluation_worst":"Five largest absolute errors","evaluation_summary":"Result interpretation","evaluation_no_improvement":"On the final test, the selected model did not beat the last-known-close baseline by MAE. This result describes only this historical period.","evaluation_improvement":"On the final test, the model MAE is lower than the last-known-close baseline MAE. This comparison describes only this historical period and does not guarantee better future results.","evaluation_equal":"On the final test, model MAE equals the last-known-close baseline MAE at the displayed rounding. This comparison describes only this historical period.","evaluation_mape_na":"MAPE could not be calculated reliably because actual test prices are zero or too close to zero.","evaluation_mape_partial":"MAPE calculated on {count} of {total} observations; prices close to zero were excluded.","evaluation_period":"Test period: {start} to {end} · {count} sessions · training {train} · validation {validation} · final test {test}.","evaluation_disclaimer":"Historical testing does not guarantee future performance and is not financial advice.","evaluation_date":"Date","evaluation_actual":"Actual close","evaluation_predicted":"Predicted close","evaluation_benchmark":"Baseline · last known close","evaluation_error":"Error (predicted − actual)","evaluation_abs_error":"Absolute error","evaluation_pct_error":"Error (%)","evaluation_direction_correct":"Direction correct","evaluation_currency_unknown":"quoted currency","evaluation_export_report":"Download report (CSV)","evaluation_export_rows":"Download test observations (CSV)","evaluation_report_period":"Test period","evaluation_report_model":"Model evaluated","evaluation_report_observations":"Test observations","evaluation_report_train":"Training observations","evaluation_report_validation":"Validation observations","evaluation_report_mae":"Model MAE","evaluation_report_rmse":"Model RMSE","evaluation_report_mape":"Model MAPE (%)","evaluation_report_direction":"Model directional accuracy (%)","evaluation_report_baseline_mae":"Baseline MAE","evaluation_report_baseline_rmse":"Baseline RMSE","evaluation_report_baseline_mape":"Baseline MAPE (%)","evaluation_report_baseline_direction":"Baseline directional accuracy (%)","evaluation_report_currency":"Currency","evaluation_validation_choice":"The trained candidate with the best validation score is compared with the baseline on the separate final test.",
}}

TEXT["fr"].update({
    "navigation_label": "Sections de l’application",
    "forecast_horizon_unit": "Prévoir en",
    "horizon_history_error": "L’historique choisi est trop court pour évaluer cette durée de prévision. Choisissez une période d’historique plus longue ou une prévision plus courte.",
    "forecast_horizon_length": "Durée",
    "horizon_unit_days": "Jours",
    "horizon_unit_weeks": "Semaines",
    "horizon_unit_months": "Mois",
    "horizon_days_1": "1 jour",
    "horizon_days_3": "3 jours",
    "horizon_days_5": "5 jours",
    "horizon_weeks_1": "1 semaine",
    "horizon_weeks_2": "2 semaines",
    "horizon_weeks_4": "4 semaines",
    "horizon_months_1": "1 mois",
    "horizon_months_3": "3 mois",
    "horizon_months_6": "6 mois",
    "chart_all": "Tout",
    "forecast_horizon": "Horizon de prévision",
    "horizon_1": "Un jour",
    "horizon_5": "Une semaine",
    "horizon_21": "Un mois",
    "forecast_title": "Estimation expérimentale sur {horizon}",
    "forecast_current_price": "Dernière clôture connue",
    "forecast_price": "Clôture prévue · {horizon}",
    "forecast_change": "Écart prévu entre les deux cours",
    "forecast_chart_title": "Cours de clôture par date",
    "forecast_chart_history": "Cours historiques",
    "forecast_chart_prediction": "Cours prévu",
    "chart_close_price": "Cours de clôture",
    "forecast_chart_note": "La date future est indicative; les jours fériés boursiers peuvent la décaler.",
    "forecast_method_note": (
        "La prévision estime directement le cours de clôture dans {horizon} à partir de l’historique des cours et des indicateurs. "
        "Une semaine correspond à 5 séances et un mois à 21 séances; les périodes longues ne sont pas une addition de prévisions quotidiennes."
    ),
    "forecast_description_horizon": (
        "Le modèle estime directement le rendement entre la dernière clôture et la clôture dans {horizon}. "
        "La semaine correspond à 5 séances et le mois à 21 séances de Bourse. Les résultats restent expérimentaux."
    ),
    "conclusion_forecast": "Le modèle <b>{model}</b> estime le rendement sur {horizon} à <b>{change:+.2f}%</b>, soit un cours prévu de <b>${price:,.2f}</b>.",
    "stock_universe":"{count} actions proposées · sélection basée sur les constituants Nasdaq-100 publiés par Nasdaq.",
    "sentiment_language_hint":"FinBERT est spécialisé dans le texte financier anglais. La langue de chaque titre est détectée; les titres non anglais sont signalés car leur score peut être moins fiable.",
    "non_english_headline":"⚠ Titre détecté en {language} · FinBERT est entraîné principalement sur des textes financiers anglais.",
    "sentiment_non_english_count":"{count} titre(s) détecté(s) dans une langue autre que l’anglais; leurs scores FinBERT peuvent être moins fiables.",
    "language_code_unknown":"langue indéterminée",
    "evaluation_mase":"MASE","evaluation_mase_help":"MAE du test divisée par l’erreur naïve moyenne calculée uniquement sur l’entraînement. Sous 1 indique une erreur inférieure à cette échelle naïve; ce n’est pas une garantie.",
    "evaluation_return_title":"Rendements réels et estimés","evaluation_return_actual":"Rendement réel (%)","evaluation_return_predicted":"Rendement prédit (%)","evaluation_zero_return":"Référence · rendement nul","evaluation_mean_return":"Référence · rendement moyen historique",
    "evaluation_walk_title":"Validation glissante répétée","evaluation_walk_note":"{folds} fenêtres de test non chevauchantes · {count} séances évaluées · à chaque fenêtre, entraînement et validation utilisent uniquement les dates antérieures.",
    "evaluation_monthly_worst":"Mois avec les erreurs moyennes les plus fortes","evaluation_month":"Mois","evaluation_month_mae":"MAE mensuelle","evaluation_month_bias":"Erreur moyenne signée",
    "evaluation_score_summary":"Sur le test final, la MAE du modèle est plus faible que celle de {better} référence(s) sur {total}. La validation glissante couvre {folds} fenêtres et {rows} séances. Ces résultats décrivent uniquement les dates historiques affichées.",
    "evaluation_report_mean_baseline_mae":"MAE référence rendement moyen","evaluation_report_mean_baseline_rmse":"RMSE référence rendement moyen","evaluation_report_mean_baseline_mape":"MAPE référence rendement moyen (%)","evaluation_report_mean_baseline_direction":"Direction référence rendement moyen (%)",
    "evaluation_report_mase":"MASE modèle","evaluation_report_walk_folds":"Fenêtres walk-forward","evaluation_report_walk_observations":"Observations walk-forward","evaluation_report_walk_mae":"MAE walk-forward modèle","evaluation_report_walk_rmse":"RMSE walk-forward modèle","evaluation_report_walk_mape":"MAPE walk-forward modèle (%)","evaluation_report_walk_direction":"Direction walk-forward modèle (%)","evaluation_report_walk_baseline_mae":"MAE walk-forward dernier cours","evaluation_report_walk_mean_mae":"MAE walk-forward rendement moyen","evaluation_report_summary":"Synthèse calculée","evaluation_report_limits":"Limites",
    "evaluation_report_walk_period":"Période walk-forward","evaluation_walk_fold":"Fenêtre","evaluation_return_error":"Erreur de rendement (points de pourcentage)",
    "evaluation_walk_insufficient":"Historique insuffisant pour au moins trois fenêtres glissantes fiables. Choisissez une période plus longue.",
})

TEXT["en"].update({
    "dcf_range_grade":"price position in scenario range",
    "data_sources_note":"Sources: Yahoo Finance for prices and company data; Yahoo Finance, Google News RSS and optional NewsAPI for headlines. FinBERT labels article text; price-derived technical indicators are calculated locally.",
    "dcf_range":"Illustrative DCF value per share: pessimistic {low:,.2f} {currency} · base {base:,.2f} {currency} · optimistic {high:,.2f} {currency}. Current price vs base case: {margin:+.1f}%.",
    "navigation_label": "App sections",
    "forecast_horizon_unit": "Forecast in",
    "horizon_history_error": "The selected price history is too short to validate this forecast horizon. Choose a longer history period or a shorter forecast horizon.",
    "forecast_horizon_length": "Duration",
    "horizon_unit_days": "Days",
    "horizon_unit_weeks": "Weeks",
    "horizon_unit_months": "Months",
    "horizon_days_1": "1 day",
    "horizon_days_3": "3 days",
    "horizon_days_5": "5 days",
    "horizon_weeks_1": "1 week",
    "horizon_weeks_2": "2 weeks",
    "horizon_weeks_4": "4 weeks",
    "horizon_months_1": "1 month",
    "horizon_months_3": "3 months",
    "horizon_months_6": "6 months",
    "chart_all": "All",
    "stock_universe":"{count} stocks available · selection based on Nasdaq-published Nasdaq-100 constituents.",
    "sentiment_language_hint":"FinBERT is specialized for English financial text. Each headline’s language is detected; non-English headlines are flagged because their scores may be less reliable.",
    "non_english_headline":"⚠ Headline detected as {language} · FinBERT is trained mainly on English financial text.",
    "sentiment_non_english_count":"{count} headline(s) detected as non-English; their FinBERT scores may be less reliable.",
    "language_code_unknown":"undetermined language",
    "evaluation_mase":"MASE","evaluation_mase_help":"Test MAE divided by the mean naive error calculated from training data only. Below 1 means lower error than that naive scale; it is not a guarantee.",
    "evaluation_return_title":"Actual and predicted returns","evaluation_return_actual":"Actual return (%)","evaluation_return_predicted":"Predicted return (%)","evaluation_zero_return":"Baseline · zero return","evaluation_mean_return":"Baseline · historical mean return",
    "evaluation_walk_title":"Repeated walk-forward validation","evaluation_walk_note":"{folds} non-overlapping test windows · {count} sessions evaluated · for each window, training and validation use earlier dates only.",
    "evaluation_monthly_worst":"Months with the highest average errors","evaluation_month":"Month","evaluation_month_mae":"Monthly MAE","evaluation_month_bias":"Mean signed error",
    "evaluation_score_summary":"On the final test, the model MAE is lower than {better} of {total} baselines. Repeated walk-forward validation covers {folds} windows and {rows} sessions. These results describe only the displayed historical dates.",
    "evaluation_report_mean_baseline_mae":"Mean-return baseline MAE","evaluation_report_mean_baseline_rmse":"Mean-return baseline RMSE","evaluation_report_mean_baseline_mape":"Mean-return baseline MAPE (%)","evaluation_report_mean_baseline_direction":"Mean-return baseline direction (%)",
    "evaluation_report_mase":"Model MASE","evaluation_report_walk_folds":"Walk-forward windows","evaluation_report_walk_observations":"Walk-forward observations","evaluation_report_walk_mae":"Walk-forward model MAE","evaluation_report_walk_rmse":"Walk-forward model RMSE","evaluation_report_walk_mape":"Walk-forward model MAPE (%)","evaluation_report_walk_direction":"Walk-forward model direction (%)","evaluation_report_walk_baseline_mae":"Walk-forward last-close MAE","evaluation_report_walk_mean_mae":"Walk-forward mean-return MAE","evaluation_report_summary":"Calculated summary","evaluation_report_limits":"Limitations",
    "evaluation_report_walk_period":"Walk-forward period","evaluation_walk_fold":"Fold","evaluation_return_error":"Return error (percentage points)",
    "evaluation_walk_insufficient":"Not enough history for at least three reliable walk-forward windows. Choose a longer period.",
})

TEXT["fr"].update({
    "dcf_range_grade":"position du cours dans la plage de scénarios",
    "data_sources_note":"Sources : Yahoo Finance pour les cours et données d’entreprise; Yahoo Finance, Google News RSS et NewsAPI facultatif pour les actualités. FinBERT classe les textes; les indicateurs techniques sont calculés localement.",
    "dcf_range":"Valeur DCF indicative par action : pessimiste {low:,.2f} {currency} · centrale {base:,.2f} {currency} · optimiste {high:,.2f} {currency}. Cours actuel vs scénario central : {margin:+.1f}%.",
    "boosting": "Gradient boosting",
    "forecast_description": (
        "Trois modèles de base (régression linéaire, forêt aléatoire et gradient boosting; "
        "LSTM facultatif) apprennent les historiques datés. Avant 100 séances complètes, "
        "l’entraînement utilise les indicateurs techniques. Dès que les historiques sont "
        "collectés, il inclut aussi les scores fondamentaux et le sentiment du jour. Les "
        "modèles sont comparés sur plusieurs fenêtres chronologiques et à une référence "
        "sans variation; les scores actuels ne sont jamais recopiés dans le passé."
    ),
    "spinner": "Entraînement et comparaison de trois modèles sur plusieurs fenêtres temporelles…",
    "three_pillar_signal": "Consensus des trois analyses",
    "signal_agreement": "d’accord",
    "analysis_pillars": "analyses disponibles",
    "pillar_model_collecting": (
        "Collecte des historiques des trois piliers : {count}/{needed} séances exploitables. "
        "En attendant, la prévision ML utilise les indicateurs techniques historiques. "
        "Une séance est enregistrée quand vous lancez l’analyse."
    ),
    "pillar_model_missing_signal": (
        "L’historique des trois piliers est suffisant, mais un score fondamental ou le "
        "sentiment manque pour la séance actuelle. La prévision reste basée sur les cours."
    ),
    "pillar_model_ready": "Prévision ML entraînée avec les trois piliers sur {count} séances datées.",
    "pillar_history_save_error": "Impossible d’enregistrer l’historique local : {error}",
    "forecast_return": "Rendement estimé",
    "forecast_details": "Détails et validation du modèle",
    "baseline_warning": (
        "Le meilleur modèle testé ({model}) n’a pas fait mieux que la référence stable. "
        "Son estimation est affichée, mais elle est moins fiable que cette référence."
    ),
})

TEXT["en"].update({
    "forecast_horizon": "Forecast horizon",
    "horizon_1": "A day",
    "horizon_5": "A week",
    "horizon_21": "A month",
    "forecast_title": "Experimental estimate for {horizon}",
    "forecast_current_price": "Latest known close",
    "forecast_price": "Predicted close · {horizon}",
    "forecast_change": "Expected difference between prices",
    "forecast_chart_title": "Closing price by date",
    "forecast_chart_history": "Historical closing prices",
    "forecast_chart_prediction": "Predicted close",
    "chart_close_price": "Closing price",
    "forecast_chart_note": "The future date is approximate; market holidays may shift it.",
    "forecast_method_note": (
        "The estimate predicts the closing price in {horizon} directly from historical prices and indicators. "
        "A week is 5 trading sessions and a month is 21; longer forecasts are not sums of daily predictions."
    ),
    "forecast_description_horizon": (
        "The model directly estimates the return from the latest close to the close in {horizon}. "
        "A week means 5 trading sessions and a month means 21 sessions. Results are experimental."
    ),
    "conclusion_forecast": "The <b>{model}</b> estimates a {horizon} return of <b>{change:+.2f}%</b>, or a predicted closing price of <b>${price:,.2f}</b>.",
    "boosting": "Gradient boosting",
    "forecast_description": (
        "Three core models (linear regression, random forest, and gradient boosting; "
        "optional LSTM) learn from dated history. Before 100 complete sessions are "
        "collected, training uses historical technical indicators. Once snapshots are "
        "available, it also uses that session’s fundamental and sentiment scores. Models "
        "are compared across chronological windows and against a no-change baseline; "
        "current scores are never copied into the past."
    ),
    "spinner": "Training and comparing three models across multiple time windows…",
    "three_pillar_signal": "Three-pillar consensus",
    "signal_agreement": "agreement",
    "analysis_pillars": "available analyses",
    "pillar_model_collecting": (
        "Collecting dated history for all three pillars: {count}/{needed} usable sessions. "
        "Until then, the ML forecast uses historical technical indicators. A session is "
        "recorded when you run the analysis."
    ),
    "pillar_model_missing_signal": (
        "There is enough three-pillar history, but the current session is missing a "
        "fundamental score or news sentiment. The forecast stays price-based."
    ),
    "pillar_model_ready": "ML forecast trained with all three pillars across {count} dated sessions.",
    "pillar_history_save_error": "Could not save the local history: {error}",
    "forecast_return": "Estimated return",
    "forecast_details": "Model details and validation",
    "baseline_warning": (
        "The best tested model ({model}) did not beat the no-change baseline. Its "
        "estimate is shown, but it is less reliable than that baseline."
    ),
})

TEXT["ar"] = {
    "app_title": "التنبؤ بأسواق الأسهم باستخدام الذكاء الاصطناعي",
    "hero": "لوحة معلومات لفهم اتجاهات الأسعار والأساسيات ومعنويات السوق.",
    "market_label": "الأسواق · التحليل · البيانات",
    "analysis": "🔎 تحليلك",
    "choose": "اختر شركة والفترة الزمنية التي تريد تحليلها.",
    "language": "اللغة",
    "stock": "سهم شائع",
    "stock_help": "اختر شركة من القائمة؛ لا حاجة لإدخال الرمز.",
    "stock_universe": "يتوفر {count} سهمًا · القائمة مستندة إلى شركات ناسداك-100.",
    "history": "الفترة التاريخية",
    "p6": "6 أشهر",
    "p1": "سنة واحدة",
    "p2": "سنتان",
    "p5": "5 سنوات",
    "p10": "10 سنوات",
    "run": "بدء التحليل",
    "refresh": "تحديث جميع البيانات",
    "refresh_help": "جلب بيانات جديدة بدلًا من استخدام ذاكرة التخزين المؤقت.",
    "third_party": "البيانات من مزودين خارجيين. التحليل لأغراض تعليمية.",
    "invalid_symbol": "اختر رمزًا صالحًا من القائمة.",
    "loading": "جارٍ جلب بيانات {symbol}…",
    "generic_error": "تعذر إكمال التحليل: {error}",
    "quick_view": "نظرة سريعة · السعر عند آخر جلسة متاحة؛ قد تتأخر البيانات لدى المزودين.",
    "close": "سعر الإغلاق",
    "daily_change": "التغير اليومي",
    "volume": "حجم التداول",
    "market_cap": "القيمة السوقية",
    "data_status": "تاريخ الأسعار {market_date} · جلب الأسعار {prices_time} · بيانات الشركة {fundamentals_time} · الأخبار {news_time}.",
    "overview": "📊 نظرة عامة",
    "technical": "📉 التحليل الفني",
    "news": "📰 الأخبار والمعنويات",
    "forecast": "🤖 التوقعات",
    "scores": "مؤشرات الشركة",
    "fundamentals": "الأساسيات",
    "sentiment": "معنويات الأخبار",
    "fundamentals_table": "المؤشرات الأساسية",
    "technical_title": "السعر والمؤشرات الفنية",
    "technical_score": "المؤشر الفني",
    "last_sessions": "عرض آخر 10 جلسات",
    "news_title": "ماذا تقول الأخبار؟",
    "sentiment_avg": "متوسط المعنويات",
    "news_count": "{count} خبرًا ذا صلة ومؤرخًا · الفترة: {date_range} · الطريقة: {method}.",
    "positives": "إيجابي",
    "neutrals": "محايد",
    "negatives": "سلبي",
    "original_headlines": "تُعرض عناوين الأخبار بلغتها الأصلية.",
    "sentiment_loading": "جارٍ تحميل FinBERT وتحليل الأخبار…",
    "sentiment_language_hint": "FinBERT متخصص في النصوص المالية الإنجليزية؛ قد تكون نتائجه أقل دقة للنصوص بلغات أخرى.",
    "sentiment_non_english_count": "تم رصد {count} عنوانًا بغير الإنجليزية؛ قد تكون درجاتها أقل موثوقية.",
    "finbert_missing": "FinBERT غير مثبت في هذه البيئة؛ يُستخدم تحليل لغوي مبسط.",
    "finbert_load_error": "تعذر تشغيل FinBERT؛ يُستخدم التحليل اللغوي البديل.",
    "finbert_error_details": "تفاصيل خطأ تحميل FinBERT",
    "lexical_warning": "التحليل البديل يستخدم كلمات وقواعد بسيطة، وهو أقل موثوقية من FinBERT.",
    "forecast_title": "تقدير تجريبي لإغلاق الجلسة التالية",
    "forecast_description": "تتعلم النماذج من البيانات التاريخية المؤرخة. قبل جمع 100 جلسة مكتملة، يعتمد التدريب على المؤشرات الفنية التاريخية. بعد توفر السجلات، تُضاف درجات الأساسيات والمعنويات لتلك الجلسات. لا تُنسخ درجات اليوم إلى الماضي.",
    "spinner": "جارٍ تدريب النماذج ومقارنتها عبر فترات زمنية…",
    "forecast_price": "السعر التقديري عند الإغلاق القادم",
    "model_used": "النموذج المختار: {model} · العائد المقدر: {return_pct:+.2%}.",
    "baseline_warning": "لم يتفوق أفضل نموذج مختبر ({model}) على مرجع عدم التغير. يظهر تقديره، لكنه أقل موثوقية من المرجع.",
    "price_band": "النطاق التقديري: ${low:,.2f} إلى ${high:,.2f}. هذا نطاق تجريبي وليس ضمانًا.",
    "validation_title": "مقارنة النماذج عبر تحقق زمني",
    "validation_note": "{folds} فترات زمنية · {rows} جلسة مختبرة · التدريب يستخدم الجلسات الأقدم فقط.",
    "chart_actual": "العائد الفعلي",
    "chart_predicted": "العائد المتوقع",
    "chart_title": "العوائد الفعلية والمتوقعة عبر الزمن",
    "chart_date": "التاريخ",
    "chart_return": "العائد اليومي",
    "forecast_error": "تعذر حساب التوقع: {error}. بقية التحليلات ما زالت متاحة.",
    "conclusion": "الخلاصة",
    "conclusion_main": "بالنسبة إلى <b>{symbol}</b>، تقييم الأساسيات <b>{fund}</b>، والتحليل الفني <b>{technical}</b>، ومعنويات الأخبار <b>{sentiment}</b>.",
    "conclusion_forecast": "يقدّر نموذج <b>{model}</b> العائد القادم بـ <b>{change:+.2f}%</b>، وسعر الإغلاق بـ <b>${price:,.2f}</b>.",
    "forecast_missing": "تعذر حساب التوقع باستخدام البيانات المتاحة.",
    "news_missing": "تعذر تقييم المعنويات لعدم توفر أخبار حديثة.",
    "disclaimer": "هذه إشارات تجريبية وقد تتعارض؛ الخلاصة غير مؤكدة وليست نصيحة مالية.",
    "summary": "ملخص الإشارات",
    "summary_line": "الأساسيات {fund} · الفني {technical} · المعنويات {sentiment} · التوقع {forecast}.",
    "disclaimer_short": "تحليل تجريبي غير مضمون ولا يمثل نصيحة مالية.",
    "prompt": "اختر شركة وفترة زمنية، ثم اضغط على **{run}**.",
    "recent_none": "لم تُعثر على أخبار حديثة وذات صلة وتاريخ موثوق.",
    "fund_income": "الإيرادات",
    "net_income": "صافي الدخل",
    "eps": "ربحية السهم",
    "pe": "مكرر الربحية",
    "roe": "العائد على حقوق الملكية",
    "debt": "إجمالي الدين",
    "free_cash": "التدفق النقدي الحر",
    "revenue_growth": "نمو الإيرادات",
    "margin": "هامش الربح",
    "missing": "غير متاح",
    "table_metric": "المؤشر",
    "table_value": "القيمة",
    "table_model": "النموذج",
    "fund_explanation": "تم توفير {count} من 5 معايير. تُحسب الدرجة من البيانات المتاحة فقط؛ وهي تعليمية وليست توصية استثمارية.",
    "technical_explanation": "إشارات متساوية الوزن: الإغلاق أعلى من المتوسط 20، ومتوسط 20 أعلى من 50، وMACD أعلى من خط الإشارة، وRSI بين 30 و70. الدرجة تعليمية وليست توقعًا منفردًا.",
    "chart_prices": "{symbol} — السعر والمتوسطات المتحركة",
    "chart_volume": "حجم التداول",
    "chart_close": "الإغلاق",
    "chart_sma20": "متوسط 20 جلسة",
    "chart_sma50": "متوسط 50 جلسة",
    "chart_volume_axis": "الحجم",
    "chart_indicator": "قيمة المؤشر",
    "bullish": "صاعد",
    "neutral": "محايد",
    "bearish": "هابط",
    "positive": "إيجابي",
    "negative": "سلبي",
    "unavailable": "غير متاح",
    "lexicon": "قاموس لغوي مبسط",
    "finbert_fallback": "FinBERT مع تحليل بديل",
    "linear": "الانحدار الخطي",
    "linear_numpy": "الانحدار الخطي (NumPy)",
    "forest": "الغابة العشوائية",
    "boosting": "التعزيز التدرجي",
    "lstm": "شبكة LSTM",
    "zero_baseline": "مرجع عدم التغير",
    "metric_mae": "متوسط الخطأ المطلق (العائد)",
    "metric_rmse": "جذر متوسط مربع الخطأ",
    "metric_direction": "دقة اتجاه الحركة",
    "not_available": "غير متاح",
    "positive_label": "إيجابي",
    "neutral_label": "محايد",
    "negative_label": "سلبي",
    "evaluation_tab": "🧪 تقييم النموذج",
    "evaluation_title": "تقييم النموذج على بيانات غير مستخدمة في التدريب",
    "evaluation_description": "تُقارن الأسعار الفعلية بالتقديرات على فترة اختبار زمنية منفصلة.",
    "evaluation_split": "التقسيم الزمني: 65٪ تدريب · 15٪ تحقق · 20٪ اختبار نهائي.",
    "evaluation_no_data": "تعذر حساب التقييم: {error}",
    "evaluation_error_details": "تفاصيل الخطأ التقني",
    "evaluation_insufficient_history": "السجل التاريخي قصير جدًا للاختبار؛ اختر فترة أطول.",
    "evaluation_walk_insufficient": "لا تتوفر بيانات كافية لثلاث فترات تحقق زمني على الأقل.",
    "evaluation_tab_error": "حدث خطأ أثناء حساب التقييم؛ راجع التفاصيل أدناه.",
    "evaluation_model": "النموذج المختبر",
    "evaluation_baseline": "المرجع (آخر سعر معروف)",
    "evaluation_mae": "MAE",
    "evaluation_rmse": "RMSE",
    "evaluation_mape": "MAPE",
    "evaluation_mase": "MASE",
    "evaluation_direction": "دقة اتجاه الحركة",
    "evaluation_mae_help": "متوسط خطأ سعر الإغلاق في الاختبار؛ الأقل أفضل لهذه الفترة.",
    "evaluation_rmse_help": "يعطي الأخطاء الكبيرة وزنًا أكبر.",
    "evaluation_mape_help": "متوسط الخطأ كنسبة مئوية؛ قد لا يناسب الأسعار القريبة من الصفر.",
    "evaluation_direction_help": "نسبة الجلسات التي صُحح فيها اتجاه الحركة.",
    "evaluation_chart_title": "الأسعار الفعلية والمتوقعة في الاختبار النهائي",
    "evaluation_error_title": "الأخطاء عبر الزمن",
    "evaluation_distribution_title": "توزيع أخطاء سعر الإغلاق",
    "evaluation_comparison_title": "مقارنة النموذج والمراجع في الجلسات نفسها",
    "evaluation_worst": "أكبر خمسة أخطاء مطلقة",
    "evaluation_summary": "تفسير النتائج",
    "evaluation_no_improvement": "لم يتفوق النموذج على مرجع آخر سعر معروف خلال هذه الفترة.",
    "evaluation_improvement": "كان خطأ النموذج أقل من مرجع آخر سعر معروف في هذه الفترة فقط؛ لا يضمن ذلك نتائج مستقبلية.",
    "evaluation_equal": "كان خطأ النموذج مساويًا تقريبًا للمرجع ضمن دقة العرض.",
    "evaluation_mape_na": "تعذر حساب MAPE بشكل موثوق بسبب أسعار فعلية قريبة من الصفر.",
    "evaluation_mape_partial": "حُسب MAPE على {count} من {total} مشاهدة بعد استبعاد الأسعار القريبة من الصفر.",
    "evaluation_period": "فترة الاختبار: {start} إلى {end} · {count} جلسة · تدريب {train} · تحقق {validation} · اختبار {test}.",
    "evaluation_disclaimer": "الاختبارات التاريخية لا تضمن الأداء المستقبلي وليست نصيحة مالية.",
    "evaluation_date": "التاريخ",
    "evaluation_actual": "الإغلاق الفعلي",
    "evaluation_predicted": "الإغلاق المتوقع",
    "evaluation_benchmark": "مرجع · آخر إغلاق معروف",
    "evaluation_error": "الخطأ (المتوقع − الفعلي)",
    "evaluation_abs_error": "الخطأ المطلق",
    "evaluation_pct_error": "الخطأ (%)",
    "evaluation_direction_correct": "الاتجاه صحيح",
    "evaluation_currency_unknown": "العملة المدرجة",
    "evaluation_export_report": "تنزيل التقرير (CSV)",
    "evaluation_export_rows": "تنزيل مشاهدات الاختبار (CSV)",
    "evaluation_validation_choice": "اختير النموذج على بيانات التحقق، ثم قورن بالمرجع في اختبار منفصل.",
    "evaluation_return_title": "العوائد الفعلية والمتوقعة",
    "evaluation_return_actual": "العائد الفعلي (%)",
    "evaluation_return_predicted": "العائد المتوقع (%)",
    "evaluation_zero_return": "مرجع · عائد صفري",
    "evaluation_mean_return": "مرجع · متوسط العائد التاريخي",
    "evaluation_walk_title": "التحقق الزمني المتكرر",
    "evaluation_walk_note": "{folds} نوافذ اختبار · {count} جلسة؛ يستخدم كل تدريب التواريخ السابقة فقط.",
    "evaluation_monthly_worst": "الأشهر ذات أعلى متوسط خطأ",
    "evaluation_month": "الشهر",
    "evaluation_month_mae": "MAE الشهري",
    "evaluation_month_bias": "متوسط الخطأ الموقّع",
    "stock_universe": "يتوفر {count} سهمًا · القائمة مستندة إلى شركات ناسداك-100.",
    "sentiment_language_hint": "FinBERT متخصص في النصوص المالية الإنجليزية؛ قد تكون نتائجه أقل دقة للغات الأخرى.",
    "non_english_headline": "⚠ تم اكتشاف لغة {language}؛ FinBERT مدرّب أساسًا على الإنجليزية.",
    "sentiment_non_english_count": "تم اكتشاف {count} عنوانًا بغير الإنجليزية؛ قد تكون درجاتها أقل موثوقية.",
    "language_code_unknown": "لغة غير محددة",
    "three_pillar_signal": "خلاصة التحليلات الثلاثة",
    "signal_agreement": "نسبة الاتفاق",
    "analysis_pillars": "من التحليلات المتاحة",
    "pillar_model_collecting": "جارٍ جمع السجل المؤرخ للتحليلات الثلاثة: {count}/{needed} جلسة صالحة. حتى ذلك الحين يعتمد توقع التعلم الآلي على المؤشرات الفنية التاريخية. سجّل جلسة عند تشغيل التحليل.",
    "pillar_model_missing_signal": "السجل كافٍ لكن تنقص درجة الأساسيات أو معنويات الأخبار في الجلسة الحالية؛ سيبقى التوقع معتمدًا على الأسعار.",
    "pillar_model_ready": "تم تدريب توقع التعلم الآلي على التحليلات الثلاثة عبر {count} جلسة مؤرخة.",
    "pillar_history_save_error": "تعذر حفظ السجل المحلي: {error}",
    "forecast_return": "العائد المتوقع",
    "forecast_details": "تفاصيل النموذج والتحقق",
    "baseline_warning": "لم يتفوق أفضل نموذج مختبر ({model}) على مرجع عدم التغير. يظهر تقديره، لكنه أقل موثوقية من المرجع.",
}

TEXT["ar"].update({
    "dcf_range_grade":"موقع السعر ضمن نطاق السيناريوهات",
    "data_sources_note":"المصادر: Yahoo Finance للأسعار وبيانات الشركات؛ وYahoo Finance وGoogle News RSS وNewsAPI الاختياري للأخبار. يصنف FinBERT النصوص؛ وتحسب المؤشرات الفنية محليًا.",
    "dcf_range":"القيمة الإرشادية للسهم وفق DCF: متشائم {low:,.2f} {currency} · أساسي {base:,.2f} {currency} · متفائل {high:,.2f} {currency}. السعر الحالي مقابل الأساسي: {margin:+.1f}%.",
    "navigation_label": "أقسام التطبيق",
    "forecast_horizon_unit": "التوقع خلال",
    "horizon_history_error": "الفترة التاريخية المحددة قصيرة جدًا للتحقق من هذا الأفق. اختر فترة تاريخية أطول أو أفق توقع أقصر.",
    "forecast_horizon_length": "المدة",
    "horizon_unit_days": "أيام",
    "horizon_unit_weeks": "أسابيع",
    "horizon_unit_months": "أشهر",
    "horizon_days_1": "يوم واحد",
    "horizon_days_3": "3 أيام",
    "horizon_days_5": "5 أيام",
    "horizon_weeks_1": "أسبوع واحد",
    "horizon_weeks_2": "أسبوعان",
    "horizon_weeks_4": "4 أسابيع",
    "horizon_months_1": "شهر واحد",
    "horizon_months_3": "3 أشهر",
    "horizon_months_6": "6 أشهر",
    "chart_all": "الكل",
    "forecast_horizon": "أفق التوقع",
    "horizon_1": "يوم",
    "horizon_5": "أسبوع",
    "horizon_21": "شهر",
    "forecast_title": "تقدير تجريبي خلال {horizon}",
    "forecast_current_price": "آخر سعر إغلاق معروف",
    "forecast_price": "سعر الإغلاق المتوقع · {horizon}",
    "forecast_change": "الفرق المتوقع بين السعرين",
    "forecast_chart_title": "سعر الإغلاق حسب التاريخ",
    "forecast_chart_history": "أسعار الإغلاق التاريخية",
    "forecast_chart_prediction": "سعر الإغلاق المتوقع",
    "chart_close_price": "سعر الإغلاق",
    "forecast_chart_note": "التاريخ المستقبلي تقريبي وقد تتغير مواعيد العطلات الرسمية.",
    "forecast_method_note": (
        "يتوقع السعر عند الإغلاق خلال {horizon} مباشرةً اعتمادًا على الأسعار والمؤشرات التاريخية. "
        "الأسبوع 5 جلسات تداول والشهر 21 جلسة؛ التوقعات الأطول ليست مجموع توقعات يومية."
    ),
    "forecast_description_horizon": (
        "يقدّر النموذج مباشرة العائد بين آخر إغلاق والإغلاق بعد {horizon}. "
        "الأسبوع يساوي 5 جلسات تداول والشهر 21 جلسة. النتائج تجريبية."
    ),
    "conclusion_forecast": "يقدّر نموذج <b>{model}</b> العائد خلال {horizon} بـ <b>{change:+.2f}%</b>، وسعر الإغلاق المتوقع بـ <b>${price:,.2f}</b>.",
})

TEXT["en"].update({
    "margin_trend":"Profit margin", "data_sources_note":"Sources: Yahoo Finance for prices and company data; Yahoo Finance, Google News RSS and optional NewsAPI for headlines. FinBERT labels article text; price-derived technical indicators are calculated locally.",
    "interval_50":"Indicative 50% range", "interval_90":"Indicative 90% range", "probability_up":"Up / down probability",
    "probability_pair":"Empirical share of walk-forward residuals that imply an outcome above or below zero for this forecast.",
    "forecast_interval_note":"Ranges use finite-sample conformal order statistics calibrated on walk-forward residuals. Because market errors are time-dependent, coverage is approximate rather than guaranteed.",
    "forecast_drivers":"Largest local forecast drivers", "forecast_feature":"Model input", "forecast_effect":"Estimated local effect on return", "forecast_drivers_missing":"Local feature effects are unavailable for this model. No explanation is fabricated.",
    "effect_up":"pushes up", "effect_down":"pushes down", "effect_neutral":"little directional effect", "experimental_forecast_label":"Experimental, not financial advice.",
})
TEXT["fr"].update({
    "margin_trend":"Marge bénéficiaire", "data_sources_note":"Sources : Yahoo Finance pour les cours et données d’entreprise; Yahoo Finance, Google News RSS et NewsAPI facultatif pour les actualités. FinBERT classe les textes; les indicateurs techniques sont calculés localement.",
    "interval_50":"Plage indicative à 50 %", "interval_90":"Plage indicative à 90 %", "probability_up":"Probabilité hausse / baisse",
    "probability_pair":"Part empirique des erreurs de validation chronologique qui donnent un résultat supérieur ou inférieur à zéro pour cette prévision.",
    "forecast_interval_note":"Les plages utilisent des quantiles conformes en échantillon fini, calibrés sur les résidus de validation chronologique. Comme les erreurs de marché sont dépendantes dans le temps, la couverture reste approximative et non garantie.",
    "forecast_drivers":"Principaux facteurs locaux de la prévision", "forecast_feature":"Entrée du modèle", "forecast_effect":"Effet local estimé sur le rendement", "forecast_drivers_missing":"Les effets locaux ne sont pas disponibles pour ce modèle; aucune explication n’est inventée.",
    "effect_up":"pousse à la hausse", "effect_down":"pousse à la baisse", "effect_neutral":"peu d’effet directionnel", "experimental_forecast_label":"Experimental, not financial advice.",
})
TEXT["ar"].update({
    "margin_trend":"هامش الربح", "data_sources_note":"المصادر: Yahoo Finance للأسعار وبيانات الشركات؛ وYahoo Finance وGoogle News RSS وNewsAPI الاختياري للأخبار. يصنف FinBERT النصوص؛ وتحسب المؤشرات الفنية محليًا.",
    "interval_50":"النطاق الإرشادي 50٪", "interval_90":"النطاق الإرشادي 90٪", "probability_up":"احتمال الصعود / الهبوط",
    "probability_pair":"النسبة التجريبية لأخطاء التحقق الزمني التي تعطي نتيجة أعلى أو أقل من الصفر لهذا التوقع.",
    "forecast_interval_note":"تستخدم النطاقات إحصاءات conformal لعينة محدودة، معايرة ببواقي التحقق الزمني. وبسبب اعتماد أخطاء السوق على الزمن، فالتغطية تقريبية وغير مضمونة.",
    "forecast_drivers":"أبرز العوامل المحلية للتوقع", "forecast_feature":"مدخل النموذج", "forecast_effect":"الأثر المحلي المقدر على العائد", "forecast_drivers_missing":"الآثار المحلية غير متاحة لهذا النموذج؛ لا يتم اختلاق تفسير.",
    "effect_up":"يدفع للصعود", "effect_down":"يدفع للهبوط", "effect_neutral":"تأثير اتجاهي محدود", "experimental_forecast_label":"توقع تجريبي، وليس نصيحة مالية.",
})

TEXT["en"].update({
    "sentiment_scale_note":"Score scale: −1 (negative) to +1 (positive). Recency and source quality affect each article's weight; non-English headlines receive a lower weight.",
    "news_price_context":"Share price · past 30 days", "sentiment_trend":"Sentiment trend · past 30 days", "sentiment_scale":"Score (−1 to +1)", "top_headlines":"Headlines with the largest score impact",
})
TEXT["fr"].update({
    "sentiment_scale_note":"Échelle : −1 (négatif) à +1 (positif). La récence et la qualité de la source pondèrent les articles; les titres non anglais reçoivent un poids réduit.",
    "news_price_context":"Cours de l’action · 30 derniers jours", "sentiment_trend":"Évolution du sentiment · 30 derniers jours", "sentiment_scale":"Score (−1 à +1)", "top_headlines":"Titres ayant le plus d’influence sur le score",
})
TEXT["ar"].update({
    "sentiment_scale_note":"المقياس: −1 (سلبي) إلى +1 (إيجابي). يؤثر حداثة الخبر وجودة المصدر في وزنه؛ وتحصل العناوين بغير الإنجليزية على وزن أقل.",
    "news_price_context":"سعر السهم · آخر 30 يومًا", "sentiment_trend":"اتجاه المعنويات · آخر 30 يومًا", "sentiment_scale":"الدرجة (−1 إلى +1)", "top_headlines":"العناوين الأكثر تأثيرًا في الدرجة",
})

TEXT["en"].update({
    "technical_grade":"Distance grade", "not_applicable":"Context only",
    "technical_graded_explanation":"Calculation: the available readings for price versus SMA20/50/200, MACD versus its signal, and RSI momentum are graded continuously (0–100) and averaged equally to {score}/100. Unavailable readings are excluded; RSI zones and ATR/support/resistance are shown as context.",
    "tech_price_sma20":"Price vs SMA 20", "tech_price_sma50":"Price vs SMA 50", "tech_price_sma200":"Price vs SMA 200",
    "tech_macd_signal":"MACD vs signal line", "tech_rsi":"RSI momentum and zone", "tech_adx":"ADX trend strength and direction",
    "tech_bollinger":"Bollinger position", "tech_volume":"Volume confirmation", "tech_high52":"Distance from 52-week high",
    "tech_levels":"20-session support / resistance", "tech_atr":"ATR · volatility context",
    "rsi_oversold":"oversold", "rsi_neutral":"neutral zone", "rsi_overbought":"overbought",
    "chart_sma200":"SMA 200", "golden_cross":"Bullish SMA crossover", "death_cross":"Bearish SMA crossover", "macd_signal_name":"MACD signal",
})
TEXT["fr"].update({
    "technical_grade":"Note selon l’écart au seuil", "not_applicable":"Contexte seulement",
    "technical_graded_explanation":"Calcul : les valeurs disponibles du cours par rapport aux MM20/50/200, du MACD par rapport à son signal et du momentum RSI sont notées progressivement (0–100), puis moyennées à poids égal : {score}/100. Les valeurs manquantes sont exclues; zones RSI et ATR/supports/résistances servent de contexte.",
    "tech_price_sma20":"Cours vs MM 20", "tech_price_sma50":"Cours vs MM 50", "tech_price_sma200":"Cours vs MM 200",
    "tech_macd_signal":"MACD vs ligne de signal", "tech_rsi":"Momentum RSI et zone", "tech_adx":"Force ADX et direction",
    "tech_bollinger":"Position dans les bandes de Bollinger", "tech_volume":"Confirmation par le volume", "tech_high52":"Écart au plus haut sur 52 semaines",
    "tech_levels":"Support / résistance sur 20 séances", "tech_atr":"ATR · contexte de volatilité",
    "rsi_oversold":"survente", "rsi_neutral":"zone neutre", "rsi_overbought":"surachat",
    "chart_sma200":"MM 200 séances", "golden_cross":"Croisement haussier MM", "death_cross":"Croisement baissier MM", "macd_signal_name":"Signal MACD",
})
TEXT["ar"].update({
    "technical_grade":"درجة حسب البعد عن المستوى", "not_applicable":"للسياق فقط",
    "technical_graded_explanation":"الحساب: تُقيّم القراءات المتاحة للسعر مقابل SMA20/50/200 وMACD مقابل إشارته وزخم RSI تدريجيًا (0–100)، ثم يُحسب متوسطها بالتساوي إلى {score}/100. تُستبعد القراءات غير المتاحة؛ ومناطق RSI وATR والدعم والمقاومة للسياق.",
    "tech_price_sma20":"السعر مقابل متوسط 20", "tech_price_sma50":"السعر مقابل متوسط 50", "tech_price_sma200":"السعر مقابل متوسط 200",
    "tech_macd_signal":"MACD مقابل خط الإشارة", "tech_rsi":"زخم RSI ومنطقته", "tech_adx":"قوة ADX واتجاهه",
    "tech_bollinger":"الموقع ضمن نطاق بولينجر", "tech_volume":"تأكيد الحجم", "tech_high52":"البعد عن أعلى سعر خلال 52 أسبوعًا",
    "tech_levels":"دعم / مقاومة 20 جلسة", "tech_atr":"ATR · سياق التقلب",
    "rsi_oversold":"تشبع بيعي", "rsi_neutral":"منطقة محايدة", "rsi_overbought":"تشبع شرائي",
    "chart_sma200":"متوسط 200 جلسة", "golden_cross":"تقاطع متوسطات صعودي", "death_cross":"تقاطع متوسطات هبوطي", "macd_signal_name":"إشارة MACD",
})

# Fundamental-analysis labels and explanations for graded metric scoring.
TEXT["en"].update({
    "pb":"Price-to-book", "ev_ebitda":"EV/EBITDA", "dcf_mos":"DCF margin of safety",
    "roic":"Return on invested capital", "debt_equity":"Debt to equity", "current_ratio":"Current ratio",
    "interest_coverage":"Interest coverage", "metric_grade":"Metric grade", "metric_weight":"Weight",
    "data_warning":"Data warning", "metric_missing_warning":"Metric unavailable; excluded from weighted score.",
    "peer_percentile":"percentile", "heuristic_score":"heuristic (no peer data)",
    "peer_data_unavailable":"Sector peer data was not supplied, so metric grades use disclosed smooth heuristics rather than a fabricated percentile.",
    "fundamental_weighted_explanation":"Calculation: weighted average of {available}/{total} available metric grades = {score}/100, renormalized across {weight:.0f}% of the configured weights. Each row shows its metric weight; unavailable values are flagged and excluded.",
    "dcf_unreliable":"DCF is omitted or unreliable for banks and companies with non-positive free cash flow; other valuation and financial metrics carry the score.",
    "fundamental_quarter":"Latest reported quarter available: {quarter}. Quarter end is not necessarily the publication date.",
    "fundamental_trends":"Financial trends (3–5 years where available)", "trend_metric":"Trend", "trend_value":"Change across available periods",
    "revenue_trend":"Revenue", "earnings_trend":"Earnings", "fcf_trend":"Free cash flow",
})
TEXT["fr"].update({
    "pb":"Cours / valeur comptable", "ev_ebitda":"VE/EBITDA", "dcf_mos":"Marge de sécurité DCF",
    "roic":"Rendement du capital investi", "debt_equity":"Dette / capitaux propres", "current_ratio":"Ratio de liquidité générale",
    "interest_coverage":"Couverture des intérêts", "metric_grade":"Note de l’indicateur", "metric_weight":"Poids",
    "data_warning":"Avertissement sur les données", "metric_missing_warning":"Indicateur indisponible; exclu du score pondéré.",
    "peer_percentile":"percentile", "heuristic_score":"heuristique (sans données de pairs)",
    "peer_data_unavailable":"Les données de pairs sectoriels ne sont pas fournies : les notes utilisent des heuristiques progressives explicites, sans inventer de percentile.",
    "fundamental_weighted_explanation":"Calcul : moyenne pondérée de {available}/{total} notes disponibles = {score}/100, renormalisée sur {weight:.0f}% des poids configurés. Chaque ligne indique son poids; les valeurs manquantes sont signalées et exclues.",
    "dcf_unreliable":"Le DCF est omis ou peu fiable pour les banques et les entreprises dont le flux de trésorerie disponible est nul ou négatif; les autres indicateurs déterminent le score.",
    "fundamental_quarter":"Dernier trimestre publié disponible : {quarter}. La fin de trimestre n’est pas nécessairement la date de publication.",
    "fundamental_trends":"Tendances financières (3 à 5 ans selon les données disponibles)", "trend_metric":"Tendance", "trend_value":"Variation sur les périodes disponibles",
    "revenue_trend":"Chiffre d’affaires", "earnings_trend":"Résultat net", "fcf_trend":"Flux de trésorerie disponible",
})
TEXT["ar"].update({
    "pb":"السعر إلى القيمة الدفترية", "ev_ebitda":"قيمة المنشأة / EBITDA", "dcf_mos":"هامش الأمان وفق DCF",
    "roic":"العائد على رأس المال المستثمر", "debt_equity":"الدين إلى حقوق الملكية", "current_ratio":"نسبة التداول",
    "interest_coverage":"تغطية الفوائد", "metric_grade":"درجة المؤشر", "metric_weight":"الوزن",
    "data_warning":"تنبيه البيانات", "metric_missing_warning":"المؤشر غير متاح؛ استُبعد من الدرجة الموزونة.",
    "peer_percentile":"المئين", "heuristic_score":"تقدير إرشادي (دون بيانات نظراء)",
    "peer_data_unavailable":"لم تُوفّر بيانات نظراء القطاع؛ لذلك تستخدم الدرجات تقديرات إرشادية معلنة بدل اختلاق ترتيب مئيني.",
    "fundamental_weighted_explanation":"الحساب: متوسط موزون لـ {available} من {total} مؤشرات متاحة = {score}/100، مع إعادة توزيع الأوزان على {weight:.0f}% من الأوزان المحددة. يظهر وزن كل مؤشر؛ وتُعلّم القيم المفقودة وتُستبعد.",
    "dcf_unreliable":"يُستبعد DCF أو لا يُعتمد عليه للبنوك والشركات ذات التدفق النقدي الحر غير الموجب؛ وتُستخدم بقية المؤشرات.",
    "fundamental_quarter":"أحدث ربع مالي متاح: {quarter}. نهاية الربع ليست بالضرورة تاريخ نشر النتائج.",
    "fundamental_trends":"الاتجاهات المالية (3 إلى 5 سنوات حسب التوفر)", "trend_metric":"الاتجاه", "trend_value":"التغير خلال الفترات المتاحة",
    "revenue_trend":"الإيرادات", "earnings_trend":"الأرباح", "fcf_trend":"التدفق النقدي الحر",
})

TEXT["fr"].update({
    "signal_status": "Signal",
    "included_in_score": "Dans le score",
    "informational": "Informatif",
    "yes": "Oui",
    "no": "Non",
    "fund_score_method": (
        "Calcul : {passed}/{available} critères validés = {score}/100. Chaque critère disponible a le même poids; les données manquantes sont exclues. "
        "Critères : croissance du chiffre d’affaires > 0, marge > 0, ROE > 0, flux de trésorerie disponible > 0 et P/E entre 0 et 25. "
        "Positif dès 60, neutre de 40 à 59, négatif sous 40. Les lignes non incluses sont informatives."
    ),
    "technical_criterion": "Critère technique",
    "technical_reading": "Valeurs récentes",
    "tech_close_sma20": "Clôture au-dessus de la moyenne 20 séances",
    "tech_sma20_sma50": "Moyenne 20 séances au-dessus de la moyenne 50 séances",
    "tech_macd_signal": "MACD vs ligne de signal",
    "tech_rsi_band": "RSI dans la zone 30–70",
    "technical_score_method": (
        "Calcul : {passed}/{available} critères validés = {score}/100; poids égal et critères indisponibles exclus. "
        "Les critères sont clôture > MM20, MM20 > MM50, MACD > signal et RSI entre 30 et 70. "
        "Haussier dès 60, neutre de 40 à 59, baissier sous 40. Les libellés montrent si le critère passe, pas une certitude sur le cours."
    ),
})

TEXT["en"].update({
    "signal_status": "Signal",
    "included_in_score": "In score",
    "informational": "Info only",
    "yes": "Yes",
    "no": "No",
    "fund_score_method": (
        "Calculation: {passed}/{available} criteria passed = {score}/100. Each available criterion has equal weight; missing data is excluded. "
        "Criteria: revenue growth > 0, profit margin > 0, ROE > 0, free cash flow > 0, and P/E between 0 and 25. "
        "Positive at 60+, neutral from 40 to 59, negative below 40. Rows not included in the score are informational."
    ),
    "technical_criterion": "Technical criterion",
    "technical_reading": "Latest reading(s)",
    "tech_close_sma20": "Close above 20-session average",
    "tech_sma20_sma50": "20-session average above 50-session average",
    "tech_macd_signal": "MACD vs signal line",
    "tech_rsi_band": "RSI within the 30–70 band",
    "technical_score_method": (
        "Calculation: {passed}/{available} criteria passed = {score}/100; equal weight, unavailable criteria excluded. "
        "The checks are close > SMA20, SMA20 > SMA50, MACD > signal, and RSI between 30 and 70. "
        "Bullish at 60+, neutral from 40 to 59, bearish below 40. Labels show whether a rule passed, not certainty about future price."
    ),
})

TEXT["ar"].update({
    "signal_status": "الإشارة",
    "included_in_score": "ضمن الدرجة",
    "informational": "للمعلومات فقط",
    "yes": "نعم",
    "no": "لا",
    "fund_score_method": (
        "الحساب: اجتياز {passed} من {available} معايير = {score}/100. لكل معيار متاح وزن متساوٍ، وتُستبعد البيانات الناقصة. "
        "المعايير: نمو الإيرادات > 0، هامش الربح > 0، ROE > 0، التدفق النقدي الحر > 0، ونسبة P/E بين 0 و25. "
        "إيجابي عند 60 فأكثر، محايد من 40 إلى 59، وسلبي دون 40. الصفوف غير الداخلة في الدرجة للمعلومات فقط."
    ),
    "technical_criterion": "المعيار الفني",
    "technical_reading": "أحدث القيم",
    "tech_close_sma20": "الإغلاق أعلى من متوسط 20 جلسة",
    "tech_sma20_sma50": "متوسط 20 جلسة أعلى من متوسط 50 جلسة",
    "tech_macd_signal": "MACD مقابل خط الإشارة",
    "tech_rsi_band": "RSI ضمن نطاق 30–70",
    "technical_score_method": (
        "الحساب: اجتياز {passed} من {available} معايير = {score}/100، بأوزان متساوية مع استبعاد غير المتاح. "
        "المعايير: الإغلاق > SMA20، وSMA20 > SMA50، وMACD > الإشارة، وRSI بين 30 و70. "
        "صعودي عند 60 فأكثر، محايد من 40 إلى 59، وهبوطي دون 40. اجتياز المعيار لا يضمن اتجاه السعر."
    ),
})

TEXT["en"].update({
    "combined_verdict":"Combined three-pillar verdict", "verdict_signal":"Overall signal", "verdict_score":"Combined score", "verdict_confidence":"Score strength", "verdict_confidence_help":"Distance of the combined score from neutral, not a probability of being right.",
    "verdict_method":"Weights: {source}. Available historical snapshots: {history}. Contributions (score points): {parts}.", "weights_default":"default 40% fundamentals / 40% technical / 20% sentiment", "weights_learned":"learned from dated snapshots after outperforming default weights on a later validation period",
    "pillar_fundamental":"Fundamentals", "pillar_technical":"Technical", "pillar_sentiment":"Sentiment",
    "evaluation_always_up":"Always-up baseline", "evaluation_sma_baseline":"20-session moving-average baseline", "evaluation_samples":"Test samples", "evaluation_backtest":"Walk-forward backtest · long or cash", "backtest_sharpe":"Sharpe ratio", "backtest_drawdown":"Maximum drawdown", "backtest_win_rate":"Win rate", "backtest_costs":"Assumed trading cost: {fees} bps fees + {slippage} bps slippage per position change. Long-only when the model signal is up; otherwise cash.", "known_limitations":"Known limitations", "known_limitations_text":"Public data can be incomplete and revised. Historical ML pillar features come only from daily snapshots captured by this app at the time; fiscal period-end values are not backfilled. The provider does not supply a complete official release-date history, so timing and later vendor revisions remain limitations. Heuristic fundamental grades are not sector rankings unless peer observations are supplied. DCF assumptions are simplified. This short sample backtest excludes taxes, dividends, liquidity effects and market impact; past results do not predict future performance.", "global_disclaimer":"Educational, experimental analysis only. Not financial advice.",
})
TEXT["fr"].update({
    "combined_verdict":"Verdict combiné des trois piliers", "verdict_signal":"Signal global", "verdict_score":"Score combiné", "verdict_confidence":"Force du score", "verdict_confidence_help":"Écart du score combiné par rapport à la neutralité; ce n’est pas une probabilité de réussite.",
    "verdict_method":"Poids : {source}. Historique daté disponible : {history}. Contributions (points de score) : {parts}.", "weights_default":"par défaut : 40 % fondamentaux / 40 % technique / 20 % sentiment", "weights_learned":"appris à partir d’instantanés datés après avoir dépassé les poids par défaut sur une période de validation ultérieure",
    "pillar_fundamental":"Fondamentaux", "pillar_technical":"Technique", "pillar_sentiment":"Sentiment",
    "evaluation_always_up":"Référence toujours en hausse", "evaluation_sma_baseline":"Référence moyenne mobile 20 séances", "evaluation_samples":"Échantillons de test", "evaluation_backtest":"Backtest chronologique · position longue ou liquidités", "backtest_sharpe":"Ratio de Sharpe", "backtest_drawdown":"Perte maximale (drawdown)", "backtest_win_rate":"Taux de trades gagnants", "backtest_costs":"Coûts supposés : {fees} pb de frais + {slippage} pb de glissement à chaque changement de position. Position longue si le signal monte, sinon liquidités.", "known_limitations":"Limites connues", "known_limitations_text":"Les caractéristiques historiques des trois piliers proviennent uniquement d’instantanés journaliers capturés par l’application au moment de leur collecte; les valeurs de fin de période ne sont pas rétrodatées. Le fournisseur ne donne pas l’historique officiel complet des dates de publication; le moment exact et les révisions restent donc des limites. Les données publiques peuvent manquer ou être révisées. Sans données de pairs, les notes fondamentales heuristiques ne sont pas des classements sectoriels. Le DCF est simplifié. Ce backtest court exclut impôts, dividendes, liquidité et impact de marché; les résultats passés ne prédisent pas ceux du futur.", "global_disclaimer":"Analyse pédagogique et expérimentale uniquement. Ceci n’est pas un conseil financier.",
})
TEXT["ar"].update({
    "combined_verdict":"الخلاصة المجمعة للمحاور الثلاثة", "verdict_signal":"الإشارة العامة", "verdict_score":"الدرجة المجمعة", "verdict_confidence":"قوة الدرجة", "verdict_confidence_help":"مدى ابتعاد الدرجة المجمعة عن الحياد؛ ليست احتمالًا لصحة التوقع.",
    "verdict_method":"الأوزان: {source}. اللقطات التاريخية المؤرخة: {history}. المساهمات (نقاط الدرجة): {parts}.", "weights_default":"افتراضيًا: 40٪ أساسيات / 40٪ فني / 20٪ معنويات", "weights_learned":"تُعلّمت من لقطات مؤرخة بعد تفوقها على الأوزان الافتراضية في فترة تحقق لاحقة",
    "pillar_fundamental":"الأساسيات", "pillar_technical":"الفني", "pillar_sentiment":"المعنويات",
    "evaluation_always_up":"مرجع الصعود الدائم", "evaluation_sma_baseline":"مرجع المتوسط المتحرك لـ20 جلسة", "evaluation_samples":"عينات الاختبار", "evaluation_backtest":"اختبار زمني · شراء أو نقد", "backtest_sharpe":"نسبة شارب", "backtest_drawdown":"أقصى تراجع", "backtest_win_rate":"معدل الصفقات الرابحة", "backtest_costs":"التكلفة المفترضة: {fees} نقطة أساس رسوم + {slippage} نقطة أساس انزلاق لكل تغيير في المركز. شراء عند إشارة الصعود وإلا نقد.", "known_limitations":"القيود المعروفة", "known_limitations_text":"تأتي ميزات الأعمدة التاريخية فقط من لقطات يومية سجلها التطبيق وقت جمعها؛ ولا تُعاد كتابة قيم نهاية الفترات على تواريخ سابقة. لا يوفر المصدر تاريخًا رسميًا كاملًا للنشر، لذلك يبقى التوقيت ومراجعات البيانات قيودًا. قد تكون البيانات العامة ناقصة أو معدلة. دون بيانات نظراء، لا تمثل الدرجات الإرشادية ترتيبًا قطاعيًا. افتراضات DCF مبسطة. يستبعد الاختبار القصير الضرائب والتوزيعات والسيولة وأثر السوق؛ النتائج السابقة لا تتنبأ بالمستقبل.", "global_disclaimer":"تحليل تعليمي وتجريبي فقط. لا يمثل نصيحة مالية.",
})

def t(lang, key, **values):
    language_text = TEXT.get(lang, {})
    english_fallback = TEXT.get("en", {})
    text = language_text.get(key, english_fallback.get(key, TEXT["fr"].get(key, key)))
    return text.format(**values) if values else text
