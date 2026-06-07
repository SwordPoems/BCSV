#!/usr/bin/env python3
"""
BCSV (Base Core Socialist Values) - 用社会主义核心价值观编码/解码数据

用法:
  python bcsv.py -e "文本"       # 直接编码
  python bcsv.py -d "编码"       # 直接解码
  python bcsv.py [文件]          # 文件/stdin编码
  python bcsv.py -d [文件]       # 文件/stdin解码
"""

import sys
import argparse

# 12个社会主义核心价值观，每2字一词
WORDS = [
    "富强", "民主", "文明", "和谐",   # group 0
    "自由", "平等", "公正", "法治",   # group 1
    "爱国", "敬业", "诚信", "友善",   # group 2
]

# 词到索引的映射
WORD_TO_IDX = {w: i for i, w in enumerate(WORDS)}

# BCSV中所有出现过的字节（用于过滤解码输入）
BYTE_SET = set()
for w in WORDS:
    for b in w.encode("utf-8"):
        BYTE_SET.add(b)


def encode_byte(byte: int) -> str:
    """将单个字节编码为3个词（6个汉字）"""
    order = byte & 0b11
    w0 = WORDS[(byte >> 2) & 0b11]       # group 0
    w1 = WORDS[4 + ((byte >> 4) & 0b11)]  # group 1
    w2 = WORDS[8 + ((byte >> 6) & 0b11)]  # group 2

    if order == 0:
        return w0 + w1 + w2
    elif order == 1:
        return w1 + w0 + w2
    elif order == 2:
        return w1 + w2 + w0
    else:  # order == 3
        return w2 + w1 + w0


def encode(data: bytes) -> str:
    """编码字节数据为BCSV字符串"""
    return "".join(encode_byte(b) for b in data)


def detect_order(words: list) -> int:
    """根据3个词的组别判断排列顺序"""
    g0 = WORD_TO_IDX[words[0]] // 4
    g1 = WORD_TO_IDX[words[1]] // 4
    g2 = WORD_TO_IDX[words[2]] // 4

    if g0 == 0 and g1 == 1 and g2 == 2:
        return 0
    elif g0 == 1 and g1 == 0 and g2 == 2:
        return 1
    elif g0 == 1 and g1 == 2 and g2 == 0:
        return 2
    elif g0 == 2 and g1 == 1 and g2 == 0:
        return 3
    else:
        raise ValueError(f"无效的BCSV词序: {words}")


def decode_char(three_words: list) -> int:
    """将3个词解码为一个字节"""
    order = detect_order(three_words)

    if order == 0:
        w0, w1, w2 = three_words[0], three_words[1], three_words[2]
    elif order == 1:
        w0, w1, w2 = three_words[1], three_words[0], three_words[2]
    elif order == 2:
        w0, w1, w2 = three_words[2], three_words[0], three_words[1]
    else:  # order == 3
        w0, w1, w2 = three_words[2], three_words[1], three_words[0]

    return order + ((WORD_TO_IDX[w0] % 4) << 2) + ((WORD_TO_IDX[w1] % 4) << 4) + ((WORD_TO_IDX[w2] % 4) << 6)


def decode(text: str) -> bytes:
    """解码BCSV字符串为原始字节"""
    # 过滤：只保留BCSV字符集中的字节
    raw = text.encode("utf-8")
    filtered = bytes(b for b in raw if b in BYTE_SET)

    if len(filtered) % 6 != 0:
        raise ValueError(f"解码输入长度必须是6的倍数（每个编码字节=6字节UTF8），当前为{len(filtered)}")

    result = bytearray()
    # 每6字节为1个词（2个汉字），每18字节（3个词）解码为1个原始字节
    for i in range(0, len(filtered), 18):
        chunk = filtered[i:i + 18]
        word_bytes = [chunk[j:j + 6] for j in range(0, 18, 6)]
        words = [wb.decode("utf-8") for wb in word_bytes]
        result.append(decode_char(words))

    return bytes(result)


def main():
    parser = argparse.ArgumentParser(
        description="BCSV - Base Core Socialist Values 编码/解码工具"
    )
    parser.add_argument(
        "-e", "--encode",
        help="编码模式：将文本转换为BCSV词串"
    )
    parser.add_argument(
        "-d", "--decode", nargs="?", const="__FILE__",
        help="解码模式：带参数直接解码BCSV词串，无参数从文件/stdin读取"
    )
    parser.add_argument(
        "file", nargs="?", default="-",
        help="输入文件，默认为标准输入（使用 - 也表示标准输入）"
    )
    args = parser.parse_args()

    # -e 模式：直接编码命令行参数中的文本
    if args.encode:
        try:
            result = encode(args.encode.encode("utf-8"))
            print(result)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # -d 带参数：直接解码命令行参数中的BCSV词串
    if args.decode and args.decode != "__FILE__":
        try:
            result = decode(args.decode)
            try:
                text = result.decode("utf-8")
                print(text)
            except UnicodeDecodeError:
                print(result.hex())
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # 文件/stdin模式
    if args.file == "-":
        data = sys.stdin.buffer.read()
    else:
        try:
            with open(args.file, "rb") as f:
                data = f.read()
        except FileNotFoundError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)

    try:
        if args.decode == "__FILE__":
            # -d 无参数：文件解码
            result = decode(data.decode("utf-8"))
            sys.stdout.buffer.write(result)
        else:
            # 默认：文件编码
            result = encode(data)
            sys.stdout.write(result)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
