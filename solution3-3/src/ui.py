"""
Gradio UI组件模块 - 多Tab版本
包含：语音收集、智能结构化、数据分析三个Tab
"""

import gradio as gr
from .service import EntryService
from .text_parser import MedicineParserService
from .voice import VOICE_RECOGNITION_JS


class GradioUI:
    """Gradio用户界面类（多Tab版本）"""

    def __init__(self, entry_service: EntryService, parser_service: MedicineParserService = None):
        self.entry_service = entry_service
        self.parser_service = parser_service or MedicineParserService()
        self.app = None

    def build(self) -> gr.Blocks:
        """构建Gradio界面（多Tab布局）"""

        with gr.Blocks(
            title="药品信息管理系统 V3.1",
            theme=gr.themes.Soft(),
            head=VOICE_RECOGNITION_JS,
            css=self._get_custom_css()
        ) as app:

            # 全局标题
            gr.Markdown("# 🎤 药品信息管理系统 V3.1")
            gr.Markdown("*集成语音收集、智能结构化、数据分析功能*")
            # 用户身份
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("### 👤 当前用户")
                with gr.Column(scale=1):
                    self.user_input = gr.Textbox(
                        label="用户ID (自动识别)",
                        value="default",
                        placeholder="输入用户名...",
                        scale=1,
                        visible=True,  # 必须为True，否则JS无法找到DOM元素
                        elem_classes=["hidden-user-input"]  # 通过CSS隐藏
                    )
                    self.user_status = gr.Markdown("✅ 当前用户: default")

            gr.Markdown("---")

            # 创建三个Tab
            with gr.Tabs() as tabs:
                with gr.Tab("📝 语音采集") as tab1:
                    self._build_tab1_voice_collection()
                
                with gr.Tab("🧠 智能结构化") as tab2:
                    self.tab2 = tab2
                    self._build_tab2_structuring()
                    
                with gr.Tab("📊 数据分析") as tab3:
                    self.tab3 = tab3
                    self._build_tab3_analysis()

            self.app = app

            # 绑定所有事件（必须在app赋值后）
            self._bind_user_events()
            self._bind_tab1_events()
            self._bind_tab2_events()
            self._bind_tab3_events()

            return app

    def _build_tab1_voice_collection(self):
        """构建Tab 1: 语音收集（保留原有功能）"""

        gr.Markdown("## ✍️ 语音输入")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("**单次模式** - 说一次,手动添加")
                self.voice_btn = gr.Button(
                    "🎤 单次语音输入",
                    variant="primary",
                    size="lg",
                    elem_classes=["voice-btn"]
                )

            with gr.Column(scale=1):
                gr.Markdown("**连续模式** - 自动添加,持续录入 (推荐!)")
                self.continuous_btn = gr.Button(
                    "🔴 连续语音输入 (点击开始/停止)",
                    variant="primary",
                    size="lg",
                    elem_classes=["continuous-btn"]
                )

        self.continuous_status = gr.Markdown("状态: 未启动")

        self.text_input = gr.Textbox(
            label="📝 识别结果 / 手动输入",
            placeholder="点击上方按钮进行语音输入，或在这里手动输入...",
            lines=2
        )

        with gr.Row():
            self.add_btn = gr.Button("➕ 添加到列表", variant="primary", size="lg")

        self.status = gr.Textbox(label="状态", interactive=False, show_label=False)

        gr.Markdown("---")
        gr.Markdown("## 📊 收集列表 - 可直接编辑")

        self.count_display = gr.Markdown("📊 已收集: **加载中...** 条")

        self.dataframe = gr.Dataframe(
            value=[],
            headers=["#", "药品信息", "录入时间", "ID"],
            datatype=["number", "str", "str", "number"],
            col_count=(4, "fixed"),
            row_count=(0, "dynamic"),
            interactive=True,
            wrap=True,
            column_widths=["8%", "52%", "25%", "15%"]
        )

        self.table_status = gr.Textbox(label="操作状态", interactive=False, show_label=False)

        with gr.Row():
            self.save_table_btn = gr.Button("💾 保存表格修改", variant="primary", size="lg")
            self.refresh_btn = gr.Button("🔄 刷新列表", variant="secondary")
            self.export_btn = gr.Button("📥 导出文本", variant="secondary")
            self.clear_btn = gr.Button("🗑️ 清空全部", variant="stop")

        self.file_output = gr.File(label="下载文件")

    def _build_tab2_structuring(self):
        """构建Tab 2: 智能结构化"""

        gr.Markdown("## 🧠 AI智能结构化")
        gr.Markdown("使用大语言模型将原始文本转换为结构化数据")

        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 📝 原始数据")
                self.tab2_source_df = gr.Dataframe(
                    value=[],
                    headers=["#", "药品信息", "录入时间"],
                    label="待处理的原始文本",
                    interactive=False,
                    wrap=True
                )

            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ 操作")

                self.tab2_status = gr.Textbox(
                    label="处理状态",
                    value="就绪",
                    interactive=False,
                    lines=5
                )

                gr.Markdown("### 📥 数据加载")
                with gr.Row():
                    self.tab2_load_voice_btn = gr.Button("🎤 加载语音数据 (覆盖)", variant="secondary")
                    self.tab2_clear_pending_btn = gr.Button("🗑️ 清空待处理数据", variant="stop")
                
                with gr.Row():
                    self.tab2_import_file = gr.File(
                        label="导入文件 (CSV/JSON/TXT)",
                        file_types=[".csv", ".json", ".txt"],
                        file_count="single"
                    )
                self.tab2_attach_file_btn = gr.Button("📎 附加文件数据 (Append)", variant="secondary")

                gr.Markdown("### 🚀 智能解析")
                self.tab2_append_checkbox = gr.Checkbox(
                    label="追加到现有结果 (默认覆盖)",
                    value=False,
                    info="选中后，解析结果将追加到下方表格，而不是覆盖现有内容"
                )
                self.tab2_parse_btn = gr.Button("🚀 开始智能解析", variant="primary", size="lg")

        gr.Markdown("---")
        gr.Markdown("### 📋 结构化结果")

        self.tab2_result_df = gr.Dataframe(
            value=[],
            headers=["#", "药名", "商品名", "学术名", "数量", "单位", "规格", "包装", "有效期", "原文", "时间"],
            label="AI解析结果（可编辑）",
            interactive=True,
            wrap=True,
            column_widths=["5%", "10%", "8%", "10%", "5%", "5%", "8%", "8%", "10%", "20%", "11%"]
        )

        with gr.Row():
            self.tab2_save_btn = gr.Button("💾 保存结构化数据", variant="primary", size="lg")
            self.tab2_export_btn = gr.Button("📥 导出CSV", variant="secondary")

        self.tab2_result_status = gr.Textbox(label="结果", interactive=False, show_label=False)
        self.tab2_file_output = gr.File(label="下载文件")

    def _build_tab3_analysis(self):
        """构建Tab 3: 数据分析"""

        gr.Markdown("## 📊 数据分析与查询")

        # 筛选控制
        with gr.Row():
            self.tab3_drug_filter = gr.Textbox(
                label="🔍 按药名筛选",
                placeholder="输入药名关键词...",
                scale=2
            )
            self.tab3_filter_btn = gr.Button("筛选", variant="secondary", scale=1)
            self.tab3_reset_btn = gr.Button("重置", variant="secondary", scale=1)

        with gr.Row():
            self.tab3_sort_by = gr.Dropdown(
                choices=["药名", "有效期"],
                label="📈 排序依据",
                value="药名",
                scale=1
            )
            self.tab3_sort_order = gr.Radio(
                choices=["升序", "降序"],
                label="排序方式",
                value="升序",
                scale=1
            )
            self.tab3_sort_btn = gr.Button("排序", variant="secondary", scale=1)

        gr.Markdown("---")

        # 统计信息
        self.tab3_stats = gr.Markdown("### 📊 统计信息\n加载中...")

        # 数据展示
        self.tab3_data_df = gr.Dataframe(
            value=[],
            headers=["#", "药名", "商品名", "学术名", "数量", "单位", "规格", "包装", "有效期", "原文", "时间"],
            label="结构化数据",
            interactive=False,
            wrap=True,
            column_widths=["5%", "10%", "8%", "10%", "5%", "5%", "8%", "8%", "10%", "20%", "11%"]
        )

        with gr.Row():
            self.tab3_refresh_btn = gr.Button("🔄 刷新数据", variant="primary", size="lg")
            self.tab3_export_btn = gr.Button("📥 导出当前视图", variant="secondary")

    def _bind_user_events_callback(self, user_id):
        """切换用户并刷新所有数据的回调函数"""
        # 刷新Tab1数据
        df1, count1 = self.entry_service.refresh(user_id)
        
        # 刷新Tab2数据 (清空显示)
        df2_source = []
        df2_result = self.parser_service.get_structured_dataframe(user_id)
        
        # 刷新Tab3数据
        self.parser_service.load_structured_data(user_id)
        df3 = self.parser_service.get_structured_dataframe(user_id)
        stats = self.parser_service.get_statistics(user_id)
        stats_text = f"""### 📊 统计信息

- **总计**: {stats['total']} 条
- **有商品名**: {stats['with_brand_name']} 条
- **有学术名**: {stats['with_generic_name']} 条
- **有规格**: {stats['with_specification']} 条
- **有效期**: {stats['with_expiry_date']} 条
"""
        
        return (
            f"✅ 当前用户: {user_id}", 
            df1, count1, 
            df2_source, "就绪", df2_result,
            df3, stats_text
        )

    def _bind_user_events(self):
        """绑定用户切换事件"""
        self.user_input.submit(
            fn=self._bind_user_events_callback,
            inputs=[self.user_input],
            outputs=[
                self.user_status,
                self.dataframe, self.count_display,
                self.tab2_source_df, self.tab2_status, self.tab2_result_df,
                self.tab3_data_df, self.tab3_stats
            ]
        )

    def _bind_tab1_events(self):
        """绑定Tab1事件"""

        # 语音按钮
        self.voice_btn.click(
            fn=None,
            outputs=[self.text_input],
            js="""
            async () => {
                try {
                    const text = await window.startVoiceRecognition();
                    return text;
                } catch (e) {
                    console.error('Recognition failed:', e);
                    return '';
                }
            }
            """
        )

        # 连续语音按钮
        self.continuous_btn.click(
            fn=None,
            outputs=[self.continuous_status],
            js="""
            () => {
                const result = window.startContinuousVoice();
                if (result === 'started') {
                    return '✅ **连续模式已启动** - 说话会自动添加到列表';
                } else if (result === 'stopped') {
                    return '⏹️ **连续模式已停止**';
                } else {
                    return '❌ **启动失败**';
                }
            }
            """
        )

        # 添加按钮
        self.add_btn.click(
            fn=self.entry_service.add_entry,
            inputs=[self.text_input, self.user_input],
            outputs=[self.status, self.dataframe, self.count_display, self.text_input]
        )

        # 保存表格
        self.save_table_btn.click(
            fn=self.entry_service.save_dataframe,
            inputs=[self.dataframe, self.user_input],
            outputs=[self.table_status, self.dataframe, self.count_display]
        )

        # 刷新
        self.refresh_btn.click(
            fn=self.entry_service.refresh,
            inputs=[self.user_input],
            outputs=[self.dataframe, self.count_display]
        )

        # 导出
        self.export_btn.click(
            fn=self.entry_service.export_to_text,
            inputs=[self.user_input],
            outputs=[self.file_output]
        )

        # 清空
        self.clear_btn.click(
            fn=self.entry_service.clear_all,
            inputs=[self.user_input],
            outputs=[self.table_status, self.dataframe, self.count_display]
        )

        # 回车提交
        self.text_input.submit(
            fn=self.entry_service.add_entry,
            inputs=[self.text_input, self.user_input],
            outputs=[self.status, self.dataframe, self.count_display, self.text_input]
        )

        # 页面加载时刷新 - 实际上由_bind_user_events_callback处理
        # self.app.load(...) 

    def _bind_tab2_events(self):
        """绑定Tab2事件"""

        def load_voice_data(user_id, current_data):
            """加载语音数据并追加"""
            print(f"DEBUG: load_voice_data called with user_id='{user_id}'")
            entry_list = self.entry_service._get_entry_list(user_id)
            entries = entry_list.get_all()
            print(f"DEBUG: Found {len(entries)} entries for user '{user_id}'")
            if not entries:
                return current_data, f"⚠️ 没有语音数据 (User: {user_id})"

            # 处理current_data，确保它是列表
            import pandas as pd
            if isinstance(current_data, pd.DataFrame):
                current_data_list = current_data.values.tolist()
            elif isinstance(current_data, list):
                current_data_list = current_data
            else:
                current_data_list = []

            # 转换为dataframe格式 [序号, 文本, 时间]
            # start_index = len(current_data_list) # Overwrite mode starts from 0
            new_data = [[i + 1, e.text, e.timestamp] for i, e in enumerate(entries)]
            
            # 覆盖现有数据
            updated_data = new_data
            return updated_data, f"✅ 已加载 {len(entries)} 条语音数据 (User: {user_id})"

        def attach_file_data(file_obj, current_data):
            """附加文件数据"""
            if not file_obj:
                return current_data, "⚠️ 请先上传文件"
                
            entries = self.entry_service.parse_file_to_entries(file_obj.name)
            if not entries:
                return current_data, "⚠️ 文件解析失败或为空"
                
            # 处理current_data，确保它是列表
            import pandas as pd
            if isinstance(current_data, pd.DataFrame):
                current_data_list = current_data.values.tolist()
            elif isinstance(current_data, list):
                current_data_list = current_data
            else:
                current_data_list = []

            # 转换为dataframe格式
            start_index = len(current_data_list)
            new_data = [[start_index + i + 1, e['text'], e['timestamp']] for i, e in enumerate(entries)]
            
            updated_data = current_data_list + new_data
            return updated_data, f"✅ 已追加 {len(entries)} 条文件数据"

        def clear_pending_data():
            """清空待处理数据"""
            return [], "✅ 待处理数据已清空"

        def parse_all(user_id, source_data, append_mode):
            """解析所有原始数据"""
            # 处理source_data，确保它是列表
            import pandas as pd
            if isinstance(source_data, pd.DataFrame):
                source_data_list = source_data.values.tolist()
            elif isinstance(source_data, list):
                source_data_list = source_data
            else:
                source_data_list = []

            if not source_data_list or len(source_data_list) == 0:
                return [], "⚠️ 没有数据需要解析", self.parser_service.get_structured_dataframe(user_id)

            # 从source_data重建Entry对象列表
            # source_data format: [序号, 文本, 时间]
            from .models import Entry
            entries = []
            for row in source_data_list:
                if len(row) >= 2:
                    entries.append(Entry.create(row[1])) # 重建Entry，ID会重新生成，但这不影响解析

            success, failed, failed_texts = self.parser_service.parse_and_save(entries, user_id, append=append_mode)

            status_msg = f"✅ 解析完成！\n成功: {success} 条\n失败: {failed} 条"
            if failed_texts:
                status_msg += f"\n\n失败的文本:\n" + "\n".join(f"- {t}" for t in failed_texts[:5])

            return [], status_msg, self.parser_service.get_structured_dataframe(user_id)

        def save_structured(user_id, df_data):
            """保存结构化数据"""
            # 处理df_data，确保它是列表
            import pandas as pd
            if isinstance(df_data, pd.DataFrame):
                df_data_list = df_data.values.tolist()
            elif isinstance(df_data, list):
                df_data_list = df_data
            else:
                df_data_list = []

            # 先从表格更新数据
            if self.parser_service.update_from_dataframe(user_id, df_data_list):
                # 然后保存到文件
                if self.parser_service.save_structured_data(user_id):
                    structured_list = self.parser_service._get_structured_list(user_id)
                    count = structured_list.count()
                    return f"✅ 已保存 {count} 条结构化数据"
            
            return "❌ 保存失败"

        def on_tab2_select(user_id):
            """Tab2选中时自动加载数据"""
            print(f"DEBUG: on_tab2_select called with user_id='{user_id}'")
            df = self.parser_service.get_structured_dataframe(user_id)
            print(f"DEBUG: on_tab2_select returning {len(df)} rows")
            return df

        # 绑定事件
        self.tab2.select(
            fn=on_tab2_select,
            inputs=[self.user_input],
            outputs=[self.tab2_result_df]
        )

        self.tab2_load_voice_btn.click(
            fn=load_voice_data,
            inputs=[self.user_input, self.tab2_source_df],
            outputs=[self.tab2_source_df, self.tab2_status]
        )

        self.tab2_attach_file_btn.click(
            fn=attach_file_data,
            inputs=[self.tab2_import_file, self.tab2_source_df],
            outputs=[self.tab2_source_df, self.tab2_status]
        )

        self.tab2_clear_pending_btn.click(
            fn=clear_pending_data,
            inputs=[],
            outputs=[self.tab2_source_df, self.tab2_status]
        )

        self.tab2_parse_btn.click(
            fn=parse_all,
            inputs=[self.user_input, self.tab2_source_df, self.tab2_append_checkbox],
            outputs=[self.tab2_source_df, self.tab2_status, self.tab2_result_df]
        )

        self.tab2_save_btn.click(
            fn=save_structured,
            inputs=[self.user_input, self.tab2_result_df],
            outputs=[self.tab2_result_status]
        )

        self.tab2_export_btn.click(
            fn=self.parser_service.export_to_csv,
            inputs=[self.user_input],
            outputs=[self.tab2_file_output]
        )

    def _bind_tab3_events(self):
        """绑定Tab3事件"""

        def refresh_data(user_id):
            """刷新数据和统计"""
            self.parser_service.load_structured_data(user_id)
            df = self.parser_service.get_structured_dataframe(user_id)
            stats = self.parser_service.get_statistics(user_id)

            stats_text = f"""### 📊 统计信息

- **总计**: {stats['total']} 条
- **有商品名**: {stats['with_brand_name']} 条
- **有学术名**: {stats['with_generic_name']} 条
- **有规格**: {stats['with_specification']} 条
- **有效期**: {stats['with_expiry_date']} 条
"""
            return df, stats_text

        def filter_data(drug_name, user_id):
            """筛选数据"""
            if not drug_name or not drug_name.strip():
                return self.parser_service.get_structured_dataframe(user_id)
            return self.parser_service.filter_by_drug_name(drug_name.strip(), user_id)

        def sort_data(sort_by, sort_order, user_id):
            """排序数据"""
            reverse = (sort_order == "降序")

            if sort_by == "药名":
                return self.parser_service.sort_by_drug_name(user_id, reverse=reverse)
            elif sort_by == "有效期":
                return self.parser_service.sort_by_expiry(user_id, reverse=reverse)
            else:
                return self.parser_service.get_structured_dataframe(user_id)

        # 绑定事件
        self.tab3_refresh_btn.click(
            fn=refresh_data,
            inputs=[self.user_input],
            outputs=[self.tab3_data_df, self.tab3_stats]
        )

        self.tab3_filter_btn.click(
            fn=filter_data,
            inputs=[self.tab3_drug_filter, self.user_input],
            outputs=[self.tab3_data_df]
        )

        self.tab3_reset_btn.click(
            fn=lambda user_id: self.parser_service.get_structured_dataframe(user_id),
            inputs=[self.user_input],
            outputs=[self.tab3_data_df]
        )

        self.tab3_sort_btn.click(
            fn=sort_data,
            inputs=[self.tab3_sort_by, self.tab3_sort_order, self.user_input],
            outputs=[self.tab3_data_df]
        )

        # 页面加载时：
        # 1. 执行JS获取/生成User ID
        # 2. 将ID填入user_input
        # 3. 触发switch_user加载该用户数据
        
        get_user_id_js = """
        () => {
            let userId = localStorage.getItem('medicine_tracker_user_id');
            if (!userId) {
                userId = 'user_' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('medicine_tracker_user_id', userId);
            }
            console.log('Loaded User ID:', userId);
            return userId;
        }
        """

        self.app.load(
            fn=None,
            inputs=None,
            outputs=[self.user_input],
            js=get_user_id_js
        ).then(
            fn=self._bind_user_events_callback, # 使用专门的回调函数
            inputs=[self.user_input],
            outputs=[
                self.user_status,
                self.dataframe, self.count_display,
                self.tab2_source_df, self.tab2_status, self.tab2_result_df,
                self.tab3_data_df, self.tab3_stats
            ]
        )

    def _get_custom_css(self) -> str:
        """获取自定义CSS样式"""
        return """
        .voice-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            font-size: 18px !important;
            padding: 20px !important;
            font-weight: bold !important;
        }
        .continuous-btn {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            color: white !important;
            border: none !important;
            font-size: 18px !important;
            padding: 20px !important;
            font-weight: bold !important;
        }
        .hidden-user-input {
            display: none !important;
        }
        """

    def launch(self, **kwargs):
        """启动应用"""
        if self.app is None:
            self.build()

        return self.app.launch(**kwargs)
