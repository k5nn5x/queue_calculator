import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys


class QueueCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("排队剩余时间计算器")
        self.root.geometry("520x620")
        self.root.resizable(False, False)

        # 存储进度记录: [(time_obj, number), ...]
        self.records = []

        self.setup_ui()

    def setup_ui(self):
        # ========== 取号信息 ==========
        frame_info = ttk.LabelFrame(self.root, text="取号信息", padding=10)
        frame_info.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(frame_info, text="取号时间 (HH:MM):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_ticket_time = ttk.Entry(frame_info, width=15)
        self.entry_ticket_time.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.entry_ticket_time.insert(0, "08:00")

        ttk.Label(frame_info, text="取号号码:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_ticket_number = ttk.Entry(frame_info, width=15)
        self.entry_ticket_number.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.entry_ticket_number.insert(0, "A100")

        # ========== 当前进度输入 ==========
        frame_progress = ttk.LabelFrame(self.root, text="输入当前进度", padding=10)
        frame_progress.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_progress, text="当前时间 (HH:MM):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_current_time = ttk.Entry(frame_progress, width=15)
        self.entry_current_time.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame_progress, text="当前叫到号码:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_current_number = ttk.Entry(frame_progress, width=15)
        self.entry_current_number.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        btn_frame = ttk.Frame(frame_progress)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="添 加 记 录", command=self.add_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="清 空 记 录", command=self.clear_records).pack(side="left", padx=5)

        # ========== 进度记录列表 ==========
        frame_list = ttk.LabelFrame(self.root, text="进度记录", padding=10)
        frame_list.pack(fill="both", expand=True, padx=10, pady=5)

        self.listbox = tk.Listbox(frame_list, height=6, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ========== 计算结果 ==========
        frame_result = ttk.LabelFrame(self.root, text="计算结果", padding=10)
        frame_result.pack(fill="x", padx=10, pady=5)

        self.result_text = tk.Text(frame_result, height=8, font=("Microsoft YaHei", 10), state="disabled", wrap="word")
        self.result_text.pack(fill="x")

        # ========== 底部按钮 ==========
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Button(bottom_frame, text="计算预计到达时间", command=self.calculate).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="用当前时间填充", command=self.fill_current_time).pack(side="left", padx=5)

    def fill_current_time(self):
        """用当前系统时间填充当前时间输入框"""
        now = datetime.now().strftime("%H:%M")
        self.entry_current_time.delete(0, tk.END)
        self.entry_current_time.insert(0, now)

    def parse_time(self, time_str: str) -> datetime | None:
        """解析时间字符串为 datetime 对象（以今天为基准）"""
        time_str = time_str.strip()
        for fmt in ["%H:%M", "%H:%M:%S", "%H.%M"]:
            try:
                parsed = datetime.strptime(time_str, fmt)
                return parsed.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
            except ValueError:
                continue
        return None

    def parse_number(self, number_str: str) -> int | None:
        """解析号码字符串，提取数字部分用于比较"""
        number_str = number_str.strip()
        if not number_str:
            return None
        # 尝试提取纯数字
        import re
        nums = re.findall(r'\d+', number_str)
        if nums:
            return int(nums[-1])  # 取最后一个数字组
        return None

    def add_record(self):
        current_time_str = self.entry_current_time.get().strip()
        current_number_str = self.entry_current_number.get().strip()

        if not current_time_str or not current_number_str:
            messagebox.showwarning("提示", "请填写当前时间和当前叫到号码")
            return

        time_obj = self.parse_time(current_time_str)
        if time_obj is None:
            messagebox.showwarning("提示", "时间格式错误，请使用 HH:MM 格式（如 09:30）")
            return

        number_val = self.parse_number(current_number_str)
        if number_val is None:
            messagebox.showwarning("提示", "号码格式错误，请包含数字（如 A101 或 101）")
            return

        self.records.append((time_obj, number_val, current_number_str))
        display_str = f"{current_time_str}  →  {current_number_str} (序号 {number_val})"
        self.listbox.insert(tk.END, display_str)

        # 清空输入
        self.entry_current_time.delete(0, tk.END)
        self.entry_current_number.delete(0, tk.END)

        # 自动计算（如果有取号信息）
        if self.entry_ticket_time.get().strip() and self.entry_ticket_number.get().strip():
            self.calculate()

    def clear_records(self):
        self.records.clear()
        self.listbox.delete(0, tk.END)
        self.update_result("记录已清空。")

    def get_number_sort_key(self, number_str: str) -> int:
        """获取号码的排序数值"""
        import re
        nums = re.findall(r'\d+', number_str)
        if nums:
            return int(nums[-1])
        return 0

    def calculate(self):
        ticket_time_str = self.entry_ticket_time.get().strip()
        ticket_number_str = self.entry_ticket_number.get().strip()

        if not ticket_time_str or not ticket_number_str:
            messagebox.showwarning("提示", "请先填写取号时间和取号号码")
            return

        ticket_time = self.parse_time(ticket_time_str)
        if ticket_time is None:
            messagebox.showwarning("提示", "取号时间格式错误")
            return

        my_number = self.parse_number(ticket_number_str)
        if my_number is None:
            messagebox.showwarning("提示", "取号号码格式错误")
            return

        if len(self.records) < 1:
            self.update_result(f"你的号码: {ticket_number_str}\n请至少输入一条当前进度记录以估算剩余时间。")
            return

        # 排序记录（按时间）
        sorted_records = sorted(self.records, key=lambda x: x[0])

        # 取最后一条记录
        latest_time, latest_number, latest_number_str = sorted_records[-1]

        # 计算已经过去的分钟数（从取号到现在）
        minutes_since_ticket = (latest_time - ticket_time).total_seconds() / 60.0

        # 计算从取号到现在的叫号数量
        numbers_served = latest_number - self.parse_number(ticket_number_str)

        # 计算速度（个/分钟）
        if minutes_since_ticket > 0 and numbers_served > 0:
            speed = numbers_served / minutes_since_ticket  # 个/分钟
        else:
            # 如果有两个以上的记录，用最近两个计算瞬时速度
            if len(sorted_records) >= 2:
                r1 = sorted_records[-2]
                r2 = sorted_records[-1]
                time_diff = (r2[0] - r1[0]).total_seconds() / 60.0
                num_diff = r2[1] - r1[1]
                if time_diff > 0 and num_diff > 0:
                    speed = num_diff / time_diff
                else:
                    speed = 0
            else:
                speed = 0

        # 剩余号码数
        remaining_numbers = my_number - latest_number

        # 计算额外信息：使用多种速度估算
        remaining_time_min = 0
        if speed > 0 and remaining_numbers > 0:
            remaining_time_min = remaining_numbers / speed
        elif remaining_numbers <= 0:
            remaining_time_min = 0
        else:
            remaining_time_min = -1  # 表示无法计算

        # 预计到达时间
        if remaining_time_min >= 0:
            estimated_arrival = latest_time + timedelta(minutes=remaining_time_min)
            arrival_str = estimated_arrival.strftime("%H:%M")
        else:
            arrival_str = "无法估算"

        # 构建输出信息
        lines = []
        lines.append(f"你的号码: {ticket_number_str} (序号 {my_number})")
        lines.append(f"取号时间: {ticket_time.strftime('%H:%M')}")
        lines.append(f"─" * 35)
        lines.append(f"最近进度: {latest_time.strftime('%H:%M')} → {latest_number_str}")
        lines.append(f"已叫号: {numbers_served} 个 (用时 {minutes_since_ticket:.0f} 分钟)")

        if speed > 0:
            lines.append(f"平均速度: {speed:.2f} 个/分钟")
            lines.append(f"当前剩余: {remaining_numbers} 个")
            if remaining_numbers > 0:
                if remaining_time_min < 60:
                    lines.append(f"预计还需: {remaining_time_min:.0f} 分钟")
                else:
                    h = int(remaining_time_min // 60)
                    m = int(remaining_time_min % 60)
                    lines.append(f"预计还需: {h} 小时 {m} 分钟")
                lines.append(f"预计到达时间: {arrival_str}")

                # 如果有多条记录，提供基于最近一段时间的估算
                if len(sorted_records) >= 2:
                    r1 = sorted_records[-2]
                    r2 = sorted_records[-1]
                    seg_time = (r2[0] - r1[0]).total_seconds() / 60.0
                    seg_num = r2[1] - r1[1]
                    if seg_time > 0 and seg_num > 0:
                        seg_speed = seg_num / seg_time
                        seg_remaining = remaining_numbers / seg_speed
                        seg_arrival = r2[0] + timedelta(minutes=seg_remaining)
                        lines.append(f"─" * 35)
                        lines.append(f"近期速度参考:")
                        lines.append(f"  最近段: {r1[0].strftime('%H:%M')}→{r2[0].strftime('%H:%M')}")
                        lines.append(f"  {seg_num} 个用了 {seg_time:.0f} 分钟 ({seg_speed:.2f} 个/分钟)")
                        if seg_remaining < 60:
                            lines.append(f"  预计还需: {seg_remaining:.0f} 分钟")
                        else:
                            h = int(seg_remaining // 60)
                            m = int(seg_remaining % 60)
                            lines.append(f"  预计还需: {h} 小时 {m} 分钟")
                        lines.append(f"  预计到达: {seg_arrival.strftime('%H:%M')}")
            else:
                lines.append(f"✅ 已经叫到你的号码了！")
        else:
            if remaining_numbers <= 0:
                lines.append(f"✅ 已经叫到你的号码了！")
            else:
                lines.append(f"⚠️ 数据不足，暂时无法估算速度。请再添加一条进度记录。")

        self.update_result("\n".join(lines))
        return True

    def update_result(self, text: str):
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
        self.result_text.configure(state="disabled")


def main():
    root = tk.Tk()
    app = QueueCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
