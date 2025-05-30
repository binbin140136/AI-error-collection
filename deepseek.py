import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import re
from datetime import datetime

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

# - 更新模型 ：使用新的模型，以获得更好的分析结果
# - 更详细的系统提示 ：提供了明确的角色定位和详细的格式要求
# - 添加了示例 ：通过具体的输入输出示例，帮助模型理解预期的格式
# - 使用 response_format 参数 ：明确告诉 API 我们需要 JSON 格式的响应
# - 降低温度值 ：从 0.3 降低到 0.1，使输出更加确定性
# - 优化解析逻辑 ：先尝试直接解析，失败后再使用正则表达式提取
def analyze_question(text):
    """调用DeepSeek分析错题"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个专业的教育分析助手。请分析学生的错题，并严格按照以下JSON格式返回分析结果，不要添加任何其他文字说明：
                    {
                        "subject": "学科名称（如数学/物理/化学/生物/语文/英语等）",
                        "knowledge_points": ["知识点1", "知识点2"],
                        "error_type": "错误类型（如概念理解错误/计算错误/公式应用错误等）",
                        "correct_approach": "正确的解题思路和方法，详细说明解题步骤",
                        "common_mistakes": "学生在此类题目中常见的错误和误区",
                        "answer": "大模型生成的参考答案"
                    }
                    
                    示例输入：
                    已知函数f(x)=ln(x+1)，求f'(2)的值。
                    学生解答：f'(x)=1/(x+1)，所以f'(2)=1/3
                    
                    示例输出：
                    {
                        "subject": "数学",
                        "knowledge_points": ["导数", "对数函数求导"],
                        "error_type": "计算错误",
                        "correct_approach": "1. 对f(x)=ln(x+1)求导，得f'(x)=1/(x+1)\\n2. 将x=2代入f'(x)=1/(x+1)\\n3. 计算f'(2)=1/(2+1)=1/3\\n学生的导数公式是正确的，但计算结果有误，正确答案是1/3",
                        "common_mistakes": "此类题目常见错误包括：对数函数求导公式记忆错误、代入数值计算错误、忽略链式法则等",
                        "answer": "1/3"
                    }
                    
                    请只返回JSON格式数据，不要有任何前缀或后缀说明。"""
                },
                {
                    "role": "user",
                    "content": f"分析以下题目：\n{text}"
                }
            ],
            temperature=0.1,  # 降低温度以获得更确定性的输出
            max_tokens=800,   # 增加token上限以容纳更详细的解题思路
            response_format={"type": "json_object"}  # 明确要求JSON格式响应
        )
        
        raw_response = response.choices[0].message.content
        print("[DeepSeek原始响应]\n", raw_response)
        
        # 尝试直接解析JSON
        try:
            result = json.loads(raw_response)
            # 检查必要字段
            required_fields = ["subject", "knowledge_points", "error_type"]
            if not all(key in result for key in required_fields):
                print(f"JSON结构不完整: {result}")
                raise ValueError("JSON结构不完整")
            
            # 为可选字段设置默认值
            if "correct_approach" not in result:
                result["correct_approach"] = "未提供解题思路"
            if "common_mistakes" not in result:
                result["common_mistakes"] = "未提供常见错误分析"
            if "answer" not in result:
                result["answer"] = "未提供参考答案"
                   
            return result
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试使用正则表达式提取JSON部分
            json_match = re.search(r'(?s)\{.*\}', raw_response, re.DOTALL)
            if not json_match:
                print("未找到JSON数据")
                return {"subject": "未知", "knowledge_points": ["格式错误"], "error_type": "响应格式异常"}
                
            extracted_json = json_match.group()
            try:
                result = json.loads(extracted_json)
                if not all(key in result for key in ("subject", "knowledge_points", "error_type")):
                    print(f"JSON结构不完整: {result}")
                    raise ValueError("JSON结构不完整")
                return result
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON解析失败: {str(e)}\n原始内容: {extracted_json}")
                # 记录原始响应到文件
                with open("deepseek_errors.log", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now().isoformat()}\n{raw_response}\n\n")
                return {
                    "subject": "未知",
                    "knowledge_points": ["解析失败：" + str(e)],
                    "error_type": "API响应异常"
                }
        except ValueError as e:
            print(f"JSON结构验证失败: {str(e)}")
            with open("deepseek_errors.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()}\n{raw_response}\n\n")
            return {
                "subject": "未知",
                "knowledge_points": ["结构错误：" + str(e)],
                "error_type": "数据结构异常"
            }
    except Exception as e:
        print(f"DeepSeek分析失败: {str(e)}")
        return {
            "subject": "未知",
            "knowledge_points": ["服务异常"],
            "error_type": "系统错误"
        }
    