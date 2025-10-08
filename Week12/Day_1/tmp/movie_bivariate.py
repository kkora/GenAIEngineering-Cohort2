import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
url = 'https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv'
data = pd.read_csv(url)

# Function for Bivariate & Multivariate Analysis

def bivariate_multivariate_analysis(data):
    # Correlation matrix heatmap for numerical variables only
    numerical_data = data[['Rating', 'Year', 'Revenue (Millions)', 'Metascore', 'Runtime (Minutes)']]
    plt.figure(figsize=(10, 8))
    corr_matrix = numerical_data.corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix Heatmap')
    plt.savefig('correlation_matrix_heatmap.png')

    # Rating vs Revenue scatter plot with trend line
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=data, x='Revenue (Millions)', y='Rating')
    sns.regplot(data=data, x='Revenue (Millions)', y='Rating', scatter=False, color='red')
    plt.title('Rating vs Revenue Scatter Plot')
    plt.savefig('rating_vs_revenue_scatter.png')

    # Genre vs Rating box plots
    plt.figure(figsize=(14, 8))
    genres = data['Genre'].str.split(',', expand=True).stack().reset_index(level=1, drop=True)
    sns.boxplot(x=genres, y=data['Rating'], order=genres.value_counts().index)
    plt.xticks(rotation=90)
    plt.title('Genre vs Rating Box Plot')
    plt.savefig('genre_vs_rating_boxplot.png')

    # Director performance analysis
    director_rating = data.groupby('Director')['Rating'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=director_rating.values, y=director_rating.index, palette='viridis')
    plt.title('Top 10 Directors by Average Rating')
    plt.xlabel('Average Rating')
    plt.savefig('top_directors_ratings.png')

bivariate_multivariate_analysis(data)