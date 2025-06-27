import requests
import json
import re
import os


class AgentStreamResponse:
    def __init__(self):
        self.api_host = "http://localhost:82"
        self.api_key = "ragflow-I2YThjMjU0NTBhZjExZjBiMzI3MDI0Mm"
        self.agent_id = "5fcdd62c500111f0a7f20242ac1c0006"

        self.url = self.api_host + "/api/v1/agents/" + self.agent_id + "/completions"

        self.headers = {
            "Authorization": "Bearer %s" % self.api_key,
            "Content-Type": "application/json",
        }

    def get_session_id(self):
        """
        获取会话 ID
        """
        data = {"id": self.agent_id}
        response = requests.post(self.url, data=data, headers=self.headers)
        try:
            line_list = []
            with requests.post(
                self.url, json=data, headers=self.headers, stream=True, timeout=30
            ) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:  # 过滤掉空行
                            # print(line.decode("utf-8"))
                            line_list.append(line.decode("utf-8"))
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    return False

            # print("line_list",line_list)

            first_line = line_list[0]
            # 提取data内容
            line_row = first_line.split("data:")[1]
            # json解析
            line_dict = json.loads(line_row)
            # 获取session_id
            session_id = line_dict["data"]["session_id"]
            return session_id
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return False

    def get_stream_data(self, session_id, question):
        """
        获取流式数据
        """
        try:
            # session_id = self.get_session_id()
            data = {
                "id": self.agent_id,
                "question": question,
                "stream": "true",
                "session_id": session_id,
            }

            line_list = []
            with requests.post(
                self.url, json=data, headers=self.headers, stream=True, timeout=30
            ) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:  # 过滤掉空行
                            # print(line.decode("utf-8"))
                            line_list.append(line.decode("utf-8"))
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    return False

            print(line_list[-2])
            print(type(line_list[-2]))
            return line_list[-2]
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return False


def clean_answer(answer):
    tmp = re.sub(r"\s+##\d+\$\$", "", answer.strip())
    res = re.sub(r"\s+\[ID:\d+\]", "", tmp.strip())

    return res


def write_result(line, res, fpath):
    if res:
        line_dict = json.loads(line)  # 源jsonl内容
        res_dict = json.loads(res)  # 知识库返回内容
        answer = clean_answer(res_dict["data"]["answer"])
        line_dict["prediction"]["content"] = answer
        line_dict["prediction"]["references"] = [
            {"title": chunk["document_name"], "content": chunk["content"]}
            for chunk in res_dict["data"]["reference"]["chunks"]
        ]

        with open(fpath, "a") as f:
            f.write(json.dumps(line_dict, ensure_ascii=False) + "\n")
    else:
        raise Exception("query result is empty.")


def process_line_and_write(args):
    line, session_id, fpath, agent_stream_response = args
    line = line.strip()
    if not line:
        return
    try:
        question = json.loads(line)["query"]["content"]
        res = agent_stream_response.get_stream_data(session_id, question).removeprefix(
            "data:"
        )
        print(res, flush=True)
        write_result(line, res, fpath)
    except Exception as e:
        print(f"Error processing line: {e}")


def query_ragflow(project_type):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    query_file = os.path.join(SCRIPT_DIR, "query.jsonl")
    query_done_file = os.path.join(SCRIPT_DIR, f"../data/{project_type}.jsonl")

    with open(query_done_file, "w") as f:
        f.write("")

    agent_stream_response = AgentStreamResponse()

    session_id = agent_stream_response.get_session_id()

    with open(query_file, "r") as f:
        lines = [
            (line.strip(), session_id, query_done_file, agent_stream_response)
            for line in f
            if line.strip()
        ]

    from multiprocessing import Pool, cpu_count

    num_processes = 50
    with Pool(processes=num_processes) as pool:
        pool.map(process_line_and_write, lines[:160])  # 测试前160个问题

    # process_line_and_write(lines[1])


if __name__ == "__main__":
    query_ragflow("ragflow")
