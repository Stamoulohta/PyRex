# vim: fileencoding=utf-8:expandtab:tabstop=2:softtabstop=2:shiftwidth=2:
#======================================================================================================================#
#
# Copyright © 2012 George A Stamoulis (g.a.stamoulis@gmail.com)
#
# TODO LICENCE GOES HERE...
#
#======================================================================================================================#
"""
Extensions package initiation.
`__all__` list must be explicitly updated whith every new module
allong with importing the modules class.

Please read README.md for Instrucrions on porting new RegularExperssion
libraries.

author  : George Stamoulis
email   : g.a.stamoulis@gmail.com
website : http://www.stamoulohta.com
edited  : 10/12/2012

"""

from rEx import RELib
from stdRe import StdRe 
from qRegExp import QRegExp


__all__=["RELib", "StdRe", "QRegExp"]
