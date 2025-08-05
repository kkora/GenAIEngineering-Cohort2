import pyodbc
import pandas as pd
from datetime import datetime
import os
from contextlib import contextmanager

class MoviesMSSQLDB:
    def __init__(self, server, database, username=None, password=None, trusted_connection=True):
        """
        Initialize connection to MS SQL Server
        
        Args:
            server: SQL Server instance (e.g., 'localhost' or 'SERVER\\INSTANCE')
            database: Database name
            username: SQL Server username (if not using Windows Auth)
            password: SQL Server password (if not using Windows Auth)
            trusted_connection: Use Windows Authentication (default: True)
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.trusted_connection = trusted_connection
        self.connection_string = self._build_connection_string()
        
        # Test connection and create database if needed
        self._create_database_if_not_exists()
        self.create_tables()
    
    def _build_connection_string(self):
        """Build the connection string for SQL Server"""
        driver = "{ODBC Driver 17 for SQL Server}"  # or "{SQL Server}" for older versions
        
        if self.trusted_connection:
            # Windows Authentication
            conn_str = f"DRIVER={driver};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;"
        else:
            # SQL Server Authentication
            conn_str = f"DRIVER={driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password};"
        
        return conn_str
    
    def _create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        # Connect to master database to create our database
        master_conn_str = self.connection_string.replace(f"DATABASE={self.database}", "DATABASE=master")
        
        try:
            # Use a direct connection without context manager for database creation
            conn = pyodbc.connect(master_conn_str, autocommit=True)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("""
                SELECT database_id 
                FROM sys.databases 
                WHERE name = ?
            """, self.database)
            
            if not cursor.fetchone():
                # Create database - autocommit handles the transaction automatically
                cursor.execute(f"CREATE DATABASE [{self.database}]")
                print(f"Database '{self.database}' created successfully!")
            else:
                print(f"Database '{self.database}' already exists.")
            
            # Close the connection
            cursor.close()
            conn.close()
                    
        except pyodbc.Error as e:
            print(f"Error creating database: {e}")
            # If database creation fails, it might already exist or we don't have permissions
            # Try to connect to the target database to see if it exists
            try:
                test_conn = pyodbc.connect(self.connection_string)
                test_conn.close()
                print(f"Database '{self.database}' is accessible.")
            except pyodbc.Error:
                print(f"Cannot access database '{self.database}'. Please create it manually or check permissions.")
                raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            yield conn
        except pyodbc.Error as e:
            if conn:
                conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def create_tables(self):
        """Create all database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Drop tables if they exist (for fresh start)
            drop_tables = [
                "DROP TABLE IF EXISTS MovieActors",
                "DROP TABLE IF EXISTS MovieGenres", 
                "DROP TABLE IF EXISTS Reviews",
                "DROP TABLE IF EXISTS Actors",
                "DROP TABLE IF EXISTS Genres",
                "DROP TABLE IF EXISTS Movies"
            ]
            
            for drop_sql in drop_tables:
                try:
                    cursor.execute(drop_sql)
                except:
                    pass  # Table might not exist
            
            # Create Movies table
            cursor.execute("""
                CREATE TABLE Movies (
                    MovieID INT IDENTITY(1,1) PRIMARY KEY,
                    Title NVARCHAR(255) NOT NULL,
                    ReleaseYear INT,
                    Director NVARCHAR(255),
                    Rating DECIMAL(3,1) CHECK (Rating >= 0 AND Rating <= 10),
                    DurationMinutes INT,
                    Budget BIGINT,
                    BoxOffice BIGINT,
                    Plot NTEXT,
                    Language NVARCHAR(50),
                    Country NVARCHAR(100),
                    CreatedAt DATETIME2 DEFAULT GETDATE(),
                    UpdatedAt DATETIME2 DEFAULT GETDATE()
                )
            """)
            
            # Create Genres table
            cursor.execute("""
                CREATE TABLE Genres (
                    GenreID INT IDENTITY(1,1) PRIMARY KEY,
                    GenreName NVARCHAR(50) UNIQUE NOT NULL,
                    Description NVARCHAR(500)
                )
            """)
            
            # Create Actors table
            cursor.execute("""
                CREATE TABLE Actors (
                    ActorID INT IDENTITY(1,1) PRIMARY KEY,
                    FirstName NVARCHAR(100) NOT NULL,
                    LastName NVARCHAR(100) NOT NULL,
                    BirthDate DATE,
                    Nationality NVARCHAR(100),
                    Biography NTEXT,
                    CreatedAt DATETIME2 DEFAULT GETDATE()
                )
            """)
            
            # Create MovieGenres junction table
            cursor.execute("""
                CREATE TABLE MovieGenres (
                    MovieID INT,
                    GenreID INT,
                    PRIMARY KEY (MovieID, GenreID),
                    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID) ON DELETE CASCADE,
                    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID) ON DELETE CASCADE
                )
            """)
            
            # Create MovieActors junction table
            cursor.execute("""
                CREATE TABLE MovieActors (
                    MovieID INT,
                    ActorID INT,
                    Role NVARCHAR(255),
                    IsMainRole BIT DEFAULT 0,
                    PRIMARY KEY (MovieID, ActorID),
                    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID) ON DELETE CASCADE,
                    FOREIGN KEY (ActorID) REFERENCES Actors(ActorID) ON DELETE CASCADE
                )
            """)
            
            # Create Reviews table
            cursor.execute("""
                CREATE TABLE Reviews (
                    ReviewID INT IDENTITY(1,1) PRIMARY KEY,
                    MovieID INT NOT NULL,
                    ReviewerName NVARCHAR(100),
                    Rating INT CHECK (Rating >= 1 AND Rating <= 5),
                    ReviewText NTEXT,
                    ReviewDate DATETIME2 DEFAULT GETDATE(),
                    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IX_Movies_Title ON Movies(Title)",
                "CREATE INDEX IX_Movies_ReleaseYear ON Movies(ReleaseYear)",
                "CREATE INDEX IX_Movies_Director ON Movies(Director)",
                "CREATE INDEX IX_Movies_Rating ON Movies(Rating)",
                "CREATE INDEX IX_Actors_LastName ON Actors(LastName)",
                "CREATE INDEX IX_Reviews_MovieID ON Reviews(MovieID)",
                "CREATE INDEX IX_Reviews_Rating ON Reviews(Rating)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            print("All tables and indexes created successfully!")
    
    def add_genre(self, genre_name, description=None):
        """Add a new genre"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO Genres (GenreName, Description)
                    VALUES (?, ?)
                """, genre_name, description)
                conn.commit()
                
                # Get the inserted ID
                cursor.execute("SELECT @@IDENTITY")
                genre_id = cursor.fetchone()[0]
                print(f"Genre '{genre_name}' added with ID: {genre_id}")
                return int(genre_id)
            except pyodbc.IntegrityError:
                print(f"Genre '{genre_name}' already exists")
                return self.get_genre_id(genre_name)
    
    def get_genre_id(self, genre_name):
        """Get genre ID by name"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT GenreID FROM Genres WHERE GenreName = ?", genre_name)
            result = cursor.fetchone()
            return result[0] if result else None
    
    def add_actor(self, first_name, last_name, birth_date=None, nationality=None, biography=None):
        """Add a new actor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Actors (FirstName, LastName, BirthDate, Nationality, Biography)
                VALUES (?, ?, ?, ?, ?)
            """, first_name, last_name, birth_date, nationality, biography)
            conn.commit()
            
            cursor.execute("SELECT @@IDENTITY")
            actor_id = cursor.fetchone()[0]
            print(f"Actor '{first_name} {last_name}' added with ID: {actor_id}")
            return int(actor_id)
    
    def add_movie(self, title, release_year=None, director=None, rating=None, 
                  duration_minutes=None, budget=None, box_office=None, plot=None,
                  language=None, country=None):
        """Add a new movie"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Movies (Title, ReleaseYear, Director, Rating, DurationMinutes, 
                                  Budget, BoxOffice, Plot, Language, Country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, title, release_year, director, rating, duration_minutes, 
                budget, box_office, plot, language, country)
            conn.commit()
            
            cursor.execute("SELECT @@IDENTITY")
            movie_id = cursor.fetchone()[0]
            print(f"Movie '{title}' added with ID: {movie_id}")
            return int(movie_id)
    
    def link_movie_genre(self, movie_id, genre_id):
        """Link a movie with a genre"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO MovieGenres (MovieID, GenreID)
                    VALUES (?, ?)
                """, movie_id, genre_id)
                conn.commit()
                print(f"Linked movie ID {movie_id} with genre ID {genre_id}")
            except pyodbc.IntegrityError:
                print(f"Movie {movie_id} already linked to genre {genre_id}")
    
    def link_movie_actor(self, movie_id, actor_id, role=None, is_main_role=False):
        """Link a movie with an actor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO MovieActors (MovieID, ActorID, Role, IsMainRole)
                    VALUES (?, ?, ?, ?)
                """, movie_id, actor_id, role, is_main_role)
                conn.commit()
                print(f"Linked movie ID {movie_id} with actor ID {actor_id}")
            except pyodbc.IntegrityError:
                print(f"Movie {movie_id} already linked to actor {actor_id}")
    
    def add_review(self, movie_id, reviewer_name, rating, review_text=None):
        """Add a movie review"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Reviews (MovieID, ReviewerName, Rating, ReviewText)
                VALUES (?, ?, ?, ?)
            """, movie_id, reviewer_name, rating, review_text)
            conn.commit()
            
            cursor.execute("SELECT @@IDENTITY")
            review_id = cursor.fetchone()[0]
            print(f"Review added with ID: {review_id}")
            return int(review_id)
    
    def get_all_movies(self):
        """Get all movies with basic information"""
        with self.get_connection() as conn:
            query = """
                SELECT MovieID, Title, ReleaseYear, Director, Rating, DurationMinutes, Language, Country
                FROM Movies
                ORDER BY ReleaseYear DESC, Title
            """
            return pd.read_sql(query, conn)
    
    def get_movies_by_genre(self, genre_name):
        """Get movies by genre"""
        with self.get_connection() as conn:
            query = """
                SELECT m.Title, m.ReleaseYear, m.Director, m.Rating, g.GenreName
                FROM Movies m
                INNER JOIN MovieGenres mg ON m.MovieID = mg.MovieID
                INNER JOIN Genres g ON mg.GenreID = g.GenreID
                WHERE g.GenreName = ?
                ORDER BY m.Rating DESC, m.Title
            """
            return pd.read_sql(query, conn, params=[genre_name])
    
    def get_movies_by_actor(self, first_name, last_name):
        """Get movies by actor"""
        with self.get_connection() as conn:
            query = """
                SELECT m.Title, m.ReleaseYear, m.Director, ma.Role, m.Rating
                FROM Movies m
                INNER JOIN MovieActors ma ON m.MovieID = ma.MovieID
                INNER JOIN Actors a ON ma.ActorID = a.ActorID
                WHERE a.FirstName = ? AND a.LastName = ?
                ORDER BY m.ReleaseYear DESC
            """
            return pd.read_sql(query, conn, params=[first_name, last_name])
    
    def get_movies_by_director(self, director_name):
        """Get movies by director"""
        with self.get_connection() as conn:
            query = """
                SELECT Title, ReleaseYear, Rating, DurationMinutes, BoxOffice
                FROM Movies
                WHERE Director LIKE ?
                ORDER BY ReleaseYear DESC
            """
            return pd.read_sql(query, conn, params=[f'%{director_name}%'])
    
    def get_top_rated_movies(self, limit=10):
        """Get top-rated movies"""
        with self.get_connection() as conn:
            query = """
                SELECT TOP (?) Title, ReleaseYear, Director, Rating, BoxOffice
                FROM Movies
                WHERE Rating IS NOT NULL
                ORDER BY Rating DESC, BoxOffice DESC
            """
            return pd.read_sql(query, conn, params=[limit])
    
    def get_movie_details(self, movie_id):
        """Get detailed information about a specific movie"""
        with self.get_connection() as conn:
            # Movie basic info
            movie_query = """
                SELECT * FROM Movies WHERE MovieID = ?
            """
            movie_df = pd.read_sql(movie_query, conn, params=[movie_id])
            
            # Genres
            genres_query = """
                SELECT g.GenreName
                FROM Genres g
                INNER JOIN MovieGenres mg ON g.GenreID = mg.GenreID
                WHERE mg.MovieID = ?
            """
            genres_df = pd.read_sql(genres_query, conn, params=[movie_id])
            
            # Actors
            actors_query = """
                SELECT a.FirstName, a.LastName, ma.Role, ma.IsMainRole
                FROM Actors a
                INNER JOIN MovieActors ma ON a.ActorID = ma.ActorID
                WHERE ma.MovieID = ?
                ORDER BY ma.IsMainRole DESC, a.LastName
            """
            actors_df = pd.read_sql(actors_query, conn, params=[movie_id])
            
            # Reviews
            reviews_query = """
                SELECT ReviewerName, Rating, ReviewText, ReviewDate
                FROM Reviews
                WHERE MovieID = ?
                ORDER BY ReviewDate DESC
            """
            reviews_df = pd.read_sql(reviews_query, conn, params=[movie_id])
            
            return {
                'movie': movie_df,
                'genres': genres_df,
                'actors': actors_df,
                'reviews': reviews_df
            }
    
    def get_database_statistics(self):
        """Get comprehensive database statistics"""
        with self.get_connection() as conn:
            stats = {}
            
            # Basic counts
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Movies")
            stats['total_movies'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Actors")
            stats['total_actors'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Genres")
            stats['total_genres'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Reviews")
            stats['total_reviews'] = cursor.fetchone()[0]
            
            # Average rating
            cursor.execute("SELECT AVG(CAST(Rating AS FLOAT)) FROM Movies WHERE Rating IS NOT NULL")
            avg_rating = cursor.fetchone()[0]
            stats['average_rating'] = round(avg_rating, 2) if avg_rating else None
            
            # Movies by decade
            decade_query = """
                SELECT (ReleaseYear / 10) * 10 as Decade, COUNT(*) as MovieCount
                FROM Movies 
                WHERE ReleaseYear IS NOT NULL
                GROUP BY (ReleaseYear / 10) * 10
                ORDER BY Decade DESC
            """
            stats['movies_by_decade'] = pd.read_sql(decade_query, conn)
            
            # Top genres
            genre_query = """
                SELECT TOP 5 g.GenreName, COUNT(*) as MovieCount
                FROM Genres g
                INNER JOIN MovieGenres mg ON g.GenreID = mg.GenreID
                GROUP BY g.GenreName
                ORDER BY COUNT(*) DESC
            """
            stats['top_genres'] = pd.read_sql(genre_query, conn)
            
            # Most productive directors
            director_query = """
                SELECT TOP 5 Director, COUNT(*) as MovieCount, AVG(CAST(Rating AS FLOAT)) as AvgRating
                FROM Movies 
                WHERE Director IS NOT NULL
                GROUP BY Director
                HAVING COUNT(*) > 1
                ORDER BY COUNT(*) DESC
            """
            stats['top_directors'] = pd.read_sql(director_query, conn)
            
            return stats
    
    def search_movies(self, search_term):
        """Search movies by title, director, or actor"""
        with self.get_connection() as conn:
            query = """
                SELECT DISTINCT m.MovieID, m.Title, m.ReleaseYear, m.Director, m.Rating
                FROM Movies m
                LEFT JOIN MovieActors ma ON m.MovieID = ma.MovieID
                LEFT JOIN Actors a ON ma.ActorID = a.ActorID
                WHERE m.Title LIKE ? 
                   OR m.Director LIKE ?
                   OR CONCAT(a.FirstName, ' ', a.LastName) LIKE ?
                ORDER BY m.Rating DESC, m.Title
            """
            search_pattern = f'%{search_term}%'
            return pd.read_sql(query, conn, params=[search_pattern, search_pattern, search_pattern])

def setup_sample_data(db):
    """Setup sample data for testing"""
    print("\n=== Setting up sample data ===")
    
    # Add genres
    action_id = db.add_genre("Action", "High-energy films with intense sequences")
    drama_id = db.add_genre("Drama", "Character-driven stories with emotional depth")
    scifi_id = db.add_genre("Sci-Fi", "Science fiction and futuristic themes")
    crime_id = db.add_genre("Crime", "Criminal activities and investigations")
    
    # Add actors
    morgan_id = db.add_actor("Morgan", "Freeman", "1937-06-01", "American")
    christian_id = db.add_actor("Christian", "Bale", "1974-01-30", "British")
    leonardo_id = db.add_actor("Leonardo", "DiCaprio", "1974-11-11", "American")
    john_id = db.add_actor("John", "Travolta", "1954-02-18", "American")
    
    # Add movies
    shawshank_id = db.add_movie(
        "The Shawshank Redemption", 1994, "Frank Darabont", 9.3, 142,
        25000000, 16000000, 
        "Two imprisoned men bond over years, finding solace and redemption through acts of common decency.",
        "English", "USA"
    )
    
    dark_knight_id = db.add_movie(
        "The Dark Knight", 2008, "Christopher Nolan", 9.0, 152,
        185000000, 1004558444,
        "Batman faces the Joker, a criminal mastermind who seeks to undermine Batman's influence.",
        "English", "USA"
    )
    
    inception_id = db.add_movie(
        "Inception", 2010, "Christopher Nolan", 8.8, 148,
        160000000, 836836967,
        "A thief who enters the dreams of others to steal their secrets.",
        "English", "USA"
    )
    
    pulp_fiction_id = db.add_movie(
        "Pulp Fiction", 1994, "Quentin Tarantino", 8.9, 154,
        8000000, 214179088,
        "The lives of two mob hitmen, a boxer, and others intertwine in four tales of violence.",
        "English", "USA"
    )
    
    # Link movies with genres
    db.link_movie_genre(shawshank_id, drama_id)
    db.link_movie_genre(dark_knight_id, action_id)
    db.link_movie_genre(dark_knight_id, crime_id)
    db.link_movie_genre(inception_id, action_id)
    db.link_movie_genre(inception_id, scifi_id)
    db.link_movie_genre(pulp_fiction_id, crime_id)
    db.link_movie_genre(pulp_fiction_id, drama_id)
    
    # Link movies with actors
    db.link_movie_actor(shawshank_id, morgan_id, "Ellis Boyd 'Red' Redding", True)
    db.link_movie_actor(dark_knight_id, christian_id, "Bruce Wayne / Batman", True)
    db.link_movie_actor(inception_id, leonardo_id, "Dom Cobb", True)
    db.link_movie_actor(pulp_fiction_id, john_id, "Vincent Vega", True)
    
    # Add some reviews
    db.add_review(shawshank_id, "Roger Ebert", 5, "A masterpiece of storytelling and character development.")
    db.add_review(dark_knight_id, "Movie Critic", 5, "Heath Ledger's Joker is unforgettable.")
    db.add_review(inception_id, "Film Enthusiast", 4, "Mind-bending and visually stunning.")
    
    print("Sample data setup complete!")

def main():
    """Main function demonstrating the MoviesDB functionality"""
    # Database connection parameters
    # Modify these according to your SQL Server setup
    SERVER = "BEST-LTF3W0H97"  # or your server name/IP
    DATABASE = "MoviesDB"
    
    # For Windows Authentication (recommended if available)
    USE_TRUSTED_CONNECTION = True
    USERNAME = None
    PASSWORD = None
    
    # For SQL Server Authentication (uncomment and modify if needed)
    # USE_TRUSTED_CONNECTION = False
    # USERNAME = "your_username"
    # PASSWORD = "your_password"
    
    try:
        # Initialize database
        print("Connecting to SQL Server...")
        db = MoviesMSSQLDB(
            server=SERVER,
            database=DATABASE,
            username=USERNAME,
            password=PASSWORD,
            trusted_connection=USE_TRUSTED_CONNECTION
        )
        
        # Setup sample data
        setup_sample_data(db)
        
        print("\n=== Database Queries Demo ===")
        
        # Get all movies
        print("\n1. All Movies:")
        all_movies = db.get_all_movies()
        print(all_movies.to_string(index=False))
        
        # Get movies by genre
        print("\n2. Action Movies:")
        action_movies = db.get_movies_by_genre("Action")
        print(action_movies.to_string(index=False))
        
        # Get top-rated movies
        print("\n3. Top-Rated Movies:")
        top_movies = db.get_top_rated_movies(5)
        print(top_movies.to_string(index=False))
        
        # Get movies by actor
        print("\n4. Leonardo DiCaprio Movies:")
        leo_movies = db.get_movies_by_actor("Leonardo", "DiCaprio")
        print(leo_movies.to_string(index=False))
        
        # Search movies
        print("\n5. Search Results for 'Nolan':")
        search_results = db.search_movies("Nolan")
        print(search_results.to_string(index=False))
        
        # Get detailed movie information
        print("\n6. Detailed Information for 'Inception':")
        movie_details = db.get_movie_details(3)  # Assuming Inception has ID 3
        print("Movie Info:")
        print(movie_details['movie'].to_string(index=False))
        print("\nGenres:")
        print(movie_details['genres'].to_string(index=False))
        print("\nActors:")
        print(movie_details['actors'].to_string(index=False))
        
        # Get database statistics
        print("\n7. Database Statistics:")
        stats = db.get_database_statistics()
        print(f"Total Movies: {stats['total_movies']}")
        print(f"Total Actors: {stats['total_actors']}")
        print(f"Total Genres: {stats['total_genres']}")
        print(f"Total Reviews: {stats['total_reviews']}")
        print(f"Average Rating: {stats['average_rating']}")
        
        print("\nMovies by Decade:")
        print(stats['movies_by_decade'].to_string(index=False))
        
        print("\nTop Genres:")
        print(stats['top_genres'].to_string(index=False))
        
        print("\nTop Directors:")
        print(stats['top_directors'].to_string(index=False))
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("\nTroubleshooting Steps:")
        print("1. Ensure SQL Server is running and accessible")
        print("2. Check if you have permission to create databases")
        print("3. Try creating the database manually first:")
        print(f"   CREATE DATABASE [{DATABASE}]")
        print("4. Verify connection parameters are correct")
        print("5. Install required packages:")
        print("   pip install pyodbc pandas")
        print("6. Install ODBC Driver 17 for SQL Server")
        print("\nIf database creation fails, you can:")
        print("- Create the database manually in SQL Server Management Studio")
        print("- Or ask your DBA to create it for you")
        print("- Or use an existing database by changing the DATABASE variable")

if __name__ == "__main__":
    main()