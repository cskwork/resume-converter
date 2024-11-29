from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import os
import logging
import time
from langchain.llms import Ollama
from googlesearch import search
from bs4 import BeautifulSoup
import random
from config import OLLAMA_BASE_URL, DEFAULT_MODEL, AVAILABLE_MODELS, MODEL_SETTINGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Ollama with default model
current_model = DEFAULT_MODEL
try:
    llm = Ollama(
        model=current_model,
        base_url=OLLAMA_BASE_URL,
        **MODEL_SETTINGS.get(current_model, {})
    )
    logger.info(f"Successfully initialized Ollama with model: {current_model}")
except Exception as e:
    logger.error(f"Failed to initialize Ollama: {str(e)}")
    raise

@app.route('/models', methods=['GET', 'POST'])
def handle_models():
    """Get available models or register a new one"""
    global AVAILABLE_MODELS
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            model_id = data.get('id')
            model_name = data.get('name', model_id)
            
            # Validate model exists in Ollama
            try:
                test_llm = Ollama(
                    model=model_id,
                    base_url=OLLAMA_BASE_URL
                )
                # Try a simple test prompt
                test_llm("test")
            except Exception as e:
                logger.error(f"Model validation failed: {str(e)}")
                return jsonify({
                    'error': f'모델을 찾을 수 없습니다. Ollama에 모델이 설치되어 있는지 확인해주세요: {str(e)}'
                }), 400
            
            # Check if model already exists
            if model_id in [m['id'] for m in AVAILABLE_MODELS]:
                return jsonify({'error': '이미 등록된 모델입니다.'}), 400
            
            # Add new model
            new_model = {'id': model_id, 'name': model_name}
            AVAILABLE_MODELS.append(new_model)
            
            # Add default settings for the new model
            MODEL_SETTINGS[model_id] = {
                'temperature': 0.7,
                'top_p': 0.9,
            }
            
            logger.info(f"New model registered: {model_id}")
            return jsonify({'success': True, 'model': new_model})
            
        except Exception as e:
            logger.error(f"Error registering model: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify(AVAILABLE_MODELS)

@app.route('/model', methods=['GET', 'POST'])
def handle_model():
    """Get or set current model"""
    global current_model, llm
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            new_model = data.get('model')
            
            if new_model not in [m['id'] for m in AVAILABLE_MODELS]:
                return jsonify({'error': '유효하지 않은 모델입니다.'}), 400
            
            # Initialize new model
            llm = Ollama(
                model=new_model,
                base_url=OLLAMA_BASE_URL,
                **MODEL_SETTINGS.get(new_model, {})
            )
            current_model = new_model
            logger.info(f"Switched to model: {current_model}")
            
            return jsonify({'success': True, 'model': current_model})
        except Exception as e:
            logger.error(f"Error switching model: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'model': current_model})

def get_company_info_from_web(company_name):
    """
    Get company information from web search results
    """
    logger.info(f"Starting web search for company: {company_name}")
    collected_info = []
    sources = []
    
    try:
        # Search for company information
        search_query = f"{company_name} 회사 정보 기업문화 비전"
        search_results = list(search(search_query, lang="kr", num_results=5))
        
        for url in search_results:
            try:
                # Yield progress for each URL
                progress_msg = {"status": "searching", "message": f"검색 중: {url}"}
                yield json.dumps(progress_msg, ensure_ascii=False)
                
                # Add random delay between requests
                time.sleep(random.uniform(1, 2))
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text and clean it
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Truncate text if too long
                if len(text) > 2000:
                    text = text[:2000] + "..."
                
                if text.strip():
                    collected_info.append(text)
                    sources.append(url)
                    
            except Exception as e:
                logger.warning(f"Error scraping {url}: {str(e)}")
                continue
        
        # Combine collected information with sources
        combined_text = "\n\n".join(collected_info)
        source_text = "\n\n## 참고 출처\n" + "\n".join([f"- {url}" for url in sources])
        
        yield combined_text + "\n" + source_text
        
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        raise Exception(f"웹 검색 중 오류가 발생했습니다: {str(e)}")

def analyze_company(company_name):
    """
    Analyze company information and values using web data and Ollama
    """
    logger.info(f"Starting company analysis for: {company_name}")
    
    try:
        # Get recent company information from the web with progress updates
        company_info_generator = get_company_info_from_web(company_name)
        company_info = ""
        
        # Process the generator
        for progress in company_info_generator:
            try:
                progress_data = json.loads(progress)
                if isinstance(progress_data, dict) and 'status' in progress_data:
                    # This is a progress update, yield it
                    yield progress
                else:
                    # This is the final data
                    company_info = progress
            except json.JSONDecodeError:
                # This is the final data
                company_info = progress
        
        prompt = f"""
        회사 정보 분석:
        회사 이름: {company_name}
        
        웹에서 수집된 정보:
        {company_info}
        
        위 정보를 바탕으로 다음 사항들을 분석해서 한국어로 작성해주세요.
        마크다운 형식으로 작성하되, 각 섹션을 명확하게 구분해주세요.
        참고 출처는 그대로 유지해주세요.

        # 회사 분석 결과

        ## 1. 회사의 주요 가치관
        - 가치관 1
        - 가치관 2
        - ...

        ## 2. 회사 문화
        - 문화 특징 1
        - 문화 특징 2
        - ...

        ## 3. 이상적인 직원 프로필
        - 역량 1
        - 역량 2
        - ...

        ## 4. 주요 기술 스택 및 요구사항
        - 기술 1
        - 기술 2
        - ...

        ## 5. 최근 회사의 주요 성과나 방향성
        - 성과/방향성 1
        - 성과/방향성 2
        - ...

        위 형식을 참고하여 구체적이고 실용적으로 작성해주세요.
        """
        
        logger.info("Sending company analysis prompt to Ollama")
        response = llm(prompt)
        logger.info("Successfully received company analysis from Ollama")
        yield response.strip()
        
    except Exception as e:
        logger.error(f"Error in company analysis: {str(e)}")
        raise Exception(f"회사 분석 중 오류가 발생했습니다: {str(e)}")

def optimize_resume(resume_text, company_analysis):
    """
    Optimize the resume based on company analysis
    """
    logger.info("Starting resume optimization")
    try:
        prompt = f"""
        다음 이력서를 회사 분석 결과에 맞게 최적화해주세요.
        마크다운 형식으로 작성해주세요:

        원본 이력서:
        {resume_text}
        
        회사 분석:
        {company_analysis}
        
        요구사항:
        1. 정확성 유지하면서 회사의 가치관과 문화에 맞게 조정
        2. 회사의 현재 방향성과 일치하는 경험 강조
        3. 핵심 역량을 회사의 요구사항에 맞게 재구성
        4. 전문 용어를 회사의 기술 스택에 맞게 조정
        5. 성과 중심적인 서술로 변환

        ## 자기소개
        [회사의 가치관과 문화에 맞춘 자기소개]

        원본 이력서의 내용을 유지하면서 회사에 최적화된 형태로 작성해주세요.
        """
        
        logger.info("Sending resume optimization prompt to Ollama")
        response = llm(prompt)
        logger.info("Successfully received optimized resume from Ollama")
        return response.strip()
    except Exception as e:
        logger.error(f"Error in resume optimization: {str(e)}")
        raise Exception(f"이력서 최적화 중 오류가 발생했습니다: {str(e)}")

def generate_progress():
    try:
        yield "data: " + json.dumps({"status": "started", "message": "분석 시작..."}) + "\n\n"
        time.sleep(0.5)
        
        yield "data: " + json.dumps({"status": "analyzing", "message": "회사 정보 수집 중..."}) + "\n\n"
        
        # Company analysis now yields progress updates
        company_analysis = ""
        for progress in analyze_company(company_name):
            if isinstance(progress, str):
                try:
                    progress_data = json.loads(progress)
                    if progress_data.get('status') == 'searching':
                        yield "data: " + json.dumps({
                            "status": "analyzing",
                            "message": progress_data['message']
                        }, ensure_ascii=False) + "\n\n"
                except json.JSONDecodeError:
                    company_analysis = progress
            else:
                company_analysis = progress
        
        yield "data: " + json.dumps({"status": "analyzed", "message": "회사 분석 완료"}) + "\n\n"
        time.sleep(0.5)
        
        yield "data: " + json.dumps({"status": "optimizing", "message": "이력서 최적화 중..."}) + "\n\n"
        optimized_resume = optimize_resume(resume_text, company_analysis)
        
        result = {
            "status": "complete",
            "company_analysis": company_analysis,
            "optimized_resume": optimized_resume
        }
        logger.info("Successfully completed optimization process")
        yield "data: " + json.dumps(result, ensure_ascii=False) + "\n\n"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in progress generation: {error_msg}")
        yield "data: " + json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False) + "\n\n"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        global company_name, resume_text  # Make these accessible to generate_progress
        company_name = data.get('company')
        resume_text = data.get('resume')
        
        if not company_name or not resume_text:
            return jsonify({'error': '회사명과 이력서 내용을 모두 입력해주세요.'}), 400

        return Response(generate_progress(), mimetype='text/event-stream')
    except Exception as e:
        logger.error(f"Error in optimization process: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application on port 5001")
    app.run(debug=True, port=5001)
