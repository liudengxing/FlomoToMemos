import os
import requests
import time
from memos.util import getType

# 需要修改 Host 与 token.txt
Host = 'http://your-memos-host:5230'  # 改成你的网址 结尾不要斜杠 例如: https://memos.thatcoder.cn
ApiBase = f'{Host}/api/v1'
ApiSignIn = ApiBase + '/auth/signin'
ApiAttachment = ApiBase + '/attachments'
ApiMemo = ApiBase + '/memos'



def getCookie():
    with open('token.txt', 'r') as c:
        Cookie = c.read()
    return Cookie


Headers = {
    # 'Cookie': getCookie(),    # 0.18版本左右改为    Authorization验证
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Referer': f'{Host}/auth',
    'Origin': Host,
    'Authorization': f'Bearer {getCookie()}'
}


def upFile(filePath, memo_name=None):
    """
    memos v1 API: 用 base64 JSON 上传附件到 /api/v1/attachments
    可选关联 memo_name (如 memos/xxx)，返回附件 name
    """
    import base64
    file_name = os.path.basename(filePath)
    with open("flomo/" + filePath, "rb") as f:
        file_data = f.read()
    content_b64 = base64.b64encode(file_data).decode('utf-8')
    mime_type = 'image/jpeg' if filePath.lower().endswith(('.jpg', '.jpeg')) else \
                'image/png' if filePath.lower().endswith('.png') else \
                'image/gif' if filePath.lower().endswith('.gif') else \
                'image/webp' if filePath.lower().endswith('.webp') else \
                'application/octet-stream'
    headers = Headers
    data = {
        'filename': file_name,
        'content': content_b64,
        'type': mime_type,
    }
    if memo_name:
        data['memo'] = memo_name
    response = requests.post(ApiAttachment, headers=headers, json=data)
    result = response.json()
    return result['name']


def upMemo(ct, msg):
    """
    memos v1 API: createTime 用 ISO 8601 格式字符串
    """
    headers = Headers
    data = {
        'createTime': ct,
        'content': msg,
        'visibility': 'PRIVATE',
    }
    response = requests.post(ApiMemo, headers=headers, json=data)
    return response.json()




def deleteMemo(MemoId):
    return requests.delete(ApiMemo + f'/{MemoId}', headers=Headers).text
