#!/bin/bash
# validate.sh - 会议纪要格式完整性验证脚本
# Usage: ./validate.sh <meeting-minutes-file.md>
# Output: PASS or FAIL with details

set -e

INPUT_FILE="$1"
PASS=true
ERRORS=()

if [ -z "$INPUT_FILE" ]; then
    echo "Usage: ./validate.sh <meeting-minutes-file.md>"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "FAIL: 输入文件不存在: $INPUT_FILE"
    exit 1
fi

echo "=== 会议纪要格式验证 ==="
echo "文件: $INPUT_FILE"
echo ""

# Check 1: 必要章节存在
echo "[1/8] 检查必要章节..."
REQUIRED_SECTIONS=("议题摘要" "决议事项" "行动项追踪" "关键分歧")
for section in "${REQUIRED_SECTIONS[@]}"; do
    if ! grep -q "$section" "$INPUT_FILE"; then
        PASS=false
        ERRORS+=("缺少章节: $section")
        echo "  ✗ 缺少: $section"
    else
        echo "  ✓ 存在: $section"
    fi
done

# Check 2: 会议基础信息
echo "[2/8] 检查会议基础信息..."
INFO_FIELDS=("日期" "参与者")
for field in "${INFO_FIELDS[@]}"; do
    if ! grep -q "$field" "$INPUT_FILE"; then
        PASS=false
        ERRORS+=("缺少基础信息: $field")
        echo "  ✗ 缺少: $field"
    else
        echo "  ✓ 存在: $field"
    fi
done

# Check 3: 行动项表格格式验证
echo "[3/8] 检查行动项表格..."
if grep -q "行动项追踪" "$INPUT_FILE"; then
    if grep -q "负责人" "$INPUT_FILE" && grep -q "截止时间" "$INPUT_FILE"; then
        echo "  ✓ 行动项表头格式正确"
    else
        PASS=false
        ERRORS+=("行动项表格缺少必要列（负责人/截止时间）")
        echo "  ✗ 行动项表格缺少必要列"
    fi
fi

# Check 4: 检查是否有空白负责人（禁止）
echo "[4/8] 检查行动项负责人..."
if grep -P "^\| \d+ \|[^|]+\|\s*\|" "$INPUT_FILE" > /dev/null 2>&1; then
    PASS=false
    ERRORS+=("存在负责人为空的行动项")
    echo "  ✗ 发现空白负责人字段"
else
    echo "  ✓ 所有行动项均有负责人或待确认标注"
fi

# Check 5: 优先级字段格式
echo "[5/8] 检查优先级字段..."
if grep -q "行动项" "$INPUT_FILE"; then
    if grep -q -E "(高|中|低)" "$INPUT_FILE"; then
        echo "  ✓ 优先级字段格式正确"
    else
        echo "  ⚠ 未检测到优先级字段（高/中/低），建议补充"
    fi
fi

# Check 6: 决议事项非空
echo "[6/8] 检查决议事项..."
DECISIONS_COUNT=$(grep -c "^\d\+\." "$INPUT_FILE" 2>/dev/null || echo "0")
if [ "$DECISIONS_COUNT" -gt "0" ] || grep -A5 "决议事项" "$INPUT_FILE" | grep -q "\S"; then
    echo "  ✓ 决议事项非空"
else
    echo "  ⚠ 决议事项可能为空，请核实"
fi

# Check 7: 分歧表格
echo "[7/8] 检查分歧与待确认章节..."
if grep -q "关键分歧\|全面共识" "$INPUT_FILE"; then
    echo "  ✓ 分歧章节存在"
else
    PASS=false
    ERRORS+=("缺少关键分歧与待确认章节")
    echo "  ✗ 缺少关键分歧章节"
fi

# Check 8: 免责声明
echo "[8/8] 检查自动生成声明..."
if grep -q "smart-meeting-minutes\|自动生成" "$INPUT_FILE"; then
    echo "  ✓ 自动生成声明存在"
else
    echo "  ⚠ 缺少自动生成声明（建议补充）"
fi

echo ""
echo "================================"
if [ "$PASS" = true ]; then
    echo "✅ PASS - 会议纪要格式验证通过"
    exit 0
else
    echo "❌ FAIL - 发现以下问题："
    for error in "${ERRORS[@]}"; do
        echo "  • $error"
    done
    exit 1
fi
