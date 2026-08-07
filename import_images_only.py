"""只补图片：上传附件到已有的 memo，不新建"""
import json
import time
from datetime import datetime
import requests

token = open('token.txt').read().strip()
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}
host = 'http://your-memos-host:5230'  # 改成你的 memos 站点地址

# 1. 拉取所有 memo，建立 createTime -> memo_name 映射
all_memos = []
page_token = ''
while True:
    resp = requests.get(f'{host}/api/v1/memos', headers=headers, params={
        'limit': 100, 'pageToken': page_token
    })
    data = resp.json()
    memos = data.get('memos', [])
    all_memos.extend(memos)
    page_token = data.get('nextPageToken', '')
    if not page_token or not memos:
        break

time_to_memo = {}
for m in all_memos:
    time_to_memo[m.get('createTime', '')] = m['name']
print(f'已加载 {len(all_memos)} 条 memo')

# 2. 找出有附件的笔记
flomo = json.load(open('flomo/myMemos.json', encoding='utf-8'))
with_files = [m for m in flomo if m['filePath'] != 'None']
print(f'有附件的笔记: {len(with_files)} 条')

# 3. 逐个上传附件
import base64, os

total = 0
skipped = 0

for flomo in with_files:
    dt = datetime.strptime(flomo['time'], '%Y-%m-%d %H:%M:%S')
    ct = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    memo_name = time_to_memo.get(ct)
    
    if not memo_name:
        print(f'[跳过] 未找到匹配 memo: {flomo["time"]}')
        skipped += 1
        continue

    for file_path in flomo['filePath']:
        full_path = 'flomo/' + file_path
        if not os.path.exists(full_path):
            print(f'  [跳过] 文件不存在: {file_path}')
            skipped += 1
            continue

        file_name = os.path.basename(file_path)
        ext = file_path.lower()
        mime_type = (
            'image/jpeg' if ext.endswith(('.jpg', '.jpeg')) else
            'image/png' if ext.endswith('.png') else
            'image/gif' if ext.endswith('.gif') else
            'image/webp' if ext.endswith('.webp') else
            'application/octet-stream'
        )

        with open(full_path, 'rb') as f:
            content_b64 = base64.b64encode(f.read()).decode('utf-8')

        try:
            resp = requests.post(f'{host}/api/v1/attachments', headers=headers, json={
                'filename': file_name,
                'content': content_b64,
                'type': mime_type,
                'memo': memo_name,
            })
            if resp.status_code == 200:
                att_name = resp.json().get('name', '?')
                total += 1
                print(f'  ✅ {file_name} -> {att_name}')
            else:
                print(f'  ❌ {file_name}: HTTP {resp.status_code} {resp.text[:100]}')
                skipped += 1
        except Exception as e:
            print(f'  ❌ {file_name}: {e}')
            skipped += 1

        time.sleep(1.5)

    print(f'已完成 {flomo["time"]} ({len(flomo["filePath"])} 个文件)')

print(f'\n===== 完成 =====')
print(f'成功: {total} 个附件')
print(f'跳过: {skipped} 个')
print(f'无重复，图片已挂到已有的 memo 上！')
