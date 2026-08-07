import json
import time
from datetime import datetime

from memos.api import upFile, upMemo, deleteMemo
from memos.util import timeToUnix


def add():
    # 倒叙渐新插入符合时间感官
    flomoData = sorted(json.load(open("flomo/myMemos.json", encoding="UTF-8")), key=lambda k: k['time'])

    for flomo in flomoData:

        # 无内容纯图片则跳过, 按你的需要是否注释
        # if flomo['content'] == 'None':
        #     continue

        # 跳过空内容且无附件的笔记
        if flomo['content'] == 'None' and flomo['filePath'] == 'None':
            continue

        # 内容处理：先创建 memo（memos v1 需要先有 memo 再关联附件）
        dt = datetime.strptime(flomo['time'], "%Y-%m-%d %H:%M:%S")
        ct = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        msg = "\n".join(flomo['content']) if flomo['content'] != 'None' else ''
        msgObject = upMemo(ct, msg)
        memo_name = msgObject['name']
        time.sleep(0.5)

        # 文件处理：上传附件并关联到刚创建的 memo
        if flomo['filePath'] != "None":
            for f in flomo['filePath']:
                try:
                    upFile(f, memo_name)
                    time.sleep(1.5)
                except Exception as e:
                    print(f'[跳过] 文件上传失败 {f}: {e}')

        print(f'已完成 {flomo["time"]}')


def delete(many):
    for i in range(many):
        deleteMemo(i)


if __name__ == '__main__':
    # delete(400)   # 删除ID小于many的memo, 删除了memo就能一键删除图片啦, 防止不满意的你!!!
    add()
