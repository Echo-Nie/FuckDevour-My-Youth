from flask import Flask, request, jsonify, render_template
from neo4j import GraphDatabase
import threading
from import_medical_data import MedicalDataImporter
import requests

class DeepSeekAI:
    def __init__(self, api_key, base_url="https://api.siliconflow.cn/v1/"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def get_response(self, prompt, temperature=0.7, max_tokens=1000):
        payload = {
            "model": "deepseek-ai/DeepSeek-R1", # 使用deepseek-ai/DeepSeek-R1模型
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(f"{self.base_url}/chat/completions", headers=self.headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        result = response.json()
        return result['choices'][0]['message']['content']

app = Flask(__name__)

uri = "bolt://localhost:7687"
username = "NTSoftware-Devour-My-Youth"
password = "NTSoftware-Devour-My-Youth"
driver = GraphDatabase.driver(uri, auth=(username, password))

# 硅基流动的
DEEPSEEK_API_KEY = "NTSoftware-Devour-My-Youth"
DEEPSEEK_BASE_URL = "https://api.siliconflow.cn/v1/"
deepseek_ai = DeepSeekAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# 初始化状态标记
init_complete = False

def initialize_system():
    global init_complete
    try:
        importer = MedicalDataImporter()
        importer.run()
        init_complete = True
        print("系统初始化完成，数据已导入！")
    except Exception as e:
        print(f"初始化失败：{str(e)}")

def get_answer(question):
    """从Neo4j数据库中获取答案或使用大模型生成答案"""
    print(f"接收到问题: {question}")
    with driver.session() as session:
        result_qa = session.run("""
            MATCH (q:Question)-[:HAS_ANSWER]->(a:Answer)
            WHERE toLower(q.text) CONTAINS toLower($question)
            RETURN q.text as question, a.text as answer
            LIMIT 1
        """, question=question)
        
        record_qa = result_qa.single()
        if record_qa:
            print(f"从问答对中找到答案: {record_qa['answer']}")
            return record_qa['answer']
        
        print("问答对中未找到答案，尝试从知识图谱查询疾病信息...")
        # 如果问答对没有找到，尝试查询知识图谱中的疾病信息
        result_kg = session.run("""
            MATCH (d:SleepDisorder)
            WHERE toLower(d.name) CONTAINS toLower($question) OR toLower(d.description) CONTAINS toLower($question)
            OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s)
            OPTIONAL MATCH (d)-[:HAS_TREATMENT]->(t)
            OPTIONAL MATCH (d)-[:HAS_RISK_FACTOR]->(r)
            RETURN d.name as name, d.description as description, 
                   COLLECT(DISTINCT s.name) as symptoms, 
                   COLLECT(DISTINCT t.name) as treatments, 
                   COLLECT(DISTINCT r.name) as risk_factors
            LIMIT 1
        """, question=question)
        
        kg_record = result_kg.single()
        if kg_record and kg_record['name']:
            answer_text = f"{kg_record['name']}：{kg_record['description']}。"
            if kg_record['symptoms']: 
                answer_text += f"常见症状包括：{ '、'.join(kg_record['symptoms']) }。"
            if kg_record['treatments']: 
                answer_text += f"治疗方法包括：{ '、'.join(kg_record['treatments']) }。"
            if kg_record['risk_factors']: 
                answer_text += f"相关风险因素有：{ '、'.join(kg_record['risk_factors']) }。"
            print(f"从知识图谱中找到答案: {answer_text}")
            return answer_text

        print("在问答对和知识图谱中均未找到答案，尝试调用大语言模型...")
        # 如果知识图谱也没有找到，调用大语言模型
        try:
            llm_response = deepseek_ai.get_response(question, temperature=0.7, max_tokens=1000)
            print(f"大语言模型生成的答案: {llm_response}")
            return llm_response
        except Exception as e:
            print(f"调用大语言模型失败: {str(e)}")
            return "抱歉，大语言模型暂时无法提供答案。"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({'initialized': init_complete})

@app.route('/ask', methods=['POST'])
def ask():
    if not init_complete:
        return jsonify({'error': '系统正在初始化，请稍候...'}), 503
    
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    
    answer = get_answer(question)
    return jsonify({'answer': answer})

@app.route('/knowledge_graph')
def knowledge_graph_page():
    return render_template('knowledge_graph.html')

@app.route('/api/knowledge_graph_data')
def get_knowledge_graph_data():
    """获取知识图谱数据并返回vis.js所需的格式"""
    print("正在获取知识图谱数据...")
    
    try:
        with driver.session() as session:
            nodes = []
            relationships = []
            node_ids = set()

            disorders = session.run("""
                MATCH (d:SleepDisorder)
                RETURN id(d) as id, d.name as name, d.description as description
                ORDER BY d.name
            """)
            for record in disorders:
                node_id = str(record["id"])
                node_ids.add(node_id)
                nodes.append({
                    "id": node_id,
                    "label": record["name"],
                    "properties": {
                        "description": record["description"]
                    },
                    "type": "SleepDisorder",
                    "level": 0
                })

            relationships_symptom = session.run("""
                MATCH (d:SleepDisorder)-[r:HAS_SYMPTOM]->(s:Symptom)
                RETURN id(d) as source_id, id(s) as target_id, s.name as symptom_name, s.description as symptom_desc
                ORDER BY s.name
            """)
            for record in relationships_symptom:
                source_id = str(record["source_id"])
                target_id = str(record["target_id"])

                if target_id not in node_ids:
                    node_ids.add(target_id)
                    nodes.append({
                        "id": target_id,
                        "label": record["symptom_name"],
                        "properties": {
                            "description": record["symptom_desc"]
                        },
                        "type": "Symptom",
                        "level": 1
                    })
                
                relationships.append({
                    "startNode": source_id,
                    "endNode": target_id,
                    "type": "HAS_SYMPTOM"
                })

            relationships_treatment = session.run("""
                MATCH (d:SleepDisorder)-[r:HAS_TREATMENT]->(t:Treatment)
                RETURN id(d) as source_id, id(t) as target_id, t.name as treatment_name, t.description as treatment_desc
                ORDER BY t.name
            """)
            for record in relationships_treatment:
                source_id = str(record["source_id"])
                target_id = str(record["target_id"])

                if target_id not in node_ids:
                    node_ids.add(target_id)
                    nodes.append({
                        "id": target_id,
                        "label": record["treatment_name"],
                        "properties": {
                            "description": record["treatment_desc"]
                        },
                        "type": "Treatment",
                        "level": 1
                    })
                
                relationships.append({
                    "startNode": source_id,
                    "endNode": target_id,
                    "type": "HAS_TREATMENT"
                })

            relationships_risk = session.run("""
                MATCH (d:SleepDisorder)-[r:HAS_RISK_FACTOR]->(rf:RiskFactor)
                RETURN id(d) as source_id, id(rf) as target_id, rf.name as risk_name, rf.description as risk_desc
                ORDER BY rf.name
            """)
            for record in relationships_risk:
                source_id = str(record["source_id"])
                target_id = str(record["target_id"])

                if target_id not in node_ids:
                    node_ids.add(target_id)
                    nodes.append({
                        "id": target_id,
                        "label": record["risk_name"],
                        "properties": {
                            "description": record["risk_desc"]
                        },
                        "type": "RiskFactor",
                        "level": 1
                    })
                
                relationships.append({
                    "startNode": source_id,
                    "endNode": target_id,
                    "type": "HAS_RISK_FACTOR"
                })

            if not nodes:
                return jsonify({
                    "nodes": [],
                    "relationships": []
                })

            print("知识图谱数据获取成功！")
            return jsonify({
                "nodes": nodes,
                "relationships": relationships
            })

    except Exception as e:
        print(f"获取知识图谱数据失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_thread = threading.Thread(target=initialize_system)
    init_thread.start()
    app.run(debug=True) 