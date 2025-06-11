import json
from neo4j import GraphDatabase
import os
from tqdm import tqdm
import datasets
from datasets import load_dataset


class MedicalDataImporter:
    def __init__(self):
        # Neo4j连接配置
        self.uri = "bolt://localhost:7687"
        self.username = "NTSoftware-Devour-My-Youth"
        self.password = "NTSoftware-Devour-My-Youth"
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))

        # 创建数据目录
        if not os.path.exists('data'):
            os.makedirs('data')

    def print_dataset_info(self, dataset, name):
        """打印数据集信息"""
        print(f"\n{name} 数据集结构:")
        print("示例数据:")
        print(dataset['train'][0])
        print("\n数据集特征:")
        print(dataset['train'].features)

    def import_knowledge_graph_data(self):
        """导入知识图谱数据"""
        print("正在导入知识图谱数据...")
        # 加载知识图谱数据集
        kg_dataset = load_dataset('FreedomIntelligence/huatuo_knowledge_graph_qa')
        self.print_dataset_info(kg_dataset, "知识图谱")

        with self.driver.session() as session:
            for item in tqdm(kg_dataset['train']):
                try:
                    session.run("""
                        MERGE (q:Question {
                            text: $question
                        })
                        MERGE (a:Answer {
                            text: $answer
                        })
                        MERGE (q)-[:HAS_ANSWER]->(a)
                    """, {
                        'question': item['questions'][0],
                        'answer': item['answers'][0]
                    })
                except Exception as e:
                    print(f"处理数据项时出错: {str(e)}")
                    print(f"问题数据: {item}")
                    continue

    def import_encyclopedia_data(self):
        """导入医学百科数据"""
        print("正在导入医学百科数据...")
        # 加载医学百科数据集
        encyclopedia_dataset = load_dataset('FreedomIntelligence/huatuo_encyclopedia_qa')
        self.print_dataset_info(encyclopedia_dataset, "医学百科")

        with self.driver.session() as session:
            for item in tqdm(encyclopedia_dataset['train']):
                try:
                    # 创建问答对
                    session.run("""
                        MERGE (q:Question {
                            text: $question
                        })
                        MERGE (a:Answer {
                            text: $answer
                        })
                        MERGE (q)-[:HAS_ANSWER]->(a)
                    """, {
                        'question': item['questions'][0],
                        'answer': item['answers'][0]
                    })
                except Exception as e:
                    print(f"处理数据项时出错: {str(e)}")
                    print(f"问题数据: {item}")
                    continue

    def import_consultation_data(self):
        """导入医疗咨询数据"""
        print("正在导入医疗咨询数据...")
        # 加载医疗咨询数据集
        consultation_dataset = load_dataset('FreedomIntelligence/huatuo_consultation_qa')
        self.print_dataset_info(consultation_dataset, "医疗咨询")

        with self.driver.session() as session:
            for item in tqdm(consultation_dataset['train']):
                try:
                    # 创建问答对
                    session.run("""
                        MERGE (q:Question {
                            text: $question
                        })
                        MERGE (a:Answer {
                            text: $answer
                        })
                        MERGE (q)-[:HAS_ANSWER]->(a)
                    """, {
                        'question': item['questions'][0],
                        'answer': item['answers'][0]
                    })
                except Exception as e:
                    print(f"处理数据项时出错: {str(e)}")
                    print(f"问题数据: {item}")
                    continue

    def import_test_data(self):
        """导入测试数据集"""
        print("正在导入测试数据...")
        # 加载测试数据集
        test_dataset = load_dataset('FreedomIntelligence/huatuo26M-testdatasets')
        self.print_dataset_info(test_dataset, "测试")

        with self.driver.session() as session:
            for item in tqdm(test_dataset['train']):
                try:
                    # 创建测试问答对
                    session.run("""
                        MERGE (q:Question {
                            text: $question,
                            source: 'test'
                        })
                        MERGE (a:Answer {
                            text: $answer,
                            source: 'test'
                        })
                        MERGE (q)-[:HAS_ANSWER]->(a)
                    """, {
                        'question': item['questions'][0],
                        'answer': item['answers'][0]
                    })
                except Exception as e:
                    print(f"处理数据项时出错: {str(e)}")
                    print(f"问题数据: {item}")
                    continue

    def run(self):
        """运行导入流程"""
        try:
            # 清除现有数据
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")

            # 导入数据
            self.import_knowledge_graph_data()
            self.import_encyclopedia_data()
            self.import_consultation_data()
            self.import_test_data()

            print("数据导入完成！")

        except Exception as e:
            print(f"导入过程中出现错误：{str(e)}")
        finally:
            self.driver.close()


if __name__ == "__main__":
    importer = MedicalDataImporter()
    importer.run()