# 8 问题二求解与结果分析

## 8.1 问题二的求解实现

依据第4章统一模型和第5章算法求解问题二，正式实验设置见第6章。Scene B按计算核组织Task，同核tensor采用片上直接通信，跨核依赖依据官方规则插入COPY_OUT和COPY_IN并施加相应等待。统一求解器在该场景下生成、评价和改进plan，最终指标由问题二官方Evaluator给出。

<!-- Evidence: paper/EVIDENCE_MAP.md A“P2/Scene B”、B、C；paper/sections/04_model.md 4.2.2、4.5；paper/sections/05_algorithm.md 5.1；paper/sections/06_experiment.md -->

## 8.2 多核加速结果

P2的正式平均Speedup在N=1、2、3、4、5时依次为1.0000、1.9004、2.6663、3.2978、3.8369，完整数值与P1并列于表4(a)。其中，N=1是第6章规定的共同单核参考点；P2的多核结果采用P2 VNS记录，单核分母共用正式Scene A singlecore基准。

<!-- Evidence: results/final_visualization/figure_numbers.md“P2加速比”；paper/EVIDENCE_MAP.md E、F；paper/sections/06_experiment.md 6.3 -->

P2平均加速比由N=2时的1.9004增至N=5时的3.8369，在所测核数范围内保持单调增长，且N=2至5的各平均值仍低于相应线性参考值N。

**数据直接支持的事实。** P2在集合平均意义上获得了随核数增长的加速：从双核1.9004增至五核3.8369。该均值趋势不意味着每个case都有同样的扩展曲线。

**结合模型机制的解释。** Scene B仍保留计算图依赖和跨核COPY等待，增加计算核不会消除这些时序条件；负载分布与跨核数据搬运也可能限制并行收益。这些模型因素为平均Speedup未达到N提供了可能解释，当前统计不包含逐因素的独立验证。

<!-- Evidence: 数值来自figure_numbers.md；机制来自paper/EVIDENCE_MAP.md A、C及04_model.md 4.2.2；不据曲线推定各因素独立贡献。 -->

## 8.3 与问题一的对比

图3将P1、P2在相同核数下的正式平均Speedup置于同一坐标中，便于统一比较两场景的扩展趋势及均值差异。

[FIGURE: fig3_p1p2_combined]

<!-- 插图位置：本节首次且唯一完整呈现fig3；第7章不提前引用。推荐caption：图3 P1/P2在不同核数下的正式平均Speedup。100个case逐case计算后取算术平均，两场景共用正式单核基准。fig1_p1_speedup、fig2_p2_speedup置于附录。 -->

**数据直接支持的事实。** 在相同核数下，P2的正式平均Speedup均高于P1：N=2时为1.9004与1.7890，N=3时为2.6663与2.4163，N=4时为3.2978与2.9514，N=5时为3.8369与3.3877。该对比使用相同的100-case范围及共同单核参考，结论限于各核数的集合平均值。

<!-- Evidence: results/final_visualization/figure_numbers.md“P1加速比”“P2加速比”；paper/EVIDENCE_MAP.md E、F；表4(a) -->

**结合模型机制的解释。** Scene A按子图封装Task并处理子图边界COPY；Scene B按核组织Task，同核tensor直接进行片上通信，而跨核边采用COPY_OUT/COPY_IN。P2较高的平均Speedup可能与上述Task组织、通信及等待规则的差异有关。由于两个场景分别求解、执行规则也不同，图3没有隔离某一机制，不能将N=5时3.8369与3.3877的差异全部归因于某一类COPY减少或等待变化，也不能据此断言所有case均由P2取得更低Makespan。

<!-- Evidence: paper/EVIDENCE_MAP.md A；04_model.md 4.2.1、4.2.2；正式数值不构成单一机制的受控因果比较。 -->

## 8.4 本问小结

P2在N=2至5下的正式平均Speedup由1.9004增长到3.8369，且这四个核数的均值均高于对应P1结果。对该差异的机制讨论限于Task组织与通信规则所提供的解释，独立贡献尚不能由当前场景比较确定。

<!-- Evidence: results/final_visualization/figure_numbers.md；paper/EVIDENCE_MAP.md A、E、F -->
