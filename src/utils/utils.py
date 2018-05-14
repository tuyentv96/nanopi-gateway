import string
import random

def randomString(size=8, chars=string.ascii_letters + string.digits):
    """
    Returns a string of random characters, useful in generating temporary
    passwords for automated password resets.

    size: default=8; override to provide smaller/larger passwords
    chars: default=A-Za-z0-9; override to provide more/less diversity

    Credit: Ignacio Vasquez-Abrams
    Source: http://stackoverflow.com/a/2257449
    """
    return ''.join(random.choice(chars) for i in range(size))

def parseMessage(instr):
    prefix = instr.find('|')
    delimiter = instr.find('#')
    if prefix < 0 or delimiter < 0:
        return None
    return instr[delimiter+1:]