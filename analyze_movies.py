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

    order = ''
    grouping = ''
    num_results = 0

    def __init__(self):
        # this will check for Movie Lens files, load them into memory etc
        # TODO: basic validation that data in these files is what we expect - read the first line and check contents
        # TODO: load the data into useful data structures for use with getResults - load differently / transform depending on how we are called?
        pass

    def validateInput(self, shell_input):
        # validate input from the shell - must be in this format: (gender|agegroup) (top|bottom) <number>
        self.grouping = shell_input.pop(0)
        if not self.grouping in MovieLensParser.ALLOWED_GROUPINGS:
            raise MovieLensParserInputException("{0} is not a valid request type. Supported types are: ({1})".format(
                                                self.grouping, ", ".join(MovieLensParser.ALLOWED_GROUPINGS)))

        self.order = shell_input.pop(0)
        if not self.order in MovieLensParser.ALLOWED_ORDERS:
            raise MovieLensParserInputException("{0} is not a valid order. Supported orders are: ({1})".format(
                                                self.order, ", ".join(MovieLensParser.ALLOWED_ORDERS)))
        try:
            self.number = int(shell_input.pop(0))
        except (TypeError, ValueError):
            raise MovieLensParserInputException('<number> must be an integer')

        if self.number + 0 > MovieLensParser.MAX_MOVIES:
            raise MovieLensParserInputException("Please choose an number less than {0}".format(
                                                MovieLensParser.MAX_MOVIES))

    def getResults(self):
        # based on our validated parameters, return a set of results, formatted for output to shell
        print "***"
        pass


# exceptions relating to input
class MovieLensParserInputException(Exception):
    pass


# other exceptions
class MovieLensParserException(Exception):
    pass
if __name__ == '__main__':
    # shift off the script name from argv before passing through for validation
    sys.argv.pop(0)

    try:
        ml = MovieLensParser()
        ml.validateInput(sys.argv)
        print ml.getResults()
    except MovieLensParserException as e:
        #TODO: nice error handling here
        raise SystemError(e.message)
    except MovieLensParserInputException as e:
        print "Received invalid input: %s" % e.message
        print MovieLensParser.USAGE

