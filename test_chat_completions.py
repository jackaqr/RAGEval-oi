import requests, time, asyncio, httpx, os


def get_models(token):
    url = os.path.join(URL, "api/models")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers)

    models = []
    for model in response.json()["data"]:
        models.append(model["id"])
    print("Modules:\n", models)

    free_models = []
    for model in models:
        if "free" in model:
            free_models.append(model)
    print("Free Modules:\n", free_models)
    return models


def upload_files(token):
    url = os.path.join(URL, "api/v1/files")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        #"Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    files = {
        "file": (
            "公司年报_环保_0.txt",
            open("/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/qar_generation/output/finance/zh/doc/0/公司年报_环保_0.txt", "rb"),
            "text/plain"
        )
    }
    response = requests.post(url, headers=headers, files=files)
    return response.json()

def upload_folders(token, folder_path):
    """
    批量上传文件夹中的文件
    
    Args:
        token (str): 认证token
        folder_path (str): 文件夹路径
    """
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return
    
    # 文件类型映射
    mime_types = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.txt': 'text/plain'
    }
    
    # 遍历文件夹
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # 获取文件MIME类型
            file_type = mime_types.get(file_ext)
            if not file_type:
                print(f"跳过不支持的文件类型: {filename}")
                continue
            
            # 上传文件
            url = os.path.join(URL, "api/v1/files")
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            }
            
            try:
                with open(file_path, "rb") as file:
                    files = {
                        "file": (filename, file, file_type)
                    }
                    response = requests.post(url, headers=headers, files=files)
                    response.raise_for_status()
                    print(f"文件上传成功: {filename}")
                    
            except Exception as e:
                print(f"文件上传失败 {filename}: {str(e)}")


async def concurrency_test(url, data, headers, total_requests):
    async def _single_request(client, url, data, headers, req_index):
        t1 = time.time()
        try:
            response = await client.post(url, json=data, headers=headers, timeout=100)
            response.raise_for_status()  # 检查 HTTP 错误
            print(f"Request({req_index}) Response Status Code:", response.status_code)
            print(f"Request({req_index}) Response Body:", response.json())
        except httpx.HTTPStatusError as e:
            print(f"Request({req_index}) HTTP Error: {e}")
        except Exception as e:
            print(f"Request({req_index}) Request Failed: {e}")

        print(f"Query ID: {req_index}, Time Used: {time.time() - t1}")

    async with httpx.AsyncClient() as client:
        tasks = [
            _single_request(client, url, data, headers, req_index)
            for req_index in range(total_requests)
        ]
        results = await asyncio.gather(*tasks)


async def test_chat_completions(token, type, web_search_enabled, total_requests):
    url = os.path.join(URL, "api/chat/completions")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    data = {
        "model": "DeepSeek-R1",
        "messages": [{"role": "user", "content": "美国现任总统"}],
        "features": {"web_search": web_search_enabled},
    }

    if type == "web_search":
        pass
    elif type == "ocr":
        # first upload
        file_resp = upload_files(token)

        # # second
        # data["files"] = [
        #     {
        #         "type": "file",
        #         "id": file_resp["id"],
        #         "name": file_resp["filename"],
        #         "status": "uploaded",
        #     }
        # ]
        # data["messages"][0]["content"] = "这篇文章的主要内容"
    elif type == "upload_file":
        url = os.path.join(URL, "api/v1/files")
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        files = {
            "file": open(
                "/root/code/清程极智PPT2025年3月.pdf",
                "rb",
            ),
            "type": "application/pdf",
        }

    # await concurrency_test(url, data, headers, total_requests)


async def send_chat_completion(token, model, message, web_search_enabled=False):
    """
    发送聊天完成请求
    
    Args:
        token (str): 认证token
        model (str): 模型名称
        message (str): 用户消息内容
        web_search_enabled (bool): 是否启用网络搜索
    
    Returns:
        dict: API响应结果
    """
    url = "http://localhost:8888/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "features": {
            "web_search": web_search_enabled
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP错误: {e}")
            return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None

def get_files(token):
    url = os.path.join(URL, "api/v1/files")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers)
    return response.json()


if __name__ == "__main__":
    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIzMDI5MzI5LWRkNWEtNGE0NS04YmQ1LTQ2MDk5NGEyMDViMyJ9.RZ3q2EGLJfTXd7T-znevviSSZWy5sOsDzgiS_WmtK6I"

    # open_api_base_urls = {
    #     "http://106.39.85.225:8000/v1": ["Qwen2.5-7B-Instruct-1M"],
    #     "http://61.49.53.7:9001/v1": "DeepSeek-R1",
    # }

    # t1 = time.time()

    # type = "ocr"
    # # type = "web_search"
    # # type = "upload_file"
    # web_search_enabled = False
    # total_requests = 1

    # URL = "http://localhost:7901"

    # URL = "http://localhost:8888"
    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjgyMTZlNzgzLWQxZGEtNGNiMS1iZTQzLTUwY2Y3ODM0YjY0NCJ9.VRss5BLzy-aMo7NfpaYeBiMqwTrbm8rcu17DXhkIXng"

    URL = "http://localhost:9999"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjgyMTZlNzgzLWQxZGEtNGNiMS1iZTQzLTUwY2Y3ODM0YjY0NCJ9.VRss5BLzy-aMo7NfpaYeBiMqwTrbm8rcu17DXhkIXng"


    # asyncio.run(test_chat_completions(token, type, web_search_enabled, total_requests))

    # t2 = time.time()
    # print("Total Time:", t2 - t1)

    #upload_files(token)
    #get_models(token)

    #folder_path = "/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/qar_generation/output/finance/zh/doc/0"
    #upload_folders(token, folder_path)
    
    # 设置必要的参数
    
    # type = "web_search"  # 可选值: "web_search", "ocr", "upload_file"
    # web_search_enabled = True  # 是否启用网络搜索
    # total_requests = 1  # 并发请求数量

    # # 使用asyncio运行异步函数
    # asyncio.run(test_chat_completions(token, type, web_search_enabled, total_requests))

    # # 示例使用
    # model = "qwen2.5-7b-instruct"
    # message = "北京天气"
    
    # # 运行异步函数
    # response = asyncio.run(send_chat_completion(token, model, message, web_search_enabled))
    # if response:
    #     print("API响应:", response)
    response = get_files(token)
    print(response)