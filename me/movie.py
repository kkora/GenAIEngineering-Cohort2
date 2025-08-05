import sqlite3
from datetime import datetime
import os

class MoviesDB:
    def __init__(self, db_name="movies.db"):
        """Initialize the database connection and create tables"""
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create the movies database schema"""
        # Movies table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                release_year INTEGER,
                genre TEXT,
                director TEXT,
                rating REAL CHECK(rating >= 0 AND rating <= 10),
                duration_minutes INTEGER,
                budget INTEGER,
                box_office INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Actors table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS actors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                birth_year INTEGER,
                nationality TEXT
            )
        ''')
        
        # Movie-Actor relationship table (many-to-many)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS movie_actors (
                movie_id INTEGER,
                actor_id INTEGER,
                role TEXT,
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                FOREIGN KEY (actor_id) REFERENCES actors (id),
                PRIMARY KEY (movie_id, actor_id)
            )
        ''')
        
        self.conn.commit()
        print("Database tables created successfully!")
    
    def add_movie(self, title, release_year, genre, director, rating=None, 
                  duration_minutes=None, budget=None, box_office=None):
        """Add a new movie to the database"""
        self.cursor.execute('''
            INSERT INTO movies (title, release_year, genre, director, rating, 
                              duration_minutes, budget, box_office)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, release_year, genre, director, rating, 
              duration_minutes, budget, box_office))
        
        movie_id = self.cursor.lastrowid
        self.conn.commit()
        print(f"Movie '{title}' added with ID: {movie_id}")
        return movie_id
    
    def add_actor(self, name, birth_year=None, nationality=None):
        """Add a new actor to the database"""
        self.cursor.execute('''
            INSERT INTO actors (name, birth_year, nationality)
            VALUES (?, ?, ?)
        ''', (name, birth_year, nationality))
        
        actor_id = self.cursor.lastrowid
        self.conn.commit()
        print(f"Actor '{name}' added with ID: {actor_id}")
        return actor_id
    
    def link_movie_actor(self, movie_id, actor_id, role=None):
        """Link a movie with an actor"""
        self.cursor.execute('''
            INSERT OR IGNORE INTO movie_actors (movie_id, actor_id, role)
            VALUES (?, ?, ?)
        ''', (movie_id, actor_id, role))
        
        self.conn.commit()
        print(f"Linked movie ID {movie_id} with actor ID {actor_id}")
    
    def get_all_movies(self):
        """Get all movies from the database"""
        self.cursor.execute('''
            SELECT id, title, release_year, genre, director, rating, duration_minutes
            FROM movies 
            ORDER BY release_year DESC
        ''')
        return self.cursor.fetchall()
    
    def search_movies_by_genre(self, genre):
        """Search movies by genre"""
        self.cursor.execute('''
            SELECT title, release_year, director, rating
            FROM movies 
            WHERE genre LIKE ?
            ORDER BY rating DESC
        ''', (f'%{genre}%',))
        return self.cursor.fetchall()
    
    def search_movies_by_year_range(self, start_year, end_year):
        """Search movies within a year range"""
        self.cursor.execute('''
            SELECT title, release_year, genre, director, rating
            FROM movies 
            WHERE release_year BETWEEN ? AND ?
            ORDER BY release_year DESC
        ''', (start_year, end_year))
        return self.cursor.fetchall()
    
    def get_top_rated_movies(self, limit=10):
        """Get top-rated movies"""
        self.cursor.execute('''
            SELECT title, release_year, genre, director, rating
            FROM movies 
            WHERE rating IS NOT NULL
            ORDER BY rating DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_movies_with_actors(self):
        """Get movies along with their actors"""
        self.cursor.execute('''
            SELECT m.title, m.release_year, m.director, a.name, ma.role
            FROM movies m
            JOIN movie_actors ma ON m.id = ma.movie_id
            JOIN actors a ON ma.actor_id = a.id
            ORDER BY m.title, a.name
        ''')
        return self.cursor.fetchall()
    
    def get_actor_filmography(self, actor_name):
        """Get all movies for a specific actor"""
        self.cursor.execute('''
            SELECT m.title, m.release_year, m.genre, ma.role
            FROM movies m
            JOIN movie_actors ma ON m.id = ma.movie_id
            JOIN actors a ON ma.actor_id = a.id
            WHERE a.name LIKE ?
            ORDER BY m.release_year DESC
        ''', (f'%{actor_name}%',))
        return self.cursor.fetchall()
    
    def get_movies_by_director(self, director_name):
        """Get all movies by a specific director"""
        self.cursor.execute('''
            SELECT title, release_year, genre, rating, duration_minutes
            FROM movies 
            WHERE director LIKE ?
            ORDER BY release_year DESC
        ''', (f'%{director_name}%',))
        return self.cursor.fetchall()
    
    def get_movie_statistics(self):
        """Get basic statistics about the movie collection"""
        stats = {}
        
        # Total movies
        self.cursor.execute('SELECT COUNT(*) FROM movies')
        stats['total_movies'] = self.cursor.fetchone()[0]
        
        # Average rating
        self.cursor.execute('SELECT AVG(rating) FROM movies WHERE rating IS NOT NULL')
        avg_rating = self.cursor.fetchone()[0]
        stats['average_rating'] = round(avg_rating, 2) if avg_rating else None
        
        # Movies by decade
        self.cursor.execute('''
            SELECT (release_year / 10) * 10 as decade, COUNT(*) as count
            FROM movies 
            WHERE release_year IS NOT NULL
            GROUP BY decade
            ORDER BY decade DESC
        ''')
        stats['movies_by_decade'] = self.cursor.fetchall()
        
        # Top genres
        self.cursor.execute('''
            SELECT genre, COUNT(*) as count
            FROM movies 
            WHERE genre IS NOT NULL
            GROUP BY genre
            ORDER BY count DESC
            LIMIT 5
        ''')
        stats['top_genres'] = self.cursor.fetchall()
        
        return stats
    
    def update_movie_rating(self, movie_id, new_rating):
        """Update a movie's rating"""
        self.cursor.execute('''
            UPDATE movies 
            SET rating = ?
            WHERE id = ?
        ''', (new_rating, movie_id))
        
        if self.cursor.rowcount > 0:
            self.conn.commit()
            print(f"Updated movie ID {movie_id} rating to {new_rating}")
            return True
        else:
            print(f"No movie found with ID {movie_id}")
            return False
    
    def delete_movie(self, movie_id):
        """Delete a movie and its actor relationships"""
        # First delete the actor relationships
        self.cursor.execute('DELETE FROM movie_actors WHERE movie_id = ?', (movie_id,))
        
        # Then delete the movie
        self.cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        
        if self.cursor.rowcount > 0:
            self.conn.commit()
            print(f"Deleted movie ID {movie_id}")
            return True
        else:
            print(f"No movie found with ID {movie_id}")
            return False
    
    def close_connection(self):
        """Close the database connection"""
        self.conn.close()
        print("Database connection closed")

def main():
    """Example usage of the MoviesDB class"""
    # Initialize the database
    db = MoviesDB()
    
    print("=== Adding Sample Data ===")
    
    # Add some sample movies
    movie1_id = db.add_movie("The Shawshank Redemption", 1994, "Drama", "Frank Darabont", 9.3, 142)
    movie2_id = db.add_movie("The Dark Knight", 2008, "Action", "Christopher Nolan", 9.0, 152)
    movie3_id = db.add_movie("Pulp Fiction", 1994, "Crime", "Quentin Tarantino", 8.9, 154)
    movie4_id = db.add_movie("Inception", 2010, "Sci-Fi", "Christopher Nolan", 8.8, 148)
    
    # Add some actors
    actor1_id = db.add_actor("Morgan Freeman", 1937, "American")
    actor2_id = db.add_actor("Christian Bale", 1974, "British")
    actor3_id = db.add_actor("John Travolta", 1954, "American")
    actor4_id = db.add_actor("Leonardo DiCaprio", 1974, "American")
    
    # Link movies with actors
    db.link_movie_actor(movie1_id, actor1_id, "Ellis Boyd 'Red' Redding")
    db.link_movie_actor(movie2_id, actor2_id, "Bruce Wayne / Batman")
    db.link_movie_actor(movie3_id, actor3_id, "Vincent Vega")
    db.link_movie_actor(movie4_id, actor4_id, "Dom Cobb")
    
    print("\n=== Querying the Database ===")
    
    # Get all movies
    print("\n1. All Movies:")
    movies = db.get_all_movies()
    for movie in movies:
        print(f"   {movie[1]} ({movie[2]}) - {movie[3]} - Rating: {movie[5]}")
    
    # Search by genre
    print("\n2. Action Movies:")
    action_movies = db.search_movies_by_genre("Action")
    for movie in action_movies:
        print(f"   {movie[0]} ({movie[1]}) - {movie[2]} - Rating: {movie[3]}")
    
    # Get top-rated movies
    print("\n3. Top-Rated Movies:")
    top_movies = db.get_top_rated_movies(3)
    for movie in top_movies:
        print(f"   {movie[0]} ({movie[1]}) - Rating: {movie[4]}")
    
    # Get movies with actors
    print("\n4. Movies with Actors:")
    movies_actors = db.get_movies_with_actors()
    for entry in movies_actors:
        print(f"   {entry[0]} ({entry[1]}) - {entry[4]} played by {entry[3]}")
    
    # Get actor filmography
    print("\n5. Leonardo DiCaprio's Filmography:")
    filmography = db.get_actor_filmography("Leonardo DiCaprio")
    for movie in filmography:
        print(f"   {movie[0]} ({movie[1]}) - {movie[2]} as {movie[3]}")
    
    # Get Christopher Nolan movies
    print("\n6. Christopher Nolan Movies:")
    nolan_movies = db.get_movies_by_director("Christopher Nolan")
    for movie in nolan_movies:
        print(f"   {movie[0]} ({movie[1]}) - {movie[2]} - Rating: {movie[3]}")
    
    # Get statistics
    print("\n7. Database Statistics:")
    stats = db.get_movie_statistics()
    print(f"   Total Movies: {stats['total_movies']}")
    print(f"   Average Rating: {stats['average_rating']}")
    print("   Movies by Decade:")
    for decade, count in stats['movies_by_decade']:
        print(f"     {int(decade)}s: {count} movies")
    print("   Top Genres:")
    for genre, count in stats['top_genres']:
        print(f"     {genre}: {count} movies")
    
    # Close the database connection
    db.close_connection()

if __name__ == "__main__":
    main()