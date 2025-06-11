from neo4j import GraphDatabase

def test_neo4j_connection():
    # Neo4j连接配置
    uri = "bolt://localhost:7687"
    user = "NTSoftware-Devour-My-Youth"
    password = "NTSoftware-Devour-My-Youth"
    
    print("连接Neo4j...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN '连接成功！' as message")
            record = result.single()
            print(record["message"])
            print("\n正在创建测试节点...")
            session.run("""
            CREATE (d:Disease {
                name: '高血压',
                description: '血压持续高于正常值的疾病',
                symptoms: ['头痛', '眩晕', '心悸']
            })
            """)
            print("测试节点创建成功！")
            print("\n正在查询测试节点...")
            result = session.run("MATCH (d:Disease) RETURN d")
            for record in result:
                print("节点信息：", record["d"])
            
    except Exception as e:
        print("连接失败：", str(e))
    finally:
        driver.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    test_neo4j_connection()