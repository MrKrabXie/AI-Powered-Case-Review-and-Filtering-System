
1. **智能分级检测系统架构**

[bussiness](bussiness)： 
   [CheckArticle.py](bussiness/CheckArticle.py) 分析正负面情绪的程序
   [GradubgDetectSys.py](bussiness/GradubgDetectSys.py) 分级检测系统
[test](test)
   [test_detectSys.py](test/test_detectSys.py) 测试 分级检测系统
   [test_sst-model.py](test/test_sst-model.py)  测试 正负面情绪的系统
[test_chroma](test_chroma)
   [add.py](test_chroma/add.py) 测试本地向量的代码


   原始文本
   ├─ 政治敏感过滤 → 立即拦截
   ├─ 案例库相似检索 → 获取3个最接近历史判例
   ├─ 动态提示生成 → 注入历史判例和当前场景参数
   ├─ 大模型二维评估 → 输出场景分/占比分
   └─ 分级处置：
   ├─ 正常通过（综合分<0.2）
   ├─ 限时修改（0.2≤综合分<0.6）
   └─ 人工复核（综合分≥0.6）

- 使用Ollama运行mistral 7B模型（平衡性能与速度）
- ChromaDB存储最近3个月的人工审核案例（按照选中次数进行排序，把比对次数少的给删除掉， 维持一个量级的响亮库）
- 每周自动生成微调数据集（保留各分类典型样本）


2. 后续的功能：
a.界面， 界面去审核， 作为工具的话就QT去做吧， 或者网页也行。 想试试QT
b.一个消息机制， 满足用户申诉要求， 它和人工审核占用同一个消息队列
c.下载模型是用通用模型，之后最好自己预训练一个模型， 然后再半夜的时候不停地训练， 增加准确率，和专业性， 并且不同语言和不同尺度的模型也会要求， 用量身定制的模型去应对效果更好
d。chroma向量库， 如果有性能要求再换。
e. langchain的模型准确度的性能监控， langSMITH, 可以结合进来完成。
f. 对于不同细分分类的类别的体裁文章他们关键字，模型是不一样的， 这一块儿， 通过测试后去做比较好。 目前只用中文的。

3. 后续要模块
a.版权问题
b.种族问题
c.宗教问题
---

# AI-Powered-Case-Review-and-Filtering-System
A comprehensive system for dynamic legal case review and filtering, powered by the Mistral 7B model running via Ollama. This project features:

Political Sensitivity Filter: Immediate interception of politically sensitive content.
Case Similarity Search: Retrieve the top 3 most relevant historical cases based on similarity.
Dynamic Hint Generation: Inject historical cases and scene parameters for context-driven suggestions.
Two-Dimensional Evaluation with Large Models: Scene scoring and distribution outputs.
Tiered Processing:
Normal Approval (Overall Score < 0.2)
Time-Limited Modification (0.2 ≤ Overall Score < 0.6)
Manual Review (Overall Score ≥ 0.6)
Features include:

Use of ChromaDB for storing manually reviewed cases from the past 3 months, prioritized by frequency of selection.
Automated weekly creation of fine-tuning datasets, retaining key samples from each classification.
