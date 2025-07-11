import requests, json, os, time

def main():
    pushplus_key = os.environ.get("PUSHPLUS_TOKEN", "")
    cookies = os.environ.get("GLADOS_COOKIE", "").split("&")
    
    # 空值判断修正
    if not cookies or not any(cookies):
        print("未获取到有效的COOKIE")
        if pushplus_key:
            requests.post(f"https://www.pushplus.plus/send", json={
                "token": pushplus_key,
                "title": "GLaDOS签到失败",
                "content": "未配置COOKIE"
            })
        return

    results = []
    url = "https://glados.rocks/api/user/checkin"
    status_url = "https://glados.rocks/api/user/status"
    
    headers = {
        'referer': 'https://glados.rocks/console/checkin',
        'origin': 'https://glados.rocks',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8'
    }
    
    for cookie in cookies:
        if not cookie.strip(): continue  # 跳过空cookie
        
        try:
            # 获取账号状态
            status_res = requests.get(status_url, headers={**headers, 'cookie': cookie})
            if status_res.status_code != 200:
                results.append(f"{cookie[:15]}... - 状态获取失败")
                continue
                
            # 执行签到
            payload = {'token': 'glados.one'}
            checkin_res = requests.post(url, headers={**headers, 'cookie': cookie}, 
                                       data=json.dumps(payload))
            
            # 处理结果
            user_data = status_res.json().get('data', {})
            email = user_data.get('email', '未知账号')
            left_days = str(user_data.get('leftDays', 0)).split('.')[0]
            
            if checkin_res.status_code == 200:
                res_data = checkin_res.json()
                message = res_data.get('message', '无状态信息')
                results.append(f"{email} - {message} - 剩余{left_days}天")
            else:
                results.append(f"{email} - 签到失败: HTTP {checkin_res.status_code}")
                
        except Exception as e:
            results.append(f"处理异常: {str(e)}")
    
    # 最终通知
    summary = "\n".join(results)
    print(f"签到结果:\n{summary}")
    
    if pushplus_key:
        requests.post("https://www.pushplus.plus/send", json={
            "token": pushplus_key,
            "title": "GLaDOS签到结果",
            "content": summary
        })

if __name__ == '__main__':
    main()
