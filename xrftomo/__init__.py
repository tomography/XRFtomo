#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #########################################################################
# Copyright © 2020, UChicago Argonne, LLC. All Rights Reserved.        	  #
#    																	  #
#						Software Name: XRFtomo							  #
#																		  #
#					By: Argonne National Laboratory						  #
#																		  #
#						OPEN SOURCE LICENSE                               #
#                                                                         #
# Redistribution and use in source and binary forms, with or without      #
# modification, are permitted provided that the following conditions      #
# are met:                                                                #
#                                                                         #
# 1. Redistributions of source code must retain the above copyright       #
#    notice, this list of conditions and the following disclaimer.        #
#																		  #
# 2. Redistributions in binary form must reproduce the above copyright    #
#    notice, this list of conditions and the following disclaimer in      #
#    the documentation and/or other materials provided with the 		  #
#    distribution.														  #
# 									                                      #
# 3. Neither the name of the copyright holder nor the names of its 		  #
#    contributors may be used to endorse or promote products derived 	  #
#    from this software without specific prior written permission.		  #
#																		  #
#								DISCLAIMER								  #
#							  											  #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 	  #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 	  #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR   #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 	  #
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 		  #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,   #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY   #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 	  #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE   #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.	  #
###########################################################################

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from xrftomo.file_io.reader import *
from xrftomo.file_io.writer import *

from xrftomo.reco import *
from xrftomo.elements import *
from xrftomo.widgets.custom_view_box import *
from xrftomo.widgets.difference_view import *
from xrftomo.widgets.scatter_view import *
from xrftomo.widgets.mini_recon_view import *

from xrftomo.models.element_table import *
from xrftomo.models.file_table import *
from xrftomo.widgets.file_loader import *

from xrftomo.widgets.image_process import *
from xrftomo.widgets.image_process_controls import *
from xrftomo.widgets.image_view import *
from xrftomo.widgets.image_process_actions import *

from xrftomo.widgets.reconstruction import *
from xrftomo.widgets.reconstruction_controls import *
from xrftomo.widgets.reconstruction_view import *
from xrftomo.widgets.reconstruction_actions import *

from xrftomo.widgets.sinogram import *
from xrftomo.widgets.sinogram_controls import *
from xrftomo.widgets.sinogram_view import *
from xrftomo.widgets.sinogram_actions import *

from xrftomo.widgets.lami import *
from xrftomo.widgets.lami_controls import *
from xrftomo.widgets.lami_view import *
from xrftomo.widgets.lami_actions import *

from xrftomo.menu_installer import *

try:
    import pkg_resources
    __version__ = pkg_resources.working_set.require("xrftomo")[0].version
except:
    pass
