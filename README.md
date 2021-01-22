# Ontonotes 5.0

ontonotes 5.0 数据预处理，按照官方给的方式进行训练集、验证集、测试集的分割。

## 数据处理

### Step 0: clone代码到本地

### Step 1: 下载官方的OntoNote 5.0的数据

可以从这里下载 [https://catalog.ldc.upenn.edu/LDC2013T19](https://catalog.ldc.upenn.edu/LDC2013T19)
，这份指南可能可以帮助你下载 https://www.zhihu.com/question/67166283/answer/629915159 。然后将结果解压到代码所在的文件夹。
解码之后你的文件夹应该有如下结构（onotenotes-release-5.0是解压后得到的）

```
ontonotes
  -onotenotes-release-5.0/
  -conll-2012/
  -collect_conll.py
  -README.md
  -..
```

### Step 2: Running the script to recover words

1. 在当前文件夹打开终端，创建py27环境，并执行第一步数据处理

```
$ conda create --name py27 python=2.7
$ source activate py27
$ ./conll-2012/v3/scripts/skeleton2conll.sh -D ./ontonotes-release-5.0/data/files/data/ ./conll-2012/
```

2. 切换回python3环境

```
source deactivate
```

## 格式说明

(*) 生成的conll文件格式如下(根据需要选取所需要的列)

    1 Document ID : ``str``
        This is a variation on the document filename
    2 Part number : ``int``
        Some files are divided into multiple parts numbered as 000, 001, 002, ... etc.
    3 Word number : ``int``
        This is the word index of the word in that sentence.
    4 Word : ``str``
        This is the token as segmented/tokenized in the Treebank. Initially the ``*_skel`` file
        contain the placeholder [WORD] which gets replaced by the actual token from the
        Treebank which is part of the OntoNotes release.
    5 POS Tag : ``str``
        This is the Penn Treebank style part of speech. When parse information is missing,
        all part of speeches except the one for which there is some sense or proposition
        annotation are marked with a XX tag. The verb is marked with just a VERB tag.
    6 Parse bit: ``str``
        This is the bracketed structure broken before the first open parenthesis in the parse,
        and the word/part-of-speech leaf replaced with a ``*``. When the parse information is
        missing, the first word of a sentence is tagged as ``(TOP*`` and the last word is tagged
        as ``*)`` and all intermediate words are tagged with a ``*``.
    7 Predicate lemma: ``str``
        The predicate lemma is mentioned for the rows for which we have semantic role
        information or word sense information. All other rows are marked with a "-".
    8 Predicate Frameset ID: ``int``
        The PropBank frameset ID of the predicate in Column 7.
    9 Word sense: ``float``
        This is the word sense of the word in Column 3.
    10 Speaker/Author: ``str``
        This is the speaker or author name where available. Mostly in Broadcast Conversation
        and Web Log data. When not available the rows are marked with an "-".
    11 Named Entities: ``str``
        These columns identifies the spans representing various named entities. For documents
        which do not have named entity annotation, each line is represented with an ``*``.
    12+ Predicate Arguments: ``str``
        There is one column each of predicate argument structure information for the predicate
        mentioned in Column 7. If there are no predicates tagged in a sentence this is a
        single column with all rows marked with an ``*``.
    -1 Co-reference: ``str``
        Co-reference chain information encoded in a parenthesis structure. For documents that do
         not have co-reference annotations, each line is represented with a "-".

## Reference

http://conll.cemantix.org/2012/data.html

https://github.com/yuchenlin/OntoNotes-5.0-NER-BIO

https://github.com/ontonotes/conll-formatted-ontonotes-5.0

https://github.com/allenai/allennlp

https://github.com/yhcc/OntoNotes-5.0-NER

https://github.com/HuHsinpang/Ontonotes5.0-pretreatment
