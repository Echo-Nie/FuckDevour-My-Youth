from neo4j import GraphDatabase
from openai import OpenAI
import json
from typing import Dict, List, Optional
import time

class SleepQA:
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

        self.user_state = {
            "symptoms": [],
            "risk_factors": [],
            "sleep_habits": {},
            "medical_history": [],
            "current_assessment": None
        }

        self.conversation_history = []

    def query_knowledge_graph(self, query_type: str, keywords: List[str]) -> List[Dict]:
        """从知识图谱中查询相关信息"""

        try:
            with self.driver.session() as session:
                if query_type == "sleep_disorder":
                    # 查询睡眠障碍信息
                    cypher_query = """
                    MATCH (d:SleepDisorder)
                    WHERE any(keyword in $keywords WHERE d.name CONTAINS keyword OR d.description CONTAINS keyword)
                    OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
                    OPTIONAL MATCH (d)-[:HAS_RISK_FACTOR]->(r:RiskFactor)
                    OPTIONAL MATCH (d)-[:HAS_TREATMENT]->(t:Treatment)
                    RETURN d, collect(distinct s) as symptoms, 
                           collect(distinct r) as risk_factors,
                           collect(distinct t) as treatments
                    """
                elif query_type == "treatment":
                    # 查询治疗方法信息
                    cypher_query = """
                    MATCH (t:Treatment)
                    WHERE any(keyword in $keywords WHERE t.name CONTAINS keyword OR t.description CONTAINS keyword)
                    OPTIONAL MATCH (t)-[:INCLUDES_ADVICE]->(a:Advice)
                    RETURN t, collect(distinct a) as advice
                    """
                else:
                    return []

                result = session.run(cypher_query, keywords=keywords)
                return [record for record in result]

        except Exception as e:
            print(f"知识图谱查询错误：{str(e)}")
            return []

    def update_user_state(self, user_input: str, intent: str):
        """更新用户状态"""
        if intent == "symptom_report":
            # 提取症状信息
            self.user_state["symptoms"].extend(self.extract_symptoms(user_input))
        elif intent == "risk_factor_report":
            # 提取风险因素
            self.user_state["risk_factors"].extend(self.extract_risk_factors(user_input))
        elif intent == "sleep_habit_report":
            # 更新睡眠习惯
            self.user_state["sleep_habits"].update(self.extract_sleep_habits(user_input))
        elif intent == "medical_history_report":
            # 更新病史
            self.user_state["medical_history"].extend(self.extract_medical_history(user_input))

    def extract_symptoms(self, text: str) -> List[str]:
        """从文本中提取症状信息"""
        # 这里可以添加更复杂的NLP处理
        return [text]

    def extract_risk_factors(self, text: str) -> List[str]:
        """从文本中提取风险因素"""
        return [text]

    def extract_sleep_habits(self, text: str) -> Dict:
        """从文本中提取睡眠习惯"""
        return {"text": text}

    def extract_medical_history(self, text: str) -> List[str]:
        """从文本中提取病史"""
        return [text]

    def generate_assessment(self) -> Dict:
        """生成个性化评估"""
        try:
            # 构建评估提示词
            assessment_prompt = f"""基于以下用户信息进行睡眠健康评估：

            症状：{json.dumps(self.user_state['symptoms'], ensure_ascii=False)}
            风险因素：{json.dumps(self.user_state['risk_factors'], ensure_ascii=False)}
            睡眠习惯：{json.dumps(self.user_state['sleep_habits'], ensure_ascii=False)}
            病史：{json.dumps(self.user_state['medical_history'], ensure_ascii=False)}

            请提供：
            1. 可能的睡眠问题诊断
            2. 风险等级评估
            3. 改善建议
            4. 是否需要就医建议
            """

            # 调用API生成评估
            messages = [
                {"role": "system", "content": "你是一个专业的睡眠健康评估专家。"},
                {"role": "user", "content": assessment_prompt}
            ]

            response = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=messages,
                stream=False,
                max_tokens=2000
            )

            return {
                "timestamp": time.time(),
                "assessment": response.choices[0].message.content
            }

        except Exception as e:
            print(f"生成评估错误：{str(e)}")
            return None

    def get_ai_response(self, question: str, kg_info: List[Dict], context: Optional[Dict] = None) -> str:
        """获取AI回答"""
        try:
            # 构建系统提示词
            system_prompt = """你是一个专业的睡眠健康顾问，请基于提供的知识图谱信息回答问题。
            如果知识图谱中没有相关信息，请基于你的专业知识回答。
            请确保回答专业、准确、易懂。"""

            # 构建用户提示词
            user_prompt = f"""问题：{question}
            
            知识图谱信息：
            {json.dumps(kg_info, ensure_ascii=False, indent=2)}
            
            {f'用户背景信息：{json.dumps(context, ensure_ascii=False)}' if context else ''}
            
            请给出专业、准确的回答。"""

            # 调用API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=messages,
                stream=True,
                max_tokens=2000
            )

            # 处理流式响应
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

    def process_user_input(self, user_input: str) -> str:
        """处理用户输入"""
        # 1. 更新用户状态
        self.update_user_state(user_input, "symptom_report")  # 这里可以添加更复杂的意图识别

        # 2. 查询知识图谱
        kg_info = self.query_knowledge_graph("sleep_disorder", [user_input])

        # 3. 获取AI回答
        response = self.get_ai_response(user_input, kg_info, self.user_state)

        # 4. 更新对话历史
        self.conversation_history.append({
            "user": user_input,
            "assistant": response,
            "timestamp": time.time()
        })

        # 5. 定期生成评估
        if len(self.conversation_history) % 3 == 0:  # 每3轮对话生成一次评估
            assessment = self.generate_assessment()
            if assessment:
                self.user_state["current_assessment"] = assessment
                response += f"\n\n=== 最新评估 ===\n{assessment['assessment']}"

        return response

    def close(self):
        """关闭数据库连接"""
        self.driver.close()

def main():
    # 创建问答系统实例
    qa_system = SleepQA()
    
    print("欢迎使用睡眠健康问答系统！")
    print("您可以询问关于睡眠障碍、症状、治疗方法等问题。")
    print("系统会记录您的症状和习惯，定期提供个性化评估。")
    print("输入'退出'结束对话。\n")
    
    try:
        while True:
            # 获取用户输入
            question = input("\n请输入您的问题：")
            
            if question.lower() in ['退出', 'exit', 'quit']:
                break
                
            # 处理用户输入
            response = qa_system.process_user_input(question)
            
    except KeyboardInterrupt:
        print("\n程序已终止")
    finally:
        # 关闭连接
        qa_system.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main() 