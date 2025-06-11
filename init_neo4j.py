from neo4j import GraphDatabase

def init_neo4j():
    # Neo4j连接配置
    uri = "bolt://localhost:7687"
    user = "NTSoftware-Devour-My-Youth"
    password = "NTSoftware-Devour-My-Youth"
    
    print("正在连接Neo4j数据库...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            print("\n清除现有数据...")
            session.run("MATCH (n) DETACH DELETE n")

            print("创建疾病数据...")
            session.run("""
            CREATE (d1:Disease {
                name: '高血压',
                description: '血压持续高于正常值的疾病，通常指收缩压≥140mmHg和/或舒张压≥90mmHg',
                symptoms: ['头痛', '眩晕', '心悸', '耳鸣', '视力模糊'],
                risk_factors: ['年龄增长', '家族史', '肥胖', '高盐饮食', '缺乏运动'],
                treatments: ['生活方式改变', '降压药物', '定期监测']
            })
            
            CREATE (d2:Disease {
                name: '糖尿病',
                description: '由于胰岛素分泌不足或作用障碍导致的血糖升高疾病',
                symptoms: ['多饮', '多尿', '多食', '体重下降', '疲劳'],
                risk_factors: ['家族史', '肥胖', '缺乏运动', '年龄增长'],
                treatments: ['饮食控制', '运动治疗', '胰岛素治疗', '口服降糖药']
            })
            
            CREATE (d3:Disease {
                name: '冠心病',
                description: '冠状动脉粥样硬化导致的心肌缺血性疾病',
                symptoms: ['胸痛', '胸闷', '气短', '心悸', '疲劳'],
                risk_factors: ['高血压', '高血脂', '吸烟', '糖尿病', '肥胖'],
                treatments: ['药物治疗', '介入治疗', '搭桥手术', '生活方式改变']
            })
            """)

            print("创建症状关系...")
            session.run("""
            MATCH (d:Disease)
            UNWIND d.symptoms as symptom
            MERGE (s:Symptom {name: symptom})
            MERGE (d)-[:HAS_SYMPTOM]->(s)
            """)

            print("创建风险因素关系...")
            session.run("""
            MATCH (d:Disease)
            UNWIND d.risk_factors as risk
            MERGE (r:RiskFactor {name: risk})
            MERGE (d)-[:HAS_RISK_FACTOR]->(r)
            """)

            print("创建治疗方法关系...")
            session.run("""
            MATCH (d:Disease)
            UNWIND d.treatments as treatment
            MERGE (t:Treatment {name: treatment})
            MERGE (d)-[:HAS_TREATMENT]->(t)
            """)
            
            print("\n数据初始化完成！")
            
    except Exception as e:
        print("初始化失败：", str(e))
    finally:
        driver.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    init_neo4j() 