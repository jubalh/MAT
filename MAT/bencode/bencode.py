# Copyright 2007 by Petru Paler
# Copyright 2011 by Julien (jvoisin) Voisin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

'''
    A quick (and also nice) lib to bencode/bdecode torrent files
'''


import types


class BTFailure(Exception):
    '''Custom Exception'''
    pass


class Bencached(object):
    '''Custom type : cached string'''
    __slots__ = ['bencoded']

    def __init__(self, string):
        self.bencoded = string


def decode_int(x, f):
    '''decode an int'''
    f += 1
    newf = x.index('e', f)
    n = int(x[f:newf])
    if x[f] == '-':
        if x[f + 1] == '0':
            raise ValueError
    elif x[f] == '0' and newf != f + 1:
        raise ValueError
    return (n, newf + 1)


def decode_string(x, f):
    '''decode a string'''
    colon = x.index(':', f)
    n = int(x[f:colon])
    if x[f] == '0' and colon != f + 1:
        raise ValueError
    colon += 1
    return (x[colon:colon + n], colon + n)


def decode_list(x, f):
    '''decode a list'''
    result = []
    f += 1
    while x[f] != 'e':
        v, f = DECODE_FUNC[x[f]](x, f)
        result.append(v)
    return (result, f + 1)


def decode_dict(x, f):
    '''decode a dict'''
    result = {}
    f += 1
    while x[f] != 'e':
        k, f = decode_string(x, f)
        result[k], f = DECODE_FUNC[x[f]](x, f)
    return (result, f + 1)


def encode_bool(x, r):
    '''bencode a boolean'''
    if x:
        encode_int(1, r)
    else:
        encode_int(0, r)


def encode_int(x, r):
    '''bencode an integer/float'''
    r.extend(('i', str(x), 'e'))


def encode_list(x, r):
    '''bencode a list/tuple'''
    r.append('l')
    [ENCODE_FUNC[type(item)](item, r) for item in x]
    r.append('e')


def encode_dict(x, result):
    '''bencode a dict'''
    result.append('d')
    ilist = x.items()
    ilist.sort()
    for k, v in ilist:
        result.extend((str(len(k)), ':', k))
        ENCODE_FUNC[type(v)](v, result)
    result.append('e')


DECODE_FUNC = {}
DECODE_FUNC.update(dict([(str(x), decode_string) for x in xrange(9)]))
DECODE_FUNC['l'] = decode_list
DECODE_FUNC['d'] = decode_dict
DECODE_FUNC['i'] = decode_int


ENCODE_FUNC = {}
ENCODE_FUNC[Bencached] = lambda x, r: r.append(x.bencoded)
ENCODE_FUNC[types.IntType] = encode_int
ENCODE_FUNC[types.LongType] = encode_int
ENCODE_FUNC[types.StringType] = lambda x, r: r.extend((str(len(x)), ':', x))
ENCODE_FUNC[types.ListType] = encode_list
ENCODE_FUNC[types.TupleType] = encode_list
ENCODE_FUNC[types.DictType] = encode_dict
ENCODE_FUNC[types.BooleanType] = encode_bool


def bencode(string):
    '''bencode $string'''
    table = []
    ENCODE_FUNC[type(string)](string, table)
    return ''.join(table)


def bdecode(string):
    '''decode $string'''
    try:
        result, lenght = DECODE_FUNC[string[0]](string, 0)
    except (IndexError, KeyError, ValueError):
        raise BTFailure('Not a valid bencoded string')
    if lenght != len(string):
        raise BTFailure('Invalid bencoded value (data after valid prefix)')
    return result
