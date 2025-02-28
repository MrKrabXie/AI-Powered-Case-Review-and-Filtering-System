# 测试脚本（test_demo.py）
import json

import bussiness.GradubgDetectSys as GradubgDetectSys
import time
# 初始化系统
guard = GradubgDetectSys.ContentGuardSystem()

def main():
    # 测试不同场景
    test_cases = [
        ("实验室内的常规病理检测", "医疗", "pass"),
        ("他的手掌滑过她腰间的曲线", "言情", "require_revision"),
        ("广场上的群众集会", "都市", "block"),
        ("习XX曾经说过", "官场", "block"),
        ("月光下两人的剪影渐渐重叠", "言情", "human_review")
    ]

    for text, genre, expected in test_cases:
        print(f"测试文本：{text}")
        start = time.time()
        result = guard.analyze_text(text, genre)
        print(f"结果：{result} | 耗时：{time.time()-start:.2f}s")
        print("━"*50)

def add_demo():
    # 添加争议案例到知识库
    decision_str = json.dumps({"action": "pass"})
    guard.process_human_review(
        "她轻咬下唇的娇羞模样",
        decision_str
    )

if __name__ == "__main__":
    add_demo()
    main()
