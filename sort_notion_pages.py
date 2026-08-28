#!/usr/bin/env python3
"""Sort Notion database entries by stage and priority, output numbered titles."""

cpp_data = [
    {"知识点": "函数", "阶段": "基础语法", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f8104a125c1582bd24931"},
    {"知识点": "构造函数与析构函数", "阶段": "面向对象", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81059a37d02a9947636b"},
    {"知识点": "指针与引用", "阶段": "基础语法", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f8114a49fd74f5daa10e5"},
    {"知识点": "多态与虚函数", "阶段": "面向对象", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f812eb3cce3f686263229"},
    {"知识点": "类与对象", "阶段": "面向对象", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81359ea1f98c2eeede00"},
    {"知识点": "智能指针", "阶段": "现代C++", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f817f8b2fd7e0f33db2b8"},
    {"知识点": "控制流程", "阶段": "基础语法", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f8188a6d7e8281323c1a3"},
    {"知识点": "变量与数据类型", "阶段": "基础语法", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f819dac00ce24cf718026"},
    {"知识点": "序列容器", "阶段": "STL与模板", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81c589c6cf9acc6e5772"},
    {"知识点": "继承", "阶段": "面向对象", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81c7887fc338b27691ec"},
    {"知识点": "数组与字符串", "阶段": "基础语法", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81e098a9fbc92f0d40b9"},
    {"知识点": "运算符与表达式", "阶段": "基础语法", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81e5a661e80e08441080"},
    {"知识点": "关联容器", "阶段": "STL与模板", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f8107a9ded2aa705aa885"},
    {"知识点": "算法", "阶段": "STL与模板", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f811185c2d380da51832f"},
    {"知识点": "运算符重载", "阶段": "面向对象", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f8132a0ffc8ab1e7a1563"},
    {"知识点": "模板与泛型编程", "阶段": "STL与模板", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f8154ada1c58df5286f72"},
    {"知识点": "学生成绩管理系统", "阶段": "实战项目", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f8159a4f6f52965bde7a6"},
    {"知识点": "移动语义与完美转发", "阶段": "现代C++", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f815ba525f7f1629a439c"},
    {"知识点": "auto与类型推导", "阶段": "现代C++", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81998b0acce8551e08aa"},
    {"知识点": "多线程生产者消费者", "阶段": "实战项目", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f819cb8d6f76322ccc188"},
    {"知识点": "内存管理", "阶段": "STL与模板", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81c8bbbef9e68cfccf42"},
    {"知识点": "Lambda表达式", "阶段": "现代C++", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81d49911d4244d0d71d6"},
    {"知识点": "迭代器与适配器", "阶段": "STL与模板", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81d7b2fdcc9f23d52636"},
    {"知识点": "简易计算器", "阶段": "实战项目", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81eebb13e022359835e9"},
    {"知识点": "多线程编程", "阶段": "STL与模板", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81f799fcc5e87e4f97ae"},
    {"知识点": "范围for与初始化列表", "阶段": "现代C++", "优先级": "P2-了解", "url": "https://app.notion.com/p/3c9503fbd69f810c8650c05d3d7819a5"},
]

ros_data = [
    {"知识点": "节点管理与launch文件", "阶段": "基础与架构", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f8103a1d1cc27587f8404"},
    {"知识点": "自定义消息类型", "阶段": "核心通信", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f810884a2da8ab43450cf"},
    {"知识点": "机械臂运动规划", "阶段": "仿真与进阶", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f8111a0c2e5b677fb4f4f"},
    {"知识点": "第一个ROS程序小海龟", "阶段": "基础与架构", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f811f9b9de2c99f2e908c"},
    {"知识点": "服务Service", "阶段": "核心通信", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81228d52e30d9c570cdd"},
    {"知识点": "动作Action", "阶段": "核心通信", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f8146a2d1c1f93d520fd5"},
    {"知识点": "SLAM建图", "阶段": "导航与感知", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f815da047f554cbeb6bb9"},
    {"知识点": "Xacro宏语言", "阶段": "机械臂与操作", "优先级": "P2-了解", "url": "https://app.notion.com/p/3c9503fbd69f8160a9aace474c2dfb3a"},
    {"知识点": "感知处理基础", "阶段": "导航与感知", "优先级": "P2-了解", "url": "https://app.notion.com/p/3c9503fbd69f816588cfd24af91acd89"},
    {"知识点": "Ubuntu与ROS安装", "阶段": "基础与架构", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f816aa809ec17be6bad55"},
    {"知识点": "RViz可视化工具", "阶段": "仿真与进阶", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f816d8983d9fd0fc59540"},
    {"知识点": "参数服务器", "阶段": "核心通信", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81708409d063d96f2536"},
    {"知识点": "什么是ROS", "阶段": "基础与架构", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f8186a635c7dde92d1b39"},
    {"知识点": "创建功能包", "阶段": "基础与架构", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f818c9865f3a1b1c678a2"},
    {"知识点": "URDF基础", "阶段": "机械臂与操作", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f818f8ae3ee4706cde9a4"},
    {"知识点": "导航栈Navigation", "阶段": "导航与感知", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f8197b8f6c81644b6ceab"},
    {"知识点": "话题Topic", "阶段": "核心通信", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f819c910fc7751640383e"},
    {"知识点": "TF坐标变换", "阶段": "仿真与进阶", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81ae84ced943cdee5177"},
    {"知识点": "ROS版本选择", "阶段": "基础与架构", "优先级": "P2-了解", "url": "https://app.notion.com/p/3c9503fbd69f81ae9364ea6522297300"},
    {"知识点": "Gazebo仿真环境", "阶段": "仿真与进阶", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81b3aa8cdbce73263e14"},
    {"知识点": "传感器与消息类型", "阶段": "导航与感知", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81b5b006ecf38fd6ac06"},
    {"知识点": "移动机器人仿真导航", "阶段": "仿真与进阶", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81b797f8f7f6c6045c6f"},
    {"知识点": "工作空间结构", "阶段": "基础与架构", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81c88fdac5110ae24aee"},
    {"知识点": "Gazebo插件配置", "阶段": "机械臂与操作", "优先级": "P2-了解", "url": "https://app.notion.com/p/3c9503fbd69f81dd953ec0700be59201"},
    {"知识点": "rqt与rosbag", "阶段": "仿真与进阶", "优先级": "P2-了解", "url": "https://app.notion.com/p/3c9503fbd69f81e8891fe2f9c689e029"},
    {"知识点": "项目需求分析", "阶段": "仿真与进阶", "优先级": "P1-重要", "url": "https://app.notion.com/p/3c9503fbd69f81ed8b37d76ee3289294"},
    {"知识点": "Catkin编译系统", "阶段": "基础与架构", "优先级": "P0-核心", "url": "https://app.notion.com/p/3c9503fbd69f81ee957edd3b2a36a7f2"},
]

cpp_stage_order = {"基础语法": 1, "面向对象": 2, "STL与模板": 3, "现代C++": 4, "实战项目": 5}
ros_stage_order = {"基础与架构": 1, "核心通信": 2, "导航与感知": 3, "机械臂与操作": 4, "仿真与进阶": 5}
priority_order = {"P0-核心": 1, "P1-重要": 2, "P2-了解": 3}

def sort_and_number(data, stage_order):
    sorted_data = sorted(data, key=lambda x: (stage_order[x["阶段"]], priority_order[x["优先级"]]))
    for i, item in enumerate(sorted_data, 1):
        item["序号"] = i
        item["新标题"] = f"{i:02d}. {item['知识点']}"
    return sorted_data

cpp_sorted = sort_and_number(cpp_data, cpp_stage_order)
ros_sorted = sort_and_number(ros_data, ros_stage_order)

print("=" * 60)
print("C++ 学习知识库 - 排序后编号")
print("=" * 60)
for item in cpp_sorted:
    print(f"{item['新标题']} | {item['阶段']} | {item['优先级']}")

print()
print("=" * 60)
print("ROS 学习知识库 - 排序后编号")
print("=" * 60)
for item in ros_sorted:
    print(f"{item['新标题']} | {item['阶段']} | {item['优先级']}")

# Also output as JSON for programmatic use
import json
print("\n\n--- CPP JSON ---")
print(json.dumps([{"page_id": item["url"].split("/p/")[1], "new_title": item["新标题"], "old_title": item["知识点"]} for item in cpp_sorted], ensure_ascii=False))
print("\n--- ROS JSON ---")
print(json.dumps([{"page_id": item["url"].split("/p/")[1], "new_title": item["新标题"], "old_title": item["知识点"]} for item in ros_sorted], ensure_ascii=False))
