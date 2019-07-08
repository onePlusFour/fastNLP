import os

from typing import Union, Dict


def check_dataloader_paths(paths:Union[str, Dict[str, str]])->Dict[str, str]:
    """
    检查传入dataloader的文件的合法性。如果为合法路径，将返回至少包含'train'这个key的dict。类似于下面的结果
    {
        'train': '/some/path/to/', # 一定包含，建词表应该在这上面建立，剩下的其它文件应该只需要处理并index。
        'test': 'xxx' # 可能有，也可能没有
        ...
    }
    如果paths为不合法的，将直接进行raise相应的错误

    :param paths: 路径. 可以为一个文件路径(则认为该文件就是train的文件); 可以为一个文件目录，将在该目录下寻找train(文件名
        中包含train这个字段), test.txt, dev.txt; 可以为一个dict, 则key是用户自定义的某个文件的名称，value是这个文件的路径。
    :return:
    """
    if isinstance(paths, str):
        if os.path.isfile(paths):
            return {'train': paths}
        elif os.path.isdir(paths):
            filenames = os.listdir(paths)
            files = {}
            for filename in filenames:
                path_pair = None
                if 'train' in filename:
                    path_pair = ('train', filename)
                if 'dev' in filename:
                    if path_pair:
                        raise Exception("File:{} in {} contains bot `{}` and `dev`.".format(filename, paths, path_pair[0]))
                    path_pair = ('dev', filename)
                if 'test' in filename:
                    if path_pair:
                        raise Exception("File:{} in {} contains bot `{}` and `test`.".format(filename, paths, path_pair[0]))
                    path_pair = ('test', filename)
                if path_pair:
                    files[path_pair[0]] = os.path.join(paths, path_pair[1])
            return files
        else:
            raise FileNotFoundError(f"{paths} is not a valid file path.")

    elif isinstance(paths, dict):
        if paths:
            if 'train' not in paths:
                raise KeyError("You have to include `train` in your dict.")
            for key, value in paths.items():
                if isinstance(key, str) and isinstance(value, str):
                    if not os.path.isfile(value):
                        raise TypeError(f"{value} is not a valid file.")
                else:
                    raise TypeError("All keys and values in paths should be str.")
            return paths
        else:
            raise ValueError("Empty paths is not allowed.")
    else:
        raise TypeError(f"paths only supports str and dict. not {type(paths)}.")

def get_tokenizer():
    try:
        import spacy
        spacy.prefer_gpu()
        en = spacy.load('en')
        print('use spacy tokenizer')
        return lambda x: [w.text for w in en.tokenizer(x)]
    except Exception as e:
        print('use raw tokenizer')
        return lambda x: x.split()