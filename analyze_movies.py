from collections import defaultdict, Counter
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

    # readable names for fields in the users.dat file
    USER_GENDERS = {'F': 'Female', 'M': 'Male'}
    USER_AGES =    {1:  "Under 18", 18:  "18-24", 25:  "25-34", 35:  "35-44",
                    45:  "45-49", 50:  "50-55", 56:  "56+"}

    order = ''
    grouping = ''
    max_results = 0
    movies = {}
    ratings = defaultdict(dict)
    users = defaultdict(list)
    # cache for use with decodeline
    expected_parts = {}

    # output message to display results in
    output_msg = []

    def __init__(self, args):
        # this will check for Movie Lens files, load them into memory etc
        # TODO: basic validation that data in these files is what we expect - read the first line and check contents
        # TODO: load the data into useful data structures for use with getResults - load differently / transform depending on how we are called?
        # check the command line args are sane, and store them
        self.validateInput(args)

        # files to load
        self.DATA_FILES = {
            "movies.dat": self.loadMovies,
            "ratings.dat": self.loadRatings,
            "users.dat": self.loadUsers,
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
            movie_details = self.decodeLine('movies.dat', line, line_counter, line_format)
            self.movies[movie_details[0]] = movie_details[1]

    def loadRatings(self, data_file):
        line_format = 'UserID::MovieID::Rating::Timestamp'
        line_counter = 0
        for line in data_file:
            line_counter += 1
            rating_details = self.decodeLine('ratings.dat', line, line_counter, line_format)
            # ie ratings[user_id][movie_id] = rating
            self.ratings[rating_details[0]][rating_details[1]] = rating_details[2]

    def loadUsers(self, data_file):
        # the most important loader since this will be the start point for our analysis
        # load / key the data differently according to whether gender or agegroup was chosen
        line_counter = 0
        line_format = 'UserID::Gender::Age::Occupation::Zip-code'

        for line in data_file:
            line_counter += 1
            user_details = self.decodeLine('users.dat', line, line_counter, line_format)

            if self.grouping == 'gender':
                # gender => list of user ids
                self.users[user_details[1]].append(user_details[0])
            elif self.grouping == 'agegroup':
                # agegroup => list of userids
                self.users[int(user_details[2])].append(user_details[0])
            else:
                raise MovieLensParserInputError('{0} is not a supported grouping'.format(self.grouping))
        pass

    def decodeLine(self, filename, line, line_counter, line_format):
        # cache split of line format for speed
        if filename not in self.expected_parts:
            self.expected_parts[filename] = len(line_format.split('::'))

        parts = line.split('::')
        if len(parts) != self.expected_parts[filename]:
            line_error = 'Invalid data detected in {0} at line {1}, expected [{2}], got [{3}]'.format(
                         filename, line_counter, line_format, line
            )
            raise MovieLensParserFileError(line_error)
        return parts

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
            self.max_results = int(shell_input.pop(0))
        except (TypeError, ValueError):
            raise MovieLensParserInputError('<number> must be an integer')

        if self.max_results + 0 > MovieLensParser.MAX_MOVIES:
            raise MovieLensParserInputError("Please choose an number less than {0}".format(
                                            MovieLensParser.MAX_MOVIES))

    def getResults(self):
        # based on our validated parameters, return a set of results, formatted for output to shell
        # iterate through our groups, and assign the movies / ratings in them into the relevant buckets
        for group in sorted(self.users.keys()):
            group_name = self.USER_AGES[group] if self.grouping == 'agegroup' else self.USER_GENDERS[group]
            bucketed = Counter()
            # do a slice on our ratings to get the ratings for the set of users in this group
            group_ratings = [self.ratings[x] for x in self.users[group]]
            # iterate over each user's set of ratings
            for rating_set in group_ratings:
                for movie_id in rating_set.keys():
                    bucketed[movie_id] += int(rating_set[movie_id])

            if self.order == 'top':
                ranked_movies = bucketed.most_common(self.max_results)
            elif self.order == 'bottom':
                ranked_movies = reversed(bucketed.most_common()[len(bucketed) - self.max_results:])
            else:
                raise MovieLensParserInputError('{0} is not a valid ordering'.format(self.order))

            group_title = ['', '{0} ranked movies for group: {1}'.format(self.order.capitalize(), group_name), '']
            self.output_msg.extend(group_title)

            for movie in ranked_movies:
                formatted = "{0} - total rating {1}".format(
                    self.movies[movie[0]], movie[1]
                )
                self.output_msg.append(formatted)

        return "\n".join(self.output_msg)


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

