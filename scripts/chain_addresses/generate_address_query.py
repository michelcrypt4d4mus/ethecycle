#from ethecycle.util.string_helper import quoted_join

import re
from typing import Any, Callable, Iterable, List, Optional
from urllib.parse import parse_qs


def quoted_join(_list: Iterable[Any], quote_char: str = "'", separator: str = ', ', func: Callable = str) -> str:
    """
    Return a comma separated list of strings quoted by 'quote_char'. If 'func' arg is provided
    the output of calling it on each element of the list will be used instead of str().
    """
    quoted_list = [f"{quote_char}{func(item)}{quote_char}" for item in _list]
    return separator.join(quoted_list)

addresses = """
0x48627335FdDFd35f35ea8CCf08F5045e57388B3
0×676aecc97bf721c3cb3329a22d49c0ea0ed375f7
0xA294cCa691e4C83B1fc0c8d63D9a3eeF0A196DE1
0x530e0A6993eA99ffc96615aF43f327225a5fe536
0xF30026fe8a2C0D01b70B1949Ceaf2e09EFd8B4A5
0x845cbCb8230197F733b59cFE1795F282786f212C
0x3BA2166477F48273f41d241AA3722FFb9E07E247
0x26994D7c461a91Ef532447058C10b18D9DD8D43A
0x0349923aE2B35FF4f0099869aeea99d1f3FD12a9
0x4a4A3Cb97559fC531715362Bc41A31B192448a35
""".split()


query = 'SELECT * FROM wallets WHERE address LIKE '
query += quoted_join(addresses, separator='\n OR address LIKE ')
print(query)
