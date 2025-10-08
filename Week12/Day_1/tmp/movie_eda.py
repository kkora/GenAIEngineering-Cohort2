import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

# Load the dataset
url = 'https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv'
data = pd.read_csv(url)

# Function for Univariate Analysis

def univariate_analysis(data):
    # Distribution of movie ratings
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 3, 1)
    sns.histplot(data['Rating'].dropna(), kde=True)
    plt.title('Distribution of Movie Ratings')

    plt.subplot(1, 3, 2)
    sns.boxplot(x=data['Rating'].dropna())
    plt.title('Box Plot of Movie Ratings')

    plt.subplot(1, 3, 3)
    sns.violinplot(x=data['Rating'].dropna())
    plt.title('Violin Plot of Movie Ratings')
    plt.savefig('movie_rating_distribution.png')

    # Revenue distribution analysis
    plt.figure(figsize=(10, 5))
    sns.histplot(data['Revenue (Millions)'].dropna(), kde=True)
    plt.title('Distribution of Movie Revenue')
    plt.xlabel('Revenue in Millions')
    plt.savefig('revenue_distribution.png')

    # Genre frequency analysis
    plt.figure(figsize=(12, 6))
    genres = data['Genre'].str.split(',', expand=True).stack()
    sns.countplot(y=genres, order=genres.value_counts().index)
    plt.title('Frequency of Movie Genres')
    plt.savefig('genre_frequency.png')

    # Release year trends
    plt.figure(figsize=(10, 5))
    sns.histplot(data['Year'].dropna(), bins=len(data['Year'].unique()), kde=False)
    plt.title('Number of Movies Released Over the Years')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.savefig('year_trends.png')

    # Runtime distribution analysis
    plt.figure(figsize=(10, 5))
    sns.histplot(data['Runtime (Minutes)'].dropna(), kde=True)
    plt.title('Distribution of Movie Runtimes')
    plt.xlabel('Runtime (Minutes)')
    plt.savefig('runtime_distribution.png')

univariate_analysis(data)