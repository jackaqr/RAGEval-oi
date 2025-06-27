import requests, json, os


class AgentStreamResponse:
    def post_chatwiki(self, question):
        url = "http://localhost:18080/chat/request"

        data = {
            "robot_key": "z3plaq20uv",
            "openid": "1",
            "question": question,
            "form_ids": "",
            "dialogue_id": "383",
            "global": {"robot_key": "z3plaq20uv", "id": "7"},
        }

        rsp = requests.post(url, data=data, stream=True, timeout=300)

        references, content = self.parse_chatwiki_rsp(rsp)
        return references, content

    def parse_chatwiki_rsp(self, rsp):
        references = []
        content = ""

        for line in rsp.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").strip()

                # print(decoded_line)

                if decoded_line.startswith("event:"):
                    event_type = decoded_line.split(":", 1)[1].strip()

                    if event_type in ["quote_file", "data"]:
                        next_event_data = event_type
                    else:
                        next_event_data = None
                elif decoded_line.startswith("data:"):
                    data_contents = decoded_line[5:].strip()
                    if next_event_data:

                        data_contents = json.loads(data_contents)

                        if next_event_data == "quote_file":
                            for data_content in data_contents:
                                file_name = data_content["file_name"]
                                answer_source_data = json.loads(
                                    data_content["answer_source_data"]
                                )

                                for per_asd in answer_source_data:
                                    references.append(
                                        {
                                            "title": file_name,
                                            "content": per_asd["content"],
                                        }
                                    )
                        elif next_event_data == "data":
                            content = data_contents["content"]

                    next_event_data = None

        return references, content


def clean_answer(answer):
    # return re.sub(r"\s+##\d+\$\$", "", answer.strip())
    return answer


def write_result(line, res, fpath):
    if res:
        line_dict = json.loads(line)  # 源jsonl内容
        references, content = res  # 知识库返回内容

        line_dict["prediction"] = {"content": content, "references": references}

        with open(fpath, "a") as f:
            f.write(json.dumps(line_dict, ensure_ascii=False) + "\n")
    else:
        raise Exception("query result is empty.")


def process_line_and_write(args):
    line, fpath, agent_stream_response = args
    line = line.strip()
    if not line:
        return
    try:
        question = json.loads(line)["query"]["content"]
        res = agent_stream_response.post_chatwiki(question)
        print(res, flush=True)
        while not res[0]: # 确保都能有结果
            res = agent_stream_response.post_chatwiki(question)
            print(res, flush=True)
        write_result(line, res, fpath)
    except Exception as e:
        raise Exception(f"Error processing line: {e}")


def query_chatwiki(project_type):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    query_file = os.path.join(SCRIPT_DIR, "query.jsonl")
    query_done_file = os.path.join(SCRIPT_DIR, f"../data/{project_type}.jsonl")

    with open(query_done_file, "w") as f:
        f.write("")

    agent_stream_response = AgentStreamResponse()

    with open(query_file, "r") as f:
        lines = [
            (line.strip(), query_done_file, agent_stream_response)
            for line in f
            if line.strip()
        ]

    from multiprocessing import Pool, cpu_count

    num_processes = 50
    with Pool(processes=num_processes) as pool:
        pool.map(process_line_and_write, lines[:160])  # 测试前160个问题

    # process_line_and_write(lines[159])


if __name__ == "__main__":
    query_chatwiki("chatwiki")
