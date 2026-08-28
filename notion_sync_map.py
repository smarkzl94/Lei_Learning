# -*- coding: utf-8 -*-
"""Notion page ID mapping for C++ and ROS learning notes"""

# Format: local_filename_without_ext -> notion_page_id
# Extracted from create-pages results

CPP_PAGE_IDS = {
    "变量与数据类型": "3c9503fb-d69f-819d-ac00-ce24cf718026",
    "运算符与表达式": "3c9503fb-d69f-81e5-a661-e80e08441080",
    "控制流程": "3c9503fb-d69f-8188-a6d7-e8281323c1a3",
    "函数": "3c9503fb-d69f-8104-a125-c1582bd24931",
    "指针与引用": "3c9503fb-d69f-8114-a49f-d74f5daa10e5",
    "数组与字符串": "3c9503fb-d69f-81e0-98a9-fbc92f0d40b9",
    "类与对象": "3c9503fb-d69f-8135-9ea1-f98c2eeede00",
    "构造函数与析构函数": "3c9503fb-d69f-8105-9a37-d02a9947636b",
    "继承": "3c9503fb-d69f-81c7-887f-c338b27691ec",
    "多态与虚函数": "3c9503fb-d69f-812e-b3cc-e3f686263229",
    "运算符重载": "3c9503fb-d69f-8132-a0ff-c8ab1e7a1563",
    "智能指针": "3c9503fb-d69f-817f-8b2f-d7e0f33db2b8",
    "Lambda表达式": "3c9503fb-d69f-81d4-9911-d4244d0d71d6",
    "auto与类型推导": "3c9503fb-d69f-8199-8b0a-cce8551e08aa",
    "移动语义与完美转发": "3c9503fb-d69f-815b-a525-f7f1629a439c",
    "范围for与初始化列表": "3c9503fb-d69f-810c-8650-c05d3d7819a5",
    "序列容器": "3c9503fb-d69f-81c5-89c6-cf9acc6e5772",
    "关联容器": "3c9503fb-d69f-8107-a9de-d2aa705aa885",
    "算法": "3c9503fb-d69f-8111-85c2-d380da51832f",
    "迭代器与适配器": "3c9503fb-d69f-81d7-b2fd-cc9f23d52636",
    "多线程编程": "3c9503fb-d69f-81f7-99fc-c5e87e4f97ae",
    "内存管理": "3c9503fb-d69f-81c8-bbbe-f9e68cfccf42",
    "模板与泛型编程": "3c9503fb-d69f-8154-ada1-c58df5286f72",
    "学生成绩管理系统": "3c9503fb-d69f-8159-a4f6-f52965bde7a6",
    "简易计算器": "3c9503fb-d69f-81ee-bb13-e022359835e9",
    "多线程生产者消费者": "3c9503fb-d69f-819c-b8d6-f76322ccc188",
}

ROS_PAGE_IDS = {
    "什么是ROS": "3c9503fb-d69f-8186-a635-c7dde92d1b39",
    "ROS版本选择": "3c9503fb-d69f-81ae-9364-ea6522297300",
    "Ubuntu与ROS安装": "3c9503fb-d69f-816a-a809-ec17be6bad55",
    "第一个ROS程序小海龟": "3c9503fb-d69f-811f-9b9d-e2c99f2e908c",
    "工作空间结构": "3c9503fb-d69f-81c8-8fda-c5110ae24aee",
    "Catkin编译系统": "3c9503fb-d69f-81ee-957e-dd3b2a36a7f2",
    "创建功能包": "3c9503fb-d69f-818c-9865-f3a1b1c678a2",
    "节点管理与launch文件": "3c9503fb-d69f-8103-a1d1-cc27587f8404",
    "话题Topic": "3c9503fb-d69f-819c-910f-c7751640383e",
    "服务Service": "3c9503fb-d69f-8122-8d52-e30d9c570cdd",
    "动作Action": "3c9503fb-d69f-8146-a2d1-c1f93d520fd5",
    "参数服务器": "3c9503fb-d69f-8170-8409-d063d96f2536",
    "自定义消息类型": "3c9503fb-d69f-8108-84a2-da8ab43450cf",
    "RViz可视化工具": "3c9503fb-d69f-816d-8983-d9fd0fc59540",
    "Gazebo仿真环境": "3c9503fb-d69f-81b3-aa8c-dbce73263e14",
    "rqt与rosbag": "3c9503fb-d69f-81e8-891f-e2f9c689e029",
    "TF坐标变换": "3c9503fb-d69f-81ae-84ce-d943cdee5177",
    "URDF基础": "3c9503fb-d69f-818f-8ae3-ee4706cde9a4",
    "Xacro宏语言": "3c9503fb-d69f-8160-a9aa-ce474c2dfb3a",
    "Gazebo插件配置": "3c9503fb-d69f-81dd-953e-c0700be59201",
    "传感器与消息类型": "3c9503fb-d69f-81b5-b006-ecf38fd6ac06",
    "SLAM建图": "3c9503fb-d69f-815d-a047-f554cbeb6bb9",
    "导航栈Navigation": "3c9503fb-d69f-8197-b8f6-c81644b6ceab",
    "感知处理基础": "3c9503fb-d69f-8165-88cf-d24af91acd89",
    "项目需求分析": "3c9503fb-d69f-81ed-8b37-d76ee3289294",
    "移动机器人仿真导航": "3c9503fb-d69f-81b7-97f8-f7f6c6045c6f",
    "机械臂运动规划": "3c9503fb-d69f-8111-a0c2-e5b677fb4f4f",
}

ALL_PAGE_IDS = {**CPP_PAGE_IDS, **ROS_PAGE_IDS}

# Filename to key mapping (extract knowledge point name from filename)
import os, glob, json

def get_key_from_path(path):
    """从文件路径提取知识点名称"""
    base = os.path.splitext(os.path.basename(path))[0]
    # 去掉数字前缀，如 "01_变量与数据类型" -> "变量与数据类型"
    if '_' in base:
        parts = base.split('_', 1)
        if parts[0].isdigit():
            return parts[1]
    return base

if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    files = []
    for pattern in [os.path.join(base, 'C++学习', '**', '*.md'), os.path.join(base, 'ROS学习', '**', '*.md')]:
        for p in sorted(glob.glob(pattern, recursive=True)):
            if os.path.basename(p) == 'README.md':
                continue
            key = get_key_from_path(p)
            page_id = ALL_PAGE_IDS.get(key)
            if page_id:
                files.append({'path': p, 'key': key, 'page_id': page_id})
            else:
                print(f"WARNING: No Notion page found for {key}")
    
    print(f"Matched {len(files)} files")
    for f in files:
        print(f"  {f['key']} -> {f['page_id']}")
