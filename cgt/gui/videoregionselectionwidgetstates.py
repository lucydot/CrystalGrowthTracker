## -*- coding: utf-8 -*-
"""
Created on Wed 10 Feb 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
from enum import IntEnum

class VideoRegionSelectionWidgetStates(IntEnum):
    """
    specify the number of the pages in the wizard
    """
    VIEW = 0
    CREATE = 2
    EDIT = 4
    DISPLAY = 8
    DELETE = 16
