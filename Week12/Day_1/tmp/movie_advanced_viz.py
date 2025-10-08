import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
url = 'https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv'
data = pd.read_csv(url)

# Function for Advanced Visualizations

def advanced_visualizations(data):
    # Top 20 highest-rated movies
    top_rated_movies = data.nlargest(20, 'Rating')[['Title', 'Rating']].set_index('Title')
    plt.figure(figsize=(12, 8))
    top_rated_movies.sort_values('Rating', ascending=True).plot(kind='barh', color='skyblue')
    plt.title('Top 20 Highest-Rated Movies')
    plt.xlabel('Rating')
    plt.savefig('top_20_highest_rated_movies.png')

    # Top 20 highest-grossing movies
    top_grossing_movies = data.nlargest(20, 'Revenue (Millions)')[['Title', 'Revenue (Millions)']].set_index('Title')
    plt.figure(figsize=(12, 8))
    top_grossing_movies.sort_values('Revenue (Millions)', ascending=True).plot(kind='barh', color='salmon')
    plt.title('Top 20 Highest-Grossing Movies')
    plt.xlabel('Revenue (Millions)')
    plt.savefig('top_20_highest_grossing_movies.png')

    # Genre popularity over time
    data['Decade'] = (data['Year'] // 10) * 10
    plt.figure(figsize=(14, 8))
    genre_popularity = data.groupby(['Decade', 'Genre']).size().unstack().fillna(0)
    genre_popularity.plot.area(stacked=True, colormap='tab20', alpha=0.7)
    plt.title('Genre Popularity Over Time')
    plt.xlabel('Decade')
    plt.ylabel('Number of Movies')
    plt.savefig('genre_popularity_over_time.png')

    # Rating distribution by decade
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='Decade', y='Rating', data=data, palette='Blues')
    plt.title('Rating Distribution by Decade')
    plt.savefig('rating_distribution_by_decade.png')

    # Revenue vs Rating colored by genre
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=data, x='Revenue (Millions)', y='Rating', hue='Genre', alpha=0.6, palette='tab10')
    plt.title('Revenue vs Rating Colored by Genre')
    plt.savefig('revenue_vs_rating_genre.png')

advanced_visualizations(data)