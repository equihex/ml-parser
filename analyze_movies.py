import sys
# performs basic analysis of data from Movie Lens 1m dataset ( http://grouplens.org/datasets/movielens/ )
class MovieLensParser(object):

    def __init__(self):
        # this will check for Movie Lens files, load them into memory etc
        # TODO: basic validation that data in these files is what we expect - read the first line and check contents
        # TODO: load the data into useful data structures for use with getResults - load differently / transform depending on how we are called?
        pass

    def validateInput(self, shell_input):
        # validate input from the shell - must be in this format: (gender|agegroup) (top|bottom) <number>
        # TODO: sane limit on total number of results allowed to request

        pass

    def getResults(self):
        # based on our validated parameters, return a set of results, formatted for output to shell
        pass


# allows us to catch predefined exceptions coming out of the processing, and report them nicely
class MovieLensParserException(Exception):
    pass

if __name__ == '__main__':
    # shift off the script name from argv before passing through for validation
    sys.argv.pop(0)
    try:
        ml = MovieLensParser()
        ml.validateInput(sys.argv)
    except MovieLensParserException:
        #TODO: nice error handling here
        pass

    print ml.getResults()

