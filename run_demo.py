## -*- coding: utf-8 -*-
"""
Created on Wed 03 Feb 2021

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
import sys
import argparse
from cgt.regionselectionapp import RegionSelectionApp

def get_args():
    """
    use argparse to get the video file name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", type=str, required=True, help="input file")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    application = RegionSelectionApp(sys.argv, args.video)
