import os
import time


def parse(line, qargs):
    '''
    line:
        a line of text
    qargs:
        query arguments
    return:
        a dict of gpu infos
    Pasing a line of csv format text returned by nvidia-smi
    解析一行nvidia-smi返回的csv格式文本
    '''
    numberic_args = ['memory.free', 'memory.total', 'power.draw', 'power.limit']  # 可计数的参数
    power_manage_enable = lambda v: (not 'Not Support' in v)  # lambda表达式，显卡是否滋瓷power management（笔记本可能不滋瓷）
    to_numberic = lambda v: float(v.upper().strip().replace('MIB', '').replace('W', ''))  # 带单位字符串去掉单位
    process = lambda k, v: (
        (int(to_numberic(v)) if power_manage_enable(v) else 1) if k in numberic_args else v.strip())
    return {k: process(k, v) for k, v in zip(qargs, line.strip().split(','))}


def query_gpu(qargs=[]):
    '''
    qargs:
        query arguments
    return:
        a list of dict
    Querying GPUs infos
    查询GPU信息
    '''
    qargs = ['index', 'gpu_name', 'memory.free', 'memory.total', 'power.draw', 'power.limit'] + qargs
    cmd = 'nvidia-smi --query-gpu={} --format=csv,noheader'.format(','.join(qargs))
    results = os.popen(cmd).readlines()
    return [parse(line, qargs) for line in results]


class GPUManager(object):
    '''
    qargs:
        query arguments
    A manager which can list all available GPU devices
    and sort them and choice the most free one.Unspecified
    ones pref.
    GPU设备管理器，考虑列举出所有可用GPU设备，并加以排序，自动选出
    最空闲的设备。在一个GPUManager对象内会记录每个GPU是否已被指定，
    优先选择未指定的GPU。
    '''

    def __init__(self, qargs=[]):
        '''
        '''
        self.qargs = qargs
        self.gpus = query_gpu(qargs)
        for gpu in self.gpus:
            gpu['specified'] = False
        self.gpu_num = len(self.gpus)

    def wait_memory(self, mem_size):
        res = []
        while not res:
            time.sleep(0.5)
            info_gpus = query_gpu()
            for one_dic in info_gpus:
                if one_dic["memory.free"] > mem_size:
                    res.append(one_dic["index"])
        return res


if __name__ == '__main__':
    import sys

    gm = GPUManager()
    print(" ".join(sys.argv[2:]))
    gpus = gm.wait_memory(int(sys.argv[1]))
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpus[0])
    print(gpus[0])
    os.system(" ".join(sys.argv[2:]))
