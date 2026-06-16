"""
分析中间件服务
整合OCR识别和LLM分析
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import requests
import os
import logging
import json
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="分析服务", version="1.0.0")

# 配置
OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://localhost:8001")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:11434")

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USERNAME", "orangehrm"),
    "password": os.getenv("MYSQL_PASSWORD", "orangehrm123"),
    "database": os.getenv("MYSQL_DATABASE", "orangehrm")
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        logger.error(f"数据库连接错误: {str(e)}")
        raise HTTPException(status_code=500, detail="数据库连接失败")

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("[*] 分析服务已启动")
    logger.info(f"[*] OCR服务: {OCR_SERVICE_URL}")
    logger.info(f"[*] LLM服务: {LLM_SERVICE_URL}")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    # 检查OCR服务
    ocr_status = "down"
    try:
        response = requests.get(f"{OCR_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            ocr_status = "up"
    except:
        pass
    
    # 检查LLM服务
    llm_status = "down"
    try:
        response = requests.get(f"{LLM_SERVICE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            llm_status = "up"
    except:
        pass
    
    # 检查数据库
    db_status = "down"
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "up"
    except:
        pass
    
    return {
        "status": "healthy" if all(s == "up" for s in [ocr_status, llm_status, db_status]) else "degraded",
        "services": {
            "ocr": ocr_status,
            "llm": llm_status,
            "database": db_status
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analysis/process-archive")
async def process_archive(
    employee_id: int = None,
    archive_name: str = None,
    file: UploadFile = File(...)
):
    """
    处理档案：OCR识别 + LLM分析
    
    参数:
        employee_id: 员工ID (可选)
        archive_name: 档案名称
        file: 档案文件
    
    返回:
        {
            "status": "success",
            "ocr_text": "识别的文本",
            "analysis": "分析结果",
            "confidence": 0.95
        }
    """
    try:
        logger.info(f"[*] 开始处理档案: {archive_name}")
        
        # 1. 调用OCR识别
        logger.info("[*] 发送文件到OCR服务...")
        ocr_response = requests.post(
            f"{OCR_SERVICE_URL}/ocr/recognize",
            files={"file": (file.filename, await file.read(), "application/octet-stream")},
            timeout=120
        )
        
        if ocr_response.status_code != 200:
            raise HTTPException(
                status_code=500, 
                detail=f"OCR识别失败: {ocr_response.text}"
            )
        
        ocr_result = ocr_response.json()
        extracted_text = ocr_result.get("text", "")
        confidence = ocr_result.get("confidence", 0)
        
        logger.info(f"[✓] OCR识别完成，置信度: {confidence}")
        
        # 2. 调用LLM进行分析
        logger.info("[*] 发送文本到LLM分析...")
        
        analysis_prompt = f"""
请对以下档案内容进行分析，提供以下信息：

1. **档案完整性评分** (0-100分)：评估档案中包含的信息是否完整
2. **关键信息提取**：从档案中提取的核心信息
3. **内容分类**：档案的主要类别或主题
4. **风险预警**：如果发现任何潜在问题或缺陷
5. **改进建议**：如何改进或补充档案

档案内容：
---
{extracted_text}
---

请按上述格式提供专业的分析报告。
"""
        
        llm_response = requests.post(
            f"{LLM_SERVICE_URL}/api/generate",
            json={
                "model": "llama2",
                "prompt": analysis_prompt,
                "stream": False,
                "options": {
                    "num_predict": 2000,
                    "temperature": 0.7,
                    "top_k": 40,
                    "top_p": 0.9
                }
            },
            timeout=300
        )
        
        if llm_response.status_code != 200:
            logger.warning(f"LLM分析失败，使用默认报告")
            analysis_result = f"档案已识别，共{len(extracted_text)}个字符。由于LLM服务暂不可用，请稍后重试分析。"
        else:
            analysis_result = llm_response.json().get("response", "")
        
        logger.info("[✓] LLM分析完成")
        
        # 3. 存储到数据库（可选）
        if employee_id:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                insert_query = """
                INSERT INTO oovc_employee_archive_analysis 
                (employee_id, archive_name, ocr_text, analysis_report, confidence, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    employee_id,
                    archive_name,
                    extracted_text,
                    analysis_result,
                    confidence,
                    datetime.now()
                ))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                logger.info(f"[✓] 分析结果已保存到数据库")
            except Exception as db_error:
                logger.warning(f"数据库保存失败: {str(db_error)}")
        
        return {
            "status": "success",
            "employee_id": employee_id,
            "archive_name": archive_name,
            "ocr_text": extracted_text,
            "analysis": analysis_result,
            "confidence": confidence,
            "character_count": len(extracted_text),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[✗] 处理档案出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/analysis/batch")
async def batch_analysis(files: list[UploadFile] = File(...)):
    """
    批量处理档案
    
    参数:
        files: 多个档案文件
    
    返回:
        {
            "status": "completed",
            "total": 3,
            "results": [...]
        }
    """
    results = []
    
    for file in files:
        try:
            result = await process_archive(
                archive_name=file.filename,
                file=file
            )
            results.append(result)
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    success_count = sum(1 for r in results if r.get("status") == "success")
    
    return {
        "status": "completed",
        "total": len(files),
        "success": success_count,
        "failed": len(files) - success_count,
        "results": results
    }

@app.get("/analysis/history")
async def get_analysis_history(employee_id: int = None, limit: int = 10):
    """
    获取分析历史
    
    参数:
        employee_id: 员工ID (可选)
        limit: 返回数量
    
    返回:
        {
            "status": "success",
            "total": 5,
            "records": [...]
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if employee_id:
            query = """
            SELECT * FROM oovc_employee_archive_analysis
            WHERE employee_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            cursor.execute(query, (employee_id, limit))
        else:
            query = """
            SELECT * FROM oovc_employee_archive_analysis
            ORDER BY created_at DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
        
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "total": len(records),
            "records": records
        }
    
    except Exception as e:
        logger.error(f"查询历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="查询失败")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
