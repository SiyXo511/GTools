from excel_processor.sql_to_table import parse_sql_insert

# 测试第6行的SQL
sql_line6 = """INSERT INTO `rules_output` (`规则ID`, `原始规则`, `源监管清单文本`, `规则来源`, `所属科室`, `所属科室来源`, `涉及违规的医保对象名称`, `涉及违规医保对象名称来源`, `涉及违规的医保对象编码`, `涉及违规医保编码来源`, `问题描述`, `底层数据依赖`, `机器可判定性`, `问题类别`, `问题类别来源`, `认定依据`, `规则涉及的模糊医保对象名称`, `规则涉及模糊医保对象名称来源`, `规则涉及的医保对象名称`, `规则涉及医保对象名称来源`, `规则涉及的医保对象编码`, `规则涉及医保编码来源`, `监管规则重写（要素式）`, `监管规则重写（常规描述）`, `实体识别结果`, `增强后的规则`, `规则标准化推理结果`, `任务书`, `代码`, `创建时间`, `更新时间`, `执行次数`, `失败次数`, `规则状态`, `停用原因`, `用户备注`, `附加信息`, `生成过程日志`) VALUES (2118, '{\"序号\": 270, \"提取实体\": \"小儿智力糖浆\", \"医保目录名称\": \"小儿智力糖浆\", \"限定性别\": \"无\", \"问题描述\": \"医保目录名称为儿童药品专用，参保人年龄超过12，超出儿童年龄限制\", \"政策依据\": \"开窍益智，调补心肾，滋养安神。用于心肾不足，痰浊阻窍所致小儿多动，少语，烦躁不安，神思涣散，少寐健忘，潮热盗汗；儿童多动症见上述证候者。\"}', NULL, '国家库', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);"""

print("=== 诊断SQL解析 ===")
records = parse_sql_insert(sql_line6)
print(f"解析到记录数: {len(records)}")

if records:
    record = records[0]
    print(f"\n列数: {len(record)}")
    print(f"\n所有字段及其值:")
    
    null_count = 0
    non_null_count = 0
    
    for key, value in record.items():
        if value is None:
            null_count += 1
            print(f"  {key}: None")
        else:
            non_null_count += 1
            display_value = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
            print(f"  {key}: {display_value}")
    
    print(f"\n=== 统计 ===")
    print(f"NULL字段数: {null_count}")
    print(f"非NULL字段数: {non_null_count}")

