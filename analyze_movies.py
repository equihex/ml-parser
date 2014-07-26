import sys


# performs basic analysis of data from Movie Lens 1m dataset ( http://grouplens.org/datasets/movielens/ )
class MovieLensParser(object):

    USAGE = "usage: analyze_movies.py (gender|agegroup) (top|bottom) <number>"
    # what's the highest number of movies that can reasonably be requested so that the output is sane on a shell
    MAX_MOVIES = 100
    # supported types of report
    ALLOWED_GROUPINGS = ["gender", "agegroup"]
    # orderings allowed
    ALLOWED_ORDERS = ["top", "bottom"]
    # data files and how to handle them

    order = ''
    grouping = ''
    num_results = 0
    movies = {}
    ratings = {}
    users = {}

    def __init__(self, args):
        # this will check for Movie Lens files, load them into memory etc
        # TODO: basic validation that data in these files is what we expect - read the first line and check contents
        # TODO: load the data into useful data structures for use with getResults - load differently / transform depending on how we are called?
        # check the command line args are sane, and store them
        self.validateInput(args)

        # files to load
        self.DATA_FILES = {
            "movies.dat": self.loadMovies,
         #   "ratings.dat": "loadRatings",
         #   "users.dat": "loadUsers",
        }

        for filename in self.DATA_FILES.keys():
            try:
                data_file = open(filename)
            except IOError as e:
                raise MovieLensParserFileError('Unable to open {0} for reading ({1})'.format(filename, e))
            # load the data from within the file
            self.DATA_FILES[filename](data_file)
            data_file.close()

    def loadMovies(self, data_file):
        # straightforward - we just need a mapping of movie name to movie id
        line_format = 'MovieID::Title::Genres'
        line_counter = 0
        for line in data_file:
            line_counter += 1
            movie_details = line.split('::')
            if len(movie_details) != 3:
                line_error = 'Invalid data detected in movies.dat at line {0}, expected [{1}], got [{2}]'.format(
                             line_counter, line, line_format
                )
                raise MovieLensParserFileError(line_error)

            self.movies[movie_details[0]] = movie_details[1]

    def validateInput(self, shell_input):
        # validate input from the shell - must be in this format: (gender|agegroup) (top|bottom) <number>
        self.grouping = shell_input.pop(0)
        if not self.grouping in MovieLensParser.ALLOWED_GROUPINGS:
            raise MovieLensParserInputError("{0} is not a valid request type. Supported types are: ({1})".format(
                                            self.grouping, ", ".join(MovieLensParser.ALLOWED_GROUPINGS)))

        self.order = shell_input.pop(0)
        if not self.order in MovieLensParser.ALLOWED_ORDERS:
            raise MovieLensParserInputError("{0} is not a valid order. Supported orders are: ({1})".format(
                                            self.order, ", ".join(MovieLensParser.ALLOWED_ORDERS)))
        try:
            self.number = int(shell_input.pop(0))
        except (TypeError, ValueError):
            raise MovieLensParserInputError('<number> must be an integer')

        if self.number + 0 > MovieLensParser.MAX_MOVIES:
            raise MovieLensParserInputError("Please choose an number less than {0}".format(
                                            MovieLensParser.MAX_MOVIES))

    def getResults(self):
        # based on our validated parameters, return a set of results, formatted for output to shell
        print self.movies
        pass


# exceptions relating to input
class MovieLensParserInputError(Exception):
    pass


# exceptions relating to opening / reading the files
class MovieLensParserFileError(Exception):
    pass

if __name__ == '__main__':
    # shift off the script name from argv before passing through for validation
    sys.argv.pop(0)

    try:
        ml = MovieLensParser(sys.argv)
        print ml.getResults()
    except MovieLensParserFileError as e:
        print "Encountered an error trying to read a data file"
        print "Please ensure data files are in the same directory as analyze_movies.py and are named like movies.dat"
        print "Error details: {0}".format(e.message)

        raise SystemError(e.message)
    except MovieLensParserInputError as e:
        print "Received invalid input: {0}".format(e.message)
        print MovieLensParser.USAGE

