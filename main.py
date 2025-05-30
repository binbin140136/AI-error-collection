from deepseek import analyze_question
from flask import Flask,request,jsonify,render_template, send_file,send_from_directory
from ocr import recognize_text
from aliy_ocr import AliOcr
from datebase import init_db, save_error, get_errors,get_error_details,delete_error
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app=Flask(__name__)
app.config['UPLOAD_FOLDER']='static/images'
#初始化数据库
init_db()

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/upload", methods=['POST'])
def upload():
    # 检查图片
    if "image" not in request.files:
        return jsonify({
            "status":"error",
            "message": "请选择要上传的图片文件",
            "code": 400
        }), 400

    # 获取图片
    file = request.files["image"]
    subject = request.form.get("subject", "unknown")
    tags = request.form.get("tags", "").split(",")

    # 检查文件名
    if file.filename == "":
        return jsonify({
            "status":"error",
            "message": "文件名不能为空",
            "code": 400
        }), 400

    # 定义text变量
    text = ""
    analysis = {"subject": "", "knowledge_points": [], "error_type": ""}

    try:
        # 生成文件名
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        save_path = os.path.join('static', 'images', filename)
        file.save(save_path)
        print(save_path)
        # OCR
        text = AliOcr.main([save_path])
         
        # 检查OCR结果
        if not text.strip():
            return jsonify({
                "status": "error",
                "message": "OCR未识别到有效文字",
                "code": 400
            }), 400
        
        # DeepSeek
        analysis = analyze_question(text)
        print(analysis.get('common_mistakes'),'分析结果')
        # 保存错题到数据库 (无论是否有异常都应该保存)
        save_error(
            text=text,
            subject=analysis.get("subject", subject),  # 使用分析结果的学科，如果没有则使用表单提供的
            knowledge_points=analysis.get("knowledge_points", []),
            error_type=analysis.get("error_type", "未知"),
            original_filename=filename,
            common_mistakes = analysis.get("common_mistakes", "无"),
            correct_approach = analysis.get("correct_approach", "无"),
            answer=analysis.get("answer", "无")
        )
        # 返回成功信息
        return jsonify({"status": "success", "text": text, "analyze": analysis, "filename": filename}), 200

    except Exception as e:
        # 保存错误
        # save_error(
        #     text=text,
        #     subject=analysis.get("subject","unknown"),
        #     knowledge_points=analysis.get("knowledge_points",[]),
        #     error_type=analysis.get("error_type","unknown"),
        #     filename=filename
        # )
        return jsonify({
            "status":"error",
            "message":str(e)
        }),500

             


@app.route("/errors")
def errors():
    try:
        errors=get_errors()
        return jsonify({"status":"success","errors":errors})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500
    
@app.route('/error_page/<int:error_id>')
def error_detail_page(error_id):
    """错题详情展示页"""
    error_data = get_error_details(error_id)
    if error_data:
        return render_template('error_detail.html', error=error_data)
    return render_template('404.html'), 404
 
@app.route('/api/error/<int:error_id>', methods=['DELETE'])
def delete_error_endpoint(error_id):
    """删除指定错题的API端点"""
    try:
        result = delete_error(error_id)
        print(result,'删除指定错题的API端点')
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'message': '错题删除成功'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'删除失败: {str(e)}'
        }), 500
@app.route("/statistics")
def statistics():
    try:
        stats=get_statistics() 
        return jsonify({"status":"success","stats":stats})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500

@app.route('/practice')
def practice():
    try:
        pdf_path=generate_pdf() 
        return send_file(pdf_path,as_attachment=True)
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500

if __name__ == "__main__":
    app.run(
     debug=True,
     host="0.0.0.0",
     port=5000
    )
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"status": "error", "message": "接口不存在"}), 404, {'Content-Type': 'application/json'}

@app.route("/data")
def get_data():
    return jsonify({"key": "value"}), 200, {'Content-Type': 'application/json'}

