#!/usr/bin/env python3
"""
meeting-analyzer.py - 会议内容分析与行动项提取脚本

功能：
- 从会议转录文本中提取结构化信息
- 识别行动项（任务/负责人/截止时间）
- 分析发言人分布与议题分布
- 识别会议类型
- 输出结构化分析结果

Usage:
    python3 meeting-analyzer.py --input <meeting-transcript.txt> [--output <analysis.json>]
"""

import re
import json
import argparse
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple


# ============================================================
# 会议类型识别
# ============================================================

MEETING_TYPE_KEYWORDS = {
    "项目例会": ["进度", "里程碑", "sprint", "迭代", "站会", "周会", "项目", "延期", "上线"],
    "管理层会议": ["战略", "预算", "OKR", "KPI", "人力", "扩招", "汇报", "季度", "年度"],
    "技术评审": ["架构", "方案", "代码", "评审", "review", "技术债", "设计", "接口", "API"],
    "头脑风暴": ["创意", "想法", "brainstorm", "发散", "灵感", "探讨", "头脑风暴", "点子"],
    "客户会议": ["客户", "需求", "合同", "交付", "验收", "甲方", "乙方", "商务"],
}

ACTION_PATTERNS = [
    r'([^\s，。！？]+)[负]责([^，。！？\n]{2,30})',
    r'([^\s，。！？]+)[将会要]([去做完成跟进处理]{1,3})([^，。！？\n]{3,30})',
    r'([^\s，。！？]+)[回去]([查看了解确认]{1,3})([^，。！？\n]{3,30})',
    r'action item[：:]?\s*([^，。！？\n]{5,50})',
    r'待办[：:]?\s*([^，。！？\n]{3,50})',
    r'([^\s，。！？]+)[需要]([^，。！？\n]{3,40})[，。]',
]

DATE_PATTERNS = [
    r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
    r'(下周[一二三四五六日])',
    r'(本周[一二三四五六日])',
    r'(\d+月\d+日)',
    r'(下次会议[前后]?)',
    r'(\d+天内)',
    r'(今[天晚]|明[天晚]|后天)',
]

PERSON_INDICATORS = ["说", "提到", "表示", "认为", "建议", "提出", "反馈", "汇报", "负责", "确认", "跟进"]


def detect_meeting_type(text: str) -> str:
    """识别会议类型"""
    scores = {}
    for meeting_type, keywords in MEETING_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text.lower())
        scores[meeting_type] = score
    if max(scores.values(), default=0) == 0:
        return "综合会议"
    return max(scores, key=scores.get)


def extract_participants(text: str) -> List[str]:
    """
    从会议文本中提取参与者姓名（简单模式匹配）
    识别 "张三说/提到/建议" 等模式
    """
    participants = set()
    for indicator in PERSON_INDICATORS:
        pattern = rf'([^\s，。！？\n]{1,4}){indicator}'
        matches = re.findall(pattern, text)
        for match in matches:
            # 过滤明显非人名的词
            if len(match) >= 2 and not any(skip in match for skip in ["会议", "系统", "项目", "方案", "需求"]):
                participants.add(match.strip())
    return sorted(list(participants))


def extract_action_items(text: str) -> List[Dict]:
    """提取行动项（任务/负责人/截止时间）"""
    action_items = []
    
    # 按行处理
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # 跳过空行
        if not line.strip():
            continue
        
        # 检测行动指标词
        action_indicators = ["负责", "跟进", "回去查", "需要", "action", "待办", "确认", "安排"]
        if any(indicator in line.lower() for indicator in action_indicators):
            # 提取时间
            deadline = "未定"
            for pattern in DATE_PATTERNS:
                match = re.search(pattern, line)
                if match:
                    deadline = match.group(1)
                    break
            
            # 提取负责人
            person = "待确认"
            for indicator in PERSON_INDICATORS:
                pattern = rf'([^\s，。！？]{1,4}){indicator}'
                match = re.search(pattern, line)
                if match:
                    candidate = match.group(1).strip()
                    if len(candidate) >= 2:
                        person = candidate
                        break
            
            action_items.append({
                "task": line.strip()[:80],  # 截断过长任务描述
                "owner": person,
                "deadline": deadline,
                "priority": "中",  # 默认中优先级
                "source_line": i + 1,
            })
    
    return action_items


def extract_topics(text: str, max_topics: int = 7) -> List[Dict]:
    """提取会议议题（基于段落结构）"""
    topics = []
    
    # 按段落分割
    paragraphs = re.split(r'\n{2,}', text)
    
    for i, para in enumerate(paragraphs[:max_topics]):
        if len(para.strip()) < 20:
            continue
        
        # 取段落首句作为议题标题
        first_sentence = re.split(r'[。！？\n]', para)[0][:50]
        summary = para.strip()[:200]
        
        topics.append({
            "index": i + 1,
            "title": first_sentence.strip(),
            "summary": summary,
        })
    
    return topics


def extract_decisions(text: str) -> List[str]:
    """提取决议事项"""
    decisions = []
    decision_patterns = [
        r'决定[：:]?([^。！？\n]{5,60})',
        r'确认[：:]?([^。！？\n]{5,60})',
        r'批准[：:]?([^。！？\n]{5,60})',
        r'同意[：:]?([^。！？\n]{5,60})',
        r'达成[共识一致][：:]?([^。！？\n]{5,60})',
    ]
    for pattern in decision_patterns:
        matches = re.findall(pattern, text)
        decisions.extend([m.strip() for m in matches if len(m.strip()) > 5])
    return list(dict.fromkeys(decisions))  # 去重保序


def extract_conflicts(text: str) -> List[Dict]:
    """识别分歧与争议点"""
    conflicts = []
    conflict_patterns = [
        r'([^\s，。]{2,8})[认为主张]([^，。！？]{5,40})[，。].*?([^\s，。]{2,8})[认为主张]([^，。！？]{5,40})',
        r'分歧[在于是]([^，。！？\n]{5,60})',
        r'争议[点是在]([^，。！？\n]{5,60})',
        r'有人[认为主张]([^，。！？\n]{5,40})[，。]?也有人([^，。！？\n]{5,40})',
    ]
    for pattern in conflict_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if isinstance(m, tuple) and len(m) >= 2:
                conflicts.append({
                    "topic": str(m[0])[:40],
                    "viewpoints": [str(v)[:60] for v in m[1:]],
                    "status": "待讨论",
                })
            elif isinstance(m, str):
                conflicts.append({
                    "topic": m[:60],
                    "viewpoints": ["待整理"],
                    "status": "已识别",
                })
    return conflicts[:5]  # 最多返回5条


def analyze_meeting(text: str) -> Dict:
    """主分析函数：综合分析会议文本"""
    if not text or not text.strip():
        raise ValueError("输入文本为空，请提供有效的会议记录")
    
    result = {
        "analyzed_at": datetime.now().isoformat(),
        "text_length": len(text),
        "meeting_type": detect_meeting_type(text),
        "participants": extract_participants(text),
        "topics": extract_topics(text),
        "action_items": extract_action_items(text),
        "decisions": extract_decisions(text),
        "conflicts": extract_conflicts(text),
        "stats": {
            "topic_count": 0,
            "action_item_count": 0,
            "decision_count": 0,
            "conflict_count": 0,
            "participant_count": 0,
        }
    }
    
    # 填充统计
    result["stats"]["topic_count"] = len(result["topics"])
    result["stats"]["action_item_count"] = len(result["action_items"])
    result["stats"]["decision_count"] = len(result["decisions"])
    result["stats"]["conflict_count"] = len(result["conflicts"])
    result["stats"]["participant_count"] = len(result["participants"])
    
    return result


def print_summary(analysis: Dict) -> None:
    """打印分析摘要"""
    print("=" * 50)
    print("📊 会议分析摘要")
    print("=" * 50)
    print(f"会议类型: {analysis['meeting_type']}")
    print(f"文本长度: {analysis['text_length']} 字")
    print(f"参与者: {', '.join(analysis['participants']) or '未识别'}")
    print()
    print(f"📋 议题数量: {analysis['stats']['topic_count']}")
    print(f"✅ 决议事项: {analysis['stats']['decision_count']}")
    print(f"📌 行动项数: {analysis['stats']['action_item_count']}")
    print(f"⚠️  分歧点数: {analysis['stats']['conflict_count']}")
    print()
    
    if analysis["action_items"]:
        print("行动项列表:")
        for i, item in enumerate(analysis["action_items"][:10], 1):
            print(f"  {i}. [{item['owner']}] {item['task'][:60]} | 截止: {item['deadline']}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="meeting-analyzer.py — 会议内容分析与行动项提取"
    )
    parser.add_argument("--input", "-i", required=True, help="会议转录文本文件路径")
    parser.add_argument("--output", "-o", help="输出分析结果的JSON文件路径（可选）")
    parser.add_argument("--summary", "-s", action="store_true", help="仅打印摘要")
    args = parser.parse_args()
    
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"错误: 文件不存在 — {args.input}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print("错误: 文件编码不支持，请确保文件为 UTF-8 编码", file=sys.stderr)
        sys.exit(1)
    
    try:
        analysis = analyze_meeting(text)
    except ValueError as e:
        print(f"分析失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.summary:
        print_summary(analysis)
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"✅ 分析结果已保存: {args.output}")
        print_summary(analysis)
    else:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
