"""Multi-consumer multi-producer dispatching mechanism

Originally based on pydispatch (BSD) http://pypi.python.org/pypi/PyDispatcher/2.0.1
See license.txt for original license.

Heavily modified for Django's purposes.

Modified again for RconSoft's purposes. It now supports python 2.6 and
3.0 (I think). I changed all im_func to __func__ and all im_self to __self__.
This breaks backwards compatibility.
"""

from dispatcher import Signal