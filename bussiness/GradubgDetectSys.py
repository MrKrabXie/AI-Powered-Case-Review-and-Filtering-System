
# 环境准备
"""
1. 安装依赖：
pip install langchain-ollama chromadb python-dotenv apscheduler

2. 启动Ollama服务：
ollama serve

3. 下载模型（在终端执行）：
ollama pull mistral
"""

"""
原始文本
├─ 政治敏感过滤 → 立即拦截
├─ 案例库相似检索 → 获取3个最接近历史判例
├─ 动态提示生成 → 注入历史判例和当前场景参数
├─ 大模型三维评估 → 输出场景分/占比分/隐喻分
└─ 分级处置：
├─ 正常通过（综合分<0.2）
├─ 限时修改（0.2≤综合分<0.6）
└─ 人工复核（综合分≥0.6）

"""

import json
from typing import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_community.llms import Ollama
from langchain_ollama import OllamaEmbeddings, OllamaLLM  # 新的导入路径

from datetime import datetime
# 动态场景评估提示模板
DYNAMIC_PROMPT = """
[角色设定]
你是有十年经验的网文责任编辑，熟悉各题材尺度规范

[任务]
对文本进行三维评估：
1. 场景合理性(1-5分)：结合当前剧情发展判断敏感词出现的必要性
2. 描写占比(百分比)：计算敏感内容占段落的比例
3. 隐喻密度(低/中/高)：检测暗示性描写的密集程度

[示例]
文本："两人褪去衣衫倒在绣床上，红烛映照着起伏的身影"
分析：场景合理(4分)/占比20%/隐喻密度高 → 二级预警

待分析文本：{text}
"""

DYNAMIC_JSON_PROMPT = """
[角色设定]
你是有十年经验的网文责任编辑，熟悉各题材尺度规范

[任务]
请根据以下文本内容生成严格符合JSON格式的分析结果：
{{
    "scene_assessment": {{
        "score": <1-5的整数值>,
        "reason": "结合当前剧情发展的合理性分析"
    }},
    "sensitive_ratio": {{
        "percentage": <0-1之间的小数>,
        "description": "敏感内容占比说明"
    }}
}}

评估规则：
1. 医疗类场景默认score=5
2. 政治相关内容ratio>=0.3时自动触发预警
3. 言情类场景需结合上下文判断合理性

待分析文本：{text}
"""

class ContentGuardSystem:
    def __init__(self):
        # 初始化模型组件
        self.embeddings = OllamaEmbeddings(model="mistral")
        self.llm = OllamaLLM(model="mistral")  # 注意类名改为OllamaLLM

        # 初始化向量数据库
        self.vector_store = Chroma(
            collection_name="audit_cases",
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )

        # 政治敏感词库（示例）
        self.political_blacklist = {"特定政治词汇", "习XX"}

        # 类型对应阈值配置
        self.genre_config = {
            '言情': 0.15,
            '悬疑': 0.05,
            '历史': 0.02
        }


    def analyze_text(self, text: str, genre: str) -> dict:
        """核心处理流程"""
        # 快速拦截检查
        if self._contains_blacklist(text):
            return {"action": "block", "reason": "政治敏感内容"}

        # 上下文检索
        similar_cases = self.vector_store.similarity_search(text, k=3)

        # 动态提示生成
        prompt = self._build_dynamic_prompt(text, similar_cases, genre)

        # 大模型分析
        llm_output = self.llm.invoke(prompt)

        # 解析与决策
        scene_score, ratio, metaphor = self._parse_llm_output(llm_output)
        return self._make_decision(scene_score, ratio, metaphor, genre)

    def _build_dynamic_prompt(self, text: str, cases: list, genre: str) -> str:
        """构建动态提示模板"""
        case_context = "\n".join([f"历史案例 {i+1}: {c.page_content}" for i, c in enumerate(cases)])
        return f"""
        当前小说类型：{genre}
        历史审核案例参考：
        {case_context}

        {DYNAMIC_JSON_PROMPT.format(text=text)}
        """

    def _make_decision(self, scene_score: int, ratio: float, metaphor: str, genre: str) -> dict:
        # risk_score = ...  # 保持原有计算方式
        risk_score = (scene_score/5)*0.4 + ratio*0.4 + (0.3 if metaphor=='高' else 0.1)
        # 获取动态阈值并应用
        max_allowed = self._dynamic_threshold(genre)

        # 重新设计决策逻辑
        if ratio <= max_allowed and scene_score >= 3:  # 示例逻辑
            return {"action": "pass"}
        elif ratio <= max_allowed * 1.5:
            return {"action": "require_revision"}
        else:
            return {"action": "human_review"}


    def _parse_llm_output(self, llm_output: str) -> tuple:
        try:
            # 预处理LLM输出（处理常见的格式错误）
            output = llm_output.strip().replace("：", ":").replace("，", ",")

            data = json.loads(output)

            # 防御性数值提取
            score = data.get('scene_assessment', {}).get('score', 5)
            ratio = data.get('sensitive_ratio', {}).get('percentage', 0.0)

            # 强制数值范围
            score = max(1, min(5, int(score)))
            ratio = round(max(0.0, min(1.0, float(ratio))), 2)

            return score, ratio, 0

        except Exception as e:
            print(f"解析失败：{str(e)}")
            return 5, 0.0, 0  # 安全默认值




    # 其他辅助方法实现（部分示例）
    def _contains_blacklist(self, text: str) -> bool:
        return any(word in text for word in self.political_blacklist)

    def _dynamic_threshold(self, genre: str) -> float:
        return self.genre_config.get(genre, 0.1)

    def process_human_review(self, text: str, decision: str):
        """人工审核结果处理"""
        self.vector_store.add_texts(
            texts=[text],
            metadatas=[{
                'decision': decision,
                'timestamp': datetime.now().isoformat()
            }]
        )
# 初始化系统
content_guard = ContentGuardSystem()
