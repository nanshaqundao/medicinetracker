"""
Gradio UI组件模块
构建Web界面
"""

import gradio as gr
from .service import EntryService
from .voice import VOICE_RECOGNITION_JS


class GradioUI:
    """Gradio用户界面类"""

    def __init__(self, service: EntryService):
        self.service = service
        self.app = None

    def build(self) -> gr.Blocks:
        """构建Gradio界面"""

        with gr.Blocks(
            title="药品信息收集器 V3",
            theme=gr.themes.Soft(),
            head=VOICE_RECOGNITION_JS,
            css=self._get_custom_css()
        ) as app:

            # 标题和统计
            gr.Markdown("# 🎤 药品信息收集器 V3")
            gr.Markdown("*基于Gradio的语音药品信息收集工具*")
            count_display = gr.Markdown("📊 已收集: **加载中...** 条")

            gr.Markdown("---")

            # 语音输入区域
            gr.Markdown("## ✍️ 语音输入")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("**单次模式** - 说一次,手动添加")
                    voice_btn = gr.Button(
                        "🎤 单次语音输入",
                        variant="primary",
                        size="lg",
                        elem_classes=["voice-btn"]
                    )

                with gr.Column(scale=1):
                    gr.Markdown("**连续模式** - 自动添加,持续录入 (推荐!)")
                    continuous_btn = gr.Button(
                        "🔴 连续语音输入 (点击开始/停止)",
                        variant="primary",
                        size="lg",
                        elem_classes=["continuous-btn"]
                    )

            continuous_status = gr.Markdown("状态: 未启动")

            text_input = gr.Textbox(
                label="📝 识别结果 / 手动输入",
                placeholder="点击上方按钮进行语音输入，或在这里手动输入...",
                lines=2
            )

            with gr.Row():
                add_btn = gr.Button("➕ 添加到列表", variant="primary", size="lg")

            status = gr.Textbox(label="状态", interactive=False, show_label=False)

            gr.Markdown("---")

            # 数据表格区域
            gr.Markdown("## 📊 收集列表 - 可直接编辑")
            gr.Markdown("""
            💡 **提示**:
            - **编辑**: 双击单元格直接修改内容
            - **删除**: 选中行，点击删除按钮
            - **保存**: 修改后点击"💾 保存表格修改"按钮
            """)

            dataframe = gr.Dataframe(
                value=[],  # 初始化为空，由 app.load() 统一加载数据
                headers=["#", "药品信息", "录入时间", "ID"],
                datatype=["number", "str", "str", "number"],
                col_count=(4, "fixed"),
                row_count=(0, "dynamic"),
                interactive=True,  # 可编辑
                wrap=True,
                column_widths=["8%", "52%", "25%", "15%"]
            )

            table_status = gr.Textbox(label="操作状态", interactive=False, show_label=False)

            with gr.Row():
                save_table_btn = gr.Button("💾 保存表格修改", variant="primary", size="lg")
                refresh_btn = gr.Button("🔄 刷新列表", variant="secondary")
                export_btn = gr.Button("📥 导出文本", variant="secondary")
                clear_btn = gr.Button("🗑️ 清空全部", variant="stop")

            file_output = gr.File(label="下载文件")

            gr.Markdown("---")

            # 使用说明
            gr.Markdown("""
            ### 💡 使用说明

            #### 🎤 语音输入
            - **单次模式**: 点击按钮 → 说话 → 点击"添加到列表"
            - **连续模式**: 点击按钮 → 持续说话 → 自动添加 (推荐!)

            #### ✏️ 编辑数据
            - **直接编辑**: 双击表格单元格修改内容
            - **删除行**: 选中行，点击键盘Delete键或清空行
            - **保存**: 编辑完成后点击"💾 保存表格修改"

            #### 📥 数据管理
            - **刷新**: 点击"🔄 刷新列表"查看最新数据
            - **导出**: 导出为txt文本文件
            - **清空**: 清空所有数据（谨慎操作）

            **浏览器要求**: Chrome / Edge (需麦克风权限)
            """)

            # 事件绑定
            self._bind_events(
                voice_btn, continuous_btn, add_btn, refresh_btn,
                export_btn, clear_btn, text_input, continuous_status,
                status, dataframe, count_display, file_output,
                save_table_btn, table_status
            )

            # 页面加载时自动刷新数据（解决浏览器刷新后数据不同步的问题）
            app.load(
                fn=self.service.refresh,
                outputs=[dataframe, count_display]
            )

            self.app = app
            return app

    def _bind_events(
        self, voice_btn, continuous_btn, add_btn, refresh_btn,
        export_btn, clear_btn, text_input, continuous_status,
        status, dataframe, count_display, file_output,
        save_table_btn, table_status
    ):
        """绑定事件处理"""

        # 单次语音按钮
        voice_btn.click(
            fn=None,
            inputs=[],
            outputs=[text_input],
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
        continuous_btn.click(
            fn=None,
            inputs=[],
            outputs=[continuous_status],
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
        add_btn.click(
            fn=self.service.add_entry,
            inputs=[text_input],
            outputs=[status, dataframe, count_display, text_input]
        )

        # 保存表格修改按钮
        save_table_btn.click(
            fn=self.service.save_dataframe,
            inputs=[dataframe],
            outputs=[table_status, dataframe, count_display]
        )

        # 刷新按钮
        refresh_btn.click(
            fn=self.service.refresh,
            outputs=[dataframe, count_display]
        )

        # 导出按钮
        export_btn.click(
            fn=self.service.export_to_text,
            outputs=[file_output]
        )

        # 清空按钮
        clear_btn.click(
            fn=self.service.clear_all,
            outputs=[table_status, dataframe, count_display]
        )

        # 支持回车提交
        text_input.submit(
            fn=self.service.add_entry,
            inputs=[text_input],
            outputs=[status, dataframe, count_display, text_input]
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
        """

    def launch(self, **kwargs):
        """启动应用"""
        if self.app is None:
            self.build()

        return self.app.launch(**kwargs)
