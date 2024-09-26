# VictorVis (VictoryVision)

Chace Snedecor, Dana Fulmer, Shayne Powell, Spencer Buck,

## Description

This project focuses on predicting match winners in esports by analyzing player ratings from HLTV and team-level data. While our goal was to predict match outcomes using match data with individual player and team statistics, we had to adapt our approach due to data limitations. Instead of relying on match results, we used player and team statistics only as proxies to forecast match outcomes by predicting which player or team would perform better based on their predicted rating driven by their stats.

**Key Questions Addressed:**

1. **Use Rankings as a Proxy for Match Outcomes**  
   **Assumption:** Higher-ranked players or teams are more likely to win against lower-ranked ones.  
   **Application:** We used player ratings and team data as proxies for predicting match outcomes. Our models leveraged differences in player and team rankings HLTV ratings to predict player ranks.

2. **Which Player or Team Statistics Are the Most Significant Predictors of Performance Rankings?**  
   **Objective:** Identify the key statistics that most strongly correlate with HLTV rankings.  
   **Answer:** Our analysis showed that key stats such as kills per round, damage per round, headshot percentage, and player impact ratings were the most significant predictors of performance. Random Forest and XGBoost models highlighted these metrics as strong indicators of player ratings and match outcomes.

3. **How Do Differences in Key Statistics Between Players or Teams Affect Their Likelihood of Winning?**  
   **Objective:** Analyze how disparities in specific stats influence match outcomes.  
   **Answer:** We found that larger disparities in key stats, especially kills and damage per round, increased the likelihood of a player or team winning. Our models used these differences to predict match winners by analyzing the impact of stronger performance metrics on the likelihood of victory.

4. **Can We Develop a Composite Scoring System That Effectively Ranks Players or Teams?**  
   **Objective:** Create an alternative ranking system based on weighted stats.  
   **Answer:** While we didn't fully develop a composite scoring system, our machine learning models provided insights into how different stats could be weighted to predict match outcomes. Feature importance values from the models effectively created an internal ranking system based on player and team performance.

5. **How Do Biographical Factors (e.g., Age, Country) Influence Performance and Rankings?**  
   **Objective:** Examine the impact of non-statistical factors on player success.  
   **Answer:** Although we initially wanted to explore biographical factors like age and country, due to some issues with processing age ranges and country, this factor was excluded from the final models. However, future analysis with cleaner data could provide more insights.

6. **What Statistical Differences Distinguish Top-Tier Players/Teams from Lower-Tier Ones?**  
   **Objective:** Identify the key factors that set elite players/teams apart.  
   **Answer:** The main differences between top-tier and lower-tier players were identified through metrics like kills per round, headshot percentage, and damage dealt per round. These stats were key to distinguishing elite performers from average ones, which was crucial in our model predictions.


## Usage

1. Open the following notebooks in the provided order:
   - **DataCleaning.ipynb**: Covers data cleaning and preprocessing, including handling inconsistencies in player and team data.
   - **ExploreData.ipynb**: Perform exploratory data analysis and feature selection for both player ratings and team-level data.
   - **ModelTime.ipynb**: Initial modeling process where we built prediction models (Random Forest, Linear Regression, XGBoost) to analyze player ratings and predict match winners based on player and team data.
   - **Optimization.ipynb**: Further optimizes the models using XGBoost and tuned hyperparameters to improve accuracy in predicting match outcomes.

2. The notebooks provide detailed steps for how the data was processed. Visualizations and tables summarize the features that had the greatest impact on predicting match outcomes.

## Credits

Special thanks to the HLTV API and GRID API (despite delayed access to GRID) for providing the player and team data necessary for this project. Thanks also to various machine learning resources that guided the project’s development including Claude and ChatGPT.

## Badges
![Python version](https://img.shields.io/badge/python-3.x-blue)

## Features

- Analyze player ratings based on individual statistics.
- Use machine learning models (Random Forest, XGBoost) to predict match winners based on player ratings and team performance.
- Feature importance analysis shows which individual stats have the largest impact on predicting match results.

## Tests

We evaluated and tested the following machine learning algorithms to predict match outcomes:
- **Linear Regression:** Tested as a baseline to understand the relationship between individual stats, team stats, and player ratings.
- **Random Forest:** Used to manage the complexity of both player and team data, as it handles non-linear relationships and provides feature importance.
- **XGBoost:** Optimized for handling complex, hierarchical datasets that include both player- and team-level variables, yielding more accurate predictions for match outcomes.

While Random Forest provided a solid baseline, **XGBoost** emerged as the most accurate model after optimization. Future plans include combining models (e.g., Random Forest and XGBoost) to enhance the prediction accuracy of match winners.