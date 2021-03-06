# emotionAnalysis
疫情背景下，基于情感词典和机器学习对新闻和微博评论的情感分析

# Data Science Basics in SWI, NJU, 2020-Fall

> ## 计算社会学：基于NLP技术的新冠疫情下的社会心态研究

Cong Jin , YDJSIR, Sugar Xu‘s  project of 2020 Data Science Basic Course in SWI, NJU.

此为发布开源的版本而不是开发环境中使用的版本。



## 文件结构

```bash
│  LICENSE
│  README.md
├─Analyze # 分析数据的过程中所使用的所有代码
├─Data # 原始数据以及处理过后的所有数据
├─Report # 报告相关源文件以及最终报告的成品
└─Spyder # 爬虫代码
```

文件结构经过事后整理，并不是工作时目录的状态，因而代码中所涉及的路径需要稍加修改后运行。

原始报告数据在评分后抹掉相关关键词后后放出。



> ### `Data`目录下文件结构
>
> 该目录下共有6个文件夹，分别对应`stage0` - `stage6`
>
> ##### stage内文件目录结构
>
> ```bash
> │  COVkeywords-Stage<No>-.json # 人工筛选后的疫情相关关键词
> │  COVkeywords-Stage<No>.json  # 未经筛选的疫情关键词
> │  keywords-Stage<No>.json	   # 从荔枝新闻中获取的原始结果
> │  ratioByDate.png			   # 该阶段内每日疫情相关重点微博占比
> │  SaveTest.png				   # 疫情相关度分布拟合结果图1
> │  SaveTest_Fit.png			   # 疫情相关度分布拟合结果图2
> │  stageCOVWeibo.json		   # 该阶段内疫情相关重点微博（按时间先后排序）
> │  stageCOVWeiboByImportance.json	# 该阶段内疫情相关重点微博（按疫情相关度排序）
> |  SaveTest-热度.png            # 各项热度指标占比 
> │  stageInfo.json			   # 该阶段基础信息
> │  weiboPolar.png              # 疫情相关重点微博情感极性图
> |  weiboEmotion.png            # 当前阶段的疫情相关微博情感倾向
> ├─YYYY-MM-DD-
> ├─YYYY-MM-DD-
> ├─YYYY-MM-DD-
> ├─YYYY-MM-DD-
> ...
> └─YYYY-MM-DD-
> ```
>
> ##### 每个日期内文件目录结构
>
> ```bash
> YYYY-MM-DD 
> | jstvRAW.csv # 疫情相关关键词检索得到的荔枝新闻原始数据
> | <YYYY-MM-DD->keywords.json # 荔枝新闻正文提取出来的关键词及其乘以100以后的TextRank权值
> | <YYYY-MM-DD->wordcloud.html # 由荔枝新闻生成的词云图
> | <YYYY-MM-DD->blog-Scored.json # 每篇微博都有一个疫情相关度
> | <YYYY-MM-DD->blog-COV.json # 筛选后的新冠疫情相关微博
> | <YYYY-MM-DD->blogInfo.json # 当日博客相关基础信息
> | <YYYY-MM-DD->weiboEmotion.png # 基于心态词典的当日疫情相关微博重点评论情感分析生成的雷达图
> └─<YYYY-MM-DD->weiboEmotion.csv # 基于心态词典的当日疫情相关微博重点评论情感分析原始数据
> ```

=======

# emotionAnalysis

疫情背景下，基于情感词典和机器学习对新闻和微博评论的情感分析

>>>>>>> 2a2647e2590bc86a53c28a4257d00c8a8c399fed
