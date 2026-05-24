# Data Analysis Skill

## Repo patterns
- Libraries: pandas, matplotlib, seaborn, numpy
- Existing analyses: Titanic (`titanic.py`), PCA (`pca.py`), Customer Churn, Kidney Disease
- Visualization: candlestick charts (`candlestick_chart.py`), standard seaborn plots

## Standard EDA sequence
1. `df.shape`, `df.dtypes`, `df.head()`
2. `df.isnull().sum()` — check for missing values
3. `df.duplicated().sum()` — check for duplicates
4. `df.describe()` — summary statistics for numeric columns
5. Value counts for categorical columns
6. Correlation heatmap for numeric features

## Visualization defaults
- Use seaborn for statistical plots (distributions, heatmaps, pairplots)
- Use matplotlib for custom or composite figures
- Always label axes with units; always add a title
- Use `figsize=(10, 6)` as default unless layout requires otherwise
- Save figures with `plt.tight_layout()` before `plt.savefig()`

## Data cleaning practices
- Impute missing values deliberately — document the strategy (median, mean, mode, forward-fill)
- Drop duplicates only after inspecting them
- Encode categoricals explicitly: prefer `pd.get_dummies` for low-cardinality, `LabelEncoder` for ordinal
- Never silently drop rows — log what was removed and why

## Feature engineering
- Document each new feature with a one-line comment explaining the business logic
- Check for multicollinearity before feeding to linear models (VIF or correlation matrix)
