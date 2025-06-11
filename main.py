from neo4j import GraphDatabase
from openai import OpenAI
import json

class MedicalQA:
    def __init__(self):
        self.neo4j_uri = "bolt://localhost:7687"
        self.neo4j_user = "NTSoftware-Devour-My-Youth"
        self.neo4j_password = "NTSoftware-Devour-My-Youth"
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        # 初始化DeepSeek API
        self.client = OpenAI(
            base_url='https://api.siliconflow.cn/v1/',
            api_key='NTSoftware-Devour-My-Youth'
        )

    def query_knowledge_graph(self, question):
        """从知识图谱中查询相关信息"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (d:Disease)
                WHERE d.name CONTAINS $keyword OR d.description CONTAINS $keyword
                RETURN d
                LIMIT 5
                """

                result = session.run(query, keyword=question)
                records = [record["d"] for record in result]

                kg_info = []
                for record in records:
                    info = {
                        "name": record.get("name", ""),
                        "description": record.get("description", ""),
                        "symptoms": record.get("symptoms", [])
                    }
                    kg_info.append(info)
                
                return kg_info
        except Exception as e:
            print(f"知识图谱查询错误：{str(e)}")
            return []

    def get_ai_response(self, question, kg_info):
        """获取AI回答"""
        try:
            system_prompt = """你是一个专业的医疗助手，请基于提供的知识图谱信息回答问题。
            如果知识图谱中没有相关信息，请基于你的医学知识回答。
            请确保回答专业、准确、易懂。"""

            user_prompt = f"""问题：{question}
            
            知识图谱信息：
            {json.dumps(kg_info, ensure_ascii=False, indent=2)}
            
            请给出专业、准确的回答。"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=messages,
                stream=True,
                max_tokens=4096
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end='', flush=True)
            
            return full_response
            
        except Exception as e:
            print(f"AI响应错误：{str(e)}")
            return None

    def answer_question(self, question):
        """回答问题的主函数"""
        print(f"\n问题：{question}")

        # 1. 查询知识图谱
        print("\n正在查询知识图谱...")
        kg_info = self.query_knowledge_graph(question)
        
        # 2. 获取AI回答
        print("\n正在生成回答...")
        answer = self.get_ai_response(question, kg_info)
        
        return answer

    def close(self):
        """关闭数据库连接"""
        self.driver.close()

def main():
    qa_system = MedicalQA()
    
    try:
        while True:
            question = input("\n请输入您的问题（输入'退出'结束）：")
            
            if question.lower() in ['退出', 'exit', 'quit']:
                break

            qa_system.answer_question(question)

    except KeyboardInterrupt:
        print("\n程序已终止")
    finally:
        qa_system.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main() 