import sqlite3
import pandas as pd

def get_error_details(error_id):
    """根据ID获取错题详情"""
    try:
        conn = sqlite3.connect('data/errors.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                id,
                text,
                subject,
                knowledge_points,
                error_type,
                timestamp,
                original_filename,
                common_mistakes,
                correct_approach,
                answer
            FROM errors WHERE id = ?
        ''', (error_id,))
        
        result = cursor.fetchone()
        if not result:
            return None
            
        # 将结果转换为字典
        columns = [column[0] for column in cursor.description]
        error_dict = dict(zip(columns, result))
        
        # 将知识点的字符串转换为列表
        error_dict['knowledge_points'] = error_dict['knowledge_points'].split(',')
        
        return error_dict
    except Exception as e:
        print(f"数据库查询失败: {str(e)}")
        return None
    finally:
        conn.close()

# 修复表结构中的逗号缺失问题（在现有代码中修改）
def init_db():
    """初始化数据库"""
    import os
    db_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(os.path.join(db_dir, 'errors.db'))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            subject TEXT,
            knowledge_points TEXT,
            error_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            original_filename TEXT,  -- 添加逗号
            common_mistakes TEXT,    -- 添加逗号
            correct_approach TEXT,
            answer TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_error(text, subject, knowledge_points, error_type, original_filename,common_mistakes,correct_approach,answer):
    """保存错题记录"""
    try:
        conn = sqlite3.connect('data/errors.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO errors (text, subject, knowledge_points, error_type, original_filename,common_mistakes,correct_approach,answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (text, subject, ','.join(knowledge_points), error_type, original_filename,common_mistakes,correct_approach,answer))
        conn.commit()
    except Exception as e:
        print(f"数据库保存失败: {str(e)}")
    finally:
        conn.close()

def get_errors():
    """获取所有错题"""
    conn = sqlite3.connect('data/errors.db')
    df = pd.read_sql('SELECT * FROM errors ORDER BY timestamp DESC', conn)
    conn.close()
    return df.to_dict('records')


def delete_error(error_id):
    """删除指定错题"""
    try:
        conn = sqlite3.connect('data/errors.db')
        cursor = conn.cursor()
        
        # 先查询原始文件名，用于删除图片文件
        cursor.execute('SELECT original_filename FROM errors WHERE id = ?', (error_id,))
        result = cursor.fetchone()
        print(result)
        if result:
            # 删除记录
            cursor.execute('DELETE FROM errors WHERE id = ?', (error_id,))
            conn.commit()
            
            # 删除对应的图片文件
            if result[0]:  # 如果有图片文件
                try:
                    import os
                    image_path = os.path.join('static', 'images', result[0])
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print(f"删除图片文件失败: {str(e)}")
                    # 即使图片删除失败，数据库记录已删除，仍返回成功
            
            return {
                'status': 'success',
                'message': '删除成功'
            }
        else:
            return {
                'status': 'error',
                'message': '未找到指定错题'
            }
            
    except Exception as e:
        print(f"删除错题失败: {str(e)}")
        return {
            'status': 'error',
            'message': f'删除失败: {str(e)}'
        }
    finally:
        conn.close()