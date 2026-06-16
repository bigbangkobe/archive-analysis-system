"""
OCR识别服务
使用PaddleOCR进行文字识别
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR
from PIL import Image
import io
import os
import logging
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="OCR识别服务", version="1.0.0")

# 初始化PaddleOCR
logger.info("[*] 正在初始化PaddleOCR模型...")
try:
    ocr = PaddleOCR(
        use_angle_cls=True, 
        lang='ch',
        model_storage_directory='/models',
        enable_mkldnn=True,
        use_gpu=False
    )
    logger.info("[✓] PaddleOCR模型加载成功")
except Exception as e:
    logger.error(f"[✗] PaddleOCR模型加载失败: {str(e)}")
    ocr = None

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("[*] OCR服务已启动")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("[*] OCR服务已关闭")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "OCR Service",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": ocr is not None
    }

@app.post("/ocr/recognize")
async def recognize_document(file: UploadFile = File(...)):
    """
    识别文档中的文字
    
    参数:
        file: 上传的图片或PDF文件
    
    返回:
        {
            "status": "success",
            "text": "识别的文本内容",
            "confidence": 0.95,
            "timestamp": "2024-01-01T12:00:00",
            "details": [
                {
                    "text": "文本",
                    "confidence": 0.95,
                    "position": [[x1, y1], [x2, y2], ...]
                }
            ]
        }
    """
    if not ocr:
        raise HTTPException(status_code=503, detail="OCR模型未加载")
    
    try:
        # 检查文件类型
        if file.filename.lower().split('.')[-1] not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail="不支持的文件类型，仅支持: " + ",".join(ALLOWED_EXTENSIONS)
            )
        
        # 检查文件大小
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"文件过大，最大支持{MAX_FILE_SIZE/(1024*1024)}MB"
            )
        
        logger.info(f"[*] 开始识别文件: {file.filename}")
        start_time = time.time()
        
        # 打开图片
        image = Image.open(io.BytesIO(contents))
        
        # 转换为RGB（处理RGBA等格式）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 保存临时文件用于PaddleOCR处理
        temp_path = f"/tmp/{file.filename}"
        image.save(temp_path)
        
        # 执行OCR识别
        result = ocr.ocr(temp_path, cls=True)
        
        # 处理结果
        extracted_text = ""
        details = []
        total_confidence = 0
        confidence_count = 0
        
        if result:
            for line in result:
                for item in line:
                    text = item[1]
                    confidence = float(item[2])
                    position = item[0]
                    
                    extracted_text += text + "\n"
                    details.append({
                        "text": text,
                        "confidence": confidence,
                        "position": [[float(p[0]), float(p[1])] for p in position]
                    })
                    
                    total_confidence += confidence
                    confidence_count += 1
        
        # 计算平均置信度
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        elapsed_time = time.time() - start_time
        logger.info(f"[✓] 文件识别完成，耗时{elapsed_time:.2f}秒")
        
        return {
            "status": "success",
            "filename": file.filename,
            "text": extracted_text.strip(),
            "confidence": round(avg_confidence, 2),
            "character_count": len(extracted_text),
            "line_count": len(details),
            "process_time": round(elapsed_time, 2),
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
    
    except Exception as e:
        logger.error(f"[✗] OCR识别出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")

@app.post("/ocr/batch")
async def batch_recognize(files: list[UploadFile] = File(...)):
    """
    批量识别多个文件
    
    参数:
        files: 多个上传的文件
    
    返回:
        {
            "status": "success",
            "total": 3,
            "results": [
                {"filename": "file1.png", "status": "success", "text": "..."},
                {"filename": "file2.png", "status": "failed", "error": "..."}
            ]
        }
    """
    if not ocr:
        raise HTTPException(status_code=503, detail="OCR模型未加载")
    
    results = []
    
    for file in files:
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            temp_path = f"/tmp/{file.filename}"
            image.save(temp_path)
            
            result = ocr.ocr(temp_path, cls=True)
            
            extracted_text = ""
            if result:
                for line in result:
                    for item in line:
                        extracted_text += item[1] + "\n"
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "text": extracted_text.strip(),
                "character_count": len(extracted_text)
            })
        
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    success_count = sum(1 for r in results if r["status"] == "success")
    
    return {
        "status": "completed",
        "total": len(files),
        "success": success_count,
        "failed": len(files) - success_count,
        "results": results
    }

@app.get("/ocr/models")
async def get_model_info():
    """获取模型信息"""
    return {
        "status": "success",
        "model": "PaddleOCR",
        "version": "2.7.0.3",
        "language": ["Chinese", "English"],
        "angle_recognition": True,
        "model_loaded": ocr is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
