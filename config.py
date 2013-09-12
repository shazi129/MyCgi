import os
import logging

CFG_PATH = os.path.split(os.path.realpath(__file__))[0]

LOG_CFG = {
    "dir":"../log",
    "level":logging.DEBUG,
    "prefix":"interface",
    "enable":True,
    "to_stream": False
}

