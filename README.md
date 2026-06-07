# BCSV - 社会主义核心价值观编解码工具

用社会主义核心价值观（富强、民主、文明、和谐……）对任意文本进行编解码。

本项目提供两种互不兼容的编码算法，均改写自已有开源/公开代码。

## 项目结构

```
├── bcsv.py      # 算法一：BCSV（Base Core Socialist Values）
├── bcsv2.py     # 算法二：CV-V2（CTF 变体 / BCSV2 算法）
```

## 算法一：bcsv.py（BCSV）

**来源：** 改写自 [QSCTech/BaseCoreSocialistValues](https://github.com/QSCTech/BaseCoreSocialistValues) Rust 版（作者 YangKeao，MIT 协议）。

**原理：** 将原始字节直接编码为价值观词汇。

- 12 个词分为 3 组（国家层、社会层、个人层），每个字节从每组各选 1 个词
- 字节的低 2 位决定 3 个词的排列顺序（4 种排列），实现确定性混淆
- 每个字节 → 3 个词（6 个汉字）
- **同输入必定同输出（确定性）**

### 用法

```bash
# 直接编码
python bcsv.py -e "Hello"
# → 文明自由敬业公正民主敬业和谐公正敬业和谐公正敬业敬业公正和谐

# 直接解码
python bcsv.py -d "文明自由敬业公正民主敬业和谐公正敬业和谐公正敬业敬业公正和谐"
# → Hello

# 管道编码
echo "Hello" | python bcsv.py

# 文件解码
python bcsv.py -d 文件.txt
```

## 算法二：bcsv2.py（CV-V2 / 熊2）

**来源：** 改写自 [长亭百川云在线工具箱](https://rivers.chaitin.cn/tools/) 的社会主义核心价值观编码 JavaScript 实现。

**原理：** 文本 → URL 编码 → 十六进制 → 十二进制 → 价值观词映射。

1. 将文本进行 URL 编码得到十六进制串（如 `E4B880...`）
2. 每个 hex 字符（0-F）转为十二进制（0-11）
3. 0-9 直接映射，A-F（10-15）有两条随机等效路径：`[10, n-10]` 或 `[11, n-6]`
4. 每个十二进制值映射到一个核心价值观词（0→富强, 1→民主, ..., 11→友善）
5. **同输入多次编码结果可能不同（A-F 随机双路径）**

### 用法

```bash
# 编码（每次输出可能不同）
python bcsv2.py -e "Hello"

# 解码
python bcsv2.py -d "公正公正公正诚信文明公正民主公正法治法治..."
```

## 两种算法对比

| | bcsv (算法一) | bcsv2 (算法二) |
|---|---|---|
| 输入单位 | 二进制字节 | UTF-8 文本 |
| 编码粒度 | 每字节 → 3 个词（6 字） | 每 hex 字符 → 1~2 个词 |
| 随机性 | 确定性，同入同出 | A-F 有随机双路径 |
| 典型来源 | Rust crate BCSV | CTF 竞赛 / 百川云 |
| 互通性 | 互不兼容 | 互不兼容 |

## 致谢

- bcsv 算法源自 [QSCTech/BaseCoreSocialistValues](https://github.com/QSCTech/BaseCoreSocialistValues) (MIT)
- bcsv2 算法改写自 [长亭百川云](https://rivers.chaitin.cn/tools/) 在线工具箱的 JavaScript 版本

## License

MIT
