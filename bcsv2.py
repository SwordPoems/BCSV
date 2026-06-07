#!/usr/bin/env python3
"""
BCSV2 (Core Values Encoding V2) - 社会主义核心价值观编解码工具（JavaScript版算法移植）

与bcsv的区别：
  - bcsv是将每个原始字节编码为3个词（6汉字），有order排列混淆
  - bcsv2是将文本先URL编码为hex，再将每个hex字符转十二进制，每个十二进制位映射为一个词

用法:
  python bcsv2.py -e "文本"     # 编码（每次结果可能不同，A-F有随机双路径）
  python bcsv2.py -d "编码"     # 解码为文本
"""

import sys
import argparse
import random
import re
import urllib.parse

# 12个社会主义核心价值观串联为24字串
VALUES = "富强民主文明和谐自由平等公正法治爱国敬业诚信友善"

# 十二进制值 → 词（2字）
# 0→富强, 1→民主, 2→文明, 3→和谐, 4→自由, 5→平等, 6→公正, 7→法治, 8→爱国, 9→敬业, 10→诚信, 11→友善
VALUE_TO_WORD = {i: VALUES[2 * i:2 * i + 2] for i in range(12)}

# 构建词→十二进制值的映射（通过字符索引/2）
WORD_TO_VALUE = {}
for i in range(12):
    word = VALUES[2 * i:2 * i + 2]
    WORD_TO_VALUE[word] = i


def str2utf8(s: str) -> str:
    """
    将字符串转为URL编码hex串（大写），去掉%。
    对应JS的 str2utf8：
      1. 先用regex替换 [A-Za-z0-9-_.!~*'()] 为codepoint hex
      2. 再 encodeURIComponent
      3. 去掉 %，转大写
    """
    not_encoded = re.compile(r"[A-Za-z0-9\-_.!~*'()]")
    str1 = not_encoded.sub(lambda m: format(ord(m.group()), "X"), s)
    str2 = urllib.parse.quote(str1, safe="")
    return str2.upper().replace("%", "")


def utf82str(hexs: str) -> str:
    """将hex串还原为原始字符串（逆URL编码）"""
    # 每2个hex字符插入一个%
    parts = []
    for i in range(0, len(hexs), 2):
        parts.append("%" + hexs[i:i + 2])
    return urllib.parse.unquote("".join(parts))


def hex2duo(hexs: str) -> list:
    """hex字符串 → 十二进制数组。
    A-F有两条随机路径： [10, n-10] 或 [11, n-6]
    """
    duo = []
    for c in hexs:
        n = int(c, 16)
        if n < 10:
            duo.append(n)
        else:
            if random.random() >= 0.5:
                duo.append(10)
                duo.append(n - 10)
            else:
                duo.append(11)
                duo.append(n - 6)
    return duo


def duo2hex(duo: list) -> str:
    """十二进制数组 → hex字符串"""
    hex_parts = []
    i = 0
    while i < len(duo):
        v = duo[i]
        if v < 10:
            hex_parts.append(v)
        elif v == 10:
            i += 1
            hex_parts.append(duo[i] + 10)
        else:  # v == 11
            i += 1
            hex_parts.append(duo[i] + 6)
        i += 1
    return "".join(format(h, "X") for h in hex_parts)


def duo2values(duo: list) -> str:
    """十二进制数组 → 价值观词串"""
    return "".join(VALUE_TO_WORD[d] for d in duo)


def values2duo(encoded: str) -> list:
    """价值观词串 → 十二进制数组"""
    duo = []
    # 遍历字符串中每个字符
    for c in encoded:
        i = VALUES.find(c)
        if i == -1:
            continue  # 跳过非价值观字符
        if i & 1:  # 奇数索引 → 词的第二个字，跳过
            continue
        duo.append(i >> 1)  # 偶数索引 → 词头，值=index/2
    return duo


def encode(text: str) -> str:
    """编码文本为价值观词串"""
    hexs = str2utf8(text)
    duo = hex2duo(hexs)
    return duo2values(duo)


def decode(bcsv_text: str) -> str:
    """解码价值观词串为原始文本"""
    duo = values2duo(bcsv_text)
    hexs = duo2hex(duo)
    return utf82str(hexs)


def main():
    parser = argparse.ArgumentParser(
        description="BCSV2 - 社会主义核心价值观编解码工具"
    )
    parser.add_argument(
        "-e", "--encode",
        help="编码模式：将文本转换为价值观词串"
    )
    parser.add_argument(
        "-d", "--decode",
        help="解码模式：将价值观词串还原为文本"
    )
    args = parser.parse_args()

    if not args.decode and not args.encode:
        parser.print_help()
        sys.exit(1)

    try:
        if args.encode:
            result = encode(args.encode)
            print(result)
        elif args.decode:
            result = decode(args.decode)
            print(result)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
