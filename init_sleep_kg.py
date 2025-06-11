from neo4j import GraphDatabase
import time

def init_sleep_kg():
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "neo4j123.."
    
    print("正在连接Neo4j数据库...")
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            print("清除现有数据...")
            session.run("MATCH (n) DETACH DELETE n")

            print("创建睡眠障碍数据...")
            session.run("""
                CREATE (d1:SleepDisorder {
                    name: '失眠症',
                    description: '难以入睡或维持睡眠的睡眠障碍',
                    diagnostic_criteria: '每周至少3次，持续3个月以上',
                    severity: '中度',
                    duration: '慢性'
                })
                CREATE (d2:SleepDisorder {
                    name: '睡眠呼吸暂停',
                    description: '睡眠时呼吸反复暂停的疾病',
                    diagnostic_criteria: '每小时发生5次以上呼吸暂停',
                    severity: '重度',
                    duration: '慢性'
                })
                CREATE (d3:SleepDisorder {
                    name: '不宁腿综合征',
                    description: '腿部不适感导致难以入睡的疾病',
                    diagnostic_criteria: '腿部不适感在休息时加重，活动后缓解',
                    severity: '中度',
                    duration: '慢性'
                })
            """)

            print("创建症状关系...")
            session.run("""
                MATCH (d:SleepDisorder)
                WITH d
                CREATE (s1:Symptom {name: '入睡困难', description: '需要30分钟以上才能入睡'})
                CREATE (s2:Symptom {name: '早醒', description: '比预期时间早醒且无法再次入睡'})
                CREATE (s3:Symptom {name: '日间疲劳', description: '白天感到疲倦和困倦'})
                CREATE (s4:Symptom {name: '打鼾', description: '睡眠时发出响亮的呼吸声'})
                CREATE (s5:Symptom {name: '腿部不适', description: '腿部有爬行感或刺痛感'})
                WITH d, s1, s2, s3, s4, s5
                MATCH (d:SleepDisorder {name: '失眠症'})
                CREATE (d)-[:HAS_SYMPTOM]->(s1)
                CREATE (d)-[:HAS_SYMPTOM]->(s2)
                CREATE (d)-[:HAS_SYMPTOM]->(s3)
                WITH d, s4, s5
                MATCH (d:SleepDisorder {name: '睡眠呼吸暂停'})
                CREATE (d)-[:HAS_SYMPTOM]->(s4)
                CREATE (d)-[:HAS_SYMPTOM]->(s3)
                WITH d, s5
                MATCH (d:SleepDisorder {name: '不宁腿综合征'})
                CREATE (d)-[:HAS_SYMPTOM]->(s5)
                CREATE (d)-[:HAS_SYMPTOM]->(s1)
            """)

            print("创建风险因素...")
            session.run("""
                MATCH (d:SleepDisorder)
                WITH d
                CREATE (r1:RiskFactor {name: '年龄', description: '年龄增长会增加睡眠问题风险'})
                CREATE (r2:RiskFactor {name: '压力', description: '心理压力会影响睡眠质量'})
                CREATE (r3:RiskFactor {name: '不良生活习惯', description: '不规律的作息时间会影响睡眠'})
                WITH d, r1, r2, r3
                MATCH (d:SleepDisorder)
                CREATE (d)-[:HAS_RISK_FACTOR]->(r1)
                CREATE (d)-[:HAS_RISK_FACTOR]->(r2)
                CREATE (d)-[:HAS_RISK_FACTOR]->(r3)
            """)

            print("创建治疗方法...")
            session.run("""
                MATCH (d:SleepDisorder)
                WITH d
                CREATE (t1:Treatment {
                    name: '认知行为疗法',
                    description: '通过改变不良认知和行为改善睡眠',
                    effectiveness: '高',
                    duration: '8-12周'
                })
                CREATE (t2:Treatment {
                    name: '睡眠卫生教育',
                    description: '培养良好的睡眠习惯',
                    effectiveness: '中',
                    duration: '长期'
                })
                CREATE (t3:Treatment {
                    name: '持续气道正压通气',
                    description: '使用呼吸机维持气道通畅',
                    effectiveness: '高',
                    duration: '长期'
                })
                WITH d, t1, t2, t3
                MATCH (d:SleepDisorder)
                CREATE (d)-[:HAS_TREATMENT]->(t1)
                CREATE (d)-[:HAS_TREATMENT]->(t2)
                WITH d, t3
                MATCH (d:SleepDisorder {name: '睡眠呼吸暂停'})
                CREATE (d)-[:HAS_TREATMENT]->(t3)
            """)

            print("创建改善建议...")
            session.run("""
                MATCH (t:Treatment)
                WITH t
                CREATE (a1:Advice {
                    name: '规律作息',
                    description: '保持固定的睡眠和起床时间',
                    difficulty: '低',
                    importance: '高'
                })
                CREATE (a2:Advice {
                    name: '睡前放松',
                    description: '睡前进行放松活动，如冥想或阅读',
                    difficulty: '低',
                    importance: '中'
                })
                CREATE (a3:Advice {
                    name: '避免咖啡因',
                    description: '睡前6小时避免摄入咖啡因',
                    difficulty: '中',
                    importance: '高'
                })
                WITH t, a1, a2, a3
                MATCH (t:Treatment)
                CREATE (t)-[:INCLUDES_ADVICE]->(a1)
                CREATE (t)-[:INCLUDES_ADVICE]->(a2)
                CREATE (t)-[:INCLUDES_ADVICE]->(a3)
            """)
            
            print("初始化完成！")
            
    except Exception as e:
        print(f"初始化失败：{str(e)}")
    finally:
        driver.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    init_sleep_kg() 