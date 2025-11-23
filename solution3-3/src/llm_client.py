"""
LLM客户端封装模块
支持多种LLM提供商（Claude、OpenAI、Ollama）
"""

import logging
import json
from typing import Dict, Any, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端基类"""

    def parse_medicine_text(self, text: str) -> Dict[str, Any]:
        """解析药品文本为结构化数据"""
        raise NotImplementedError


class ClaudeClient(LLMClient):
    """Claude API客户端"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022",
                 max_tokens: int = 1024, temperature: float = 0.3):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        logger.info(f"ClaudeClient 初始化: model={model}")

    def parse_medicine_text(self, text: str) -> Dict[str, Any]:
        """
        使用Claude解析药品文本

        Args:
            text: 原始药品信息文本

        Returns:
            结构化数据字典
        """
        prompt = self._build_prompt(text)

        try:
            logger.info(f"调用Claude API解析文本: {text[:50]}...")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            logger.info(f"Claude响应: {response_text[:100]}...")

            # 解析JSON响应
            result = json.loads(response_text)
            logger.info(f"解析成功: {result.get('drug_name', 'N/A')}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 响应: {response_text[:200]}")
            return self._fallback_parse(text)
        except Exception as e:
            logger.error(f"Claude API调用失败: {e}", exc_info=True)
            return self._fallback_parse(text)

    def parse_medicine_batch(self, texts: list[str]) -> list[Dict[str, Any]]:
        """
        批量解析多条药品文本
        
        Args:
            texts: 药品文本列表
            
        Returns:
            结构化数据字典列表
        """
        if not texts:
            return []
            
        if len(texts) == 1:
            return [self.parse_medicine_text(texts[0])]
            
        prompt = self._build_batch_prompt(texts)
        
        try:
            logger.info(f"调用Claude API批量解析: {len(texts)} 条")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens * 2,  # 批量处理需要更多tokens
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            logger.info(f"Claude批量响应: {response_text[:200]}...")
            
            # 解析JSON数组响应
            results = json.loads(response_text)
            
            if not isinstance(results, list):
                logger.error(f"批量解析返回格式错误，期望数组，实际: {type(results)}")
                # 降级为单条处理
                return [self.parse_medicine_text(text) for text in texts]
                
            if len(results) != len(texts):
                logger.warning(f"批量解析结果数量不匹配: 期望{len(texts)}, 实际{len(results)}")
                # 如果数量不匹配，降级为单条处理
                return [self.parse_medicine_text(text) for text in texts]
                
            logger.info(f"批量解析成功: {len(results)} 条")
            return results
            
        except json.JSONDecodeError as e:
            logger.error(f"批量JSON解析失败: {e}, 降级为单条处理")
            return [self.parse_medicine_text(text) for text in texts]
        except Exception as e:
            logger.error(f"批量API调用失败: {e}, 降级为单条处理", exc_info=True)
            return [self.parse_medicine_text(text) for text in texts]

    def _build_batch_prompt(self, texts: list[str]) -> str:
        """构建批量处理提示词"""
        texts_list = "\n".join([f"{i+1}. \"{text}\"" for i, text in enumerate(texts)])
        
        return f"""请从以下多条药品信息文本中提取结构化数据，返回JSON数组。

文本列表：
{texts_list}

请为每条文本提取以下信息：
1. drug_name（药名/通用名）- 必填
2. brand_name（商品名）- 如果文本中有提及
3. generic_name（学术名/化学名）- 根据药名推断
4. quantity（数量）- 提取数字
5. unit（单位）- 如"盒"、"片"、"袋"
6. specification（规格）- 如"0.5g"、"500mg"
7. package_count（包装数量）- 如"1盒"、"2板"
8. expiry_date（有效期）- 格式化为YYYY-MM或YYYY-MM-DD

注意事项：
- 返回JSON数组，数组长度必须等于文本数量（{len(texts)}条）
- 数组顺序必须与输入文本顺序一致
- 如果某个字段在文本中没有提及，请设为空字符串""
- 只返回JSON数组，不要其他说明文字

返回格式示例：
[
  {{
    "drug_name": "阿莫西林",
    "brand_name": "",
    "generic_name": "Amoxicillin",
    "quantity": 1.0,
    "unit": "盒",
    "specification": "",
    "package_count": "1盒",
    "expiry_date": "2027-06"
  }},
  ...
]"""

    def _build_prompt(self, text: str) -> str:
        """构建提示词"""
        return f"""请从以下药品信息文本中提取结构化数据。

文本："{text}"

请提取以下信息并以JSON格式返回：
1. drug_name（药名/通用名）- 必填
2. brand_name（商品名）- 如果文本中有提及
3. generic_name（学术名/化学名）- 根据药名推断，如阿莫西林→Amoxicillin
4. quantity（数量）- 提取数字，如"一盒"→1，"30片"→30
5. unit（单位）- 如"盒"、"片"、"袋"
6. specification（规格）- 如"0.5g"、"500mg"
7. package_count（包装数量）- 如"1盒"、"2板"
8. expiry_date（有效期）- 格式化为YYYY-MM或YYYY-MM-DD，如"2027年6月"→"2027-06"

注意事项：
- 如果某个字段在文本中没有提及，请设为空字符串""
- generic_name可以根据drug_name推断（如果你知道的话）
- 数量和日期尽量标准化
- 只返回JSON，不要其他说明文字

返回格式示例：
{{
    "drug_name": "阿莫西林",
    "brand_name": "",
    "generic_name": "Amoxicillin",
    "quantity": 1.0,
    "unit": "盒",
    "specification": "",
    "package_count": "1盒",
    "expiry_date": "2027-06"
}}"""

    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """后备解析方法（LLM失败时）"""
        logger.warning(f"使用后备解析: {text}")
        return {
            "drug_name": text.split('，')[0] if '，' in text else text.split(',')[0],
            "brand_name": "",
            "generic_name": "",
            "quantity": 0.0,
            "unit": "",
            "specification": "",
            "package_count": "",
            "expiry_date": ""
        }


class OpenAIClient(LLMClient):
    """OpenAI API客户端（待实现）"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        logger.info("OpenAIClient 初始化（未实现）")

    def parse_medicine_text(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError("OpenAI客户端尚未实现")


class OllamaClient(LLMClient):
    """Ollama本地LLM客户端（待实现）"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        logger.info("OllamaClient 初始化（未实现）")

    def parse_medicine_text(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError("Ollama客户端尚未实现")


def create_llm_client(provider: str, **kwargs) -> LLMClient:
    """
    工厂函数：创建LLM客户端

    Args:
        provider: LLM提供商 ("claude", "openai", "ollama")
        **kwargs: 客户端特定参数

    Returns:
        LLMClient实例
    """
    if provider == "claude":
        return ClaudeClient(**kwargs)
    elif provider == "openai":
        return OpenAIClient(**kwargs)
    elif provider == "ollama":
        return OllamaClient(**kwargs)
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")
