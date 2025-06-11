import json
from neo4j import GraphDatabase
import os
from tqdm import tqdm

class MedicalDataImporter:
    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.username = "NTSoftware-Devour-My-Youth"
        self.password = "NTSoftware-Devour-My-Youth"
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        
        # 创建数据目录
        if not os.path.exists('data'):
            os.makedirs('data')

    def import_sleep_data(self):
        """导入睡眠相关的数据"""
        print("正在导入睡眠数据...")
        sleep_data = {
            'sleep_disorders': [
                {
                    'name': '失眠症',
                    'description': '难以入睡或维持睡眠的睡眠障碍',
                    'symptoms': [
                        {'name': '入睡困难', 'description': '需要30分钟以上才能入睡'},
                        {'name': '早醒', 'description': '比预期时间早醒且无法再次入睡'},
                        {'name': '日间疲劳', 'description': '白天感到疲倦和困倦'},
                        {'name': '注意力不集中', 'description': '难以集中注意力'},
                        {'name': '情绪波动', 'description': '易怒、焦虑或抑郁'}
                    ],
                    'treatments': [
                        {'name': '认知行为疗法', 'description': '通过改变不良认知和行为改善睡眠', 'effectiveness': '高'},
                        {'name': '睡眠卫生教育', 'description': '培养良好的睡眠习惯', 'effectiveness': '中'},
                        {'name': '放松训练', 'description': '通过放松技巧改善睡眠', 'effectiveness': '中'},
                        {'name': '药物治疗', 'description': '在医生指导下使用助眠药物', 'effectiveness': '高'}
                    ],
                    'risk_factors': [
                        {'name': '压力', 'description': '心理压力会影响睡眠质量'},
                        {'name': '焦虑', 'description': '焦虑情绪会导致入睡困难'},
                        {'name': '抑郁', 'description': '抑郁症状会影响睡眠'},
                        {'name': '不良睡眠习惯', 'description': '不规律的作息时间会影响睡眠'},
                        {'name': '环境因素', 'description': '噪音、光线等环境因素会影响睡眠'}
                    ]
                },
                {
                    'name': '睡眠呼吸暂停',
                    'description': '睡眠时呼吸反复暂停的疾病',
                    'symptoms': [
                        {'name': '打鼾', 'description': '睡眠时发出响亮的呼吸声'},
                        {'name': '呼吸暂停', 'description': '睡眠时呼吸暂时停止'},
                        {'name': '日间嗜睡', 'description': '白天过度困倦'},
                        {'name': '晨起头痛', 'description': '早晨起床时头痛'},
                        {'name': '注意力不集中', 'description': '难以集中注意力'}
                    ],
                    'treatments': [
                        {'name': '持续气道正压通气', 'description': '使用呼吸机维持气道通畅', 'effectiveness': '高'},
                        {'name': '口腔矫治器', 'description': '使用口腔装置改善气道', 'effectiveness': '中'},
                        {'name': '手术', 'description': '通过手术改善气道', 'effectiveness': '高'},
                        {'name': '生活方式改变', 'description': '减肥、戒烟等', 'effectiveness': '中'}
                    ],
                    'risk_factors': [
                        {'name': '肥胖', 'description': '体重过重会增加患病风险'},
                        {'name': '年龄', 'description': '年龄增长会增加患病风险'},
                        {'name': '性别', 'description': '男性患病风险更高'},
                        {'name': '家族史', 'description': '家族中有患者会增加风险'},
                        {'name': '吸烟', 'description': '吸烟会增加患病风险'}
                    ]
                },
                {
                    'name': '不宁腿综合征',
                    'description': '腿部不适感导致难以入睡的疾病',
                    'symptoms': [
                        {'name': '腿部不适感', 'description': '腿部有爬行感或刺痛感'},
                        {'name': '活动冲动', 'description': '需要活动腿部才能缓解不适'},
                        {'name': '夜间加重', 'description': '症状在夜间加重'},
                        {'name': '影响睡眠', 'description': '症状影响入睡'},
                        {'name': '日间疲劳', 'description': '白天感到疲倦'}
                    ],
                    'treatments': [
                        {'name': '药物治疗', 'description': '使用多巴胺能药物等', 'effectiveness': '高'},
                        {'name': '生活方式改变', 'description': '规律运动、避免咖啡因等', 'effectiveness': '中'},
                        {'name': '运动疗法', 'description': '通过运动改善症状', 'effectiveness': '中'},
                        {'name': '按摩', 'description': '通过按摩缓解症状', 'effectiveness': '低'}
                    ],
                    'risk_factors': [
                        {'name': '缺铁', 'description': '铁缺乏会增加患病风险'},
                        {'name': '妊娠', 'description': '妊娠期间易发'},
                        {'name': '慢性疾病', 'description': '某些慢性疾病会增加风险'},
                        {'name': '家族史', 'description': '家族中有患者会增加风险'},
                        {'name': '年龄', 'description': '年龄增长会增加风险'}
                    ]
                }
            ]
        }
        
        with self.driver.session() as session:
            for disorder in tqdm(sleep_data['sleep_disorders']):
                # 创建睡眠障碍节点
                session.run("""
                    MERGE (d:SleepDisorder {
                        name: $name,
                        description: $description
                    })
                """, {
                    'name': disorder['name'],
                    'description': disorder['description']
                })
                
                # 创建症状关系
                for symptom in disorder['symptoms']:
                    session.run("""
                        MATCH (d:SleepDisorder {name: $disorder})
                        MERGE (s:Symptom {
                            name: $name,
                            description: $description
                        })
                        MERGE (d)-[:HAS_SYMPTOM]->(s)
                    """, {
                        'disorder': disorder['name'],
                        'name': symptom['name'],
                        'description': symptom['description']
                    })
                
                # 创建治疗方法关系
                for treatment in disorder['treatments']:
                    session.run("""
                        MATCH (d:SleepDisorder {name: $disorder})
                        MERGE (t:Treatment {
                            name: $name,
                            description: $description,
                            effectiveness: $effectiveness
                        })
                        MERGE (d)-[:HAS_TREATMENT]->(t)
                    """, {
                        'disorder': disorder['name'],
                        'name': treatment['name'],
                        'description': treatment['description'],
                        'effectiveness': treatment['effectiveness']
                    })
                
                # 创建风险因素关系
                for risk in disorder['risk_factors']:
                    session.run("""
                        MATCH (d:SleepDisorder {name: $disorder})
                        MERGE (r:RiskFactor {
                            name: $name,
                            description: $description
                        })
                        MERGE (d)-[:HAS_RISK_FACTOR]->(r)
                    """, {
                        'disorder': disorder['name'],
                        'name': risk['name'],
                        'description': risk['description']
                    })

    def import_qa_data(self):
        """导入问答数据"""
        print("正在导入问答数据...")
        qa_data = [
            {
                'question': '失眠症有哪些常见症状？',
                'answer': '失眠症的常见症状包括：入睡困难（需要30分钟以上才能入睡）、早醒（比预期时间早醒且无法再次入睡）、日间疲劳、注意力不集中和情绪波动。这些症状会影响日常生活和工作。'
            },
            {
                'question': '如何改善睡眠质量？',
                'answer': '改善睡眠质量的方法包括：1. 保持规律的作息时间；2. 创造良好的睡眠环境（安静、黑暗、凉爽）；3. 避免睡前使用电子设备；4. 避免睡前摄入咖啡因和酒精；5. 进行适当的运动，但避免睡前剧烈运动；6. 学习放松技巧，如冥想或深呼吸。'
            },
            {
                'question': '睡眠呼吸暂停需要治疗吗？',
                'answer': '是的，睡眠呼吸暂停需要及时治疗。如果不治疗，可能会导致严重的健康问题，如高血压、心脏病、中风等。治疗方法包括：持续气道正压通气（CPAP）、口腔矫治器、手术和生活方式改变（如减肥、戒烟）。建议在医生指导下选择合适的治疗方案。'
            },
            {
                'question': '不宁腿综合征是什么？',
                'answer': '不宁腿综合征是一种神经系统疾病，主要表现为腿部不适感（如爬行感或刺痛感）和强烈的活动冲动，这些症状在休息时加重，活动后缓解。症状通常在夜间加重，影响睡眠质量。治疗方法包括药物治疗、生活方式改变、运动疗法和按摩等。'
            }
        ]
        
        with self.driver.session() as session:
            for qa in tqdm(qa_data):
                session.run("""
                    MERGE (q:Question {
                        text: $question
                    })
                    MERGE (a:Answer {
                        text: $answer
                    })
                    MERGE (q)-[:HAS_ANSWER]->(a)
                """, qa)

    def run(self):
        """运行导入流程"""
        try:
            with self.driver.session() as session:
                print("正在清空数据库...")
                session.run("MATCH (n) DETACH DELETE n")
                print("数据库清空完成！")

            self.import_sleep_data()
            self.import_qa_data()

            print("数据导入完成！")
            
        except Exception as e:
            print(f"导入过程中出现错误：{str(e)}")
        finally:
            self.driver.close()

if __name__ == "__main__":
    print("开始强制重新导入数据...")
    importer = MedicalDataImporter()
    importer.run()
    print("数据重新导入完成！")