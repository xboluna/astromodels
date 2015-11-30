__author__ = 'giacomov'

def _behaves_like_a_number(obj):
    '''

    :param obj:
    :return: True if obj supports addition, subtraction, multiplication and division. False otherwise.
    '''


    try:

        obj + 1
        obj * 2
        obj / 2
        obj - 1

    except TypeError:

        return False

    else:

        return True

class Parameter(object):

    '''

    Implements a numerical parameter.

    :param name: Name for the parameter
    :param initial_value: Initial value
    :keyword min: minimum allowed value for the parameter (default: None)
    :keyword max: maximum allowed value for the parameter (default: None)
    :keyword delta: initial step used by some fitting engines (default: 0.1 * value)

    Examples
    --------

    Create a parameter with::

    > p = Parameter("param1",1.0)

    This will create a parameter called "param1" with initial value 1.0 and no boundaries. It will also have a
    default delta of 10% the value, in this case 0.1 * 1 = 0.1.

    You can use optional keywords to define the boundaries of the parameter as well as its delta::

    > p = Parameter("param1",1.0, min = -10.0, max = 35, delta = 3)

    This will create a parameter bounded between -10.0 and 35, with initial delta = 3.

    You can set the current value of the parameter as::

    > p.value = 2.5

    or get its current value as::

    > current_value = p.value

    You can set its boundaries with::

    > p.set_bounds(-10, 35)

    A value of None for either the minimum or the maximum will remove the boundary in that direction.

    You can get the current boundaries as::

    > min_value, max_value = p.get_bounds()



    You can set or get the value for delta as::

    > p.delta = 0.3
    > current_delta = p.delta

    The Parameter class provides also a functionality to set callbacks which are called whenever the value of the
    parameter changes. This can be used for tracing purposes or other things. This code for example sets a simple
    callback which just prints the value of the parameter any time it is changed::

      > def callback( value ):
            print("The parameter changed value. It is now %s" % value )
      > p.add_callback( callback )
      > p.value = 10.0
      The parameter changed value. It is now 10.0

    This is instead a more elaborated example where a class is used to keep track of all the values the parameter has
    assumed with time::

      > class MyRecorder( object ):
          def __init__(self):
              self.values = []
          def __call__(self, value):
              self.values.append(value)
          def print_values(self):
              print("This is the history of all the values this parameter has been set to:")
              print(self.values)
      > recorder = MyRecorder()
      > p.add_callback( recorder )
      > p.value = 5.0
      > p.value = -2.0
      > p.value = 18.0
      > recorder.print_values()
      This is the history of all the values this parameter has been set to:
      [5.0, -2.0, 18.0]

    More than one callback can be registered. The callbacks will be executed in the order they are entered. To clear all
    callbacks use the method empty_callbacks().
    '''

    def __init__(self, name, initial_value, **kwargs):

        #NOTE: we avoid enforcing a particular type or even that initial_values, max, min and delta are python numbers.
        #Indeed, as long as they behave as numbers we are going to be fine. We want to keep the possibility to use
        #numbers coming from C, C++ or other sources, for example. Note however that string parameters are not supported

        #Callbacks are executed any time the value for the parameter changes (i.e., its value changes)

        #We start from a empty list of callbacks.
        self._callbacks = []

        #Assign to members

        self.name = name

        self._value = initial_value

        #Set minimum if provided, otherwise use default

        if 'min' in kwargs.keys():

            self._min_value = kwargs['min']

        else:

            self._min_value = None

        #Set maximum if provided, otherwise use default

        if 'max' in kwargs.keys():

            self._max_value = kwargs['max']

        else:

            self._max_value = None

        #Set delta if provided, otherwise use default

        if 'delta' in kwargs.keys():

            self._delta = kwargs['delta']

        else:

            self._delta = 0.1 * self._value

        #pre-defined prior is no prior
        self._prior = None

        #Now perform a very lazy check that we can perform math operations on all members

        if not _behaves_like_a_number(self._value):

            raise TypeError("The provided initial value is not a number")

        if not _behaves_like_a_number(self._delta):

            raise TypeError("The provided delta is not a number")

        if self._min_value is not None:

            if not _behaves_like_a_number(self._min_value):

                raise TypeError("The provided minimum value is not a number")

        if self._max_value is not None:

            if not _behaves_like_a_number(self._max_value):

                raise TypeError("The provided maximum value is not a number")

    def get_value(self):
        '''Return current parameter value'''
        return self._value

    def set_value(self, value):
        """Sets the current value of the parameter, ensuring that it is within the allowed range"""

        if self._min_value is not None and value < self._min_value:

            raise ValueError(
                "Trying to set parameter {0} = {1}, which is less than the minimum allowed {2}".format(
                    self.name, value, self._min_value))

        if self._max_value is not None and value > self._max_value:

            raise ValueError(
                "Trying to set parameter {0} = {1}, which is more than the maximum allowed {2}".format(
                    self.name, value, self._max_value))

        #Call the callbacks (if any)

        for callback in self._callbacks:

            try:

                callback( value )

            except:

                raise RuntimeError("Could not get callback for parameter %s with value %s" %(self.name, value))

        self._value = value

    value = property(get_value, set_value,
                         doc="""Gets or sets the value for the parameter""")

    def get_delta(self):
        '''Gets the current value for the delta of the parameter'''
        return self._delta

    def set_delta(self, delta):
        '''Sets the current delta for the parameter. The delta is used as initial step by some fitting engines'''

        if not _behaves_like_a_number(delta):

            raise ValueError("Provided delta is not a number" % delta)

        self._delta = delta

    delta = property(get_delta,set_delta,
                     doc='''Gets or sets the delta for the parameter''')

    def get_min_value(self):
        '''Return current minimum allowed value'''
        return self._min_value

    def set_min_value(self, min_value):
        '''Sets current minimum allowed value'''

        if min_value is not None and not _behaves_like_a_number(min_value):

            raise ValueError("Provided minimum value is not a number nor None")

        self._min_value = min_value

    min_value = property(get_min_value, set_min_value,
                         doc='Gets or sets the minimum allowed value for the parameter')

    def get_max_value(self):
        '''Return current minimum allowed value'''
        return self._max_value

    def set_max_value(self, max_value):
        '''Sets current minimum allowed value'''

        if max_value is not None and not _behaves_like_a_number(max_value):

            raise ValueError("Provided maximum value is not a number nor None")

        self._max_value = max_value

    max_value = property(get_max_value, set_max_value,
                         doc='Gets or sets the maximum allowed value for the parameter')

    def set_bounds(self, min_value, max_value):
        '''Sets the boundaries for this parameter to min_value and max_value'''

        #Use the properties so that the checks are made automatically

        self.min_value = min_value

        self.max_value = max_value

    def get_bounds(self):
        '''Returns the current boundaries for the parameter'''

        return self.min_value, self.max_value

    def add_callback(self, callback):
        '''Add a callback to the list of functions which are called whenever the value of the parameter is changed.
        The callback must be a function accepting the current value as input. The return value of the callback is
        ignored. More than one callback can be specified. In that case, the callbacks will be called in the same order
        they have been entered.'''

        self._callbacks.append(callback)

    def empty_callbacks(self):
        '''Remove all callbacks for this parameter'''
        self._callback = []

    def get_prior(self):

        if self._prior is None:

            raise RuntimeError("There is no defined prior for parameter %s" % self.name)

        return self._prior

    def set_prior(self, prior):
        '''Set prior for this parameter. The prior must be a function accepting the current value of the parameter
        as input and giving the probability density as output.'''

        #Try and call the prior with the current value of the parameter
        try:

            val = prior(self._value)

        except:

            raise RuntimeError("Could not call the provided prior. " +
                               "Is it a function accepting the currentv value of the parameter?")

        self._prior = prior

    prior = property(get_prior,set_prior,
                     doc="Gets or sets the current prior for this parameter. The prior must be a callable function +"
                         "accepting the current value of the parameter as input and returning the probability "+
                         "density as output")